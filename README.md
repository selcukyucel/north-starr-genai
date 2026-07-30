# North Starr GenAI

**Evidence-led AI architecture and delivery for Codex** | development version 0.17.0

North Starr turns client discovery into reviewable architecture decisions,
machine-readable artifacts, and governed implementation plans. Codex is the
recommended experience. Claude Code and GitHub Copilot remain supported.

The default journey is intentionally small:

```text
$north-starr-genai:intake
   ↓
$north-starr-genai:assess
   ↓
$north-starr-genai:architecture-design
   ↓
named human acceptance
   ↓
$north-starr-genai:decompose → $north-starr-genai:orchestrate
```

The first three stages produce a proposal. They do not silently approve a
design or authorize implementation.

## Why North Starr

AI architecture fails when polished assumptions are mistaken for client facts,
or when a model, SDK, RAG pipeline, or multi-agent system is selected before the
problem is understood. North Starr keeps those decisions explicit:

- validates Vignola handoffs, discovery exports, transcripts, briefs, and PRDs;
- separates confirmed facts, inferences, assumptions, unknowns, deferred items,
  and conflicts;
- considers no-build, configuration, buy, and deterministic software before AI;
- selects the simplest viable shape: bounded AI component, prompt chain,
  governed workflow, bounded agent loop, or justified multi-agent system;
- records MCP servers and tools as concrete security and operations contracts;
- treats exact model selection as `benchmark_required` and unresolved library
  selection as `spike_required`;
- defines evaluation, human authority, observability, rollback, and residual
  risk before implementation;
- preserves source hashes so changed evidence marks downstream work stale.

## Codex installation (recommended)

North Starr is packaged as a Codex plugin in `.codex-plugin/plugin.json`. The
plugin exposes all 26 skills and lightweight routing hooks.

For this development checkout, install it from the configured personal
marketplace:

```bash
codex plugin add north-starr-genai@personal
```

Codex discovers the default personal marketplace automatically from
`~/.agents/plugins/marketplace.json`; do not add it again. For a different
local marketplace, add the root that contains its marketplace file, then
install with that marketplace name:

```bash
codex plugin marketplace add <path-to-marketplace-root>
codex plugin add north-starr-genai@<marketplace-name>
```

You can also open **Plugins** in the Codex desktop app and install North Starr
from that marketplace. Review and trust the bundled hooks when prompted, then
start a new Codex task so the skills are loaded.

Verify the installation:

```bash
codex plugin list --json
```

For a project-local fallback, including Codex surfaces where plugins are not
loaded, install the same skills into the project:

```bash
north-starr-genai codex-init /path/to/project
```

This creates `.agents/skills/`, shared `.agents/references/`, and a compact
`AGENTS.md` without copying the legacy 18-agent workflow into every task.
Project-local skills use unqualified names such as `$intake`; plugin skills use
qualified names such as `$north-starr-genai:intake`.

## Minimum-complexity workflow

### 1. Validate discovery evidence

Start with a Vignola North Starr handoff or another discovery artifact:

```text
$north-starr-genai:intake /path/to/north-starr-handoff.json
```

`$north-starr-genai:intake` checks structure and provenance, preserves MCP/tool
mentions, and asks no more than three decision-blocking follow-ups. It writes:

```text
.north-starr/intake-validation.json
.north-starr/intake-validation.md
```

Six resolved client prompts can support a provisional intake. Twelve are
recommended. `unknown` and `deferred` are valid answers and remain visible.

### 2. Decide whether AI is justified

```text
$north-starr-genai:assess .north-starr/intake-validation.json
```

`$north-starr-genai:assess` considers no-build, process/configuration, buy, and
deterministic software before recommending an AI shape. It writes:

```text
.north-starr/assessment.json
.north-starr/assessment.md
```

### 3. Create the architecture proposal

```text
$north-starr-genai:architecture-design .north-starr/intake-validation.json .north-starr/assessment.json
```

The design is organized into six plain-language cards:

1. Goal and scope
2. System shape
3. Information and tools
4. Human control
5. Quality and operations
6. Runtime and technology stack

The skill writes:

```text
.north-starr/architecture-proposal.json
.north-starr/architecture-proposal.md
.north-starr/technology-stack.json
.north-starr/tool-registry.json
.north-starr/manifest.json
```

### 4. Accept the proposal deliberately

Architecture begins with status `proposed`. A named human must review it and
record acceptance with:

- approver name and timestamp;
- accepted scope and current evidence hashes;
- residual-risk owner;
- conditions or expiry, when applicable.

Only an `accepted` architecture with current source hashes may become
implementation work. A proposal is not accepted merely because a skill
completed successfully.

### 5. Plan and execute

After acceptance:

```text
$north-starr-genai:decompose .north-starr/architecture-proposal.json
$north-starr-genai:orchestrate
```

Use `$north-starr-genai:decompose` to turn the accepted scope into stories. Use
`$north-starr-genai:orchestrate` when those stories are ready for governed
execution.

## Machine-readable architecture workspace

North Starr writes human-readable Markdown and versioned JSON side by side in
`.north-starr/`.

- JSON is the canonical machine-readable artifact.
- Markdown is the concise review view of the same decision.
- `manifest.json` links artifacts to source hashes.
- Changed discovery evidence makes dependent assessment and design artifacts
  stale.
- Architecture status follows
  `draft/proposed → accepted/rejected/superseded`.
- Only a named human can create acceptance or implementation authority.

The repository includes schemas and a dependency-free validator:

```bash
python3 scripts/validate_artifacts.py repo .
python3 scripts/validate_artifacts.py handoff /path/to/north-starr-handoff.json
python3 scripts/validate_artifacts.py bundle /path/to/vignola-export-directory
python3 scripts/validate_artifacts.py manifest .north-starr/manifest.json
```

## How technology choices are made

North Starr records separate decisions for:

- host language, runtime, and deployment environment;
- model-provider API client;
- structured-output and validation library;
- agent or workflow SDK category;
- durable workflow or graph runtime;
- MCP client/server integration;
- evaluation, tracing, secrets, and persistence.

An agent SDK is not the default. The design compares:

| Category | Use when |
|---|---|
| `no_agent_sdk` | One bounded call or a small deterministic workflow is enough |
| `provider_sdk` | Provider-specific capabilities have measured value |
| `portable_ai_sdk` | Portability and typed model/tool calls matter |
| `agent_sdk` | A bounded tool loop, handoffs, or built-in tracing add measured value |
| `durable_workflow_runtime` | Long-running work needs resumability, timers, or approvals |
| `graph_runtime` | Dynamic graph state and checkpoints materially simplify the workflow |

Candidates are verified against current primary documentation and a small
capability spike. Models are benchmarked on representative gold cases rather
than chosen from preference or an undated pricing table.

## Skills (26)

Plugin skills use `$north-starr-genai:skill-name` in Codex. Project-local
skills use `$skill-name`. Claude Code uses the equivalent `/skill-name` syntax.

### Discovery and architecture

| Skill | Purpose |
|---|---|
| `intake` | Validate discovery evidence and produce a trusted intake |
| `discover` | Run the separate 12-question client discovery spine |
| `assess` | Test AI necessity and recommend the simplest system shape |
| `architecture-design` | Produce the six-card architecture and technology proposal |
| `decompose` | Convert an accepted PRD or architecture scope into stories |
| `orchestrate` | Execute accepted stories through governed delivery |
| `genai-bootstrap` | Capture project context and North Starr conventions |
| `genai-sync` | Refresh managed North Starr project instructions |

### Risk, quality, and operations

| Skill | Purpose |
|---|---|
| `ai-invert` | Analyze AI-specific failure modes |
| `genai-invert` | Run general inversion analysis |
| `baseline` | Capture a reproducible pre-change baseline |
| `cost-estimate` | Build a scale-aware cost envelope |
| `eval-suite` | Design statistical and model-graded evaluations |
| `ai-test` | Generate deterministic tests for structured AI outputs |
| `prompt-test` | Test prompt behavior and regressions |
| `guardrail-spec` | Specify input, output, tool, and policy controls |
| `deploy-checklist` | Produce an AI-aware release checklist |
| `incident-playbook` | Define response, degradation, rollback, and recovery |
| `prompt-version` | Version prompts and their evaluation evidence |
| `autoimprove` | Optimize against explicit evaluations |

### Engineering and delivery

| Skill | Purpose |
|---|---|
| `analyze-code` | Analyze implementation and architecture context |
| `generate-commit` | Prepare an intentional commit description |
| `generate-pr` | Prepare a pull request description |
| `handoff-doc` | Create a delivery or operational handoff |
| `learn` | Record reusable project learning |
| `report-weekly` | Summarize progress, risks, and decisions |

## Specialist prompts

The repository retains 18 legacy specialist prompts in `agents/` and matching
Claude Code/Copilot templates. They cover product, architecture, retrieval,
prompts, evaluation, guardrails, adversarial testing, cost, integrations,
operations, UX, and delivery.

Codex users normally enter through the skills above. North Starr may use a
small number of relevant subagents when parallel work adds value; it does not
force all 18 specialists into every engagement. The legacy prompts remain for
compatibility and detailed advanced workflows.

## Claude Code compatibility

Install the Claude Code plugin:

```text
/plugin marketplace add selcukyucel/north-starr-genai
/plugin install north-starr-genai
```

This loads the same 26 skills using slash commands, the 18 specialist prompts,
and the Claude-specific routing hooks. Start with:

```text
/intake /path/to/north-starr-handoff.json
/assess .north-starr/intake-validation.json
/architecture-design
```

To update:

```text
/plugin marketplace update selcukyucel/north-starr-genai
/plugin install north-starr-genai
```

## GitHub Copilot compatibility

Install the CLI with Homebrew:

```bash
brew tap selcukyucel/north-starr-genai https://github.com/selcukyucel/north-starr-genai.git
brew install north-starr-genai
```

Initialize a project:

```bash
cd <your-project>
north-starr-genai init
```

This installs Copilot-compatible assets:

- `.github/agents/`
- `.github/skills/`
- `.github/instructions/`
- `AGENTS.md`

Update them with:

```bash
north-starr-genai update
```

Copilot does not use the Codex or Claude hook runtimes. The same governance
travels through the generated `AGENTS.md` and skill instructions.

## Repository layout

```text
.codex-plugin/         Codex plugin manifest
.claude-plugin/        Claude Code plugin and marketplace manifests
skills/                26 reusable workflows
agents/                18 legacy specialist prompts
hooks/                 Codex and Claude routing hooks
schemas/               Versioned machine-readable artifact contracts
scripts/               Artifact validation and maintenance tools
templates/             Codex, Claude Code, and GitHub Copilot project templates
references/            Shared pattern, landmine, and code-virtue references
tests/                 Artifact and hook regression tests
bin/                   north-starr-genai CLI
```

## Design principles

1. Evidence before architecture.
2. The simplest adequate system wins.
3. Tools and MCP servers are governed interfaces, not product-name assumptions.
4. Models are benchmarked; SDKs are justified by capability spikes.
5. Human authority is explicit.
6. Evaluation, observability, security, and rollback are architecture.
7. Machine-readable artifacts remain traceable to their sources.

## License

MIT
