---
name: handoff-doc
description: Generate client-facing documentation for completed AI automations. Includes system overview, architecture diagram, monitoring guide, prompt modification guide, escalation procedures, and SLA summary.
argument-hint: <automation or project name>
---

# Handoff Doc — Client Handoff Documentation

## Purpose

Generate client-facing documentation for completed AI automations. When an AI automation is delivered to a client, they need more than working software — they need to understand what they have, how to monitor it, how to safely modify it, when to escalate, and what to expect in terms of performance. This skill produces that documentation.

The output is written in client language — clear, non-technical where possible, with a glossary for terms that require explanation. It serves as both an operational manual and a reference document for the client's team.

Run this **after** the automation is complete, tested, and ready for handoff. The skill reads the full codebase and all `.plans/` artifacts to produce a comprehensive document without requiring the client to understand the internal engineering.

## Pre-flight: Auto-sync Check

Before starting, read the root `CLAUDE.md` (if it exists). If `## How to Approach Tasks` appears AFTER `## Tech Stack` or `## Architecture`, the file has an outdated section order. Silently run `/genai-sync` to fix it before continuing with this skill.

## Input

The user provides the name of the automation or project being handed off. This can be:
- A project name (e.g., "Acme Support Classifier", "Invoice Processing Pipeline")
- An automation name matching existing `.plans/` artifacts
- A client name plus a brief description of what was built

## Workflow

### Step 1: Read the Full Automation and Artifacts

**Actions:**
1. Read the full automation codebase:
   - Application code and entry points
   - Prompts and system instructions (every prompt file)
   - Model configurations (model name, version, temperature, max tokens, any fine-tuning)
   - Pipeline configurations (RAG setup, retrieval settings, embedding configs)
   - Infrastructure definitions (deployment configs, environment variables, scheduled jobs)
   - API definitions (endpoints, request/response schemas, authentication)
   - Guardrail implementations (input validation, output filtering, rate limiting)
2. Read root context files (`CLAUDE.md`, `AGENTS.md`) for architecture and conventions
3. Read ALL `.plans/` artifacts:
   - `INVERT-*.md` — risk analyses (informs Known Limitations section)
   - `GUARDRAILS-*.md` — guardrail specs (informs Monitoring Guide)
   - `BASELINE-*.md` — baselines (informs SLA Summary)
   - `COST-*.md` — cost projections (informs SLA Summary)
   - `EVAL-*/` — eval suites (informs performance expectations)
   - `PLAYBOOK-*.md` — incident playbooks (informs Escalation Procedures)
   - `DEPLOY-*.md` — deployment checklists (informs Architecture section)
   - `DECISIONS.md` — design decisions (informs Architecture and Known Limitations)
   - `LEARNINGS.md` — lessons learned (informs Known Limitations)
   - `PROMPTS-*/` — prompt versions (informs Prompt Modification Guide)
4. Build a complete mental model of: what the system does, how it works, what can go wrong, and how to operate it

### Step 2: Generate Documentation Sections

Generate each of the following sections. Write in client-friendly language. Avoid internal engineering jargon unless it is defined in the Glossary. Assume the reader is technically competent but not an AI/ML specialist.

#### Section A: System Overview

**What to cover:**
- What the system does — in one paragraph, plain language, from the client's perspective
- What problem it solves and what value it delivers
- Key capabilities (what it can do) and explicit non-capabilities (what it cannot and should not be used for)
- How end users interact with it (UI, API, automated pipeline, email, etc.)
- High-level data flow: what goes in, what comes out
- Confidence levels — what the system is very good at, what it handles adequately, and where human review is recommended

**Tone:** Clear, confident, honest about limitations. No marketing language.

#### Section B: Architecture

**What to cover:**
- Component diagram in text format (ASCII or Mermaid markdown):
  - Data sources (what feeds the system)
  - Processing pipeline (how data flows through the system)
  - AI components (which models, what they do, where they run)
  - Storage (databases, indexes, caches)
  - Output channels (where results go)
  - External integrations (third-party APIs, model providers)
- For each component:
  - What it does (one sentence)
  - Where it runs (cloud service, server, client-side)
  - Key configuration that the client might need to know about
- Data flow narrative: walk through a typical request from input to output
- Security boundaries: where data crosses trust boundaries, what encryption is in place, where credentials are stored

**Note:** Keep this section accessible. The client needs to understand the architecture for operational purposes, not to rebuild it.

#### Section C: Monitoring Guide

**What to cover:**
- **What to monitor** — organized by importance:
  - Critical metrics (check daily): error rate, response time, output quality indicators
  - Important metrics (check weekly): cost trends, token usage, guardrail trigger rates
  - Informational metrics (review monthly): input patterns, usage growth, model performance trends
- **Where to look** — specific dashboards, log locations, or monitoring tools (name the actual tools)
- **What is normal** — derive ALL values from `.plans/BASELINE-*.md`. Do NOT use placeholder X/Y/Z values — use the actual baseline numbers:

  | Metric | Normal Range | Investigate If | Source |
  |--------|-------------|---------------|--------|
  | Response time p50 | <baseline_p50 ± 20%> | > <baseline_p95 × 1.5> | BASELINE-*.md |
  | Response time p95 | <baseline_p95 ± 20%> | > <baseline_p95 × 2> | BASELINE-*.md |
  | Error rate | <baseline_rate ± 1%> | > <baseline_rate + 3%> | BASELINE-*.md |
  | Daily cost | $<baseline_daily ± 15%> | > $<baseline_daily × 1.5> | COST-*.md |
  | Guardrail trigger rate | <baseline_rate ± 25%> | > <baseline_rate × 3> | GUARDRAILS-REPORT-*.md |
  | Request volume | <baseline_volume ± 30%> | 0 for >10 min during business hours | logs |

  If a baseline doesn't exist for a metric, flag it as `[NEEDS BASELINE — run /baseline]` rather than guessing. The "Investigate If" thresholds use the regression thresholds from the baseline where available.

- **What is abnormal** — for each abnormal signal, state the specific threshold (derived above), the first diagnostic step, and who to contact. Reference the incident playbook (`.plans/PLAYBOOK-*.md`) for each signal if it maps to a known incident category.
- **What to do when something looks wrong:**
  - For each abnormal signal: first diagnostic step and who to contact
  - Reference the incident playbook (`.plans/PLAYBOOK-*.md`) if it exists
- **Scheduled maintenance:**
  - Data refresh schedule (how often embeddings/indexes are updated)
  - Model update process (how model version changes are handled)
  - Certificate/credential rotation schedule

#### Section D: Prompt Modification Guide

**What to cover:**
- **What prompts are and why they matter** — brief explanation in client language: prompts are the instructions that tell the AI how to behave; changing them changes the system's behavior
- **Which prompts can be modified** — list each prompt with:
  - Location (file path or configuration location)
  - Purpose (what this prompt controls)
  - Modification safety level with **rationale**:

  | Prompt | Purpose | Safety Level | Rationale |
  |--------|---------|-------------|-----------|
  | <name> | <what it controls> | **Safe** | <why: "Tone and greeting text only — no impact on classification accuracy. Changes won't affect downstream systems."> |
  | <name> | <what it controls> | **Caution** | <why: "Few-shot examples affect classification accuracy. Changes require re-running eval suite. Last measured: 92% accuracy with current examples."> |
  | <name> | <what it controls> | **Do Not Modify** | <why: "Contains compliance-critical classification rules validated against 500+ test cases and approved by legal. Changes require full eval + guardrail validation + legal review."> |

  The rationale explains what BREAKS if the prompt is modified incorrectly — not just the risk level but the specific consequence and what testing is needed.
- **How to safely modify a prompt:**
  1. Document the reason for the change
  2. Save the current version before making changes (reference `/prompt-version` if available)
  3. Make the change in a non-production environment first
  4. Run the eval suite to verify no regressions (explain how to run evals)
  5. Compare results against baseline
  6. Deploy to production with monitoring
  7. Watch metrics for 24-48 hours after the change
- **Common safe modifications:**
  - Adding or updating examples in few-shot prompts
  - Adjusting tone or style instructions
  - Adding new output categories (with testing)
  - Updating knowledge cutoff references
- **Modifications that require expert support:**
  - Changing the system prompt structure or role definition
  - Modifying guardrail instructions within prompts
  - Changing output format schemas
  - Switching models or model versions
  - Modifying retrieval or context injection logic
- **Rollback procedure:** How to revert to a previous prompt version if the change causes issues

#### Section E: Escalation Procedures

**What to cover:**
- **When to escalate** — clear triggers, not judgment calls:
  - System is down (no responses for more than X minutes)
  - Error rate exceeds X% for more than Y minutes
  - Client reports factually incorrect output that could cause harm
  - Cost exceeds daily/monthly budget threshold
  - Security concern (suspected data breach, prompt injection success)
  - Output quality noticeably degraded across multiple requests
- **Who to contact:**
  - **Level 1 — Operational issues** (system down, errors): [contact details, response time SLA]
  - **Level 2 — Quality issues** (accuracy problems, unexpected behavior): [contact details, response time SLA]
  - **Level 3 — Security issues** (data exposure, injection, compliance): [contact details, response time SLA]
- **How to escalate:**
  - Preferred communication channel (email, Slack, phone, ticketing system)
  - Information to include in the escalation (timestamp, affected request IDs, screenshots, error messages)
  - Expected response time for each severity level
- **What NOT to do:**
  - Do not modify system prompts or configurations under pressure without testing
  - Do not restart production services without understanding the root cause
  - Do not share system prompts or internal error messages externally

#### Section F: SLA Summary

**What to cover — derive ALL numbers from existing artifacts. Do NOT use placeholder X values:**

- **Accuracy targets:** Derive from `.plans/EVAL-*/results.md` and `.plans/BASELINE-*.md`
  - Overall accuracy: <actual eval score>% on <metric name> as measured by <eval suite name>
  - Per-category accuracy if applicable (from eval per-category breakdown)
  - Accuracy measurement method and frequency
  - If no eval results exist: flag as `[ACCURACY TARGET NEEDS EVAL — run /eval-suite]`

- **Latency targets:** Derive from `.plans/BASELINE-*.md`
  - p50 response time: <actual baseline p50>
  - p95 response time: <actual baseline p95>
  - Maximum acceptable: <baseline p95 × 2> (or from DECISIONS.md if defined)
  - If no baseline exists: flag as `[LATENCY TARGET NEEDS BASELINE — run /baseline]`

- **Availability targets:**
  - Uptime target: <from DECISIONS.md or contractual agreement>
  - Planned maintenance windows
  - If not defined: flag as `[AVAILABILITY TARGET TO BE AGREED WITH CLIENT]`

- **Cost targets:** Derive from `.plans/COST-*.md`
  - Expected monthly cost: $<actual projection from cost estimate> at <volume>
  - Cost scaling behavior: <from cost estimate 1x/10x/100x table>
  - Cost cap: <from DECISIONS.md or budget allocation>
  - If no cost estimate exists: flag as `[COST TARGET NEEDS ESTIMATE — run /cost-estimate]`

- **Throughput:**
  - Maximum requests per minute/hour (from rate limit config)
  - Burst capacity
  - What happens when limits are reached

- **What is NOT covered by the SLA:**
  - Explicit carve-outs (e.g., "accuracy targets do not apply to inputs outside the defined scope")
  - Force majeure (model provider outages, regulatory changes)

**Rule:** Every SLA number must have a source. If the source artifact doesn't exist, use `[NEEDS <artifact> — run /<skill>]` instead of inventing numbers. Handoff documents with made-up SLA numbers create contractual risk.

#### Section G: Known Limitations

**What to cover:**
- **Scope limitations:** What the system was designed to handle vs. what it should not be used for
- **Input limitations:** Input types, formats, languages, or sizes that may produce poor results
- **Accuracy limitations:** Specific scenarios where accuracy is expected to be lower than the overall target
- **Freshness limitations:** How current the system's knowledge is, what the refresh cycle is
- **Language/locale limitations:** If the system works better in some languages or regions than others
- **Edge cases:** Known scenarios that produce unexpected or suboptimal results
- **Model limitations:** Inherent limitations of the underlying AI model (hallucination potential, reasoning limits, knowledge cutoff)
- **Dependency limitations:** What happens when external dependencies are unavailable

**Tone:** Honest and specific. Vague disclaimers ("AI can sometimes make mistakes") are not helpful. Name the specific limitations.

#### Section H: Glossary

**What to cover:**
- Define every technical term used in the document that a non-AI-specialist might not know
- Keep definitions concise (one to two sentences) and practical (what it means for the client, not a textbook definition)
- Common terms to include (add others as needed):
  - **AI Model**: The software that processes inputs and generates outputs. Think of it as a very sophisticated pattern-matching engine.
  - **Prompt**: The instructions given to the AI model that control its behavior. Similar to a detailed brief given to a human worker.
  - **Hallucination**: When the AI generates information that sounds plausible but is not based on actual data. Like a confident person guessing instead of admitting they do not know.
  - **Embedding**: A numerical representation of text that allows the system to find similar content. Like an index in a textbook, but for meaning rather than keywords.
  - **RAG (Retrieval-Augmented Generation)**: A technique where the AI retrieves relevant documents before generating a response, ensuring answers are grounded in actual data.
  - **Guardrail**: A safety check that validates inputs or outputs to prevent errors, harmful content, or misuse.
  - **Token**: The basic unit of text that AI models process. Roughly equivalent to a word or part of a word. Costs are often measured per token.
  - **Eval / Evaluation Suite**: A set of test cases used to measure the system's accuracy and quality. Like quality assurance tests for AI output.
  - **Baseline**: The reference performance level measured when the system was last verified. Used to detect degradation over time.
  - **Latency**: The time between sending a request and receiving a response.
  - **p50 / p95**: The response time that 50% / 95% of requests complete within. p95 captures the "slow tail" of requests.
  - **Context Window**: The maximum amount of text an AI model can process in a single request. Exceeding it causes failures or truncation.

### Step 3: Write to Disk

**Actions:**
1. Create `.plans/` directory if it does not exist
2. Generate a short kebab-case name from the project or automation (e.g., `acme-support-classifier`, `invoice-pipeline`)
3. Write the full documentation to `.plans/HANDOFF-<name>.md` with this structure:

```markdown
# Client Handoff: <project or automation name>

**Created:** <date>
**Client:** <client name>
**System:** <brief description>
**Version:** <version number or deployment identifier>
**Prepared by:** <team or individual>

---

## Table of Contents

1. System Overview
2. Architecture
3. Monitoring Guide
4. Prompt Modification Guide
5. Escalation Procedures
6. SLA Summary
7. Known Limitations
8. Glossary

---

## 1. System Overview

<Section A content>

## 2. Architecture

<Section B content, including text-based diagram>

## 3. Monitoring Guide

### 3.1 What to Monitor
<organized by importance>

### 3.2 Where to Look
<dashboards, tools, log locations>

### 3.3 Normal vs. Abnormal
<specific thresholds>

### 3.4 Responding to Issues
<first steps for each abnormal signal>

### 3.5 Scheduled Maintenance
<refresh schedules, update process>

## 4. Prompt Modification Guide

### 4.1 Understanding Prompts
<brief explanation>

### 4.2 Modifiable Prompts
<list with safety levels>

### 4.3 Safe Modification Process
<step-by-step>

### 4.4 When to Call for Help
<modifications requiring expert support>

## 5. Escalation Procedures

### 5.1 When to Escalate
<clear triggers>

### 5.2 Contact Information
<tiered contacts>

### 5.3 How to Escalate
<process and information to include>

## 6. SLA Summary

### 6.1 Performance Targets
<accuracy, latency, availability>

### 6.2 Cost Expectations
<cost range and scaling>

### 6.3 Exclusions
<what is not covered>

## 7. Known Limitations

<honest, specific list>

## 8. Glossary

<term definitions>
```

4. Inform the user: "Handoff documentation saved to `.plans/HANDOFF-<name>.md`"

### Step 4: Present Summary

After writing to disk, present a concise summary:

```
## Client Handoff: <name>

**Sections:** 8
**Key contacts documented:** <yes/no — flag if escalation contacts need to be filled in>
**SLA targets documented:** <yes/no — flag if SLA numbers need to be confirmed>
**Prompts catalogued:** <count of prompts documented>
**Known limitations:** <count>

### Sections Requiring Client Review

- <list any sections where placeholder values need to be filled in by the team or client>
- <list any sections where assumptions were made that need validation>

Handoff documentation saved to `.plans/HANDOFF-<name>.md`.
```

### Step 5: Flag Gaps

After writing the document, check for completeness:

1. **Missing escalation contacts**: If contact details could not be determined from the codebase or artifacts, flag them as `[TO BE FILLED]` in the document and note this in the summary
2. **Missing SLA numbers**: If specific thresholds were not found in baselines or cost projections, flag them as `[TO BE CONFIRMED]` and note this
3. **Missing monitoring setup**: If the Monitoring Guide references tools or dashboards that do not appear to be configured, flag this
4. **Missing incident playbook**: If no `PLAYBOOK-*.md` exists for this automation, recommend running `/incident-playbook` before handoff
5. **Missing eval suite**: If no `EVAL-*/` exists, note that the client will not have a way to verify prompt changes until one is created

## Notes

- This skill is language-agnostic and framework-agnostic — it produces client-facing documentation, not code
- Read the actual codebase and all `.plans/` artifacts before writing — the document must accurately reflect what was built, not what was planned
- Write in client language — the audience is technically competent but not AI/ML specialists
- Be honest about limitations — overpromising in the handoff document erodes trust faster than admitting known constraints
- The Glossary should define every technical term used elsewhere in the document — if you use a term, define it
- Placeholder values (`[TO BE FILLED]`, `[TO BE CONFIRMED]`) are expected — not all information can be inferred from code. Flag them clearly rather than inventing values
- The handoff document is a living document — recommend the client review and update it as the system evolves
- If a `/deploy-checklist` exists, reference its findings in the Architecture and Monitoring sections
- If an `/incident-playbook` exists, reference it in the Escalation Procedures and Monitoring Guide
- If `/prompt-version` tracking exists, reference it in the Prompt Modification Guide
- Architecture diagrams should use Mermaid markdown format when possible (widely supported in documentation tools) or ASCII as a fallback
- Keep section lengths proportional to their importance to the client — the Monitoring Guide and Escalation Procedures are usually the most referenced sections post-handoff
