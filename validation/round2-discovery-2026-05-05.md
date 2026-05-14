# Round 2 — Discovery Validation — 2026-05-05

Stratified empirical validation of the four-bucket filter and the v2 booth-aha contract by running the automated discovery skill on **30 category representatives** spanning 30 distinct categories from the conference attendee list. Goal: validate categories, not individual companies — one rep per category, drop similar duplicates.

Outputs: `runs/2026-05-05T-round2/<slug>/discovery.json`. All 30 validated against `schema_version: 2`.

## Aggregate metrics

| Verdict | Count | Share |
|---|---|---|
| BUILD | 28 | 93% |
| SKIP | 2 | 7% |
| AMBIGUOUS | 0 | — |

(MEGA_CORP / AMBIGUOUS path was already validated in round 1 — 3/3 — so no new picks here.)

## Per-category results

| # | Category | Pick | Verdict | Top target shape | Score | Notes |
|---|---|---|---|---|---|---|
| 1 | Foundation lab / API | Cohere | BUILD | workflow_skill USE majority | 0.78 | No official MCP yet — clear opening |
| 2 | AI hardware / inference cloud | Cerebras | BUILD | workflow_skill USE majority | 0.82 | Official cerebras-code-mcp narrowly scoped, broader agentic-workflow open |
| 3 | OSS model hub | Hugging Face | BUILD | workflow_skill USE majority | 0.78 | `hf skills add` already publishes Claude-installable skills |
| 4 | Agent runtime / serverless GPU SDK | Modal | BUILD | tooling_assist USE majority | 0.82 | Anthropic Claude Agent SDK docs explicitly recommend Modal Sandbox |
| 5 | Workflow-automation OSS | n8n | BUILD | domain_skill **AUTHOR** majority | 0.40 | Saturated end-user lane; AUTHOR (n8n core engineers) is the right booth population |
| 6 | Cloud dev env / background coding agent | Ona (= Gitpod) | BUILD | workflow_skill USE majority | 0.78 | **Alias resolution validated** (Sep 2025 rebrand, GitHub still `gitpod-io`) |
| 7 | AI code editor | Cursor | BUILD | workflow_skill USE majority | **0.85** | Native SKILL.md system + MDC rules — Anysphere dogfoods |
| 8 | AI app builder | Lovable | BUILD | domain_skill USE majority | 0.78 | Booth-aha is *prompt-shaping*, not code-shaping |
| 9 | LLM eval / observability | Langfuse | BUILD | workflow_skill USE majority | 0.78 | Heavy first-party prior art (MCP + Docs MCP + skills repo) handled correctly |
| 10 | Voice AI / TTS | ElevenLabs | BUILD | workflow_skill USE majority | 0.82 | Both first-party MCP + skills repo; agent went up-stack |
| 11 | Speech diarization | PyannoteAI | BUILD | workflow_skill USE majority* | 0.82* | *Population misclassified — see findings |
| 12 | Vector DB | turbopuffer | BUILD | workflow_skill USE majority | 0.78 | Ships official MCP + Code Mode + tpuf router skills plugin |
| 13 | Graph DB | Neo4j | BUILD | workflow_skill USE majority | 0.78 | Aura demo workflow — devrel/SE daily routine |
| 14 | CDN / edge platform | Cloudflare | BUILD | workflow_skill USE majority | **0.85** | Agents-SDK lifecycle on Durable Objects |
| 15 | B2B auth / SSO | WorkOS | BUILD | workflow_skill USE majority | 0.80 | WorkOS *inverts* MCP question (auth-protects MCPs, isn't one) |
| 16 | Incident response / AI SRE | incident.io | BUILD | workflow_skill USE majority | 0.82 | Official remote MCP (March 2026, 34 tools) — went up-stack to workflow idioms |
| 17 | Data orchestration | Astronomer | BUILD | workflow_skill USE majority | 0.62 | `astronomer/agents` (25 skills, 359★) saturates obvious lane; agent found a gap |
| 18 | Bank / quant with OSS | Man Group | BUILD | workflow_skill USE majority | 0.78 | ArcticDB confirmed as foundational internal tool ("the foundational block of quantitative data science at Man Group") |
| 19 | Bank validated EMPTY | Baillie Gifford | SKIP | — | — | Filter prior held; no fabricated targets |
| 20 | Engineering boutique consultancy | 8th Light | BUILD | workflow_skill USE majority | 0.55 | Codifies the *manner* (TDD/pairing/apprenticeship) — distinct from MEGA Big-N |
| 21 | Industrial / heavy industry | Baker Hughes | SKIP | — | — | Internal MCP/A2A use confirmed but unreachable from booth |
| 22 | Consumer retail / marketplace | Vinted | BUILD | workflow_skill USE majority | 0.62 | OSS-as-signal: monolith decomposition, not consumer API |
| 23 | Travel / hospitality | Skyscanner | BUILD | domain_skill USE majority | 0.78 | Backpack design system dogfooded by every engineer |
| 24 | Government / public sector | Polisen | BUILD | domain_skill INTEGRATE external | 0.0126 | Public events API serves external builders; internal stack non-public |
| 25 | Legacy enterprise SaaS | IFS | BUILD | domain_skill USE majority | 0.70 | Marble + PL/SQL Cust/Ext layered customization is daily R&D + partner-ecosystem work |
| 26 | Vertical AI — legal | Legora | BUILD | domain_skill USE minority | 0.42 | Customer-side Legal Engineers; minority within firm but multiplied across 1000+ firms |
| 27 | Vertical AI — insurance | Sixfold | BUILD | workflow_skill USE majority | 0.78 | Carrier MCP serves consumers; api.sixfold.dev is the integration-engineering path |
| 28 | Web-data tooling | Bright Data | BUILD | workflow_skill USE majority | 0.65 | Heavy prior art (`brightdata/skills` + MCP); confidence intentionally tempered |
| 29 | Agentic-commerce protocol | Forter | BUILD | workflow_skill INTEGRATE external | 0.0294 | Booth visitor is external merchant evaluating TACP, not Forter platform engineer |
| 30 | Resolved-from-UNKNOWN | Iterate (= iterate.com) | BUILD | domain_skill USE majority | 0.78 | Second-pass UNKNOWN→RUN_DISCOVERY upgrade emphatically validated |

\* PyannoteAI's population was misclassified — see Finding #2.

## Findings

### 1. Skill-spec ecosystem is converging — far faster than the POC's spec assumed

Round 2 surfaced direct prior art on **at least 12 distinct skill formats / repos** across the 30-company sample. Beyond Black Forest Labs (`agentskills.io`) called out in the original validation:

| Company | Format / repo |
|---|---|
| Bright Data | `brightdata/skills` (109★, 9+ skill folders) |
| Telnyx | `team-telnyx/telnyx-toolkit` |
| Hugging Face | `hf skills add` Claude-installable skills (`transformers-to-mlx` etc.) |
| Langfuse | `langfuse/skills` (first-party) |
| Astronomer | `astronomer/agents` (25 skills, 359★, last commit today, follows skills.sh / Claude marketplace spec) |
| n8n | `czlonkowski/n8n-skills` (4.8k★) + n8n's in-monorepo `.claude/skills/n8n-conventions/SKILL.md` |
| Iterate | `.agents/skills/<name>/SKILL.md` in-tree format |
| ElevenLabs | `elevenlabs/skills` (first-party) |
| Ona (Gitpod) | `.ona/skills/SKILL.md` |
| Cursor | Native SKILL.md system + MDC-format rules |
| turbopuffer | `turbopuffer/skills` (tpuf router with 9 atomic refs) |
| 8th Light | (no skill repo, but Manifesto codification is a comparable artifact) |

Plus official MCP servers at virtually every dev-tools company (Cloudflare, GitHub, Cerebras, ElevenLabs, Granola, Linear, Monday, Postman, Stripe, Supabase, Vercel, Cursor, Cohere-borderline, etc.).

**Implication for POC:** the spec's Black-Forest-Labs prior-art callout undercounts by an order of magnitude. The POC competes with both first-party skill repos and an emerging de-facto `<vendor>/skills` convention. Default differentiation cannot be "first skill" — it must be either **gap-filler** (workflow chains the first-party repo doesn't ship), **boutique-style** (manner/conventions vs primitives), or **cross-vendor** (skills that span multiple companies' surfaces). All three of those shapes appeared in the round-2 outputs naturally — the agent skill is correctly biasing away from generic "wrap-the-API" wrappers.

### 2. Booth-aha framing produced sharp differentiation, with one population-classification slip

**Successes** — the score correctly captured:

- **Protocol-builder external population** — Forter scored 0.029 (INTEGRATE/external) because TACP integrators are external merchants, not Forter platform engineers. Mature behavior.
- **Government with non-public internal stack** — Polisen scored 0.013 because the *public* surface serves external builders while the *internal* AI/ML stack is unreachable. The agent honestly flagged: "Polisen employee at the booth wouldn't be its primary user."
- **Hidden multi-population** — Legora scored 0.42 (minority within each firm × 1000 firms) because the booth visitor is most likely a customer-side Legal Engineer, not a Legora employee.
- **AUTHOR-shape exception** — n8n scored 0.40 because AUTHOR weight (0.5) penalized the score, but the agent correctly picked AUTHOR over the saturated end-user lane: the n8n booth visitor is more likely a core engineer than a workflow author.
- **OSS-as-signal escape on non-tech sectors** — Skyscanner routed to Backpack design system (every product engineer), Vinted to monolith decomposition (every Rails+Packwerk extractor). Both consumer brands with no consumer API produced clean USE/majority targets.
- **Foundation-lab differentiation** — Cohere is a foundation lab but produced a clean BUILD; the SELF_OR_NA strategic-conflict sub-rule applies only to *runtime*-providing labs (Anthropic, OpenAI), not to competing labs whose APIs we can wrap.

**One slip — PyannoteAI** labeled cloud-API integrators as `USE/majority` when they're actually `INTEGRATE/external`. The v2 contract permits this misclassification when the agent doesn't tightly reason about "who at the *target company* uses this daily." Worth a SKILL.md tightening — explicit reasoning prompt to enumerate target-company employees vs external integrators before settling task_shape.

### 3. Internal-usage check distinguished cases OSS-as-signal alone couldn't

- **Baker Hughes vs Capital One**: both customer-only at API layer, both with substantial internal MCP/A2A. Capital One has a substantive Apache-2.0 OSS portfolio (DataProfiler, datacompy, rubicon-ml) → BUILD with high lift. Baker Hughes has zero notable OSS → SKIP, with the v2 framing correctly tagging internal MCP/A2A use as `confirmed` but unreachable from booth.
- **Man Group**: ArcticDB is `confirmed` foundational ("the foundational block of quantitative data science at Man Group" per their own tech page) — not just an OSS donation but the actual desk tooling. Maximum-strength OSS-as-signal case.

### 4. Round-2 operational notes

- **All 30 agents succeeded on first run.** Round 1's 9/12 partial-failure rate was a transient API outage; round 2 had no such failures.
- **`schema_version: 2` validated cleanly** across all 30 outputs. Validator caught zero issues; writer-script persistence worked.
- **One bug surfaced (Sixfold):** the env-var-via-pipe form `DISCOVERY_RUN_TS=… <input> | bash script.sh` silently breaks because the env var doesn't propagate through the pipeline (the env affects the source command, not the pipeline target). Created a stray auto-stamped directory. Fix: either use `DISCOVERY_RUN_TS=… bash -c '<input> | script.sh'` or the script reads `DISCOVERY_RUN_TS` from arg/file. Folding into the next iteration of `SKILL.md` Step 7.
- **Token cost (round 2):** ~30 × 90k tokens average = ~2.7M tokens. Significantly cheaper than the projected 86-company set ($220–$440) at ~$80–$170 practical.

## Filter validation summary

Combining round 1 (12 companies, 4 buckets) + round 2 (30 companies, RUN_DISCOVERY only):

| Filter bucket | Tested | Verdict pattern | False positives |
|---|---|---|---|
| MEGA_CORP | 3 (round 1) | 3 AMBIGUOUS | 0 |
| SELF_OR_NA | 4 (round 1) | 3 SKIP + 1 BUILD-strategic-drop (Anthropic) | 0 (strategic-drop is by-design) |
| UNKNOWN | 1 (round 1) + 1 resolved (Iterate, round 2) | 1 SKIP-with-candidates + 1 BUILD | 0 |
| RUN_DISCOVERY | 6 (round 1) + 30 (round 2) = 36 | 32 BUILD + 4 SKIP | n/a (this bucket has no false-positive metric — discovery decides BUILD/SKIP per-company) |

**Drop-bucket false-positive rate (combined): 12.5%** — 1 of 8 (Anthropic), and that's the strategic-conflict case the SELF_OR_NA sub-rule now documents. Net structural false positives: **0**.

**Route-bucket BUILD rate (combined): ~89%** (32 BUILD / 36 routed). The 4 SKIPs (Asparanta, Baillie Gifford, Baker Hughes, Vän Swim-from-round-1) are all defensible — thin-surface or empty-engineering cases discovery's gate caught correctly.

## Implications for the broader POC

1. **The skill-spec ecosystem is dense.** ~40% of round-2 BUILDs noted existing first-party skill or MCP prior art. The "first skill in market" differentiation framing from the original spec is almost never available; the leverage lives in workflow chains, conventions/manner, gap-fillers between primitives, or cross-vendor composition.
2. **Booth-aha framing pays off.** The score correctly distinguished company-employee-relevant targets from external-builder targets, which the popularity-driven v1 framing wouldn't have. The Forter/Polisen/n8n/Lovable/Skyscanner/Vinted cases were all materially better-targeted under v2.
3. **Internal-usage signal is the load-bearing addition** — it explained why Baker Hughes SKIPs while Capital One BUILDs, and why Anthropic should drop despite having a real surface.
4. **One contract gap to close** (population reasoning slip on PyannoteAI) — explicit prompt scaffolding in SKILL.md Step 4 could enumerate target-company employees vs external integrators before bucketing.
5. **One script bug to close** (env-var-via-pipe in `write-versioned-output.sh`).

## Sample size and caveats

42 unique discoveries total (12 round-1 + 30 round-2) covering all 4 filter buckets and 30+ industry categories. RUN_DISCOVERY validation was deliberately stratified by category (1 rep per category) rather than by random sampling — interpret aggregate metrics accordingly. The remaining ~218 RUN_DISCOVERY entries from the original 248 are not validated by discovery; they are presumed similar-to-the-tested-rep-of-their-category and would not be re-tested unless category-level findings change.
