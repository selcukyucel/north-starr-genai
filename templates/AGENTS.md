# [Project Name]

[One-sentence project description]

<!-- [NORTH-STARR-GENAI:how-to-approach-tasks v3.1] -->
## How to Approach Tasks

Before ANY code change, print this assessment:

| # | Question | Answer |
|---|----------|--------|
| Q0 | Is current behavior covered by evals? | Yes / No |
| Q1 | Does this touch a production prompt or model config? | Yes / No |
| Q2 | Does this change what data the model sees? (RAG sources, context window, tool definitions) | Yes / No |
| Q3 | Does this affect a client-facing output? | Yes / No |
| Q4 | Could this change cost at scale? (new model, more tokens, removed caching) | Yes / No |

**Gate Rules (MANDATORY — not advisory):**
- **Fast-path**: Q0 = Yes, all others No → state file + proceed. Declare "FAST-PATH" when routing hook asks.
- Q0 = No → MUST invoke `baseline-capturer` (via `/baseline`) to capture current behavior FIRST.
- Q1 or Q2 = Yes → MUST invoke `ai-invert-analyst` (via `/ai-invert`). PreToolUse hook surfaces reminder when Write/Edit targets `.plans/PROMPTS-*`, `.plans/RAG-*`, `.plans/EVAL-*`, `.plans/GUARDRAILS-*` — route to specialist instead of writing directly. Inversion ready → use `vscode_askQuestions` to ask "Proceed with layout plan?" (options: "Yes, run genai-layoutplan", "No, let me review first"). Plan ready → ask again with `vscode_askQuestions`: "Plan is ready. Start implementation?" (options: "Yes, start coding", "No, I want to adjust the plan"). No proceed without approval at each gate.
- Q3 = Yes → MUST invoke `baseline-capturer` (via `/baseline`) before any change.
- Q4 = Yes → MUST invoke `cost-estimator` (via `/cost-estimate`) before proceeding.
- Two or more of Q1–Q4 = Yes → spawn `genai-layoutplan` for structured planning.
- All Low → state files + wait for confirmation.

## Delegation Policy (MUST)

Task touches one of these domains → MUST invoke matching specialist via Agent tool (`subagent_type: "north-starr-genai:<name>"`) on separate thread, cite output path in response `Cross-Consult Log`, and NOT write to specialist's owned `.plans/` directory directly:

| Domain | Specialist | Owned `.plans/` paths |
|---|---|---|
| Prompt design, few-shot, CoT, system messages | `prompt-engineer` | `PROMPTS-*/` |
| Eval design, golden sets, rubrics, regression tests | `eval-designer` | `EVAL-*/` |
| Baseline capture (pre-change snapshot) | `baseline-capturer` | `BASELINE-*.md` |
| RAG, retrieval, embedding, chunking, re-rank | `rag-advisor` | `RAG-*.md` |
| Guardrails, injection defense, PII, content filter, compliance | `guardrails-designer` | `GUARDRAILS-*.md`, `GUARDRAILS-REPORT-*.md` |
| Red-teaming, adversarial prompts | `prompt-adversary` | `ADVERSARY-*.md` |
| Cost estimation, token budget, model-tier routing | `cost-estimator` | `COST-*.md` |
| Architecture, model selection, ADRs, topology | `ai-architect` | `ADR-*.md` |
| Monitoring, observability, telemetry, drift, SLA, alerts | `ai-ops` | `OPS-*.md` |
| External APIs, credentials, webhooks, auth, retry | `integration-planner` | `INTEGRATION-*.md` |
| Risk analysis, inversion, failure modes | `ai-invert-analyst` | `INVERT-*.md` |
| UI/UX for AI interfaces | `agentic-designer` | `UI-*.md` |
| Implementation plan from inversion | `genai-layoutplan` | `PLAN-*.md` |
| Story decomposition (PRD → stories) | `genai-storymap` or `chief-ai-po` | `STORIES-*.md`, `STORIES-AI-*.md` |
| Story refinement (TRIAGE mode) | `chief-ai-po` | `REFINED-*.md` |

**Exceptions — delegation NOT required:**
- True fast-path changes (config, docs, typo, trivial one-line fix) — declare "FAST-PATH".
- User explicitly says "handle it yourself" / "no agents" — follow user.
- You are the specialist agent writing your own output file.

**Peer consultation mandatory inside specialist threads:** every specialist report ends with `## Cross-Consult Log` citing peers consulted. Missing log → orchestrator flags incomplete at HARDEN → DELIVER, routes back for rework. See each specialist's `## Required Peer Consultations` for MUST-cite list.

## Token Discipline (MUST — applies to every dispatch)

Before dispatching ANY specialist, AND inside every specialist thread:

1. **Story-slice, not whole STORIES file.** Pass `.plans/stories/<story-id>.md` slice path. Never pass `.plans/STORIES-AI-<name>.md` path to specialists. If slice missing, generate it from STORIES first (chief-ai-po + genai-storymap auto-emit slices to `.plans/stories/`).
2. **Compress peer artifacts before Wave-2 dispatch.** Between waves (DESIGN → PLAN, PLAN → BUILD, BUILD → HARDEN), run `/caveman:compress` on each prior-wave artifact >5KB (INVERT/BASELINE/COST/RAG/ADR/PROMPTS/GUARDRAILS/INTEGRATION/OPS). Wave 2+ specialists read compressed copies. Original kept as `<file>.original.md` for audit.
3. **Existence-gate optional reads.** Glob first; skip missing `CLAUDE.md`, `AGENTS.md`, `LEARNINGS.md`, `DECISIONS.md`. Do not pay token cost for failed reads.
4. **Section-range Reads** for any artifact >300L. Use `Read` `offset`+`limit` to read only the section being cited.
5. **Cap turn budget per specialist.** Each specialist agent prompt enforces its own turn budget (8–12 typical). Beyond → checkpoint and partial output, not silent over-run.
6. **Iteration mode = latest version only.** When iterating on prompts/RAG/etc, read latest version + diff vs prior, not all historical versions.

These rules cap input-token spend per agent dispatch. Skipping them = the bloat-per-story trap (1M+ tokens per wave).

**Workflow — 5 phases executed in order:**

**1. ASSESS** — Run gate above. Capture baseline if needed. Run `/ai-invert` → `genai-layoutplan` for complex tasks.

**2. BUILD** — Implement plan. Check each task's `**Specialists needed:**` field, spawn required agents:
- `prompt-engineer` → designs/versions prompts → `.plans/PROMPTS-<name>/`
- `rag-advisor` → designs chunking, embeddings, retrieval → `.plans/RAG-<name>.md`
- `integration-planner` → API contracts, auth, retry → `.plans/INTEGRATION-<name>.md`
- `agentic-designer` → AI UI patterns → `.plans/UI-<name>.md`
- `none` → code directly, no specialist needed

**Dispatch order:** Both `rag-advisor` + `prompt-engineer` needed → run `rag-advisor` FIRST. Wait for Context Injection Contract (format, delimiters, token budget, no-results fallback), then spawn `prompt-engineer` with instruction to read that contract. Other specialists run parallel.

**Inter-wave compression:** before dispatching Wave 2 (e.g. `prompt-engineer`/`guardrails`/`ai-ops`), run `/caveman:compress` on each Wave 1 artifact (`INVERT-*.md`, `BASELINE-*.md`, `COST-*.md`, `RAG-*.md`, `ADR-*.md`) the new specialists will read. Skipping this re-pays full input-token cost on every Wave 2 specialist (the documented bloat trap).

**After all specialists complete**, read outputs and implement per this mapping:
- prompt-engineer output (`.plans/PROMPTS-<name>/`) → implement prompt loading, model call, output parsing
- rag-advisor output (`.plans/RAG-<name>.md`) → implement document ingestion, embedding, retrieval pipeline, context injection
- integration-planner output (`.plans/INTEGRATION-<name>.md`) → implement API client with auth, retry, fallback
- agentic-designer output (`.plans/UI-<name>.md`) → implement UI components per interaction patterns
- integration-planner flagged BLOCKED (missing creds) → skip those tasks, escalate — unblocked tasks first

Write tests/evals first (RED), then implement (GREEN).

**Cost tracking during BUILD:** plan has cost envelope → track cumulative token usage during implementation. Cumulative > 50% of story's cost envelope before complete → stop, escalate to ai-architect (cost estimate may need revision).

**3. HARDEN** — Validate after code works:
- `eval-designer` → runs eval suite (`.plans/EVAL-<name>/`), scores vs rubric, compares to baseline. No eval suite → creates one from acceptance criteria.
- `guardrails-designer` → tests input/output guardrails, PII filtering, injection defenses, audit logging.
- **Both must pass.** Either fails:
  - Eval failure → review failing criteria, fix prompt or code, re-run
  - Guardrail failure → fix gap, re-run
  - Same validation fails twice → stop, ask user

**4. COMPLETE** — Summary: files modified, eval scores, guardrail status. Use `vscode_askQuestions` to prompt developer with options: "Generate commit message", "Generate PR description", "Run /learn (capture learnings)", "Done". No auto-action — wait for choice. Developer chooses "Generate commit message" → generate, then `vscode_askQuestions` again with options: "Generate PR description", "Run /learn (capture learnings)", "Done".

**5. LEARN** — User chooses `/learn` → capture prompt patterns, model quirks, cost insights, eval calibrations discovered.

**Todo discipline:** never create todo item for verification steps ("run tests", "run evals", "build project", "verify changes"). Testing, evaluation, building are implicit, not standalone tasks.

**Skip full workflow for:** config changes, docs, CI, trivial one-line fixes — fast-path.
More files affected than estimated mid-implementation → STOP, run `/ai-invert`.
Always check `.plans/` for active plans before new work.
<!-- [/NORTH-STARR-GENAI:how-to-approach-tasks] -->

<!-- [NORTH-STARR-GENAI:auto-learn v1.0] -->
## When to Learn Automatically

Run `/learn` automatically when any of: user corrects your approach; same fix requested twice; your change breaks something; user rejects generated code; undocumented convention discovered; trap not in landmine rules; prompt change causes unexpected regression; model-specific behavior (works on one, fails on another); cost optimization found (caching, batching, model selection); eval threshold adjusted (too strict/loose); guardrail gap in production; hallucination pattern identified; data pipeline quirk. Finish immediate fix first, then capture.
<!-- [/NORTH-STARR-GENAI:auto-learn] -->

## Tech Stack

[List languages with versions, frameworks, key dependencies, build tools, package manager, test runner, CI/CD — specific, not generic. Include LLM provider SDKs, vector stores, embedding models, eval frameworks, prompt management tools.]

## Architecture

[Name pattern (RAG pipeline, agent orchestration, prompt chain, etc.), topology (monolith, modular, microservices). List each layer with responsibility + dependency direction. Include model selection strategy, caching approach, guardrail placement.]

## Grain

[What changes easily (adding new prompt variant) vs hard (changing embedding model). State what to avoid going against + why.]

## Module Map

[List each top-level module with one-line purpose. Show key dependencies between modules. Note shared infrastructure, model configs, prompt registries.]
