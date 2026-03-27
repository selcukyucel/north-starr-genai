---
name: orchestrate
description: Start the AI story orchestration pipeline. Feeds stories from a story map into the orchestrator agent, which routes them through TRIAGE → DESIGN → PLAN → BUILD → HARDEN → DELIVER with feedback loops, conflict detection, and human escalation.
argument-hint: <story map path or story IDs to run>
---

# Orchestrate — Start the AI Pipeline

## Purpose

Bridge between story decomposition and story execution. After `/decompose` produces a backlog of stories, this skill starts the orchestration pipeline — routing stories through specialized agents in the correct order, managing dependencies, detecting conflicts, and enforcing quality gates.

Without this skill, stories sit in `.plans/STORIES-AI-*.md` as a static document. With it, they flow through: chief-ai-po (refine) → ai-architect → layoutplan → specialists → validators → demo-builder, with the orchestrator managing state, feedback loops, and human escalation at every step.

## When to Use

- After `/decompose` generates a story map
- When you have multiple stories to execute through the full pipeline
- When you want automated conflict detection across stories (budget, architecture, resources)
- When you need dual human-in-the-loop (operator + client) coordination

For a **single task** without a story map, use the complexity gate in CLAUDE.md instead — it routes directly to `/ai-invert` → `layoutplan`.

## Input

The user provides one of:
- A path to a story map (`.plans/STORIES-AI-<name>.md` or `.plans/STORIES-<name>.md`)
- Specific story IDs to run (e.g., "S1.1, S1.2, S2.1")
- "all" to run all stories in the most recent story map
- "next" to run the next unblocked story in priority order

## Workflow

### Step 1: Load the Story Map

**Actions:**
1. If a path is provided, read the story map file
2. If no path, find the most recent `STORIES-AI-*.md` or `STORIES-*.md` in `.plans/`
3. If neither exists, inform the user: "No story map found. Run `/decompose` first to create one."
4. Parse the stories: IDs, titles, priorities, dependencies, sizes, invert candidates

### Step 2: Check Pipeline State

**Actions:**
1. Check if `.plans/PIPELINE-STATUS.md` exists — if so, resume from current state
2. Check `.plans/DECISIONS.md` for prior architectural decisions
3. Check `.plans/LEARNINGS.md` for accumulated team learnings
4. Check for any in-progress stories (`.plans/REFINED-*.md`, `.plans/ADR-*.md`, `.plans/PLAN-*.md`)

If resuming an existing pipeline:
```
Pipeline Status: ACTIVE
─────────────────────────
Active stories:    [count] (list with current phases)
Blocked stories:   [count] (list with blockers)
Completed stories: [count]
Queued stories:    [count]

Resume from current state? (y / restart from scratch)
```

### Step 3: Select Stories to Run

**Actions:**
1. If specific story IDs were provided, validate they exist in the story map
2. If "all" was specified, select all stories
3. If "next" was specified, find the highest-priority unblocked story
4. If no specification, present the selection:

```
Stories available for orchestration:
────────────────────────────────────

Ready to start (no unresolved dependencies):
  • S1.1 — <title> [MUST] [size: M] [invert candidate]
  • S2.1 — <title> [MUST] [size: S]
  • SA.1 — Confidence & Hallucination [MUST] [size: M]

Blocked (dependencies not met):
  • S1.2 — <title> [depends on: S1.1]
  • S1.3 — <title> [depends on: S1.1, S1.2]

Options:
  1. Run all MUST stories in dependency order (recommended)
  2. Run specific stories: <enter story IDs>
  3. Run just the next unblocked story
  4. Run a specific epic: <enter epic ID>
```

Wait for user selection.

### Step 3b: Preview Budget Impact

Before starting, estimate the total cost of selected stories and compare to the project budget:

```
Budget Preview
──────────────
Selected stories: [count]
Estimated total cost: $[N]/mo (based on story sizes and AI cost signals from story map)
Project budget: $[N]/mo (from .plans/COST-*.md or DECISIONS.md, or ask user)
Budget status: WITHIN BUDGET / OVER BUDGET by $[N]

Stories with highest cost impact:
  • S2.1 — <title> [~$N/mo — LLM calls per action: 8]
  • S1.3 — <title> [~$N/mo — embedding volume: 10K docs]
```

If cost data isn't available (no `/cost-estimate` has been run), note: "No cost estimates available. The orchestrator will run `/cost-estimate` during the DESIGN phase for each story. Consider running it upfront for budget visibility."

If over budget, ask: "Estimated cost exceeds budget. Options: (1) Proceed — costs will be validated per-story during DESIGN, (2) Remove stories to fit budget, (3) Increase budget."

### Step 4: Initialize Pipeline

**Actions:**
1. Create `.plans/DECISIONS.md` if it doesn't exist (append-only architecture decision log)
2. Create `.plans/LEARNINGS.md` if it doesn't exist (append-only team learnings)
3. Initialize `.plans/PIPELINE-STATUS.md` with all selected stories in QUEUED state
4. Set up the shared resource registry in PIPELINE-STATUS.md:

```markdown
## Shared Resources
| Resource | Claimed By | Amount | Remaining |
|----------|-----------|--------|-----------|
| Monthly AI budget | — | — | $<total>/mo |
```

### Step 5: Spawn the Orchestrator

Spawn the `orchestrator` agent on a separate thread with this context:

> "Run the orchestration pipeline for the following stories from `.plans/STORIES-AI-<name>.md`:
> [list of selected story IDs]
>
> Pipeline state: `.plans/PIPELINE-STATUS.md`
> Decisions: `.plans/DECISIONS.md`
> Learnings: `.plans/LEARNINGS.md`
>
> Start with the first unblocked story. Route through: TRIAGE (chief-ai-po refine) → DESIGN (ai-architect + invert + cost-estimator) → PLAN (layoutplan) → BUILD (specialists) → HARDEN (eval-designer + guardrails-designer + ai-ops) → DELIVER (demo-builder).
>
> At each HUMAN escalation, pause and present the escalation payload.
> After each state transition, update PIPELINE-STATUS.md."

### Step 6: Present Pipeline Summary

After the orchestrator starts, present:

```
Pipeline started
─────────────────

Orchestrator: running on separate thread
Stories queued: [count]
First story: <ID> — <title> → entering TRIAGE

Pipeline status: .plans/PIPELINE-STATUS.md
Decisions log:   .plans/DECISIONS.md
Learnings log:   .plans/LEARNINGS.md

The orchestrator will:
  • Route each story through the full pipeline
  • Pause for your input at HUMAN escalation points
  • Update PIPELINE-STATUS.md after every state change
  • Detect conflicts between stories automatically

You can check progress anytime:
  • Read .plans/PIPELINE-STATUS.md
  • Run /orchestrate to see current state
```

### Step 7: Handle Ongoing Operations

When invoked on an **active pipeline** (PIPELINE-STATUS.md exists with active stories), provide operational commands:

```
Pipeline Operations
────────────────────

  status   — Show current PIPELINE-STATUS.md
  next     — Start the next queued story
  pause    — Pause a specific story
  resume   — Resume a paused story
  cancel   — Cancel a story (release resources)
  add      — Add stories from the story map to the queue
  budget   — Show budget allocation across stories
  decide   — Record a manual decision to DECISIONS.md
```

## The Full Agent Flow

For reference, here is how a single story flows through the pipeline when orchestrated:

```
TRIAGE:  orchestrator → chief-ai-po (refine mode)
           → Enriches story with AI acceptance criteria
           → Verdict: READY / NEEDS CLARIFICATION / NEEDS DECOMPOSITION

DESIGN:  orchestrator → ai-architect
           → Produces ADR, selects model, defines cost envelope
           → Routes to /ai-invert (risks) + cost-estimator (budget) in parallel
           → Checks DECISIONS.md for constraints

PLAN:    orchestrator → layoutplan
           → Reads inversion + ADR + cost envelope + learnings
           → Produces implementation plan with tasks

BUILD:   orchestrator → [prompt-engineer, rag-advisor, integration-planner]
           → Specialists work in parallel on different plan sections
           → Each reads LEARNINGS.md before starting

HARDEN:  orchestrator → [eval-designer, guardrails-designer, ai-ops]
           → All three validate in parallel
           → ALL must pass to proceed
           → Any failure → REWORK (targeted re-entry)

DELIVER: orchestrator → demo-builder
           → Packages deliverables, generates handoff doc
           → Triggers client acceptance gate

REWORK:  orchestrator → routes feedback to specific upstream agent
           → eval fails → prompt-engineer
           → guardrails fail → ai-architect
           → cost overrun → ai-architect
           → Same gate fails twice → HUMAN escalation
```

## Notes

- This skill is the **entry point** for the orchestration pipeline — it bridges `/decompose` output to the `orchestrator` agent
- For single tasks without a story map, the complexity gate in CLAUDE.md handles routing directly — no orchestrator needed
- The orchestrator runs on a separate thread to keep the main context clean
- PIPELINE-STATUS.md is the single source of truth for pipeline state — check it anytime
- DECISIONS.md and LEARNINGS.md are append-only — they accumulate knowledge across stories
- The orchestrator enforces SLAs — stories that stall get escalated automatically
- Human escalation pauses the story but not the pipeline — other stories continue flowing
- Re-running `/orchestrate` on an active pipeline resumes from current state, doesn't restart
