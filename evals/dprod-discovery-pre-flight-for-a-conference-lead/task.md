# Discovery Pre-flight for a Conference Lead

## Problem/Feature Description

A sales team attending an industry summit collected "Alphabet" as a lead to run through the discovery pipeline. Before the pipeline spends time crawling docs and building skill targets, the team wants to know whether the input is ready to process as-is or needs refinement.

Run produce-mode discovery for the company name "Alphabet" and produce the discovery JSON. If the input is ready to process, proceed through the full discovery workflow. If something about the input needs to be resolved before a meaningful discovery can be produced, output the appropriate response so the caller knows what to do next.

## Output Specification

Write a file named `discovery.json` containing the produce-mode discovery result. The JSON should reflect whatever stage of the workflow is appropriate given what you find about "Alphabet" as a company input.
