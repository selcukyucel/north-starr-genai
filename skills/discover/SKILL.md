---
name: discover
description: Elicit requirements from a client who has a problem but no PRD. Asks structured questions, identifies actual needs, and generates a PRD draft ready for /decompose.
argument-hint: <problem description or topic area>
---

# Discover — Requirement Elicitation

## Purpose

Help clients articulate what they need when they don't have a PRD. This skill bridges the gap between "I have a problem" and "here's a structured requirements document." It asks the right questions, identifies what the client actually needs (which may differ from what they asked for), and generates a PRD ready for `/decompose`.

Without `/discover`, the pipeline requires a pre-written PRD. With it, North Starr can work with raw problem statements, vague descriptions, or even just a topic area.

## When to Use

- Client describes a problem but has no document
- Client has a brief or rough idea that needs structure
- `/assess` recommended running `/discover` because the requirement lacks detail
- You want to challenge assumptions before investing in decomposition

For clients who already have a detailed PRD, skip directly to `/decompose`.

## Input

The user provides one of:
- **Problem statement** — a description of what they're trying to solve
- **Topic area** — a general domain or capability they want
- **Conversation context** — prior discussion that contains scattered requirements

## Workflow

### Step 1: Understand the Problem Space

Read the input and identify:
- What problem the client is trying to solve
- Who is affected (users, teams, customers)
- What they've tried or considered so far
- Any constraints they've mentioned (budget, timeline, technology)

### Step 2: Ask Structured Questions

Present questions in groups. Do NOT ask all at once — present one group, wait for answers, then present the next group based on what you learned.

**Group 1: The Problem**
1. What specific problem are you trying to solve? (not "what do you want built" — focus on the pain point)
2. Who experiences this problem? (end users, internal team, customers, all of the above)
3. How is this problem handled today? (manual process, existing tool, not handled at all)
4. What happens when this problem isn't solved? (business impact, user frustration, cost)

**Group 2: The Solution Space** (adapt based on Group 1 answers)
5. What does success look like? (specific outcomes, not features)
6. What should the solution definitely NOT do? (scope boundaries)
7. Are there compliance, security, or regulatory requirements?
8. What's the expected scale? (users, documents, transactions per day/month)

**Group 3: Constraints & Context** (adapt based on Groups 1-2)
9. Is there an existing codebase or infrastructure this must integrate with?
10. What's the timeline expectation? (proof of concept by X, production by Y)
11. What's the budget expectation? (monthly operational cost, development investment)
12. Who are the stakeholders and decision-makers?

**Group 4: AI-Specific Questions** (only if the solution likely involves AI)
13. What data sources are available? (documents, databases, APIs, user-generated content)
14. Is there labeled data or examples of correct behavior?
15. What's the acceptable error rate? (must be 99% correct, or 80% is fine for a first pass)
16. Does the output need to be explainable or auditable?
17. Are there human-in-the-loop requirements? (approval flows, escalation)

### Step 3: Identify the Actual Need

After gathering answers, synthesize what the client actually needs. ALWAYS produce the Problem/Solution/Why block below, even when you agree with the client's framing — it confirms alignment.

**Three reframe scenarios:**

**Scenario A — Client described only a problem (no proposed solution):**
Propose a solution type based on the answers. State what you recommend and why.
> Example: Client says "tickets pile up." You say: "Solution: Automation pipeline — classify tickets by department and priority, then auto-route. Why: This addresses the backlog without replacing human agents."

**Scenario B — Client proposed a specific technology (may be premature):**
Challenge whether that technology is the right starting point. Recommend the simplest approach that could work.
- "I need a chatbot" → You need document retrieval with a conversational interface
- "I need AI to classify tickets" → You need an automation pipeline with routing logic
- "I need a multi-agent system" → You need a single agent with tools (simpler, cheaper)
- "I need fine-tuning" → You need better prompts and/or RAG (try simpler approaches first)

**Scenario C — Client described a complex multi-step workflow:**
Validate whether all steps are needed for MVP. Recommend phasing if the workflow has 3+ distinct capabilities.
> Example: Client says "monitor changes, compare policies, flag gaps, generate drafts." You say: "Solution: Phase 1 — monitor + flag gaps (highest value, lowest complexity). Phase 2 — generate draft updates (depends on Phase 1 data). Why: Phasing reduces risk and delivers value sooner."

Present the reframe to the client:

```
Based on our discussion, here's what I understand:

Problem:    <the actual problem, in the client's language>
Solution:   <what I recommend building — be specific about the approach>
Why:        <why this approach — reference simplicity, cost, phasing, or reframe rationale>
```

Wait for confirmation or correction before proceeding.

### Step 4: Run /assess

Once the requirement is clear, run `/assess` internally to classify the project type, estimate complexity, and identify which agents will be needed. Include the assessment results in the PRD.

### Step 5: Generate PRD Draft

Write the PRD to `.plans/PRD-<name>.md`:

```markdown
# PRD: <name>

**Generated:** <date>
**Source:** /discover session
**Status:** DRAFT — awaiting client review

## Problem Statement

<2-3 paragraphs describing the problem, who's affected, current state, and business impact.
Written from the client's perspective, using their language.>

## Success Criteria

<Each criterion MUST include a number or measurable threshold. Derive metrics from the client's answers:
- "too slow" → target response time (e.g., "Average first-response time under 4 hours")
- "too many errors" → target accuracy (e.g., "Classification accuracy above 90%")
- "costs too much" → target cost (e.g., "Reduce per-ticket handling cost by 30%")
- If the client gave no numbers, propose reasonable defaults and flag them as "assumed — confirm with client">
- <criterion 1 — with number or threshold>
- <criterion 2 — with number or threshold>
- <criterion 3 — with number or threshold>

## Solution Overview

<High-level description of what will be built. References the project type from /assess.>

**Project Type:** <from /assess classification>
**Complexity:** <from /assess estimate>

## User Personas

| Persona | Role | Key Workflow | Pain Point |
|---|---|---|---|
| <name> | <role> | <what they do> | <what's broken for them> |

## Requirements

### Must Have (MVP)
- <requirement 1>
- <requirement 2>

### Should Have (Phase 2)
- <requirement 3>

### Could Have (Future)
- <requirement 4>

### Won't Have (Out of Scope)
<Populate from Question 6 answers AND from your own analysis. Include at least one item from each of these sources:
1. Client's explicit exclusions (from "What should the solution definitely NOT do?")
2. Adjacent capabilities that someone might assume are included but aren't (e.g., if building ticket classification, exclude "Won't auto-resolve tickets — human agents still handle responses")
3. Technology scope limits (e.g., "Won't fine-tune a custom model — uses prompt engineering + RAG")
If the client provided no exclusions, propose 2-3 common ones for their project type and flag them as "proposed — confirm with client">
- <excluded item 1>
- <excluded item 2>

## Data Sources

<What data the solution needs access to, format, volume, sensitivity.>

## Constraints

- **Timeline:** <deadline or phase expectations>
- **Budget:** <monthly operational budget, development budget>
- **Compliance:** <regulatory requirements, if any>
- **Integration:** <existing systems that must be integrated>
- **Scale:** <expected usage volume>

## AI-Specific Requirements

<Only if the solution involves AI. From the /assess classification.>

- **Model requirements:** <accuracy, latency, cost targets>
- **Data availability:** <what's available for training/retrieval>
- **Human oversight:** <approval flows, escalation requirements>
- **Explainability:** <audit trail, citation, reasoning transparency>

## Open Questions

<Anything not yet resolved that should be addressed before or during decomposition.>

## Assessment Summary

<Paste the /assess output: project type, agent activation map, risk flags.>
```

### Step 6: Present & Confirm

Present the PRD draft to the client:

```
PRD Generated: .plans/PRD-<name>.md
──────────────────────────────────────
Problem:          <one-line summary>
Solution type:    <project type from /assess>
Complexity:       <S/M/L/XL>
Requirements:     <MUST count> must, <SHOULD count> should, <COULD count> could
Open questions:   <count>

Please review the PRD. I can:
  1. Edit specific sections
  2. Proceed to /decompose (create stories from this PRD)
  3. Save as-is for later
```

Wait for the client's choice.

## Notes

- This skill is conversational — it should feel like an intake meeting, not a form
- Questions adapt based on prior answers — don't ask about AI if the solution is pure automation
- The reframe step (Step 3) is critical — challenge assumptions respectfully
- PRDs generated by /discover are tagged as DRAFT — the client should review before decomposing
- If the client's answers reveal a very simple need, say so: "This is straightforward enough that we don't need a full PRD. Let me create a single story and run /ai-invert on it directly."
- /assess runs internally — the client sees the results in the PRD but doesn't need to invoke it separately
