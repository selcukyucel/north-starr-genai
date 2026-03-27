# Changelog

All notable changes to north-starr-genai will be documented in this file.

## [0.10.0] — 2026-03-27

### Overview

First release of North Starr GenAI — an agentic AI development workflow framework for teams building AI automations. All 4 phases implemented and optimized via autoimprove (49 improvements, 0 reverts).

### Skills (21 total)

#### New AI Skills
- `/ai-invert` — AI-specific deep inversion analysis (10 dimensions: prompt fragility, hallucination, cost, drift, data pipeline, compliance). Classifies risks as NEW/PRE-EXISTING/AMPLIFIED, cites specific files, per-risk eval strategy.
- `/baseline` — Capture AI system performance before changes. Specific measurement methods, regression thresholds, reproduction steps, prior baseline comparison.
- `/cost-estimate` — Token cost projection at 1x/10x/100x scale. Per-component breakdown, cost delta for pipeline changes, model comparison.
- `/eval-suite` — Generate evaluation datasets from requirements. Golden examples, tailored adversarial inputs, boundary cases, regression anchors with match types, scoring rubrics.
- `/prompt-test` — Single-run prompt evaluation. Consumes eval handoffs, non-deterministic handling (3 runs), regression highlighting with deltas, failure-pattern-specific fix suggestions.
- `/guardrail-spec` — Generate guardrail specifications scoped to pipeline stages. False positive estimation, testable acceptance criteria per guardrail, risk-tiered minimums.
- `/orchestrate` — Start the multi-story pipeline. Budget preview, resume from prior session, operational commands for active pipelines.
- `/deploy-checklist` — Pre-deployment verification. Risk mitigation mapping from /ai-invert, staging/production diff table, alert routing verification.
- `/incident-playbook` — AI failure runbooks for 9 incident categories. Escalation chains, time-to-detect estimates, blast radius per severity, runnable detection commands.
- `/handoff-doc` — Client-facing documentation. Monitoring ranges from baselines, SLA numbers from artifacts, prompt safety levels with rationale, gap flagging.
- `/prompt-version` — Prompt version tracking with diffs, scores, rollback, and changelog.

#### Extended Skills (from North Starr)
- `/bootstrap` — AI stack detection, AI-specific patterns/landmines, AI architecture guidance, installs all 14 agents, `NORTH-STARR-GENAI:` managed sections
- `/learn` — AI-specific auto-triggers (prompt regression, model quirks, cost optimization, eval thresholds, guardrail gaps, hallucination patterns, data pipeline quirks)
- `/sync` — `NORTH-STARR-GENAI:` marker prefix, v2.0 AI complexity gate with 5-phase workflow

#### Inherited Skills (from North Starr, unchanged)
- `/invert`, `/decompose`, `/generate-commit`, `/generate-pr`, `/analyze-code`, `/report-weekly`, `/autoimprove`

### Agents (14 total)

#### Planning & Decomposition
- `layoutplan` — Extended: reads ADRs, cost envelopes, DECISIONS.md, LEARNINGS.md
- `storymap` — Inherited from North Starr
- `chief-ai-po` — 3 modes: decompose, refine (TRIAGE), incorporate-feedback (REWORK)

#### Orchestration
- `orchestrator` — Pipeline state machine (TRIAGE→DESIGN→PLAN→BUILD→HARDEN→DELIVER), feedback loops, conflict detection, dual human-in-the-loop, SLA enforcement
- `ai-architect` — Technical design, model selection, ADRs, cost envelopes
- `cost-estimator` — Estimation mode (DESIGN phase) + analysis mode (standalone)

#### Build Specialists
- `prompt-engineer` — Prompt design with eval handoff, design rationale, versioning
- `rag-advisor` — RAG pipeline design (chunking, embeddings, retrieval, re-ranking)
- `integration-planner` — External system integration (API contracts, retry strategies)

#### Validation
- `eval-designer` — Eval suite execution. Consumes prompt-engineer handoff, statistical noise awareness, actual model outputs in feedback.
- `guardrails-designer` — Safety validation. Delegates injection testing to prompt-adversary, project-specific PII, pipeline-stage coverage map, blast radius in failures.
- `prompt-adversary` — Red-teaming. Targeted weakness per attack, multi-step chained attacks, implementation-specific recommendations, structured output for guardrails-designer.
- `ai-ops` — Monitoring, alerting, drift detection configuration

#### Delivery
- `demo-builder` — Client delivery packaging, UAT instructions, acceptance gate

### Templates
- AI Complexity Gate v2.0 (Q0-Q4) with 5-phase workflow: ASSESS → BUILD (auto-spawn specialists) → HARDEN (auto-spawn validators) → COMPLETE → LEARN
- AI Auto-Learn triggers (7 AI-specific signals)
- Extended pattern/landmine templates with Model Compatibility, Cost Impact, Eval Criteria, Blast Radius, Detection Lag, Client Impact fields

### Infrastructure
- CLI: `bin/north-starr-genai` v0.10.0 (init, update, status, cache-update)
- Homebrew: `Formula/north-starr-genai.rb`
- Claude Code plugin: `.claude-plugin/marketplace.json`
- CI: release.yml (auto-update SHA/version on tag), validate.yml (frontmatter + path validation)

### Autoimprove Results

49 improvements applied across 16 targets, 0 reverted:

| Target | Before | After |
|--------|--------|-------|
| `/bootstrap` | 83% | 100% |
| `/ai-invert` | 33% | 100% |
| `/baseline` | 0% | 100% |
| `prompt-engineer` | 67% | 100% |
| `eval-designer` | 50% | 100% |
| `/eval-suite` | 50% | 100% |
| `guardrails-designer` | 17% | 100% |
| `/guardrail-spec` | 50% | 100% |
| `prompt-adversary` | 33% | 100% |
| `/orchestrate` | 83% | 100% |
| `orchestrator` | 100% | 100% |
| `/cost-estimate` | 67% | 100% |
| `/deploy-checklist` | 50% | 100% |
| `/incident-playbook` | 17% | 100% |
| `/handoff-doc` | 50% | 100% |
| `/prompt-test` | 33% | 100% |
