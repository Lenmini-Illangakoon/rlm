"""Independent solvers of serialized source; no imports from tasks/generate.py."""

import json
import re
from collections import defaultdict
from typing import Any

VERSION = "serialized-oracles-1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sections(data: bytes, explicit_ends: bool = False) -> dict[str, list[tuple[int, str]]]:
    result: dict[str, list[tuple[int, str]]] = {}
    active = None
    for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        marker = re.fullmatch(r"=== (.+) ===", line)
        if marker:
            name = marker.group(1)
            if name == "END" or name.startswith("End "):
                end_name = name.removeprefix("End ").removeprefix("of ")
                require(active is not None and (name == "END" or active == end_name), "Mismatched section end")
                active = None
            else:
                require(not explicit_ends or active is None, "Missing section end")
                require(name not in result, f"Duplicate section {name}")
                result[name] = []
                active = name
        else:
            require(active is not None, f"Record outside section at line {number}")
            result[active].append((number, line))
    require(active is None, "Unclosed final section")
    return result


def json_rows(lines: list[tuple[int, str]]) -> list[dict[str, Any]]:
    rows = []
    for number, line in lines:
        def unique_pairs(pairs):
            obj = {}
            for key, value in pairs:
                require(key not in obj, f"Duplicate JSON key {key} at {number}")
                obj[key] = value
            return obj
        obj = json.loads(line, object_pairs_hook=unique_pairs)
        require(isinstance(obj, dict), f"Expected record at {number}")
        rows.append({**obj, "source_line": number})
    return rows


def solve_s1(data: bytes) -> dict:
    parts = sections(data, explicit_ends=True)
    require(set(parts) == {"Orders", "Shipments", "Refunds"}, "S1 section coverage")
    records = {name: json_rows(lines) for name, lines in parts.items()}
    require([len(records[k]) for k in ("Orders", "Shipments", "Refunds")] == [100,194,194], "S1 counts")
    all_records = [r for group in records.values() for r in group]
    require(len({r['Record ID'] for r in all_records}) == len(all_records), "Duplicate Record ID")
    orders = {r["Order ID"]: r for r in records["Orders"]}
    require(len(orders) == 100, "Duplicate Order ID")
    shipped: dict[str, int] = defaultdict(int)
    refunded: dict[str, int] = defaultdict(int)
    for name, field, statuses, target in [
        ("Shipments", "Shipped Quantity", ("posted", "void"), shipped),
        ("Refunds", "Refunded Quantity", ("approved", "pending"), refunded),
    ]:
        for row in records[name]:
            require(type(row[field]) is int and row[field] > 0, "Invalid quantity")
            require(row["Status"] in statuses, "Invalid status")
            if row["Order ID"] in orders and row["Status"] == statuses[0]:
                target[row["Order ID"]] += row[field]
    balances = {}
    for key, row in orders.items():
        require(row["Status"] in ("open", "cancelled"), "Invalid order status")
        require(type(row["Ordered Quantity"]) is int and row["Ordered Quantity"] > 0, "Invalid ordered quantity")
        balance = row["Ordered Quantity"] - shipped[key] - refunded[key]
        require(balance >= 0, "Over-reconciled order")
        balances[key] = {"outstanding": balance, "status": row["Status"], "source_line": row["source_line"]}
    selected = sorted(k for k, v in balances.items() if v["status"] == "open" and v["outstanding"] > 0)
    return {"scenario": "S1", "selected_ids": selected, "total": sum(balances[k]["outstanding"] for k in selected),
            "record_counts": {k: len(v) for k,v in records.items()}, "balances": balances}


def solve_s2(data: bytes) -> dict:
    require(not data.startswith(b"\xef\xbb\xbf") and b"\r" not in data, "S2 encoding")
    require(data.endswith(b"\n") and not data.endswith(b"\n\n") and b"\n\n" not in data, "S2 line endings")
    parts = sections(data, explicit_ends=True)
    names = ["Shipment Requests", "Warehouse Inventory", "Quality Release", "Dispatch Holds", "Archived Shipments"]
    require(list(parts) == names, "S2 section order")
    patterns = {
        "R": [r"Request (SH-\d{5}): (\d+) units requested\.", r"(SH-\d{5}) requires shipment of (\d+) units\."],
        "W": [r"Warehouse stock for (SH-\d{5}): (\d+) units available\.", r"Available quantity for (SH-\d{5}) is (\d+) units\."],
        "Q": [r"Quality decision for (SH-\d{5}): (APPROVED|PENDING)\.", r"(SH-\d{5}) has quality status (APPROVED|PENDING)\."],
        "H": [r"Dispatch hold status for (SH-\d{5}): (NONE|ACTIVE)\.", r"(SH-\d{5}): dispatch status (NONE|ACTIVE)\."],
    }
    parsed: dict[str, dict] = {}
    for section, prefix in zip(names[:4], "RWQH"):
        require(len(parts[section]) == 160, f"S2 coverage: {section}")
        table = {}
        for line_no, line in parts[section]:
            source, body = line.split(" | ", 1)
            require(re.fullmatch(prefix + r"-\d{3}", source) is not None, "Invalid source ID")
            matches = [m for pat in patterns[prefix] if (m := re.fullmatch(pat, body))]
            require(len(matches) == 1, f"Unparsed/ambiguous note at {line_no}")
            shipment, value = matches[0].groups()
            require(shipment not in table, "Duplicate shipment note")
            require(int(source[2:]) == int(shipment[3:]) - 10000, "Source ID association")
            table[shipment] = {"value": int(value) if prefix in "RW" else value, "source_id": source, "source_line": line_no}
        require(len({x['source_id'] for x in table.values()}) == 160, "Duplicate source")
        parsed[prefix] = table
    ids = set(parsed["R"])
    require(all(set(t) == ids for t in parsed.values()), "Incomplete join")
    require(len(parts[names[4]]) == 8, "Archive coverage")
    archive_ids = []
    for line_no, line in parts[names[4]]:
        m = re.fullmatch(r"(A-\d{3}) \| Archived (SH-\d{5}): requested (\d+) units; available (\d+) units; quality APPROVED; hold NONE\.", line)
        require(m is not None, f"Invalid archive {line_no}")
        source, shipment, q, a = m.groups()
        require(shipment not in ids, "Archive/current overlap")
        require(int(source[2:]) == int(shipment[3:]) - 90000, "Archive association")
        archive_ids.append(shipment)
    require(len(set(archive_ids)) == 8, "Duplicate archive")
    joined = {}
    for shipment in sorted(ids):
        row = {p: parsed[p][shipment] for p in "RWQH"}
        eligible = row['R']['value'] > 0 and row['W']['value'] >= row['R']['value'] and row['Q']['value'] == 'APPROVED' and row['H']['value'] == 'NONE'
        joined[shipment] = {"requested": row['R']['value'], "available": row['W']['value'], "quality": row['Q']['value'], "hold": row['H']['value'], "eligible": eligible,
                            "sources": [row[p]['source_id'] for p in "RWQH"], "source_lines": [row[p]['source_line'] for p in "RWQH"]}
    ranked = sorted((k for k,v in joined.items() if v['eligible']), key=lambda k: (-joined[k]['requested'], int(k[3:])))
    selected = [{"id": k, "requested": joined[k]['requested'], "sources": joined[k]['sources']} for k in ranked[:3]]
    return {"scenario": "S2-v2", "selected": selected, "total": sum(x['requested'] for x in selected), "eligible_count": len(ranked), "ranked_ids": ranked, "joined": joined, "excluded_archives": sorted(archive_ids)}


def solve_s3(data: bytes) -> dict:
    parts = sections(data)
    require({k: len(v) for k,v in parts.items()} == {"Product Inventory": 320, "Archived Products": 4, "Planned Products": 4}, "S3 coverage")
    records = {name: json_rows(lines) for name,lines in parts.items()}
    all_ids = [r['Product ID'] for group in records.values() for r in group]
    require(all(type(x) is int for x in all_ids) and len(set(all_ids)) == 328, "S3 ID integrity")
    eligible = [r for r in records['Product Inventory'] if r['Status'] == 'ACTIVE' and r['Region'] == 'APAC']
    ordered = sorted(eligible, key=lambda r: r['Product ID'])
    ids = [r['Product ID'] for r in ordered[:2]]
    require(len(ids) == 2, "Insufficient eligible records")
    return {"scenario": "S3", "selected_ids": ids, "product": ids[0]*ids[1], "eligible_count": len(eligible), "ranked_ids": [r['Product ID'] for r in ordered], "source_lines": [r['source_line'] for r in ordered[:2]], "record_counts": {k:len(v) for k,v in records.items()}}


SOLVERS = {"S1": solve_s1, "S2-v2": solve_s2, "S3": solve_s3}


def score_answer(scenario: str, extracted_answer: dict, oracle: dict) -> dict:
    """Score a documented extraction of the ACTUAL return; never infer H5-S/V."""
    fields = {"S1": ("selected_ids", "total"), "S2-v2": ("selected", "total"), "S3": ("selected_ids", "product")}[scenario]
    missing = [key for key in fields if key not in extracted_answer]
    if scenario == "S2-v2" and "selected" in extracted_answer:
        if len(extracted_answer['selected']) != 3:
            missing.append('exactly_three_selected_rows')
        for i, row in enumerate(extracted_answer['selected']):
            missing.extend(f"selected[{i}].{key}" for key in ('id','requested','sources') if key not in row)
            if 'sources' in row and len(row['sources']) != 4:
                missing.append(f"selected[{i}].four_source_ids")
    if scenario == "S3" and "selected_ids" in extracted_answer and len(extracted_answer['selected_ids']) != 2:
        missing.append('two_product_ids')
    matches = {k: extracted_answer.get(k) == oracle[k] for k in fields}
    return {"correctness": "correct" if all(matches.values()) else "incorrect", "output_coverage": "incomplete" if missing else "complete", "missing": missing, "field_matches": matches,
            "support": "human_review_required", "visibility": "human_review_required", "raw_return_reference_required": True}
