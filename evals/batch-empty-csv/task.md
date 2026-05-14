# Run the A1 Batch Driver on the Conference Attendee Export

## Problem/Feature Description

The marketing ops team is gearing up for a developer conference and exported the registration list into `inputs/attendees.csv`. They want a full A1 batch run completed before tomorrow morning so the booth reps can pull per-company artifacts as visitors arrive.

Run the batch-driver skill against `inputs/attendees.csv`. Document the command you ran and its outcome in `summary-log.txt` for the team's morning standup.

## Output Specification

1. `summary-log.txt` documenting the command(s) run, the parse summary, and the disposition of the batch.
2. If the input is processable, the canonical batch artifacts under `runs/<DISCOVERY_RUN_TS>/`.
