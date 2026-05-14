# Target Selection for StreamlineHQ

## Problem/Feature Description

The discovery pipeline has completed a run for StreamlineHQ, a developer workflow automation company. The output is available at `inputs/discovery.json`. Your task is to run the full target selection workflow on this discovery output.

As part of this workflow, produce a ranked candidates file so the team can see the prioritized options. The engineering lead has reviewed the ranked list and confirmed they want to move forward with target `tgt_02` (the webhook integration offering).

Complete the full target selection workflow through to writing and validating the selection artifact.

## Output Specification

- `candidates-report.md` — a markdown file containing the ranked candidate table produced in Step 3 of the workflow (the presentation to the human decision-maker)
- the persisted selection artifact for the chosen target
- The validator script output should be visible in your working notes or terminal output
