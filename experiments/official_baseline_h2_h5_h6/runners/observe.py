"""Passive wrappers around the pinned methods; no injected feedback or validation."""

import contextvars
import time
import uuid
from contextlib import ExitStack
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from unittest.mock import patch

NODE = contextvars.ContextVar("observed_node", default=None)
ACTION = contextvars.ContextVar("observed_action", default=None)
SLOT = contextvars.ContextVar("observed_slot", default=None)
BATCH = contextvars.ContextVar("observed_batch", default=None)


def snapshot(value, seen=None):
    """Copy exact builtin containers only. Never invoke user repr/str/deepcopy hooks."""
    if type(value) in (str, int, float, bool, type(None)):
        return value
    seen = set() if seen is None else seen
    if id(value) in seen:
        return {"unobserved": "cycle"}
    seen = seen | {id(value)}
    if type(value) in (list, tuple):
        return [snapshot(v, seen) for v in value]
    if type(value) is dict:
        return {k: snapshot(v, seen) for k, v in value.items() if type(k) is str}
    return {"unobserved": "non-builtin value"}


class Observer:
    def __init__(self, sink=None):
        self.run_id = "mock-" + uuid.uuid4().hex
        self.events = []
        self.lock = Lock()
        self.nodes = {}
        self.env_nodes = {}
        self.transports = {}
        self.stack = ExitStack()
        self.sink = sink

    def emit(self, kind, **data):
        with self.lock:
            seq = len(self.events) + 1
            row = {"run_id": self.run_id, "event_id": f"{self.run_id}:e{seq:05d}",
                   "seq": seq, "monotonic_ns": time.perf_counter_ns(), "kind": kind,
                   "node": NODE.get(), "action": ACTION.get(), "slot": SLOT.get(), **snapshot(data)}
            self.events.append(row)
            if self.sink:
                self.sink(row)
            return row["event_id"]

    def install(self):
        from rlm.core import rlm as core
        from rlm.core import comms_utils
        from rlm.core.lm_handler import LMRequestHandler
        from rlm.environments.local_repl import LocalREPL, _AnswerDict
        from rlm.logger import RLMLogger

        completion = core.RLM.completion
        subcall = core.RLM._subcall
        environment = core.get_environment
        execute = LocalREPL.execute_code
        capture = LocalREPL._capture_answer
        cleanup = LocalREPL.cleanup
        restore = LocalREPL._restore_scaffold
        log = RLMLogger.log
        format_iteration = core.format_iteration
        submit = ThreadPoolExecutor.submit
        socket_send = comms_utils.socket_send
        setitem = _AnswerDict.__setitem__

        def completion_wrapper(instance, *args, **kwargs):
            parent = NODE.get()
            node = self.emit("node_start", parent_node=parent, depth=instance.depth,
                             inputs={"args": args, "kwargs": kwargs})
            self.nodes[id(instance)] = node
            token = NODE.set(node)
            try:
                result = completion(instance, *args, **kwargs)
                self.emit("actual_return", content=result.response, model=result.root_model,
                          execution_time=result.execution_time, usage_summary=result.usage_summary.to_dict())
                return result
            except BaseException as exc:
                self.emit("node_failure", exception_type=type(exc).__name__)
                raise
            finally:
                NODE.reset(token)

        def subcall_wrapper(instance, instruction, context, model=None):
            token = NODE.set(self.nodes[id(instance)])
            route = "depth_limit_plain" if instance.depth + 1 >= instance.max_depth else "genuine_recursive"
            event = self.emit("recursive_dispatch", route=route, depth=instance.depth + 1,
                              instruction=instruction, context=context, model_override=model)
            action_token = ACTION.set(event)
            try:
                result = subcall(instance, instruction, context, model)
                self.emit("recursive_result", content=result.response, model=result.root_model,
                          execution_time=result.execution_time, metadata=result.metadata,
                          usage_summary=result.usage_summary.to_dict())
                return result
            finally:
                ACTION.reset(action_token)
                NODE.reset(token)

        def environment_wrapper(*args, **kwargs):
            env = environment(*args, **kwargs)
            self.env_nodes[id(env)] = NODE.get()
            return env

        def execute_wrapper(env, code):
            phase = "execution" if id(env) in self.env_nodes else "environment_setup"
            token = NODE.set(self.env_nodes.get(id(env), NODE.get()))
            action = self.emit("python_start", code=code, phase=phase)
            action_token = ACTION.set(action)
            try:
                result = execute(env, code)
                self.emit("python_result", stdout=result.stdout, stderr=result.stderr, phase=phase,
                          execution_time=result.execution_time,
                          locals=result.locals, final_answer=result.final_answer,
                          exception_detail="stderr is observed; exception object is not exposed")
                return result
            except BaseException as exc:
                self.emit("python_raised", exception_type=type(exc).__name__)
                raise
            finally:
                ACTION.reset(action_token)
                NODE.reset(token)

        def capture_wrapper(env, content):
            capture(env, content)  # official conversion once; observe the resulting immutable text
            self.emit("candidate_capture", content=env._last_final_answer)

        def cleanup_wrapper(env):
            try:
                return cleanup(env)
            finally:
                self.env_nodes.pop(id(env), None)

        def restore_wrapper(env):
            before = env._last_final_answer
            result = restore(env)
            if before is None and env._last_final_answer is not None:
                self.emit("candidate_capture", content=env._last_final_answer,
                          capture_path="scaffold_restoration")
            return result

        def setitem_wrapper(answer, key, value):
            self.emit("answer_write_attempt", key=key, value=value)
            return setitem(answer, key, value)

        def send_wrapper(sock, data):
            # Host-side correlation only: no changes to the bytes on the pinned protocol.
            if type(data) is dict and "depth" in data:
                with self.lock:
                    self.transports[sock.getsockname()] = (NODE.get(), ACTION.get())
            return socket_send(sock, data)

        def socket_handler_wrapper(original):
            def call(connection, request, handler):
                with self.lock:
                    node, action = self.transports.pop(connection.client_address, (None, None))
                nt, at = NODE.set(node), ACTION.set(action)
                bt = BATCH.set({"prompts": request.prompts, "next": 0} if request.is_batched else None)
                try:
                    self.emit("socket_request", request=request.to_dict(), correlation_known=action is not None)
                    return original(connection, request, handler)
                finally:
                    NODE.reset(nt)
                    ACTION.reset(at)
                    BATCH.reset(bt)
            return call

        def submit_wrapper(executor, fn, *args, **kwargs):
            # Only the pinned recursive batch closure; unrelated executors are untouched.
            if getattr(fn, "__qualname__", "") != "LocalREPL._rlm_query_batched.<locals>._run_subcall":
                return submit(executor, fn, *args, **kwargs)
            ctx = contextvars.copy_context()
            ctx.run(SLOT.set, args[0])
            return submit(executor, ctx.run, fn, *args, **kwargs)

        def log_wrapper(logger, iteration):
            self.emit("iteration_selection", selected=iteration.final_answer,
                      iteration=logger.iteration_count + 1, iteration_time=iteration.iteration_time,
                      code_block_count=len(iteration.code_blocks),
                      response=iteration.response, prompt=iteration.prompt)
            return log(logger, iteration)

        def format_wrapper(iteration):
            messages = format_iteration(iteration)  # official formatter exactly once
            self.emit('formatted_results', messages=messages,
                      visibility='prepared_for_next_prompt; provider_dispatch confirms delivery')
            return messages

        def helper_wrapper(name, original):
            def call(env, *args, **kwargs):
                batch = name.endswith("batched")
                event = self.emit("helper_start", helper=name, inputs={"args": args, "kwargs": kwargs},
                                  route="recursive" if "rlm" in name else "plain", batch=batch)
                token = ACTION.set(event)
                slot_token = SLOT.set(0 if batch and len(args[0] if args else next(iter(kwargs.values()))) == 1 else SLOT.get())
                try:
                    result = original(env, *args, **kwargs)
                    self.emit("helper_return", helper=name, result=result,
                              slots=[{"batch": event, "slot": i, "output": v} for i, v in enumerate(result)] if batch else None,
                              consumption="available to same-block Python; dependency requires code review")
                    return result
                finally:
                    SLOT.reset(slot_token)
                    ACTION.reset(token)
            return call

        def path_wrapper(name, original):
            def call(instance, *args, **kwargs):
                self.emit("finalization_path", path=name)
                return original(instance, *args, **kwargs)
            return call

        patches = [(core.RLM, "completion", completion_wrapper),
                   (core.RLM, "_subcall", subcall_wrapper),
                   (core, "get_environment", environment_wrapper),
                   (LocalREPL, "execute_code", execute_wrapper),
                   (LocalREPL, "_capture_answer", capture_wrapper),
                   (LocalREPL, "cleanup", cleanup_wrapper),
                   (LocalREPL, "_restore_scaffold", restore_wrapper),
                   (_AnswerDict, "__setitem__", setitem_wrapper),
                   (ThreadPoolExecutor, "submit", submit_wrapper),
                   (comms_utils, "socket_send", send_wrapper),
                   (core, "format_iteration", format_wrapper),
                   (RLMLogger, "log", log_wrapper)]
        for name in ("_handle_single", "_handle_batched"):
            patches.append((LMRequestHandler, name, socket_handler_wrapper(getattr(LMRequestHandler, name))))
        for name in ("_llm_query", "_llm_query_batched", "_rlm_query", "_rlm_query_batched"):
            patches.append((LocalREPL, name, helper_wrapper(name, getattr(LocalREPL, name))))
        for name in ("_default_answer", "_fallback_answer"):
            patches.append((core.RLM, name, path_wrapper(name, getattr(core.RLM, name))))
        for target, name, replacement in patches:
            self.stack.enter_context(patch.object(target, name, replacement))
        return self

    def close(self):
        self.stack.close()
