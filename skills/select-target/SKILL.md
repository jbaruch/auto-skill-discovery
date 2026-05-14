---
name: select-target
description: 'Step 3 of the workflow — human-gated target selection from a discovery.json. Reads a discovery output, presents ranked skill_targets to the human (sorted by booth-aha score for consume-mode v2 and v3+consume, by raw confidence for v1 and produce-mode v3), accepts a single pick, and persists a selection.json alongside the discovery file. The only manual step in the pipeline per `SPEC.md`. Trigger phrases — "pick a target", "select skill target", "human-gate selection", "step 3 selection", "run selection on a company slug".'
---

# Target Selection Skill

Process steps in order. Do not skip ahead. This skill has one human-in-the-loop pause at Step 3 — that is the spec's only manual step in the pipeline. Every other step continues immediately.

## Step 1 — Locate and Load the Discovery File

Input is one of:

- An explicit path to a `discovery.json`, or
- A company slug (e.g., `spotify`) — find the most-recent `runs/<UTC-timestamp>/<slug>/discovery.json` by lex-sort descending of the timestamp directory name. Tie-breaking is filesystem-time descending.

Validate the file exists and parses as JSON. Branch on `verdict`:

- `BUILD` → proceed to Step 2.
- `SKIP` → output `verdict: SKIP`, the `skip_reason` and `search_attempted`, then **finish here** (no selection to make).
- `AMBIGUOUS` → output the `sub_brands_detected[]` list and the `guidance` field, then **finish here** with the message: re-invoke the discovery skill with `parent/sub-brand`.

Proceed immediately to Step 2 only if verdict is BUILD.

## Step 2 — Sort Candidates

Take `skill_targets[]` from the discovery JSON. Sort descending by:

- **Consume-mode** (`schema_version: 2`, or `schema_version: 3` with `mode: "consume"`): booth-aha score = `confidence × iu_weight × pop_weight × ts_weight`, with weights from the contract (`iu`: confirmed=1.0, inferred=0.7, weak=0.3, none=0.1; `pop`: majority=1.0, minority=0.6, small_team=0.4, external=0.2; `ts`: USE=1.0, AUTHOR=0.5, INTEGRATE=0.3).
- **Produce-mode** (`schema_version: 3` with `mode: "produce"`): by raw `confidence` only — produce-mode targets do not carry the v2 consume-side fields, so the booth-aha multipliers are not defined.
- **v1**: by raw `confidence` only (v1 outputs lack the consume-side fields needed for booth-aha computation).

Drop candidates with raw `confidence < 0.5` from presentation. The BUILD verdict already requires at least one target ≥0.5; lower-confidence candidates exist as discovery hints but are not human-gate-ready.

If the filtered list is empty, surface that to the user and finish — discovery passed BUILD but no candidate is mature enough for human selection.

Proceed immediately to Step 3.

## Step 3 — Present and Accept Selection (human-in-the-loop)

This is the spec's only manual step. Present the candidates in a Markdown table or a numbered list with these fields per row. The exact column set depends on mode:

**Common columns (all modes):**

- Rank (1, 2, 3...) ordered by score
- Target ID
- Title
- Kind
- Confidence (raw)
- Rationale (1–2 sentences)
- Differentiation hypothesis (1–2 sentences)
- Existing competition (one clause)

**Consume-mode additions (v2 / v3+consume):**

- Task_shape and size_class
- Booth-aha score (computed)
- Internal-usage anchor (surface name + level)

**Produce-mode (v3+produce):** omit the consume-mode columns above. The booth-aha score column shows "—" and the audience is implicitly "external developers consuming the public API."

**v1**: omit consume-mode columns; show "—" for booth-aha score (same effective layout as produce-mode).

Then explicitly ask the human to pick exactly one of:

- A target ID (e.g., `tgt_01`) — selects that target.
- `skip` — the human is rejecting all candidates; ask for a one-line reason and require a non-empty answer.
- `defer` — postpone the decision; no `selection.json` is written.

Wait for the human reply. Do not auto-pick.

This step legitimately ends with output and a question — the agent's job is to surface options and ask. The human's reply is the input to Step 4. **Do not generate a synthetic pick on the human's behalf.**

Proceed to Step 4 only after the human has responded.

## Step 4 — Validate Selection

Branch on the human's reply:

- **Target ID** — verify it appears as an `id` in the discovery's `skill_targets[]`. If not (typo, wrong format, out-of-range), surface the error and re-prompt — return to Step 3.
- **`skip`** — record the supplied reason; require non-empty.
- **`defer`** — finish here without writing a `selection.json`.

Proceed immediately to Step 5 unless `defer` was chosen.

## Step 5 — Persist Selection

Write `selection.json` to the **same directory** as the input `discovery.json` with this shape:

```json
{
  "schema_version": 1,
  "discovery_path": "<absolute path to the discovery.json>",
  "selected_target_id": "tgt_01",
  "selection_status": "selected | skipped",
  "selection_rationale": "<human-supplied note; required for skipped, optional for selected>",
  "selected_at": "ISO-8601 UTC"
}
```

For `selection_status: skipped`, `selected_target_id` is `null` and `selection_rationale` is required (captures *why* none of the candidates were chosen — feedback for future discovery iterations).

Run `skills/select-target/scripts/validate-selection.py <selection-path>` to confirm the file validates. The validator cross-references the linked `discovery.json` to ensure the selected target_id (when present) is real.

Output the absolute path of the persisted selection. Finish here.
