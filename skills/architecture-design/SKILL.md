---
name: architecture-design
description: Turn validated discovery and assessment evidence into a minimum-complexity AI architecture proposal. Decide system shape, SDK/framework category, MCP/tool boundaries, knowledge approach, model benchmark requirements, human control, evaluation, observability, runtime constraints, and dual-format machine-readable artifacts without approving or implementing the design.
---

# Architecture Design — Minimum-Complexity Proposal

Produce a reviewable proposal, not implementation authority.

## Required inputs

Prefer:

- `.north-starr/intake-validation.json`;
- `.north-starr/assessment.json`;
- the referenced Vignola handoff or requirement;
- existing codebase constraints when a target repository is supplied.

If intake validation is absent, run the sibling `intake` skill. If material
evidence changed, stop and refresh stale intake or assessment artifacts.

## Design the six cards

Complete six compact cards. Cite exact evidence or label the value as an
assumption, inference, unknown, or benchmark/spike requirement.

Within each card, represent decisions as typed records with a stable decision
ID, title, value, selection status, rationale, and evidence references. Do not
use an unconstrained notes object as the machine-readable decision.

### 1. Goal and scope

Capture the problem, outcome, MVP, exclusions, users, owner, and what a human
must still decide.

### 2. System shape

Evaluate in this order:

1. `no_change_or_no_build`
2. `process_or_configuration`
3. `buy_or_managed_capability`
4. `deterministic_software`
5. `deterministic_workflow_with_one_ai_component`
6. `prompt_chain`
7. `governed_workflow`
8. `bounded_agent_loop`
9. `multi_agent`

Choose the earliest option that meets the evidence. A bounded agent loop needs
partly emergent next steps plus tools. Multi-agent is valid only when there is
a separate task boundary and measurable benefit from at least one of:
parallelism, context isolation, separate authority, or independent evaluation.
Require a benchmark against one agent; otherwise select one agent.

Record build-vs-buy trade-offs: security/data residency, integration fit,
time-to-value, total and exit cost, portability, operability, and vendor
maturity. Do not assume custom software is necessary.

### 3. Information and tools

Prefer the simplest authoritative source:

1. deterministic database/search/query;
2. live authoritative API or MCP tool for changing system-of-record data;
3. full-context input for a small stable corpus;
4. retrieval pipeline only after retrieval need and evaluation are clear.

Create a tool registry. For each MCP server or external tool, record:

- server name, endpoint and transport;
- capture status plus an explicit list of unknown contract fields;
- owner, trust boundary, schema/version policy;
- authentication, scopes, tenant/app boundary;
- tool name, purpose, authoritative source;
- read, write, side-effect, or destructive class;
- actor allowlist and human approval point;
- timeout, retry, idempotency, quotas, and failure behavior;
- data classification, result sanitization, audit fields, and contract tests.

Unknown fields stay unknown. A vendor name is not a tool contract.
An unnamed capability may be represented with a stable local ID, null
name/purpose, `capture_status: mentioned`, and `unknown_fields`; do not invent a
tool name to satisfy the schema.

### 4. Human control

Define who reviews outputs, who owns residual risk, who may approve side
effects, and who may stop or restore service. Default tools to least privilege.
Keep read and write scopes separate. Critical privacy, tenant-isolation,
security, or compliance controls are not waivable by a generic “good enough.”

### 5. Quality and operations

Define:

- executable gold cases and unsafe/boundary cases;
- deterministic checks, task-success metrics, and human-scored criteria;
- tool selection, argument, authorization, side-effect, termination, and
  recovery tests;
- trace fields for model, prompt/policy hash, retrieval sources, tool server
  and schema, redacted arguments/result hash, actor/tenant, approval,
  retry/idempotency, latency, tokens, cost, failures, and feedback;
- release, rollback, degradation, and incident ownership.

Use `benchmark_required` instead of invented thresholds when evidence is
missing.

### 6. Runtime and technology stack

Separate these decisions:

1. host language/runtime and deployment environment;
2. provider API client;
3. structured-output and validation library;
4. agent/workflow SDK category;
5. durable workflow/state runtime;
6. MCP client/server integration;
7. evaluation, tracing, secrets, and persistence.

Represent all nine component decisions explicitly in the technology artifact:
provider client, structured-output validation, orchestration, workflow runtime,
MCP integration, evaluation, tracing, secrets, and persistence. Each records a
category, selection status, selected candidate or null, rationale, and evidence
references. Do not hide layered choices in a free-form platform map.

Evaluate SDK/framework categories:

- `no_agent_sdk` — one bounded call or a small deterministic workflow;
- `provider_sdk` — provider-specific capabilities are valuable and acceptable;
- `portable_ai_sdk` — provider portability and typed model/tool calls matter;
- `agent_sdk` — bounded tool loop, handoffs, or built-in tracing add measured
  value;
- `durable_workflow_runtime` — long-running work, resumability, timers, or
  human approvals require durable state;
- `graph_runtime` — dynamic graph state/checkpoints materially simplify a
  complex workflow.

Compare candidates using current primary documentation and a small capability
spike. Score structured output, tool calls/streaming, MCP support,
checkpointing, approvals, portability, tracing, tests/mocks, runtime/team fit,
maturity/support, licensing, and operational burden. Record the category even
when the exact library is `spike_required`. Do not choose an agent SDK merely
because the product description says “agent.”

Exact model names remain `benchmark_required` until representative,
anonymized gold cases compare eligible candidates. Record required quality,
p50 and p95 latency, cost per successful outcome, context, structured output,
tool/MCP behavior, portability, data region, and snapshot/version pinning.
Do not embed undated pricing.

## Outputs

Create and cross-reference:

- `.north-starr/architecture-proposal.json`
- `.north-starr/architecture-proposal.md`
- `.north-starr/technology-stack.json`
- `.north-starr/tool-registry.json`
- `.north-starr/manifest.json`

Use the schemas under `../../schemas/`. Include source hashes, evidence
references, assumptions, rejected alternatives, open questions, and stale
dependencies. Markdown must be a readable rendering of the JSON, not a second
source of truth.

Set architecture status to `proposed`. Set model selection to
`benchmark_required` and unresolved library choices to `spike_required` where
appropriate.

## Approval boundary

Never change the proposal to `accepted`, add it to an accepted decisions log,
decompose it for implementation, or create implementation authority in this
skill. Acceptance requires a separate human action with named approver,
timestamp, scope, evidence hashes, residual-risk owner, and any expiry or
conditions.

Return the five paths plus at most three blockers. Recommend human review next.
