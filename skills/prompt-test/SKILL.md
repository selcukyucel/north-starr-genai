---
name: prompt-test
description: Run a prompt against a test suite of inputs, score outputs, and compare against baseline. Use for single-run prompt evaluation after changes.
---

# Prompt Test — Single-Run Prompt Evaluation

## Overview

Run a prompt against a test suite of inputs, score every output against a binary rubric, compare results to an existing baseline, and deliver a pass/fail verdict. This is the single-run counterpart to `/autoimprove` — where `/autoimprove` iterates in a loop, `/prompt-test` executes one evaluation cycle and reports results.

Use this skill after making a manual change to a prompt and wanting to know: **did it get better, worse, or stay the same?**

## When to Use

Use this skill when the user requests:
- "Test my prompt"
- "Run evals on [prompt name]"
- "Did my prompt change help or hurt?"
- "Compare this prompt against baseline"
- "Score the [prompt name] outputs"
- "Run the test suite for [prompt name]"
- Any request to evaluate prompt quality without iterative optimization

If the user wants **iterative optimization**, point them to `/autoimprove` instead.

## Workflow

### Step 1: Locate Inputs

**Actions:**
1. Determine the prompt to test from the user's argument:
   - **By name:** look for `.plans/PROMPTS-<name>/` or `skills/<name>/SKILL.md`
   - **By file path:** read the prompt directly from the provided path
   - **Inline:** the user pastes the prompt text directly — store it temporarily for the run
2. Locate the eval suite for test inputs:
   - Check `.plans/EVAL-<name>/` for a matching eval suite directory
   - Check for `test-inputs.md` or `inputs.json` inside the eval suite
   - Check `evals/`, `tests/eval/`, or `benchmarks/` directories
3. If no eval suite is found, ask the user to provide test inputs:

```
No eval suite found for this prompt. I need test inputs to run against.

Options:
  1. Provide 1-5 test inputs now (I'll use them for this run)
  2. Point me to a file containing test inputs
  3. I'll generate representative test inputs based on the prompt's purpose (you approve before I run)
```

4. If the user chooses option 3, analyze the prompt to generate 3-5 representative inputs that cover:
   - A typical/happy-path case
   - An edge case (very short, very long, unusual format)
   - A challenging case (ambiguous, requires nuance)
   - Present generated inputs for user approval before proceeding

**Validation:**
- You must have at least 1 test input. 3-5 is recommended for meaningful results.
- You must have a prompt to test. If neither a file nor inline text is provided, ask.

### Step 2: Load Scoring Rubric

The rubric defines what "good output" looks like. It uses the same binary yes/no format as `/autoimprove`.

**Actions:**
1. Check for an existing rubric (in priority order):
   - `.plans/EVAL-<name>/rubric.md` — the eval suite's rubric (most authoritative)
   - `.plans/PROMPTS-<name>/v<N>.md` — check the latest prompt version for an **Eval Handoff** section from the `prompt-engineer` agent. If present, it contains suggested scoring criteria, test inputs, and known weak spots. **Use these as your starting point** — the prompt-engineer designed them for this specific prompt.
   - `.plans/autoimprove-<name>/` — reuse the checklist from a prior autoimprove run
2. If a rubric exists, load it and present it to the user for confirmation:

```
Found existing rubric with [N] criteria:
  1. [criterion 1]
  2. [criterion 2]
  ...

Use this rubric? (y / n / modify)
```

3. If no rubric exists, help the user create one:

```
I need a scoring rubric — 3-6 yes/no questions that define what "good output" looks like.

Option 1: I'll analyze the prompt and propose a rubric (recommended)
Option 2: You provide your own rubric
Option 3: I'll propose one, then you refine it
```

4. If generating a rubric, follow these rules:
   - Each criterion must be **binary** — unambiguous yes or no
   - Each criterion must be **specific** — tests one concrete, observable thing
   - Each criterion must be **independent** — no overlap with other criteria
   - 3-6 criteria is the sweet spot; more than 6 leads to gaming

**Rubric anti-patterns to avoid:**
- "Is the output high quality?" (vague)
- "Does it follow best practices?" (not specific)
- "Is the tone appropriate?" (subjective without a reference)

**Example rubric for a customer-reply prompt:**

```
1. Does the reply directly address the customer's specific question or complaint?
2. Is the reply under 200 words?
3. Does the reply include a concrete next step or action item?
4. Is the reply free of corporate jargon and filler phrases?
5. Does the reply acknowledge the customer's frustration (if any) before offering a solution?
```

Get user approval on the rubric before proceeding.

### Step 3: Load Baseline

**Actions:**
1. Check for an existing baseline:
   - `.plans/BASELINE-<name>.md` — created by `/baseline`
   - `.plans/autoimprove-<name>/results.tsv` — baseline row from a prior autoimprove run
2. If a baseline exists, extract the per-criterion scores and aggregate score
3. If no baseline exists, note this — the run will produce absolute scores without a comparison:

```
No baseline found for this prompt. Results will show absolute scores only.
To enable comparison, run /baseline first, or this run's results will serve
as the baseline for future comparisons.
```

**Baseline data to extract (when available):**
- Per-criterion pass rates (e.g., "Q1: 3/3, Q2: 1/3, Q3: 2/3")
- Aggregate score (e.g., "8/12 = 66.7%")
- Configuration snapshot (model, prompt version) for context on what changed

### Step 4: Run the Prompt

**Actions:**
1. For each test input:
   a. Execute the prompt with the test input as context
   b. Capture the full output
   c. Record the output for scoring
2. Track execution metadata:
   - Number of test inputs processed
   - Any errors or failures during execution (timeout, refusal, empty output)
   - If a test input fails to produce output, record it as a failed run (scores 0 on all criteria)

**Important:**
- Use the SAME prompt text for every test input — no modifications between runs
- If the prompt requires additional context (e.g., a RAG pipeline), use the same retrieval setup for all inputs
- Capture the raw output before any post-processing — score what the model actually produces

**Non-deterministic output handling:**
If the prompt uses temperature > 0 or the model produces variable outputs:
1. Run each test input **3 times** (not just once)
2. Score each run independently
3. Report per-input results as: `[pass_count]/[3 runs]` instead of binary YES/NO
4. Flag **inconsistent** inputs — where some runs pass and others fail on the same criterion:
   ```
   ⚠ Input 3 is inconsistent: Q2 passes 2/3 runs (67%)
   ```
5. Use the **majority result** for aggregate scoring (2/3 passes = YES, 1/3 = NO)
6. Inconsistent inputs indicate prompt fragility — note them in the results as candidates for prompt hardening

If temperature = 0 and the model is deterministic, a single run per input is sufficient. Note which mode was used in the results header.

### Step 5: Score Each Output

Apply the rubric to every output using the strict scoring protocol from `/autoimprove`.

**Scoring rules:**
1. **Read the full output** before scoring any criterion
2. **Score each criterion independently** — do not let one answer influence another
3. **Be strict** — "partially" counts as NO. The criterion either clearly passes or it does not.
4. **Provide evidence** — for each score, include a brief quote or observation justifying the YES or NO
5. **Handle edge cases:**
   - Empty output = NO on all criteria
   - Output that errors/crashes = NO on all criteria
   - Output in wrong format but correct content = score each criterion on its own merits

**Scoring format per test input:**

```
Test Input [N]: [input description or first 80 chars]
  Q1: [YES/NO] — [brief evidence from the output]
  Q2: [YES/NO] — [brief evidence from the output]
  Q3: [YES/NO] — [brief evidence from the output]
  Q4: [YES/NO] — [brief evidence from the output]
  Input Score: [X]/[total]
```

### Step 6: Compare to Baseline

If a baseline exists, produce a per-criterion comparison.

**Actions:**
1. For each criterion, compare current pass rate to baseline pass rate
2. Classify each criterion:
   - **Improved** — current pass rate > baseline pass rate
   - **Regressed** — current pass rate < baseline pass rate
   - **Same** — no change
3. Flag any regressions prominently — regressions are the most important finding

**Comparison format:**

```
Per-Criterion Comparison
────────────────────────
  Q1: [criterion text]
      Baseline: [X]/[N] ([%])  →  Current: [Y]/[N] ([%])  |  Delta: [+/-N%]  |  [IMPROVED / REGRESSED / SAME]

  Q2: [criterion text]
      Baseline: [X]/[N] ([%])  →  Current: [Y]/[N] ([%])  |  Delta: [+/-N%]  |  [IMPROVED / REGRESSED / SAME]

  ⚠ REGRESSIONS:
  Q2: was 92%, now 78% — REGRESSION of 14 points. [criterion text]
  [list only regressed criteria here for quick scanning]
```

**Regression highlighting rules:**
- Any criterion that drops by more than 5 percentage points gets a `⚠` warning
- Any criterion that drops below the pass threshold gets a `🔴` critical flag
- Show the absolute point drop (not just "regressed") — "14 point regression" is actionable, "regressed" is not

If no baseline exists, skip this step and note: "No baseline available for comparison."

### Step 7: Calculate Aggregate

**Actions:**
1. Sum all YES scores across all test inputs and all criteria
2. Calculate: `aggregate = total_yes / (num_inputs x num_criteria)`
3. Determine pass/fail:
   - **Pass threshold: 80%** (default, unless the user or eval suite specifies a different threshold)
   - If aggregate >= threshold: **PASS**
   - If aggregate < threshold: **FAIL**
4. If baseline exists, calculate the delta: `delta = current_aggregate - baseline_aggregate`

### Step 8: Present Results

Display a formatted summary with all findings.

```
Prompt Test Results: <prompt name>
════════════════════════════════════

Prompt:     <path or name>
Test inputs: <N>
Rubric:     <N> criteria
Baseline:   <available / not available>

────────────────────────────────────
Per-Input Scores
────────────────────────────────────

  Input 1: [description]          [X]/[total]
  Input 2: [description]          [X]/[total]
  Input 3: [description]          [X]/[total]
  ...

────────────────────────────────────
Per-Criterion Breakdown
────────────────────────────────────

  Q1: [criterion]                 [Y]/[N] inputs passed
  Q2: [criterion]                 [Y]/[N] inputs passed
  Q3: [criterion]                 [Y]/[N] inputs passed
  ...

  Weakest:  Q[X] — [criterion text]
  Strongest: Q[X] — [criterion text]

────────────────────────────────────
Baseline Comparison
────────────────────────────────────

  [per-criterion comparison table from Step 6, or "No baseline available"]

  Regressions: [count, or "None"]
  Improvements: [count]

────────────────────────────────────
Aggregate
────────────────────────────────────

  Score:     [total_yes]/[total_possible] ([percentage]%)
  Baseline:  [baseline_score]% (delta: [+/-N]%)
  Threshold: [threshold]%
  Verdict:   **PASS** / **FAIL**

════════════════════════════════════
```

If there are regressions, add a prominent warning block:

```
!! REGRESSIONS DETECTED
   Q[X]: [criterion] dropped from [old]% to [new]%
   Q[Y]: [criterion] dropped from [old]% to [new]%

   Review these before shipping the prompt change.
```

### Step 9: Save Results

**Actions:**
1. Create `.plans/EVAL-<name>/` directory if it doesn't exist
2. Save results to `.plans/EVAL-<name>/results-<date>.md` with the full output from Step 8
3. Save the rubric to `.plans/EVAL-<name>/rubric.md` if it was newly created
4. If no prior baseline existed, offer to save current results as the baseline:

```
No prior baseline exists. Save these results as the baseline for future comparisons?
(This writes to .plans/BASELINE-<name>.md)
```

If the user agrees, write a baseline file in the format defined by `/baseline`, populating the Accuracy/Quality section with the rubric scores.

### Step 10: Suggest Next Steps

Tailor suggestions based on the verdict:

**If FAIL:**

Analyze the failure pattern and suggest a **specific fix**, not generic advice:

```
The prompt did not meet the [threshold]% threshold (scored [X]%).

Failure Analysis:
  Weakest criterion: Q[X] — [criterion text] — passed [N]/[N] ([%])
  Failure pattern: [describe the pattern — e.g., "All adversarial inputs fail Q3",
    "Long inputs (>500 words) consistently fail Q1", "Ambiguous tickets
    misclassified as 'general' instead of 'billing'"]

Suggested fix (based on failure pattern):
  • [SPECIFIC action — e.g., "Add a grounding instruction: 'Only use information
    from the provided ticket text. If the category is ambiguous, output
    confidence: low instead of guessing.'"]
  • [OR: "Add a few-shot example showing an ambiguous billing/general ticket
    correctly classified as billing"]
  • [OR: "The prompt truncates long inputs — add a summarization step before
    classification for inputs >500 tokens"]

To fix iteratively: run /autoimprove targeting Q[X]
```

The fix suggestion must reference the actual failing criterion, failing inputs, and a concrete prompt change — not "improve the prompt."

**If PASS with regressions:**

```
The prompt passes overall but has regressions in [N] criteria.

Suggested next steps:
  1. Investigate regressions before shipping:
     - Q[X]: [what changed and why it might have regressed]
  2. If regressions are acceptable trade-offs, document the decision
  3. Run /learn to capture what worked in this prompt change
```

**If PASS with no regressions:**

```
The prompt passes with no regressions. Good to ship.

Suggested next steps:
  1. Run /learn to capture what made this prompt change effective
  2. Update the baseline: run /baseline to record the new performance level
  3. If you want to push the score higher, run /autoimprove
```

## Scoring Protocol

This protocol is shared with `/autoimprove` to ensure consistent measurement across single runs and iterative optimization.

1. **Binary only** — every criterion is YES or NO. There is no partial credit, no 0.5, no "mostly."
2. **Strict interpretation** — when in doubt, score NO. Leniency introduces noise that hides real regressions.
3. **Evidence required** — every YES or NO must cite a specific part of the output. "Looks good" is not evidence.
4. **Independence** — score each criterion without reference to other criteria. A brilliant answer to Q1 does not earn leniency on Q2.
5. **Consistency across inputs** — apply the same strictness to every test input. Do not relax standards for "hard" inputs.
6. **Full coverage** — score every criterion for every test input. Do not skip criteria or inputs.

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| `/baseline` | Provides the "before" metrics that `/prompt-test` compares against |
| `/autoimprove` | Uses `/prompt-test` as its inner evaluation loop — runs it every round |
| `/learn` | Captures insights from test results as reusable rules |
| `/eval-suite` | Creates the test inputs and rubrics that `/prompt-test` consumes |

## Notes

- This skill evaluates **prompts**, not code. For code quality, use other tools.
- The pass/fail threshold defaults to 80% but can be overridden by the user or the eval suite configuration.
- When used as the inner loop of `/autoimprove`, skip the interactive steps (rubric confirmation, next-step suggestions) — those are handled by the outer loop.
- If the prompt requires external context (documents, database results, API responses), the user must provide or mock that context for each test input. Without it, the evaluation is incomplete.
- Results files accumulate in `.plans/EVAL-<name>/` — each run gets a dated filename so historical performance is preserved.
- A regression on even one criterion is worth investigating, even if the aggregate score improved. Individual criterion regressions can indicate the prompt traded one quality for another rather than genuinely improving.
- For prompts with non-deterministic output (high temperature), consider running each test input 2-3 times and averaging. Note this in the results.
