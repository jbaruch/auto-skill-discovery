#!/usr/bin/env python3
"""Compute per-scenario and aggregate lift from baseline + with-skill eval runs.

Reads two eval result files (paths as positional args): baseline first,
with-skill second. Each file must conform to the shape:

    {
      "mode": "baseline | with_skill",
      "scenarios": [
        {"id": "scn_01", "score": 0.62, ...}
      ],
      "aggregate_score": 0.58
    }

Emits a lift JSON on stdout:

    {
      "per_scenario_lift": [
        {"id": "scn_01", "baseline": 0.62, "with_skill": 0.91, "lift": 0.29}
      ],
      "aggregate_lift": 0.23,
      "aggregate_baseline": 0.58,
      "aggregate_with_skill": 0.81,
      "near_zero_scenarios": ["scn_03"]
    }

`near_zero_scenarios` collects ids where |lift| < NEAR_ZERO_THRESHOLD — these are
flagged per `rules/plugin-evals.md` § Lift, Not Attainment for follow-up review
(coincidence-with-baseline, leaked technique, or universal-competence criteria).

Exit 0 on success; 2 on usage / file errors; 3 if the two files disagree on
scenario set (different ids).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

NEAR_ZERO_THRESHOLD = 0.05


def fail(code: int, msg: str) -> None:
    print(f"compute-lift.py: {msg}", file=sys.stderr)
    sys.exit(code)


def load_results(path: Path, expected_mode: str) -> dict[str, Any]:
    if not path.is_file():
        fail(2, f"results file not found: {path}")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(2, f"invalid JSON in {path}: {exc}")
    mode = data.get("mode")
    if mode != expected_mode:
        fail(2, f"expected mode={expected_mode!r} in {path}, got {mode!r}")
    return data


def index_by_id(scenarios: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for s in scenarios:
        sid = s.get("id")
        if not sid:
            fail(2, f"scenario missing id: {s}")
        out[sid] = s
    return out


def main() -> int:
    if len(sys.argv) < 3:
        fail(2, "usage: compute-lift.py <baseline-results.json> <with-skill-results.json>")

    baseline = load_results(Path(sys.argv[1]), "baseline")
    with_skill = load_results(Path(sys.argv[2]), "with_skill")

    b_idx = index_by_id(baseline.get("scenarios") or [])
    w_idx = index_by_id(with_skill.get("scenarios") or [])

    if set(b_idx.keys()) != set(w_idx.keys()):
        only_b = sorted(set(b_idx) - set(w_idx))
        only_w = sorted(set(w_idx) - set(b_idx))
        fail(3, f"scenario id mismatch — only in baseline: {only_b}; only in with-skill: {only_w}")

    per_scenario: list[dict[str, Any]] = []
    near_zero: list[str] = []
    for sid in sorted(b_idx):
        b_score = float(b_idx[sid].get("score") or 0.0)
        w_score = float(w_idx[sid].get("score") or 0.0)
        lift = w_score - b_score
        per_scenario.append({
            "id": sid,
            "baseline": b_score,
            "with_skill": w_score,
            "lift": round(lift, 4),
        })
        if abs(lift) < NEAR_ZERO_THRESHOLD:
            near_zero.append(sid)

    agg_baseline = float(baseline.get("aggregate_score") or 0.0)
    agg_with = float(with_skill.get("aggregate_score") or 0.0)

    report = {
        "per_scenario_lift": per_scenario,
        "aggregate_lift": round(agg_with - agg_baseline, 4),
        "aggregate_baseline": round(agg_baseline, 4),
        "aggregate_with_skill": round(agg_with, 4),
        "near_zero_scenarios": near_zero,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
