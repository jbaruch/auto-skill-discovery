# Run Build-and-Evaluate on a Skipped Selection

## Problem/Feature Description

A selection.json is at `inputs/selection.json` and the linked discovery.json is at `inputs/discovery.json`. Run the build-and-evaluate pipeline.

## Output Specification

If the selection is actionable (selection_status=selected), run the full phases 4–10 pipeline.

If the selection cannot drive a build, surface the rationale to the user and finish without producing skill scaffolding, scenarios, or eval runs.
