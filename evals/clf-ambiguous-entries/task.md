# Attendee List Triage with Ambiguous Entries

## Problem/Feature Description

A sales team scraped a developer conference badge list and exported it into a text file. The list has 14 entries, but many are problematic: some appear to be marketing taglines rather than company names, some use "trading as" / "t/a" notation for legal entities, some are acronyms whose meaning isn't immediately clear, and a few may simply be typos with no identifiable referent.

The team needs a triage report to decide which entries are worth running through the discovery pipeline. For any entries that were ambiguous and required research to resolve, include a brief resolution note explaining what you found so the team can audit your reasoning. Entries that remain truly unresolvable after thorough research should be flagged for manual review.

The raw list is at `inputs/companies.txt`.

## Output Specification

Produce two files:

1. `triage-report.md` — the classification report with all four sections. For any entry that was ambiguous and required research to resolve, include a parenthetical resolution note on the same line (e.g., `- Liquid AI  *(resolved from tagline "Purpose AI at Every Scale")*`).

2. `dedup-output.json` — the raw JSON from the deduplication step (`unique`, `count_in`, `count_out`).
