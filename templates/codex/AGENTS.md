# Project Instructions

Use North Starr only when the task concerns AI discovery, architecture, model or
tool behavior, evaluation, safety, cost, or AI operations. Ordinary code, docs,
configuration, and small fixes follow the project's normal workflow.

## North Starr Journey

1. Validate client evidence with `$intake`.
2. Choose the simplest viable system shape with `$assess`.
3. Create a six-card proposal with `$architecture-design`.
4. Ask a named human to accept, reject, or revise the proposal.
5. Use `$decompose` or `$orchestrate` only for an accepted, current design.

Never treat a proposal as implementation authority. Discovery changes make
dependent assessment and architecture artifacts stale until regenerated.

## Decision Rules

- Separate confirmed facts, inferences, assumptions, unknowns, deferred items,
  and conflicts.
- Consider no-build, configuration, buying, and deterministic software before
  adding AI.
- Prefer one bounded AI component before a prompt chain, governed workflow,
  bounded agent loop, or multi-agent system.
- Use multi-agent only for a separate task boundary with measurable benefit.
- Record MCP servers and other tools explicitly, including authority, scopes,
  side effects, approval, failure behavior, and audit requirements.
- Keep exact model names as `benchmark_required` and uncertain SDK choices as
  `spike_required` until evidence supports a decision.
- Produce versioned JSON and readable Markdown under `.north-starr/`.
- Keep client-facing language plain and surface no more than three blockers at
  once.

## Project Context

### Tech Stack

[Languages, frameworks, package manager, build, test, CI/CD, AI SDKs, MCP
servers, model providers, data systems, and evaluation tools actually found.]

### Architecture

[Current topology, module boundaries, dependency direction, runtime boundaries,
and human-control points.]

### Grain

[Changes that are easy, changes that are expensive, and conventions not to
fight without evidence.]

### Module Map

[Top-level modules and their responsibilities.]
