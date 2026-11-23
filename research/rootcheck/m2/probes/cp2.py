import json
from unittest.mock import patch
import rlm.core.rlm as core
from rlm import RLM
from rlm.core.lm_handler import LMHandler
from rlm.core.types import RLMChatCompletion, UsageSummary
from rlm.environments.local_repl import LocalREPL
from tests.mock_lm import MockLM

class ProbeReject(Exception):
    pass

def completion(text):
    return RLMChatCompletion("mock", "request", text, UsageSummary({}), 0)

def emit(name, **fields):
    print(json.dumps({"probe":name, "status":"PASS", **fields}, sort_keys=True))

passed = 0
for mode in ("llm", "rlm_callback", "rlm_no_callback", "rlm_core_leaf"):
    for batched in (False, True):
        events = []
        def produce(prompt):
            tag = "bad" if str(prompt).startswith("bad") else "good"
            events.append("dispatch:" + tag)
            if tag == "bad":
                events.extend(["candidate:REJECTED_PAYLOAD", "reject:bad"])
                raise ProbeReject("REJECTED")
            events.append("return:good")
            return "OK"
        def callback(instruction, context, model):
            return completion(produce(instruction))
        fake_client = MockLM(response_fn=produce)
        with patch.object(core, "get_client", return_value=fake_client):
            with RLM(backend_kwargs={"model_name":"mock"}, max_depth=1) as leaf_parent:
                cb = callback if mode == "rlm_callback" else leaf_parent._subcall if mode == "rlm_core_leaf" else None
                with LMHandler(fake_client) as handler:
                    with LocalREPL(lm_handler_address=handler.address, subcall_fn=cb, custom_tools={"note": lambda value: events.append(value)}) as env:
                        if mode == "llm":
                            expr = "llm_query_batched(['bad', 'good'])" if batched else "llm_query('bad')"
                        else:
                            expr = "rlm_query_batched([('bad', {}), ('good', {})])" if batched else "rlm_query('bad', {})"
                        code = "value = " + expr + "\nnote('consume')\nanswer['content'] = str(value)\nanswer['ready'] = True"
                        result = env.execute_code(code)
                        value = env.locals["value"]
                        bad_value = value[0] if batched else value
                        assert "REJECTED_PAYLOAD" not in bad_value and "Error:" in bad_value and "REJECTED" in bad_value
                        assert result.stderr == "" and result.final_answer == str(value)
                        assert events.index("dispatch:bad") < events.index("candidate:REJECTED_PAYLOAD") < events.index("reject:bad") < events.index("consume")
                        expected_records = (2 if batched else 1) if mode == "rlm_core_leaf" else (1 if batched else 0)
                        assert len(result.rlm_calls) == expected_records
                        if batched:
                            assert value[1] == "OK" and "return:good" in events
                        output = {"mode":mode, "batched":batched, "original_withheld":True, "downstream_ran":True,
                                  "ready_final_present":result.final_answer is not None, "recorded_calls":len(result.rlm_calls),
                                  "bad_return":bad_value, "bad_path_events":[e for e in events if "good" not in e]}
        passed += 1
        emit("I" + str(passed), **output)

with LocalREPL(subcall_fn=lambda *args: completion("REJECTED: explanation")) as env:
    result = env.execute_code("value = rlm_query('task', {})\nanswer['content'] = value\nanswer['ready'] = True")
    assert result.final_answer == "REJECTED: explanation" and len(result.rlm_calls) == 1
    assert result.rlm_calls[0].error is None
emit("I9_rejection_text_is_normal_completion", returned="REJECTED: explanation", recorded_error=None)

for caught in (False, True):
    events = []
    with LocalREPL(subcall_fn=lambda *args: completion("REJECTED_PAYLOAD"), custom_tools={"note":lambda value:events.append(value)}) as env:
        original = env._rlm_query
        def wrapper(*args, **kwargs):
            value = original(*args, **kwargs)
            events.extend(["candidate_available", "reject"])
            raise ProbeReject("REJECTED")
        with patch.dict(env.globals, {"rlm_query":wrapper}):
            query = "value = rlm_query('task', {})"
            code = ("try:\n    " + query + "\nexcept Exception:\n    note('caught')\n") if caught else query + "\n"
            code += "note('downstream')\nanswer['content'] = 'AFTER'\nanswer['ready'] = True"
            result = env.execute_code(code)
            assert len(result.rlm_calls) == 1 and "value" not in env.locals
            if caught:
                assert result.stderr == "" and result.final_answer == "AFTER" and "downstream" in events
            else:
                assert "ProbeReject: REJECTED" in result.stderr and result.final_answer is None and "downstream" not in events
    emit("I10_wrapper_caught" if caught else "I10_wrapper_uncaught", original_withheld=True, caught=caught,
         downstream_ran="downstream" in events, final=result.final_answer, events=events)
    passed += 1

def block(code):
    return "```repl\n" + code + "\n```"
first = block("value = rlm_query('task', {})\nanswer['content'] = 'FIRST'\nanswer['ready'] = True")
second = block("answer['content'] = 'SECOND'\nanswer['ready'] = True")
client = MockLM(responses=[first + "\n" + second])
recorded = []
original_get_env = core.get_environment
def get_env(kind, kwargs):
    env = original_get_env(kind, kwargs)
    env.subcall_fn = lambda *args: completion("REJECTED_PAYLOAD")
    original = env._rlm_query
    def wrapper(*args, **kw):
        original(*args, **kw)
        raise ProbeReject("REJECTED")
    env.globals["rlm_query"] = wrapper
    original_execute = env.execute_code
    def execute(code):
        result = original_execute(code)
        recorded.append(result)
        return result
    env.execute_code = execute
    return env
with patch.object(core, "get_client", return_value=client), patch.object(core, "get_environment", side_effect=get_env):
    with RLM(backend_kwargs={"model_name":"mock"}, max_iterations=1) as root:
        result = root.completion({})
assert len(recorded) == 2 and "ProbeReject" in recorded[0].stderr and recorded[0].final_answer is None
assert recorded[1].final_answer == "SECOND" and result.response == "SECOND"
emit("I11_interrupt_one_block_not_iteration", first_candidate=None, second_candidate="SECOND", returned=result.response)
print("CP2 deterministic probes: 12 passed")
