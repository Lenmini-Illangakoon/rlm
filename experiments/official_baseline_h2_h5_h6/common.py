import hashlib
import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
REPO = WORKSPACE.parents[1]
PIN = "e11f1a8f8ee4490686e16dd6463233abe08a07eb"
BRANCH = "experiment/official-rlm-h2-h5-h6-baseline"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode())


def preserved_hashes() -> dict[str, str]:
    archive = json.loads((REPO / "research/rootcheck/m2/environment-current.json").read_text())
    paths = [REPO / row['path'] for row in archive['baseline_source_files']]
    paths += [p for p in (REPO / "research/rootcheck/m2").rglob('*') if p.is_file()]
    paths += [REPO / "experiments/m2/smoke_test.py"]
    for row in archive['baseline_source_files']:
        if sha((REPO / row['path']).read_bytes()) != row['archive_time_working_sha256']:
            raise ValueError(f"Pinned source mismatch: {row['path']}")
    return {p.relative_to(REPO).as_posix(): sha(p.read_bytes()) for p in paths}
