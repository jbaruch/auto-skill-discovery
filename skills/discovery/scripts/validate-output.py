#!/usr/bin/env python3
"""Validate a discovery JSON artifact against the contract.

Reads JSON from stdin or a file path; prints a JSON validation report to stdout.
Exits 0 on success, non-zero with stderr diagnostic on validation failure.

Contract: discovery-output-contract.md (authoritative).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_VERDICTS = {"BUILD", "SKIP", "AMBIGUOUS"}
ALLOWED_TARGET_KINDS = {"api_wrapper", "domain_skill", "workflow_skill", "tooling_assist"}
ALLOWED_ACCESS_TIERS = {"open", "customer_only", "partner_only", "dead", "internal"}
ALLOWED_LIFT_SIGNALS = {"high", "medium", "low"}
ALLOWED_AUTHORITY_RANKS = {1, 2, 3, 4}
ALLOWED_SCHEMA_VERSIONS = {1, 2, 3}
ALLOWED_MODES = {"consume", "produce"}
ALLOWED_INTERNAL_USAGE_LEVELS = {"confirmed", "inferred", "weak", "none"}
ALLOWED_TASK_SHAPES = {"USE", "AUTHOR", "INTEGRATE"}
ALLOWED_POPULATION_SIZES = {"majority", "minority", "small_team", "external"}


def fail(msg: str) -> None:
    print(f"validate-output.py: {msg}", file=sys.stderr)
    sys.exit(2)


def load_input() -> dict[str, Any]:
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if not path.is_file():
            fail(f"input file not found: {path}")
        return json.loads(path.read_text())
    return json.loads(sys.stdin.read())


def collect_errors(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    # Required top-level fields
    for field in ("schema_version", "company", "verdict", "sources"):
        if field not in data:
            errors.append(f"missing top-level field: {field}")

    schema_version = data.get("schema_version")
    if schema_version not in ALLOWED_SCHEMA_VERSIONS:
        errors.append(f"schema_version must be in {sorted(ALLOWED_SCHEMA_VERSIONS)}, got {schema_version!r}")

    # mode is required for schema_version 3; defaulted to "consume" for v1/v2 (back-compat)
    if schema_version == 3:
        mode = data.get("mode")
        if mode not in ALLOWED_MODES:
            errors.append(f"schema_version 3 requires mode in {sorted(ALLOWED_MODES)}, got {mode!r}")
    else:
        mode = "consume"

    company = data.get("company") or {}
    for field in ("name", "canonical_url", "discovered_at"):
        if field not in company:
            errors.append(f"missing company.{field}")

    verdict = data.get("verdict")
    if verdict not in ALLOWED_VERDICTS:
        errors.append(f"verdict must be one of {sorted(ALLOWED_VERDICTS)}, got {verdict!r}")

    # Verdict-specific shape
    if verdict == "BUILD":
        targets = data.get("skill_targets") or []
        if not targets:
            errors.append("BUILD requires at least one skill_target")
        if not any(isinstance(t.get("confidence"), (int, float)) and t["confidence"] >= 0.5 for t in targets):
            errors.append("BUILD requires at least one skill_target with confidence >= 0.5")
        for required in ("domain_signal", "product_surface", "agentic_landscape"):
            if required not in data:
                errors.append(f"BUILD requires top-level {required}")
    elif verdict == "SKIP":
        for required in ("skip_reason", "search_attempted", "would_change_verdict_if"):
            if required not in data:
                errors.append(f"SKIP requires top-level {required}")
        if data.get("skill_targets"):
            errors.append("SKIP must have empty skill_targets")
    elif verdict == "AMBIGUOUS":
        if "sub_brands_detected" not in data:
            errors.append("AMBIGUOUS requires sub_brands_detected[]")

    # Sources collection
    sources = data.get("sources") or []
    source_ids: set[str] = set()
    for i, src in enumerate(sources):
        sid = src.get("id")
        if not sid:
            errors.append(f"sources[{i}] missing id")
            continue
        if sid in source_ids:
            errors.append(f"duplicate source id: {sid}")
        source_ids.add(sid)
        for field in ("url", "kind", "fetched_at", "authority_rank"):
            if field not in src:
                errors.append(f"sources[{sid}] missing {field}")
        rank = src.get("authority_rank")
        if rank not in ALLOWED_AUTHORITY_RANKS:
            errors.append(f"sources[{sid}].authority_rank must be in {sorted(ALLOWED_AUTHORITY_RANKS)}, got {rank!r}")

    # Internal usage: required for consume-mode BUILD (schema 2 or schema 3 + mode=consume).
    # Produce-mode (schema 3 + mode=produce) does not carry internal_usage.
    internal_usage_surfaces: set[str] = set()
    consume_mode_build = verdict == "BUILD" and (
        schema_version == 2 or (schema_version == 3 and mode == "consume")
    )
    if consume_mode_build:
        if "internal_usage" not in data:
            errors.append("consume-mode BUILD requires top-level internal_usage[]")
        for i, iu in enumerate(data.get("internal_usage") or []):
            surface = iu.get("surface")
            if not surface:
                errors.append(f"internal_usage[{i}] missing surface")
                continue
            internal_usage_surfaces.add(surface)
            level = iu.get("level")
            if level not in ALLOWED_INTERNAL_USAGE_LEVELS:
                errors.append(f"internal_usage[{surface}].level must be in {sorted(ALLOWED_INTERNAL_USAGE_LEVELS)}, got {level!r}")
            for src_ref in iu.get("evidence_source_ids") or []:
                if src_ref not in source_ids:
                    errors.append(f"internal_usage[{surface}].evidence_source_ids references unknown source: {src_ref}")
    elif schema_version == 3 and mode == "produce" and data.get("internal_usage"):
        errors.append("produce-mode must not carry internal_usage[]")

    # Skill targets reference real sources; kinds and lift signals are valid
    for i, tgt in enumerate(data.get("skill_targets") or []):
        tid = tgt.get("id") or f"index_{i}"
        kind = tgt.get("kind")
        if kind not in ALLOWED_TARGET_KINDS:
            errors.append(f"skill_targets[{tid}].kind must be in {sorted(ALLOWED_TARGET_KINDS)}, got {kind!r}")
        lift = tgt.get("expected_lift_signal")
        if lift not in ALLOWED_LIFT_SIGNALS:
            errors.append(f"skill_targets[{tid}].expected_lift_signal must be in {sorted(ALLOWED_LIFT_SIGNALS)}, got {lift!r}")
        for src_ref in tgt.get("supporting_source_ids") or []:
            if src_ref not in source_ids:
                errors.append(f"skill_targets[{tid}].supporting_source_ids references unknown source: {src_ref}")
        # Consume-mode required fields: present on v2 and on v3 with mode=consume.
        # Produce-mode (v3 + mode=produce) explicitly forbids them.
        consume_target_required = schema_version == 2 or (schema_version == 3 and mode == "consume")
        if consume_target_required:
            iu_surface = tgt.get("internal_usage_surface")
            if not iu_surface:
                errors.append(f"skill_targets[{tid}] missing internal_usage_surface (consume-mode required)")
            elif iu_surface not in internal_usage_surfaces:
                errors.append(f"skill_targets[{tid}].internal_usage_surface references unknown surface: {iu_surface}")
            shape = tgt.get("task_shape")
            if shape not in ALLOWED_TASK_SHAPES:
                errors.append(f"skill_targets[{tid}].task_shape must be in {sorted(ALLOWED_TASK_SHAPES)}, got {shape!r}")
            pop = tgt.get("target_population") or {}
            size = pop.get("size_class")
            if size not in ALLOWED_POPULATION_SIZES:
                errors.append(f"skill_targets[{tid}].target_population.size_class must be in {sorted(ALLOWED_POPULATION_SIZES)}, got {size!r}")
            if not pop.get("description"):
                errors.append(f"skill_targets[{tid}].target_population.description is required")
        elif schema_version == 3 and mode == "produce":
            for forbidden in ("internal_usage_surface", "task_shape", "target_population"):
                if forbidden in tgt:
                    errors.append(f"skill_targets[{tid}] must not carry {forbidden} in produce-mode")

    # Access classification tiers valid
    for i, ac in enumerate(data.get("access_classification") or []):
        tier = ac.get("tier")
        if tier not in ALLOWED_ACCESS_TIERS:
            errors.append(f"access_classification[{i}].tier must be in {sorted(ALLOWED_ACCESS_TIERS)}, got {tier!r}")

    # Domain evidence references real sources
    for i, ev in enumerate((data.get("domain_signal") or {}).get("domain_evidence") or []):
        sid = ev.get("source_id")
        if sid and sid not in source_ids:
            errors.append(f"domain_signal.domain_evidence[{i}].source_id references unknown source: {sid}")

    return errors


def main() -> int:
    try:
        data = load_input()
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail("top-level JSON must be an object")

    errors = collect_errors(data)

    report = {
        "ok": not errors,
        "errors": errors,
        "company": (data.get("company") or {}).get("name"),
        "verdict": data.get("verdict"),
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
