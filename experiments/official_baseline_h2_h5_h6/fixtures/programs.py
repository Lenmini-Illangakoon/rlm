from dataclasses import dataclass, field


def block(code: str) -> str:
    return "```repl\n" + code + "\n```"


def finish(expression: str) -> str:
    return f"answer['content'] = {expression}\nanswer['ready'] = True"


@dataclass
class Fixture:
    name: str
    responses: list[str]
    expected: str | None
    children: dict[str, list[str]] = field(default_factory=dict)
    plain: dict[str, str] = field(default_factory=dict)
    iterations: int = 10
    error: str | None = None
    delays: dict[str, float] = field(default_factory=dict)


FIXTURES = [
    Fixture("same_block", [block("x = 6 * 7\n" + finish("x"))], "42"),
    Fixture("plain_consumption", [block("x = int(llm_query('plain-seven'))\n" + finish("x * 6"))], "42", plain={"plain-seven": "7"}),
    Fixture("recursive", [block("x = rlm_query('fixture-child-a', 'child context')\n" + finish("x"))], "child-A", children={"fixture-child-a": [block(finish("'child-A'"))]}),
    Fixture("plain_batch", [block("x = llm_query_batched(['plain-a', 'plain-error', 'plain-b'])\n" + finish("'|'.join(x)"))], "A|Error: llm() call failed - synthetic provider failure|B", plain={"plain-a": "A", "plain-error": "!ERROR", "plain-b": "B"}),
    Fixture("recursive_batch", [block("x = rlm_query_batched([('fixture-child-a', 'a'), ('fixture-child-b', 'b')])\n" + finish("'|'.join(x)"))], "A|B", children={"fixture-child-a": [block(finish("'A'"))], "fixture-child-b": [block(finish("'B'"))]}),
    Fixture("multiple_blocks", [block(finish("'A'")) + "\n" + block(finish("'B'"))], "A"),
    Fixture("repeated_capture", [block(finish("'A'") + "\n" + finish("'B'"))], "B"),
    Fixture("capture_then_error", [block(finish("'captured'") + "\nraise ValueError('after capture')")], "captured"),
    Fixture("caught_exception", [block("try:\n    int('bad')\nexcept ValueError:\n    x = 'incomplete'\n" + finish("x"))], "incomplete"),
    Fixture("uncaught_recovery", [block("raise ValueError('broken')"), block(finish("'recovered'"))], "recovered"),
    Fixture("mutable_snapshot", [block("x = [1]\nprint(x)"), block("x.append(2)\n" + finish("x"))], "[1, 2]"),
    Fixture("truncated_feedback", [block("print('x' * 25000)\nraise ValueError('TAIL_MARKER')"), block(finish("'done'"))], "done"),
    Fixture("iteration_default", [block("x = 1"), block(finish("'never executed'"))], block(finish("'never executed'")), iterations=1),
    Fixture("depth_fallback", [block("x = rlm_query('fixture-child-a', 'a')\n" + finish("x"))], "leaf", children={"fixture-child-a": [block("x = rlm_query('leaf-instruction', 'leaf context')\n" + finish("x"))]}, plain={"leaf-instruction": "leaf"}),
    Fixture("provider_error", [block("x = llm_query('plain-error')\n" + finish("x"))], "Error: synthetic provider failure", plain={"plain-error": "!ERROR"}),
    Fixture("cancel", ["!CANCEL"], None, error="CancellationError"),
    Fixture("duplicate_plain_slots", [block("x = llm_query_batched(['repeat', 'repeat'])\n" + finish("'|'.join(x)"))], "R|R", plain={"repeat": "R"}),
    Fixture("reordered_plain_slots", [block("x = llm_query_batched(['slow', 'fast'])\n" + finish("'|'.join(x)"))], "S|F", plain={"slow": "S", "fast": "F"}, delays={"slow": 0.05}),
    Fixture("duplicate_recursive_slots", [block("x = rlm_query_batched([('fixture-child-a', 'same'), ('fixture-child-a', 'same')])\n" + finish("'|'.join(x)"))], "A|A", children={"fixture-child-a": [block(finish("'A'")), block(finish("'A'"))]}),
    Fixture("capture_then_mutate", [block("x = [1]\n" + finish("x") + "\nx.append(2)")], "[1]"),
    Fixture("rebound_answer", [block("answer = {'content': 'rebound', 'ready': True}")], "rebound"),
]
