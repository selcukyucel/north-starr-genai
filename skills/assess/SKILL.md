---
name: assess
description: Assess a validated client requirement or Vignola handoff and recommend the simplest viable system shape. Consider no-build, configuration, buy, deterministic software, bounded AI workflows, prompt chains, governed workflows, agent loops, and justified multi-agent systems; identify only essential specialists and emit JSON plus Markdown without prescribing an unbenchmarked model or SDK.
---

# Assess — Simplest Viable System

Classify what kind of solution is justified before decomposing work or choosing
technology. This is a short decision gate, not a full architecture studio.

## Input

Accept:

- `.north-starr/intake-validation.json`;
- a Vignola `north_starr_handoff` export;
- a PRD, brief, or raw requirement.

When the input is a handoff or contains discovery claims and no current intake
validation exists, run the sibling `intake` skill first. Proceed provisionally
when the intake is provisional and the unknowns do not block system-shape
selection. Stop when it is stale or blocked.

## Decision order

Evaluate options in this order. Recommend the first option that can achieve the
evidenced outcome.

1. `no_change_or_no_build` — the problem is not worth solving now, evidence is
   insufficient, or an existing capability already meets the need.
2. `process_or_configuration` — training, naming, policy, dashboard, workflow,
   or product configuration fixes the problem.
3. `buy_or_managed_capability` — an existing product/capability is a better fit
   than custom software.
4. `deterministic_software` — fixed rules, search, queries, mappings, or
   conventional code can solve it.
5. `deterministic_workflow_with_one_ai_component` — one bounded probabilistic
   task sits inside an otherwise explicit flow.
6. `prompt_chain` — several fixed model transformations run in a known order.
7. `governed_workflow` — business stages, branching, retries, approvals, and
   failure paths are known.
8. `bounded_agent_loop` — the next step is partly emergent and the model must
   select from a restricted toolset under iteration, cost, time, and authority
   limits.
9. `multi_agent` — valid only with a separate task boundary plus measurable
   benefit from parallelism, context isolation, separate authority, or
   independent evaluation. Require a one-agent baseline.

The word “agent” in a requirement is not evidence for an agent architecture.
Private or changing knowledge is not automatically RAG; live authoritative
tools or deterministic queries may be simpler.

## Workflow

### 1. Restate the evidence

Summarize the problem, affected people, desired outcome, MVP boundary, and
human owner. Keep confirmed facts separate from assumptions and unknowns.

### 2. Compare build strategies

Compare `no_build`, `configure`, `buy`, `build`, and `hybrid` using:

- security, privacy, compliance, and data residency;
- integration fit and authoritative systems;
- time-to-value;
- total operating and exit cost;
- portability and vendor lock-in;
- team skills and operational burden;
- reversibility and failure impact.

Do not recommend custom build merely because the input asks for one.

### 3. Check AI necessity

Identify the smallest task that actually needs probabilistic reasoning. Keep
normalization, filtering, authorization, validation, state transitions, and
business rules deterministic unless evidence shows otherwise.

### 4. Check knowledge and actions

Record whether the solution needs:

- a deterministic query or existing search;
- a live authoritative API/MCP tool;
- a small stable context;
- retrieval with a measurable retrieval evaluation;
- read-only analysis or side-effecting action.

If MCP or tools are mentioned but endpoint, auth, scopes, tenant boundary, or
tool allowlist are missing, record an architecture input gap. Do not invent a
tool catalogue.

### 5. Set technology requirements, not products

Record required quality, latency, cost, context, portability, data region,
structured output, streaming, tool calling, MCP, state, approvals, and tracing.
Keep:

- exact model: `benchmark_required`;
- exact SDK/framework: `spike_required` unless the codebase and capability
  evidence make the choice obvious.

Do not include a static provider/model pricing table.

### 6. Activate only necessary expertise

Select at most three immediate specialists. Typical choices:

- the sibling `architecture-design` skill for a proposal;
- `eval-suite` for representative gold cases;
- `ai-invert` for material risk;
- `cost-estimate` for a quantified budget;
- integration, retrieval, prompt, safety, or operations work only when the
  chosen shape actually needs it.

Do not launch the full pipeline during assessment.

## Output

Create:

- `.north-starr/assessment.json`
- `.north-starr/assessment.md`

The JSON must validate against `../../schemas/assessment.schema.json` and
include source hashes, readiness, selected shape, build strategy, at least two
alternatives, risks, assumptions, no more than three blocking questions, and
`model_selection_status: benchmark_required`.

The Markdown must be a compact rendering with:

```text
Recommended shape:
Why this is the simplest fit:
AI task, if any:
Authoritative systems/tools:
Build strategy:
Rejected or conditional alternatives:
Assumptions and blockers:
Next step:
```

Set status to `provisional` when important inputs are assumptions. Changed
source hashes make the assessment `stale`.

## Boundaries

- Do not produce an accepted ADR.
- Do not select an exact model without eval evidence.
- Do not select an agent SDK before determining that an agent loop is needed.
- Do not decompose or implement.
- Ask no more than three plain-language blocking questions.

Recommend the sibling `architecture-design` skill when a proposal is justified.
Recommend no further AI design when no-build, configuration, buy, or
deterministic software is sufficient.
