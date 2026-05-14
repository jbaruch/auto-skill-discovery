# Changelog

All notable changes to `jbaruch/auto-skill-discovery` are documented here.

The format roughly follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow semver.

## [0.1.1] — 2026-05-14

### Fixed

- `.gitignore` rule `runs/` was matching eval-scenario fixture directories under `evals/<name>/runs/`. Scoped the pattern to root-only (`/runs/`) so per-run app outputs at the project root stay excluded while eval-scenario fixtures ship with the tile. The 0.1.0 publish landed in the registry but with two batch-driver scenarios missing their `runs/` fixture data; this release ships the complete eval suite.

## [0.1.0] — 2026-05-14

Initial release of the A1 MVP cell of the operating-modes 2x2 (produce-mode discovery, no personalization). Built ahead of the AI Security Summit by Snyk for booth-scale conference runs.

### Skills

- **`discovery-produce`** — produce-mode source discovery from a company name; targets external/public API/SDK surface (the A1 entry point).
- **`discovery`** — consume-mode source discovery (B1/B2 deferred path) targeting dogfood/internal surfaces; included for completeness with the schema_version-3 contract.
- **`select-target`** — human-gated target selection from a discovery JSON; mode-aware sort (booth-aha score for consume-mode v2/v3+consume, raw confidence for produce-mode v3 and v1).
- **`build-and-evaluate`** — phases 4–10 orchestrator: scaffolds the skill via `tessl skill new`, generates scenarios via `tessl scenario generate`, audits bleeding/leaking, runs `tessl skill review --threshold 85`, runs `tessl eval run --variant without-context --variant with-context`, computes per-scenario lift, analyzes gaps, renders the report.
- **`batch-driver`** — CSV-driven orchestrator that loops the per-company pipeline under one shared `DISCOVERY_RUN_TS` and emits a per-batch index.
- **`company-list-filter`** — pre-discovery triage that drops obviously-out and surfaces obviously-in companies from a raw list.

### Contract

- Discovery output contract at `discovery-output-contract.md`, schema_version 3 with the `mode` field (`consume` | `produce`). v1 and v2 outputs remain valid; new runs emit v3.
- Validator (`skills/discovery/scripts/validate-output.py`) enforces mode-specific shapes — produce-mode rejects v2 consume-side fields (`internal_usage`, `task_shape`, `target_population`) and vice versa.

### Plumbing

- Per-run versioned output at `runs/<DISCOVERY_RUN_TS>/<slug>/...` shared across consume- and produce-mode discovery via `skills/discovery/scripts/write-versioned-output.sh`.
- Deterministic scripts: `audit-scenarios.py` (bleeding check), `compute-lift.py` (per-scenario + aggregate lift), `render-report.py` (markdown report), `parse-attendees.py` (CSV normalization), `auto-select.py` (top-confidence pick for batch mode), `summarize-batch.py` (per-batch index).
- `smoke-test-a1.sh` exercises all deterministic plumbing end-to-end on synthetic Stripe data.

### Known gaps

- Live `tessl eval run --variant without-context --variant with-context` output schema not yet exercised — `build-and-evaluate` Step 8 instructs the agent to parse the variants into the canonical two-file shape until a `parse-eval-view.py` script can be written from observed output.
- A2 (produce + personalization), B1, and B2 cells of the 2x2 deferred until A1 results justify expansion.
