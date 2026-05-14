# Validation: Finance + Consulting Sectors — 2026-05-04

Empirical validation of public engineering surface for 26 firms drawn from the AI Engineer conference attendee list. Goal: test whether sector-level filter rules ("drop banks", "drop consultancies") are supported by evidence, before the `company-list-filter` skill encodes them.

## Banks / Insurers / Asset Managers (14 firms)

| Company | Docs/API | GitHub org | Eng blog | Notable OSS | Multi-product | Surface verdict |
|---|---|---|---|---|---|---|
| Bank of America | developer.bankofamerica.com (CashPro Developer Studio, 350+ payment types, 100+ APIs) | github.com/bankofamerica — empty/private | None public; press releases only | — | Y (CashPro / Merrill Lynch / Merrill Edge / Private Bank) | MEGA |
| Allianz Direct | — (parent has Open Insurance Platform) | github.com/allianz-direct (~6 forks); parent github.com/allianz (~9, ng-aquila notable) | globaldigitalfactory.allianz.com/blog (parent) | ng-aquila Angular UI lib (parent) | Y (Direct vs parent vs azukds vs allianz-de) | MEGA |
| Aioi Nissay Dowa | — | None found | None | — | N | EMPTY |
| Absa Group | — | github.com/AbsaOSS (144 repos); github.com/absa-group (2) | absaoss.github.io (early stub) | ABRiS (Avro SerDe Spark), k3d-action, spark-data-standardization, living-doc-generator | N | RICH |
| Liberty Specialty Markets | Shares developer.libertymutual.com (parent only) | Shares github.com/libertymutual (53 repos) | Liberty Mutual "Tomorrow Talks" (parent) | External Secrets Operator (co-maintained), BMO | Y (LSM / Liberty International / GRS under Liberty Mutual) | MEGA |
| Monzo | github.com/monzo/docs (public API docs) | github.com/monzo — 176 repos; typhon ~2.3k, egress-operator ~700 | monzo.com/blog — active (Mar 2026) | typhon (Go HTTP), egress-operator, aws-nitro-util | N | RICH |
| BIT Capital | — | None (Berlin firm; bitcapital-hq is unrelated) | None | — | N | EMPTY |
| Baillie Gifford | — | None public | None (careers content only) | — | N | EMPTY |
| Hudson River Trading | — | github.com/hudson-trading (~7 repos) | hudsonrivertrading.com/hrtbeat — active | slang-server (SystemVerilog LSP), heracles-ql (~26), pymetabind | N | MODERATE |
| G-Research | — | github.com/G-Research (~50+ repos) | gresearch.com/news + g-research.github.io | ParquetSharp (~590), Armada (CNCF Sandbox, ~1k+), spark-extension, FastTrackML, Consul.NET; ILGPU community (~1.7k) | N | RICH |
| Man Group | — | github.com/man-group | man.com news + arcticdb.io/blogs | ArcticDB (~2.2k), Notebooker (~900), dtale, PyBloqs | N | RICH |
| DNB | developer.dnb.no (Open Banking) | github.com/DNBbank (~5); github.com/dnb-asa (~3) | None (portal-adjacent only) | — (small samples only) | N | MODERATE |
| NN Group | developer.nn-group.com (API Store) | None public found | nn-careers.com tech content (career-marketing) | — | Y (Nationale-Nederlanden / NN / ABN AMRO Verzekeringen / Movir / BeFrank / OHRA / AZL / Woonnu / NN Bank) | MEGA |
| PFA | — | None | None | — | N | EMPTY |

**Distribution:** 4 RICH (29%), 2 MODERATE (14%), 4 MEGA (29%), 4 EMPTY (29%).

**Pattern:** sector-mixed, not sector-uniform. Asset managers / quant funds are the strongest cluster (Man Group ArcticDB 2.2k★, G-Research Armada+ParquetSharp, HRT slang-server) — the cleanest Capital-One-shape examples in the sample. Insurance is the weakest. Multi-brand parents (BoA, Allianz, Liberty, NN) are MEGA — same input-shape problem as Google.

## Consulting / Services Firms (12 firms)

| Firm | Docs/API | GitHub org | Eng blog | Notable OSS | Tech publications | Multi-practice | Surface verdict |
|---|---|---|---|---|---|---|---|
| McKinsey (QuantumBlack) | — | mckinsey ~7 repos; Vizro 3.7k, CausalNex 2.5k. Kedro lives at kedro-org (LF) | QuantumBlack Medium, active | Kedro (10k+), Vizro (3.7k), CausalNex (2.5k) | QuantumBlack publications, McKinsey Digital insights | Y (QuantumBlack vs Digital vs Strategy) | MEGA |
| Deloitte | — | deloitte ~5 + DeloitteAU + DeloitteDigitalUK + DeloittePE — fragmented; top repo `beacon` 8★ | deloitte-engineering.github.io (NL); latest 2025-12 | — (none ≥100★ originated) | Deloitte Insights (business, not technical) | Y (NL Eng / AU / Digital / PE) | MEGA |
| BCG (BCG X) | — | BCG-X-Official ~10 repos; FACET 532, ARTKIT 167 | sparse; posts on bcg.com | FACET (532), ARTKIT (167) | BCG Henderson Institute, BCG X publications | Y (X / Gamma / Platinion / classic) | MEGA |
| Accenture | — | Accenture 221 repos; AmpliGraph 2.2k, RIG 602 | accenture.github.io/blog; latest 2022-10 (stale) | AmpliGraph (2.2k), RIG (602) | Accenture Research, Tech Vision | Y (Song / Industry X / Federal / Strategy) | MEGA |
| Capgemini | — | capgemini 132 repos; dcx-react-library 118 | capgemini.github.io; latest 2026-04 | dcx-react-library (118) | TechnoVision, World Reports | Y (Sogeti / Engineering / Invent) | MODERATE |
| Thoughtworks | — | thoughtworks 69 repos; build-your-own-radar 2.5k, talisman 2.1k | thoughtworks.com/insights, active | build-your-own-radar (2.5k), talisman (2.1k), Gauge, Mingle | **Tech Radar** (flagship), books (Fowler et al.) | N | RICH |
| KPMG | — | KPMG-UK (private members) + KaveIO 18 repos; PhiK 171 | KaveIO blog; KPMG-UK Medium referenced | PhiK (171) | KPMG insights (business-led) | Y (Audit / Advisory / Lighthouse) | SPARSE |
| NTT DATA | — | Fragmented: NTTDATA-DACH 16, launchbynttdata, nttdata-oss; top viewnode 20★ | nttdata-dach.github.io; latest 2025-07 | — | regional whitepapers | Y (DACH / EMEA / Launch / Innovation) | MEGA |
| Oliver Wyman | — | no central org; tech.labs.oliverwyman.com/open-source | tech.labs.oliverwyman.com/blog, active | FrameLog, Vellere (small) | OW Forum (business) | N | SPARSE |
| 8th Light | — | 8thlight 94 repos; Hyperion 118, ex_state 113 | 8thlight.com/insights; latest 2026-04 | Hyperion (118), ex_state (113) | Software Craftsmanship Manifesto co-authoring; books | N | RICH |
| Xebia | — | xebia 163 + xebia-functional (xef, fetch, arrow contributors) + xebialabs | xebia.com/blog, active | Arrow-kt contributors, xef, fetch (Scala) — multiple ≥100★ | Xebia Essentials cards, books | Y (Functional / Cloud / Microsoft / Data) | RICH |
| Schuberg Philis | — | schubergphilis 358 repos; chef-acme 110, mcvs-* suite | schubergphilis.com/news, active | chef-acme (110), MCVS suite | engineering articles, conference talks | N | MODERATE |

**Distribution:** 3 RICH (25%), 2 MODERATE (17%), 5 MEGA (42%), 2 SPARSE (17%), 0 EMPTY.

**Pattern:** three shapes — engineering-first boutiques (Thoughtworks, 8th Light, Xebia, Schuberg Philis) behave like product companies; Big-N multi-practice firms (McKinsey, Deloitte, BCG, Accenture, NTT DATA) have rich surfaces inside specific sub-brands (QuantumBlack/Kedro+Vizro, BCG X/FACET, Accenture/AmpliGraph, KPMG/KaveIO) but the parent name is the wrong query unit; strategy houses (Oliver Wyman, classic McKinsey strategy) are sparse-to-empty. Consultancies basically never EMPTY (sample 0 of 12).

## Cross-sector findings

1. **Sector-level drop is empirically wrong.** Banks: 43% have useful surface (RICH+MODERATE). Consultancies: 42% have useful surface excluding MEGAs, plus MEGAs themselves carry surface at the sub-brand level. Both correction targets the user called out (Capital One = bank, Thoughtworks = consultancy) confirmed: Man Group's ArcticDB and Thoughtworks' Tech Radar are the canonical examples.
2. **MEGA is the dominant non-trivial bucket.** 29% of banks and 42% of consultancies are multi-brand. Same input-shape problem as Google — discovery on the parent name fans out to disjoint sub-brands. The fix is the same: require sub-brand specifier or route to a dedicated MEGA bucket pending caller clarification.
3. **`PRODUCT_COMPANY` vs `NEEDS_DISCOVERY` split is not data-supported.** Both end up at discovery; discovery's BUILD/SKIP machinery handles fine-grained classification with real evidence. The split was filter-time prioritization disguised as routing — drop the split, keep one routing bucket.
4. **EMPTY exists but discovery's SKIP verdict handles it fast.** 4 of 14 banks were genuinely empty. No filter rule needed — discovery returns SKIP cheaply when surface is absent.

## Implication for filter

Reduce to four buckets:

- `MEGA_CORP` — multi-brand parent (consumer mega-corps, multi-brand banks, Big-N consultancies). Drop pending sub-brand specifier.
- `SELF_OR_NA` — own employer, foundation labs, conference organizers, personal domains. Drop.
- `RUN_DISCOVERY` — everything else. Discovery decides BUILD/SKIP with evidence.
- `UNKNOWN` — entity unrecognized. Verify before discovery.

Sample size: 26 of 312 unique companies. Other sectors (industrials, consumer brands, hospitality, smaller AI startups) not yet validated; revisit if filter behavior on those sectors looks suspicious.
