"""AppContainer compatibility for CPython's private (mode 0700) temp directories.

Preserve exclusive randomized creation, but inherit the scratch directory's
container ACL. Never alter an RLM file or create directories outside scratch.
"""

import os
import sys
import tempfile
from pathlib import Path


def install(scratch: Path, container_sid: str):
    def mkdtemp(suffix=None, prefix=None, dir=None):
        # Same CPython naming/exclusive-create algorithm. Mode 0777 on Windows
        # inherits the already restricted scratch ACL instead of installing a
        # user-only 0700 DACL that excludes the creating AppContainer itself.
        prefix, suffix, directory, output_type = tempfile._sanitize_params(prefix, suffix, dir)
        if output_type is not str:
            raise TypeError('The RLM isolation adapter supports string temp paths')
        if not Path(directory).resolve().is_relative_to(scratch.resolve()):
            raise PermissionError('Temporary directories must remain inside isolated scratch')
        names = tempfile._get_candidate_names()
        for _ in range(tempfile.TMP_MAX):
            name = os.path.join(directory, prefix + next(names) + suffix)
            sys.audit('tempfile.mkdtemp', name)
            try:
                os.mkdir(name, 0o777)
            except FileExistsError:
                continue
            return os.path.abspath(name)
        raise FileExistsError('No usable temporary directory name')

    tempfile.mkdtemp = mkdtemp
