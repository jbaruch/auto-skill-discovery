# Skill Pipeline Onboarding Script

## Problem Description

The ML platform team at your company has a new engineer joining next week. She will be responsible for running the automated skill-build-and-evaluate pipeline for new company targets. The pipeline takes a pre-selected target (stored in a `selection.json` file) and runs it through scaffold generation, scenario creation, quality review, eval execution, and report generation — all orchestrated via the `tessl` CLI and a set of helper Python scripts.

To help her get up to speed quickly, her tech lead wants a single, executable shell script called `pipeline.sh` that encodes every step of the pipeline in the right order. The script should be self-contained: given a `selection.json` path as its first argument, it should run the full pipeline without any additional human input. It must handle the case where the target has already been scaffolded in a previous run (the scaffold directory already exists), and it must include logic for what to do if the quality review gate is not met or if the eval run encounters an error.

The company's standard is:
- 5 eval scenarios per target
- A quality review threshold that gate-keeps the eval step
- Baseline and with-skill eval variants run in a single invocation
- Lift computation and report generation always follow the eval

The selection context is in `inputs/selection.json` and its linked discovery data is in `inputs/discovery.json`. Write `pipeline.sh` using those as the concrete example paths.

## Output Specification

Produce a single file: `pipeline.sh`

The script should:
- Accept the path to a `selection.json` as its first argument (default to `inputs/selection.json` if not provided)
- Run every step of the pipeline in sequence with appropriate CLI flags
- Include brief inline comments marking each phase
- Handle errors from the eval step before proceeding to compute lift
- Derive and use `run_dir` (the directory of the selection file) as the base path for all artifacts
