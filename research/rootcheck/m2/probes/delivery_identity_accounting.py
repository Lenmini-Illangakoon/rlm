import copy
import json
from unittest.mock import patch

import rlm.core.rlm as core
from rlm import RLM
from rlm.core.types import ModelUsageSummary, RLMIteration, UsageSummary
from rlm.environments.local_repl import LocalREPL
from rlm.logger import RLMLogger
from tests.mock_lm import MockLM

def block(code):
    return "```repl\n" + code + "\n```"

def ready(value):
    return block("answer['content'] = " + repr(value) + "\nanswer['ready'] = True")

def emit(name, **fields):
    print(json.dumps({"probe":name, "status":"PASS", **fields}, sort_keys=True))

response = block("print('x' * 20005)\nraise ValueError('HIDDEN_STDERR')") + "\n" + block("print('SECOND')")
requests = []
captured = []
vars_line = "REPL variables: ['answer', 'context_0', 'context']\n"
raw_first = "\n" + "x" * 20005 + "\n" + "\n\n" + "\n\nValueError: HIDDEN_STDERR" + "\n\n" + vars_line
expected_first = raw_first[:20000] + "... + [" + str(len(raw_first)-20000) + " chars...]"
expected_second = "\nSECOND\n" + "\n\n" + vars_line
expected_feedback = "REPL output (block 1):\n" + expected_first + "\n\nREPL output (block 2):\n" + expected_second
def respond(prompt):
    requests.append(copy.deepcopy(prompt))
    if len(requests) == 1:
        return response
    assert prompt[-3] == {"role":"assistant", "content":response}
    assert prompt[-2] == {"role":"user", "content":expected_feedback}
    assert prompt[-1] == {"role":"user", "content":"Turn 2/2:"}
    assert "HIDDEN_STDERR" not in prompt[-2]["content"] and "SECOND" in prompt[-2]["content"]
    return ready("SCRIPTED_REPAIR")
client = MockLM(response_fn=respond)
original_get_env = core.get_environment
def capture_env(kind, kwargs):
    env = original_get_env(kind, kwargs)
    original = env.execute_code
    def execute(code):
        result = original(code)
        captured.append(result)
        return result
    env.execute_code = execute
    return env
with patch.object(core,"get_client",return_value=client), patch.object(core,"get_environment",side_effect=capture_env):
    with RLM(backend_kwargs={"model_name":"mock"}, max_iterations=2) as root:
        result = root.completion({})
assert result.response == "SCRIPTED_REPAIR" and len(requests) == 2
assert "HIDDEN_STDERR" in captured[0].stderr
emit("D1_exact_next_request", blocks=2, per_block_cap=20000, exact_feedback_match=True,
     error_in_raw_result=True, error_in_next_feedback=False, second_block_delivered=True,
     returned=result.response, acted_upon="scripted mock branch only")

history = [{"role":"user","content":"BEFORE"}]
logger = RLMLogger()
logger.log(RLMIteration(history, "response", []))
entry = logger._iterations[0]
serialized_before = json.dumps(entry)
assert entry["prompt"] is history
history.append({"role":"user","content":"LATER"})
assert entry["prompt"][-1]["content"] == "LATER" and "LATER" not in serialized_before
emit("D2_in_memory_history_alias", shared_reference=True, earlier_memory_entry_changed=True,
     serialized_snapshot_changed=False)

with LocalREPL() as env:
    earlier = env.execute_code("items = [1]")
    frozen = copy.deepcopy(earlier.locals["items"])
    env.execute_code("items.append(2)")
    assert earlier.locals["items"] == [1,2] and frozen == [1]
    failed = env.execute_code("items.append(3)\nnew_binding = 5\nraise ValueError('STOP')")
    assert "ValueError" in failed.stderr and earlier.locals["items"] == [1,2,3]
    assert "new_binding" not in env.locals
    env.execute_code("items = [99]")
    assert env.locals["items"] == [99] and earlier.locals["items"] == [1,2,3]
emit("D3_locals_alias_and_partial_effects", earlier_value=[1,2,3], frozen_value=[1],
     new_binding_after_error=False, later_rebinding=[99])

class MeterLM(MockLM):
    def __init__(self, model_name, response):
        super().__init__(model_name=model_name, responses=[response])
    def get_usage_summary(self):
        tokens, out, cost = (10,5,0.01) if self.model_name == "root" else (30,7,0.03)
        return UsageSummary({self.model_name:ModelUsageSummary(self._call_count,tokens*self._call_count,out*self._call_count,cost*self._call_count)})
made = []
parent_code = block("value = rlm_query('extract', {'v':'A'}, model='child')\nanswer['content'] = value\nanswer['ready'] = True")
def create_meter(backend, kwargs):
    client = MeterLM(kwargs["model_name"], parent_code if kwargs["model_name"] == "root" else ready("A"))
    made.append(client)
    return client
observed = {}
with patch.object(core,"get_client",side_effect=create_meter):
    with RLM(backend_kwargs={"model_name":"root"}, max_depth=2,max_iterations=1,max_budget=1.0,logger=RLMLogger()) as root:
        original_check = root._check_iteration_limits
        def check(iteration, number, handler):
            observed["before"] = root._cumulative_cost
            original_check(iteration, number, handler)
            observed["after"] = root._cumulative_cost
        root._check_iteration_limits = check
        result = root.completion({})
        recorded_child = result.metadata["iterations"][0]["code_blocks"][0]["result"]["rlm_calls"][0]
assert len(made) == 2 and all(client._call_count == 1 for client in made)
assert observed == {"before":0.03, "after":0.01}
assert result.usage_summary.total_cost == 0.01 and result.usage_summary.total_input_tokens == 10
assert recorded_child["usage_summary"]["total_cost"] == 0.03
emit("D4_recursive_usage_ownership", child_cost_before_check=observed["before"], parent_cost_after_check=observed["after"],
     returned_cost=0.01, distinct_client_cost_sum=0.04, returned_input_tokens=10, distinct_client_input_sum=40)

clock = {"now":0.0, "calls":0}
def timed_response(prompt):
    clock["calls"] += 1
    clock["now"] += 2.0 if clock["calls"] == 1 else 7.0
    return block("print('WORK')") if clock["calls"] == 1 else "RAW_FINAL"
client = MockLM(response_fn=timed_response)
with patch.object(core,"get_client",return_value=client), patch.object(core.time,"perf_counter",side_effect=lambda:clock["now"]):
    with RLM(backend_kwargs={"model_name":"mock"},max_iterations=1) as root:
        result = root.completion({})
assert result.response == "RAW_FINAL" and result.execution_time == 2.0 and clock["now"] == 9.0
emit("D5_default_latency", reported=2.0, fake_outer_elapsed=9.0, omitted_default_call=7.0)

for batched in (False,True):
    events = []
    root_code = ("values = rlm_query_batched([('extract', {'v':'A'}), ('extract', {'v':'B'})], model='child')\nvalue = '|'.join(values)\n"
                 if batched else "value = rlm_query('extract', {'v':'A'}, model='child')\n")
    root_code += "note('consume:' + value)\nanswer['content'] = value\nanswer['ready'] = True"
    child_code = "note('child_body:' + context['v'])\nanswer['content'] = context['v']\nanswer['ready'] = True"
    def create_client(backend, kwargs):
        return MockLM(model_name=kwargs["model_name"], responses=[block(root_code if kwargs["model_name"] == "root" else child_code)])
    def observe_env(kind, kwargs):
        env = original_get_env(kind, kwargs)
        if kwargs["depth"] == 1:
            original_subcall = env.subcall_fn
            def subcall(instruction, context, model):
                events.append("dispatch:" + context["v"])
                answer = original_subcall(instruction, context, model)
                events.append("available:" + answer.response)
                return answer
            env.subcall_fn = subcall
            answer_dict = env.locals["answer"]
            original_ready = answer_dict._on_ready
            def on_ready(content):
                events.append("ready:" + str(content))
                original_ready(content)
            answer_dict._on_ready = on_ready
        return env
    with patch.object(core,"get_client",side_effect=create_client), patch.object(core,"get_environment",side_effect=observe_env):
        with RLM(backend_kwargs={"model_name":"root"},max_depth=2,max_iterations=1,custom_tools={"note":events.append}) as root:
            result = root.completion({})
    expected = "A|B" if batched else "A"
    assert result.response == expected
    for value in (["A","B"] if batched else ["A"]):
        assert events.index("dispatch:"+value) < events.index("child_body:"+value) < events.index("available:"+value) < events.index("consume:"+expected) < events.index("ready:"+expected)
    emit("D7_actual_child_batch_order" if batched else "D6_actual_child_single_order",
         events=events, actual_child_repl=True, returned=result.response)

print("CP3 / identity / accounting / child-order probes: 7 passed")
