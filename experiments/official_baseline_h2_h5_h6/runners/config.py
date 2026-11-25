"""Frozen pilot order, transport validation, and engineering-only progression gates."""

import json

from ..common import WORKSPACE, sha

PILOT_ORDER = ("S1-R01", "S2-R01", "S3-R01", "S2-R02", "S3-R02", "S1-R02",
               "S3-R03", "S1-R03", "S2-R03")


def load_config():
    return json.loads((WORKSPACE / "runners/pilot.json").read_text(encoding="utf-8"))


def load_task(scenario: str) -> tuple[str, str]:
    manifest = json.loads((WORKSPACE / "tasks/dataset_manifest.json").read_text(encoding="utf-8"))
    entry = manifest["scenarios"][scenario]
    values = []
    for name in ("context", "query"):
        data = (WORKSPACE / "tasks/data" / scenario / (name + ".txt")).read_bytes()
        if sha(data) != entry[name + "_sha256"]:
            raise ValueError(f"Frozen {scenario} {name} checksum mismatch")
        values.append(data.decode("utf-8"))
    return tuple(values)


def progression(records: list[dict], engineering_checkpoint_passed=False) -> str:
    if [r["pilot_id"] for r in records] != list(PILOT_ORDER[:len(records)]):
        raise ValueError("Pilot order changed or a failed run was omitted")
    threshold = load_config()["excessive_censoring_stop_count"]
    if threshold is None:
        return "blocked_missing_approved_censoring_threshold"
    if len(records) in (3, 6, 9) and sum(r["status"] == "resource_censored" for r in records) >= threshold:
        return "stop_excessive_resource_censoring"
    if len(records) >= 3 and not engineering_checkpoint_passed:
        return "stop_for_round_one_engineering_review"
    return "complete" if len(records) == 9 else PILOT_ORDER[len(records)]
