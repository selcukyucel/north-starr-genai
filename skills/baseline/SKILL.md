---
name: baseline
description: Capture a reproducible AI performance baseline before changes. Dispatches the `baseline-capturer` agent on a separate thread. Use before any change to a client-facing AI output. Triggered automatically by the Q3 gate in CLAUDE.md.
---

# /baseline — Dispatch the Baseline Capturer

## Purpose

Entry point for AI performance baselining. Delegates measurement to the `baseline-capturer` agent on a separate thread.

Run this **before** making changes. The complexity gate in `CLAUDE.md` triggers this automatically when Q3 = Yes (client-facing output change).

## Input

The user provides the name or description of the AI component to baseline.

## Workflow

### Step 1 — Check for Existing Baseline

Glob `.plans/BASELINE-*.md` for a baseline matching the component. If one exists, ask:

```
A baseline for <component> from <date> exists at .plans/BASELINE-<name>.md.
  1. Refresh (overwrite with a new measurement + trend comparison)
  2. Keep existing — proceed with changes against the current baseline
  3. Cancel
```

### Step 2 — Dispatch the Agent

Spawn `baseline-capturer` via the Agent tool (`subagent_type: "north-starr-genai:baseline-capturer"`) on a separate thread. Pass the component name plus any known context (eval suite path, test inputs, pricing source).

The agent will:
1. Read the codebase + any existing eval suite or test fixtures
2. Measure accuracy (via eval suite, golden files, or manual 5–10 input scoring)
3. Measure latency (p50/p95/p99 from 20+ inputs)
4. Measure token usage, cost, error rate, format compliance
5. Snapshot the full configuration (model, params, prompt, RAG, guardrails, dependencies)
6. Write `.plans/BASELINE-<name>.md` with reproduction steps
7. Cross-consult `eval-designer`, `cost-estimator`, and `ai-ops` where relevant

### Step 3 — Present Results

Read `.plans/BASELINE-<name>.md` and surface a concise summary:

```
Baseline captured: .plans/BASELINE-<name>.md

Component: <name>
Measured by: <method>
Sample size: <N>

Key metrics:
- Accuracy: <score>
- Latency p95: <ms>
- Cost/request: $<N>
- Error rate: <N>%

Regression thresholds set. Ready to proceed with changes.
```

If a prior baseline existed and the user chose "Refresh", include the trend comparison table.

## Notes

- This skill is a thin dispatcher — measurement lives in the `baseline-capturer` agent
- The baseline file is consumed by `eval-designer` and by `/prompt-test` for change comparison
- Accuracy is best measured against an eval suite — if none exists, the agent recommends `/eval-suite`
- The agent runs on a separate thread to keep main conversation context clean
- Reproduction steps must be exact commands — the baseline is worthless if the next person can't re-run the measurement
