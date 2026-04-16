#!/usr/bin/env bash
# North Starr GenAI — specialist-owned-path reminder hook.
# Fires on Write/Edit. If the target path is inside a specialist-owned
# .plans/ subdir, inject a reminder (non-blocking) that the matching
# specialist agent should be the one producing or revising this file.
# Blocking is intentionally avoided: bootstrap writes (the specialist's
# own first Write) need to succeed, and the main agent usually shouldn't
# be writing here at all — so the reminder is surfaced on every write
# instead of gating it.

set -euo pipefail

input=$(cat)
tool=$(printf '%s' "$input" | jq -r '.tool_name // ""')
path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""')

if [[ "$tool" != "Write" && "$tool" != "Edit" && "$tool" != "NotebookEdit" ]]; then
  exit 0
fi
if [[ -z "$path" ]]; then
  exit 0
fi

specialist=""
case "$path" in
  */.plans/PROMPTS-*|*/.plans/PROMPTS-*/*)
    specialist="prompt-engineer" ;;
  */.plans/RAG-*|*/.plans/RAG-*.md)
    specialist="rag-advisor" ;;
  */.plans/EVAL-*|*/.plans/EVAL-*/*)
    specialist="eval-designer" ;;
  */.plans/INTEGRATION-*|*/.plans/INTEGRATION-*.md)
    specialist="integration-planner" ;;
  */.plans/UI-*|*/.plans/UI-*.md)
    specialist="agentic-designer" ;;
  */.plans/GUARDRAILS-*|*/.plans/GUARDRAILS-*.md|*/.plans/GUARDRAILS-REPORT-*.md)
    specialist="guardrails-designer" ;;
  */.plans/ADVERSARY-*|*/.plans/ADVERSARY-*.md)
    specialist="prompt-adversary" ;;
  */.plans/ADR-*|*/.plans/ADR-*.md)
    specialist="ai-architect" ;;
  */.plans/COST-*|*/.plans/COST-*.md|*/.plans/COST-ANALYSIS-*.md)
    specialist="cost-estimator" ;;
  */.plans/OPS-*|*/.plans/OPS-*.md)
    specialist="ai-ops" ;;
  */.plans/INVERT-*|*/.plans/INVERT-*.md)
    specialist="ai-invert-analyst" ;;
  */.plans/BASELINE-*|*/.plans/BASELINE-*.md)
    specialist="baseline-capturer" ;;
  */.plans/PLAN-*|*/.plans/PLAN-*.md)
    specialist="genai-layoutplan" ;;
  */.plans/STORIES-*|*/.plans/STORIES-*.md|*/.plans/STORIES-AI-*.md)
    specialist="genai-storymap or chief-ai-po" ;;
  */.plans/REFINED-*|*/.plans/REFINED-*.md)
    specialist="chief-ai-po" ;;
  *)
    exit 0 ;;
esac

reminder="SPECIALIST-OWNED PATH: ${path}
This path is owned by the \`${specialist}\` agent (north-starr-genai:${specialist%% *}). If you are the specialist agent, proceed. If you are the main conversation, you almost certainly should be invoking the specialist via the Agent tool instead of writing here directly — the file belongs in the specialist's thread so its \`Cross-Consult Log\` is captured alongside the artifact. See templates/CLAUDE.md \`## Delegation Policy (MUST)\`."

jq -n --arg ctx "$reminder" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "allow",
    additionalContext: $ctx
  }
}'
