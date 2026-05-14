#!/usr/bin/env python3
"""Audit eval scenarios for bleeding (criterion literals leaking into task text).

Reads a scenarios.json file (path as first arg). For each scenario, checks every
criterion's expected literal against the task description for verbatim matches.
Emits a JSON report on stdout; exits 0 on clean audit, 1 on violations found, 2
on usage error.

Scenarios schema assumed:

    {
      "scenarios": [
        {
          "id": "scn_01",
          "task": "<task description>",
          "criteria": [
            {"id": "crit_01", "expected": "<literal expected in output>", ...}
          ]
        }
      ]
    }

A bleeding violation is recorded when `criterion["expected"]` (after lowercase +
whitespace-collapse normalization) appears verbatim in `scenario["task"]` after
the same normalization. The check is intentionally strict on substrings of >=4
words — shorter expected literals are too likely to coincide with task vocabulary
(e.g., "POST /v1/charges") and would generate false-positive violations.

Contract: `rules/plugin-evals.md` § No Bleeding.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

MIN_WORDS_FOR_BLEED = 4


def fail(msg: str) -> None:
    print(f"audit-scenarios.py: {msg}", file=sys.stderr)
    sys.exit(2)


def normalize(text: str) -> str:
    """Lowercase and collapse whitespace for comparison."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def word_count(text: str) -> int:
    return len([w for w in text.split() if w])


def audit_scenario(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a list of violation records for one scenario."""
    violations: list[dict[str, Any]] = []
    task_norm = normalize(scenario.get("task", ""))
    for crit in scenario.get("criteria", []):
        expected = crit.get("expected", "")
        if not isinstance(expected, str) or not expected.strip():
            continue
        if word_count(expected) < MIN_WORDS_FOR_BLEED:
            continue
        if normalize(expected) in task_norm:
            violations.append({
                "scenario_id": scenario.get("id"),
                "criterion_id": crit.get("id"),
                "expected_literal": expected,
                "kind": "bleeding",
                "explanation": (
                    f"Criterion expected literal appears verbatim in the task description "
                    f"(criterion is testing reading of the task, not application of the tile). "
                    f"Fix by stripping the literal from the task; keep the criterion."
                ),
            })
    return violations


def main() -> int:
    if len(sys.argv) < 2:
        fail("usage: audit-scenarios.py <scenarios.json>")

    path = Path(sys.argv[1])
    if not path.is_file():
        fail(f"scenarios file not found: {path}")

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        fail("scenarios.json missing top-level 'scenarios' array")

    violations: list[dict[str, Any]] = []
    for scn in scenarios:
        violations.extend(audit_scenario(scn))

    report = {
        "ok": not violations,
        "scenarios_audited": len(scenarios),
        "violations": violations,
    }
    print(json.dumps(report, indent=2))
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
