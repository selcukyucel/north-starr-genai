# North Starr GenAI

**Your North Starr for AI Development** | v0.10.0

An agentic development workflow framework for teams building AI automations — extending North Starr's "control over speed" philosophy to the non-deterministic world of prompts, models, pipelines, and evaluations.

## What It Does

North Starr GenAI replaces the traditional complexity gate with an **AI Complexity Gate** that catches the risks specific to AI systems:

| # | Question | Why |
|---|----------|-----|
| Q0 | Is current behavior covered by evals? | Eval-first discipline |
| Q1 | Does this touch a production prompt or model config? | Prompt changes are high-risk |
| Q2 | Does this change what data the model sees? | Data changes alter model behavior |
| Q3 | Does this affect a client-facing output? | Client-visible changes need baselines |
| Q4 | Could this change cost at scale? | Cost is a first-class concern |

Based on the answers, it routes your work through a 5-phase workflow: **ASSESS** (gate + baseline + risk analysis) → **BUILD** (specialist agents auto-spawn) → **HARDEN** (eval + guardrails auto-validate) → **COMPLETE** → **LEARN**.

## Relationship to North Starr

Two products, one philosophy, same community.

- **[North Starr](https://github.com/selcukyucel/north-starr)** — for traditional software development
- **North Starr GenAI** — for AI automations (RAG, agents, prompt chains, LLM integrations)

North Starr GenAI inherits the core workflow shape (gate → analyze → plan → build → verify → learn) but replaces the content of each step with AI-specific concerns.

## Installation

### Claude Code (recommended)

```
/plugin marketplace add selcukyucel/north-starr-genai
/plugin install north-starr-genai
```

Then run `/bootstrap` in your AI project.

### VS Code Copilot (Homebrew)

```bash
brew tap selcukyucel/north-starr-genai https://github.com/selcukyucel/north-starr-genai.git
brew install north-starr-genai
cd your-project && north-starr-genai init
```

Then run `/bootstrap` to generate project-specific config.

## Skills (21)

### Core Workflow

| Skill | Purpose |
|-------|---------|
| `/bootstrap` | Generate AI tool config from codebase — detects AI stack, generates rules, installs all 14 agents |
| `/ai-invert` | AI-specific risk analysis — 10 dimensions, NEW/PRE-EXISTING/AMPLIFIED classification, per-risk eval strategy |
| `/baseline` | Capture AI system performance — measurement methods, regression thresholds, reproduction steps |
| `/cost-estimate` | Token cost projection — per-component breakdown, cost delta for changes, model comparison |
| `/orchestrate` | Start the multi-story pipeline — budget preview, resume support, operational commands |

### Evaluation & Safety

| Skill | Purpose |
|-------|---------|
| `/eval-suite` | Generate evaluation datasets — golden examples, tailored adversarial inputs, regression anchors |
| `/prompt-test` | Single-run prompt evaluation — non-deterministic handling, regression highlighting, pattern-specific fix suggestions |
| `/guardrail-spec` | Generate guardrail specs — pipeline-stage scoped, false positive estimation, testable acceptance criteria |

### Agency Operations

| Skill | Purpose |
|-------|---------|
| `/deploy-checklist` | Pre-deployment verification — risk mitigation mapping, staging/prod diff, alert routing verification |
| `/incident-playbook` | AI failure runbooks — escalation chains, time-to-detect, blast radius, runnable detection commands |
| `/handoff-doc` | Client documentation — monitoring ranges from baselines, SLA numbers from artifacts, prompt safety rationale |
| `/prompt-version` | Prompt version tracking — diffs, scores, rollback, changelog |

### Inherited from North Starr

| Skill | Purpose |
|-------|---------|
| `/invert` | Standard inversion analysis (for non-AI code in AI projects) |
| `/decompose` | Break PRDs into epics and user stories |
| `/learn` | Capture learnings (extended with 7 AI-specific triggers) |
| `/sync` | Inject managed sections after plugin update |
| `/generate-commit` | Generate commit messages from staged changes |
| `/generate-pr` | Generate PR descriptions from branch diffs |
| `/analyze-code` | Find refactoring opportunities and code smells |
| `/report-weekly` | Generate weekly commit reports |
| `/autoimprove` | Autonomously optimize skill prompts |

## Agents (14)

### Planning & Decomposition
| Agent | Purpose |
|-------|---------|
| `layoutplan` | Build implementation plans from inversion analysis (extended for AI) |
| `storymap` | Decompose PRDs into prioritized user stories |
| `chief-ai-po` | AI-specific story decomposition — 3 modes: decompose, refine, incorporate-feedback |

### Orchestration
| Agent | Purpose |
|-------|---------|
| `orchestrator` | Pipeline state machine — routes stories through the full DAG with feedback loops |
| `ai-architect` | Technical design, model selection, cost envelopes, ADRs |
| `cost-estimator` | Cost projection (estimation mode) and optimization analysis |

### Build Specialists
| Agent | Purpose |
|-------|---------|
| `prompt-engineer` | Design, write, and iterate on prompts — eval handoff, design rationale |
| `rag-advisor` | Design RAG pipelines — chunking, embeddings, retrieval, re-ranking |
| `integration-planner` | Plan external system integrations — API contracts, retry strategies |

### Validation
| Agent | Purpose |
|-------|---------|
| `eval-designer` | Run eval suites — consumes handoffs, statistical noise awareness, actual outputs in feedback |
| `guardrails-designer` | Test safety guardrails — delegates to prompt-adversary, pipeline-stage coverage map |
| `prompt-adversary` | Red-team prompts — targeted attacks, chained attacks, structured output for guardrails-designer |
| `ai-ops` | Configure monitoring, alerting, drift detection |

### Delivery
| Agent | Purpose |
|-------|---------|
| `demo-builder` | Package deliverables, generate handoff docs, trigger client acceptance |

## Quick Start

1. Install the plugin (see Installation above)
2. Run `/bootstrap` in your AI project
3. Start working — the AI Complexity Gate guides you automatically:
   - Touching a prompt? → `/ai-invert` runs, specialists spawn during BUILD
   - Client-facing change? → `/baseline` captures performance, validators run during HARDEN
   - Cost impact? → `/cost-estimate` projects costs at scale
   - Multiple stories? → `/decompose` then `/orchestrate` for the full pipeline

## Workflows

### Agent Interaction Map

How the 14 agents connect in the orchestration pipeline:

```
                         ┌─────────────┐
                         │ ORCHESTRATOR │
                         └──────┬──────┘
                                │
                     ┌──────────┴──────────┐
                     │    chief-ai-po      │
                     │   (refine story)    │
                     └──────────┬──────────┘
                                │
                     ┌──────────┴──────────┐
                     │    ai-architect     │
                     │  (design + ADR)     │
                     └────┬──────────┬─────┘
                          │          │
                ┌─────────┘          └──────────┐
                ▼                               ▼
          ┌──────────┐                 ┌───────────────┐
          │ ai-invert│                 │cost-estimator │
          │ (risks)  │                 │  (budget)     │
          └────┬─────┘                 └───────┬───────┘
               │                               │
               └───────────────┬───────────────┘
                               ▼
                        ┌─────────────┐
                        │  layoutplan │
                        │   (plan)    │
                        └──────┬──────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌────────────┐  ┌────────────┐  ┌───────────────┐
       │  prompt-   │  │   rag-     │  │ integration-  │
       │  engineer  │  │  advisor   │  │   planner     │
       └─────┬──────┘  └─────┬──────┘  └───────┬───────┘
             │               │                  │
             └───────────────┼──────────────────┘
                             ▼
               ┌─────────────┼──────────────┐
               ▼             ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌───────────┐
       │   eval-    │ │ guardrails-│ │  ai-ops   │
       │  designer  │ │  designer  │ │ (monitor) │
       └─────┬──────┘ └──────┬─────┘ └─────┬─────┘
             │          ┌────┴─────┐        │
             │          │  prompt- │        │
             │          │adversary │        │
             │          └──────────┘        │
             └───────────────┼──────────────┘
                             ▼
                      ┌────────────┐
                      │demo-builder│
                      │ (deliver)  │
                      └────────────┘

Feedback loops (failures route back upstream):
  eval-designer ──fails──→ prompt-engineer    "Fix the prompt"
  guardrails    ──fails──→ ai-architect       "Fix the design"
  cost-estimator ──over──→ ai-architect       "Reduce cost"
  same gate fails twice──→ HUMAN escalation   "Your call"
```

### Orchestrator State Machine

```
STATES:
  TRIAGE    → chief-ai-po refines story
  DESIGN    → ai-architect + ai-invert + cost-estimator
  PLAN      → layoutplan produces tasks
  BUILD     → specialist agents work in parallel
  HARDEN    → eval + guardrails + ops validate
  DELIVER   → demo-builder packages output
  REWORK    → feedback loop, targeted re-entry
  HUMAN     → waiting for operator or client decision

TRANSITIONS:
  TRIAGE  → DESIGN    when: story has acceptance criteria
  TRIAGE  → HUMAN     when: story needs clarification
  DESIGN  → PLAN      when: architecture approved + cost within budget
  DESIGN  → HUMAN     when: cost exceeds budget or conflicting constraints
  PLAN    → BUILD     when: user approves plan
  BUILD   → HARDEN    when: all tasks complete
  HARDEN  → DELIVER   when: all gates pass
  HARDEN  → REWORK    when: any gate fails
  HARDEN  → HUMAN     when: same gate fails twice after rework
  REWORK  → BUILD     when: issue is in code/prompts (targeted fix)
  REWORK  → DESIGN    when: issue is architectural
```

### Parallel vs Sequential Execution

```
SEQUENTIAL (each needs the previous output):
  chief-ai-po → ai-architect → layoutplan

PARALLEL (independent work from the same plan):
  ┌─ prompt-engineer
  ├─ rag-advisor
  └─ integration-planner

PARALLEL (independent validation of the same code):
  ┌─ eval-designer
  ├─ guardrails-designer
  └─ ai-ops
```

### Single Task (Developer View)
```
Task → AI Complexity Gate (Q0-Q4)
  → ASSESS: /baseline + /ai-invert → layoutplan
  → BUILD: prompt-engineer / rag-advisor / integration-planner (auto-spawned)
  → HARDEN: eval-designer + guardrails-designer (auto-validated)
  → COMPLETE → LEARN
```

### Multi-Story Pipeline (Team View)
```
PRD → /decompose (story map) → /orchestrate (start pipeline)
  → orchestrator routes each story through:
     TRIAGE (chief-ai-po refine)
     → DESIGN (ai-architect + cost-estimator)
     → PLAN (layoutplan)
     → BUILD (prompt-engineer + rag-advisor + integration-planner)
     → HARDEN (eval-designer + guardrails-designer + ai-ops)
     → DELIVER (demo-builder → client acceptance)
  → Feedback loops: eval fails → prompt-engineer, guardrails fail → ai-architect
  → /learn captures insights after each story
```

## CLI

```bash
north-starr-genai init [dir]      # Install skills in a project
north-starr-genai update [dir]    # Update skills (preserves config)
north-starr-genai status [dir]    # Check setup status
north-starr-genai cache-update    # Refresh Claude Code plugin cache
north-starr-genai version         # Show version
north-starr-genai help            # Show help
```

## License

MIT
