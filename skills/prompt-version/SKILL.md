---
name: prompt-version
description: Track prompt iterations with diffs, scores, and rollback capability. Version control for prompts — the "source code" of AI automations.
argument-hint: <prompt name>
---

# Prompt Version — Prompt Version Tracking

## Purpose

Track prompt iterations with diffs, eval scores, and rollback capability. Prompts are the "source code" of AI automations — a single word change in a prompt can dramatically alter system behavior, accuracy, cost, and safety. Yet prompts often live in code files or config strings without the version control discipline applied to application code.

This skill provides structured prompt versioning: every change is snapshotted with metadata, diffed against the previous version, scored against evals, and logged in a changelog. When a prompt change causes a regression, you can identify exactly what changed and roll back to a known-good version.

Run this **whenever a prompt changes** — whether during development, optimization, or production maintenance. The versioned history becomes an invaluable artifact for debugging, auditing, and the `/handoff-doc` skill.

## Pre-flight: Auto-sync Check

Before starting, read the root `CLAUDE.md` (if it exists). If `## How to Approach Tasks` appears AFTER `## Tech Stack` or `## Architecture`, the file has an outdated section order. Silently run `/sync` to fix it before continuing with this skill.

## Input

The user provides the name of the prompt to version. This can be:
- A prompt name (e.g., "classification-system-prompt", "extraction-instructions")
- A file path containing the prompt
- A reference to an existing prompt in `.plans/PROMPTS-*/`
- The keyword "new" to create a fresh prompt version history

The user may also specify an action:
- **save** (default): Snapshot the current prompt as a new version
- **diff**: Show the diff between two versions (or current vs. previous)
- **rollback**: Activate a previous version
- **history**: Show the version changelog
- **compare**: Side-by-side comparison of two versions with their eval scores

## Workflow

### Step 1: Identify the Prompt

**Actions:**
1. Determine which prompt the user wants to version:
   - If a file path is given: read the prompt from that file
   - If a prompt name is given: search the codebase for files matching the name (check `prompts/`, `src/prompts/`, config files, inline prompt strings)
   - If a `.plans/PROMPTS-<name>/` directory exists: read the latest version from there
   - If "new" is specified: the user will provide the prompt text
2. Read the full prompt text, including:
   - System prompt / instructions
   - Few-shot examples (if any)
   - Output format instructions
   - Guardrail instructions embedded in the prompt
   - Variable placeholders or template syntax
3. Identify the prompt's context:
   - Which automation or feature uses this prompt
   - Which model it is configured to run against (model name, version)
   - Model parameters (temperature, max tokens, top_p, etc.)
   - How the prompt is assembled at runtime (static text + dynamic context + user input)
4. Check root context files (`CLAUDE.md`, `AGENTS.md`) for prompt conventions

### Step 2: Create or Update the Prompt Directory

**Actions:**
1. Generate a short kebab-case name for the prompt if one does not exist (e.g., `support-classifier`, `invoice-extractor`, `summarization-instructions`)
2. Create `.plans/PROMPTS-<name>/` directory if it does not exist
3. If the directory already exists, read its contents:
   - `changelog.md` — version history
   - `v1.md`, `v2.md`, etc. — version snapshots
   - `active-version.md` — pointer to the currently active version
4. Determine the next version number (N = highest existing version + 1, or 1 if new)

### Step 3: Save the Version Snapshot

**Actions:**
1. Write the full prompt snapshot to `.plans/PROMPTS-<name>/v<N>.md` with this structure:

```markdown
# <prompt name> — Version <N>

**Version:** <N>
**Created:** <date and time>
**Author:** <who made this change — from user context or git>
**Model:** <model name and version this prompt is designed for>
**Model Config:** temperature=<T>, max_tokens=<N>, top_p=<P>, [other params]
**Reason for Change:** <why this version was created — what was the goal of the change?>
**Status:** <active / inactive>

## Prompt Text

```text
<full prompt text, exactly as it would be sent to the model>
<include system prompt, few-shot examples, format instructions, guardrail instructions>
<mark dynamic sections with clear delimiters: {{user_input}}, {{retrieved_context}}, etc.>
```

## Change Summary

<1-3 sentences describing what changed from the previous version and why.
For v1: "Initial version." with a brief description of the prompt's purpose.>

## Eval Scores

<If eval results are available at the time of versioning, record them here.
If not available, note "Evals not yet run for this version.">

| Metric | Score | Threshold | Status |
|--------|-------|-----------|--------|
| <metric name> | <value> | <required threshold> | <PASS/FAIL> |
| <metric name> | <value> | <required threshold> | <PASS/FAIL> |

## Metadata

- **Token count (prompt only):** <estimated token count of the static prompt portion>
- **Token count (with typical context):** <estimated token count when assembled with average retrieved context and user input>
- **Estimated cost per call:** $<cost based on model pricing>
- **Source file:** <path to the file in the codebase where this prompt lives, if applicable>
- **Dependencies:** <other prompts, templates, or configs this prompt depends on>
```

2. If this is v1, the Change Summary should describe the prompt's purpose and initial design rationale
3. If this is v2+, the Change Summary should specifically describe what changed and why

### Step 4: Generate Diff from Previous Version

**Actions:**
1. If a previous version exists (v<N-1>.md), generate a readable diff:
   - Show added lines, removed lines, and changed lines
   - Highlight significant changes (not just whitespace or formatting)
   - Call out changes to: instructions, examples, output format, guardrail language, model config
2. Write the diff as a section in the version file or present it to the user
3. Classify the change magnitude:
   - **Minor**: Formatting, typo fixes, minor wording adjustments (low risk)
   - **Moderate**: New examples, adjusted instructions, refined output format (medium risk, test recommended)
   - **Major**: Structural changes, new capabilities, changed model, removed guardrails (high risk, evals required)

**Diff format:**

```markdown
## Diff from v<N-1>

**Change magnitude:** <Minor / Moderate / Major>

### Added
- <line or section added>

### Removed
- <line or section removed>

### Changed
- <before> -> <after>

### Model Config Changes
- <parameter>: <old value> -> <new value>
```

4. If the change magnitude is Major, add a warning: "Major prompt change. Run full eval suite before deploying this version."

### Step 5: Record Eval Scores

**Actions:**
1. Check for eval results associated with this prompt version:
   - `.plans/EVAL-*/results.md` — look for results timestamped near this version
   - Inline eval results provided by the user
   - Automated eval output from the codebase
2. If eval results are available:
   - Record the scores in the version file's Eval Scores section
   - Compare against the previous version's scores — flag regressions
   - Compare against baseline (`.plans/BASELINE-*.md`) — flag if below threshold
3. If eval results are NOT available:
   - Note "Evals not yet run for this version" in the Eval Scores section
   - If the change magnitude is Moderate or Major, recommend running evals before activating this version
4. Score comparison format (appended to diff or presented to user):

```markdown
## Score Comparison

| Metric | v<N-1> | v<N> | Delta | Status |
|--------|--------|------|-------|--------|
| <metric> | <score> | <score> | <+/- delta> | <Improved / Regressed / Unchanged> |
```

### Step 6: Update Changelog

**Actions:**
1. Read `.plans/PROMPTS-<name>/changelog.md` (create if it does not exist)
2. Append a new entry at the top (most recent first):

```markdown
## Changelog: <prompt name>

### v<N> — <date>
- **Author:** <who>
- **Reason:** <why this change was made>
- **Change magnitude:** <Minor / Moderate / Major>
- **Summary:** <1-2 sentence description of the change>
- **Eval status:** <Passed / Failed / Not yet run>
- **Status:** <Active / Inactive>

### v<N-1> — <date>
- ...
```

3. Update `.plans/PROMPTS-<name>/active-version.md`:

```markdown
# Active Version: <prompt name>

**Current active version:** v<N>
**Activated:** <date>
**Last eval:** <date and result, or "not yet run">
```

4. If the user did not explicitly request activation, set the new version as active by default for save operations. Note: rollback operations change the active version to the specified prior version.

### Step 7: Support Rollback

**Actions (when the user requests a rollback):**
1. Read the requested version from `.plans/PROMPTS-<name>/v<target>.md`
2. Verify the target version exists and has a complete prompt text
3. Update `active-version.md` to point to the target version
4. Add a changelog entry:

```markdown
### Rollback to v<target> — <date>
- **Author:** <who>
- **Reason:** <why rolling back — e.g., "v<N> caused accuracy regression">
- **Rolled back from:** v<N>
- **Rolled back to:** v<target>
- **Action required:** Update the prompt in the codebase to match v<target>
```

5. **Important:** The rollback updates the version tracking, but the actual prompt in the codebase must also be updated. Present the user with:
   - The full prompt text of the target version
   - The file path where the prompt lives in the codebase (from the version metadata)
   - Clear instructions: "Update the prompt at `<path>` to match v<target>. The version tracking has been updated."
6. If the rollback target has eval scores, display them as confirmation that the version is known-good
7. If the rollback target does NOT have eval scores, warn: "Version v<target> does not have recorded eval scores. Consider running evals after rollback to confirm quality."

### Step 8: Present Summary

After completing the requested action, present a concise summary:

**For save operations:**
```
## Prompt Version: <name>

**Action:** Saved v<N>
**Change magnitude:** <Minor / Moderate / Major>
**Change:** <1-sentence summary>
**Eval status:** <Passed / Failed / Not yet run>
**Active version:** v<N>

Prompt version saved to `.plans/PROMPTS-<name>/v<N>.md`.
Changelog updated at `.plans/PROMPTS-<name>/changelog.md`.
```

**For rollback operations:**
```
## Prompt Version: <name>

**Action:** Rolled back to v<target>
**Rolled back from:** v<N>
**Reason:** <reason>
**Active version:** v<target>

Version tracking updated. Update the prompt in the codebase at `<path>` to match v<target>.
```

**For history/diff operations:**
```
## Prompt Version: <name>

**Total versions:** <count>
**Active version:** v<N>
**Last change:** <date> — <summary>

<changelog or diff content>
```

## Output Structure

The skill produces and maintains a directory at `.plans/PROMPTS-<name>/` with this structure:

```
.plans/PROMPTS-<name>/
  changelog.md          — Version history with dates, authors, reasons, and scores
  active-version.md     — Pointer to the currently active version
  v1.md                 — First version snapshot (full prompt + metadata)
  v2.md                 — Second version snapshot
  v3.md                 — Third version snapshot
  ...
```

Each version file is self-contained — it includes the full prompt text, model config, change summary, diff from previous, and eval scores. This means any version can be understood and restored without reading the entire history.

## Notes

- This skill is language-agnostic — it versions prompts regardless of the framework or language they are used in
- Read the actual prompt from the codebase before versioning — never version based on the user's description alone
- The version file must contain the COMPLETE prompt text, not a summary or description of it. The whole point is to have an exact snapshot that can be restored
- Dynamic sections of the prompt (user input, retrieved context) should be marked with clear delimiters (`{{variable_name}}`) so the static and dynamic portions are distinguishable
- Token counts are estimates — use the appropriate tokenizer for the model if available, otherwise estimate at 1 token per 4 characters
- Eval scores are recorded as-available. Not every version will have scores immediately. The skill should not block on evals — record "not yet run" and move on
- The changelog is append-only (newest first). Never modify or delete existing changelog entries
- Rollback updates the version tracking but does NOT automatically update the codebase. The user must apply the change to the source file. This is intentional — prompt changes in code should go through normal code review
- If the prompt is assembled from multiple template files at runtime, version the complete assembled prompt (what the model actually receives) rather than individual template fragments
- This skill pairs with `/handoff-doc` (the version history informs the Prompt Modification Guide) and `/deploy-checklist` (the checklist verifies prompt versions are tracked)
- When in doubt about whether a change is Minor, Moderate, or Major, classify it one level higher. It is better to run unnecessary evals than to miss a regression
- Cost estimation should use the model's current published pricing. If pricing is not known, note "pricing not available" rather than guessing
