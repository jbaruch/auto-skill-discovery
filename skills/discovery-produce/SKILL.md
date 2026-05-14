---
name: discovery-produce
description: 'Produce-mode automated source discovery for a single company (steps 1–2 of the workflow, A1 cell of the operating-modes 2x2 in `SPEC.md`). Takes a company name (optionally `parent/sub-brand` for MEGA_CORP cases that have been pre-scoped) and produces a discovery JSON conforming to `discovery-output-contract.md` — schema_version 3, mode=produce. Targets the company external/public API/SDK surface — what an outside developer would consume — rather than the internal dogfood surfaces consume-mode targets. Output is the input to step 3 (human-gated target selection). Trigger phrases: "run produce-mode discovery on X", "discover external API surface for X", "A1 discovery on X", "produce a produce-mode discovery JSON for X".'
---

# Discovery Skill — Produce Mode

Process steps in order. Do not skip ahead.

This skill is the A1 cell of the 2x2 in the spec: produce-mode (external API/SDK surface) with no personalization (company name is the only input). The output drives downstream skill-build + eval for an agent that consumes the company's public API the way an external developer would.

The companion skill `discovery` (consume-mode, B1/B2) targets the *opposite* surface — what the company's own engineers touch daily. The two skills share an output contract and a downstream pipeline; only step 1–2 (discovery) differs between them. Use this skill when the booth motion is "demonstrate Tessl improving agent use of *the company's product*"; use the consume-mode skill when the motion is "demonstrate Tessl improving agent use of *what the company's engineers use daily*."

## Step 1 — Resolve Input and Detect Hidden Multi-brand

Take the input (company name, or `parent/sub-brand` for already-scoped MEGA_CORP cases).

Apply alias resolution before keying searches:

- **Rebrand check**: Google `"<name>" formerly known as` and `"<name>" rebranded` — if the company has rebranded recently, the GitHub org and docs portal often still use the legacy name (Ona = Gitpod, runZero = Rumble, Altrina = Tessa).
- **Acquisition check**: Google `"<name>" acquired by` — note the acquirer; the engineering surface may have moved or been integrated.
- **DBA / trading-as**: if the input contains `t/a` or `operated by`, resolve to the operating entity.

Run the hidden-multi-brand check from `skills/company-list-filter/heuristics.md` § MEGA_CORP — count distinct GitHub orgs / docs portals / sub-brand pages. If multi-brand structure is detected and the input did NOT include a sub-brand specifier, write a `verdict: "AMBIGUOUS"` JSON to the run directory listing the sub-brands and exit. The caller must re-invoke with `parent/sub-brand`.

Document every alias / acquisition / multi-brand finding as a `sources[]` entry now — they are evidence the rest of the pipeline depends on.

Proceed immediately to Step 2.

## Step 2 — Source Discovery (public-surface focus)

Find sources for the company's external/public API surface. Produce-mode is narrower than consume-mode discovery — focus exclusively on what an outside developer would touch. The minimum probe set:

- **Official developer docs / API portal**: try `developer.<domain>`, `docs.<domain>`, `<domain>/docs`, `api.<domain>`, `<domain>/developers`. Fetch the landing page and the API reference index. Note recency of the latest changelog entry.
- **OpenAPI / GraphQL spec**: search for `<company> openapi`, `<company> swagger`, `<company> graphql schema`. A published, current spec is the strongest produce-mode signal — the agent has a complete contract to teach.
- **Official SDKs**: enumerate the languages the company ships SDKs in. For each, note the package name, latest release date, and active maintenance (commits in the last 90 days). Multi-language SDK with recent releases → high confidence.
- **Official MCP**: search the company's docs and GitHub for `mcp` / `MCP server` / `model context protocol`. An official MCP is competition for `api_wrapper` targets but a baseline reference for `workflow_skill` targets layered on top.
- **Community MCPs**: probe `smithery.ai`, `mcp.so`, `github.com/punkpeye/awesome-mcp-servers`, and `github.com/topics/mcp-server` for community-built servers naming the company. High community-MCP density → wrapper space is crowded; bias toward workflow- or domain-skill targets instead.
- **Existing public skills**: search `github.com/<org>/skills` and `github.com/topics/agent-skills`. If the company already publishes its own skill repo (Cursor, Sentry, BFL, Telnyx pattern), that is *direct prior art* — confidence must reflect the gap between published skills and the proposed target, not the absence of any skill at all.
- **Webhooks / event surfaces**: search for `<company> webhooks`, `<company> events`. Webhook handling is the highest-failure-mode step for new integrators and a frequent target for `workflow_skill` candidates.
- **Authentication surface**: note auth mechanisms (OAuth2, API key, JWT, mTLS) and signup friction (free tier, dev sandbox, requires-sales-call). A surface gated behind sales is `partner_only` or `customer_only` and produces a lower-confidence target than `open`.
- **Public examples**: official sample apps, starter templates, hackathon kits. The presence of these is a positive signal — the company expects external developers and has invested in their onboarding.

Record everything as `sources[]` entries with `id`, `url`, `kind`, `fetched_at`, `freshness_signal`, and `authority_rank` per the contract. Authority rank: `1` for official primary, `2` for official secondary (engineering blog, talks about the API), `3` for community (community MCPs, third-party repos), `4` for third-party tutorials.

Proceed immediately to Step 3.

## Step 3 — Extract Contract Dimensions

Fill the produce-mode-relevant dimensions of [discovery-output-contract.md](../../discovery-output-contract.md). Quick reference at [contract-reference.md](contract-reference.md) — read it once for this run.

Dimensions to populate:

- `domain_signal` — what does the company do and what's the current focus of the public API? Extract from the developer docs landing page, recent changelog, and any blog posts announcing new API features. `core_themes` capture the stable product identity (e.g., "payments", "issue tracking"); `active_focus` captures what's shipping in the last 3 months on the public surface.
- `product_surface` — **the load-bearing section for produce-mode.** Every API, SDK, and webhook surface enumerated, with `access_tier` honestly classified per the five-tier model (`open | customer_only | partner_only | dead | internal`). Use `endpoint_family` (and leave `endpoint: null`) when the surface is a product line of APIs without a single callable URL — typical for partner-gated banking/enterprise APIs where the spec is published but no public endpoint is. SDK entries must reflect actual maintenance status — a stale repo with `last_release` >18 months ago is `maintained: false` regardless of how popular the package once was.
- `agentic_landscape` — distinguish official MCP, community MCPs (with stars / last commit), existing public skills, and the company's own AI/agent posture. Fill `competition_assessment` with a sentence on whether existing wrappers leave room for differentiation. For produce-mode, this section is critical: a saturated agentic landscape (official MCP + multiple community MCPs + published skill repos) reduces confidence on `api_wrapper` targets and pushes the candidate set toward `workflow_skill` or `domain_skill`.
- `access_classification` — five-tier model per surface. Be honest about `dead` (offline endpoints), `partner_only` (sales-gated), and `customer_only` (paid product required). Produce-mode targets anchored on `partner_only` or `customer_only` surfaces produce lower-confidence candidates because the agent's user can't trivially test them.
- `people_signal` — 3–5 entries max, focused on developer-facing engineers / DX / DevRel — the people whose public talks and blog posts describe the API. Used by scenario generation to ground "what would a developer realistically need help with right now."

**Produce-mode does NOT carry**: `internal_usage[]` (that's consume-mode only), `engineering_practices` (consume-mode signal about how the company codes internally — irrelevant for produce-mode targets). Omit both top-level fields from the output JSON.

Proceed immediately to Step 4.

## Step 4 — Identify Candidate Skill Targets

Generate the `skill_targets[]` array. For produce-mode, every target is implicitly addressed at "whoever consumes the public API" — sales engineers, partner integrators, third-party developers, or even internal employees who happen to use their own API externally. The booth-aha distinction between internal/external audiences does NOT apply; the audience is generic.

For each candidate target, fill: `id`, `kind ∈ {api_wrapper, domain_skill, workflow_skill, tooling_assist}`, `title`, `confidence` (0.0–1.0), `rationale`, `supporting_source_ids`, `existing_competition`, `differentiation_hypothesis`, `expected_lift_signal ∈ {high, medium, low}`.

**Do NOT carry** `internal_usage_surface`, `task_shape`, or `target_population` — those are consume-mode fields. The validator rejects them in produce-mode.

### Kind selection bias

- `api_wrapper` — the default produce-mode kind. The skill wraps the company's public API into agent-friendly recipes (auth, common endpoint sequences, error handling, retry/idempotency conventions). Suitable when the API has a clear primary surface (Stripe Payments, Linear GraphQL, Twilio Messaging) AND no official MCP already covers the same ground.
- `workflow_skill` — multi-step recipes layered on top of existing primitives (signed webhook verification with retry; OAuth flow + token refresh; idempotent batch upload + reconciliation). Strongest when official MCP exists for basic CRUD but composed workflows are not packaged.
- `domain_skill` — idioms specific to the company's API style (e.g., "Stripe-style expand parameters", "Linear's filter DSL", "Plaid's environment-keyed sandbox/development/production pattern"). Suitable when the API has non-obvious conventions a generic OpenAPI-driven wrapper would miss.
- `tooling_assist` — appropriate when the company ships SDKs or agent runtimes themselves (Trigger.dev, Modal, Together AI) and the leverage is teaching the SDK lifecycle (init, deploy, test) rather than wrapping an API.

### Confidence calibration

The confidence score reflects the *likelihood that a built skill would clear the lift bar in evals* — not the popularity of the company or its API. Calibrate against:

- **Public spec quality** — current OpenAPI/Swagger/GraphQL spec → +0.2; missing or stale spec → −0.2.
- **SDK maturity** — multi-language SDKs with releases in the last 90 days → +0.15; single language or stale → +0.0; no SDK → −0.15.
- **Auth/access friction** — `open` tier (free signup, sandbox available) → +0.1; `customer_only` or `partner_only` → −0.1 (agent can't trivially test; eval scenarios become harder to ground).
- **Competition density** — no MCP and no community wrappers → +0.15; official MCP + multiple community wrappers + published company skills repo → −0.2 (the skill must clear a higher bar to add lift). Note the asymmetry: a saturated landscape doesn't kill the BUILD, but it shifts the differentiation hypothesis from "wrap the API" to "package a workflow the wrappers don't cover."
- **Webhook / event complexity** — present and frequently mis-implemented (signature verification, replay) → +0.1; absent → +0.0.

Anchor: a Stripe-like surface (current OpenAPI, multi-language SDKs, open access, signed webhooks, no official MCP) lands around `0.85`. A surface gated entirely behind enterprise sales with no public spec lands around `0.35` — eligible as a BUILD only if the agentic-landscape signal is otherwise empty and the target is honestly framed as `partner_only`-anchored.

### Cap and ordering

Cap candidates at 3 per company for the human-gate at step 3 of the workflow. Sort by `confidence` descending — produce-mode does not use the booth-aha score.

Proceed immediately to Step 5.

## Step 5 — Render Verdict

`verdict ∈ {BUILD, SKIP, AMBIGUOUS}`. Rules:

- `BUILD`: `skill_targets` has at least one entry with `confidence ≥ 0.5`. This is the default outcome when the company has a non-trivial public API surface.
- `SKIP`: `skill_targets` is empty AND the public-surface search was exhaustive. Produce-mode SKIPs typically come from one of three patterns:
  1. **No public API at all** — consultancies, individual people, financial firms with no developer portal. Document which probes returned empty.
  2. **All surfaces `dead`** — APIs deprecated or sunset (Yahoo APIs, legacy SOAP services). Note end-of-life status.
  3. **All surfaces `internal`** — the company has a "developer site" that's really partner documentation behind a contract, with no self-service signup or sandbox. Honest SKIP rather than producing a target the eval can't ground.

  Populate `skip_reason`, `search_attempted`, and `would_change_verdict_if`. Generic phrasing like "no public API" is insufficient — list the specific probes from Step 2 that were attempted and what each returned.

- `AMBIGUOUS`: hidden multi-brand detected in Step 1 without a sub-brand specifier. Populate `sub_brands_detected[]` and exit before reaching Step 4.

Do not auto-resolve `AMBIGUOUS` — bouncing back to the caller is the right behavior, not picking a sub-brand silently.

Proceed immediately to Step 6.

## Step 6 — Validate Output

Run `skills/discovery/scripts/validate-output.py` against the in-memory JSON. The script accepts produce-mode v3 outputs and enforces:

- `schema_version: 3`
- `mode: "produce"`
- Absence of consume-mode fields (`internal_usage[]` top-level; `internal_usage_surface`, `task_shape`, `target_population` per target)
- All cross-references resolve (skill_targets → sources, etc.)

Exit non-zero with stderr diagnostic on validation failure; fix and re-validate before persisting.

Proceed immediately to Step 7.

## Step 7 — Persist Versioned Output

Run `skills/discovery/scripts/write-versioned-output.sh <company-slug>` piping the validated JSON to stdin. The script (shared with consume-mode discovery) writes to `runs/<UTC-timestamp>/<company-slug>/discovery.json`, where the timestamp is set per skill invocation (not per company — a batch run shares one timestamp directory so all companies in the batch are diff-able as a unit).

### Critical: where to put `DISCOVERY_RUN_TS` in the pipeline

The `DISCOVERY_RUN_TS` env var must be applied to the **script invocation**, not to a `cat` / `echo` source. In a shell pipeline, `VAR=value command1 | command2` exports `VAR` to `command1` only — `command2` does not see it. Use one of:

```bash
# Option A: env var directly before the script (preferred for stdin-from-pipe)
echo "$JSON" | DISCOVERY_RUN_TS=2026-05-13T-snyk skills/discovery/scripts/write-versioned-output.sh <slug>

# Option B: heredoc / redirection (env var also goes before the script)
DISCOVERY_RUN_TS=2026-05-13T-snyk skills/discovery/scripts/write-versioned-output.sh <slug> <<'EOF'
{ ... validated JSON ... }
EOF

# Option C: bash -c subshell when chaining is unavoidable
DISCOVERY_RUN_TS=2026-05-13T-snyk bash -c 'echo "$JSON" | skills/discovery/scripts/write-versioned-output.sh <slug>'
```

Anti-pattern (silently drops the timestamp env var, falls back to a fresh per-second timestamp and leaks a stray run directory):

```bash
# WRONG: env var attaches to cat, not to the script
DISCOVERY_RUN_TS=2026-05-13T-snyk cat input.json | skills/discovery/scripts/write-versioned-output.sh <slug>
```

Output the path of the written file and finish here.
