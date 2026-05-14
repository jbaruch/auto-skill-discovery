# Run the A1 Batch Driver on the Attendee List

## Problem/Feature Description

Run the batch-driver skill on `inputs/attendees.csv`.

## Output Specification

If the CSV yields at least one usable company, run the per-company pipeline and write a per-batch index.

If the CSV yields zero usable rows, surface the situation to the user and do not write a runs/<DISCOVERY_RUN_TS>/ directory or any batch-manifest.json.
