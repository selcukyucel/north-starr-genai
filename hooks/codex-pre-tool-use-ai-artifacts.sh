#!/usr/bin/env bash
# North Starr GenAI — non-blocking reminder for governed architecture artifacts.

set -euo pipefail

input="$(cat)"
tool="$(printf '%s' "$input" | jq -r '.tool_name // ""')"

case "$tool" in
  apply_patch|Write|Edit|NotebookEdit) ;;
  *) exit 0 ;;
esac

payload="$(printf '%s' "$input" | jq -r '[.tool_input | .. | strings] | join("\n")')"

if ! grep -qE '(\.north-starr|\.plans)/(ARCHITECTURE|TECH-STACK|TOOL-REGISTRY|ADR|DECISIONS|APPROVAL|MANIFEST|architecture|technology-stack|tool-registry|approval|manifest)' <<<"$payload"; then
  exit 0
fi

reminder="North Starr governed artifact: keep source/evidence hashes and facts, assumptions, unknowns, and conflicts explicit. A generated architecture remains PROPOSED; do not write it as ACCEPTED or add it to an accepted decision registry without a named human approver, timestamp, and scope."

jq -n --arg ctx "$reminder" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    additionalContext: $ctx
  }
}'
