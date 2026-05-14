#!/usr/bin/env python3
"""Render a batch-summary index.md from a per-batch run directory.

Walks a `runs/<DISCOVERY_RUN_TS>/` directory:
- Reads `batch-manifest.json` for the canonical company list
- For each company subdirectory, loads `discovery.json` (verdict + target) and,
  if present, `lift.json` (aggregate lift) and `report.md` (link target)
- Emits `index.md` with verdict counts, per-company table, aggregate BUILD lift,
  and a follow-up checklist (SKIPs / AMBIGUOUS / errors)

Stdout: the absolute path of the written `index.md`.
Stderr: diagnostic on errors.
Exit 0 on success; 2 on usage / missing-input errors.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any


def fail(msg: str) -> None:
    print(f"summarize-batch.py: {msg}", file=sys.stderr)
    sys.exit(2)


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"summarize-batch.py: invalid JSON in {path}: {exc}", file=sys.stderr)
        return None


def main() -> int:
    if len(sys.argv) < 2:
        fail("usage: summarize-batch.py <run-dir>")

    run_dir = Path(sys.argv[1]).resolve()
    if not run_dir.is_dir():
        fail(f"run dir not found: {run_dir}")

    manifest_path = run_dir / "batch-manifest.json"
    manifest = load_json(manifest_path)
    if not manifest:
        fail(f"batch-manifest.json not found or invalid in {run_dir}")

    companies: list[dict[str, Any]] = manifest.get("companies") or []
    batch_id = manifest.get("batch_id") or run_dir.name
    run_ts = manifest.get("discovery_run_ts") or run_dir.name

    rows: list[dict[str, Any]] = []
    for entry in companies:
        slug = entry.get("slug") or "unknown"
        name = entry.get("company_name") or slug
        co_dir = run_dir / slug
        disc = load_json(co_dir / "discovery.json") if co_dir.is_dir() else None
        lift = load_json(co_dir / "lift.json") if co_dir.is_dir() else None

        if not disc:
            rows.append({"slug": slug, "name": name, "verdict": "error",
                         "target": None, "aggregate_lift": None,
                         "report": None, "note": "discovery.json missing or unreadable"})
            continue

        verdict = disc.get("verdict")
        target_title = None
        if verdict == "BUILD":
            targets = disc.get("skill_targets") or []
            if targets:
                # Top target by raw confidence (works for produce-mode and consume-mode v1)
                top = max(targets, key=lambda t: t.get("confidence") or 0)
                target_title = top.get("title")

        report_path = co_dir / "report.md"
        rows.append({
            "slug": slug,
            "name": name,
            "verdict": verdict,
            "target": target_title,
            "aggregate_lift": (lift or {}).get("aggregate_lift"),
            "report": str(report_path.relative_to(run_dir)) if report_path.is_file() else None,
            "note": (disc.get("skip_reason") or "").splitlines()[0][:140] if verdict == "SKIP" else None,
        })

    verdict_counts: dict[str, int] = {"BUILD": 0, "SKIP": 0, "AMBIGUOUS": 0, "error": 0}
    for r in rows:
        v = r["verdict"] or "error"
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    build_lifts = [r["aggregate_lift"] for r in rows
                   if r["verdict"] == "BUILD" and isinstance(r["aggregate_lift"], (int, float))]
    median_lift = statistics.median(build_lifts) if build_lifts else None
    mean_lift = statistics.mean(build_lifts) if build_lifts else None

    parts: list[str] = []
    parts.append(f"# Batch Run Summary — {batch_id}\n")
    parts.append(f"_Run timestamp: `{run_ts}` • Total companies: {len(rows)}_\n\n")
    parts.append("## Verdict counts\n")
    parts.append(f"- BUILD: {verdict_counts['BUILD']}\n")
    parts.append(f"- SKIP: {verdict_counts['SKIP']}\n")
    parts.append(f"- AMBIGUOUS: {verdict_counts['AMBIGUOUS']}\n")
    parts.append(f"- error: {verdict_counts['error']}\n")

    if median_lift is not None:
        parts.append(f"\n## Aggregate lift across BUILDs ({len(build_lifts)} measured)\n")
        parts.append(f"- Median: {median_lift:+.2f}\n")
        parts.append(f"- Mean: {mean_lift:+.2f}\n")

    parts.append("\n## Per-company outcomes\n\n")
    parts.append("| Company | Verdict | Top target | Aggregate lift | Report |\n")
    parts.append("|---|---|---|---|---|\n")
    for r in rows:
        target = r["target"] or "—"
        lift_str = f"{r['aggregate_lift']:+.2f}" if isinstance(r["aggregate_lift"], (int, float)) else "—"
        report_str = f"[link]({r['report']})" if r["report"] else "—"
        parts.append(f"| {r['name']} | {r['verdict'] or 'error'} | {target} | {lift_str} | {report_str} |\n")

    followups = [r for r in rows if r["verdict"] in ("SKIP", "AMBIGUOUS", "error")]
    if followups:
        parts.append("\n## Follow-up checklist\n\n")
        for r in followups:
            note = r.get("note") or ""
            parts.append(f"- **{r['name']}** ({r['verdict']}) — {note}\n")

    index_path = run_dir / "index.md"
    index_path.write_text("".join(parts))
    print(str(index_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
