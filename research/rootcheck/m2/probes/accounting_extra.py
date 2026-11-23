import json
from unittest.mock import patch
import rlm.core.rlm as core
from rlm import RLM
from rlm.core.comms_utils import send_lm_request_batched
from rlm.core.lm_handler import LMHandler
from rlm.core.types import ModelUsageSummary, UsageSummary
from tests.mock_lm import MockLM

def block(code):
    return "```repl\n" + code + "\n```"
def ready(value):
    return block("answer['content'] = " + repr(value) + "\nanswer['ready'] = True")

class Meter(MockLM):
    def get_usage_summary(self):
        cost = 0.01 if self.model_name == "root" else 0.03
        return UsageSummary({self.model_name:ModelUsageSummary(self._call_count,10,10,cost*self._call_count)})
clients = []
def factory(backend, kwargs):
    response = block("answer['content'] = rlm_query('extract', {}, model='child')\nanswer['ready'] = True") if kwargs["model_name"] == "root" else ready("A")
    client = Meter(model_name=kwargs["model_name"],responses=[response])
    clients.append(client)
    return client
with patch.object(core,"get_client",side_effect=factory):
    with RLM(backend_kwargs={"model_name":"root"},max_depth=2,max_iterations=1,max_budget=0.035) as root:
        result = root.completion({})
assert len(clients) == 2 and result.response == "A"
actual_cost = sum(client.get_usage_summary().total_cost for client in clients)
assert actual_cost == 0.04 and actual_cost > 0.035 and result.usage_summary.total_cost == 0.01
print(json.dumps({"probe":"D8_recursive_budget_overshoot","status":"PASS","synthetic_total":actual_cost,
                  "configured_budget":0.035,"reported_total":0.01,"termination":"normal","returned":"A"}))

clock = {"now":0.0}
class BatchMeter(MockLM):
    def __init__(self):
        super().__init__(model_name="mock")
        self.inputs = []
        self.last = None
    def completion(self,prompt):
        tokens, duration = (15,2.0) if prompt == "first" else (40,8.0)
        self.inputs.append(tokens)
        self.last = ModelUsageSummary(1,tokens,0,tokens/1000)
        clock["now"] += duration
        return "OK:"+prompt
    def get_last_usage(self):
        return self.last
    def get_usage_summary(self):
        return UsageSummary({"mock":ModelUsageSummary(len(self.inputs),sum(self.inputs),0,sum(self.inputs)/1000)})
client = BatchMeter()
with patch.object(core.time,"perf_counter",side_effect=lambda:clock["now"]):
    with LMHandler(client) as handler:
        slots = send_lm_request_batched(handler.address,["first","second"])
        summary = handler.get_usage_summary()
assert [s.chat_completion.response for s in slots] == ["OK:first","OK:second"]
inputs = [s.chat_completion.usage_summary.total_input_tokens for s in slots]
durations = [s.chat_completion.execution_time for s in slots]
assert inputs == [40,40] and summary.total_input_tokens == 55
assert durations == [5.0,5.0]
print(json.dumps({"probe":"D9_batch_metrics","status":"PASS","slot_input_tokens":inputs,
                  "handler_input_total":55,"slot_duration_estimates":durations,
                  "fixture_call_durations":[2.0,8.0]}))
print("Additional accounting probes: 2 passed")
