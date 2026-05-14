# Contract Quick Reference — Produce Mode

One-page cheatsheet of `discovery-output-contract.md` for the produce-mode discovery skill. The contract document is authoritative; this file exists to keep the skill execution plan compact.

## Top-level shape (v3, produce)

```json
{
  "schema_version": 3,
  "mode": "produce",
  "company": { "name": "...", "canonical_url": "...", "discovered_at": "ISO-8601" },
  "verdict": "BUILD | SKIP | AMBIGUOUS",
  "domain_signal": { ... },
  "product_surface": { ... },
  "agentic_landscape": { ... },
  "people_signal": [ ... ],
  "access_classification": [ ... ],
  "skill_targets": [ ... ],
  "sources": [ ... ],
  "skip_reason": null
}
```

**Omit in produce-mode:** `internal_usage` (consume-mode only), `engineering_practices` (consume-mode signal). The validator rejects `internal_usage` if present.

## Field-by-field

### `domain_signal`

```json
{
  "summary": "one-sentence what-they-do plus current focus of the public API",
  "core_themes": ["stable product identity, e.g., 'payments'", "..."],
  "active_focus": ["last 3 months on the public surface, e.g., 'agentic commerce'", "..."],
  "domain_evidence": [{ "claim": "...", "source_id": "src_NN" }]
}
```

### `product_surface` — load-bearing for produce-mode

```json
{
  "apis": [
    {
      "kind": "graphql | rest | grpc | webhook",
      "endpoint": "https://...",
      "endpoint_family": null,
      "spec_url": "https://...",
      "auth": ["oauth2", "api_key"],
      "access_tier": "open | customer_only | partner_only | dead | internal"
    }
  ],
  "sdks": [{ "language": "...", "package": "...", "last_release": "...", "maintained": true }],
  "examples": [{ "url": "...", "kind": "starter_app | snippet | tutorial" }],
  "webhooks": { "available": true, "doc_url": "..." }
}
```

Use `endpoint_family` (and leave `endpoint: null`) when the surface is a product line of APIs without a single callable URL — typical for partner-gated banking/enterprise APIs where the spec is published but no public endpoint is.

### `agentic_landscape`

```json
{
  "official_mcp": { "url": "...", "auth": "oauth", "scope": "..." },
  "community_mcps": [{ "repo": "...", "stars": 0, "last_commit": "..." }],
  "existing_skills": [{ "registry": "tessl | github | agentskills.io", "name": "...", "url": "..." }],
  "company_ai_posture": {
    "ships_ai_features": true,
    "publishes_ai_research": false,
    "evidence_source_ids": ["src_NN"]
  },
  "competition_assessment": "one sentence on whether existing wrappers leave room for the proposed targets"
}
```

### `people_signal`

```json
[
  {
    "name": "...",
    "role": "Developer Relations | DX | API engineer",
    "public_handles": { "twitter": "...", "github": "..." },
    "current_focus": "...",
    "evidence_source_ids": ["src_NN"]
  }
]
```

Cap at 3–5 entries. Focus on developer-facing engineers / DX / DevRel, not internal platform teams.

### `access_classification`

```json
[
  { "surface": "<product-name>", "tier": "open|customer_only|partner_only|dead|internal", "barriers": ["..."] }
]
```

One entry per distinct surface (API, SDK, repo, doc).

### `skill_targets` (produce-mode shape)

```json
[
  {
    "id": "tgt_NN",
    "kind": "api_wrapper | domain_skill | workflow_skill | tooling_assist",
    "title": "...",
    "confidence": 0.0,
    "rationale": "...",
    "supporting_source_ids": ["src_NN"],
    "existing_competition": "...|null",
    "differentiation_hypothesis": "...",
    "expected_lift_signal": "high | medium | low"
  }
]
```

**Do not include** `internal_usage_surface`, `task_shape`, or `target_population`. Cap at 3 candidates. Sort descending by raw `confidence`. Bias away from `api_wrapper` when an official MCP exists.

### Confidence calibration anchors

- Current OpenAPI/Swagger/GraphQL spec → +0.2; missing/stale → −0.2
- Multi-language SDKs with releases in last 90 days → +0.15; stale → 0; absent → −0.15
- `open` access tier → +0.1; `customer_only` / `partner_only` → −0.1
- No MCP + no community wrappers → +0.15; saturated landscape → −0.2
- Webhook surface with signed-verification complexity → +0.1

Stripe-like (current OpenAPI, multi-language SDKs, open, signed webhooks, no official MCP) ≈ 0.85. Sales-gated enterprise API with no public spec ≈ 0.35.

### `sources`

```json
[
  {
    "id": "src_NN",
    "url": "...",
    "kind": "official_docs | sdk | github_repo | blog_post | talk | mcp_server | skill_repo",
    "fetched_at": "ISO-8601",
    "freshness_signal": "changelog_within_2_weeks | last_commit_within_3_months | older_than_1_year",
    "authority_rank": 1
  }
]
```

Authority: 1 = official primary (developer docs, API reference), 2 = official secondary (engineering blog, talks about the API), 3 = community (community MCPs, third-party repos), 4 = third-party tutorials.

### SKIP shape

```json
{
  "verdict": "SKIP",
  "skip_reason": "...",
  "search_attempted": ["developer docs portal", "openapi spec", "official SDKs", "official MCP", "community MCPs", "skill repos", "webhooks"],
  "would_change_verdict_if": "..."
}
```

The `search_attempted` list MUST enumerate which produce-mode probes from Step 2 were tried and what each returned. Generic "no public API" without trail is a process error.

### AMBIGUOUS shape (hidden multi-brand detected without sub-brand specifier)

```json
{
  "verdict": "AMBIGUOUS",
  "sub_brands_detected": [
    { "name": "...", "github_org": "...", "docs_portal": "..." }
  ],
  "guidance": "Re-invoke with `<parent>/<sub-brand>`."
}
```

## Decision shortcuts

- **`BUILD` requires at least one target with `confidence ≥ 0.5`** AND a non-empty `sources[]` AND every `domain_evidence[].source_id` resolves.
- **`SKIP` only after exhaustive produce-mode probe set** (developer docs, OpenAPI spec, official SDKs, official MCP, community MCPs, skill repos, webhooks, auth/access surface, public examples). The skip_reason enumerates which probes were attempted and what each returned.
- **`AMBIGUOUS` is set in Step 1**, before reaching the dimension-extraction phase. Don't try to resolve sub-brands by silently picking one.
- **Difference from consume-mode**: no `internal_usage[]` reasoning, no booth-aha scoring, no `task_shape` distinction — the audience is generic external developer.
