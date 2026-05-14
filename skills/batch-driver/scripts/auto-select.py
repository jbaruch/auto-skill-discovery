#!/usr/bin/env python3
"""Auto-pick the top-confidence skill target from a discovery.json for batch mode.

Reads a discovery.json path as the first arg. Picks the highest-`confidence`
target (ties broken by listed order) and writes a `selection.json` alongside the
discovery file with `selection_status: "selected"` and a rationale noting the
auto-pick — so manual review later can distinguish auto-picks from human picks
in the same shape.

Skips with verdict != BUILD: writes nothing, prints a short note to stderr, exits
0 (no usable target is not an error in batch mode — the batch summary records it).

Stdout: the absolute path of the written selection.json (or empty on skip).
Stderr: a short status line.
Exit 0 on success or non-BUILD skip; 2 on usage / missing-file errors.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any


def fail(msg: str) -> None:
    print(f"auto-select.py: {msg}", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    if len(sys.argv) < 2:
        fail("usage: auto-select.py <discovery.json>")

    disc_path = Path(sys.argv[1]).resolve()
    if not disc_path.is_file():
        fail(f"discovery file not found: {disc_path}")
    try:
        disc = json.loads(disc_path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {disc_path}: {exc}")

    verdict = disc.get("verdict")
    if verdict != "BUILD":
        print(f"auto-select.py: verdict={verdict!r}; nothing to pick", file=sys.stderr)
        return 0

    targets: list[dict[str, Any]] = disc.get("skill_targets") or []
    eligible = [t for t in targets if isinstance(t.get("confidence"), (int, float)) and t["confidence"] >= 0.5]
    if not eligible:
        print("auto-select.py: BUILD verdict but no target with confidence >= 0.5", file=sys.stderr)
        return 0

    top = max(eligible, key=lambda t: t["confidence"])

    selection = {
        "schema_version": 1,
        "discovery_path": str(disc_path),
        "selected_target_id": top["id"],
        "selection_status": "selected",
        "selection_rationale": (
            f"Auto-selected in batch mode: top-confidence target "
            f"(confidence={top['confidence']:.2f}). No human gate."
        ),
        "selected_at": dt.datetime.now(dt.UTC).isoformat(),
        "auto_selected": True,
    }

    sel_path = disc_path.parent / "selection.json"
    sel_path.write_text(json.dumps(selection, indent=2) + "\n")
    print(f"auto-select.py: picked {top['id']!r} (confidence={top['confidence']:.2f})", file=sys.stderr)
    print(str(sel_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
