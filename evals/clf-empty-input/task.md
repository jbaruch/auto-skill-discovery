# Triage an Empty Conference Roster

## Problem/Feature Description

A coworker handed you a conference attendee list at `inputs/companies.txt` and asked you to run pre-discovery triage on it. Produce a triage report.

## Output Specification

If the input file yields a non-empty list of unique companies, produce `triage-report.md` with the standard four-section classification.

If the input yields zero unique companies, do not fabricate a report. Communicate the situation to the user — name the file you read, the row count it produced, and what the user should do next — without writing a triage-report.md at all.
