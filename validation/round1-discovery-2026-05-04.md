# Round 1 — Discovery Validation — 2026-05-04

Stratified empirical validation of the four-bucket filter by running the automated discovery skill on 12 companies covering all buckets. Goal: measure drop-bucket false-positive rate and route-bucket BUILD rate before scaling to the full 312.

Outputs: `runs/2026-05-04T-round1/<slug>/discovery.json`. Plus 2 prior smoke-tests in `runs/2026-05-04T-smoke/`.

## Results

| Bucket | Company | Verdict | Targets / Notes |
|---|---|---|---|
| MEGA_CORP | Google | AMBIGUOUS | 11 sub-brands enumerated (Cloud, Workspace, Search, Ads, Android, Chrome, Firebase, YouTube, Maps, Gemini/AI, DeepMind) |
| MEGA_CORP | McKinsey & Company | AMBIGUOUS | QuantumBlack / Digital / Strategy split; technical surface lives at QuantumBlack |
| MEGA_CORP | Caesar Groep | AMBIGUOUS | 9 sub-brands detected via structural signals (separate GitHub orgs `CloudRepublic`, `Garansysbv`; multiple domains) |
| SELF_OR_NA | Anthropic | **BUILD** (all targets ≤0.55) | Surface IS real (Managed Agents beta, three-agent harness, Agent Skills standard). Filter drop is correct but for *strategic* reasons, not structural |
| SELF_OR_NA | NEA | SKIP | VC firm; investment marketing only, no callable surface |
| SELF_OR_NA | Ben's Bites | SKIP | Newsletter; placeholder GitHub (0★, last activity 2023-08), Substack-hosted |
| SELF_OR_NA | Vän Swim *(smoke)* | SKIP | Apparel; Shopify storefront, no eng surface |
| UNKNOWN | ORYX SOFTWARE | SKIP | 5 unrelated entities documented (KP Labs flight software, Oryx Dental, ORYX Systems SA, oryxsoft.qa, Tracxn-listed marketing); skill correctly refused to silently pick |
| RUN_DISCOVERY | Stripe | BUILD | 3 `workflow_skill` targets — Connect onboarding, webhook hardening, agentic-commerce wiring (Issuing-for-Agents, Agent Guardrails, MPP Shared Payment Tokens). Non-obvious finding: official MCP covers ~25 tools but omits Connect/Checkout/webhooks/tax — first-skill-in-market opportunity |
| RUN_DISCOVERY | Granola | BUILD | 3 targets, **zero `api_wrapper`** — meeting-to-artifact pipelines, API idioms (auth scope, summary-gating, cache drift), local-cache analytics. Meta-target handling worked as designed |
| RUN_DISCOVERY | Spotify | BUILD | 3 targets, all platform/OSS-side — Backstage Software Templates, Web API post-Feb-2026 migration, Backstage AiKA / MCP-broker. OSS-as-signal validated at scale on a non-Capital-One sector |
| RUN_DISCOVERY | Capital One | BUILD | 2 targets — DataProfiler+datacompy, Slingshot SDK. Regression test: matches hand-crafted reference's two flagship targets and access-tier classifications. Auto-discovery declined Cloud Custodian (mis-attributed) and rubicon-ml (low confidence) |
| RUN_DISCOVERY | Asparanta | SKIP | Sole-proprietor consultancy; protocol-resolved UNKNOWN→RUN_DISCOVERY upgrade correctly caught by SKIP gate |
| RUN_DISCOVERY | Linear *(smoke)* | BUILD | 3 `workflow_skill` targets — AIG-compliant Linear agent, Linear Releases workflow, sub-team triage. Caught Linear's July 2025 Agent Interaction SDK push that the hand-crafted reference predates |

## Aggregate metrics

| Bucket | Tested | Verdict pattern |
|---|---|---|
| MEGA_CORP | 3 | 3 AMBIGUOUS (100%) — filter exact-match |
| SELF_OR_NA | 4 | 3 SKIP + 1 BUILD-with-caveats (75% SKIP, 25% strategic-drop) |
| UNKNOWN | 1 | 1 SKIP with documented candidates |
| RUN_DISCOVERY | 6 | 5 BUILD + 1 SKIP (83% BUILD rate) |

**Drop-bucket false-positive rate**: 1/8 (12.5%) — only Anthropic surfaced BUILD, and that's the strategic-conflict case below, not a structural false positive.

**Route-bucket BUILD rate**: 5/6 (83%) — the one SKIP (Asparanta) was a thin-surface case the second-pass UNKNOWN→RUN_DISCOVERY upgrade correctly produced; discovery's SKIP gate caught it as designed.

## Findings

### 1. MEGA_CORP rule is exactly correct

Three for three: Google, McKinsey, Caesar Groep all returned AMBIGUOUS at Step 1 with sub-brands enumerated. The hidden-multi-brand active check fired on structural signals (Caesar Groep's separate GitHub orgs and domains) not just on the heuristic's example list. No revision needed.

### 2. SELF_OR_NA conflates structural and strategic drops — needs sub-rule

The single non-trivial filter finding from round 1: **Anthropic returned BUILD with structurally-valid targets (Managed Agents beta, three-agent harness, Agent Skills standard, MCP).** Surface is real, recent, and rich. The filter's drop is still correct, but for a different reason than the Vän Swim / Ben's Bites / NEA drops:

- Vän Swim / Ben's Bites / NEA: dropped because no engineering surface exists.
- Anthropic: dropped because Claude is the runtime executing the skill, `anthropics/skills/claude-api` already saturates the API-reference layer, the recursive-recommendation loop creates self-reference, and the same model would review the skill it shipped.

The current SELF_OR_NA bucket conflates these two reasons under one label. Recommendation: split into two sub-types:

- `SELF_OR_NA — no engineering surface` (apparel, podcasts, VCs, schools, branding agencies, etc.)
- `SELF_OR_NA — strategic conflict` (foundation labs whose model is the runtime: Anthropic, OpenAI; the user's own employer Tessl)

Both still drop, but for documented reasons. Future borderline cases (e.g., a future foundation-lab attendee) get explicit reasoning instead of implicit lumping.

### 3. UNKNOWN bucket residue handled cleanly

ORYX SOFTWARE returned SKIP with 5 distinct candidate entities documented in the JSON (KP Labs flight software, Oryx Dental SaaS, ORYX Systems SA, oryxsoft.qa, Tracxn-listed marketing). The skill refused to silently pick — exactly the spec'd behavior. Caller can re-invoke with `<entity>/<scope>` if any of the candidates is the intended target.

### 4. Meta-target handling working as spec'd

Granola's discovery produced **zero `api_wrapper` candidates** — the skill correctly biased away from the obvious wrap-the-API target because Granola's MCP saturates CRUD, and surfaced `workflow_skill` recipes (cross-tool composition, scope-boundary reasoning) plus a `domain_skill` target on idioms the MCP doesn't teach. The validation finding ("default differentiation should be scenario-driven recipe over wrap-the-API") shows up empirically in the skill's output, not just in the spec.

### 5. OSS-as-signal validated at scale on a new sector

Spotify, a consumer-music brand, routed to platform-engineering targets — Backstage Software Templates and Backstage AiKA / MCP-broker integration — not to the consumer Web API. The two highest-confidence/highest-lift targets came from the OSS portfolio, not from the product. The Capital One pattern (founding case study for OSS-as-signal) generalizes to a different sector.

### 6. Regression test passed

Capital One auto-discovery converged on the same two flagship targets (DataProfiler+datacompy, Slingshot SDK) as the hand-crafted reference, with the same access-tier classifications. Auto version is narrower (declined Cloud Custodian for being mis-attributed and rubicon-ml for low confidence) but matches the substance. The hand-crafted reference is reproducible by the automated pipeline.

### 7. Stripe finding worth noting

Stripe's discovery produced the most non-obvious finding: the official `mcp.stripe.com` covers only ~25 tools and explicitly *omits* Connect, Checkout Sessions, webhooks, tax, and most update operations. The "MCP saturates" assumption inverts on Stripe — narrowly-wrapped, broadly-empty. Plus Sessions 2026 just shipped Issuing-for-Agents + Agent Guardrails + MPP Shared Payment Tokens with no community wrappers — first-skill-in-market opportunity on fresh agent-commerce primitives. This is the kind of insight the validation findings predicted (~25% of routing candidates have meta-target shape, but the gaps are where the leverage is).

## Operational notes

- 9 of 12 round-1 agents failed on first launch with API connectivity errors (FailedToOpenSocket / ConnectionRefused / Stream idle timeout) after 8–13 minutes. Retry succeeded for all 9. Cause was a transient API outage, not a skill bug.
- 12 successful runs averaged ~85k tokens each. Full 312 ≈ 26M tokens. Token budget is the main constraint for scaling.
- Validator caught no issues across 12 outputs — schema is stable enough to scale.

## Recommendation

The filter is empirically validated with one revision (SELF_OR_NA strategic-vs-structural sub-rule, codified in `heuristics.md` after this report). Round 1's metrics support scaling to the full 312:

- Drop-bucket false-positive rate is acceptable (12.5%, all in the strategic-drop bucket which is by-design correct).
- Route-bucket BUILD rate is good (83%), and the one SKIP was a thin-surface case discovery's gate handled correctly.
- Discovery output quality is consistent with the hand-crafted reference (regression test passed) and surfaces non-obvious findings.

Next: launch round 2 covering the remaining 300 companies in batches.
