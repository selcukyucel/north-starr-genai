---
name: ai-invert
description: AI-specific deep inversion analysis on a requirement before implementation. Analyzes prompt fragility, hallucination risk, cost at scale, model drift, data pipeline failures, and compliance gaps. Use before complex or high-stakes AI tasks.
argument-hint: <requirement or feature description>
---

# AI Inversion Analysis — What Could Go Wrong?

## Purpose

Before committing to implementation on an AI automation, systematically invert the requirement: instead of "how do I build this," ask "how could this fail?" Produces a structured risk analysis with AI-specific dimensions that feeds directly into planning.

This extends the standard `/genai-invert` with dimensions specific to AI/ML systems: prompt fragility, hallucination, cost, model drift, data pipelines, and compliance. Use this for any change that touches prompts, models, RAG pipelines, or AI-powered outputs. For non-AI code changes within an AI project, the standard `/genai-invert` is still available.

Run this **before** implementation for complex or high-stakes AI work. For routine tasks, the lightweight risk assessment in the project `CLAUDE.md` is sufficient.

## Pre-flight: Auto-sync Check

Before starting, read the root `CLAUDE.md` (if it exists). If `## How to Approach Tasks` appears AFTER `## Tech Stack` or `## Architecture`, the file has an outdated section order. Silently run `/genai-sync` to fix it before continuing with this skill.

## Input

The user provides a requirement, feature description, or task involving AI components. Can be a single sentence or a detailed spec.

## Workflow

### Step 1: Understand the Requirement

**Actions:**
1. Restate the requirement in your own words — confirm understanding
2. Read relevant code to understand what exists today (prompts, model configs, RAG pipelines, guardrails)
3. Check root context files (`CLAUDE.md`, `AGENTS.md`) for architecture, grain, and module map
4. Identify which AI components this task touches (prompts, models, embeddings, retrieval, guardrails, outputs)
5. Check `.plans/DECISIONS.md` and `.plans/LEARNINGS.md` if they exist — prior decisions and learnings constrain this analysis
6. **Surface assumptions** — what does this requirement take for granted? List every assumption about:
   - Input data (format, quality, availability, freshness, volume)
   - Model behavior (accuracy, consistency, latency, cost)
   - User expectations (quality threshold, acceptable failure rate, response time)
   - External systems (API uptime, model provider stability, embedding service availability)
   - Data quality (RAG source accuracy, embedding freshness, document completeness)
   - Compliance (PII handling, audit requirements, regulatory constraints)
   - Cost (token budgets, scaling behavior, caching effectiveness)
   For each assumption, ask: "What happens if this is wrong?" Assumptions that would cause HIGH impact if wrong become risks in Step 2.

### Step 2: AI Inversion Analysis

Systematically work through each dimension:

#### A. User / Consumer Impact
- What could frustrate or confuse the end user?
- What existing workflows could this break?
- What happens if the user does something unexpected?
- **Trust erosion**: If the AI produces wrong output, how badly does user trust degrade? Is recovery possible?
- **Who is most harmed** if this feature produces wrong output — and how badly? (e.g., financial loss, legal liability, reputational damage, safety risk). Name the specific stakeholder roles.
- Are there **domain-specific consequences** beyond software failure? (e.g., regulatory non-compliance, contractual breach, audit failure). If yes, these risks are automatically HIGH severity.

#### B. Prompt Fragility
- What inputs could break the prompt? (format variations, unusual characters, multiple languages, very long/short inputs)
- Is the prompt sensitive to instruction order? Would reordering sections change output quality?
- Does the prompt rely on specific model behavior that could change between versions?
- Could few-shot examples bias the model toward certain output patterns?
- Does the prompt use negative instructions ("don't do X") that models may not follow reliably?
- What happens with **adversarial inputs**? (prompt injection attempts, instructions disguised as data)
- **Generate 3-5 specific adversarial input examples** tailored to THIS prompt/pipeline:
  - Read the actual prompt text and input format first
  - Each example must use the real input format (e.g., if input is a support ticket, the adversarial input is a realistic-looking support ticket with injection payload)
  - Each example must state: the input, which specific vulnerability it targets, and the expected failure mode if the attack succeeds
  - Do NOT use generic examples like "Ignore all previous instructions" — craft attacks that exploit the specific prompt's structure, few-shot examples, or output format

#### C. Hallucination & Confabulation
- Where could the model fabricate facts, citations, or data?
- What's the **blast radius** of a hallucination? (user sees wrong info, downstream automation acts on wrong data, financial decisions based on wrong output)
- Does the system present all output with equal confidence, or does it surface uncertainty?
- What **confidence calibration** exists? Can the system say "I'm not sure"?
- Are there output fields where hallucination is more likely? (names, dates, numbers, URLs, code)
- Score hallucination risk per output field: LOW / MEDIUM / HIGH

#### D. Data Pipeline & Retrieval
- **RAG quality**: Could retrieved context be irrelevant, outdated, or contradictory?
- **Embedding drift**: Could the embedding model or index become stale? What's the refresh mechanism?
- **Chunk boundary issues**: Could important information be split across chunks and lost?
- **Missing documents**: What happens if expected source documents are unavailable?
- **Data poisoning**: Could malicious or incorrect data enter the pipeline?
- At each step of the pipeline (ingestion → parsing → embedding → retrieval → generation → post-processing), what could go wrong?
- What validation exists between steps — and what's missing?
- **RAG failure taxonomy (if the pipeline includes retrieval):** Systematically check for these six failure modes:
  1. **Retrieval failure** — relevant documents exist but aren't retrieved (test: known-answer queries where the document is in the index). Mitigations: contextual retrieval (pre-embedding context enrichment reduces retrieval failure by ~35%), hybrid retrieval, query rewriting.
  2. **Chunk boundary** — answer spans chunk boundaries and neither chunk is complete (test: questions about information near section breaks). Mitigations: contextual retrieval (context paragraph preserves document structure lost during chunking), parent-child chunking, increased overlap.
  3. **Semantic gap** — user phrasing doesn't match document phrasing (test: paraphrased queries using synonyms or different jargon). Mitigations: self-query (extracts structured filters so semantic mismatch in filter attributes doesn't hurt recall), hybrid retrieval with BM25, query rewriting, HyDE.
  4. **Multi-hop** — answer requires combining facts from 2+ documents (test: comparison or synthesis questions)
  5. **Temporal staleness** — index contains outdated information (test: questions about recently updated facts)
  6. **Context ignored** — LLM uses parametric knowledge instead of retrieved context (test: questions where retrieved context contradicts common knowledge)
  For each mode, generate 1-2 specific test inputs tailored to THIS pipeline's corpus and query patterns.
  **Cross-cutting mitigations:** If multiple failure modes score MEDIUM or HIGH, evaluate contextual retrieval (ingestion-time — mitigates modes 1, 2, 3) and self-query (query-time — mitigates modes 1, 3, 5). Both are described in the `rag-advisor` agent design.

#### E. Cost & Resource
- **Token cost at scale**: Estimate cost per request (input tokens + output tokens) × volume at 1x, 10x, 100x
- **Context window limits**: What happens when input exceeds the context window? Is there graceful truncation?
- **Rate limiting**: What happens when the model provider rate limits? Is there queueing or fallback?
- **Caching opportunities**: What can be cached? System prompts, embeddings, frequent queries?
- **Batch vs real-time**: Are there operations better suited for batch processing?
- What happens if costs exceed the budget? Is there an alert? An automatic shutoff?

#### E2. Reasoning Risk (if the pipeline uses reasoning models or chain-of-thought)
- **Confident wrong reasoning:** Model produces plausible-sounding but incorrect reasoning chains. More dangerous than hallucination because the reasoning "looks right." Test with problems that have counterintuitive answers.
- **Hidden assumptions:** Model introduces unstated assumptions mid-reasoning that change the conclusion. Test by varying premises slightly — does the reasoning adapt or carry over stale assumptions?
- **Circular reasoning:** Model restates the premise as a conclusion through several intermediate steps. Monitor for reasoning loops.
- **Runaway cost:** Reasoning models can consume 3-10x more tokens on complex problems. What happens if reasoning exceeds the token budget? Is there a hard cap? A fallback?
- **Verification gaps:** Are intermediate reasoning steps verified against tools or facts, or is the model trusting its own reasoning? Systems that verify (calculator, DB lookup, code execution) are dramatically more reliable than pure text reasoning.
- Score reasoning risk: LOW (simple tasks, standard models) / MEDIUM (multi-step with verification) / HIGH (multi-step without verification, high-stakes decisions)

#### F. Model Dependency
- What breaks if the model provider updates the model? (behavior changes, deprecation, pricing changes)
- Is the model version pinned? If not, what drift risk exists?
- Is there a fallback model? What's the quality trade-off?
- Does the system depend on model-specific features (function calling, JSON mode, vision) that may not be portable?
- What's the blast radius if the model provider has an outage?

#### G. Guardrail & Compliance
- **PII exposure**: Could user PII be sent to external model APIs? Is it logged?
- **Prompt injection**: Could user input manipulate the model to bypass business rules, leak system prompts, or produce unintended output?
- **Content filtering**: Does the model provider's content filter affect legitimate use cases?
- **Audit trail**: Is there a complete log of inputs, outputs, and decisions for compliance?
- **Regulatory requirements**: Does this need to comply with GDPR, HIPAA, SOC2, or industry-specific regulations?
- What happens when a guardrail triggers? Is there a graceful fallback?

#### H. Observability & Recovery
- How would you detect a 10% accuracy drop? What metrics are monitored?
- How would you detect a 3x cost spike? What alerts exist?
- Is the failure reversible? What's the rollback path?
- Can you replay failed requests after a fix?
- What monitoring exists for latency, error rate, token usage, and output quality?
- If the AI starts producing bad output at 2 AM, who gets paged and what do they do?

#### I. Architecture & Convention Risks
- Does this go against the grain? (check grain section in root context files)
- Does this violate any path-scoped rules (`.claude/rules/`, `.github/instructions/`)?
- Does this create coupling between modules that were independent?
- Does this introduce a pattern inconsistent with existing code?

#### J. Virtue Trade-offs (Code Quality)

Check this change against the 7 Code Virtues (see `skills/_references/virtues/code-virtues.md`) in priority order:

- **Working**: Could this break existing behavior? Are there evals proving current correctness?
- **Unique**: Does this duplicate logic that already exists elsewhere?
- **Simple**: Does this add unnecessary entities, relationships, or indirection?
- **Clear**: Will the result be obvious to the next reader, or puzzling?
- **Easy**: Will this make future changes harder or easier?
- **Developed**: Are the abstractions mature and well-placed, or primitive?
- **Brief**: Is there unnecessary verbosity?

When two virtues conflict, **always preserve the higher-priority one**. Name the tension explicitly:

```
**Virtue Tension:** [lower virtue] would improve, but at the cost of [higher virtue] → preserve [higher virtue]
```

### Step 2b: Classify New vs Pre-Existing Risks

After completing the dimension analysis, go back through every risk identified and classify it:

- **NEW** — This risk is introduced or significantly worsened by the proposed change. It didn't exist (or was negligible) before.
- **PRE-EXISTING** — This risk already exists in the current system. The change doesn't make it worse, but the analysis surfaced it.
- **AMPLIFIED** — This risk existed before but the proposed change makes it materially worse (e.g., adding more model calls amplifies an existing "no cost controls" risk).

In the output (Step 4), mark each risk with its classification: `[NEW]`, `[PRE-EXISTING]`, or `[AMPLIFIED]`. This tells the user which risks they're *adding* vs. which they're *inheriting*.

**Rule:** Pre-existing risks are still worth listing (the user may not know about them), but they should not inflate the overall risk rating. Only NEW and AMPLIFIED risks determine the overall risk level.

### Step 3: Assess and Prioritize

Rate the overall risk (based on NEW and AMPLIFIED risks only — pre-existing risks inform but don't escalate):

| Level | Meaning | Action |
|-------|---------|--------|
| **LOW** | Well-understood, contained, reversible | Proceed to implementation |
| **MEDIUM** | Some unknowns, but manageable with care | Plan carefully, validate incrementally |
| **HIGH** | Significant unknowns, wide blast radius, or irreversible | Spawn the `genai-layoutplan` agent to break into tracked pieces, spike first, or clarify requirements |

### Step 4: Produce Output

Present the analysis:

```
## AI Inversion Analysis: [requirement summary]

**Modules Affected:** [list]
**AI Components Touched:** [prompts / models / embeddings / retrieval / guardrails / outputs]
**Against the Grain?** [yes/no — why]
**Virtue Tensions:** [any virtue trade-offs identified, or "none"]

### Risks

1. **[risk name]** — [severity: HIGH/MED/LOW] — [dimension: A-J] — [NEW/PRE-EXISTING/AMPLIFIED]
   **Where:** `path/to/file.py:function_name` (or module/component if file-level is too broad)
   [description, how it could happen, what the impact would be]

2. **[risk name]** — [severity: HIGH/MED/LOW] — [dimension: A-J] — [NEW/PRE-EXISTING/AMPLIFIED]
   **Where:** `path/to/file.py:function_name`
   [description, how it could happen, what the impact would be]

[...repeat for each significant risk]

### Hallucination Risk Map

| Output Field | Risk Level | Mitigation |
|-------------|-----------|------------|
| [field]     | HIGH/MED/LOW | [what to do] |

### Cost Projection

| Scale | Requests/mo | Input Tokens | Output Tokens | Est. Cost/mo |
|-------|------------|--------------|---------------|-------------|
| 1x    | [N]        | [N]          | [N]           | $[N]        |
| 10x   | [N]        | [N]          | [N]           | $[N]        |
| 100x  | [N]        | [N]          | [N]           | $[N]        |

### Adversarial Input Examples

(Each must use the actual input format and target a specific vulnerability)

1. **Input:** [realistic input with embedded attack, using the actual format]
   **Targets:** [which vulnerability: injection, extraction, hallucination trigger, guardrail bypass]
   **Expected failure:** [what happens if the attack succeeds]

2. **Input:** [...]
   **Targets:** [...]
   **Expected failure:** [...]

3. **Input:** [...]
   **Targets:** [...]
   **Expected failure:** [...]

### Assumptions (verify before implementing)

- [assumption]: [what happens if wrong]
- [assumption]: [what happens if wrong]

### Edge Cases to Handle

- [case]: [what should happen]
- [case]: [what should happen]

### Recommendations

**Overall Risk:** [LOW / MEDIUM / HIGH]

**Before implementing:**
- [prerequisite or clarification needed]

**During implementation:**
- [specific thing to watch for]
- [specific validation to include]

**Eval strategy (one per HIGH/MED risk):**

| Risk | Test Type | Pass Criteria |
|------|-----------|---------------|
| [risk name] | [specific test: golden file / adversarial inputs / load test / A/B comparison / human review sampling / statistical scoring] | [concrete threshold: "95% accuracy on golden set" / "0 injection bypasses on 20 adversarial inputs" / "p95 < 500ms at 100 RPS"] |

**After implementing:**
- [what to verify]
- [what to monitor — specific metrics, dashboards, alerts]
```

### Step 5: Persist to Disk

After presenting the analysis to the user (and incorporating any feedback), write it to disk so downstream agents can consume it without context loss.

**Actions:**
1. Create `.plans/` directory if it doesn't exist
2. Generate a short kebab-case name from the requirement (e.g., `rag-pipeline-upgrade`, `classification-prompt`)
3. Write the full analysis to `.plans/INVERT-<name>.md` using the format from Step 4, with this header:

```markdown
# AI Inversion Analysis: <requirement summary>

**Created:** <date>
**Overall Risk:** <LOW / MEDIUM / HIGH>
**Modules Affected:** <list>
**AI Components Touched:** <list>
**Against the Grain?** <yes/no — why>
**Virtue Tensions:** <any virtue trade-offs identified, or "none">
```

4. Inform the user: "Analysis saved to `.plans/INVERT-<name>.md`"

### Step 6: Trigger Planning

If the overall risk is MEDIUM or HIGH, prompt the user:

> "Risk is [MEDIUM/HIGH]. I'll spawn the genai-layoutplan agent to build an implementation plan from this analysis. It runs on a separate thread so your main context stays clean."

Then spawn the `genai-layoutplan` agent (available in `.claude/agents/` or `.github/agents/`). The agent runs on a separate thread to keep the main context clean.

For LOW risk, inform the user that the `genai-layoutplan` agent is available if they want structured planning, but it's optional.

## Notes

- This skill is language-agnostic — it works for any AI project type
- Read actual code, prompts, and configs before forming opinions — never invert based on assumptions
- **Every risk must cite a specific file path or function** — abstract risks like "hallucination could occur" without grounding in actual code are not actionable. If you can't point to where in the code the risk manifests, the risk is too vague.
- Root context files (`CLAUDE.md`, `AGENTS.md`) and path-scoped rules provide the baseline for convention checks
- `.plans/DECISIONS.md` and `.plans/LEARNINGS.md` provide accumulated knowledge from prior stories — read them if they exist
- Focus on risks that are **likely and impactful** — don't enumerate every theoretical failure
- Dimensions B-H are AI-specific; dimensions A, I, J overlap with the standard `/genai-invert`
- If the analysis reveals HIGH risk, recommend spawning the `genai-layoutplan` agent to break the task into tracked, safer pieces
- The output of this analysis feeds directly into the `genai-layoutplan` agent — the risks become constraints and dedicated tasks in the implementation plan
- For non-AI code changes within an AI project, use the standard `/genai-invert` instead
