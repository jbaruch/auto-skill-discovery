---
name: discovery
description: 'Automated source discovery and structure extraction for a single company (steps 1–2 of the workflow in `Automated Company Skills Eval App — Spec.md`). Takes a company name (optionally `parent/sub-brand` for MEGA_CORP cases that have been pre-scoped), produces a JSON artifact conforming to `discovery-output-contract.md`, and writes it to a versioned per-run directory. Output is the input to step 3 (human-gated target selection). Trigger phrases — "run discovery on X", "discover sources for X", "produce a discovery JSON for X".'
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

### Sub-step 4a — Classify each candidate surface as consumer-side or builder-side (REQUIRED before task_shape)

This step exists because the most common failure mode of round-2 was systematic mislabeling of API/SDK-provider companies. The agent saw "100s of companies use Cohere v2 API daily" and labeled `USE/majority` — but those are Cohere's *customers*, not Cohere's *employees*. The booth visitor builds the API; they don't call it from their app.

For every candidate surface, ask: **does the target company's daily-employee population CONSUME this surface, or BUILD it?**

- **Consumer-side surface** — the company's employees use it the same way external customers would. Examples:
  - Cursor IDE (Anysphere engineers code in Cursor)
  - Linear app (Linear engineers track issues in Linear)
  - Spotify Backstage (every Spotify engineer browses the catalog daily)
  - Internal monorepo conventions / internal design system (every engineer follows them)
  - WorkOS dogfooding AuthKit on the WorkOS dashboard
  - Man Group ArcticDB (quants run notebook research against it daily)

  → `USE/majority` targets pointing at this surface ARE credible.

- **Builder-side surface** — the company *ships* this surface for outside consumers. Their relationship is "we build it," not "we use it as customers do." Examples:
  - Cohere v2 Chat API (employees implement it; consumers are external)
  - Cerebras Inference API (Cerebras runs the cloud; customers send tokens)
  - turbopuffer query API (TP tunes the index; customers tune queries)
  - PyannoteAI Cloud API (PyannoteAI trains models; customers integrate)
  - Modal SDK from a customer's perspective (Modal builds Modal; customers use the SDK)
  - Astronomer's managed Airflow (the *cited* DAG-choreography pain belongs to customers like GetYourGuide)
  - Bright Data's primitives (BD builds the pipes; customers route requests)
  - Sixfold's underwriting API (Sixfold ships it; carrier integration engineers consume it)

  → `USE/majority` targets pointing at *that* surface are WRONG. Three legitimate moves instead, in priority order — exhaust each before falling to the next:

  1. **Hunt aggressively for a consumer-side surface inside the company.** "Builder-side at the public API" does NOT mean "no consumer-side surface exists." Internal surfaces are often described publicly. Run **all** of these searches before concluding none exists:
     - Engineering blog: search for `"we use internally"`, `"our internal"`, `"how we built"`, `"dogfood"`, `"we run on our own"` — many companies blog explicitly about internal tooling
     - Public conference talks: search YouTube / company channel for the last 24 months — engineers describing their own daily workflows is common
     - Hiring / job posts: senior eng listings often describe day-in-the-life and name internal tools
     - "X-on-X" patterns: companies notably build their own product with their own product (Modal-on-Modal, Vercel-on-Vercel, GitHub-on-GitHub, Spotify-on-Backstage) — this is a *consumer-side* signal even when the product is also sold externally
     - Engineering handbook / dev onboarding docs that leaked public (GitLab handbook, PostHog handbook)
     - OSS projects the company itself consumes (pyannote.audio at PyannoteAI, ArcticDB at Man Group, Backstage at Spotify) — OSS-as-signal still applies if the company *consumes* the OSS, not just authors it
     - Podcast / interview appearances by named engineers describing their workflow
     - Internal eval / test harnesses publicly documented (model eval pipelines, perf benchmarking suites)

     **The skip_reason must enumerate which of these searches were attempted and what each returned.** Generic phrasing like "internal tooling is non-public" is insufficient and indicates lazy search.

  2. **AUTHOR-shape target on the same surface** — "how to author a new endpoint in our API following our conventions." Population is `small_team` (the API team only). Score will be lower (AUTHOR weight is 0.5). Use this when option 1 finds nothing AND there's a real authoring pattern an agent could codify.

  3. **INTEGRATE/external target** explicitly marked external — for the company's customers, not its employees. Booth-aha score will be low (`external` × `INTEGRATE` weights ≈ 0.06). Acknowledge this honestly rather than relabeling.

**Honest-SKIP rule (after exhaustive consumer-side search):** if option 1's full search list has been run and documented in `skip_reason`, AND no candidate clears the BUILD floor of raw `confidence ≥ 0.5` in any task_shape, fall to Step 5 verdict `SKIP`. The `skip_reason` MUST list the specific consumer-side searches attempted (with what was searched and what came back) — not just a generic "non-public internal engineering" claim. A SKIP without a documented search trail is a process error and should be reworked.

The booth-aha score is **advisory ranking only**, not a verdict gate. A target with `confidence ≥ 0.5` but low booth-aha score (e.g., AUTHOR/small_team yielding ~0.10) still produces BUILD — but the low score honestly signals to the human-gate at workflow Step 3 that the booth-aha audience is narrow. Don't inflate population/task_shape labels to pump the score.

Inflating an INTEGRATE/external candidate to USE/majority to clear the BUILD threshold is a process error. Both shortcuts (lazy-SKIP without search and over-inflate-to-BUILD) violate the contract.

### Booth-aha framing — required reasoning step

The goal is a skill that produces an aha-moment for an employee of the target company stopping at our booth. That requires reasoning about *who at the company would actually use this skill* — not just whether the surface is publicly popular. Before drafting targets, answer for each candidate surface:

1. **Internal usage**: which entry in `internal_usage[]` (Step 3) does this surface map to? If `level: weak` or `none`, the surface produces useful targets only as a fallback when no `confirmed`/`inferred` surface yields a viable candidate.
2. **Task shape**: does the skill help a `USE` consumer of the surface (largest population — every engineer who touches it daily), an `AUTHOR` who extends/contributes to it (small platform team), or an `INTEGRATE` external builder (population is outside this company entirely)?
3. **Target population**: describe who at the company would use this and `size_class ∈ {majority, minority, small_team, external}`.

**Required population-disambiguation step before settling task_shape**: enumerate explicitly:

- *Who at this target company* would invoke this skill in their daily work? List the role(s).
- *Who outside this company* would invoke this skill? List the role(s) (third-party integrators, downstream customers, partner builders).
- If the daily-use population is dominated by people *outside* the target company, the task_shape is `INTEGRATE` and `size_class: external` — even when the surface is heavily used by external integrators. The booth visitor IS an employee of the target company; their job dictates the bucketing.

Concrete trap 1 — at Spotify, "Backstage scaffolder action authoring" is a popular-OSS target with `task_shape: AUTHOR` and `size_class: small_team` — the booth visitor is overwhelmingly *not* on the platform team. The right target is `task_shape: USE` for the catalog/scaffolder/tech-docs daily workflow with `size_class: majority`.

Concrete trap 2 — at PyannoteAI, "voice-AI pipeline using their cloud API" looks like USE because integrators heavily use the API, but those integrators are *external builders*, not PyannoteAI employees. Correct shape: `INTEGRATE` / `external`. PyannoteAI engineers themselves *build* the API; they don't consume it as users.

Concrete trap 3 — at Forter, the TACP integration target is an external-merchant task; Forter platform engineers wrote the protocol but don't integrate against it. Correct shape: `INTEGRATE` / `external`.

### Required v2 fields per target

- `internal_usage_surface` — must reference an entry in the top-level `internal_usage[]` array.
- `task_shape ∈ {USE, AUTHOR, INTEGRATE}`.
- `target_population: { description, size_class }`.

### Kind selection bias

- `api_wrapper` is rarely the right shape — ~25% of routing candidates already publish official or community MCPs / skills. Prefer `workflow_skill` (multi-step recipes layered on top of existing primitives) or `domain_skill` (idioms specific to the company's tooling) when an MCP already covers CRUD.
- `tooling_assist` is appropriate when the company ships SDKs / agent runtimes themselves (Trigger.dev, Modal, Together AI) and the leverage is teaching the SDK lifecycle, not wrapping an API.

### Booth-aha ranking

Sort the final array by:

```
score = confidence × iu_weight × pop_weight × ts_weight
```

Where `iu_weight` is `confirmed=1.0, inferred=0.7, weak=0.3, none=0.1`; `pop_weight` is `majority=1.0, minority=0.6, small_team=0.4, external=0.2`; `ts_weight` is `USE=1.0, AUTHOR=0.5, INTEGRATE=0.3`. Score is advisory ranking only — BUILD verdict still requires raw `confidence ≥ 0.5` on at least one target.

Cap candidates at 3 per company for the human-gate at step 3 of the workflow. Sort by score descending so the human sees the highest-leverage candidate first.

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
