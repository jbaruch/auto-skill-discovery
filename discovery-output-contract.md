# Discovery Output Contract

The structured artifact produced by the **discovery + extraction** phase (steps 1–2 of the workflow). Every downstream step (scenario generation, skill drafting, evals, report) consumes this contract. Stable shape > rich shape — get this right and the rest of the pipeline has a real target.

## Design principles

- **Intelligence over inventory.** The output is what we *learned about the company*, not a list of URLs we crawled. Sources are evidence, not the deliverable.
- **OSS-as-signal, not noise.** Infra tools authored by the company (e.g., Cloud Custodian at Capital One) reveal domain focus, even when they aren't "the company's product." They feed the domain-signal dimension and inform candidate skill targets.
- **Agentic discoveries are first-class.** Existing MCP servers, Claude Skills, AI-tool integrations, and the company's own AI/agent-engineering posture are the highest-priority signal — they tell us whether to build, what to build, and what we'd be competing with.
- **SKIP is rare and structured.** A SKIP verdict means there's nothing public to learn from — not "no callable API." Most companies produce a BUILD with one or more non-obvious targets.
- **Provenance always.** Every claim ties back to a source URL with a freshness signal.

## Top-level shape

```json
{
  "schema_version": 3,
  "mode": "consume",
  "company": {
    "name": "Linear",
    "canonical_url": "https://linear.app",
    "discovered_at": "2026-04-30T14:30:00Z"
  },
  "verdict": "BUILD",
  "domain_signal": { ... },
  "product_surface": { ... },
  "engineering_practices": { ... },
  "agentic_landscape": { ... },
  "people_signal": [ ... ],
  "access_classification": [ ... ],
  "internal_usage": [ ... ],
  "skill_targets": [ ... ],
  "sources": [ ... ],
  "skip_reason": null
}
```

**Schema versioning.** `schema_version: 1` is the original shape (no `internal_usage`, raw-confidence ranking). `schema_version: 2` adds `internal_usage`, `task_shape`, and `target_population` for the booth-aha ranking. `schema_version: 3` adds the top-level `mode` field which discriminates between **consume-mode** (the booth-aha pipeline — same field set as v2 with `internal_usage` and per-target `internal_usage_surface` / `task_shape` / `target_population` required) and **produce-mode** (the external-API pipeline — drops the v2 consume-side fields entirely; `skill_targets` rank by raw `confidence`). v1 and v2 outputs remain valid for existing files but new discovery runs emit v3. The `mode` field is required on every v3 output.

### Mode discrimination

- **`mode: "consume"`** — targets the surface the company's own engineers touch daily (internal dogfood, vendor stacks, conventions). Same field set as v2: `internal_usage[]` required at top level; each `skill_target` requires `internal_usage_surface`, `task_shape`, and `target_population`. Ranked by booth-aha score (see below).
- **`mode: "produce"`** — targets the company's external/public surface (APIs, SDKs, integrations they ship to customers). The audience is whoever consumes the public surface — internal employees, partner integrators, third-party developers — without distinguishing among them. Drops `internal_usage[]` at top level and the three v2 consume-side fields on each `skill_target`. Ranked by raw `confidence` only.

The same downstream pipeline (selection, scenario generation, skill build, evals, report) consumes both modes — only the discovery skill differs between them.

## Dimensions

### `domain_signal` — what does this company do and care about?

Extracted from blog topics, OSS portfolio, talk titles, repo themes. Drives scenario realism.

```json
{
  "summary": "Project management for software teams; recently focused on agent-native workflows.",
  "core_themes": ["issue tracking", "project planning", "agent integration"],
  "active_focus": ["MCP support", "Code Intelligence", "Linear Agent"],
  "domain_evidence": [
    { "claim": "Heavy AI/ML research investment", "source_id": "src_07" }
  ]
}
```

For Capital One this would surface: cloud cost governance, data quality, ML reproducibility — even though no banking API exists.

### `product_surface` — what's callable / consumable from outside

```json
{
  "apis": [
    {
      "kind": "graphql",
      "endpoint": "https://api.linear.app/graphql",
      "endpoint_family": null,
      "spec_url": "https://studio.apollographql.com/public/Linear-API/...",
      "auth": ["oauth2", "api_key"],
      "access_tier": "open"
    }
  ],
  "_note_on_endpoint_vs_endpoint_family": "Use `endpoint` for a single callable URL. Use `endpoint_family` (and leave `endpoint` null) when the surface is a product line of APIs without a single callable URL — typical for partner-gated banking/enterprise APIs where the spec is published but no public endpoint is.",
  "sdks": [
    { "language": "typescript", "package": "@linear/sdk", "last_release": "2026-04-21", "maintained": true }
  ],
  "examples": [ { "url": "...", "kind": "starter_app" } ],
  "webhooks": { "available": true, "doc_url": "..." }
}
```

### `engineering_practices` — tools, patterns, conventions the company uses internally (signal extracted from public OSS + blog)

Drives "adjacent skill" targets — even if there's no product API, a skill teaching the company's *engineering style* may be useful.

```json
{
  "languages": ["python", "typescript"],
  "notable_oss_authored": [
    { "name": "Cloud Custodian", "domain": "cloud governance", "now_owned_by": "CNCF" },
    { "name": "DataProfiler", "domain": "data profiling" }
  ],
  "patterns_observed": ["serverless-first", "CNCF-style governance-as-code"],
  "notes": "Free-form text. Use this to capture *why an empty list is meaningful* — e.g., 'Linear authors no public OSS; their footprint is product-only, not platform.' Absence is itself signal."
}
```

### `agentic_landscape` — first-class section because agentic context is highest-leverage

```json
{
  "official_mcp": { "url": "https://mcp.linear.app/sse", "auth": "oauth", "scope": "issues, projects, comments" },
  "community_mcps": [
    { "repo": "jerhadf/linear-mcp-server", "stars": 234, "last_commit": "..." }
  ],
  "existing_skills": [
    { "registry": "tessl", "name": "...", "url": "..." }
  ],
  "company_ai_posture": {
    "ships_ai_features": true,
    "publishes_ai_research": false,
    "evidence_source_ids": ["src_03", "src_11"]
  },
  "competition_assessment": "Official MCP covers core CRUD. Skill differentiation likely lives in higher-level workflows + scenario-driven recipes, not API wrapping."
}
```

### `people_signal` — key public-facing engineers/PMs and their focus

```json
[
  {
    "name": "Tuomas Artman",
    "role": "Co-founder / CTO",
    "public_handles": { "twitter": "@artman", "github": "artman" },
    "current_focus": "Linear Agent, MCP",
    "evidence_source_ids": ["src_12"]
  }
]
```

Limited to 3–5 people. Used by scenario generation to ground "what would a developer realistically need help with right now."

### `access_classification` — five-tier model

For each distinct surface (API, SDK, repo, doc):

```json
[
  { "surface": "Linear GraphQL API", "tier": "open", "barriers": ["free signup"] },
  { "surface": "DevExchange Customer Transactions", "tier": "partner_only", "barriers": ["contract"] },
  { "surface": "Slingshot API", "tier": "customer_only", "barriers": ["paid product"] },
  { "surface": "Nessie mock API", "tier": "dead", "barriers": ["endpoint offline"] },
  { "surface": "Internal core banking", "tier": "internal", "barriers": ["not exposed"] }
]
```

Tiers: `open` | `customer_only` | `partner_only` | `dead` | `internal`.

### `internal_usage` — does the company itself consume this surface? *(consume-mode only)*

The booth-aha-moment goal is producing a skill that helps an actual employee of the target company in their daily work. A surface that the company *authored* but does not *consume* internally is a false-positive target — popular publicly but useless to the booth visitor. This dimension distinguishes "they shipped it" from "they live in it."

For each surface relevant to a candidate `skill_target`:

```json
[
  {
    "surface": "Backstage (OSS framework)",
    "level": "confirmed",
    "evidence_source_ids": ["src_05", "src_06", "src_08"],
    "evidence_summary": "Spotify productized Backstage as Spotify Portal (commercial); Honk background coding agent built on top of Backstage; multi-part eng-blog series describing daily Backstage workflows."
  },
  {
    "surface": "Spotify Web API",
    "level": "weak",
    "evidence_source_ids": ["src_02"],
    "evidence_summary": "External-developer surface; Spotify employees consume it only as creators of the API, not as users of it."
  }
]
```

Levels:

- `confirmed` — productized commercial layer, downstream internal tooling built on top, eng-blog series describing daily use, conference talks where employees describe consuming the surface.
- `inferred` — circumstantial signal (hiring posts, talk topics, OSS patterns) suggests internal use but no direct evidence.
- `weak` — surface exists but evidence is only authorship; the company donated it and may have moved on.
- `none` — no public signal of internal usage; surface is purely external.

Reasoning rule: surfaces with `level: confirmed` or `inferred` are the candidate set for skill_targets aimed at the booth-aha population. `weak` and `none` surfaces should produce skill_targets only if no `confirmed`/`inferred` surface yields a viable target.

### `skill_targets` — candidate skills the pipeline could build

The most important section. Discovery's job is to identify these; downstream steps build them. Shape differs by mode: **consume-mode** carries `internal_usage_surface`, `task_shape`, and `target_population` and ranks by booth-aha score (see below); **produce-mode** omits those three fields and ranks by raw `confidence`.

#### Consume-mode shape

```json
[
  {
    "id": "tgt_01",
    "kind": "workflow_skill",
    "title": "Backstage daily-USE skill: catalog navigation, scaffolder runs, tech-docs lookup",
    "confidence": 0.85,
    "rationale": "Backstage is Spotify's primary IDP; every Spotify engineer touches the catalog and scaffolder daily. Existing OSS docs cover the framework but no skill packages the user-side workflow.",
    "supporting_source_ids": ["src_03", "src_05", "src_06"],
    "existing_competition": "Backstage docs; no agent-skill packaging.",
    "differentiation_hypothesis": "Encode the user-side commands (find a service, trigger a template, register a component, jump to TechDocs) as a single skill that the agent executes against the user's local Backstage instance.",
    "expected_lift_signal": "high",
    "internal_usage_surface": "Backstage (OSS framework)",
    "task_shape": "USE",
    "target_population": {
      "description": "All Spotify engineers (rank-and-file IC and senior, not just the platform team) who interact with Backstage daily as their IDP.",
      "size_class": "majority"
    }
  }
]
```

#### Produce-mode shape

```json
[
  {
    "id": "tgt_01",
    "kind": "api_wrapper",
    "title": "Stripe Payments — agent-driven checkout-session creation and webhook handling",
    "confidence": 0.85,
    "rationale": "Stripe's Payments API is the canonical entry point for ~90% of integrations; OpenAPI spec is current, official TypeScript/Python SDKs are well-maintained, and webhook signature verification is the highest-failure-mode step for new integrators.",
    "supporting_source_ids": ["src_01", "src_03", "src_07"],
    "existing_competition": "Official Stripe MCP covers core CRUD; community examples mostly demonstrate happy-path checkout but not signed-webhook verification end-to-end.",
    "differentiation_hypothesis": "Encode the full checkout-to-webhook lifecycle (idempotency keys, signed webhook verification, retry handling) as a single skill the agent executes against Stripe's test mode.",
    "expected_lift_signal": "high"
  }
]
```

Target kinds: `api_wrapper` | `domain_skill` | `workflow_skill` | `tooling_assist`.

Task shapes (consume-mode only):

- `USE` — the skill helps a consumer of the surface do their daily job (e.g., navigate a Backstage catalog, query a Stripe ledger, wire a Linear workflow). Population is the majority of engineers who touch the surface.
- `AUTHOR` — the skill helps someone who extends or contributes to the surface itself (e.g., write a new Backstage scaffolder action plugin, build a custom Postman collection, author a Stripe webhook integration). Population is typically a small platform/integration team.
- `INTEGRATE` — the skill helps a third-party builder hooking into the surface from outside the company (e.g., wrap the Spotify Web API for a different product). Population is external builders, not the booth visitor.

Target population `size_class` (consume-mode only):

- `majority` — most engineers at the company touch this in a typical week.
- `minority` — a specific function/team uses it regularly (e.g., data engineers, ML engineers).
- `small_team` — a single platform/infra team owns it.
- `external` — primary population is outside the company (cross-checked against `INTEGRATE` task_shape).

#### Booth-aha ranking rule (consume-mode)

Order `skill_targets` by combined score, biasing toward targets that would actually help an employee of the target company stopping at our booth:

```
score = confidence
      × internal_usage_weight(level)
      × population_weight(size_class)
      × task_shape_weight(shape)
```

Where:

- `internal_usage_weight`: confirmed=1.0, inferred=0.7, weak=0.3, none=0.1
- `population_weight`: majority=1.0, minority=0.6, small_team=0.4, external=0.2
- `task_shape_weight`: USE=1.0, AUTHOR=0.5, INTEGRATE=0.3

Concrete example: Backstage scaffolder *AUTHORING* at Spotify scores `0.78 × 1.0 × 0.4 × 0.5 = 0.156`; Backstage daily *USE* scores `0.85 × 1.0 × 1.0 × 1.0 = 0.85`. The USE-skill wins by ~5×, matching the booth-aha goal.

The score is advisory ranking, not a verdict gate — `BUILD` still requires at least one target with raw `confidence ≥ 0.5`, and the skill_targets array is sorted by score so the human-gate at workflow step 3 sees the highest-leverage candidate first.

#### Produce-mode ranking rule

Produce-mode targets rank by raw `confidence` only. No booth-aha multiplier — produce-mode doesn't distinguish internal vs external consumers of the surface, and every target is implicitly INTEGRATE-shaped (the audience is whoever calls the public API). BUILD still requires at least one target with `confidence ≥ 0.5`; the array is sorted descending by `confidence` so the human-gate sees the highest-confidence candidate first.

Confidence weighting in produce-mode comes from public-surface quality: OpenAPI spec freshness, SDK maintenance, official MCP existence, docs completeness, and presence-or-absence of existing community skills on the same surface (more competition → lower confidence the new skill clears the lift bar).

### `sources` — provenance for everything above

```json
[
  {
    "id": "src_01",
    "url": "https://linear.app/developers",
    "kind": "official_docs",
    "fetched_at": "2026-04-30T14:25:00Z",
    "freshness_signal": "changelog_within_2_weeks",
    "authority_rank": 1
  }
]
```

Authority rank: 1 (official primary), 2 (official secondary — blog, talks), 3 (community), 4 (third-party tutorials).

## Verdict & SKIP

`verdict ∈ { BUILD, SKIP }`. SKIP only when `skill_targets` is empty AND the search was exhaustive. SKIP responses must include:

```json
{
  "skip_reason": "No public surface beyond marketing site. No GitHub org, no docs portal, no engineering blog, no public talks. Likely stealth or pre-product company.",
  "search_attempted": ["docs portal", "github org", "blog", "talks", "MCPs", "key people"],
  "would_change_verdict_if": "Company publishes engineering content or opens a public repo."
}
```

The reframe matters: a regulated company with substantial OSS + active blog produces a BUILD with non-obvious targets — not a SKIP.

## What this contract is NOT

- Not a crawler config — *what* to fetch is the discoverer's problem; this contract describes the *output*
- Not a scenario list — scenarios are derived in step 3 from `domain_signal` + `skill_targets`
- Not the skill itself — the skill is built in step 5 from `skill_targets[selected]`

## Open questions

- Per-target eval-budget hint: should discovery suggest scenario count per target?
- Cache lifetime: how long is a discovery result usable before re-run?

## Resolved

- **Target selection** *(2026-04-30)*: Discovery emits all candidate targets ranked by confidence. A human picks one of the top suggestions before scenario generation. This is the only manual step in the pipeline.
