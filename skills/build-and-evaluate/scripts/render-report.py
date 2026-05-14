#!/usr/bin/env python3
"""Render the final A1 markdown report from a per-run directory.

Reads the canonical artifacts in `<run_dir>`:
- discovery.json        (sources, selected target context)
- selection.json        (human pick + rationale)
- skill-review.json     (final review score)
- lift.json             (per-scenario + aggregate lift)
- gap-analysis.md       (improvement suggestions from Step 9)

Writes `<run_dir>/report.md` and prints its absolute path on stdout.

Exit 0 on success; 2 on usage / missing-input errors.

Contract: spec § Output. The report includes:
- Research found (sources, selected target rationale)
- Per-scenario lift table + aggregate
- Near-zero-lift scenarios flagged
- Improvement suggestions (embedded from gap-analysis.md)
- Links to generated skill / scenarios / results (local paths)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def fail(msg: str) -> None:
    print(f"render-report.py: {msg}", file=sys.stderr)
    sys.exit(2)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"required input not found: {path}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def load_text(path: Path, default: str = "") -> str:
    return path.read_text() if path.is_file() else default


def find_target(discovery: dict[str, Any], target_id: str) -> dict[str, Any]:
    for tgt in discovery.get("skill_targets") or []:
        if tgt.get("id") == target_id:
            return tgt
    fail(f"selected_target_id {target_id!r} not found in discovery.skill_targets[]")
    return {}  # unreachable


def render_sources_section(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "_No sources recorded._\n"
    lines = ["| Authority | Kind | URL |", "|---|---|---|"]
    for src in sorted(sources, key=lambda s: s.get("authority_rank", 9)):
        rank = src.get("authority_rank", "?")
        kind = src.get("kind", "?")
        url = src.get("url", "?")
        lines.append(f"| {rank} | {kind} | {url} |")
    return "\n".join(lines) + "\n"


def render_lift_table(lift: dict[str, Any]) -> str:
    rows = lift.get("per_scenario_lift") or []
    if not rows:
        return "_No per-scenario lift data._\n"
    lines = ["| Scenario | Baseline | With-skill | Lift |", "|---|---|---|---|"]
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['baseline']:.2f} | {row['with_skill']:.2f} | {row['lift']:+.2f} |"
        )
    return "\n".join(lines) + "\n"


def render_report(run_dir: Path) -> str:
    discovery = load_json(run_dir / "discovery.json")
    selection = load_json(run_dir / "selection.json")
    review = load_json(run_dir / "skill-review.json")
    lift = load_json(run_dir / "lift.json")
    gap_analysis = load_text(run_dir / "gap-analysis.md", "_No gap analysis recorded._\n")

    target_id = selection.get("selected_target_id") or ""
    target = find_target(discovery, target_id)
    company = discovery.get("company", {})

    skill_dir = run_dir / "generated-skill"
    scenarios_path = run_dir / "scenarios.json"
    baseline_path = run_dir / "baseline-results.json"
    with_skill_path = run_dir / "with-skill-results.json"

    parts: list[str] = []
    parts.append(f"# A1 Skill-Build Report — {company.get('name', 'Unknown')}\n")
    parts.append(
        f"_Pipeline: produce-mode discovery → human-gated selection → skill build → "
        f"eval (baseline + with-skill) → lift analysis. Generated for "
        f"`{company.get('canonical_url', '')}` at {company.get('discovered_at', '')}._\n"
    )

    parts.append("## Selected Target\n")
    parts.append(f"**{target.get('title', 'Untitled')}** ({target.get('kind', '?')}, "
                 f"confidence {target.get('confidence', 0):.2f})\n")
    parts.append(f"\n**Rationale.** {target.get('rationale', '_(none recorded)_')}\n")
    parts.append(f"\n**Differentiation hypothesis.** {target.get('differentiation_hypothesis', '_(none recorded)_')}\n")
    parts.append(f"\n**Existing competition.** {target.get('existing_competition', '_(none recorded)_')}\n")
    if selection.get("selection_rationale"):
        parts.append(f"\n**Human selection rationale.** {selection['selection_rationale']}\n")

    parts.append("\n## Research Found\n")
    parts.append(render_sources_section(discovery.get("sources") or []))

    parts.append("\n## Skill Review\n")
    score = review.get("score") or review.get("final_score")
    parts.append(f"Final review score: **{score}** (threshold: 85)\n")
    if review.get("suggestions"):
        parts.append("\n**Reviewer suggestions:**\n")
        for sug in review["suggestions"]:
            parts.append(f"- {sug}\n")

    parts.append("\n## Eval Lift\n")
    parts.append(f"**Aggregate lift:** {lift.get('aggregate_lift', 0):+.2f} "
                 f"(baseline {lift.get('aggregate_baseline', 0):.2f} → "
                 f"with-skill {lift.get('aggregate_with_skill', 0):.2f})\n\n")
    parts.append(render_lift_table(lift))
    near_zero = lift.get("near_zero_scenarios") or []
    if near_zero:
        parts.append(
            f"\n**Near-zero-lift scenarios flagged for review:** "
            f"{', '.join(near_zero)} — per `rules/plugin-evals.md` § Lift, Not Attainment, "
            f"these signal coincidence-with-baseline, leaked technique, or universal-competence criteria.\n"
        )

    parts.append("\n## Improvement Suggestions\n")
    parts.append(gap_analysis)
    if not gap_analysis.endswith("\n"):
        parts.append("\n")

    parts.append("\n## Artifacts\n")
    parts.append(f"- Generated skill: `{skill_dir.relative_to(run_dir)}/SKILL.md`\n")
    parts.append(f"- Eval scenarios: `{scenarios_path.relative_to(run_dir)}`\n")
    parts.append(f"- Baseline eval results: `{baseline_path.relative_to(run_dir)}`\n")
    parts.append(f"- With-skill eval results: `{with_skill_path.relative_to(run_dir)}`\n")
    parts.append(f"- Discovery JSON: `discovery.json`\n")
    parts.append(f"- Selection JSON: `selection.json`\n")

    return "".join(parts)


def main() -> int:
    if len(sys.argv) < 2:
        fail("usage: render-report.py <run_dir>")
    run_dir = Path(sys.argv[1])
    if not run_dir.is_dir():
        fail(f"run_dir is not a directory: {run_dir}")

    report_md = render_report(run_dir)
    report_path = run_dir / "report.md"
    report_path.write_text(report_md)
    print(str(report_path.resolve()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
