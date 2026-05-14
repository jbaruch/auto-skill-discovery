# Discovery Assessment for a Management Consultancy

## Problem/Feature Description

A pipeline operator wants to evaluate whether McKinsey & Company is a viable target for an agent skill aimed at external developers consuming McKinsey's public APIs or SDKs. The operator suspects the answer might be negative but needs a rigorous, documented assessment rather than a guess — specifically, evidence of which discovery probes were attempted and what each one returned, so the decision can be audited later.

Run produce-mode discovery on "McKinsey & Company" and produce a discovery JSON that reflects what you find. The output should be honest about the access reality — if surfaces are gated, say so. If probes returned nothing, document exactly which probes were tried and what they returned. The goal is a trustworthy record of the search, not a superficially optimistic result.

## Output Specification

Write a file named `discovery.json` containing the produce-mode discovery result for McKinsey & Company. Whatever verdict the evidence supports, the JSON should include a thorough record of the discovery process and its findings.
