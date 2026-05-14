# Run the Build-and-Evaluate Pipeline for Vertibrate Industries

## Problem/Feature Description

The ML platform team has selection results queued at `inputs/selection.json` (with the linked discovery at `inputs/discovery.json`) and asked you to run the standard build-and-evaluate pipeline. The selection step ran earlier and the reviewer captured their rationale in the selection file.

Run the pipeline against this selection. Persist a `run-log.md` documenting which steps you executed, what was produced, and the final state. The team uses this log to audit pipeline runs without scrubbing through CLI history.

## Output Specification

Produce `run-log.md` in the working directory. The log should make clear what was run (or what was skipped, and why) and the disposition of every artifact the pipeline would normally produce.
