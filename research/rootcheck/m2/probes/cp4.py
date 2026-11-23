import copy
import json
from unittest.mock import patch

import rlm.core.rlm as core
from rlm import RLM
from rlm.logger import RLMLogger
from rlm.utils.exceptions import BudgetExceededError, ErrorThresholdExceededError, TokenLimitExceededError, TimeoutExceededError
from tests.mock_lm import MockLM
from rlm.core.types import ModelUsageSummary, UsageSummary

def block(code):
    return "```repl\n" + code + "\n```"

def ready(value):
    return block("answer['content'] = " + repr(value) + "\nanswer['ready'] = True")

def run(responses, **kwargs):
    client = MockLM(responses=responses)
    logger = RLMLogger()
    captured = []
    requests = []
    original_completion = client.completion
    def respond(prompt):
        requests.append(copy.deepcopy(prompt))
        return original_completion(prompt)
    client.completion = respond
    original_get_env = core.get_environment
    def get_env(kind, env_kwargs):
        env = original_get_env(kind, env_kwargs)
        original_execute = env.execute_code
        def execute(code):
            result = original_execute(code)
            captured.append((code, result))
            return result
        env.execute_code = execute
        return env
    with patch.object(core, "get_client", return_value=client), patch.object(core, "get_environment", side_effect=get_env):
        with RLM(backend_kwargs={"model_name": "mock"}, logger=logger, max_iterations=kwargs.pop("max_iterations", 1), **kwargs) as root:
            try:
                result = root.completion({"items": [1]}, root_prompt="Return a result")
                error = None
            except (BudgetExceededError, ErrorThresholdExceededError, TokenLimitExceededError, TimeoutExceededError) as exc:
                result, error = None, exc
    return result, error, captured, requests, logger

def emit(name, **fields):
    print(json.dumps({"probe": name, "status": "PASS", **fields}, sort_keys=True))

response = block("answer['content'] = 'A'\nanswer['ready'] = True\nraise ValueError('after-ready')")
result, error, captured, requests, logger = run([response])
assert error is None and result.response == "A"
assert captured[0][1].final_answer == "A" and "ValueError: after-ready" in captured[0][1].stderr
assert len(requests) == 1
emit("F1_ready_then_exception", captured="A", stderr=captured[0][1].stderr, returned=result.response, next_request=False)

result, error, captured, requests, logger = run([block("answer['content'] = 'A'\nanswer['ready'] = True\nanswer['content'] = 'B'")])
assert error is None and result.response == "A"
assert captured[0][1].locals["answer"]["content"] == "B"
emit("F2_content_changed_after_ready", captured=captured[0][1].final_answer, dictionary_content="B", returned=result.response)

result, error, captured, requests, logger = run([ready("A") + "\n" + ready("B")])
assert error is None and [r.final_answer for _,r in captured] == ["A", "B"] and result.response == "A"
assert captured[0][1].locals["answer"]["content"] == "B"
emit("F3_two_final_blocks", block_candidates=[r.final_answer for _,r in captured], returned=result.response, earlier_locals_now="B")

raw_default = block("raise RuntimeError('DEFAULT_CODE_MUST_NOT_RUN')")
result, error, captured, requests, logger = run([block("print('INSPECT')"), raw_default])
assert error is None and result.response == raw_default and len(requests) == 2
assert len(captured) == 1 and captured[0][1].final_answer is None
assert logger._iterations[-1]["code_blocks"] == [] and logger._iterations[-1]["final_answer"] == raw_default
emit("F4_iteration_exhaustion", normal_candidate=None, default_candidate=raw_default, calls=2, default_code_executed=False, returned=result.response)

result, error, captured, requests, logger = run([response], max_errors=1)
assert result is None and isinstance(error, ErrorThresholdExceededError)
assert captured[0][1].final_answer == "A" and len(logger._iterations) == 0
emit("F5_error_limit_beats_final", captured="A", termination=type(error).__name__, returned=None, iteration_logged=False)

result, error, captured, requests, logger = run([ready("A")], max_tokens=1)
assert result is None and isinstance(error, TokenLimitExceededError)
assert captured[0][1].final_answer == "A" and len(logger._iterations) == 0
emit("F6_token_limit_beats_final", captured="A", termination=type(error).__name__, tokens_used=error.tokens_used, returned=None)

class CostLM(MockLM):
    def get_usage_summary(self):
        return UsageSummary({self.model_name: ModelUsageSummary(1, 10, 10, 0.02)})

cost_client = CostLM(responses=[ready("A")])
captured_cost = []
original_get_env = core.get_environment
def cost_env(kind, kwargs):
    env = original_get_env(kind, kwargs)
    original_execute = env.execute_code
    def execute(code):
        result = original_execute(code)
        captured_cost.append(result.final_answer)
        return result
    env.execute_code = execute
    return env
with patch.object(core, "get_client", return_value=cost_client), patch.object(core, "get_environment", side_effect=cost_env):
    with RLM(backend_kwargs={"model_name":"mock"}, max_budget=0.01, max_iterations=1) as root:
        try:
            root.completion({})
            raise AssertionError("expected budget error")
        except BudgetExceededError as exc:
            assert captured_cost[-1] == "A" and exc.spent == 0.02
            emit("F7_cost_limit_beats_final", captured="A", termination=type(exc).__name__, returned=None)

clock = {"now": 0.0}
def overlong_final(prompt):
    clock["now"] = 2.0
    return ready("A")
client = MockLM(response_fn=overlong_final)
with patch.object(core, "get_client", return_value=client), patch.object(core.time, "perf_counter", side_effect=lambda: clock["now"]):
    with RLM(backend_kwargs={"model_name":"mock"}, max_timeout=1.0, max_iterations=1) as root:
        result = root.completion({})
        assert result.response == "A" and result.execution_time == 2.0
emit("F8_timeout_overrun_with_final", captured="A", timeout=1.0, elapsed=2.0, returned="A", termination="normal")

clock["now"] = 0.0
def overlong_nonfinal(prompt):
    clock["now"] = 2.0
    return block("print('WORK')")
client = MockLM(response_fn=overlong_nonfinal)
with patch.object(core, "get_client", return_value=client), patch.object(core.time, "perf_counter", side_effect=lambda: clock["now"]):
    with RLM(backend_kwargs={"model_name":"mock"}, max_timeout=1.0, max_iterations=2) as root:
        try:
            root.completion({})
            raise AssertionError("expected timeout")
        except TimeoutExceededError as exc:
            assert exc.elapsed == 2.0
            emit("F9_timeout_on_next_turn", captured=None, termination=type(exc).__name__, returned=None)
print("CP4 deterministic probes: 9 passed")
