---
name: guardrail-spec
description: Generate input/output guardrail specifications for an AI automation. Covers PII detection, prompt injection filtering, content safety, confidence thresholds, human escalation, fallback behavior, and audit logging.
---

# Guardrail Spec — Input/Output Guardrail Specification

## Purpose

Generate implementation-ready guardrail specifications for an AI automation. Given a use case, pipeline architecture, and risk profile, this skill produces a structured document covering every layer of defense: input validation, output filtering, human escalation, fallback behavior, and audit logging.

Run this **after** you understand the automation's architecture (e.g., after `/ai-invert` or during planning) and **before** implementation. The output feeds directly into development tasks and code review checklists.

## Pre-flight: Auto-sync Check

Before starting, read the root `CLAUDE.md` (if it exists). If `## How to Approach Tasks` appears AFTER `## Tech Stack` or `## Architecture`, the file has an outdated section order. Silently run `/genai-sync` to fix it before continuing with this skill.

## Input

The user provides a description of the AI automation or feature to guardrail. Can range from a single sentence ("our customer support chatbot") to a detailed pipeline specification. If the automation already exists in the codebase, read it directly.

## Workflow

### Step 1: Understand the Automation

**Actions:**
1. Restate the automation in your own words — confirm understanding with the user
2. Read the codebase to understand what exists today:
   - Prompts and system instructions
   - Model configurations (model name, temperature, max tokens)
   - RAG pipelines (retrieval, embedding, reranking)
   - Existing guardrails, filters, or validation logic
   - Input/output schemas and data flow
3. Check root context files (`CLAUDE.md`, `AGENTS.md`) for architecture, conventions, and module map
4. Check `.plans/` for related artifacts:
   - `INVERT-*.md` — risk analyses that identify guardrail gaps (especially dimension G)
   - `DECISIONS.md` — prior decisions about safety, compliance, or data handling
   - `LEARNINGS.md` — lessons learned from production incidents
   - `GUARDRAILS-*.md` — existing guardrail specs for other components (maintain consistency)
5. Identify all **input channels** (user text, file uploads, API payloads, RAG context, tool outputs)
6. Identify all **output channels** (user-facing responses, API responses, database writes, downstream system calls, logs)
7. **Map the pipeline stages** where guardrails can be placed:
   - **Ingestion** — where raw input enters the system
   - **Pre-processing** — where input is cleaned, formatted, enriched
   - **Before model call** — last checkpoint before data reaches the model API
   - **Model output** — immediately after model response, before post-processing
   - **Post-processing** — where output is formatted, filtered, enriched
   - **Before delivery** — last checkpoint before output reaches the user or downstream system
   - **Cross-cutting** — logging, monitoring, rate limiting that span all stages

   In Steps 3-4, assign each guardrail to the pipeline stage where it should execute. This ensures the `guardrails-designer` agent can validate coverage per stage, not just per category.

### Step 2: Classify Risk Level

Assess the automation across four dimensions to determine the overall risk tier. The risk tier drives the strictness of guardrails specified in later steps.

| Dimension | LOW | MEDIUM | HIGH |
|-----------|-----|--------|------|
| **Data sensitivity** | Public data only | Internal data, non-sensitive PII (names, emails) | Protected PII (SSN, medical, financial), trade secrets |
| **Output visibility** | Internal tools, developer-facing | Internal but cross-team, back-office | Client-facing, public-facing, regulatory submissions |
| **Autonomy level** | Human reviews every output | Human reviews samples or exceptions | Fully automated, no human in loop |
| **Regulatory exposure** | No specific regulations | Industry best practices apply | GDPR, HIPAA, SOC2, FINRA, or similar mandate |

**Scoring:**
- If ANY dimension is HIGH, overall risk is **HIGH**
- If two or more dimensions are MEDIUM, overall risk is **HIGH**
- If one dimension is MEDIUM and rest are LOW, overall risk is **MEDIUM**
- If all dimensions are LOW, overall risk is **LOW**

Record the classification — it determines minimum guardrail requirements in subsequent steps.

### Step 3: Specify Input Guardrails

For **each input channel** identified in Step 1, specify the following. Skip categories that genuinely do not apply, but err on the side of inclusion.

#### 3a. PII Detection

| Setting | Specification |
|---------|--------------|
| PII types to scan | List specific types: names, emails, phone numbers, SSNs, credit cards, addresses, dates of birth, medical record numbers, etc. Also check for **secrets**: API keys, access tokens, passwords, connection strings, private keys, AWS credentials — these are distinct from PII but equally sensitive. |
| Detection method | Regex patterns, NER model, third-party API (e.g., Presidio, AWS Comprehend), or combination |
| Action on detection | **Redact** (replace with placeholder, pass to model), **Reject** (block request, return error), or **Flag** (allow but log for review) |
| Redaction format | e.g., `[REDACTED-EMAIL]`, `[REDACTED-SSN]`, `***-**-1234` (last 4 visible) |
| Exceptions | Scenarios where PII is expected and permitted (e.g., user profile updates) |

**Minimum by risk tier:**
- LOW: Flag known PII patterns in logs
- MEDIUM: Redact PII before sending to external model APIs
- HIGH: Redact PII at ingestion, reject if redaction is ambiguous, log all detections

#### 3b. Prompt Injection Filtering

| Setting | Specification |
|---------|--------------|
| Detection approach | Pattern matching (known injection phrases), classifier model, input/output consistency check, or layered defense |
| Known patterns to block | "Ignore previous instructions," "You are now," role-switching attempts, encoded instructions (base64, ROT13), delimiter escaping |
| Blocking behavior | **Block** (reject request with generic error), **Sanitize** (strip detected injection, proceed), or **Flag** (allow but alert) |
| Canary tokens | Whether to embed canary strings in system prompts to detect leakage |
| Severity response | What to do on repeated injection attempts from same user/session |

**Minimum by risk tier:**
- LOW: Log suspicious patterns, no blocking
- MEDIUM: Block known injection patterns, log all attempts
- HIGH: Layered detection (pattern + classifier), block and alert on all attempts, rate-limit offending sessions

#### 3c. Input Validation

| Setting | Specification |
|---------|--------------|
| Format validation | Expected input format (plain text, JSON schema, file type) and rejection behavior for malformed input |
| Length limits | Minimum and maximum character/token counts per input field |
| Character set | Allowed character sets, handling of special characters, Unicode normalization |
| Schema validation | For structured inputs: JSON Schema, required fields, type checking |
| File validation | For file uploads: allowed MIME types, max file size, virus scanning |

#### 3d. Rate Limiting

| Setting | Specification |
|---------|--------------|
| Per-user limit | Requests per minute/hour per authenticated user |
| Per-endpoint limit | Requests per minute/hour per API endpoint |
| Per-session limit | Requests per conversation session (for chat interfaces) |
| Burst allowance | Short-term burst above sustained rate |
| Exceeded behavior | 429 response, queue with delay, or degrade to cached/static response |

### Step 4: Specify Output Guardrails

For **each output channel** identified in Step 1, specify the following.

#### 4a. Content Filtering

| Setting | Specification |
|---------|--------------|
| Blocked topics | List specific topics the model must never produce output about (e.g., competitor recommendations, legal advice, medical diagnoses) |
| Toxicity threshold | Toxicity score threshold for blocking (e.g., > 0.7 on Perspective API) and which categories to check (profanity, harassment, threats, sexual content) |
| Brand safety | Output patterns to avoid (competitor names, off-brand language, unauthorized commitments or promises) |
| Detection method | Model provider content filter, post-processing classifier, keyword blocklist, or combination |
| Action on detection | **Block** (suppress output, show fallback), **Rewrite** (auto-correct and serve), or **Flag** (serve but log for review) |

#### 4b. Format Validation

| Setting | Specification |
|---------|--------------|
| Schema compliance | Expected output schema (JSON Schema, XML DTD, or structural description) |
| Required fields | Fields that must always be present in the output |
| Field constraints | Value ranges, enum values, string patterns for each field |
| Retry on failure | Whether to retry the model call if output fails validation, max retries |
| Fallback on persistent failure | What to return if output fails validation after all retries |

#### 4c. Confidence Thresholds

| Setting | Specification |
|---------|--------------|
| Confidence source | How confidence is measured: model logprobs, calibrated classifier score, self-assessment prompt, consistency across multiple calls |
| Serve threshold | Minimum confidence to serve output directly (e.g., > 0.85) |
| Review threshold | Confidence range that triggers human review before serving (e.g., 0.60 - 0.85) |
| Reject threshold | Confidence below which output is not served at all (e.g., < 0.60) |
| Display to user | Whether to show confidence indicators to the end user |

**Minimum by risk tier:**
- LOW: Log confidence scores, no threshold enforcement
- MEDIUM: Enforce serve/reject thresholds, flag review-range outputs
- HIGH: Enforce all three thresholds, human review for review-range, display uncertainty to user

#### 4d. Citation and Source Requirements

| Setting | Specification |
|---------|--------------|
| Citation required | Whether outputs must cite source documents |
| Citation format | How citations appear (inline links, footnotes, reference list) |
| Source verification | Whether to verify cited sources exist and support the claim |
| Missing source behavior | What to do if the model asserts a fact without a retrievable source |
| Attribution display | How source attribution is presented to the user |

#### 4e. Relevance Check

| Setting | Specification |
|---------|--------------|
| Relevance method | Embedding similarity between query and response, LLM-as-judge relevance score, or topic classifier |
| Threshold | Minimum relevance score to serve (e.g., > 0.6 cosine similarity between query and response embeddings) |
| Off-topic behavior | **Flag** (serve but log for review), **Redirect** (ask user to rephrase), or **Block** (suppress and show fallback) |

Skip if the automation has no free-form user queries (e.g., fixed-input classification pipelines).

#### 4f. Bias Detection

| Setting | Specification |
|---------|--------------|
| Bias categories | Demographic groups to check: gender, race/ethnicity, age, disability, religion, nationality, socioeconomic status |
| Detection method | Post-processing classifier (e.g., Regard, HolisticBias), LLM-as-judge with bias rubric, or statistical comparison across demographic variants of the same query |
| Scope | Which output fields or sections to scan (e.g., recommendations, descriptions, rankings — not raw data lookups) |
| Action on detection | **Block** (suppress output, show fallback), **Rewrite** (neutralize and serve), or **Flag** (serve but log and queue for review) |
| Testing approach | Generate demographic-variant input pairs (same query with different names/pronouns/contexts) and compare output consistency |

**Minimum by risk tier:**
- LOW: No active scanning — address bias reactively if reported
- MEDIUM: Flag outputs that score above bias threshold, review monthly sample
- HIGH: Active scanning on all outputs, block biased content, human review queue

#### 4g. Generated Code Security (if the automation produces code)

| Setting | Specification |
|---------|--------------|
| Vulnerability scan | Check generated code for: SQL injection, XSS, command injection, path traversal, hardcoded credentials, insecure deserialization |
| Detection method | Static analysis rules (regex patterns for known dangerous patterns), AST-based linting, or security-focused LLM review |
| Language coverage | Which languages the scanner supports (must match what the model generates) |
| Action on detection | **Block** (suppress code, explain the vulnerability), **Annotate** (serve with inline security warnings), or **Fix** (auto-remediate and serve corrected version) |

Skip if the automation never generates executable code.

#### 4h. Hallucination Checks

| Setting | Specification |
|---------|--------------|
| Known-fact verification | Cross-check model claims against structured data or knowledge base |
| Consistency checks | Compare output against retrieved context — flag contradictions |
| Self-consistency | Run multiple generations, flag outputs that diverge across runs |
| Numeric verification | Cross-check numbers, dates, and calculations against source data |
| Entity verification | Verify named entities (people, companies, products) exist and are correctly attributed |

### Step 5: Define Human Escalation Triggers

Specify conditions under which the automation routes to a human. For each trigger, define detection, routing, and SLA.

| Trigger | Detection Method | Routing | SLA |
|---------|-----------------|---------|-----|
| **Low confidence output** | Confidence below review threshold (Step 4c) | Route to [role] via [channel] | [time to review] |
| **Sensitive topic detected** | Topic classifier or keyword match on [topics] | Route to [role] via [channel] | [time to review] |
| **Novel input pattern** | Input falls outside training/eval distribution (embedding distance, anomaly score) | Route to [role] via [channel] | [time to review] |
| **High-stakes decision** | Output involves [financial threshold, legal commitment, irreversible action] | Route to [role] via [channel] | [time to review] |
| **Multiple guardrails triggered** | Two or more guardrails fire on the same request | Route to [role] via [channel] | [time to review] |
| **User escalation request** | User explicitly asks for human help | Route to [role] via [channel] | [time to review] |
| **Repeated failures** | Same user hits [N] guardrail triggers in [time window] | Route to [role] via [channel] | [time to review] |

**Escalation queue requirements:**
- Queue visibility: who can see pending escalations
- Priority ordering: how escalations are ranked
- Timeout behavior: what happens if no human responds within SLA
- Context passed to human: full conversation, guardrail trigger details, confidence scores, suggested response

### Step 6: Define Fallback Behavior

For **each guardrail** specified in Steps 3-5, define what happens when it triggers. Every guardrail must have a defined fallback — silent failures are not acceptable.

| Guardrail | User Experience | Internal Action | Retry? |
|-----------|----------------|-----------------|--------|
| PII detected in input | [message shown to user] | [log event, alert] | [yes/no, with what change] |
| Prompt injection detected | [message shown to user] | [log event, alert, rate-limit] | [no] |
| Input validation failure | [message shown to user with guidance] | [log event] | [yes, after user corrects] |
| Rate limit exceeded | [message with retry-after] | [log event] | [yes, after cooldown] |
| Content filter triggered | [generic safe response or redirect] | [log event, flag for review] | [yes, with modified prompt] |
| Format validation failure | [fallback formatted response] | [log event, alert if persistent] | [yes, up to N times] |
| Low confidence | [qualified response with caveats or redirect to human] | [log event, queue for review] | [yes, with additional context] |
| Hallucination detected | [response withheld, user informed] | [log event, alert] | [yes, with fact-checking prompt] |
| Human escalation | [acknowledgment, ETA for human response] | [create escalation ticket] | [N/A — waiting for human] |

**Fallback message guidelines:**
- Never reveal internal guardrail logic or thresholds to the user
- Never blame the user — frame as "I want to make sure I give you accurate information"
- Provide actionable next steps (rephrase, contact support, try again later)
- Maintain brand voice and tone even in error states

### Step 6b: Estimate False Positive Impact

For each guardrail, estimate what legitimate inputs it might wrongly block or flag:

| Guardrail | False Positive Risk | Example | Mitigation |
|-----------|-------------------|---------|------------|
| PII detection | MEDIUM | Names like "John" in support tickets wrongly flagged as PII | Use entity-aware PII detection, not just pattern matching |
| Injection filter | LOW-MEDIUM | Legitimate questions containing "ignore" or "instructions" wrongly blocked | Require injection patterns to be instruction-shaped, not just keyword matches |
| Content filter | LOW | Technical discussions about security topics flagged as harmful | Whitelist domain-specific technical vocabulary |
| Rate limiting | LOW | Power users during peak hours hit limits | Set limits based on actual usage distribution, not arbitrary thresholds |

**Why this matters:** A guardrail that blocks 5% of legitimate requests creates user frustration and erodes trust in the system. High false-positive guardrails need tuning or a softer action (flag instead of block).

### Step 7: Specify Audit Logging

Define what gets logged, how, and who can access it.

#### What to Log

| Event | Fields to Capture | Sensitivity |
|-------|------------------|-------------|
| Every request | Request ID, timestamp, user ID (hashed if needed), session ID, input channel | LOW |
| Every response | Request ID, timestamp, output channel, confidence score, latency | LOW |
| Guardrail trigger | Request ID, guardrail name, trigger reason, action taken, input snippet (redacted) | MEDIUM |
| Human escalation | Request ID, escalation reason, assigned reviewer, resolution, resolution time | MEDIUM |
| PII detection | Request ID, PII types found, action taken (DO NOT log the PII itself) | HIGH |
| Prompt injection attempt | Request ID, detection method, input pattern (sanitized), action taken | HIGH |
| Configuration change | Who changed what, old value, new value, timestamp | HIGH |

#### Log Format and Storage

| Setting | Specification |
|---------|--------------|
| Format | Structured JSON, one event per line |
| Storage | [Where logs are stored — cloud logging service, database, file system] |
| Retention | [Duration by sensitivity: LOW = 90 days, MEDIUM = 1 year, HIGH = 3 years, or per regulation] |
| Encryption | [At rest and in transit requirements] |
| Access control | [Who can read logs by sensitivity level — engineers, compliance, legal] |
| PII in logs | **Never log raw PII** — log redacted versions or detection metadata only |
| Alerting | [Which events trigger real-time alerts and to whom] |

#### Compliance-Specific Requirements

- **GDPR**: Right to deletion must extend to logs — document how user data is purged
- **HIPAA**: PHI must never appear in logs, even in error messages
- **SOC2**: Log access itself must be logged (audit of audits)
- **Industry-specific**: List any additional regulatory logging requirements

### Step 8: Write to Disk

**Actions:**
1. Create `.plans/` directory if it doesn't exist
2. Generate a short kebab-case name from the automation (e.g., `support-chatbot`, `document-classifier`, `rag-pipeline`)
3. Write the full specification to `.plans/GUARDRAILS-<name>.md` with this structure:

```markdown
# Guardrail Specification: <automation name>

**Created:** <date>
**Risk Level:** <LOW / MEDIUM / HIGH>
**Automation:** <brief description>
**Input Channels:** <list>
**Output Channels:** <list>

## Risk Classification

| Dimension | Level | Rationale |
|-----------|-------|-----------|
| Data sensitivity | <L/M/H> | <why> |
| Output visibility | <L/M/H> | <why> |
| Autonomy level | <L/M/H> | <why> |
| Regulatory exposure | <L/M/H> | <why> |
| **Overall** | **<L/M/H>** | |

## Input Guardrails

### <Input Channel 1>
<PII detection, injection filtering, validation, rate limiting specs>

### <Input Channel 2>
<...>

## Output Guardrails

### <Output Channel 1>
<Content filtering, format validation, confidence, citations, hallucination checks>

### <Output Channel 2>
<...>

## Human Escalation Triggers

<Trigger table from Step 5>

## Fallback Behavior

<Fallback table from Step 6>

## Audit Logging

<Logging specs from Step 7>

## Implementation Checklist

Each guardrail includes a testable acceptance criterion so `guardrails-designer` can verify it:

| # | Guardrail | Pipeline Stage | Priority | Acceptance Test |
|---|-----------|---------------|----------|-----------------|
| 1 | <guardrail name> | <stage> | P0/P1/P2 | <specific test: "Send input containing SSN pattern → verify output contains [REDACTED-SSN], original SSN not in model API call or logs"> |
| 2 | <guardrail name> | <stage> | P0/P1/P2 | <specific test: "Send 'Ignore previous instructions' in ticket body → verify classification still correct, injection logged"> |

**Every guardrail must have an acceptance test** — a concrete input, expected behavior, and pass condition. Without this, `guardrails-designer` can't validate the implementation.

## Coverage Map (by pipeline stage)

| Pipeline Stage | Guardrails | Status |
|---------------|-----------|--------|
| Ingestion | <list: input validation, PII/secrets detection> | Covered / Gaps |
| Pre-processing | <list> | Covered / Gaps |
| Before model call | <list: injection defense, final PII check> | Covered / Gaps |
| Model output | <list: format validation, hallucination check, relevance check> | Covered / Gaps |
| Post-processing | <list: content filtering, bias detection, confidence thresholds, code security> | Covered / Gaps |
| Before delivery | <list: human escalation triggers> | Covered / Gaps |
| Cross-cutting | <list: audit logging, rate limiting, monitoring> | Covered / Gaps |

**Unprotected stages** (no guardrails specified) are highlighted as gaps requiring attention.
```

4. Inform the user: "Guardrail spec saved to `.plans/GUARDRAILS-<name>.md`"

### Step 9: Present Summary

After writing to disk, present a concise summary:

```
## Guardrail Specification: <name>

**Risk Level:** <LOW / MEDIUM / HIGH>
**Total Guardrails Specified:** <count>

### Coverage Map

| Layer | Count | Status |
|-------|-------|--------|
| Input validation | <N> | <Covered / Gaps exist> |
| PII/secrets protection | <N> | <Covered / Gaps exist> |
| Injection defense | <N> | <Covered / Gaps exist> |
| Content safety | <N> | <Covered / Gaps exist> |
| Relevance/quality | <N> | <Covered / Gaps exist> |
| Bias detection | <N> | <Covered / Gaps exist> |
| Code security | <N> | <Covered / Gaps exist> |
| Confidence/quality | <N> | <Covered / Gaps exist> |
| Human escalation | <N> | <Covered / Gaps exist> |
| Audit logging | <N> | <Covered / Gaps exist> |

### Implementation Priority

**P0 (before launch):**
- <guardrail>

**P1 (within first sprint post-launch):**
- <guardrail>

**P2 (hardening):**
- <guardrail>

Spec saved to `.plans/GUARDRAILS-<name>.md`.
```

If the risk level is HIGH, add:

> "Risk level is HIGH. Recommend running `/ai-invert` if not already done, and spawning the `genai-layoutplan` agent to break guardrail implementation into tracked tasks."

## Notes

- This skill is language-agnostic and framework-agnostic — it produces specifications, not code
- Read actual code, prompts, and pipeline configs before specifying guardrails — never spec based on assumptions alone
- Maintain consistency with existing guardrail specs in `.plans/GUARDRAILS-*.md` — reuse patterns, detection methods, and thresholds where appropriate
- The risk classification in Step 2 sets minimum requirements, but you can always specify stricter guardrails
- Every guardrail must have a defined fallback behavior — "block and log" is acceptable, "silently drop" is not
- PII must never appear in logs, error messages, or alert payloads — log detection metadata only
- If an `/ai-invert` analysis exists (especially dimension G — Guardrail & Compliance), use its findings as input to this spec
- The output of this skill feeds into implementation planning — each guardrail becomes a trackable task
- For existing systems, check what guardrails are already implemented before specifying new ones — avoid duplicating logic
- Guardrail thresholds should be configurable (not hardcoded) so they can be tuned in production without redeployment
