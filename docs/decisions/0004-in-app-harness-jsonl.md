# 0004 · In-app benchmark harness exporting JSONL

- **Status:** accepted
- **Date:** 2026-11-09
- **Deciders:** Hassaan Khalid
- **Affects:** apps, benchmark-spec, analysis

## Context
Options for measurement: (a) the official LiteRT `benchmark_model` tool, which bypasses the app layer
and so can't measure Flutter overhead; (b) external profilers (Perfetto, Android Studio), which are
accurate but manual and hard to automate across hundreds of runs; (c) an in-app harness with
timers around each stage.

## Decision
Each app contains an identical headless harness (see `benchmark-spec/harness-contract.md`)
that runs the configured workload and writes one JSON record per iteration (JSON Lines) to
app storage. Records conform to `benchmark-spec/result-schema.json`. Perfetto traces are
captured for a few configs only, to validate harness timings (triangulation).

## Consequences
- Fully automatable, schema-validated, analysable with one pipeline.
- Timer placement must be identical across platforms. This is the main parity risk, so it gets a review checklist.
- `benchmark_model` results are reported as a "runtime floor" reference line in figures.
