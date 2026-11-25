"""Worker-side BaseLM transport only. No provider, budget or credential access."""

import asyncio
import hashlib
import json
import os
import time
import uuid
from pathlib import Path
from threading import Lock
from unittest.mock import patch

from .offline_guard import install

install()

from rlm.clients.base_lm import BaseLM
from rlm.core import rlm as core
from rlm.core.types import ModelUsageSummary, UsageSummary
from rlm.logger import RLMLogger

from .config import load_config
from .observe import ACTION, BATCH, NODE, SLOT, Observer


class BrokerClient(BaseLM):
    def __init__(self, mailbox, observer, synthetic_only, **kwargs):
        super().__init__(**kwargs)
        self.mailbox, self.observer = Path(mailbox), observer
        self.owner, self.synthetic_only = NODE.get(), synthetic_only
        self.lock = Lock()
        self.usage = {}
        self.last = ModelUsageSummary(0, 0, 0)

    def completion(self, prompt, model=None):
        selected = model or self.model_name
        identifier = uuid.uuid4().hex
        request = {'model': selected, 'prompt': prompt, 'sampling_args': self.sampling_args,
                   'node': NODE.get(), 'action': ACTION.get(), 'slot': SLOT.get()}
        temporary = self.mailbox / 'inbox' / (identifier + '.tmp')
        temporary.write_text(json.dumps(request, ensure_ascii=False), encoding='utf-8')
        os.replace(temporary, temporary.with_suffix('.json'))
        response_path = self.mailbox / 'outbox' / (identifier + '.json')
        # Parent terminates the Job on budget denial/deadline. Never synthesize
        # a recoverable helper error from an admission refusal.
        admitted = self.mailbox / 'outbox' / (identifier + '.admitted.json')
        while not admitted.exists():
            time.sleep(0.01)
        dispatch = self.observer.emit('provider_dispatch', request_id=identifier, model=selected,
                                      provider='external_broker', owner_node=self.owner, request=prompt,
                                      causal_action=ACTION.get(), usage_is_synthetic=self.synthetic_only)
        started = time.perf_counter_ns()
        while not response_path.exists():
            time.sleep(0.01)
        response = json.loads(response_path.read_text(encoding='utf-8'))
        usage = response['usage']
        with self.lock:
            row = self.usage.setdefault(selected, [0, 0, 0, 0.0])
            row[0] += 1
            row[1] += usage['prompt_tokens']
            row[2] += usage['completion_tokens']
            cost = float(usage.get('cost') or 0)
            row[3] += cost
            self.last = ModelUsageSummary(1, usage['prompt_tokens'], usage['completion_tokens'], cost or None)
        self.observer.emit('provider_return', dispatch=dispatch, request_id=identifier,
                           content=response['content'], elapsed_ns=time.perf_counter_ns() - started,
                           usage={'input_tokens': usage['prompt_tokens'], 'output_tokens': usage['completion_tokens']})
        return response['content']

    async def acompletion(self, prompt, model=None):
        batch = BATCH.get()
        slot = SLOT.get()
        if batch:
            slot = batch['next']
            if batch['prompts'][slot] != prompt:
                raise RuntimeError('Pinned batch invocation order changed')
            batch['next'] += 1
        token = SLOT.set(slot)
        try:
            return await asyncio.to_thread(self.completion, prompt, model)
        finally:
            SLOT.reset(token)

    def get_usage_summary(self):
        with self.lock:
            return UsageSummary({model: ModelUsageSummary(*values[:3], values[3] or None)
                                 for model, values in self.usage.items()})

    def get_last_usage(self):
        return self.last


def run(request, work):
    config = load_config()
    # Flush every event so a parent stop still leaves an observed prefix.
    with (work / 'events.jsonl').open('w', encoding='utf-8') as stream:
        def sink(event):
            stream.write(json.dumps(event, ensure_ascii=False) + '\n')
            stream.flush()

        observer = Observer(sink=sink)
        logger = RLMLogger()
        repo = Path(core.__file__).resolve().parents[2]
        actual_hashes = {name: hashlib.sha256((repo / name).read_bytes()).hexdigest()
                         for name in request['runtime_hashes']}
        if not actual_hashes or actual_hashes != request['runtime_hashes'] or config['rootcheck']:
            raise RuntimeError('Pinned runtime identity or RootCheck gate mismatch')

        def client(backend, kwargs):
            if backend != config['provider']:
                raise ValueError('Unexpected provider selected by pinned RLM')
            return BrokerClient(request['mailbox'], observer, request['synthetic_only'], **kwargs)

        observer.install()
        runtime = None
        try:
            with patch.object(core, 'get_client', client):
                runtime = core.RLM(
                    backend=config['provider'], backend_kwargs={'model_name': config['root_model']},
                    other_backends=[config['provider']],
                    other_backend_kwargs=[{'model_name': config['plain_depth_one_model']}],
                    environment=config['environment'], max_depth=config['max_depth'],
                    max_iterations=config['max_iterations_per_instance'],
                    experimental_spec_ptc=config['experimental_spec_ptc'],
                    persistent=config['persistent'], compaction=config['compaction'],
                    max_concurrent_subcalls=config['recursive_concurrency'],
                    sampling_args={'max_tokens': config['completion_tokens_per_request']},
                    sub_sampling_args={'max_tokens': config['completion_tokens_per_request']},
                    logger=logger, verbose=False,
                )
                if type(runtime) is not core.RLM or type(runtime).__module__ != 'rlm.core.rlm':
                    raise RuntimeError('Unexpected imported runtime class')
                observer.emit('runtime_identity', class_module=type(runtime).__module__,
                              class_name=type(runtime).__qualname__, source_file=str(Path(core.__file__).resolve()),
                              source_hashes=actual_hashes, rootcheck=False, boundary='appcontainer-job')
                result = runtime.completion(request['context'], root_prompt=request['query'])
                return {'response': result.response, 'trajectory': logger.get_trajectory(),
                        'execution_time': result.execution_time, 'iteration_count': logger.iteration_count,
                        'usage_summary': result.usage_summary.to_dict()}
        finally:
            if runtime:
                runtime.close()
            observer.close()
