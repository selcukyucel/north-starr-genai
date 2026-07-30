---
name: autoimprove
description: Autonomously improve any skill or agent prompt via measure-change-test hill-climbing. Dispatches the `auto-improver` agent on a separate thread. Use when a skill gives inconsistent results, when asked to "improve/optimize/autoresearch" a skill, or when output quality needs iterative tightening.
---

# /autoimprove — Dispatch the Auto-Improver

## Purpose

Entry point for autonomous prompt optimization. Delegates the hill-climbing loop to the `auto-improver` agent on a separate thread.

Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — the same pattern applied to skill and agent prompt refinement.

## When to Use

- "Improve my [skill name] skill"
- "Optimize the [skill name] prompt"
- "Run autoresearch on [skill name]"
- "Autoimprove [skill name]"
- "My [skill name] skill gives inconsistent results"
- Any request to iteratively tighten a skill or agent's output quality

## Input

The user provides the target skill or agent name.

## Workflow

### Step 1 — Confirm Target

1. Determine which skill or agent to optimize from the user's request
2. Verify the target has a `SKILL.md` or agent file
3. If ambiguous, list matches and ask the user to pick one

**Guardrails:**
- Refuse to optimize `auto-improver` itself (infinite recursion)
- Refuse to optimize `orchestrator` directly (too coupled to pipeline state — suggest optimizing an individual transition handler instead)

### Step 2 — Gather Test Inputs & Checklist

Ask the user for test inputs (1–3 scenarios) and offer to generate the scoring checklist (3–6 yes/no questions). Get approval before starting.

### Step 3 — Dispatch the Agent

Spawn `auto-improver` via the Agent tool (`subagent_type: "north-starr-genai:auto-improver"`) on a separate thread. Pass:
- Target name + file path
- Test inputs
- Approved checklist
- Any relevant constraints (e.g., max rounds, cost budget)

The agent will:
1. Copy the target to `.plans/autoimprove-<target>/ORIGINAL.md`
2. Run baseline scoring
3. Loop: one targeted change per round, measure, keep improvements, revert regressions
4. Stop when score hits 95%+ (3x consecutive), max 15 rounds, 3 consecutive reverts, or 100%
5. Produce `IMPROVED.md`, `results.tsv`, `CHANGELOG.md`
6. Cross-consult `eval-designer` where the target is a prompt-producing component

### Step 4 — Human Checkpoints

The agent pauses every 5 rounds for a progress check. The user can continue, stop, or adjust the checklist. If the user says "autopilot", the agent skips future checkpoints.

### Step 5 — Present Results

Read the agent's output files and surface a concise summary:

```
Autoimprove Complete: <target>
────────────────────────────────
Score:   <baseline>% → <final>% (<+delta>%)
Rounds:  <total> (<kept> kept, <reverted> reverted)

Files:
  .plans/autoimprove-<target>/ORIGINAL.md  (backup)
  .plans/autoimprove-<target>/IMPROVED.md  (proposed new version)
  .plans/autoimprove-<target>/results.tsv  (per-round log)
  .plans/autoimprove-<target>/CHANGELOG.md (insights + recommendations)

To adopt: cp .plans/autoimprove-<target>/IMPROVED.md <target file path>
```

### Step 6 — Offer `/learn` Integration

After presenting results:

```
The changelog captures <N> insights about what works for this target. Want to run /learn
to capture these as pattern rules for future skills?
```

## Notes

- This skill is a thin dispatcher — the loop lives in the `auto-improver` agent
- Optimizes **prompts**, not code. For code quality, use `/analyze-code`
- The original target file is never modified — user explicitly adopts the improved version
- The changelog is the most valuable artifact — it persists across sessions and captures what works/doesn't for this specific target
- The agent runs on a separate thread to keep main conversation context clean
- Typical runs take 10–15 rounds; each round runs the target against all test inputs, so total time is proportional to (rounds × inputs × target runtime)
