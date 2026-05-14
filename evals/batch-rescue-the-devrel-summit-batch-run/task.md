# Rescue the DevRel Summit Batch Run

## Problem Description

The nightly batch run for DevRel Summit leads started but encountered problems partway through. Some companies returned errors during the discovery phase — a few have incomplete or corrupted result files, and one company's directory is missing entirely. The sales operations team needs the final report first thing in the morning and cannot wait for a full re-run.

Your job is to take the batch to completion. The run directory is at `runs/2026-05-14T-devrel-summit-batch/`, and the batch manifest at `runs/2026-05-14T-devrel-summit-batch/batch-manifest.json` lists all five companies. The pipeline scripts are at `skills/batch-driver/scripts/`. Use the existing data where it is available.

## Output Specification

1. Process all companies listed in the batch manifest, using available discovery data where it exists.
2. Write `completion-log.txt` documenting: what you found for each company, what actions you took, and how you handled any data problems.
3. Generate the final batch summary report for the run.
4. Ensure the summary includes all five companies (with appropriate error indicators for any that had problems).
5. Report the absolute path of the generated summary file in `completion-log.txt`.
