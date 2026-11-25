"""Pinned RLM with a synthetic BaseLM; no SDK and no credential lookup."""

import asyncio
import copy
import re
import time
from threading import Lock
from unittest.mock import patch

from .offline_guard import install

install()

from rlm.clients.base_lm import BaseLM
from rlm.core import rlm as core
from rlm.core.types import ModelUsageSummary, UsageSummary
from rlm.logger import RLMLogger

from ..fixtures.programs import Fixture
from .observe import ACTION, BATCH, NODE, SLOT, Observer


def canonical(value):
    """Comparison ignores wall time/UUIDs, not model messages or execution values."""
    if isinstance(value, str) and value.startswith("<_io.TextIOWrapper name="):
        return re.sub(r"repl_env_[^\\/']+", "repl_env_<fresh>", value)
    if isinstance(value, list):
        return [canonical(x) for x in value]
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in value.items()
                if k not in {"timestamp", "execution_time", "iteration_time"}}
    return value


class Script:
    def __init__(self, fixture: Fixture, observer=None, ledger=None):
        self.fixture = fixture
        self.observer = observer
        self.ledger = ledger
        self.lock = Lock()
        self.counts = {}
        self.requests = []

    def response(self, prompt, model, owner):
        started = time.perf_counter_ns()
        rendered = str(prompt)
        key = "root"
        if isinstance(prompt, list):
            # Inspect the PUBLIC instruction only. Code in previous root turns may name children.
            instruction = str(prompt[1]) if len(prompt) > 1 else ""
            key = next((k for k in self.fixture.children if k in instruction), "root")
        else:
            key = next((k for k in self.fixture.plain if k in rendered), "plain-unmatched")
        with self.lock:
            attempt = len(self.requests) + 1
            index = self.counts.get(key, 0)
            self.counts[key] = index + 1
            row = {"attempt": attempt, "model": model, "provider": "synthetic",
                   "prompt": copy.deepcopy(prompt), "route_key": key}
            self.requests.append(row)
        permit = None
        if self.ledger:
            permit = self.ledger.admit(self.ledger.run_id, model, 100, 100)
        event = None
        if self.observer:
            event = self.observer.emit("provider_dispatch", attempt=attempt, model=model,
                                       provider="synthetic", owner_node=owner, request=prompt,
                                       causal_action=ACTION.get(), usage_is_synthetic=True)
        try:
            if isinstance(prompt, list):
                outputs = self.fixture.responses if key == "root" else self.fixture.children[key]
                result = outputs[index]
            else:
                result = self.fixture.plain[key]
            if result == "!ERROR":
                raise RuntimeError("synthetic provider failure")
            if result == "!CANCEL":
                raise KeyboardInterrupt
            row["response"] = result
            if self.ledger:
                self.ledger.reconcile(permit, 20, 10)
            if self.observer:
                self.observer.emit("provider_return", dispatch=event, content=result,
                                   elapsed_ns=time.perf_counter_ns() - started,
                                   usage={"input_tokens": 20, "output_tokens": 10})
            return result
        except BaseException as exc:
            row["error"] = type(exc).__name__
            if self.ledger and permit:
                self.ledger.reconcile(permit, None, None)
            if self.observer:
                self.observer.emit("provider_failure", dispatch=event,
                                   exception_type=type(exc).__name__,
                                   elapsed_ns=time.perf_counter_ns() - started, usage=None)
            raise


class SyntheticLM(BaseLM):
    def __init__(self, model_name, script):
        super().__init__(model_name=model_name)
        self.script = script
        self.owner = NODE.get()
        self.calls = 0
        self.lock = Lock()

    def completion(self, prompt, model=None):
        with self.lock:
            self.calls += 1
        return self.script.response(prompt, model or self.model_name, self.owner)

    async def acompletion(self, prompt, model=None):
        batch = BATCH.get()
        slot = None
        if batch:
            slot = batch["next"]
            if batch["prompts"][slot] != prompt:
                raise RuntimeError("Pinned batch invocation order changed")
            batch["next"] += 1
        token = SLOT.set(slot)
        try:
            await asyncio.sleep(self.script.fixture.delays.get(str(prompt), 0))
            return self.completion(prompt, model)
        finally:
            SLOT.reset(token)

    def get_usage_summary(self):
        return UsageSummary({self.model_name: ModelUsageSummary(self.calls, self.calls * 20, self.calls * 10)})

    def get_last_usage(self):
        return ModelUsageSummary(1, 20, 10)


def run_fixture(fixture, instrumented=True, context="fixture context", query="fixture root", ledger=None, sink=None):
    from .config import load_config

    config = load_config()
    observer = Observer(sink=sink) if instrumented else None
    script = Script(fixture, observer, ledger)
    logger = RLMLogger()
    start = time.perf_counter()
    if observer:
        observer.install()
    try:
        with patch.object(core, "get_client", lambda backend, kwargs: SyntheticLM(kwargs["model_name"], script)):
            runtime = core.RLM(
                backend=config['provider'], backend_kwargs={"model_name": config['root_model']},
                other_backends=[config['provider']], other_backend_kwargs=[{"model_name": config['plain_depth_one_model']}],
                environment=config['environment'], max_depth=config['max_depth'], max_iterations=fixture.iterations,
                experimental_spec_ptc=config['experimental_spec_ptc'], persistent=config['persistent'], compaction=config['compaction'],
                max_concurrent_subcalls=config['recursive_concurrency'],
                sampling_args={"max_tokens": config['completion_tokens_per_request']},
                sub_sampling_args={"max_tokens": config['completion_tokens_per_request']},
                logger=logger, verbose=False,
            )
            response, error = None, None
            try:
                response = runtime.completion(context, root_prompt=query).response
            except BaseException as exc:
                error = type(exc).__name__
            finally:
                runtime.close()
    finally:
        if observer:
            observer.close()
    return {"fixture": fixture.name, "synthetic_only": True,
            "response": response, "error": error,
            "requests": copy.deepcopy(script.requests), "trajectory": logger.get_trajectory(),
            "events": observer.events if observer else [], "elapsed_s": time.perf_counter() - start,
            "run_id": observer.run_id if observer else None}


def run_scenario(scenario):
    from .broker import run_transport_scenario

    return run_transport_scenario(scenario)
