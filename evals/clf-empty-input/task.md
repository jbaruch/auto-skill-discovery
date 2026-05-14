# Pre-Discovery Triage on an Exported Attendee List

## Problem/Feature Description

Your team is preparing for a developer summit and a coworker exported the attendee list from the conference registration system into `inputs/companies.txt`. They were in a hurry and want you to run the standard pre-discovery triage so the discovery pipeline can pick up the survivors first thing tomorrow.

## Output Specification

If the export yields a usable list of unique companies, produce `triage-report.md` with the four-section classification and `dedup-output.json` containing the deduplication output.

If the export is unusable, write `triage-skipped.md` documenting what you read, what the deduplication step returned, and what the coworker should do to re-export the file.
