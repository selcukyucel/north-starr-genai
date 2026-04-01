# [Project Name]

[One-sentence project description]

<!-- [NORTH-STARR-GENAI:how-to-approach-tasks v2.0] -->
## How to Approach Tasks

Before ANY code change, print this assessment:

| # | Question | Answer |
|---|----------|--------|
| Q0 | Is current behavior covered by evals? | Yes / No |
| Q1 | Does this touch a production prompt or model config? | Yes / No |
| Q2 | Does this change what data the model sees? (RAG sources, context window, tool definitions) | Yes / No |
| Q3 | Does this affect a client-facing output? | Yes / No |
| Q4 | Could this change cost at scale? (new model, more tokens, removed caching) | Yes / No |

**Gate Rules:**
- **Fast-path**: Q0 = Yes, all others No → state the file and proceed. No table needed.
- Q0 = No → Write evals for current behavior FIRST (BASELINE phase)
- Q1 or Q2 = Yes → Run `/ai-invert` automatically. Once the inversion analysis is ready, ask "Proceed with layout plan?" before spawning the `layoutplan` agent. Do not proceed without approval.
- Q3 = Yes → Run `/baseline` before any change
- Q4 = Yes → Run `/cost-estimate` before proceeding
- Two or more of Q1-Q4 = Yes → Spawn `layoutplan` agent for structured planning
- All Low → State files and wait for confirmation

**Workflow — 5 phases executed in order:**

**1. ASSESS** — Run the gate above. Capture baseline if needed. Run `/ai-invert` → `layoutplan` for complex tasks.

**2. BUILD** — Implement the plan. Check each task's `**Specialists needed:**` field and spawn the required agents:
- `prompt-engineer` → designs/versions prompts, writes to `.plans/PROMPTS-<name>/`
- `rag-advisor` → designs chunking, embeddings, retrieval, writes to `.plans/RAG-<name>.md`
- `integration-planner` → maps API contracts, auth, retry strategies, writes to `.plans/INTEGRATION-<name>.md`
- `agentic-designer` → designs AI-powered UI patterns, writes to `.plans/UI-<name>.md`
- `none` → code directly, no specialist needed

**Dispatch order:** If both `rag-advisor` and `prompt-engineer` are needed, run `rag-advisor` FIRST. Wait for it to write its Context Injection Contract (format, delimiters, token budget, no-results fallback), then spawn `prompt-engineer` with instruction to read that contract. All other specialists may run in parallel.

**After all specialists complete**, read their outputs and implement following this mapping:
- prompt-engineer output (`.plans/PROMPTS-<name>/`) → implement prompt loading, model call, and output parsing
- rag-advisor output (`.plans/RAG-<name>.md`) → implement document ingestion, embedding, retrieval pipeline, and context injection
- integration-planner output (`.plans/INTEGRATION-<name>.md`) → implement API client with auth, retry, and fallback logic
- agentic-designer output (`.plans/UI-<name>.md`) → implement UI components following the interaction patterns
- If integration-planner flagged BLOCKED (missing credentials), skip those tasks and escalate — implement unblocked tasks first

Write tests/evals first (RED), then implement (GREEN).

**Cost tracking during BUILD:** If the plan has a cost envelope, track cumulative token usage during implementation. If cumulative cost exceeds 50% of the story's cost envelope before implementation is complete, stop and escalate to ai-architect — the cost estimate may need revision before continuing.

**3. HARDEN** — After code is working, validate automatically:
- Spawn `eval-designer` agent — runs the eval suite (`.plans/EVAL-<name>/`), scores outputs against rubric, compares to baseline. If no eval suite exists, it creates one from the acceptance criteria.
- Spawn `guardrails-designer` agent — tests input/output guardrails, PII filtering, prompt injection defenses, audit logging.
- **Both must pass** to proceed. If either fails:
  - Eval failure → review the failing criteria, fix the prompt or code, re-run eval
  - Guardrail failure → fix the gap, re-run validation
  - If the same validation fails twice → stop and ask the user for guidance

**4. COMPLETE** — Present a summary listing files modified, eval scores, guardrail status. Ask the user: "What would you like to do next?" with options: Generate commit message, Generate PR description, Run /learn (capture learnings), or Done. Do not run any of these automatically — wait for the user's choice.

**5. LEARN** — If the user chooses /learn, capture prompt patterns, model quirks, cost insights, and eval calibrations discovered during this task.

**Todo discipline:** Never create a todo item for verification steps like "run tests", "run evals", "build project", or "verify changes". Testing, evaluation, and building are implicit parts of the implementation workflow, not standalone tasks.

**Skip the full workflow for:** config changes, docs, CI, trivial one-line fixes — use the fast-path instead.
If more files are affected than estimated mid-implementation, STOP and run `/ai-invert`.
Always check `.plans/` for active plans before starting new work.
<!-- [/NORTH-STARR-GENAI:how-to-approach-tasks] -->

<!-- [NORTH-STARR-GENAI:auto-learn v1.0] -->
## When to Learn Automatically

Run `/learn` automatically when: user corrects your approach, same fix requested twice, your change breaks something, user rejects generated code, you discover an undocumented convention, you hit a trap not in any landmine rule, prompt change causes unexpected regression, model-specific behavior discovered (works on one model, fails on another), cost optimization found (caching, batching, model selection), eval threshold adjusted (too strict or too loose), guardrail gap discovered in production, hallucination pattern identified, or data pipeline quirk encountered. Finish the immediate fix first, then capture the insight.
<!-- [/NORTH-STARR-GENAI:auto-learn] -->

## Tech Stack

[List languages with versions, frameworks, key dependencies, build tools, package manager, test runner, CI/CD — be specific, not generic. Include: LLM provider SDKs, vector stores, embedding models, eval frameworks, prompt management tools.]

## Architecture

[Name the pattern (RAG pipeline, agent orchestration, prompt chain, etc.), topology (monolith, modular, microservices). List each layer with its responsibility and dependency direction. Include model selection strategy, caching approach, and guardrail placement.]

## Grain

[What changes easily (e.g. adding a new prompt variant) vs. what is hard (e.g. changing the embedding model). State what to avoid going against and why.]

## Module Map

[List each top-level module with one-line purpose. Show key dependencies between modules. Note shared infrastructure, model configs, and prompt registries.]
