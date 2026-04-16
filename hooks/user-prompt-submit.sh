#!/usr/bin/env bash
# North Starr GenAI — routing-directive hook.
# Fires on every UserPromptSubmit. Scans the prompt for AI-task keywords and,
# if matched, injects a mandatory routing directive into Claude's context
# naming the required specialist agents. Keep output lean (< 400 tokens).

set -euo pipefail

input=$(cat)
prompt=$(printf '%s' "$input" | jq -r '.prompt // ""')

lc=$(printf '%s' "$prompt" | tr '[:upper:]' '[:lower:]')

agents=()
domains=()

if grep -qE '(^|[^a-z])(prompt|few-shot|chain[- ]of[- ]thought|system message)' <<<"$lc"; then
  agents+=("north-starr-genai:prompt-engineer"); domains+=("prompt design")
fi
if grep -qE '(^|[^a-z])(eval|evaluation|golden set|rubric|regression test|baseline)' <<<"$lc"; then
  agents+=("north-starr-genai:eval-designer"); domains+=("eval / baseline")
fi
if grep -qE '(rag|retrieval|embedding|vector store|chunking|re[- ]rank)' <<<"$lc"; then
  agents+=("north-starr-genai:rag-advisor"); domains+=("RAG / retrieval")
fi
if grep -qE '(guardrail|injection|jailbreak|pii|content filter|safety|compliance)' <<<"$lc"; then
  agents+=("north-starr-genai:guardrails-designer"); domains+=("guardrails / safety")
fi
if grep -qE '(cost|token budget|spend|pricing|tier|throttle|rate limit)' <<<"$lc"; then
  agents+=("north-starr-genai:cost-estimator"); domains+=("cost / budget")
fi
if grep -qE '(architecture|model selection|topology|pipeline design|decision record|adr)' <<<"$lc"; then
  agents+=("north-starr-genai:ai-architect"); domains+=("architecture")
fi
if grep -qE '(monitor|observability|telemetry|drift|latency|sla|alert|ops|dashboard)' <<<"$lc"; then
  agents+=("north-starr-genai:ai-ops"); domains+=("ops / observability")
fi
if grep -qE '(integration|external api|credentials|webhook|auth method|retry strategy)' <<<"$lc"; then
  agents+=("north-starr-genai:integration-planner"); domains+=("integration")
fi
if grep -qE '(adversar|red[- ]?team|attack surface|exploit)' <<<"$lc"; then
  agents+=("north-starr-genai:prompt-adversary"); domains+=("red-team")
fi
if grep -qE '(risk analysis|inversion|what could go wrong|failure mode)' <<<"$lc"; then
  agents+=("north-starr-genai:ai-invert-analyst"); domains+=("inversion / risk")
fi

if [ "${#agents[@]}" -gt 0 ]; then
  dedup=()
  while IFS= read -r line; do
    dedup+=("$line")
  done < <(printf '%s\n' "${agents[@]}" | awk '!seen[$0]++')
  agents=("${dedup[@]}")
fi

if [ "${#agents[@]}" -eq 0 ]; then
  exit 0
fi

agent_lines=""
for a in "${agents[@]}"; do
  agent_lines+="  - ${a}"$'\n'
done
domain_list=$(IFS=", "; printf '%s' "${domains[*]}")

# Build directive via plain string concatenation to avoid heredoc quoting issues.
directive="NORTH STARR ROUTING DIRECTIVE"$'\n'
directive+="Prompt touches: ${domain_list}."$'\n\n'
directive+="Before writing code or editing prompts / evals / RAG / guardrail / ops configs, you MUST:"$'\n'
directive+="  1. State which agent(s) you will delegate to and why."$'\n'
directive+="  2. Invoke them via the Agent tool (subagent_type listed below) on separate threads."$'\n'
directive+="  3. Cite each agent output path in your response (Cross-Consult Log section)."$'\n\n'
directive+="Required agents for this prompt:"$'\n'
directive+="${agent_lines}"$'\n'
directive+="Exceptions:"$'\n'
directive+="  - True fast-path (config change, docs, typo, trivial one-line fix) => declare FAST-PATH and proceed without delegation."$'\n'
directive+="  - If the user explicitly says handle-it-yourself or no-agents => follow the user."$'\n\n'
directive+="See templates/CLAUDE.md Delegation Policy (MUST) for the full mapping."

jq -n --arg ctx "$directive" '{
  hookSpecificOutput: {
    hookEventName: "UserPromptSubmit",
    additionalContext: $ctx
  }
}'
