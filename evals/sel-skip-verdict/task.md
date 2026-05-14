# Run Target Selection on a SKIP-Verdict Discovery

## Problem/Feature Description

A discovery.json is at `inputs/discovery.json`. Run the target selection step on it.

## Output Specification

If the discovery has a selectable verdict, present candidates and persist a selection.json once the human picks.

If the discovery cannot yield a selection, surface the situation to the user and finish — no selection.json should be written for a discovery with no candidates.
