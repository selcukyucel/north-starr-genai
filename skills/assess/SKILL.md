---
name: assess
description: Classify project type, recommend approach, identify needed agents, estimate complexity, and flag risks. Runs BEFORE /decompose to help North Starr adapt its pipeline to what is being built.
argument-hint: <requirement text, file path, or brief description>
---

# Assess — Project Type Recommendation

## Purpose

When a client gives a raw requirement, this skill classifies the project type and recommends the right approach BEFORE decomposition begins. It answers the questions that `/decompose` and `chief-ai-po` don't ask: what KIND of project is this, what agents will it need, and what's the right architecture approach?

Without `/assess`, the pipeline treats every project identically. With it, North Starr adapts its agent activation, pipeline configuration, and complexity expectations to the specific project type.

## When to Use

- **Before `/decompose`** — when a client gives a raw requirement and you need to understand what kind of project it is
- **Before `/discover`** — when you want to validate your understanding of the project type before eliciting detailed requirements
- **On demand** — when mid-project you realize the project type has shifted (e.g., what started as an automation pipeline now needs multi-agent orchestration)

For projects where the type is already clear and documented, skip directly to `/decompose`.

## Input

The user provides one of:
- **Pasted text** — a raw requirement, brief, or description
- **File path** — a document (markdown, text, PDF) containing the requirement
- **Conversation summary** — output from `/discover` or a prior discussion

## Workflow

### Step 1: Read & Understand the Requirement

**Actions:**
1. If a file path is provided, read the content (use PDF pagination for large PDFs)
2. If text is pasted, use it directly
3. Extract the core intent: what problem is being solved, for whom, at what scale
4. Identify any explicit constraints mentioned (budget, timeline, compliance, existing infrastructure)

### Step 2: Classify Project Type

Evaluate the requirement against these project types:

| Type | Signals | Example |
|---|---|---|
| **Automation Pipeline** | Event-driven, classification, extraction, routing, batch processing, document processing | "Categorize support tickets and route to the right team" |
| **Agent Harness** | Production agent runtime, tool use, memory, safety-critical, long-running tasks | "Build an agent that researches competitors and writes reports" |
| **Multi-Agent System** | Multiple agents collaborating, supervisor/sub-agent, peer-to-peer, pipeline of agents | "Research agent feeds writer agent, reviewer checks output" |
| **RAG Application** | Knowledge base, document Q&A, search + generation, citations needed | "Let employees ask questions about our internal policies" |
| **Prompt Chain** | Sequential LLM calls, transformation pipeline, no agent autonomy | "Summarize → translate → format for each incoming document" |
| **AI OS Component** | Shared platform layer, multi-tenant, cross-team, extensibility required | "Build a shared knowledge layer all teams can query" |
| **Hybrid** | Combines two or more of the above | "RAG-powered agent with tool use and multi-step reasoning" |

If the requirement clearly maps to one type, classify it. If it spans multiple types, classify as **Hybrid** and list the component types.

### Step 3: Determine Architecture Approach

Based on the project type, recommend the high-level architecture:

**Automation Pipeline:**
- Topology: event source → preprocessor → AI call → post-processor → output sink
- Key decisions: batch vs streaming, model selection, error handling strategy
- Typical components: input parser, prompt template, output validator, routing logic

**Agent Harness:**
- Topology: agent loop (observe → think → act → reflect) with tool registry and safety layer
- Key decisions: memory strategy (stateless/session/persistent), checkpoint design, tool authorization
- Typical components: agent runtime, tool definitions, safety guardrails, state management

**Multi-Agent System:**
- Topology selection heuristic:
  - Agents process data in sequence (A→B→C) → **Pipeline** topology
  - One agent delegates tasks to specialists → **Supervisor / sub-agent** topology
  - Agents review or critique each other's work → **Peer-to-peer** topology
  - Complex delegation with sub-teams → **Hierarchical** topology
- Recommend a specific topology in the sketch based on the requirement signals. Name it.
- Key decisions: state sharing (message passing vs shared memory), loop control (max iterations, cost cap), handoff protocol
- Typical components: per-agent definitions, orchestrator/supervisor (if not pipeline), shared state store, inter-agent message format

**RAG Application:**
- Topology: ingest pipeline → vector store ← query pipeline → generation
- If the RAG app includes a chat interface → add: conversation manager, session memory, escalation router
- Key decisions: chunking strategy, embedding model, retrieval approach, re-ranking
- Typical components: document ingester, embedding service, vector DB, retrieval layer, prompt with context injection

**Prompt Chain:**
- Topology: sequential LLM calls with transformation between stages
- Key decisions: chain decomposition, intermediate validation, error propagation
- Typical components: prompt templates per stage, intermediate validators, chain orchestrator

**AI OS Component:**
- Topology: platform service with API layer, multi-tenant isolation, extensibility hooks
- Key decisions: multi-tenancy model, API versioning, extensibility patterns
- Typical components: API gateway, tenant isolation, plugin system, shared model configs

**Hybrid (combines two or more types):**
- Identify the primary type (the one that defines the core data flow) and the secondary type(s) that extend it
- Compose the architecture sketch by starting with the primary type's topology and layering in components from secondary types
- Example: RAG Application (primary) + Agent Harness (secondary) = ingest pipeline → vector store ← agent loop (observe → retrieve → reason → act) with safety layer
- Name each component and its source type in the sketch so the ai-architect knows which patterns to apply

### Step 4: Map Agent Activation

Based on the project type, determine which pipeline agents are needed:

| Agent | Automation | Agent Harness | Multi-Agent | RAG App | Prompt Chain | AI OS |
|---|---|---|---|---|---|---|
| chief-ai-po | Yes | Yes (all 6 safety stories) | Yes (per-agent + orchestration stories) | Yes | Yes | Yes |
| ai-architect | Yes | Yes | Yes (topology patterns critical) | Yes | Lightweight | Yes (platform concerns) |
| prompt-engineer | Yes | Yes (agent system prompts) | Yes (per-agent prompts) | Yes | Yes (per-stage prompts) | Yes |
| rag-advisor | Only if knowledge base | If retrieval-augmented | If shared retrieval | **Critical** | No | If shared knowledge layer |
| integration-planner | If external APIs | Yes (tool access) | If external communication | If external data sources | If external APIs | Yes |
| eval-designer | Yes | Yes | Yes (per-agent + end-to-end) | Yes | Yes (per-stage + end-to-end) | Yes |
| guardrails-designer | If public-facing | **Critical** | Yes | Yes | If public-facing | **Critical** |
| prompt-adversary | If public-facing | **Critical** | Yes | Yes | If public-facing | **Critical** |
| ai-ops | Lightweight | Yes | Yes (per-agent monitoring) | Yes | Lightweight | **Critical** |
| cost-estimator | Yes | Yes | Yes | Yes | Yes | Yes |
| demo-builder | Yes | Yes | Yes | Yes | Yes | Yes (with onboarding docs) |
| agentic-designer | If UI needed | If UI needed | If UI needed | If UI needed | No | If UI needed |

### Step 5: Estimate Complexity & Flag Risks

**Complexity estimation:**
- **S (Small):** Single AI call, clear input/output, no external integrations. 1-2 stories.
- **M (Medium):** Multiple AI calls or RAG pipeline, 1-2 integrations, moderate safety concerns. 2-4 stories.
- **L (Large):** Agent with tools, multi-step workflows, compliance requirements, multiple integrations. 4-8 stories.
- **XL (Extra Large):** Multi-agent system, platform component, real-time requirements, regulatory compliance. 8+ stories (recommend phased delivery).

**Risk flags — check each. For every flag that applies, you MUST state (a) the concrete impact on this project and (b) a specific mitigation or next step. Do not list a risk without both.**

- [ ] **Needs fine-tuning** — domain-specific style or format that prompt engineering alone won't achieve
- [ ] **Needs real-time** — streaming, sub-second latency, WebSocket connections
- [ ] **Needs compliance review** — PII, HIPAA, GDPR, financial regulations, audit trails
- [ ] **Needs existing infrastructure** — depends on databases, APIs, or services not yet available
- [ ] **Needs credential provisioning** — external API keys, OAuth flows, service accounts
- [ ] **High cost risk** — large volume, expensive models, or open-ended generation
- [ ] **Novel problem** — no established pattern in the team's experience
- [ ] **Multi-team dependency** — requires coordination with other teams or external vendors

Example of a properly flagged risk:
> **Needs credential provisioning** — Impact: Zendesk API requires OAuth2 service account; BUILD phase will block until credentials are provisioned. Mitigation: Request credentials in parallel with DESIGN phase; integration-planner will flag BLOCKED if missing at BUILD start.

### Step 6: Write Assessment

Write to `.plans/ASSESS-<name>.md`:

```markdown
# Assessment: <name>

**Created:** <date>
**Status:** ACTIVE
**Source:** <file path or "requirement text">

## Requirement Summary

<2-3 sentences capturing the core requirement>

## Project Type

**Classification:** <Automation Pipeline / Agent Harness / Multi-Agent System / RAG Application / Prompt Chain / AI OS Component / Hybrid>

**Rationale:** <Why this classification — what signals pointed to this type>

[If Hybrid:]
**Component types:** <list the sub-types>

## Architecture Sketch

**Topology:** <high-level component flow>

**Key components:**
- <component 1> — <responsibility>
- <component 2> — <responsibility>

**Key decisions to make in DESIGN phase:**
- <decision 1>
- <decision 2>

## Technology Recommendations

- **Model(s):** <recommended starting point, to be validated by ai-architect>
- **RAG:** <needed / not needed / conditional — reason>
- **Vector DB:** <if RAG needed, initial recommendation>
- **External integrations:** <list>
- **Infrastructure:** <what the codebase needs that may not exist>

## Agent Activation Map

| Agent | Needed | Priority | Notes |
|---|---|---|---|
| chief-ai-po | Yes/No | Critical/Standard/Lightweight | <context> |
| ai-architect | Yes/No | Critical/Standard/Lightweight | <context> |
| ... | ... | ... | ... |

## Complexity & Effort

**Complexity:** <S / M / L / XL>
**Estimated stories:** <range>
**Recommended delivery approach:** <single sprint / phased / MVP + iterations>

## Risk Flags

- <flag icon> **<risk>** — <impact and recommended mitigation>

## Recommendation

<One of:>
- **Proceed to `/decompose`** — requirement is clear enough for story decomposition
- **Run `/discover` first** — requirement needs more detail before decomposition (list what's missing)
- **Needs human discussion** — <specific concern that requires human judgment>
```

### Step 7: Present Results & Recommend Next Step

Present the assessment summary to the user:

```
Assessment: <name>
──────────────────
Project type:      <type>
Complexity:        <S/M/L/XL>
Estimated stories: <range>
Risk flags:        <count> (<list key risks>)
Agent activation:  <count> of 12 agents needed

Key architecture decisions:
  • <decision 1>
  • <decision 2>

Recommendation: <proceed to /decompose | run /discover first | needs discussion>
```

If recommending `/decompose`, ask:
> "Ready to decompose into stories? Run `/decompose` with this requirement."

If recommending `/discover`, ask:
> "The requirement needs more detail before I can decompose it. Run `/discover` to elicit the missing information."

If flagging for discussion, explain what needs human input.

## Notes

- This skill is intentionally lightweight — it should take 1-2 minutes, not 30 minutes
- The architecture sketch is high-level, NOT a full ADR — ai-architect produces that in DESIGN phase
- Agent activation map tells the orchestrator which agents to dispatch, avoiding unnecessary specialist work
- Complexity estimates use AI context budget sizing (same as story sizing in `/decompose`)
- Risk flags feed directly into the inversion analysis — they become the starting point for `/ai-invert`
- If the project type changes mid-execution (discovered during BUILD), re-run `/assess` to update the agent activation map
