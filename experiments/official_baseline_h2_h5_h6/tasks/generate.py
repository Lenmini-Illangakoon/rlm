"""S2-v2 rendering only: no selection/oracle logic."""

import hashlib

VERSION = "S2-v2.1-renderer"
SECTIONS = (
    "Shipment Requests", "Warehouse Inventory", "Quality Release", "Dispatch Holds",
    "Archived Shipments",
)
S2_QUERY = """Using the current Shipment Requests, Warehouse Inventory, Quality Release,
and Dispatch Holds sections, identify the three eligible shipments with the
largest requested quantities.

There are 160 current shipments, each with exactly one note in each of those
four sections. Match notes only by exact Shipment ID. A shipment is eligible
when its requested quantity is positive, its available quantity is at least
its requested quantity, its quality status is APPROVED, and its dispatch
hold status is NONE. Archived Shipments are out of scope.

Rank eligible shipments by requested quantity descending, breaking ties by
numeric Shipment ID ascending. Return exactly three Shipment IDs in that
order, each requested quantity, and the combined requested quantity.

For each selected shipment, also give the four source IDs identifying its
request, inventory, quality, and hold notes. Formatting is flexible, but all
requested values and source IDs must be present.
"""
S3_SPEC = """Input specification: Product Inventory contains exactly 320 records,
Archived Products contains exactly 4 records, and Planned Products contains
exactly 4 records. Each record occupies one valid JSON line between its
section markers. Product IDs are unique across the supplied records.
"""


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_s2() -> bytes:
    notes: dict[str, list[tuple[str, str]]] = {name: [] for name in SECTIONS}
    order = sorted(range(1, 161), key=lambda k: (digest(f"RC-S2-v2|id|{k:03d}"), k))
    for i, k in enumerate(order, 1):
        shipment = f"SH-{10000 + k:05d}"
        q = 6809 if i == 156 else 1000 + 37 * i
        a = q - 1 if i % 5 == 0 else q + 50
        quality = "PENDING" if i % 7 == 0 else "APPROVED"
        hold = "ACTIVE" if i % 11 == 0 else "NONE"
        odd = (
            f"Request {shipment}: {q} units requested.",
            f"Warehouse stock for {shipment}: {a} units available.",
            f"Quality decision for {shipment}: {quality}.",
            f"Dispatch hold status for {shipment}: {hold}.",
        )
        even = (
            f"{shipment} requires shipment of {q} units.",
            f"Available quantity for {shipment} is {a} units.",
            f"{shipment} has quality status {quality}.",
            f"{shipment}: dispatch status {hold}.",
        )
        for section, prefix, body in zip(SECTIONS[:4], "RWQH", odd if k % 2 else even):
            source = f"{prefix}-{k:03d}"
            notes[section].append((source, f"{source} | {body}"))
    for j in range(1, 9):
        source = f"A-{j:03d}"
        notes[SECTIONS[4]].append((source,
            f"{source} | Archived SH-{90000+j:05d}: requested {20000+j} units; "
            f"available {20050+j} units; quality APPROVED; hold NONE."))
    lines = []
    for section in SECTIONS:
        lines.append(f"=== {section} ===")
        for _, text in sorted(notes[section], key=lambda item: (
            digest(f"RC-S2-v2|{section}|{item[0]}"), item[0]
        )):
            lines.append(text)
        lines.append(f"=== End {section} ===")
    return ("\n".join(lines) + "\n").encode("utf-8")
