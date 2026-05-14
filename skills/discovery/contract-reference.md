# Contract Quick Reference

This is a one-page cheatsheet of `discovery-output-contract.md` for the discovery skill. The contract document is authoritative; this file exists to keep the skill execution plan compact.

## Top-level shape (v2)

```json
{
  "schema_version": 2,
  "company": { "name": "...", "canonical_url": "...", "discovered_at": "ISO-8601" },
  "verdict": "BUILD | SKIP | AMBIGUOUS",
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

`schema_version: 1` is the original shape (no `internal_usage`, no `task_shape`/`target_population` on targets). v1 outputs remain valid; new outputs use v2.

## Field-by-field

### `domain_signal`

```json
{
  "summary": "one-sentence what-they-do plus current focus",
  "core_themes": ["stable identity, e.g., 'issue tracking'", "..."],
  "active_focus": ["last 3 months, e.g., 'MCP support'", "..."],
  "domain_evidence": [{ "claim": "...", "source_id": "src_NN" }]
}
```

### `product_surface`

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

### `engineering_practices`

```json
{
  "languages": ["python", "typescript"],
  "notable_oss_authored": [
    { "name": "...", "domain": "...", "now_owned_by": "CNCF | null" }
  ],
  "patterns_observed": ["serverless-first", "..."],
  "notes": "free-form. Use to capture *why an empty list is meaningful* — e.g., 'Linear authors no public OSS; their footprint is product-only, not platform.'"
}
```

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
  "competition_assessment": "one sentence on whether existing wrappers leave room"
}
```

### `people_signal`

```json
[
  {
    "name": "...",
    "role": "...",
    "public_handles": { "twitter": "...", "github": "..." },
    "current_focus": "...",
    "evidence_source_ids": ["src_NN"]
  }
]
```

Cap at 3–5 entries.

### `access_classification`

```json
[
  { "surface": "<product-name>", "tier": "open|customer_only|partner_only|dead|internal", "barriers": ["..."] }
]
```

One entry per distinct surface (API, SDK, repo, doc).

### `internal_usage` (v2)

```json
[
  {
    "surface": "<must match an entry in product_surface, engineering_practices, or agentic_landscape>",
    "level": "confirmed | inferred | weak | none",
    "evidence_source_ids": ["src_NN"],
    "evidence_summary": "one-line why this level"
  }
]
```

Levels:

- `confirmed` — productized commercial layer, downstream tooling built on top, eng-blog series describing daily use, talks where employees describe consuming the surface.
- `inferred` — circumstantial signal (hiring posts, talk topics) suggests internal use.
- `weak` — surface exists but only authorship signal — they donated it and may have moved on.
- `none` — no signal of internal usage; surface is purely external.

Skill_targets aimed at the booth-aha population should anchor on `confirmed` or `inferred` surfaces.

### `skill_targets` (v2)

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
    "expected_lift_signal": "high | medium | low",
    "internal_usage_surface": "<surface name from internal_usage[]>",
    "task_shape": "USE | AUTHOR | INTEGRATE",
    "target_population": {
      "description": "who at the company would actually use this",
      "size_class": "majority | minority | small_team | external"
    }
  }
]
```

Cap at 3 candidates. Bias away from `api_wrapper` when an official MCP exists.

#### Booth-aha ranking rule

Sort `skill_targets[]` by:

```
score = confidence × iu_weight × pop_weight × ts_weight
```

- `iu_weight`: confirmed=1.0, inferred=0.7, weak=0.3, none=0.1
- `pop_weight`: majority=1.0, minority=0.6, small_team=0.4, external=0.2
- `ts_weight`: USE=1.0, AUTHOR=0.5, INTEGRATE=0.3

Score is advisory ranking only — `BUILD` still requires raw `confidence ≥ 0.5` on at least one target.

Concrete: Backstage at Spotify — scaffolder *AUTHORING* (small_team + AUTHOR) scores `0.78 × 1.0 × 0.4 × 0.5 = 0.156`; daily *USE* (majority + USE) scores `0.85 × 1.0 × 1.0 × 1.0 = 0.85`. The USE-skill wins by ~5×.

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

Authority: 1 = official primary, 2 = official secondary (blog, talks), 3 = community, 4 = third-party tutorials.

### SKIP shape

```json
{
  "verdict": "SKIP",
  "skip_reason": "...",
  "search_attempted": ["docs portal", "github org", "blog", "talks", "MCPs", "key people"],
  "would_change_verdict_if": "..."
}
```

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
- **`SKIP` only after exhaustive search**. The validation pass shows that even regulated, non-tech-sector companies (Capital One, Man Group, G-Research) often produce `BUILD` via OSS-as-signal — don't fast-fail.
- **`AMBIGUOUS` is set in Step 1**, before reaching the dimension-extraction phase. Don't try to resolve sub-brands by silently picking one.
