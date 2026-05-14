# Pipeline Queue: Selection Validation and Context Loading

## Problem Description

Your skill-discovery platform maintains a queue of companies to process. Today's queue has two entries:

1. **Company slug: `acme-corp`** — The platform stores run history under `inputs/runs/<UTC-timestamp>/acme-corp/`. Multiple runs may exist; you need the right one.

2. **Explicit path: `inputs/beta-inc/selection.json`** — A pre-identified selection file for Beta Inc.

Before the pipeline can scaffold and evaluate a skill for any company, it must validate whether the selection is ready to proceed. If a company is not ready, the pipeline should stop gracefully for that entry and explain why. If it is ready, the pipeline should load all necessary context and determine what the first build command would be.

Write a `run-log.md` documenting what happened for each company:
- Whether the pipeline proceeded or stopped, and why
- For any company that proceeds: what mode it will use, and what the first scaffold command (`tessl skill new`) would look like with the correct `--path` argument
- Any decisions or context loaded (company name, mode, selected target title)

## Output Specification

Produce `run-log.md` with a section for each company in the queue. For companies where processing proceeds, include the full `tessl skill new` command with all required flags filled in from the discovered context.
