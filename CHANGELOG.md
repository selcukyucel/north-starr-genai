# Changelog

All notable changes to north-starr-genai will be documented in this file.

## [0.15.0] — 2026-04-16

### Overview

Enforcement release. North Starr GenAI becomes fully agentic: delegation is mandatory (not advisory), specialist agents MUST cross-consult peers, and routing hooks fire automatically on every prompt and AI-artifact write. Closes the root cause of siloed specialist reports seen in `.docs/reports/` — where each agent acted in isolation and missed peer context (ai-architect skipped cost-estimator's tier routing proposal, guardrails-designer ignored cost of remediations, integration-planner filed 26 risks with no ownership, etc.).

### Three New Agents

- **`ai-invert-analyst`** — Promoted from the `/ai-invert` skill. Runs the 10-dimension AI risk inversion on a separate thread and produces `.plans/INVERT-<name>.md`.
- **`baseline-capturer`** — Promoted from the `/baseline` skill. Captures reproducible performance snapshots with exact re-run commands before any change.
- **`auto-improver`** — Promoted from the `/autoimprove` skill. Hill-climbing prompt optimization (one small change per round, keep wins, revert regressions) on a separate thread.

The `/ai-invert`, `/baseline`, and `/autoimprove` skills remain as thin dispatchers that spawn the new agents — matching the existing `/decompose → genai-storymap` pattern.

### Plugin-Level Routing Hooks (Claude Code)

Two hooks now ship with the plugin via `.claude-plugin/plugin.json` and `${CLAUDE_PLUGIN_ROOT}/hooks/`:

- **`UserPromptSubmit` hook** — Scans every prompt for AI keywords (prompt, eval, RAG, guardrail, cost, model, injection, drift, observability, integration, adversarial, etc.). When matched, injects a Routing Directive naming the required specialist agents. Fast-path prompts produce no output.
- **`PreToolUse` hook** — Fires on `Write`/`Edit`/`NotebookEdit` targeting specialist-owned `.plans/` paths (`PROMPTS-*`, `RAG-*`, `EVAL-*`, `COST-*`, `ADR-*`, `GUARDRAILS-*`, `INTEGRATION-*`, `OPS-*`, `INVERT-*`, `BASELINE-*`, etc.). Injects a reminder to delegate to the owning specialist.

Hooks auto-register on plugin install. VS Code Copilot has no hook equivalent — the same policy travels via the managed `Delegation Policy` section in `AGENTS.md`.

### Delegation Policy (MANDATORY — managed section v3.0)

The `How to Approach Tasks` managed section in `CLAUDE.md` / `AGENTS.md` is bumped to **v3.0**:

- Q0–Q4 gates are now MUST, not advisory.
- New `## Delegation Policy (MUST)` table maps 14 AI domains → specialist agents → owned `.plans/` paths.
- The main conversation MUST invoke the specialist via the Agent tool, cite its output path in a `Cross-Consult Log`, and NOT write to its owned `.plans/` directory directly.
- Existing exceptions preserved: true fast-path, user says "handle it yourself", specialist writing its own file.

### Cross-Consultation (MANDATORY)

Every specialist agent now has `## Required Peer Consultations (MUST)` and a `## Cross-Consult Log` section in its output template:

- `ai-architect` — cite `cost-estimator` (tier proposal — accept or reject explicitly), `eval-designer` (baseline), `ai-invert-analyst` (risks)
- `cost-estimator` — MUST emit a Model-Tier Routing Proposal; cross-consult `ai-ops`, `integration-planner`
- `prompt-engineer` — cite `guardrails-designer` (injection), `eval-designer` (baseline/Eval Handoff), `rag-advisor` (Context Injection Contract)
- `eval-designer` — cite `baseline-capturer`, `prompt-engineer` (Eval Handoff), `guardrails-designer`
- `guardrails-designer` — cite `cost-estimator` (remediation cost impact), `prompt-adversary`, `ai-ops` (audit logging)
- `ai-ops` — cite `integration-planner` (health checks), `cost-estimator` (observability cost), `guardrails-designer` (audit fields), `eval-designer` (drift baseline)
- `integration-planner` — MUST emit Ownership Assignment table; cross-consult `guardrails-designer`, `ai-ops`, `cost-estimator`
- `prompt-adversary` — MUST tag findings `[PROMPT-LEVEL]` / `[SYSTEM-LEVEL]` / `[GUARDRAIL-LEVEL]`; cross-consult `guardrails-designer`, `ai-architect`

Missing Cross-Consult Log → orchestrator routes back for rework at HARDEN → DELIVER.

### Orchestrator Updates

- HARDEN → DELIVER now requires a populated Cross-Consult Log on every BUILD artifact.
- HARDEN → REWORK fires on missing log (routes back to the producing specialist).
- New **peer-consult 1h SLA**: if a specialist waits on another specialist's input for longer than 1h, orchestrator auto-dispatches the consulted agent rather than stalling the requester.

### Migration

**Breaking changes:** None. Existing agent input/output contracts are preserved; new sections are additive. The fast-path exception is preserved for trivial changes.

**Claude Code plugin users (Option A):**

```
/plugin marketplace update selcukyucel/north-starr-genai
/plugin install north-starr-genai
north-starr-genai cache-update
# restart Claude Code
# then, in each existing project:
/genai-sync         # updates CLAUDE.md managed section v2.0 → v3.0
```

The marketplace version bump triggers cache refresh; plugin reinstall picks up the 3 new agents, the 8 updated specialists, and the new hooks (which auto-register). `/genai-sync` detects the v2.0 → v3.0 version tag in the managed section and replaces it with the new Delegation Policy content.

**Homebrew + VS Code Copilot users (Option B + C):**

```bash
brew update && brew upgrade north-starr-genai
cd <your-project>
north-starr-genai update
```

`north-starr-genai update` copies the 3 new agent files into `.github/agents/` (via glob), replays the 8 updated specialists, and re-injects the v3.0 managed section into `AGENTS.md`.

**New users:** `/plugin install north-starr-genai` (Option A) or `brew install` + `north-starr-genai init` (Option B+C) provisions the full v3.0 setup on first use.

### Files Changed

- 3 new agents (`agents/`) + 3 new Claude templates + 3 new Copilot templates
- 8 modified specialist agents + 8 modified Claude templates + 8 modified Copilot templates
- 1 modified orchestrator (cross-consult precondition + 1h peer-consult SLA + 16th rule)
- 2 new hook scripts (`hooks/`)
- 1 new plugin manifest (`.claude-plugin/plugin.json`) registering hooks with `${CLAUDE_PLUGIN_ROOT}`
- 1 new dev-only `.claude/settings.json` (permissions for this repo's own Claude Code sessions)
- 3 thin-dispatcher skills (`ai-invert`, `baseline`, `autoimprove`)
- 2 modified canonical sources (`skills/genai-sync/SKILL.md` both variants v2.0 → v3.0, `skills/genai-bootstrap/SKILL.md` new Analysis agents category)
- 2 modified top-level templates (`templates/CLAUDE.md`, `templates/AGENTS.md` → v3.0)

---

## [0.14.0] — 2026-04-06

### Overview

Rename `/sync` skill to `/genai-sync` to avoid namespace collision with North Starr's `/sync` skill. All cross-references across skills, CLI, rules, and documentation updated.

### Breaking Changes

- **Skill renamed:** `/sync` → `/genai-sync`

### Migration

Run `/genai-sync` in consuming projects after updating to v0.14.0.

---

## [0.13.0] — 2026-04-06

### Overview

Rename conflicting skills and agents to avoid namespace collisions with North Starr. Skills `bootstrap` → `genai-bootstrap`, `invert` → `genai-invert`. Agents `layoutplan` → `genai-layoutplan`, `storymap` → `genai-storymap`. All cross-references, templates, CLI, CI, and documentation updated.

### Breaking Changes

- **Skill renamed:** `/bootstrap` → `/genai-bootstrap`
- **Skill renamed:** `/invert` → `/genai-invert`
- **Agent renamed:** `layoutplan` → `genai-layoutplan`
- **Agent renamed:** `storymap` → `genai-storymap`

### Migration

Run `/genai-sync` in consuming projects after updating to v0.13.0. The sync skill will replace old agent files with the renamed versions. If you have custom references to the old names in project-specific sections of CLAUDE.md or AGENTS.md, update them manually.

---

## [0.12.0] — 2026-04-06

### Overview

RAG, security, evaluation, and observability enrichment release. Adds 1 new skill, enriches 6 agents and 3 skills with production RAG techniques, security guardrail categories, human annotation workflows, and tracing instrumentation design. Closes gaps identified from RAG optimization research, LLM Guard security patterns, and LangFuse evaluation workflows.

### New Skill (1)

- **`/ai-test`** — Generate executable pytest files for deterministic AI outputs. Produces assertion-based tests for classification, extraction, routing, and structured output components. Complements `/eval-suite` (statistical evaluation for non-deterministic outputs) with hard-assertion tests that run in CI/CD. Supports converting eval suite golden examples into pytest code, fixture file generation, and conftest.py scaffolding.

### RAG Advisor Enrichments

- **Data ingestion pipeline** — Added to deployed agent (was only in template). Covers source connectors, parsing (PDF/HTML/DOCX), cleaning, de-duplication, quality validation, metadata extraction, staleness/refresh strategy, access control, and data quality monitoring. Parsing quality is the #1 silent RAG failure.
- **Multimodal input handling** — Added to deployed agent. Covers PDFs with text/images/charts, table extraction as structured data, scanned document OCR, image descriptions via vision models, and quality checks (OCR confidence, table structure validation).
- **Contextual retrieval** — New chunking enhancement. Pre-embedding context enrichment using a cheap LLM to situate each chunk within its source document before embedding. Anthropic reports up to 49% retrieval failure reduction when combined with BM25. Includes when-to-use decision table, cost estimate (~$1-5 per 10K chunks), and starting defaults.
- **Self-query** — New retrieval technique. LLM-powered metadata filter extraction from natural language queries. Decomposes queries into semantic search + structured filters using a Pydantic schema. Includes when-to-use table, fallback on low confidence, and cost estimate (<$0.001/query).

### Security Guardrail Enrichments

- **Secrets detection** — PII detection scope expanded to include API keys, access tokens, passwords, connection strings, and private keys as a distinct category alongside traditional PII.
- **Bias detection** (new guardrail 4f) — Output scanning for demographic bias across gender, race/ethnicity, age, disability, religion, nationality. Detection via post-processing classifier, LLM-as-judge, or demographic-variant input comparison. Risk-tiered minimums.
- **Output relevance check** (new guardrail 4e) — Verify AI responses stay on-topic. Embedding similarity, LLM-as-judge, or topic classifier methods.
- **Generated code security** (new guardrail 4g) — Scan AI-generated code for SQL injection, XSS, command injection, path traversal, hardcoded credentials. Static analysis or security-focused LLM review.
- **guardrails-designer** updated with test sections for all new guardrail types and expanded coverage map template.

### Evaluation Enrichments

- **Human annotation workflow** — eval-designer now includes Step 3b for determining AI vs human scoring method per rubric criterion. Guidance on annotation guidelines, inter-annotator agreement (80% minimum), calibration sets, and mixed AI+human scoring on the same eval run.
- **eval-suite** rubric criteria now tagged as AI-scorable or human-required, with annotation guideline examples for human-required criteria.

### Observability Enrichments

- **Tracing & instrumentation** — ai-ops now includes Step 1b for design-time tracing decisions. Per-call trace field requirements (trace ID, span hierarchy, model version, prompt hash, token counts, retrieval metadata, guardrail triggers). Instrumentation approach guidance (decorator/middleware/SDK/manual). Content logging policy coordinated with guardrails-designer.

### AI Inversion Updates

- RAG failure modes 1-3 now include concrete mitigation references (contextual retrieval, self-query, hybrid retrieval, query rewriting, HyDE).
- Cross-cutting mitigations note: if multiple RAG failure modes score MEDIUM+, evaluate contextual retrieval (ingestion-time) and self-query (query-time).

### Template Sync

- All changes mirrored across `agents/`, `templates/claude/agents/`, and `templates/github/agents/`.
- VS Code Copilot abbreviated templates updated for rag-advisor, guardrails-designer, eval-designer, and ai-ops.
- Homebrew CLI version bumped to 0.12.0.

### Files Changed

- 18 files touched (17 modified + 1 new skill)
- +460 lines added across agents, skills, and templates

---

## [0.11.0] — 2026-04-01

### Overview

North Starr GenAI becomes a complete AI development agency. This release closes the 5 broken handoffs and 3 missing capabilities identified in the gap analysis, adds 2 new skills and 1 new agent, and optimizes all 15 agents via autoimprove (29 improvements, 0 reverts).

### New Skills (2)

- **`/assess`** — Project type recommendation. Classifies requirements into 7 project types (automation pipeline, agent harness, multi-agent system, RAG application, prompt chain, AI OS component, hybrid). Produces architecture sketch with topology heuristics, agent activation map, complexity estimate, and risk flags with mandatory impact + mitigation. Runs BEFORE `/decompose`.
- **`/discover`** — Requirement elicitation. Asks structured questions in adaptive groups, identifies actual needs (may differ from what client asked for), produces PRD draft ready for `/decompose`. Three reframe scenarios: problem-only, premature-tech, complex-workflow. Generates measurable success criteria and proactive scope exclusions.

### New Agent (1)

- **`agentic-designer`** — UI/UX design for AI-powered interfaces. Produces interaction specs for conversational UI, dashboards, approval workflows, agent activity views. Includes confidence thresholds by interface type (with starting defaults), typed data contracts for component inventory, actionable error recovery paths, and AI-specific edge case derivation tables. Spawned during BUILD when plan includes user-facing AI interface.

### Broken Handoffs Fixed (5)

1. **BUILD Dispatch Protocol** (HIGH) — Orchestrator now parses plan tasks for specialist tags, dispatches with explicit payloads (agent, story, tasks, output paths, constraints), tracks specialist completion in PIPELINE-STATUS.md, and signals implementation start. Templates updated with specialist → implementation mapping.
2. **Credential Escalation** (MEDIUM) — Integration-planner BLOCKED status triggers HUMAN escalation with 24h SLA; other specialists continue independently.
3. **RAG ↔ Prompt Coordination** (MEDIUM) — rag-advisor now produces a Context Injection Contract (format, delimiters, token budget, no-results fallback, truncation, citation). prompt-engineer reads the contract before designing. Orchestrator enforces RAG-first dispatch order.
4. **Runtime Cost Tracking** (LOW) — BUILD phase in CLAUDE.md/AGENTS.md now tracks cumulative token usage against cost envelope; escalates to ai-architect at 50%.
5. **Specialist Dispatch Format** (LOW) — layoutplan tasks now include `**Specialists needed:**` and `**Specialist input:**` fields, giving the orchestrator an explicit dispatch list.

### Missing Capabilities Added (3)

1. **Project Type Recommendation** (HIGH) — `/assess` skill classifies project type before decomposition begins.
2. **Requirement Elicitation** (MEDIUM) — `/discover` skill helps clients articulate needs without a pre-written PRD.
3. **Agentic UI/UX Design** (LOW-MEDIUM) — `agentic-designer` agent designs AI-powered interfaces during BUILD.

### Architecture Enrichments

- **ai-architect: Multi-agent topology patterns** — Topology selection table (6 patterns), state sharing patterns, loop control (max iterations, cost limit, convergence, deadlock detection), agent identity design template.
- **ai-architect: Fine-tuning decision ladder** — Prompt engineering → RAG → fine-tuning → hybrid, with red flags for premature fine-tuning.
- **ai-architect: REWORK handling** — New input path for HARDEN failures. Diagnosis workflow, targeted fix per failure type (cost/latency/accuracy/guardrail), ADR revision format (not new file), worked cost-reduction example.
- **ai-architect: Reference pricing table** — 7 models with actual $/1M token rates. Alternatives require quantified rejection reasons.
- **orchestrator: Multi-failure HARDEN rules** — Parallel dispatch to different agents, single payload to same agent, 7-level severity ranking.
- **orchestrator: Architecture divergence constraint injection** — Injects constraints into DESIGN dispatch instead of vague "must conform."
- **orchestrator: Parallel write conflict at PLAN→BUILD** — Checks file overlap against all active BUILD/HARDEN stories.
- **chief-ai-po: Refine mode threshold heuristics** — Default latency/accuracy/model by task type when story doesn't specify.
- **chief-ai-po: Feedback-to-revision mapping** — 6 feedback patterns mapped to specific revision actions.

### Autoimprove Results (this release)

29 improvements across 10 agents, 0 reverted. 7 agents scored 100% at baseline (no changes needed).

| Agent | Before | After | Rounds |
|-------|--------|-------|--------|
| `/assess` | 67% | 100% | 2 |
| `/discover` | 47% | 100% | 3 |
| `orchestrator` | 61% | 100% | 3 |
| `layoutplan` | 60% | 100% | 3 |
| `rag-advisor` | 33% | 100% | 4 |
| `prompt-engineer` | 53% | 100% | 3 |
| `ai-architect` | 53% | 100% | 3 |
| `agentic-designer` | 20% | 100% | 4 |
| `chief-ai-po` | 80% | 100% | 3 |
| `eval-designer` | 80% | 100% | 1 |
| `guardrails-designer` | 100% | 100% | 0 |
| `integration-planner` | 100% | 100% | 0 |
| `prompt-adversary` | 100% | 100% | 0 |
| `ai-ops` | 100% | 100% | 0 |
| `cost-estimator` | 100% | 100% | 0 |
| `demo-builder` | 100% | 100% | 0 |
| `storymap` | 100% | 100% | 0 |

**Dominant improvement pattern:** Decision tables that map input signals to recommended choices, good/bad example pairs, derivation formulas for calculated fields, and post-write verification steps. See `.plans/LEARNINGS.md` for 10 reusable meta-patterns.

### Skill Updates

- **`/orchestrate`** — Updated for BUILD Dispatch Protocol (specialist tags, RAG→Prompt ordering, completion tracking, multi-failure HARDEN, architecture divergence, parallel write conflicts).
- **`/decompose`** — Now detects raw requirements (not PRDs) and recommends `/assess` or `/discover` before proceeding.

### Templates

- **CLAUDE.md / AGENTS.md** — BUILD phase updated: specialist dispatch by tag, RAG→Prompt ordering, implementation mapping per specialist type, runtime cost tracking at 50% envelope.
- All 3 template variants (main `agents/`, `templates/claude/`, `templates/github/`) verified in sync.

### Learnings

- `.plans/LEARNINGS.md` created with 10 meta-patterns from autoimprove: decision tables > option lists, good/bad examples, derivation formulas, post-write verification, REWORK input paths, traits of 100%-baseline agents, RAG→Prompt ordering, BUILD handoff protocol, constraint injection, multi-failure dispatch.

### Files Changed

- 31 files touched (25 modified + 6 new)
- +1000 lines added, -163 removed across existing files
- 14 autoimprove directories with backups, results, and changelogs

---

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
- `/genai-sync` — `NORTH-STARR-GENAI:` marker prefix, v2.0 AI complexity gate with 5-phase workflow

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
