# jbaruch/auto-skill-discovery

[![tessl](https://img.shields.io/endpoint?url=https%3A%2F%2Fapi.tessl.io%2Fv1%2Fbadges%2Fjbaruch%2Fauto-skill-discovery)](https://tessl.io/registry/jbaruch/auto-skill-discovery)

Automated pipeline that takes a company name and produces a custom Tessl skill plus an eval report showing per-scenario lift (baseline agent vs with-skill agent). Designed for booth-scale runs (~100 leads) ahead of conferences.

**Install:** `tessl install jbaruch/auto-skill-discovery`

Strategic context: see [SPEC.md](SPEC.md) (the 10-step pipeline contract) and [STAKEHOLDER-BRIEF.md](STAKEHOLDER-BRIEF.md) (the four operating modes, what's validated, cost envelope).

## Operating modes

One pipeline, four cells on a 2x2 of (target surface × personalization):

|  | Personalization OFF | Personalization ON |
|---|---|---|
| **Produce** (company's public API/SDK) | **A1** ✅ shipped | A2 (deferred) |
| **Consume** (engineers' daily tools) | B1 (deferred) | B2 (deferred) |

A1 is the MVP for the AI Security Summit by Snyk. The other three cells layer in after.

## A1 pipeline shape

```
company name
   │
   ▼  Step 1 — produce-mode discovery
/discovery-produce         (skills/discovery-produce/SKILL.md)
   │                        → runs/<ts>/<slug>/discovery.json
   │
   ▼  Step 2 — target selection (human gate OR auto-pick)
/select-target <slug>      (skills/select-target/SKILL.md)
   OR
auto-select.py             (skills/batch-driver/scripts/auto-select.py)
   │                        → runs/<ts>/<slug>/selection.json
   │
   ▼  Steps 3–9 — skill build + eval + report
/build-and-evaluate <slug> (skills/build-and-evaluate/SKILL.md)
                            → runs/<ts>/<slug>/generated-skill/
                            → runs/<ts>/<slug>/scenarios.json
                            → runs/<ts>/<slug>/skill-review.json
                            → runs/<ts>/<slug>/lift.json
                            → runs/<ts>/<slug>/gap-analysis.md
                            → runs/<ts>/<slug>/report.md  ← final deliverable
```

For a batch, `/batch-driver <csv>` loops the per-company pipeline under one shared run timestamp and emits a per-batch `index.md`.

## Three ways to run

### Interactive, single company

1. `/discovery-produce` — give it a company name when prompted. Writes `runs/<ts>/<slug>/discovery.json`.
2. `/select-target <slug>` — presents the top-3 candidate targets; reply with a `tgt_NN` id, `skip`, or `defer`. Writes `selection.json`.
3. `/build-and-evaluate <slug>` — runs phases 4–10 unattended. Final output is `runs/<ts>/<slug>/report.md`.

### Non-interactive, single company

Skip the human gate by auto-picking the top-confidence target:

```bash
# After /discovery-produce has run
python3 skills/batch-driver/scripts/auto-select.py runs/<ts>/<slug>/discovery.json
```

Then `/build-and-evaluate <slug>` as above. Auto-pick writes `auto_selected: true` to `selection.json` for traceability — downstream steps can't tell auto-picks from human picks.

### Batch from a CSV

```bash
/batch-driver path/to/attendees.csv
```

CSV header must include `company` (required) and optionally `domain`. The skill:

1. Parses + normalizes the CSV (`skills/batch-driver/scripts/parse-attendees.py`), dropping empty / duplicate / non-printable rows
2. Generates one shared `DISCOVERY_RUN_TS` for the batch
3. Loops every company through `discovery-produce` → `auto-select.py` → `build-and-evaluate`
4. Renders `runs/<DISCOVERY_RUN_TS>/index.md` with verdict counts, per-company table, aggregate lift across BUILDs, and a follow-up checklist for SKIPs/AMBIGUOUS/errors

## Output layout

```
runs/
  <DISCOVERY_RUN_TS>/                # e.g., 2026-05-14T-stripe-live
    batch-manifest.json              # batch mode only
    index.md                         # batch mode only
    <slug>/                          # one per company
      discovery.json                 # Step 1 output (contract: discovery-output-contract.md)
      selection.json                 # Step 2 output
      scenarios.json                 # Step 4 output (from tessl scenario generate)
      generated-skill/               # Step 3 — scaffolded by tessl skill new
        tile.json
        SKILL.md
        evals/
      skill-review.json              # Step 6 — tessl skill review --threshold 85
      baseline-results.json          # Step 7 — without-context variant
      with-skill-results.json        # Step 7 — with-context variant
      lift.json                      # Step 8 — compute-lift.py
      gap-analysis.md                # Step 9
      report.md                      # Step 10 — final deliverable
```

## Skills

| Skill | Slash command | Role | Review score |
|---|---|---|---|
| `discovery-produce` | `/discovery-produce` | A1 entry point — produce-mode discovery from company name | 85 |
| `discovery` | `/discovery` | Consume-mode discovery (B1/B2 — deferred path) | 76 ⚠️ below gate |
| `select-target` | `/select-target` | Human-gated target selection | 85 |
| `build-and-evaluate` | `/build-and-evaluate` | Phases 4–10 orchestrator | 88 |
| `batch-driver` | `/batch-driver` | CSV-driven batch runner | 94 |
| `company-list-filter` | `/company-list-filter` | Pre-discovery triage (drop obviously-out, surface obviously-in) | 90 |

All scores against `tessl skill review --threshold 85`. The consume-mode `discovery` skill is below the gate — pre-existing issue, out of A1 scope, flagged for follow-up.

## Smoke test

```bash
./smoke-test-a1.sh
```

Exercises all deterministic plumbing (contract validator, auto-select, bleeding audit, lift compute, report render, batch summary) end-to-end on synthetic Stripe data. Passes in seconds. Does NOT exercise the live Tessl tooling — those calls happen when `build-and-evaluate` is invoked from Claude Code.

Inspect the artifacts at `runs/2026-05-13T-a1-smoke/stripe/`.

## Contract

The discovery JSON shape is the canonical interface between every step. See [discovery-output-contract.md](discovery-output-contract.md). Two modes (`consume`, `produce`) and three schema versions (1, 2, 3 — v3 introduces the `mode` field). The validator at `skills/discovery/scripts/validate-output.py` enforces shape; produce-mode rejects consume-side fields and vice versa.

## Known gaps

- Live `tessl eval run --variant without-context --variant with-context` output schema not yet exercised — `build-and-evaluate` Step 8 instructs the agent to reason over the result and emit `baseline-results.json` + `with-skill-results.json` in the canonical shape. Once the schema is observed, that step gets a `parse-eval-view.py` script.
- Consume-mode `discovery` skill scores 76 against `tessl skill review --threshold 85`. Pre-existing, not in A1 scope.
- A2/B1/B2 modes deferred until A1 results justify expanding the matrix.

## Cost

~$13–$28 per company on Opus 4.7 with prompt caching (clarifying $0–$2 + discovery $3–$6 + skill gen + eval + report $10–$20). A 100-company Snyk batch runs at ~$1.3k–$2.6k in tokens. See [STAKEHOLDER-BRIEF.md](STAKEHOLDER-BRIEF.md) § 3 for the full breakdown.

## References

Strategic / context documents:

- [SPEC.md](SPEC.md) — 10-step pipeline contract, operating-modes 2x2, MVP scope
- [STAKEHOLDER-BRIEF.md](STAKEHOLDER-BRIEF.md) — pitch with validation data and cost envelope
- [discovery-output-contract.md](discovery-output-contract.md) — JSON shape every step consumes (v3, modes: consume / produce)

Skill companion files (referenced from the SKILL.md execution plans):

- [skills/discovery-produce/contract-reference.md](skills/discovery-produce/contract-reference.md) — produce-mode contract cheatsheet
- [skills/discovery/contract-reference.md](skills/discovery/contract-reference.md) — consume-mode contract cheatsheet
- [skills/company-list-filter/heuristics.md](skills/company-list-filter/heuristics.md) — pre-discovery triage rules
