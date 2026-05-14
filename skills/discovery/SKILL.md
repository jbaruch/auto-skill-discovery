---
name: discovery
description: 'Automated source discovery and structure extraction for a single company (steps 1–2 of the workflow in `SPEC.md`). Takes a company name (optionally `parent/sub-brand` for MEGA_CORP cases that have been pre-scoped), produces a JSON artifact conforming to `discovery-output-contract.md`, and writes it to a versioned per-run directory. Output is the input to step 3 (human-gated target selection). Trigger phrases — "run discovery on X", "discover sources for X", "produce a discovery JSON for X".'
---

# Discovery Skill

Process steps in order. Do not skip ahead.

This skill is the load-bearing step of the pipeline per the spec. Everything downstream — scenarios, skill, evals, report — is only as good as the sources this skill finds. Bias toward *intelligence over inventory*: the output is what we learned about the company, not a list of URLs we crawled.

## Step 1 — Resolve Input and Detect Hidden Multi-brand

Take the input (company name, or `parent/sub-brand` for already-scoped MEGA_CORP cases).

Apply alias resolution before keying searches:

- **Rebrand check**: Google `"<name>" formerly known as` and `"<name>" rebranded` — if the company has rebranded recently, the GitHub org and docs portal often still use the legacy name (Ona = Gitpod, runZero = Rumble, Altrina = Tessa).
- **Acquisition check**: Google `"<name>" acquired by` — note the acquirer; the engineering surface may have moved or been integrated.
- **DBA / trading-as**: if the input contains `t/a` or `operated by`, resolve to the operating entity.

Run the hidden-multi-brand check from `skills/company-list-filter/heuristics.md` § MEGA_CORP — count distinct GitHub orgs / docs portals / sub-brand pages. If multi-brand structure is detected and the input did NOT include a sub-brand specifier, write a `verdict: "AMBIGUOUS"` JSON to the run directory listing the sub-brands and exit. The caller must re-invoke with `parent/sub-brand`.

Document every alias / acquisition / multi-brand finding as a `sources[]` entry now — they are evidence the rest of the pipeline depends on.

Proceed immediately to Step 2.

## Step 2 — Source Discovery (multi-pronged)

Find sources across all the contract's dimensions in parallel where possible. The minimum probe set:

- **Official docs / API portal**: try `developer.<domain>`, `docs.<domain>`, `<domain>/docs`, `api.<domain>`. Fetch the landing page if any resolves.
- **GitHub org**: search GitHub for the company name; follow rebrand markers if the top result has them (e.g., `formerly_known_as` in README); record repo count, top repos by stars, and last commit date for the top three. **Fallback**: if WebFetch on `github.com/<org>` times out, use `gh api /orgs/<org>/repos?sort=stars&per_page=5` to get the data — same content, different transport, faster.
- **Engineering blog**: try `engineering.<domain>`, `<domain>/engineering`, `<domain>/blog`, `tech.<domain>`. Note recency of latest post.
- **Public talks**: search YouTube / conference index for `"<company>" talk` or `"<company>" engineering` over the last 24 months.
- **Agentic landscape — official MCP**: search the company's docs and GitHub for `mcp` / `MCP server` / `model context protocol`.
- **Agentic landscape — community MCPs**: probe `smithery.ai`, `mcp.so`, `github.com/punkpeye/awesome-mcp-servers`, and `github.com/topics/mcp-server` for community-built servers naming the company.
- **Agentic landscape — existing skills**: search `github.com/<org>/skills` and `github.com/topics/agent-skills` and `github.com/topics/claude-skills`. Some companies (Black Forest Labs, Bright Data, Telnyx) already publish public skill repos following the `agentskills.io` spec — these are direct prior art.
- **People signal**: search LinkedIn and the company's about/team page for 3–5 public-facing engineers / PMs and their stated focus.

Record everything as `sources[]` entries with `id`, `url`, `kind`, `fetched_at`, `freshness_signal`, and `authority_rank` per the contract. Authority rank: `1` for official primary, `2` for official secondary (blog, talks), `3` for community (community MCPs, third-party repos), `4` for third-party tutorials.

Proceed immediately to Step 3.

## Step 3 — Extract Contract Dimensions

Fill every dimension of the discovery contract using the sources from Step 2. The contract is the schema; `discovery-output-contract.md` is authoritative. Quick reference at `skills/discovery/contract-reference.md` — read it once for this run.

See [contract-reference.md](contract-reference.md) for the one-page cheatsheet of [discovery-output-contract.md](../../discovery-output-contract.md).

Dimensions to populate:

- `domain_signal` — what does the company do and care about right now? Extract from blog topics, OSS portfolio themes, talk titles, recent product announcements. `core_themes` capture stable identity; `active_focus` captures what's shipping in the last 3 months.
- `product_surface` — what's callable from outside. Use `endpoint_family` (with `endpoint: null`) for partner-only surfaces where a spec is published but no public endpoint is. Tag every API with `access_tier ∈ {open, customer_only, partner_only, dead, internal}`.
- `engineering_practices` — extracted from public OSS + blog. **OSS-as-signal applies here**: a regulated company's notable OSS portfolio (Capital One's DataProfiler / Slingshot, Man Group's ArcticDB, G-Research's Armada) is domain signal even when no product API exists.
- `agentic_landscape` — first-class section because agentic context is highest-leverage. Distinguish official MCP, community MCPs (with stars / last commit), existing skills, and the company's own AI/agent posture. Fill `competition_assessment` with a sentence on whether existing wrappers leave room for differentiation.
- `people_signal` — 3–5 entries max. Used by scenario generation to ground "what would a developer realistically need help with right now."
- `access_classification` — five-tier model per surface. Be honest about `dead` (offline endpoints) and `internal` (not exposed) — these constrain what skills are buildable.
- **`internal_usage` (v2)** — for each candidate surface (in `product_surface`, `engineering_practices.notable_oss_authored`, or `agentic_landscape`), classify whether the company *itself* consumes the surface daily. The booth-aha-moment goal requires this — a popular OSS the company donated and moved on from is useless to an employee at our booth. Levels: `confirmed | inferred | weak | none`. Evidence sources: productized commercial layer (Spotify Portal proves Backstage is consumed), downstream internal tooling built on top (Honk on Backstage), eng-blog series describing daily workflows, conference talks where employees describe consuming the surface.

Proceed immediately to Step 4.

## Step 4 — Identify Candidate Skill Targets

Generate the `skill_targets[]` array. This is the most important section of the output. Discovery's job is to identify candidates; downstream steps build them.

For each candidate target, fill: `id`, `kind ∈ {api_wrapper, domain_skill, workflow_skill, tooling_assist}`, `title`, `confidence` (0.0–1.0), `rationale`, `supporting_source_ids`, `existing_competition`, `differentiation_hypothesis`, `expected_lift_signal ∈ {high, medium, low}`, plus the v2 fields below.

### Classify each candidate surface (consumer-side vs builder-side)

For every candidate surface, ask: **does the target company's daily-employee population CONSUME this surface, or BUILD it?**

- **Consumer-side** — employees use the surface as external customers would (Cursor at Anysphere, Backstage at Spotify, ArcticDB at Man Group). `USE/majority` targets pointing here ARE credible.
- **Builder-side** — the company *ships* the surface for outside consumers (Cohere v2 API, Cerebras Inference, Modal SDK, Sixfold underwriting API). `USE/majority` targets pointing at builder-side surfaces are WRONG.

When a candidate is builder-side, follow the three priority moves: (1) hunt aggressively for a consumer-side surface inside the company across blog / talks / hiring / X-on-X / handbooks / OSS / podcasts / eval harnesses — full search checklist in [classification-guide.md](classification-guide.md); (2) AUTHOR-shape target on the same surface (`small_team` population); (3) INTEGRATE/external target explicitly marked external.

`skip_reason` must enumerate which consumer-side searches were attempted and what each returned — generic "internal tooling is non-public" indicates lazy search.

Both shortcuts violate the contract: lazy-SKIP without a search trail AND over-inflating INTEGRATE/external to USE/majority to clear the BUILD threshold.

### Booth-aha framing — required per-target reasoning

For each candidate surface, answer:

1. **Internal usage** — which entry in `internal_usage[]` (Step 3) does this surface map to? `weak` or `none` surfaces are fallback only.
2. **Task shape** — `USE` (daily consumer), `AUTHOR` (small platform team extends it), or `INTEGRATE` (external builders).
3. **Target population** — describe who at the company would use this; pick `size_class ∈ {majority, minority, small_team, external}`.

**Population disambiguation rule:** enumerate *who at this target company* would invoke the skill vs. *who outside this company* would. If the daily-use population is dominated by people *outside* the target company, the shape is `INTEGRATE`/`external` — even when the surface is heavily used by external integrators. Traps and worked examples (Spotify Backstage authoring, PyannoteAI Cloud API, Forter TACP) live in [classification-guide.md](classification-guide.md).

### Required v2 fields per target

- `internal_usage_surface` — must reference an entry in the top-level `internal_usage[]` array.
- `task_shape ∈ {USE, AUTHOR, INTEGRATE}`.
- `target_population: { description, size_class }`.

### Kind selection bias

- `api_wrapper` is rarely the right shape — ~25% of routing candidates already publish official or community MCPs / skills. Prefer `workflow_skill` or `domain_skill` when an MCP already covers CRUD.
- `tooling_assist` is appropriate when the company ships SDKs / agent runtimes themselves (Trigger.dev, Modal, Together AI) and the leverage is teaching the SDK lifecycle, not wrapping an API.

### Booth-aha ranking

Sort by `score = confidence × iu_weight × pop_weight × ts_weight` — weight tables in [classification-guide.md](classification-guide.md). Score is advisory ranking only — BUILD verdict still requires raw `confidence ≥ 0.5` on at least one target. Cap candidates at 3 per company; sort descending so the human-gate sees the highest-leverage candidate first.

Proceed immediately to Step 5.

## Step 5 — Render Verdict

`verdict ∈ {BUILD, SKIP, AMBIGUOUS}`. Rules:

- `BUILD`: `skill_targets` has at least one entry with `confidence ≥ 0.5`. This is the default outcome when public surface is non-trivial.
- `SKIP`: `skill_targets` is empty AND search was exhaustive across every probe in Step 2. Populate `skip_reason`, `search_attempted`, and `would_change_verdict_if`.
- `AMBIGUOUS`: hidden multi-brand detected in Step 1 without a sub-brand specifier. Populate `sub_brands_detected[]` and exit before reaching Step 4.

Do not auto-resolve `AMBIGUOUS` — bouncing back to the caller is the right behavior, not picking a sub-brand silently.

Proceed immediately to Step 6.

## Step 6 — Validate Output

Run `skills/discovery/scripts/validate-output.py` against the in-memory JSON. The script checks: required top-level fields present, `verdict` is one of the three allowed values, every `skill_target.supporting_source_ids` references a real entry in `sources[]`, every `access_classification.surface` is referenced once. Exit non-zero with stderr diagnostic on validation failure; fix and re-validate before persisting.

Proceed immediately to Step 7.

## Step 7 — Persist Versioned Output

Run `skills/discovery/scripts/write-versioned-output.sh <company-slug>` piping the validated JSON to stdin. The script writes to `runs/<UTC-timestamp>/<company-slug>/discovery.json`, where the timestamp is set per skill invocation (not per company — a batch run shares one timestamp directory so all companies in the batch are diff-able as a unit).

### Critical: where to put `DISCOVERY_RUN_TS` in the pipeline

The `DISCOVERY_RUN_TS` env var must be applied to the **script invocation**, not to a `cat` / `echo` source. In a shell pipeline, `VAR=value command1 | command2` exports `VAR` to `command1` only — `command2` does not see it. Use one of:

```bash
# Option A: env var directly before the script (preferred for stdin-from-pipe)
echo "$JSON" | DISCOVERY_RUN_TS=2026-05-05T-round2 skills/discovery/scripts/write-versioned-output.sh <slug>

# Option B: heredoc / redirection (env var also goes before the script)
DISCOVERY_RUN_TS=2026-05-05T-round2 skills/discovery/scripts/write-versioned-output.sh <slug> <<'EOF'
{ ... validated JSON ... }
EOF

# Option C: bash -c subshell when chaining is unavoidable
DISCOVERY_RUN_TS=2026-05-05T-round2 bash -c 'echo "$JSON" | skills/discovery/scripts/write-versioned-output.sh <slug>'
```

Anti-pattern (silently drops the timestamp env var, falls back to a fresh per-second timestamp and leaks a stray run directory):

```bash
# WRONG: env var attaches to cat, not to the script
DISCOVERY_RUN_TS=2026-05-05T-round2 cat input.json | skills/discovery/scripts/write-versioned-output.sh <slug>
```

Output the path of the written file and finish here.
