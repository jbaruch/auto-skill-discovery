# Generate the Snyk Users Batch Report

## Problem Description

Your teammate ran the full A1 batch pipeline overnight for a list of Snyk conference leads. The per-company discovery, selection, and evaluation steps all completed successfully and the results are stored in `runs/2026-05-12T-snyk-users/`. Unfortunately, the final summary step was skipped — they closed their terminal before it finished — so there is no consolidated report yet.

The sales team needs the summary for their morning standup. They want to know the verdict breakdown, which companies are worth following up on, and the aggregate lift numbers for the companies that were evaluated. The pipeline scripts are available at `skills/batch-driver/scripts/`.

## Output Specification

1. Generate the batch summary report for `runs/2026-05-12T-snyk-users/`.
2. Write `summary-log.txt` documenting the command you ran and the output it produced.
3. Report the absolute path of the generated summary file in `summary-log.txt`.
