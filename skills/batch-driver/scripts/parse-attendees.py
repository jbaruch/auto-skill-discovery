#!/usr/bin/env python3
"""Parse and normalize an attendee CSV into a JSON list of company records.

Reads a CSV path as the first arg. Expected header (case-insensitive): a column
named `company` is required; `domain` is optional. Empty cells, duplicate rows
(by lowercased company name), and rows with non-printable characters are
dropped with a counter recorded in the stderr summary.

Stdout: JSON array of {slug, company_name, domain} records.
Stderr: a JSON summary `{ok, kept_rows, dropped_rows, reasons}`.

Exit 0 with stdout = JSON array when at least one row is kept; non-zero if no
rows usable.
"""

from __future__ import annotations

import csv
import json
import re
import string
import sys
from pathlib import Path
from typing import Any

PRINTABLE = set(string.printable)


def fail(code: int, msg: str) -> None:
    print(f"parse-attendees.py: {msg}", file=sys.stderr)
    sys.exit(code)


def slugify(name: str) -> str:
    """Lowercase, replace non-alphanumeric runs with single dash, strip edges."""
    s = re.sub(r"[^A-Za-z0-9]+", "-", name.lower()).strip("-")
    return s or "unknown"


def is_printable(text: str) -> bool:
    return all(ch in PRINTABLE or ch.isspace() for ch in text)


def main() -> int:
    if len(sys.argv) < 2:
        fail(2, "usage: parse-attendees.py <csv-path>")

    csv_path = Path(sys.argv[1])
    if not csv_path.is_file():
        fail(2, f"csv not found: {csv_path}")

    kept: list[dict[str, Any]] = []
    seen_slugs: set[str] = set()
    drop_reasons: dict[str, int] = {"empty_company": 0, "non_printable": 0, "duplicate": 0}

    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            fail(2, "csv has no header row")
        # Normalize header lookup (case-insensitive)
        header_map = {h.lower().strip(): h for h in reader.fieldnames if h}
        if "company" not in header_map:
            fail(2, f"csv missing required 'company' column; got headers: {reader.fieldnames}")
        company_col = header_map["company"]
        domain_col = header_map.get("domain")

        for row in reader:
            company = (row.get(company_col) or "").strip()
            if not company:
                drop_reasons["empty_company"] += 1
                continue
            if not is_printable(company):
                drop_reasons["non_printable"] += 1
                continue
            slug = slugify(company)
            if slug in seen_slugs:
                drop_reasons["duplicate"] += 1
                continue
            seen_slugs.add(slug)
            domain = (row.get(domain_col) or "").strip() if domain_col else ""
            kept.append({
                "slug": slug,
                "company_name": company,
                "domain": domain,
            })

    summary = {
        "ok": bool(kept),
        "kept_rows": len(kept),
        "dropped_rows": sum(drop_reasons.values()),
        "reasons": drop_reasons,
    }
    print(json.dumps(summary), file=sys.stderr)
    print(json.dumps(kept, indent=2))

    return 0 if kept else 1


if __name__ == "__main__":
    sys.exit(main())
