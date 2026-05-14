# Pre-Discovery Prioritization for an Industry Summit

## Problem/Feature Description

Your company is attending a European tech summit and has assembled a list of 16 companies from the sponsor and speaker roster. Before investing discovery pipeline time on each one, you need a fast triage pass that separates the obviously-useful leads from the structural dead-ends.

A key challenge with this list is that several of the names look like coherent single companies but may actually be multi-brand holding structures where a sub-brand specifier would be required before discovery can produce a coherent result. At the same time, the list also includes financial-sector and consulting-sector companies that your discovery pipeline handles fine — you don't want to inadvertently drop those just because of their sector.

Produce a triage report for this list. The raw names are at `inputs/companies.txt`.

## Output Specification

Produce two files:

1. `triage-report.md` — the classification report in four sections.

2. `dedup-output.json` — the raw JSON output from the deduplication step.
