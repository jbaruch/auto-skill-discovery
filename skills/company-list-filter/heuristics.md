# Bucket Heuristics

Reference for Step 2 of the `company-list-filter` skill. Four buckets total — two drop, one route, one flag.

## Design principle: filter on structure, not sector

The filter exists to skip discovery on companies where discovery **cannot possibly** produce a coherent target — not on companies where the agent guesses discovery would return SKIP. Sector-level priors ("banks have no surface", "consultancies have nothing public") are empirically wrong often enough that the filter must not apply them.

Validation evidence:

- Banks/insurers: 43% (6 of 14 sampled) have useful public surface. Asset managers / quant funds in particular ship notable OSS (Man Group's ArcticDB at 2.2k★, G-Research's Armada in CNCF Sandbox, Hudson River Trading's slang-server). Capital One's DataProfiler/Slingshot pattern is not exceptional. (See `validation/finance-and-consulting-2026-05-04.md`.)
- Consultancies: 42% have rich engineering output. Thoughtworks publishes the Tech Radar plus build-your-own-radar (2.5k★) and talisman (2.1k★); 8th Light, Xebia, Schuberg Philis all carry product-company-shaped public surface.
- Full-list validation across 312 companies: 12.5% MEGA_CORP, 5.8% SELF_OR_NA, 5.4% UNKNOWN, 76.3% RUN_DISCOVERY. (See `validation/full-list-2026-05-04.md`.)

Discovery's existing `verdict ∈ { BUILD, SKIP }` machinery already weighs sector evidence with real data. Letting the filter pre-empt that loses information and propagates wrong priors. Cost of routing through discovery is bounded — `SKIP` returns fast when surface is genuinely absent.

## MEGA_CORP — DROP (pending sub-product specifier)

Multi-brand or multi-practice parent with no single coherent technical surface. Discovery on the bare parent name fans out to disjoint sub-brands and the human-gate at step 3 of the discovery workflow cannot pick coherently. The fix is the caller re-inputting `parent/sub-brand`, not a filter judgement.

### Active hidden-multi-brand check

Many multi-brand parents do not read as MEGA_CORP from the name alone. Before defaulting a recognizable single-name entity into RUN_DISCOVERY, run this check:

- Does the entity have **multiple distinct GitHub orgs** with different naming patterns? (e.g., `bosch`, `bosch-thermotechnology`, `etas`, `bosch-iot`)
- Does it have **multiple separate developer-documentation portals**?
- Is the corporate name a **holding company / PE firm / aggregator** whose value lies in its portfolio, not its own engineering work? (Monterro, Digital Science, Caesar Groep, Reshift.nl)
- Has the entity recently **split, spun off, or restructured** in a way that fragments the surface across new legal entities? (Schibsted in 2025 split into Vend Marketplaces ASA + Schibsted Media; Armstrong World Industries spun off Armstrong Flooring in 2016)

If any of those signals fire, bucket as MEGA_CORP. Without this active check, validation found ~8–10 hidden mega-corps slip into RUN_DISCOVERY where discovery either fans out wastefully or arbitrarily picks one sub-brand.

### Positive signals (the obvious cases)

- Multiple separate documentation portals under the brand (`developers.X`, `cloud.X`, `ai.X`)
- Multiple distinct GitHub orgs
- Public product catalog spans unrelated verticals (search + cloud + consumer hardware + ads)

### Empirical examples

**Consumer / tech mega-corps:** Google, Microsoft, Amazon, Meta, SAP, Salesforce, IBM, NVIDIA, Yandex, LinkedIn, Apple, Oracle, Red Hat. DeepMind (= Google).

**Multi-brand finance:** Bank of America (CashPro / Merrill Lynch / Merrill Edge / Private Bank), Allianz Direct (vs Allianz parent vs azukds), Liberty Specialty Markets (under Liberty Mutual / Liberty International / GRS), NN Group (Nationale-Nederlanden / NN / ABN AMRO Verzekeringen / Movir / BeFrank / OHRA / AZL / Woonnu / NN Bank), Novo Holdings (Novo Nordisk / Novonesis).

**Big-N consultancies:** McKinsey (QuantumBlack vs Digital vs Strategy — Kedro/Vizro/CausalNex live at QuantumBlack), Deloitte (NL Engineering vs AU vs Digital UK vs PE — fragmented orgs), BCG (BCG X vs Gamma vs Platinion vs classic — FACET/ARTKIT live at BCG-X-Official), Accenture (Song / Industry X / Federal / Strategy), NTT DATA (DACH / EMEA / Launch / Innovation — fragmented regional orgs), KPMG (Audit / Advisory / Lighthouse — KaveIO is the technical sub-brand).

**Industrial / consumer-goods conglomerates:** ZEISS (SMT / Vision / Microscopy / Industrial Metrology / Medical), Robert Bosch GmbH (BSH / ETAS / Bosch Global Software / Smart Home / eBike), DHL (DPDHL Group: Express / eCommerce / Parcel / Supply Chain), Yum! Brands (KFC / Pizza Hut / Taco Bell / Habit), Bally's Interactive (Jackpotjoy / Vera&John / Virgin Games / BallyBet), CRANE (Aerospace / Process Flow / Fluid Handling), Ferrari (S.p.A. vs Trento), IKEA (Inter IKEA / Ingka Group / Ingka Digital), Springer Nature (Springer / Nature / BMC / Palgrave), Schibsted, REWE Group, Reshift.nl, Eon Digital (E.ON IT vs eon.xyz vs eon.systems — three distinct entities), Japan Tobacco, Armstrong World Industries.

**Holdings / aggregator structures:** Caesar Groep (Caesar Experts / Cloud Republic / Garansys), Digital Science (Altmetric / Dimensions / Figshare / Overleaf / ReadCube), Monterro (PE firm; portfolio companies are the surface).

### Why drop pending re-input

Input contract is `(company)`, not `(company, sub-brand)`. The mega-corp's surface is real but the parent name is the wrong query unit. The caller must specify `Google Cloud Run`, `McKinsey QuantumBlack`, `Liberty Mutual` (or a specific sub-brand), `BCG X`, `Inter IKEA Systems`, etc. Re-running with the sub-brand bypasses this bucket.

## SELF_OR_NA — DROP

Two distinct sub-rules under one bucket. Both drop, but for different reasons. Document which sub-rule fires when bucketing — future borderline cases need explicit reasoning, not implicit lumping.

### Sub-rule A: Strategic conflict (drop despite real surface)

Engineering surface exists and is structurally valid; discovery on the entity would return BUILD with viable targets. Drop anyway because building a skill creates conflict-of-interest, recursive recommendation, or self-review.

Validation evidence (`validation/round1-discovery-2026-05-04.md`): Anthropic discovery returned BUILD with three structurally valid targets (Managed Agents recipe, three-agent harness, Agent Skills standard), but every target carries near-zero baseline-lift expectation because Claude itself is the runtime executing the skill, `anthropics/skills/claude-api` already saturates the API-reference layer, and the same model would review what it shipped. The drop is correct but for strategic, not structural, reasons.

Members:

- The user's own employer (Tessl)
- Foundation labs whose model is the runtime serving generated skills (Anthropic, OpenAI; google-deepmind in foundation-lab role)
- Conference organizers whose "product" is the conference itself (`ai.engineer`)

### Sub-rule B: No engineering surface (drop because nothing to build)

**Personal / vanity domains / individuals:**

- Lower-case personal-style domains (`pichot.us`, `earendil.com`, `adjunct.ltd.uk`, `toyo-shikisai.com` — though the last is also UNKNOWN-shape)
- Single-person names (Lucas Meijer)

**Non-engineering organizations:**

- VC / PE / investment firms whose value is portfolio, not own engineering (NEA confirmed; Hetz Ventures and Novo Holdings borderline — for Novo Holdings the disjoint portfolio pushed it to MEGA_CORP instead, judgment call)
- Newsletters / podcasts / media publishers (Ben's Bites, Scaling DevTools)
- Schools / universities / educational programs (Alpha School, Dartmouth, LabXchange)
- Trade publications (DCAT Value Chain Insights)
- Non-profit professional bodies (Project Management Institute)
- Research consortia (Finnish Center for Artificial Intelligence)
- Branding / hospitality / non-tech consultancies (QUO Global)
- Apparel / consumer brands without tech surface (Vän Swim)

### Why drop (per sub-rule)

- **Sub-rule A** (strategic conflict): the surface is real but the skill we'd ship would be reviewed by, recommended through, or duplicate work that already comes from the runtime itself. Building wastes effort and risks self-referential evals.
- **Sub-rule B** (no engineering surface): nothing to build because the entity doesn't ship engineering output of its own.

Note on Sub-rule B: the line between "no engineering surface" and "thin engineering surface" can be a judgment call. When uncertain, lean RUN_DISCOVERY — discovery's SKIP verdict handles thin surfaces fast and cheap. Reserve Sub-rule B for entities where the agent is confident no engineering surface exists. Validation evidence (`validation/round1-discovery-2026-05-04.md`): Vän Swim, NEA, Ben's Bites all returned SKIP cleanly; the bucket boundary held without false positives.

## RUN_DISCOVERY — ROUTE TO DISCOVERY

Everything that isn't a structural drop. Discovery's own BUILD-vs-SKIP verdict is where surface evidence gets weighed — not here. Includes (without exhaustive enumeration):

- Single-product companies with clear public docs/SDKs/API portals
- Banks, insurers, asset managers, quant funds (excluding multi-brand parents → MEGA_CORP)
- Engineering-first consulting boutiques (Thoughtworks-shape) and other consultancies that aren't Big-N (Big-N → MEGA_CORP)
- Industrials, energy, retail, hospitality, consumer brands — discovery's domain-signal dimension catches Spotify-Backstage / Netflix-OSS / Airbnb-Airflow-shape cases
- Government, regulators, public-sector entities
- Smaller / lesser-known firms whose public surface is unknown without checking
- Borderline cases between RUN_DISCOVERY and SELF_OR_NA where some engineering surface exists

Why no example list: validation showed within-sector variance is too high to enumerate accurately. Discovery is the right place for this judgment.

## UNKNOWN — FLAG FOR MANUAL REVIEW

Use sparingly. Only when the name doesn't map to any recognizable entity AND a quick reasoning pass hasn't placed it.

Validation across 312 companies showed the bucket is doing real work — 5.4% of entries genuinely needed entity verification before bucketing.

### Sub-types observed

- **Zero web hits / probable typo:** Asparanta, LIAVELLA
- **Generic concept or marketing tagline misread as a company:** "HITL" (the Human-In-The-Loop concept), "Purpose AI at Every Scale" (Liquid AI's tagline)
- **Multiple unrelated entities sharing the same name:** Orbit (7+), TESSA, Iterate (.ai vs .com), ORYX, Bis, DOTSAFE, LDC Media, Webconsulting, rumble
- **Vanity domain pointing to thin / non-software entity:** toyo-shikisai.com (Thai pigment subsidiary)
- **Probably-not-software entity:** EXONA Laboratories Pakistan (medical lab), LIDIA (Marketplace listing only), notius.ai (empty stub)

### Procedure

The verification protocol lives in `SKILL.md` Step 2 — five search types that must all be tried before bucketing UNKNOWN. The rationale below explains *why* each step is needed:

- **Direct domain fetch** catches stealth / non-indexed brands whose only identifier is the URL on the conference list.
- **Literal name + privacy-policy scan** catches DBAs and trading-as relationships. Validation found `HITL` was bucketed UNKNOWN by an agent that did one search and gave up; the privacy-policy page at `humanintheloop-relay.com` explicitly names Chishingo Ventures Ltd. as the operator. One extra click would have resolved both list entries (the standalone `HITL` row AND the `Chishingo Ventures t/a HITL` row) as the same real company.
- **Qualified AI-context search** disambiguates multi-referent names (Orbit, Iterate, ORYX SOFTWARE, TESSA) — the AI Engineer conference attendee population is overwhelmingly the AI-flavored referent, so adding "AI" / "AI startup" / "MCP" qualifiers narrows the field.
- **Tagline / DBA expansion** handles cases where the literal string is a marketing tagline rather than a name. "Purpose AI at Every Scale" is Liquid AI's tagline — the tagline IS the signal, not an UNKNOWN.
- **Acronym expansion** handles concept-named brands (HITL → "Human In The Loop") whose literal form looks generic until expanded.

### Tagline rule

A recognizable marketing tagline or product descriptor of a known company is a *signal pointing to* that company — not an UNKNOWN. Resolve to the parent. Example: "Purpose AI at Every Scale" → Liquid AI.

### DBA / trading-as rule

When a literal contains "t/a", "trading as", "operated by", or similar markers, the DBA name and the parent are the same business. Bucket together once.

### Genuinely UNKNOWN — what the bucket should contain after the protocol

After the protocol, the bucket should contain only:

- **Probable typos with zero web evidence** — e.g., names that yield no privacy policy, no LinkedIn page, no AI-qualified hit (LIAVELLA, Asparanta).
- **Multi-referent names where no candidate has AI Engineer ecosystem signal** — e.g., generic acronyms or names where every plausible referent is AI-irrelevant (Bis, DOTSAFE, LDC Media — when no candidate ships AI/agent/MCP surface).

Anything else has been resolved by the protocol.

### Why a separate bucket from `RUN_DISCOVERY`

`UNKNOWN` is "verify the entity exists and resolves uniquely before spending discovery budget on it." Without this gate, dedup-clean strings (typos, generic concepts) silently become discovery targets despite not being real companies. With the gate, the bucket is small and the residue is genuine source-list noise.
