# Auto-Skill-Potential Discovery — Stakeholder Brief

*One pipeline, four operating modes. The MVP picks one cell to ship for the Snyk summit. 2026-05-13.*

## TL;DR

One pipeline, **four operating modes** on a 2x2 of (target surface × personalization):

|  | Personalization OFF | Personalization ON |
|---|---|---|
| **Produce** (company's public API/SDK) | **A1** — pre-built skill from name alone | **A2** — pre-built skill narrowed by clarifying answers |
| **Consume** (engineers' daily tools) | **B1** — dogfood-skill from name alone | **B2** — dogfood-skill narrowed by clarifying answers |

**We're shipping A1 as the MVP for AI Security Summit by Snyk on Thursday** — fastest path, lowest operational complexity, no booth interaction required, runs pre-conference on whatever attendee list lands (or real-time at the booth from a typed name). The other three cells layer in after, depending on what we learn from A1 in the wild.

Validation to date is on the **consume side (B1/B2)**: 70+ companies from a real conference attendee list, four rounds, round 4 produced 27/30 defensible BUILDs with documented evidence. Produce-side (A1/A2) is unvalidated; the Snyk run is the first datapoint.

Per-company token cost on Opus 4.7 lands in **~$13–$28 across all four modes** — token spend is roughly mode-independent; the modes differ on *operational* complexity, not on cost. For a 200–500-engagement booth, total token spend is ~$3k–$14k regardless of mode chosen. Trivial against booth cost.

Separately: Melanie's Snyk-integrated skills-vulnerability-scan CTA (scan visitor's existing skill repo, surface a security report) is a different product surface — not part of this 2x2; tracked separately.

---

## The four modes — pros and cons

### A1 — Produce / Personalization OFF *(MVP)*

Discovery scrapes the company's public API/SDK/docs from the name alone; pipeline generates a skill for the visitor's company's external surface.

**Pros**
- Fastest end-to-end — no booth interaction, no async wait, no return-visit dependency
- Lowest operational complexity — no clarifying-questions skill, no booth-rep UI, no email-delivery glue required to demonstrate value
- Runs pre-conference on an attendee list (where one exists) or real-time at the booth from a typed name
- Lowest engineering risk — public docs are the best-documented surface to mine
- Demo-on-the-spot: visitor walks up, rep already has their company's skill open

**Cons**
- Weak attendee relevance — most engineers at a company don't use their own external API
- Multi-product companies (AWS, Google, NVIDIA) produce generic-feeling targets
- Best-fit audience is the minority who DO consume their own external API: sales engineers, partner integrators, DX/DevRel

### A2 — Produce / Personalization ON

A1 + 3–5 clarifying questions at the booth narrowing which product line / API family.

**Pros**
- Sharper than A1 for multi-product companies — distinguishes Stripe Connect vs Issuing vs Payments
- Universe of options is small (the company's own catalog) so clarifying converges quickly
- Useful for sales engineers / partner integrators who legitimately work against external APIs

**Cons**
- Requires booth touch (~1–2 min) — can't run pre-conference
- Inherits A1's mismatch: internal engineers still aren't the audience for their own external API
- Async wait + return visit + email-delivery glue all required on top — clarifying overhead pays off only when the company has a wide product catalog

### B1 — Consume / Personalization OFF

Discovery hunts dogfood/internal surfaces from public signals (employee blogs, hiring JDs, OSS stewardship). Skill targets the daily-work tools, not the public API.

**Pros**
- Hits the booth-aha frame — *"you use this every day"* lands harder than *"your company sells this API"*
- Can run pre-conference if attendee list is known
- Validated on 70+ companies — round 4 produced 27/30 BUILD with documented evidence (see Section 2)

**Cons**
- Discovery is harder — dogfood surfaces aren't always public; SKIP rate is real
- Ambiguous for large multi-team companies (Google research vs Cloud vs Workspace consume very different stacks)
- Without clarifying answers, the agent must guess which sub-population a visitor belongs to

### B2 — Consume / Personalization ON

B1 + clarifying questions narrowing the sub-population (platform vs product vs DevRel).

**Pros**
- Sharpest targeting of all four cells — visitor self-disambiguates which team they're on
- Highest relatability — *"you, on your platform team at Tailscale, write HuJSON daily; here's a skill"*
- Validated end-to-end on the consume side; honest SKIP/AMBIGUOUS handling

**Cons**
- Requires booth touch + 1–4 hour async + return-visit-or-email delivery — most operationally complex
- Most components still to build (clarifying-questions skill, booth-rep UI, async pipeline glue, email-delivery glue)
- Most exposure to no-show risk between booth touch 1 and touch 2 (mitigated by same-day email)

---

## What events sees (operational view by mode)

| Mode | Pre-conference | At booth | Async pipeline | Follow-up |
|---|---|---|---|---|
| **A1** | Pipeline runs on every name on the attendee list (where available). | Rep greets visitor by badge, opens their pre-built skill on a laptop. | — | Email shipped same-day with skill + report. |
| **A2** | — | Rep greets, asks 3–5 clarifying questions, captures email. | 1–4 hour async. | Return visit (optional) or email shipped same-day. |
| **B1** | Pipeline runs on every name on the attendee list (where available). | Rep greets visitor by badge, opens their pre-built skill on a laptop. | — | Email shipped same-day with skill + report. |
| **B2** | — | Rep greets, asks 3–5 clarifying questions, captures email. | 1–4 hour async. | Return visit (optional) or email shipped same-day. |

A1/B1 are pre-built; A2/B2 are async-per-visitor. Personalization is what costs the wait time.

---

## 1. The idea is valid — here's why

The reasoning differs by axis. Both axes have real merit; what makes A1 the MVP is operational simplicity, not relevance superiority.

### Produce-axis (A1/A2)

A visitor's company makes something; a rep can show how Tessl improves agent use of that thing. The pitch rings true for the subset of the visitor's company who works against the external API — sales engineers, partner integrators, DX. Not relatable for the bulk of internal engineers, but it's a foot in the door, the operational cost is low, and we can run it on every name on the list (skipping where appropriate at the booth). It's also the path that demos *something* even when the company has no public dogfood signal — the public API surface is almost always documented.

### Consume-axis (B1/B2)

A booth-floor demo is a fundamentally different sales motion than emailed content. It works only if **the demo rings true to the visitor's daily work in the first 30 seconds**. The booth-aha frame is what makes that possible: the skill targets something the visitor *did this week*, not what their company's marketing page advertises. Each of these is a *different surface* than the public marketing one — and consume-mode discovery surfaces them unattended, fed only the company name (B1) plus a few clarifying answers (B2):

- **Spotify engineers** don't integrate against Spotify's Web API. They live in Backstage, scaffolder templates, TechDocs. Public Web API is for outside builders.
- **Cursor engineers** at Anysphere code in Cursor, author `.cursor/rules/*.mdc` + `AGENTS.md` + `mcp.json`. The marketplace is for users; the workflow IS their daily life.
- **Plaid engineers** triage issues via Plaid's internal MCP server (per their July 2025 blog: 80%+ adoption among Plaid engineers). The external Plaid Link API serves fintech customers, not Plaid employees.
- **Tailscale engineers** write HuJSON tailnet policy daily; `setec`, `golink`, `tclip`, `tsidp` are their internal `tsnet` services on their own tailnet. The mesh-VPN service is for customers.
- **Sentry engineers** consume Seer triage + Codecov coverage + AI Code Review predictions internally. `getsentry/skills` README literally reads *"Agent skills for Sentry employees."*

None of those come from popularity heuristics; they come from the booth-aha frame asking: *which surface does this company's own engineers touch in their daily work?* The clarifying-questions skill (B2) makes the targeting *sharper still* — the visitor disambiguates which sub-population they belong to (platform team vs product team vs DevRel), which the agent would otherwise have to guess.

### Honesty about scope (both axes)

Both axes have honest SKIPs. Produce-side: a company with no public API at all (consultancies, financial firms, individual people) lands SKIP cleanly. Consume-side: a pension fund with no public engineering surface (Baillie Gifford, PFA) gets SKIP. An ambiguous mega-corp (Google, NVIDIA — 8 sub-brands) gets AMBIGUOUS, prompting the rep to ask "which org?" before drilling in. The pipeline being honest about its limits is what makes the BUILDs trustworthy at the booth.

### Three strategic findings from the validation work *(consume-side only — B1/B2)*

1. **The agentic-skill-format ecosystem is converging fast.** ≥12 companies on the conference list ship their own `*/skills/` repos following an `agentskills.io`-shaped spec (BFL, Bright Data, Telnyx, HF, Langfuse, Astronomer, n8n, Iterate, ElevenLabs, Ona, Cursor, turbopuffer, Sentry, Trigger.dev, Arize, Comet, Sixfold). "First skill in market" rarely applies; consume-mode leverage is workflow chains, conventions/manner, gap-fillers between primitives, or cross-vendor composition the company's own skills repo doesn't ship.
2. **Hiring posts are the highest-signal source for finding internal consumer-side surfaces.** Senior eng JDs explicitly describe daily-life workflows and name internal tools. Sixfold's "Software Engineer, AI" listing reads verbatim: *"write, test, and deploy code across Sixfold's AI pipeline using Python… fine-tune prompts, design evaluation metrics."* That IS the booth visitor's job description.
3. **Sector priors don't work; structural priors do.** Banks split 43% rich / 14% moderate / 29% mega / 29% empty. Drop only structural impossibilities (multi-brand parents requiring sub-brand specifier, non-engineering entities); discovery's per-company gate handles the rest with real evidence. Capital One was the founding case study; round 4 confirmed at Genentech (pharma), G-Research (quant), Vinted (consumer retail), Skyscanner (travel).

A1/A2 (produce side) have no validation data yet — that's part of the MVP run.

---

## 2. The data proves it — consume-side (B1/B2) only, so far

We've run the consume-side pipeline on **70+ unique companies from one real conference attendee list** (AI Engineer conference, 312 deduplicated). Four rounds of validation, each closing a discovered failure mode:

| Round | Tested | What we found |
|---|---|---|
| 1 | 12 stratified across all 4 filter buckets | Filter routing correct; SELF_OR_NA needed sub-rule split between structural-absence and strategic-conflict (Anthropic case) |
| 2 | 30 stratified across 30 categories | ~25% of BUILDs were USE/majority mislabels on builder-side surfaces (Cohere v2 API, Modal SDK, ElevenLabs Cloud) — the **API/SDK-provider trap**. Closed via Sub-step 4a (consumer-side vs builder-side classification) |
| 3 | 9 cases the user pushed back on as suspiciously many SKIPs | First fix over-corrected to SKIP without searching — *lazy SKIP*. Closed via documented-search-trail requirement. Re-ran the 9: 8 flipped to defensible BUILDs (e.g., Cohere is publicly named in EleutherAI's `lm-evaluation-harness` README as an internal user) |
| 4 | **30 fresh companies, no overlap with prior rounds** | **27 BUILD (90%) / 2 SKIP / 1 AMBIGUOUS** — every verdict defensible with documented evidence. **Zero failure modes from prior rounds recurred.** |

**Round-4 sample of actual top targets — verbatim from the discovery JSONs, not curated.** Each one is a candidate B1/B2 demo for a visitor from that company:

| Booth visitor from… | Top demo target (verbatim from discovery) | Score | Smoking-gun evidence |
|---|---|---|---|
| Tailscale | *HuJSON tailnet policy authoring with idiomatic Tailscale conventions* | 0.85 | Tailscale-on-Tailscale: every employee writes HuJSON daily |
| Prefect | *FastMCP server authoring lifecycle (Components/Providers/Transforms, Horizon deploy)* | 0.85 | PrefectHQ stewards FastMCP — 25k★, ~70% of all MCP servers |
| Thoughtworks | *Author a Tech Radar blip and validate the BYOR CSV/JSON schema* | 0.85 | BYOR (2.5k★) targets the Thoughtworker's own workstation |
| Sentry | *Sentry-on-Sentry investigative loop (Seer + Codecov + AI Code Review)* | 0.80 | `getsentry/skills` README: *"Agent skills for Sentry employees"* |
| Genentech | *Clinical-trial TLG authoring with insightsengineering tern + teal + rtables* | 0.80 | F. Hoffmann-La Roche AG copyright on R packages used by every Roche statistician |
| Modal | *Modal-on-Modal authoring skill* | 0.78 | *"Dogfooding Modal: 30 employees, 13 teams, internal hackathon"* |
| Plaid | *Internal-MCP triage workflow (pick from 20+ tools, fix-or-escalate)* | 0.70 | 2025-07-29 Plaid blog: internal MCP adopted by 80%+ of Plaid engineers |
| G-Research | *Submit and monitor an Armada batch research job from a quant notebook* | 0.78 | Armada/FastTrackML/ParquetSharp — internal infra → CNCF; *"millions of batch jobs daily for quants"* |
| Sixfold | *AI-pipeline authoring & eval-metric loop* | 0.62 | Their own "Software Engineer, AI" JD describes the daily IC workflow verbatim |
| Cursor | *Cursor extensibility authoring (SKILL.md + .cursor/rules + AGENTS.md + mcp.json)* | 0.85 | Anysphere ships `cursor-team-kit` — internal team workflows as a public plugin |

**Honest narrow cases also matter** — they prove the agent isn't gaming the score to make demos look better than they are. Pomerium scored 0.033 (correctly narrow AUTHOR/small_team — booth visitor is one of ~10 Pomerium engineers, not the customer base). Informatica scored 0.091 (same shape). Honest SKIPs (PFA, Lucas Meijer, Baillie Gifford) all carry full search trails enumerating which probes were attempted and what each returned. **The booth rep can trust the score**: high-score = strong demo, narrow-score = niche skill, SKIP = "don't run a demo, just talk."

Capital One regression-tested cleanly against a hand-crafted reference example — discovery converged on the same two flagship targets (DataProfiler+datacompy, Slingshot SDK) the human-curated version surfaced.

**A1/A2 (produce side) have no validation data yet.** The MVP run on the Snyk attendee list is the first datapoint — and one of the explicit goals of that run is to find out whether produce-side discovery on a fresh attendee list lands a similar BUILD rate, or whether it surfaces failure modes the consume-side rounds didn't anticipate.

---

## 3. The cost is bounded — and roughly mode-independent

Per-company on Opus 4.7 with prompt caching, end-to-end pipeline:

| Stage | Applies to | Cost |
|---|---|---|
| Clarifying conversation (booth touch 1) | A2, B2 only | $1–$2 |
| Discovery (mode-specific source set) | all four | $3–$6 |
| Skill gen + `tessl skill review` + eval scenarios + eval runs + report | all four | $10–$20 |
| **A1 / B1 total** (no clarifying) | | **~$13–$26** |
| **A2 / B2 total** (with clarifying) | | **~$14–$28** |

For a typical 200–500-engagement booth: **~$3k–$14k total token spend regardless of mode**. Trivial against booth cost (sponsorship + travel + booth staff + marketing prep).

The four modes differ on **operational** complexity, not on token spend. A1 isn't materially cheaper than B2 to *run*; it's cheaper to *build* and *operate* — no booth-rep UI, no clarifying-questions skill, no async pipeline glue, no email-delivery wiring. That's the real reason it's the MVP, not token economics.

**Critical: there's no sunk cost on no-shows.** In A1/B1 the pipeline runs ahead of time on whoever's on the list; in A2/B2 it runs on every captured lead and ships artefacts via email same-day, whether the visitor returns or not. Email delivery is the floor; live demo on the spot (A1/B1) or on return (A2/B2) is the ceiling. Every dollar produces a deliverable.

Build-vs-not-build becomes a sales question (does close-rate lift on a personalised same-day artefact clear $13–$28 per lead?), not an engineering-cost question.

---

## What's left to build

Discovery + structure extraction + human-gated target selection are **built and validated for the consume side**; the same infrastructure needs a produce-mode source set for A1/A2.

| Component | Modes | Notes |
|---|---|---|
| Produce-mode discovery source set | A1, A2 | Extends existing discovery with public-API-surface extraction (docs site crawl, OpenAPI/SDK introspection, GH-org enumeration). Reuses output contract. **MVP scope.** |
| Phases 4–10 (skill gen + eval gen + eval run + report) | all 4 | One skill composing existing Tessl tooling: `tessl__eval-authoring` covers steps 4–5; `tessl skill review --threshold 85` is the step-7 gate; scoring infra runs step 8. Mode-shared. **MVP scope.** |
| Attendee-list batch driver | A1, B1 | Loop the per-company pipeline across a CSV/list. Needed for the Snyk run. **MVP scope.** |
| Clarifying-questions skill | A2, B2 | Drives 3–5 structured follow-ups based on the company name. Captures answers as discovery input. Deferred. |
| Booth-rep UI (form + pipeline trigger + artefact viewer) | A2, B2 | Simple web app. Not needed for A1 (pre-built). Deferred. |
| Email-delivery glue (plugin packaging + send mechanism) | A2, B2 | Templated email + tessl plugin attachment. Deferred. |

**Path to AI Security Summit by Snyk (Thursday)**: A1 only — produce-mode discovery + phases 4–10 + batch driver. Token budget for the attendee list (assuming ~100 leads): **~$1.3k–$2.6k**.

The blocker is no longer engineering effort. It's whether to commit to the booth-floor sales motion as a real channel — and the Snyk MVP is the cheapest possible test of that commitment.

---

*Artifacts: spec at `SPEC.md`; output contract at `discovery-output-contract.md`; built skills at `skills/{company-list-filter,discovery,select-target}/`; validation reports at `validation/`; per-company evidence at `runs/<UTC-timestamp>/<slug>/discovery.json`.*
