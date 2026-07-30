#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

irrelevant="$(
  printf '%s' '{"prompt":"Update the storage adapter documentation."}' |
    "$repo_root/hooks/codex-user-prompt-submit.sh"
)"
test -z "$irrelevant"

route="$(
  printf '%s' '{"prompt":"Review this Vignola handoff and decide the AI architecture."}' |
    "$repo_root/hooks/codex-user-prompt-submit.sh"
)"
printf '%s' "$route" | jq -e '.hookSpecificOutput.hookEventName == "UserPromptSubmit"' >/dev/null
printf '%s' "$route" | jq -e '.hookSpecificOutput.additionalContext | contains("$north-starr-genai:intake")' >/dev/null

ordinary_edit="$(
  printf '%s' '{"tool_name":"apply_patch","tool_input":{"command":"*** Update File: src/app.ts"}}' |
    "$repo_root/hooks/codex-pre-tool-use-ai-artifacts.sh"
)"
test -z "$ordinary_edit"

governed_edit="$(
  printf '%s' '{"tool_name":"apply_patch","tool_input":{"command":"*** Update File: .north-starr/architecture-proposal.json"}}' |
    "$repo_root/hooks/codex-pre-tool-use-ai-artifacts.sh"
)"
printf '%s' "$governed_edit" | jq -e '.hookSpecificOutput.hookEventName == "PreToolUse"' >/dev/null
printf '%s' "$governed_edit" | jq -e '.hookSpecificOutput.additionalContext | contains("PROPOSED")' >/dev/null

echo "Codex hook tests passed"
