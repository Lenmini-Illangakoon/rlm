"""Independent atomic admission ledger; synthetic rates are not live price assertions."""

import time
from dataclasses import dataclass
from decimal import Decimal
from threading import RLock

D = Decimal


class AdmissionDenied(Exception):
    pass


@dataclass(frozen=True)
class Limits:
    run_usd: Decimal = D("2")
    campaign_usd: Decimal = D("20")
    attempts: int = 24
    input_tokens: int = 64000
    output_tokens: int = 32768
    seconds: float = 900
    margin: Decimal = D("1.10")


@dataclass(frozen=True)
class Rate:
    input_per_million: Decimal
    output_per_million: Decimal

    def cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        return (self.input_per_million * input_tokens + self.output_per_million * output_tokens) / D(1000000)


class Ledger:
    def __init__(self, rates: dict[str, Rate], limits=Limits(), clock=time.monotonic, rates_kind='synthetic_only'):
        if any(not v.is_finite() or v < 0 for r in rates.values()
               for v in (r.input_per_million, r.output_per_million)):
            raise ValueError("Rates cannot be negative")
        self.rates, self.limits, self.clock = rates, limits, clock
        self.rates_kind = rates_kind
        self.lock = RLock()
        self.runs = {}
        self.tickets = {}

    def start(self, run_id: str) -> None:
        with self.lock:
            if run_id in self.runs:
                raise ValueError("Run IDs cannot be reused")
            self.runs[run_id] = {"deadline": self.clock() + self.limits.seconds,
                                 "attempts": 0, "stop_reason": None}

    def exposure(self, run_id=None):
        with self.lock:
            return sum((t["spent"] + t["reserved"] for t in self.tickets.values()
                        if run_id is None or t["run_id"] == run_id), D(0))

    def stop(self, run_id: str, reason: str) -> None:
        with self.lock:
            self.runs[run_id]["stop_reason"] = self.runs[run_id]["stop_reason"] or reason
            for t in self.tickets.values():
                if t["run_id"] == run_id and t["state"] == "in_flight":
                    t["state"] = "cancelled_usage_unknown"

    def deny(self, run_id, reason):
        self.stop(run_id, reason)
        raise AdmissionDenied(reason)

    def admit(self, run_id: str, model: str, input_bound: int, output_bound: int) -> str:
        with self.lock:
            run = self.runs[run_id]
            if run["stop_reason"]:
                raise AdmissionDenied(run["stop_reason"])
            if self.clock() >= run["deadline"]:
                self.deny(run_id, "wall_clock")
            if model not in self.rates:
                self.deny(run_id, "unpriced_model")
            if type(input_bound) is not int or type(output_bound) is not int or not (
                0 <= input_bound <= self.limits.input_tokens and 0 < output_bound <= self.limits.output_tokens
            ):
                self.deny(run_id, "token_bound")
            if run["attempts"] >= self.limits.attempts:
                self.deny(run_id, "attempt_limit")
            reservation = self.rates[model].cost(input_bound, output_bound) * self.limits.margin
            if self.exposure(run_id) + reservation > self.limits.run_usd:
                self.deny(run_id, "run_budget")
            if self.exposure() + reservation > self.limits.campaign_usd:
                self.deny(run_id, "campaign_budget")
            ticket = f"attempt-{len(self.tickets) + 1:05d}"
            self.tickets[ticket] = {"run_id": run_id, "model": model, "input_bound": input_bound,
                                    "output_bound": output_bound, "reserved": reservation,
                                    "spent": D(0), "state": "in_flight"}
            run["attempts"] += 1
            return ticket

    def reconcile(self, ticket: str, input_tokens: int | None, output_tokens: int | None,
                  billed_usd: Decimal | None = None) -> None:
        with self.lock:
            row = self.tickets[ticket]
            if row["state"] == "reconciled":
                raise ValueError("Duplicate reconciliation")
            if input_tokens is None or output_tokens is None:
                row["state"] = "usage_unknown"
                self.stop(row["run_id"], "usage_unknown")
                return  # reservation stays held, including campaign exposure
            if type(input_tokens) is not int or type(output_tokens) is not int or min(input_tokens, output_tokens) < 0:
                self.deny(row["run_id"], "invalid_usage")
            calculated = self.rates[row["model"]].cost(input_tokens, output_tokens)
            if billed_usd is not None and (not billed_usd.is_finite() or billed_usd < 0):
                self.deny(row['run_id'], 'invalid_billed_cost')
            row['reported_cost_usd'] = billed_usd
            row['rate_cost_usd'] = calculated
            row["spent"] = max(calculated, billed_usd or D(0))
            cost_exceeded = row['spent'] > row['reserved']
            row["reserved"] = D(0)
            row["state"] = "reconciled"
            if input_tokens > row["input_bound"] or output_tokens > row["output_bound"]:
                self.stop(row["run_id"], "usage_exceeded_reserved_bounds")
            if cost_exceeded:
                self.stop(row['run_id'], 'cost_exceeded_reservation')
            if self.exposure() > self.limits.campaign_usd:
                for run_id in self.runs:
                    self.stop(run_id, "campaign_budget_overrun")

    def snapshot(self):
        with self.lock:
            return {"rates_kind": self.rates_kind, "campaign_exposure_usd": str(self.exposure()),
                    "runs": {k: dict(v) for k, v in self.runs.items()},
                    "tickets": {k: {f: str(v) if isinstance(v, Decimal) else v for f, v in t.items()}
                                for k, t in self.tickets.items()}}

    def restore(self, snapshot):
        """Restore reviewed campaign accounting, including unresolved reservations."""
        with self.lock:
            if self.runs or self.tickets or snapshot['rates_kind'] != self.rates_kind:
                raise ValueError('Restore requires an empty ledger with the same rate provenance')
            self.runs = {key: dict(row) for key, row in snapshot['runs'].items()}
            for key, row in snapshot['tickets'].items():
                restored = dict(row)
                for field in ('spent', 'reserved', 'reported_cost_usd', 'rate_cost_usd'):
                    if field in restored and restored[field] is not None:
                        restored[field] = D(restored[field])
                self.tickets[key] = restored


SYNTHETIC_RATES = {name: Rate(D("1"), D("2"))
                   for name in ("openai/gpt-5", "openai/gpt-5-nano")}
