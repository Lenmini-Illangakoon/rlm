"""New supplementary M2 test; not one of the original 30 recovered probes.

Run only through the offline bootstrap extracted from reproduce.ps1.
The callback spy observes both capture events without changing baseline source.
"""

import json
from unittest.mock import patch

import rlm.core.rlm as core
from rlm import RLM
from tests.mock_lm import MockLM

CODE = (
    'answer["content"] = "A"\n'
    'answer["ready"] = True\n'
    '\n'
    'answer["content"] = "B"\n'
    'answer["ready"] = True'
)
capture_events = []
block_results = []
client = MockLM(responses=["```repl\n" + CODE + "\n```"])
original_get_environment = core.get_environment


def observe_environment(kind, kwargs):
    environment = original_get_environment(kind, kwargs)
    answer = environment.locals["answer"]
    original_on_ready = answer._on_ready

    def capture(content):
        capture_events.append(content)
        original_on_ready(content)

    answer._on_ready = capture
    original_execute = environment.execute_code

    def execute(code):
        result = original_execute(code)
        block_results.append(
            {
                "candidate": result.final_answer,
                "stderr": result.stderr,
                "dictionary_content": result.locals["answer"]["content"],
            }
        )
        return result

    environment.execute_code = execute
    return environment


with (
    patch.object(core, "get_client", return_value=client),
    patch.object(core, "get_environment", side_effect=observe_environment),
):
    with RLM(
        backend_kwargs={"model_name": "mock"},
        environment="local",
        max_depth=1,
        max_iterations=1,
        persistent=False,
        compaction=False,
        stream=False,
        experimental_spec_ptc=False,
    ) as root:
        completion = root.completion({"items": [1]}, root_prompt="Return the answer")

assert capture_events == ["A", "B"]
assert len(block_results) == 1
assert block_results[0]["candidate"] == "B"
assert block_results[0]["dictionary_content"] == "B"
assert block_results[0]["stderr"] == ""
assert completion.response == "B"
assert client._call_count == 1

print(
    json.dumps(
        {
            "probe": "P-CP4-REPEATED-READY",
            "evidence_class": "new supplementary deterministic test",
            "status": "PASS",
            "capture_events": capture_events,
            "captured_candidate": block_results[0]["candidate"],
            "dictionary_content": block_results[0]["dictionary_content"],
            "returned": completion.response,
            "stderr": block_results[0]["stderr"],
            "root_model_calls": client._call_count,
            "executed_blocks": len(block_results),
            "capture_spy": "delegates to baseline _on_ready; observes both events",
        },
        sort_keys=True,
    )
)
