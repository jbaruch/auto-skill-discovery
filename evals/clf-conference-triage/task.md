# Conference Lead Triage

## Problem/Feature Description

Your team is preparing for the AI Engineer World's Fair and has collected a raw list of companies from the conference registration data. The list was assembled by three different people across two days, so it contains some duplicates (same company with different casing or spacing) and entries from organizations that clearly aren't relevant targets for developer tooling (a university, a newsletter, a VC firm).

Before passing the list to the discovery pipeline — which is expensive to run per company — you need to produce a clean triage report. The report must categorize each organization into one of four groups: companies that are multi-brand holding structures (which need a sub-brand specifier before discovery can run), companies that are not engineering organizations (personal domains, schools, media, investors), companies that should be routed to discovery, and names that couldn't be resolved without more information.

The raw attendee list is at `inputs/companies.txt`. It contains one company name per line with some duplicates.

## Output Specification

Produce a single markdown file named `triage-report.md` containing your classification results. Do not include your working notes or intermediate outputs in this file — just the final triage report.

Also write `dedup-output.json` containing the raw output from the deduplication step (the structured JSON with `unique`, `count_in`, and `count_out` fields).
