---
name: company-list-filter
description: 'Triage a raw list of company names (conference attendees, prospect lists, sales lists) before running the discovery pipeline. Classifies each company into seven buckets and returns a focused candidate list of companies whose discovery is likely to yield a usable skill target. Use whenever the user provides a list of more than a handful of company names and needs to decide which deserve discovery effort. Trigger phrases — "filter this list", "triage these companies", "pre-discovery filter", "narrow the conference list".'
---

# Company List Filter

Process steps in order. Do not skip ahead.

This skill is the pre-discovery triage gate. Discovery is expensive per company; this filter is cheap per list. Drop the obviously-out, surface the obviously-in, flag the ambiguous — then hand the survivors to discovery.

## Step 1 — Normalize and Deduplicate the Input List

Run `skills/company-list-filter/scripts/dedup.sh` against the raw input. The script accepts a file path as its first argument or reads from stdin, and writes a JSON object to stdout:

```
{"unique": ["Linear", "Stripe", ...], "count_in": 412, "count_out": 247}
```

Contract: case-insensitive deduplication; whitespace trimmed; first-seen casing wins; exits non-zero with a stderr message on failure.

Use the `unique` array as the working list for Step 2. Report the count delta to the user (`count_in → count_out`) before continuing — heavily duplicated lists are common and the user benefits from seeing the dedup yield. Proceed immediately to Step 2.

## Step 2 — Classify Each Unique Company

For each name in the deduplicated list, assign exactly one bucket from the four defined in [heuristics.md](heuristics.md):

- `MEGA_CORP` — multi-brand parent with no coherent single surface (drop pending sub-brand specifier)
- `SELF_OR_NA` — not an engineering organization: own employer, foundation lab, conference, personal domain, VC, podcast, school, branding agency, non-tech consumer brand, etc. (drop)
- `RUN_DISCOVERY` — everything else (route to discovery; discovery decides BUILD vs SKIP using real evidence)
- `UNKNOWN` — name does not map to a recognizable entity; possible typo, marketing tagline, generic concept, or ambiguous between multiple unrelated referents (flag for manual review)

The filter excludes only **structural** impossibilities (mega-brand ambiguity, non-engineering entities). Sector heuristics are forbidden here — validation showed banks split 43% rich / 14% moderate / 29% mega / 29% empty, and consultancies split 25% rich / 17% moderate / 42% mega / 17% sparse / 0% empty (see `validation/finance-and-consulting-2026-05-04.md`). Within-sector variance is too high for sector-level rules; discovery's BUILD-vs-SKIP verdict is where sector evidence gets weighed.

### Hidden multi-brand check (required before defaulting to RUN_DISCOVERY)

Many MEGA_CORP entities don't read as multi-brand from the name alone (IKEA's Inter IKEA / Ingka split, Caesar Groep's portfolio of sub-brands, Reshift.nl's media holdings, Monterro's PE structure, recent restructurings like Schibsted's 2025 split). Before defaulting a recognizable single-name entity into RUN_DISCOVERY, apply the active check from `heuristics.md` — distinct GitHub orgs, separate docs portals, holding-company structure, recent corporate restructuring. A single targeted web search per ambiguous case is justified; do not search for entities that are unambiguously single-product (Linear, Stripe, Vercel).

### Procedure

Apply heuristics from prior knowledge first. Reserve web searches for two cases: (a) the hidden-multi-brand check above, and (b) the UNKNOWN verification protocol below. Do not search the web for unambiguously single-product names — that wastes tokens.

### UNKNOWN verification protocol (mandatory before bucketing)

When a name doesn't resolve from prior knowledge, run **all** of the following before concluding `UNKNOWN`. Failing to search and defaulting to `UNKNOWN` is a process error — validation showed agents giving up on disambiguation rather than spending one extra Google search per name.

1. **Direct domain fetch** — if the literal contains a TLD (`.ai`, `.com`, etc.), fetch it.
2. **Literal name search + privacy-policy scan** — Google `"<name>"`, then check the first 5 results, especially any **privacy policy** page. Privacy policies are the highest-signal source: they almost always name the operating company explicitly (e.g., "HITL is operated by Chishingo Ventures Ltd.").
3. **Qualified AI-context search** — `"<name>" AI` or `"<name>" AI startup` to surface the AI-relevant referent in multi-referent cases.
4. **Tagline / DBA / trading-as expansion** — if the literal looks like a marketing tagline ("Purpose AI at Every Scale" → Liquid AI) or a "trading-as" fragment ("Chishingo Ventures t/a HITL" → HITL is a DBA, not a separate entity), search the spelled-out tagline or the operator phrase.
5. **Acronym expansion** — if the name is an acronym (HITL → "Human In The Loop"), search the spelled-out form + AI context.

Only bucket `UNKNOWN` after all five searches fail. Document evidence of the searches in the row's notes if any are non-trivial.

**Tagline rule:** when a literal string is a recognizable marketing tagline or product descriptor of a known company, that string is a *signal pointing to* the company — not an UNKNOWN. Resolve to the parent company.

**DBA / trading-as rule:** when a literal contains "t/a", "trading as", "operated by", or similar markers, the surface entity (DBA name) and the parent (legal entity) are the same business; bucket together once, not twice.

If the resulting `UNKNOWN` count exceeds 10% of the deduplicated list, run a second protocol pass. Otherwise leave the residue for the caller to decide.

Proceed immediately to Step 3.

## Step 3 — Emit the Bucketed Report

Output a single markdown report with these sections, in order:

1. `## Drop — MEGA_CORP (needs sub-brand specifier)` — comma-separated list of names. No per-company rationale; the bucket name is the rationale. Note in the section header that the caller can re-submit with `parent/sub-brand` to bypass the drop.
2. `## Drop — SELF_OR_NA` — same shape.
3. `## Route to discovery — RUN_DISCOVERY` — one per line, alphabetized. No per-company rationale; discovery decides BUILD vs SKIP.
4. `## Flag for manual review — UNKNOWN` — one per line.

End with a single summary line: `Filtered N → R routed to discovery, U unknown; dropped X mega + Y self/NA.` where N is `count_out` from Step 1 and the other letters are the bucket counts.

Finish here.
