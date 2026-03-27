---
name: baseline
description: Capture AI system performance baseline before making changes. Records accuracy, latency, token usage, cost, error rates, and output format compliance. Use before any change to a client-facing AI output.
argument-hint: <component or pipeline name>
---

# Baseline — Capture Current AI Performance

## Purpose

Before changing any AI component (prompt, model config, RAG pipeline, guardrails), capture current performance metrics so you can measure whether your change helped or hurt. Without a baseline, you can't know if a 15% accuracy drop happened because of your change or was already there.

Run this **before** making changes. The complexity gate triggers this automatically when Q3 = Yes (client-facing output change).

## Input

The user provides the name or description of the AI component to baseline. Can be a pipeline name, prompt name, or feature area.

## Workflow

### Step 1: Identify What to Measure

**Actions:**
1. Read the codebase to understand the AI component being changed
2. Identify the pipeline: what goes in, what comes out, what steps exist between
3. Check for existing eval suites, test data, or metrics:
   - Look for eval directories (`.plans/EVAL-*/`, `evals/`, `tests/eval/`, `benchmarks/`)
   - Look for test datasets (golden files, fixture data, test inputs)
   - Look for existing metrics dashboards or logging
4. Check `.plans/BASELINE-*.md` for prior baselines on this component. If a prior baseline exists, load it — you'll compare in Step 4b.
5. If no eval suite exists, **warn the user**: "No eval suite found for this component. The baseline will be limited to what we can measure without one. Consider running `/eval-suite` first."

### Step 2: Capture Metrics

Measure these categories. Skip any that don't apply to this component.

#### Accuracy / Quality
- **If eval suite exists** (`.plans/EVAL-*/`): run it and record scores (aggregate + per-category)
- **If golden examples exist** (fixture files, test data): compare current output to expected output, score match rate
- **If neither exists** — do NOT skip accuracy. Instead, run a **quick manual baseline**:
  1. Identify 5-10 representative inputs for the component (ask the user if unsure what's representative)
  2. Run the pipeline on each input and capture outputs
  3. Score each output on a 1-5 scale for the most important quality dimension (accuracy, relevance, or completeness — pick the one that matters most for this component)
  4. Record the average score, min, max, and any outputs that scored below 3
  5. Note: "Manual baseline (N=X, scored by AI on [dimension]). Recommend creating a formal eval suite via `/eval-suite` for ongoing measurement."
  This gives a rough but real accuracy signal — far better than "no accuracy baseline available"

#### Latency
- **Method:** Run the pipeline on **20+ representative inputs** and compute percentiles from the response times
- Record: p50, p95, p99 end-to-end latency
- Per-step latency if the pipeline has multiple stages (use timing instrumentation or logs)
- If you can't run live requests, estimate from model specs (note: "Estimated from [source], not measured") and document the estimation method
- **Sample size matters:** 5 requests gives noisy data. 20+ gives stable percentiles.

#### Token Usage
- **Method:** Run 5-10 representative inputs and capture token counts from model API response headers (`usage.prompt_tokens`, `usage.completion_tokens`) or count using the provider's tokenizer
- Record: input tokens/request (average), output tokens/request (average), total tokens/request
- Break down input tokens: system prompt (fixed) + user input (variable) + RAG context (variable)

#### Cost
- **Method:** Multiply measured token counts × current model pricing (cite the pricing source and date)
- Record: cost per request, projected monthly cost at current volume (state the volume assumption)
- Cost breakdown by component if multiple model calls exist

#### Error Rate
- **Method:** Review logs for the last 7 days (or run 50+ test requests) and categorize failures
- Record: overall error rate, per-category rates (timeout, rate limit, content filter, parsing error, model refusal)
- Document current retry/fallback behavior

#### Output Format Compliance
- **Method:** Run 20+ inputs and check each output against the expected schema/format
- Record: compliance rate (percentage), list of common violations with frequency
- If structured output (JSON): validate against schema, count parse failures

### Step 3: Snapshot Configuration

Record the full configuration needed to reproduce this exact system state:
- **Model:** name, version, and API endpoint (e.g., "claude-sonnet-4-20250514 via api.anthropic.com")
- **Model parameters:** temperature, max_tokens, top_p, stop sequences
- **Prompt:** version or hash, and the file path where the prompt lives. If the prompt is short (<50 lines), include the full text. If long, include the hash and path.
- **RAG configuration:** embedding model + version, chunk size, chunk overlap, top-k, re-ranker model (if any), similarity threshold
- **Vector DB state:** document count in index, last refresh/rebuild date
- **Guardrail configuration:** filters enabled, thresholds, PII detection mode
- **Dependencies:** key library versions that affect AI behavior (e.g., `langchain==0.2.1`, `chromadb==0.4.22`)
- **Environment:** relevant env vars, feature flags, deployment target (staging/production)

### Step 4: Write Baseline

**Actions:**
1. Create `.plans/` directory if it doesn't exist
2. Generate a short kebab-case name from the component (e.g., `classification-prompt`, `rag-pipeline`)
3. Write to `.plans/BASELINE-<name>.md`:

```markdown
# Baseline: <component name>

**Created:** <date>
**Component:** <what was measured>
**Measured by:** <how — eval suite, manual test, estimation>

## Configuration Snapshot

| Setting | Value |
|---------|-------|
| Model | <name, version, endpoint> |
| Model params | <temperature, max_tokens, top_p, stop sequences> |
| Prompt | <version/hash, file path, or full text if short> |
| RAG config | <embedding model+version, chunk size, overlap, top-k, re-ranker, threshold> |
| Vector DB state | <document count, last refresh date> |
| Guardrails | <filters enabled, thresholds, PII mode> |
| Key dependencies | <library versions affecting AI behavior> |
| Environment | <env vars, feature flags, deployment target> |

## Metrics

### Accuracy / Quality
<scores, or "No eval suite available">

### Latency
| Percentile | Value |
|-----------|-------|
| p50 | <ms> |
| p95 | <ms> |
| p99 | <ms> |

### Token Usage
| Metric | Value |
|--------|-------|
| Input tokens/request | <N> |
| Output tokens/request | <N> |
| Total tokens/request | <N> |

### Cost
| Metric | Value |
|--------|-------|
| Cost per request | $<N> |
| Monthly cost (current volume) | $<N> |

### Error Rate
| Category | Rate |
|----------|------|
| Overall | <N>% |
| <category> | <N>% |

### Output Format Compliance
<compliance rate and common violations>

## Regression Thresholds

Define what counts as a regression for each metric. After making changes, compare against these thresholds:

| Metric | Current Value | Regression If | Source |
|--------|--------------|---------------|--------|
| Accuracy | <baseline score> | drops by >3% (absolute) | eval suite / manual baseline |
| Latency p95 | <baseline ms> | increases by >20% | measured |
| Cost/request | $<baseline> | increases by >15% | calculated |
| Error rate | <baseline>% | increases by >2% (absolute) | logs / test run |
| Format compliance | <baseline>% | drops below 95% | schema validation |

Adjust thresholds based on the component's criticality — client-facing components get tighter thresholds.

## How to Reproduce

To re-run this exact baseline measurement:

```
<list the specific commands, scripts, or steps used to capture each metric>
<e.g., "Run: python -m pytest tests/eval/ --tb=short" for accuracy>
<e.g., "Run: python scripts/benchmark.py --inputs fixtures/test_inputs.json --n 20" for latency>
<e.g., "Token counts from API response headers over 10 sample requests">
```

**Important:** Anyone should be able to re-run these steps and get comparable numbers. If a measurement required manual judgment (e.g., manual quality scoring), document the rubric used.

## Gaps

- <what couldn't be measured and why>
- <recommendations for improving measurement>
```

4. Inform the user: "Baseline saved to `.plans/BASELINE-<name>.md`."

### Step 4b: Compare Against Prior Baseline (if exists)

If a prior baseline was found in Step 1 (action 4), show the trend:

```
Baseline Trend: <component>
──────────────────────────

                    Previous (<date>)    Current (<date>)    Delta
Accuracy            <score>              <score>             <+/- %>
Latency p95         <ms>                 <ms>                <+/- %>
Cost/request        $<N>                 $<N>                <+/- %>
Error rate          <N>%                 <N>%                <+/- %>
Format compliance   <N>%                 <N>%                <+/- %>

Config changes since last baseline:
  - Model: <old> → <new> (or "unchanged")
  - Prompt: <old hash> → <new hash> (or "unchanged")
  - RAG config: <changes or "unchanged">
```

If no prior baseline exists, note: "First baseline for this component — no trend data available."

### Step 5: Suggest Next Steps

```
Baseline captured for <component>.

Next steps:
  1. Make your changes
  2. Run the same measurements after changes
  3. Compare: did accuracy improve? Did cost stay within budget? Did latency stay acceptable?

If you don't have an eval suite yet, consider running /eval-suite to create one.
```

## Notes

- This skill captures a snapshot in time — it's most useful immediately before a change
- If a baseline already exists for this component, ask the user: "A baseline from [date] exists. Create a new one (overwrites) or keep the existing one?"
- The baseline file is consumed by `/prompt-test` (Phase 2) for comparison
- Accuracy metrics require an eval suite or golden examples — without them, the baseline is limited to operational metrics (latency, cost, errors)
- All measurements should be reproducible — the "How to Reproduce" section in the output must contain the exact commands or steps, not just descriptions. Someone reading the baseline 3 months later should be able to re-run the same measurement.
- For pipelines with multiple model calls, break down metrics per step where possible
