---
name: build-and-evaluate
description: 'Steps 4–10 of the workflow — takes a selection.json produced by `select-target` and runs the full skill-build + eval + report pipeline. Scaffolds a skill via `tessl skill new`, authors its body for the selected target, generates eval scenarios via `tessl scenario generate`, audits them for bleeding/leaking, runs `tessl skill review --threshold 85` as a quality gate, runs `tessl eval run --variant without-context --variant with-context` to get baseline + with-skill scores in one call, parses the result, computes per-scenario lift, analyzes gaps, and writes a markdown report alongside the discovery / selection artifacts. End-to-end output for the A1 MVP cell of the operating-modes 2x2 in `Automated Company Skills Eval App — Spec.md`. Trigger phrases — "build the skill", "run phases 4-10", "build-and-evaluate", "generate and evaluate the skill for a given company slug".'
---

# Build-and-Evaluate Skill

Process steps in order. Do not skip ahead.

This skill consumes a `selection.json` (the output of the `select-target` skill) and runs the full downstream pipeline: skill scaffold → skill body → scenarios → bleeding/leaking audit → review gate → baseline+with-skill evals (one call, two variants) → lift analysis → report. Every step is deterministic from the prior step's output; no human input after Step 1.

The skill is mode-agnostic — it works for produce-mode (A1) and consume-mode (B1/B2) selections identically. The difference between modes lives upstream in discovery; from the selection forward, the pipeline is the same.

**Note on phase ordering vs. the spec.** The spec's workflow numbers evals (steps 4–5) before skill generation (step 6) because logically the eval task is independent of the implementation. Tessl's tooling, however, generates scenarios from an existing skill/tile (`tessl scenario generate <tile-path>`), so the implementation here scaffolds the skill first, then generates scenarios from it. The final deliverables (skill + scenarios + lift + report) match the spec contract; only the execution order differs.

## Step 1 — Load Selection and Resolve Context

Input is one of:

- An explicit path to a `selection.json`, or
- A company slug — find the most-recent `runs/<UTC-timestamp>/<slug>/selection.json` by lex-sort descending of the timestamp directory name.

Load the file and validate that `selection_status == "selected"` and `selected_target_id` is populated. If status is `skipped` or `defer`, output the rationale and **finish here** — there's nothing to build.

Resolve the linked `discovery.json` from `discovery_path`. Locate the selected target by `selected_target_id` in `discovery.skill_targets[]`. Cache in working memory:

- `run_dir` — the directory containing the selection.json (where all subsequent artifacts will be written)
- `company` — `discovery.company`
- `mode` — `discovery.mode` (defaults to `"consume"` for schema_version < 3)
- `target` — the selected skill_target entry
- `domain_signal`, `product_surface`, `agentic_landscape` — context for skill drafting

Proceed immediately to Step 2.

## Step 2 — Scaffold Skill

Run `tessl skill new` to create the skill's tile scaffold:

```bash
tessl skill new \
  --name "<slugified-target-title>" \
  --description "<one-line description derived from target.title and target.rationale>" \
  --path "<run_dir>/generated-skill"
```

This produces `<run_dir>/generated-skill/` containing `tile.json`, a starter `SKILL.md`, and an empty `evals/` directory.

If the path already exists from a prior run, remove it first — re-running on the same selection should produce a fresh scaffold, not a merge.

Proceed immediately to Step 3.

## Step 3 — Author Skill Body

Fill in `<run_dir>/generated-skill/SKILL.md` for the selected target. The draft must follow `rules/skill-authoring.md`:

- Frontmatter `description` includes trigger phrases derived from the target's daily-work language
- H1 title naming the skill
- Sequential-workflow execution preamble (default for produce-mode API wrappers): *"Process steps in order. Do not skip ahead."*
- Flat numbered steps (`## Step 1 — ...`); one action per step; no decimals
- Step-by-step coverage of the target's workflow as described in the target rationale and differentiation hypothesis
- Reference material (long examples, API tables) moved to companion files (`<run_dir>/generated-skill/<file>.md`) and referenced from the skill, per the keep-skills-compact rule

If the target's `kind` is `api_wrapper` or `workflow_skill`, also seed `<run_dir>/generated-skill/scripts/` with stub scripts the SKILL.md references (one stub per script — they can be expanded if eval runs surface gaps).

Proceed immediately to Step 4.

## Step 4 — Generate Eval Scenarios

Run `tessl scenario generate` against the scaffolded tile:

```bash
tessl scenario generate --count 5 --json "<run_dir>/generated-skill"
```

The `--count 5` matches the MVP requirement (5 scenarios per company). The command runs server-side; capture the generation id from the JSON output and download the scenarios to disk:

```bash
tessl scenario download --last --output "<run_dir>/generated-skill/evals"
```

The scenarios land under `<run_dir>/generated-skill/evals/` in Tessl's canonical scenario format.

Generation skews to happy-path cases (per `rules/plugin-evals.md`). After download, hand-author at least one negative-case scenario (refuse bad input / produce silence when nothing actionable) and write it alongside the generated scenarios. Use an existing generated scenario as a structural template.

Proceed immediately to Step 5.

## Step 5 — Audit Scenarios for Bleeding and Leaking

Run `skills/build-and-evaluate/scripts/audit-scenarios.py <run_dir>/generated-skill/evals/scenarios.json`. The script enforces the No-Bleeding rule from `rules/plugin-evals.md` (no criterion's expected literal appears verbatim in its task description).

If the audit fails, regenerate the offending scenarios (return to Step 4) with the violation list as context for `tessl scenario generate`. Cap regeneration attempts at 3 — if scenarios still fail, escalate to the user and finish here.

If audit passes, proceed immediately to Step 6.

## Step 6 — Run Skill Review Gate

Run the skill-review quality gate:

```bash
tessl skill review --threshold 85 --json "<run_dir>/generated-skill" > "<run_dir>/skill-review.json"
```

Branch on the result:

- **Score ≥ 85**: gate passed; proceed to Step 7.
- **Score < 85**: read the reviewer's suggestions; apply concrete fixes to the SKILL.md (tighten triggers, fix step numbering, add typed Skill() calls, add silence instructions, etc.); re-run `tessl skill review --threshold 85`. Cap re-review attempts at 3.
- **Score still < 85 after 3 attempts**: escalate to the user with the reviewer's final output and finish here — do NOT lower the threshold (forbidden by `rules/context-artifacts.md`) and do NOT run `tessl skill review --optimize` and ship verbatim (also forbidden by the same rule).

Proceed immediately to Step 7.

## Step 7 — Run Evals (Both Variants)

Run baseline (skill not loaded) and with-skill (skill loaded) in a single Tessl call using its built-in variant mechanism:

```bash
tessl eval run \
  --variant without-context \
  --variant with-context \
  --agent claude:claude-sonnet-4-6 \
  --label "<run_dir>/generated-skill — A1 baseline+with-skill" \
  --json \
  "<run_dir>/generated-skill" > "<run_dir>/eval-run.json"
```

`without-context` is the baseline (no skill context loaded into the solver); `with-context` is the with-skill run (full tile context loaded). Tessl runs both against the same scenarios in one invocation — this is the canonical baseline-vs-with-skill comparison shape.

If the eval run fails (network, project-not-linked, missing workspace), run `tessl doctor` to diagnose, fix, and retry once. Do not skip the eval — the lift number is the report's load-bearing output.

Proceed immediately to Step 8.

## Step 8 — Compute Lift

The Tessl eval-run output contains per-scenario per-variant scores. Parse it into the canonical two-file shape that `compute-lift.py` consumes:

- `<run_dir>/baseline-results.json` — `{"mode": "baseline", "scenarios": [{"id": ..., "score": ...}], "aggregate_score": ...}` from the `without-context` variant
- `<run_dir>/with-skill-results.json` — same shape from the `with-context` variant

If the eval-view JSON shape isn't directly compatible, run `tessl eval view --last --json > <run_dir>/eval-view.json` to fetch a full structured result; reason over its `variants` key to build the two canonical files. Document the schema in a TODO comment if it doesn't match expectations — the script can be promoted to handle Tessl's format directly once the schema stabilizes.

Then:

```bash
python3 skills/build-and-evaluate/scripts/compute-lift.py \
  "<run_dir>/baseline-results.json" \
  "<run_dir>/with-skill-results.json" \
  > "<run_dir>/lift.json"
```

The lift script flags `near_zero_scenarios` where `|lift| < 0.05` — these are surfaced in Step 9.

Proceed immediately to Step 9.

## Step 9 — Analyze Gaps

Reason over the lift data and the failed criteria from both eval variants to identify:

1. **Per-scenario gaps** — for each scenario with `lift < 0.10`, classify the cause: leaked technique in the task description (re-audit needed), criterion grading universal competence (rewrite criteria), or the skill genuinely doesn't help (skill needs targeted improvement).
2. **Improvement suggestions** — concrete next steps to improve the skill, anchored to specific failed criteria. Format as bullet points the skill author can act on without re-reading the eval logs.
3. **Cross-cutting patterns** — if multiple scenarios fail on the same kind of criterion (e.g., webhook signature verification across 3 scenarios), surface as a single pattern with priority `high`.

Write the analysis to `<run_dir>/gap-analysis.md`. Keep it under one page — the report compiles from this file.

Proceed immediately to Step 10.

## Step 10 — Render Report

Run `skills/build-and-evaluate/scripts/render-report.py <run_dir>` and output the absolute path of the rendered report. The script consumes:

- `<run_dir>/discovery.json` — sources, selected target, rationale
- `<run_dir>/selection.json` — human (or auto) pick + selection rationale
- `<run_dir>/skill-review.json` — final review score
- `<run_dir>/lift.json` — per-scenario + aggregate lift
- `<run_dir>/gap-analysis.md` — improvement suggestions

And emits `<run_dir>/report.md` with the structure required by the spec's Output section: research found, per-scenario lift table, aggregate lift, improvement suggestions, links to the generated skill / scenarios / results.

Output the absolute path of `<run_dir>/report.md` and finish here.
