"""Researcher-side annotation records. These never run in the model environment."""

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Label(StrEnum):
    OBSERVED = "observed"
    NOT_OBSERVED = "not_observed"
    NON_APPLICABLE = "non_applicable"
    INCONCLUSIVE = "inconclusive"


STRATA = {"python", "plain_lm", "recursive_rlm", "batch_slot"}
PURPOSES = {"necessary_computation", "useful_verification", "error_recovery",
            "final_delivery", "redundant_computation", "mixed", "uncertain"}
PATHS = {"voluntary", "same_block", "iteration_default", "depth_fallback",
         "forced_termination", "no_return"}


@dataclass(frozen=True)
class EvidenceLink:
    obligation_id: str
    contract_id: str | None
    source_refs: tuple[str, ...]
    observed_result_ref: str | None
    dependent_action_ref: str | None
    final_claim_ref: str | None
    relation_status: str  # established / human_review / unknown
    supporting_refs: tuple[str, ...]

    def validate(self):
        if self.relation_status not in {'established', 'human_review', 'unknown'}:
            raise ValueError('Unknown provenance relation status')
        if self.relation_status == 'established' and not self.supporting_refs:
            raise ValueError('Do not invent dependencies without supporting evidence')


@dataclass(frozen=True)
class Contract:
    action_id: str
    stratum: str
    prefix_end: int
    result_event: int
    intended_outcome: str
    obligations: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    reviewer: str
    prefix_sha256: str

    def validate(self) -> None:
        if self.stratum not in STRATA or self.prefix_end >= self.result_event:
            raise ValueError("Contract must use a pre-result prefix and an action stratum")
        if not all((self.action_id, self.intended_outcome, self.obligations,
                    self.evidence_refs, self.reviewer, self.prefix_sha256)):
            raise ValueError("Contract requires provenance and an identified human reviewer")


@dataclass
class H2:
    contract: Contract
    normal_boundary: bool | None
    material_mismatch: bool | None
    result_refs: list[str]
    origin_id: str | None = None
    propagated_from: str | None = None
    recovery: str = "unreviewed"
    containment: str = "unreviewed"
    secondary_h1_refs: list[str] = field(default_factory=list)

    def label(self) -> Label:
        self.contract.validate()
        if self.normal_boundary is False:
            return Label.NON_APPLICABLE  # execution error is a separate operational record
        if self.normal_boundary is None or self.material_mismatch is None or not self.result_refs:
            return Label.INCONCLUSIVE
        if self.material_mismatch:
            if not (self.origin_id or self.propagated_from):
                raise ValueError("Mismatch needs an origin or propagation link")
            return Label.OBSERVED
        return Label.NOT_OBSERVED


def independent_origins(rows: list[H2]) -> set[str]:
    return {row.origin_id for row in rows
            if row.label() == Label.OBSERVED and row.origin_id and not row.propagated_from}


@dataclass
class H5:
    actual_return_ref: str | None
    path: str
    correctness: str  # correct / incorrect / unassessed; never alone determines overall
    material_omission: bool | None
    material_support_gap: bool | None
    necessary_unobserved_unvalidated: bool | None
    evidence_refs: list[str]
    reviewer: str
    captures: list[str] = field(default_factory=list)
    selection_ref: str | None = None
    explanation: str = ""

    def label(self) -> Label:
        if self.path not in PATHS:
            raise ValueError("Unknown finalization path")
        if self.path == "no_return":
            return Label.NON_APPLICABLE
        if not (self.actual_return_ref and self.evidence_refs and self.reviewer):
            return Label.INCONCLUSIVE
        dimensions = (self.material_omission, self.material_support_gap,
                      self.necessary_unobserved_unvalidated)
        if any(x is True for x in dimensions):
            return Label.OBSERVED
        if any(x is None for x in dimensions):
            return Label.INCONCLUSIVE
        return Label.NOT_OBSERVED


@dataclass
class H6:
    t_compute: int | None
    t_visible: int | None
    prefix_sha256: str
    sufficient: bool | None
    stable: bool | None
    all_obligations_covered: bool | None
    material_uncertainty_resolved: bool | None
    reviewer: str
    evidence_refs: list[str]
    actions: list[dict[str, Any]] = field(default_factory=list)

    def label(self) -> Label:
        checks = (self.sufficient, self.stable, self.all_obligations_covered,
                  self.material_uncertainty_resolved)
        if any(x is None for x in checks) or not (self.reviewer and self.evidence_refs):
            return Label.INCONCLUSIVE
        if not all(checks):
            return Label.NON_APPLICABLE
        if self.t_visible is None or self.t_compute is None or not self.prefix_sha256:
            return Label.INCONCLUSIVE
        if self.t_compute > self.t_visible:
            raise ValueError("Visibility cannot precede sufficient computation")
        for action in self.actions:
            if action["purpose"] not in PURPOSES or action["event"] <= self.t_visible:
                raise ValueError("H6 continuation must follow the committed sufficient prefix")
            if not action.get("evidence_refs"):
                return Label.INCONCLUSIVE
        if any(a["purpose"] == "redundant_computation" for a in self.actions):
            return Label.OBSERVED
        if any(a["purpose"] in {"uncertain", "mixed"} for a in self.actions):
            return Label.INCONCLUSIVE
        return Label.NOT_OBSERVED


def prefix_packet(events: list[dict], through: int, root_visible_only=False) -> dict:
    """No oracle and no future events. Reviewers commit this hash before unblinding."""
    import hashlib
    import json

    prefix = [e for e in events if e["seq"] <= through]
    if root_visible_only:
        roots = {e['event_id'] for e in prefix
                 if e.get('kind') == 'node_start' and e.get('depth') == 0}
        # Only exact delivered root request histories; no hidden locals or child traces.
        prefix = [e for e in prefix if e.get('kind') == 'provider_dispatch'
                  and e.get('owner_node') in roots and isinstance(e.get('request'), list)]
    payload = json.dumps(prefix, sort_keys=True, ensure_ascii=False).encode()
    return {"prefix_end": through, "sha256": hashlib.sha256(payload).hexdigest(),
            "events": json.loads(payload), "root_visible_only": root_visible_only,
            "review_state": "awaiting_human_commitment"}


def record(review: H2 | H5 | H6) -> dict:
    return {"schema_version": "1.0", "hypothesis": type(review).__name__,
            "label": review.label().value, "review": asdict(review),
            "operational_failure": None, "infrastructure_failure": None,
            "forced_termination": None, "resource_censoring": None,
            "natural_baseline_evidence": False}
