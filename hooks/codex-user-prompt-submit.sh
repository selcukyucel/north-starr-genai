#!/usr/bin/env bash
# North Starr GenAI — concise Codex routing hint.
# The hook does not force a full pipeline for advice, discovery, or trivial edits.

set -euo pipefail

input="$(cat)"
prompt="$(printf '%s' "$input" | jq -r '.prompt // ""')"
lc="$(printf '%s' "$prompt" | tr '[:upper:]' '[:lower:]')"

if ! grep -qE '(^|[^a-z0-9])(ai architecture|agentic|multi[- ]agent|rag|retrieval|mcp|model selection|agent sdk|ai sdk|llm|prompt chain|vignola|north starr|north-starr)([^a-z0-9]|$)' <<<"$lc"; then
  exit 0
fi

route="North Starr applies only if it helps this task. Keep the default journey small:
1. Vignola or discovery artifact present -> use \$north-starr-genai:intake first.
2. Raw requirement -> use \$north-starr-genai:assess.
3. Architecture or technology choice -> use \$north-starr-genai:architecture-design after intake/assessment.
4. Implementation already scoped -> use the narrow specialist skill needed.

Do not launch the full orchestration pipeline for explanation, review, documentation, or a trivial change. Prefer no-build, configuration, deterministic software, or one bounded AI step when those meet the evidence. Architecture output is PROPOSED until an explicitly named human accepts it."

jq -n --arg ctx "$route" '{
  hookSpecificOutput: {
    hookEventName: "UserPromptSubmit",
    additionalContext: $ctx
  }
}'
