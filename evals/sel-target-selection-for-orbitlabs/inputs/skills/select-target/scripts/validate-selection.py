#!/usr/bin/env python3
"""Validate a selection.json artifact against its linked discovery.json.

Reads a selection file path as the first argument; loads the linked discovery
file referenced by `discovery_path`; checks `selected_target_id` (when present)
references a real entry in `discovery.skill_targets[]`. Prints a JSON
validation report; exits 0 on success, 1 on validation failure, 2 on usage error.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_STATUS = {"selected", "skipped"}


def fail(msg: str) -> None:
    print(f"validate-selection.py: {msg}", file=sys.stderr)
    sys.exit(2)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"file not found: {path}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def collect_errors(sel: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if sel.get("schema_version") != 1:
        errors.append(f"schema_version must be 1, got {sel.get('schema_version')!r}")

    status = sel.get("selection_status")
    if status not in ALLOWED_STATUS:
        errors.append(f"selection_status must be in {sorted(ALLOWED_STATUS)}, got {status!r}")

    if status == "selected":
        if not sel.get("selected_target_id"):
            errors.append("selection_status=selected requires selected_target_id")
    elif status == "skipped":
        if sel.get("selected_target_id"):
            errors.append("selection_status=skipped must not have selected_target_id")
        if not sel.get("selection_rationale"):
            errors.append("selection_status=skipped requires selection_rationale")

    if not sel.get("discovery_path"):
        errors.append("missing discovery_path")
    if not sel.get("selected_at"):
        errors.append("missing selected_at")

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        fail("usage: validate-selection.py <selection.json>")

    sel_path = Path(sys.argv[1])
    sel = load_json(sel_path)
    errors = collect_errors(sel)

    discovery_path_str = sel.get("discovery_path")
    target_ids: set[str] = set()
    if discovery_path_str:
        disc_path = Path(discovery_path_str)
        if not disc_path.is_file():
            errors.append(f"discovery_path references missing file: {disc_path}")
        else:
            try:
                disc = json.loads(disc_path.read_text())
            except json.JSONDecodeError as exc:
                errors.append(f"discovery_path file is not valid JSON: {exc}")
            else:
                target_ids = {
                    t.get("id")
                    for t in (disc.get("skill_targets") or [])
                    if t.get("id")
                }
                if sel.get("selection_status") == "selected":
                    target_id = sel.get("selected_target_id")
                    if target_id and target_id not in target_ids:
                        errors.append(
                            f"selected_target_id {target_id!r} not in discovery.skill_targets[]; "
                            f"available: {sorted(target_ids)}"
                        )

    report = {
        "ok": not errors,
        "errors": errors,
        "selection_status": sel.get("selection_status"),
        "selected_target_id": sel.get("selected_target_id"),
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
