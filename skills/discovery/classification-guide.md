# Consumer-side vs Builder-side Classification — Reference

Reference material for [SKILL.md](SKILL.md) Step 4. Read once per run when classifying a candidate surface.

## The core distinction

For every candidate surface, ask: **does the target company's daily-employee population CONSUME this surface, or BUILD it?**

### Consumer-side surfaces

The company's employees use the surface the same way external customers would. `USE/majority` targets pointing at this surface ARE credible.

Examples:

- Cursor IDE (Anysphere engineers code in Cursor)
- Linear app (Linear engineers track issues in Linear)
- Spotify Backstage (every Spotify engineer browses the catalog daily)
- Internal monorepo conventions / internal design system (every engineer follows them)
- WorkOS dogfooding AuthKit on the WorkOS dashboard
- Man Group ArcticDB (quants run notebook research against it daily)

### Builder-side surfaces

The company *ships* this surface for outside consumers. Their relationship is "we build it," not "we use it as customers do."

Examples:

- Cohere v2 Chat API (employees implement it; consumers are external)
- Cerebras Inference API (Cerebras runs the cloud; customers send tokens)
- turbopuffer query API (TP tunes the index; customers tune queries)
- PyannoteAI Cloud API (PyannoteAI trains models; customers integrate)
- Modal SDK from a customer's perspective (Modal builds Modal; customers use the SDK)
- Astronomer's managed Airflow (the *cited* DAG-choreography pain belongs to customers like GetYourGuide)
- Bright Data's primitives (BD builds the pipes; customers route requests)
- Sixfold's underwriting API (Sixfold ships it; carrier integration engineers consume it)

`USE/majority` targets pointing at a builder-side surface are WRONG. Three legitimate moves instead, in priority order — exhaust each before falling to the next.

## Move 1 — Hunt aggressively for a consumer-side surface inside the company

"Builder-side at the public API" does NOT mean "no consumer-side surface exists." Internal surfaces are often described publicly. Run **all** of these searches before concluding none exists:

- Engineering blog: search for `"we use internally"`, `"our internal"`, `"how we built"`, `"dogfood"`, `"we run on our own"` — many companies blog explicitly about internal tooling
- Public conference talks: search YouTube / company channel for the last 24 months — engineers describing their own daily workflows is common
- Hiring / job posts: senior eng listings often describe day-in-the-life and name internal tools
- "X-on-X" patterns: companies notably build their own product with their own product (Modal-on-Modal, Vercel-on-Vercel, GitHub-on-GitHub, Spotify-on-Backstage) — this is a *consumer-side* signal even when the product is also sold externally
- Engineering handbook / dev onboarding docs that leaked public (GitLab handbook, PostHog handbook)
- OSS projects the company itself consumes (pyannote.audio at PyannoteAI, ArcticDB at Man Group, Backstage at Spotify) — OSS-as-signal still applies if the company *consumes* the OSS, not just authors it
- Podcast / interview appearances by named engineers describing their workflow
- Internal eval / test harnesses publicly documented (model eval pipelines, perf benchmarking suites)

**The skip_reason must enumerate which of these searches were attempted and what each returned.** Generic phrasing like "internal tooling is non-public" is insufficient and indicates lazy search.

## Move 2 — AUTHOR-shape target on the same surface

"How to author a new endpoint in our API following our conventions." Population is `small_team` (the API team only). Score will be lower (AUTHOR weight is 0.5). Use this when Move 1 finds nothing AND there's a real authoring pattern an agent could codify.

## Move 3 — INTEGRATE/external target explicitly marked external

For the company's customers, not its employees. Booth-aha score will be low (`external` × `INTEGRATE` weights ≈ 0.06). Acknowledge this honestly rather than relabeling.

## Honest-SKIP rule

After exhaustive consumer-side search, if Move 1's full search list has been run and documented in `skip_reason`, AND no candidate clears the BUILD floor of raw `confidence ≥ 0.5` in any task_shape, fall to verdict `SKIP`. The `skip_reason` MUST list the specific consumer-side searches attempted (with what was searched and what came back) — not just a generic "non-public internal engineering" claim. A SKIP without a documented search trail is a process error and should be reworked.

Inflating an INTEGRATE/external candidate to USE/majority to clear the BUILD threshold is also a process error. Both shortcuts (lazy-SKIP without search and over-inflate-to-BUILD) violate the contract.

## Concrete traps

- **Spotify** — "Backstage scaffolder action authoring" looks like a USE/majority target but is actually AUTHOR/small_team (booth visitor is overwhelmingly *not* on the platform team). The right target is `task_shape: USE` for the catalog/scaffolder/tech-docs daily workflow with `size_class: majority`.
- **PyannoteAI** — "voice-AI pipeline using their cloud API" looks like USE because integrators heavily use the API, but those integrators are *external builders*, not PyannoteAI employees. Correct shape: `INTEGRATE` / `external`.
- **Forter** — TACP integration target is an external-merchant task; Forter platform engineers wrote the protocol but don't integrate against it. Correct shape: `INTEGRATE` / `external`.

## Booth-aha ranking formula

```
score = confidence × iu_weight × pop_weight × ts_weight
```

Weights:

- `iu_weight` (from `internal_usage` level): confirmed=1.0, inferred=0.7, weak=0.3, none=0.1
- `pop_weight` (from `target_population.size_class`): majority=1.0, minority=0.6, small_team=0.4, external=0.2
- `ts_weight` (from `task_shape`): USE=1.0, AUTHOR=0.5, INTEGRATE=0.3

Score is advisory ranking only — BUILD verdict still requires raw `confidence ≥ 0.5` on at least one target. The score signals to the human-gate whether the booth-aha audience is broad (majority/USE) or narrow (small_team/AUTHOR or external/INTEGRATE).
