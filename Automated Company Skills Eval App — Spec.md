# Spec for an automated company skills eval app

## Goal

Input a company name (and, in personalized modes, a short set of clarifying answers). The app automatically:

* finds public APIs, docs, repos, or existing skills
* generates eval scenarios based on how an agent would use the targeted surface
* creates a skill
* tests agent performance with and without the skill
* reports improvement of agent usage and follow-ups of how the skill could be improved further

The same pipeline supports four operating modes (see below). Mode selection determines (a) which surface discovery targets and (b) whether a clarifying-questions step gates the run.

## Operating modes (2x2)

Two independent axes:

* **Target surface — Produce vs Consume.** *Produce*-mode targets the company's external/public surface (APIs, SDKs, integrations they ship to customers). *Consume*-mode targets the surface the company's own engineers touch daily (internal dogfood, vendor stacks they consume, conventions they follow).
* **Personalization — Off vs On.** *Off* runs purely from the company name. *On* adds 3–5 booth-floor clarifying answers (role, team, daily-work focus) that narrow the target.

|  | Personalization OFF | Personalization ON |
|---|---|---|
| **Produce** | **A1** — public-API skill from company name alone | **A2** — public-API skill narrowed by clarifying answers |
| **Consume** | **B1** — dogfood/internal skill from company name alone | **B2** — dogfood/internal skill narrowed by clarifying answers |

### A1 — Produce / Personalization OFF

Targets the company's external API/SDK surface from the company name alone.

**Pros**
* Fastest end-to-end — no booth interaction required, runs pre-conference on an attendee list (where one exists) or in real time off a typed name at the booth
* No async wait, no return-visit dependency, no email-delivery glue required to demonstrate value
* Uniform contract per company — discovery's input is just a name
* Lowest engineering risk — public docs/SDKs are the best-documented surface to mine; least operational machinery to build out
* Demo-ready on the spot: rep already has the visitor's skill open when they walk up

**Cons**
* Weak attendee relevance — most engineers at a company don't use their own external API in daily work
* Large or multi-product companies (Google, NVIDIA, AWS) produce a generic-feeling target — "your company's API" rather than "your daily work"
* Best-fit visitors are the minority sub-populations who DO consume their own external API: sales engineers, partner integrators, DX/DevRel

### A2 — Produce / Personalization ON

Same target surface as A1, narrowed by clarifying answers (which product line, which API family).

**Pros**
* Sharper than A1 for multi-product companies — Stripe Connect vs Issuing vs Payments distinguishable
* Universe of options is small (the company's own product catalog), so clarifying questions converge quickly
* Useful for sales engineers / partner integrators who legitimately work against the company's external API

**Cons**
* Requires booth touch (~1–2 min) — can't run pre-conference
* Inherits A1's underlying mismatch — internal engineers usually still aren't the audience for their own external API
* Adds async wait + return-visit-or-email glue on top of A1's complexity, for a sharpening that mostly matters in multi-product cases

### B1 — Consume / Personalization OFF

Targets internal/dogfood surfaces from public signals (employee blog posts, hiring JDs, open-source projects the company stewards, public references to internal tooling).

**Pros**
* Hits the booth-aha frame — *"you use this every day"* lands harder than *"your company sells this API"*
* Can run pre-conference if the attendee list is known
* Validated on 70+ companies (round 4: 27/30 BUILD with documented evidence) on the AI Engineer conference list

**Cons**
* Discovery is harder — dogfood surfaces aren't always public; SKIP rate is non-trivial for companies with weak public signal
* Ambiguous for large multi-team companies (Google research vs Cloud vs Workspace consume very different stacks)
* Without clarifying answers, the agent must guess which sub-population a visitor belongs to — false-positive rate is real

### B2 — Consume / Personalization ON

Same surface as B1 with booth-floor clarifying answers narrowing the sub-population.

**Pros**
* Sharpest targeting of all four cells — visitor disambiguates platform vs product vs DevRel team
* Highest relatability — *"you, on your platform team at Tailscale, write HuJSON daily; here's a skill for it"*
* Validated end-to-end on the consume side; honest SKIP/AMBIGUOUS handling per the discovery output contract

**Cons**
* Requires booth touch + 1–4 hour async pipeline + optional return visit or trust-based email delivery — most operationally complex of the four
* Most components still to build (clarifying-questions skill, booth-rep UI, async pipeline glue, email-delivery glue)
* Most exposure to no-show risk between booth touch 1 and touch 2 (mitigated by same-day email)

### Separately: Snyk skills-vulnerability scan

The team's parallel booth CTA — *"scan your skills for vulnerabilities"* via Tessl/Snyk integration on a visitor's existing skill repo — is a different product surface (scan-and-report on existing artefacts vs generate-new-skill-from-research) and is not part of this app's 2x2. It's tracked separately.

## The hard problem

**Source discovery is the load-bearing step.** Everything downstream — scenarios, skill, evals, report — is only as good as the sources we found. The challenge is non-trivial because:

* Companies vary wildly: some have rich public APIs + SDKs + GH orgs, others have only marketing sites, others sit behind login walls
* "Authoritative" is fuzzy: official docs > SDK source > examples > third-party tutorials, but ranking breaks down when official docs are stale or the SDK lives in a community fork
* Conflict resolution: when sources disagree (deprecated docs vs current SDK), which wins?
* Skip criterion: when there isn't enough public surface to build a useful skill, the app should detect this early and bail out rather than generate a skill grounded in nothing
* **Mode-specific source sets**: produce-mode mines public API/SDK surfaces (well-documented, low-variance); consume-mode mines employee blogs, hiring JDs, OSS stewardship, internal-tooling references (sparser, higher-variance)

This step gets the most design attention; the rest of the pipeline is plumbing by comparison.

The output contract for discovery is specified separately in [`discovery-output-contract.md`](./discovery-output-contract.md).

## Input

* Company name/site/GH (always)
* Operating mode (A1 / A2 / B1 / B2)
* Clarifying answers (only in A2 / B2)

## Output

* Local file artifacts (no Tessl publish for MVP — we don't yet know if results are useful)
* Versioned results per run: each invocation writes to a timestamped directory so we can diff runs against the same company and see what the agent did differently to get better/worse results — this is how we'll perfect the process
* Final report showing:
  * Research found: docs, APIs, repos, existing skills
  * Per-scenario **lift** (with-skill score minus baseline score) plus aggregate lift — not just absolute attainment
  * Example improvements / recommendations to improve the skill
  * Links to
    * the generated skill (local path)
    * eval scenarios / results (local path)

## Workflow

The 10-step pipeline is mode-shared except where noted:

1. **Discover sources** *(mode-specific source set)*
    Produce-mode (A1/A2): official docs, API references, SDKs, public GH repos, existing public skills. Consume-mode (B1/B2): employee blogs, hiring JDs, OSS stewardship, public references to internal tooling.
2. **Extract structure**
    Pull out capabilities, workflows, examples, constraints, and terminology.
3. **Select skill target** *(human-in-the-loop)*
    Discovery produces multiple candidate targets ranked by confidence (see contract). Surface the top suggestions to a human; they pick one. This is the only manual step in the pipeline. Single point of control rather than letting the system silently pick a target it might be wrong about.
4. **Generate evals**
    Create realistic developer scenarios for the *selected* target. Mix of positive cases (correct behavior) and at least one negative case (refuse bad input / produce silence when nothing actionable).
5. **Audit evals for bleeding & leaking**
    Before running, check that no criterion value appears verbatim in its task description (bleeding) and no fixture reuses a skill example (also bleeding). Reject scenarios that fail the audit and regenerate. Without this gate, lift numbers are junk.
6. **Generate skill**
    Create a first-pass skill for the selected target.
7. **Quality gate the skill**
    Run `tessl skill review --threshold 85`. Below threshold blocks the run — regenerate or escalate. Skills that fail review never reach evals.
8. **Run evals** (baseline + with-skill)
9. **Analyze gaps**
    Identify failure modes and propose improvements to the skill. Flag scenarios with near-zero lift — they signal coincidence-with-baseline, leaked technique, or universal-competence criteria, not skill value.
10. **Generate report**
    Summarize sources, selected target (with rationale), scenarios, baseline vs skill results (per-scenario lift + aggregate), and next improvements.

*Personalized modes (A2, B2)* additionally run a `clarifying-questions` skill before step 1 — its output feeds discovery as a narrowing filter.

## MVP — Produce / Personalization OFF (cell A1)

Picked because it's the fastest path to a demoable artefact, the lowest engineering risk, and the simplest operationally (no booth interaction, no async wait, no email-delivery glue required to demonstrate value). It also unblocks the AI Security Summit by Snyk deadline by running pre-conference on whatever attendee list is available — or in real time off a company name typed at the booth.

* Single company input — name / site / GH only
* Crawl public docs / repos for the company's external API/SDK surface
* Surface top-3 candidate skill targets; human picks one
* Generate 5 scenarios for the picked target (≥1 negative)
* Generate 1 skill that passes review ≥85
* Run evals (baseline + with-skill)
* Output markdown report to a versioned local directory
* **Deferred:** A2 / B1 / B2 modes, batch support for ~30 companies (revisit once single-company runs prove useful), booth-rep UI, email-delivery glue, clarifying-questions skill

## Success criteria

* Automated from company name with a single human gate (target selection); everything else runs unattended
* Repeatable across many companies
* Clear before/after value shown as **per-scenario lift** (not just aggregate attainment)
* Useful improvement suggestions for the skill
* Re-running on the same company produces a new versioned result, leaving prior runs intact for diffing
