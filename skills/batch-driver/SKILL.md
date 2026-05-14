---
name: batch-driver
description: 'Run the A1 pipeline (produce-mode discovery → auto-selection → build-and-evaluate) across a CSV of company names. Drives the full pipeline unattended for booth-scale runs (~100 leads), sharing a single DISCOVERY_RUN_TS so all per-company outputs land in one diffable run directory. After completion, emits a per-batch `index.md` summarizing outcomes (BUILD/SKIP/AMBIGUOUS counts, aggregate lift across BUILDs, links to per-company reports). Trigger phrases — "run the batch driver on a CSV", "process the attendee list", "batch-pipeline the snyk leads", "A1 batch run on a CSV of company names".'
---

# Batch-Driver Skill

Process steps in order. Do not skip ahead.

This skill orchestrates the A1 pipeline across a CSV of companies. The per-company pipeline (discovery → selection → build-and-evaluate) is itself implemented by three other skills; this skill loops over them with a shared run timestamp so the batch is diff-able as a unit. Designed for pre-conference batch runs (Snyk attendee list, ~100 leads) where manual per-company target selection isn't feasible — selection auto-picks the top-confidence candidate and notes the auto-pick in `selection.json` for traceability.

## Step 1 — Parse the CSV and Branch on Yield

Input: a CSV path. Expected columns (case-insensitive header): `company` (required) and `domain` (optional). Empty cells, duplicate rows, and rows with non-printable characters are dropped with a warning.

Run `skills/batch-driver/scripts/parse-attendees.py <csv-path>`. The script emits a normalized JSON list of `{slug, company_name, domain}` records to stdout and a `{ok, dropped_rows, kept_rows}` summary to stderr.

### Branch by parse outcome:

- **Script exits 0 with `kept_rows >= 1`**: proceed to Step 2 with the parsed list cached in working memory.
- **Script exits non-zero (or `kept_rows == 0`)**: the CSV has no usable companies — every row was dropped (empty, duplicate, or non-printable). **Finish here.** Output an explanation that surfaces:
  - The CSV path that was processed
  - The stderr summary verbatim (`{ok: false, kept_rows: 0, dropped_rows: N, reasons: {...}}`)
  - An actionable next step (re-export the CSV, verify the `company` column header is correct, check the source export job)
  Do NOT proceed to Step 2. Do NOT create a run directory under `runs/`. Do NOT write a `batch-manifest.json`. Do NOT invent company names to keep the batch going — fabricating data to satisfy a downstream pipeline is the exact failure mode this gate exists to prevent. Do NOT invoke `discovery-produce` or any other per-company skill.

### Why this gate is load-bearing

A pre-0.1.2 version of this skill had the parse-outcome branch implicit ("Exit non-zero if no usable rows remain"), and the agent ignored it — given an empty CSV, the agent fabricated five companies, generated a run directory, wrote a `batch-manifest.json`, and ran the full per-company pipeline against the invented data. The published-time eval `batch-empty-csv` regressed from baseline 0.53 to with-skill 0.10 on exactly this failure mode. The branch is the first action in the step because the agent must commit to halting before any per-company tooling executes.

## Step 2 — Initialize the Batch Run Directory

Generate a shared `DISCOVERY_RUN_TS` for the batch (UTC timestamp with a human-readable suffix, e.g., `2026-05-13T-snyk-batch`). Export it as an environment variable so every per-company script invocation in Steps 3–4 writes to the same `runs/<DISCOVERY_RUN_TS>/` parent directory.

Write `runs/<DISCOVERY_RUN_TS>/batch-manifest.json` with the parsed company list and the run timestamp. The manifest is the index every downstream step (summary rendering, post-batch review) reads — do not rely on filesystem-listing alone.

Proceed immediately to Step 3.

## Step 3 — Run Per-Company Pipeline

For each company in the manifest, in sequence:

1. Invoke `Skill(skill: "discovery-produce")` with the company name. The skill writes `runs/<DISCOVERY_RUN_TS>/<slug>/discovery.json` and returns the path.
2. Branch on the discovery verdict:
   - `BUILD` → run `skills/batch-driver/scripts/auto-select.py <discovery-path>` to write a `selection.json` auto-picking the top-confidence target (no human gate in batch mode), then invoke `Skill(skill: "build-and-evaluate")` for the rest of the pipeline.
   - `SKIP` → record the skip reason in the batch index; do not invoke select-target or build-and-evaluate for this company. Move on.
   - `AMBIGUOUS` → record the sub-brand list; flag for manual re-invocation with `parent/sub-brand`. Move on.
3. Capture per-company outcome: `{slug, verdict, target_id?, aggregate_lift?, report_path?, error?}` and append to an in-memory batch results array.

Continue past per-company failures rather than aborting the batch — a single company failing should not block the other 99. If discovery returns a non-JSON or malformed result, log the error and move on.

Proceed immediately to Step 4 after the last company.

## Step 4 — Render Batch Summary

Run `skills/batch-driver/scripts/summarize-batch.py runs/<DISCOVERY_RUN_TS>` to emit `runs/<DISCOVERY_RUN_TS>/index.md`. The script consumes the batch-manifest and walks the per-company subdirectories to collect verdicts, lift scores, and report paths. Schema of the rendered summary:

- Header: batch ID, run timestamp, total companies
- Verdict counts: BUILD / SKIP / AMBIGUOUS / error
- Per-company table: slug, verdict, top-target title (BUILDs only), aggregate lift, link to report
- Aggregate lift across BUILDs
- Companies flagged for follow-up: SKIPs (review search trail), AMBIGUOUS (re-invoke), errors (re-run individually)

Output the absolute path of `index.md` and finish here.
