# Target Selection for OrbitLabs

## Problem/Feature Description

The discovery pipeline has been run multiple times for OrbitLabs, an observability infrastructure company. Historical run outputs are stored under `inputs/runs/` in timestamp-named directories. A product team wants to move through the human-gated selection step using the most up-to-date discovery data available.

Run the target selection workflow for the company slug `orbitlabs`. Use the inputs directory as the working root when searching for discovery runs. Produce a ranked candidates file showing what options were presented to the decision-maker.

After reviewing the candidates, the product team has decided that none of the available targets are the right fit for the next quarter — they are passing on all of them due to competing roadmap priorities. Record a skip decision with the reason: "Roadmap conflict — all targets deprioritized for Q1 planning cycle."

Complete the full target selection workflow through to persisting and validating the skip decision.

## Output Specification

- `candidates-report.md` — a markdown file showing the ranked candidates that were presented (the table from Step 3 of the workflow)
- The selection artifact should be written to the same directory as the chosen discovery file
- The validator script output should be visible in your working notes or a log file
