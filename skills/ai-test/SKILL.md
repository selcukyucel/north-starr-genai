---
name: ai-test
description: Generate executable pytest test files for AI outputs. Produces assertion-based tests for deterministic AI components (classification, extraction, routing, structured output) that run in CI/CD. Complements /eval-suite which produces statistical evaluation datasets for non-deterministic outputs.
argument-hint: <prompt name, pipeline name, or eval suite path>
---

# AI Test — Executable Test Code Generator

## Purpose

`/eval-suite` produces evaluation datasets (JSONL) scored by rubrics — ideal for generative, non-deterministic AI outputs where statistical thresholds matter. But many AI components produce **deterministic, structured outputs** (classification labels, extracted entities, routing decisions, structured JSON) where hard assertions are appropriate and valuable.

This skill generates **executable pytest files** with fixtures, assertions, and markers that developers can commit to the repo and run in CI/CD. It bridges the gap between eval datasets and automated testing.

## When to Use

Use this skill when:
- The AI component produces **deterministic outputs** (temperature=0, structured output via Pydantic/JSON mode)
- The output has **enumerable correct answers** (classification labels, entity types, boolean decisions, routing targets)
- You want tests that run in **CI/CD** without human scoring or AI-as-judge
- You want to catch **regressions** on specific inputs with hard pass/fail — not statistical thresholds

Do NOT use this skill when:
- The output is **generative** (summaries, explanations, creative text) — use `/eval-suite` + `/prompt-test` instead
- The "correct answer" is **subjective** or has acceptable variations — statistical eval is more appropriate
- You need to evaluate **quality dimensions** like tone, helpfulness, or relevance — those need rubric scoring

**Both can coexist:** Use `/ai-test` for deterministic contract tests (format, classification, routing) and `/eval-suite` for quality evaluation on the same component.

## Pre-flight: Auto-sync Check

Before starting, read the root `CLAUDE.md` (if it exists). If `## How to Approach Tasks` appears AFTER `## Tech Stack` or `## Architecture`, the file has an outdated section order. Silently run `/genai-sync` to fix it before continuing with this skill.

## Input

The user provides one of:
- A prompt name or file path for an AI component to test
- A path to an existing eval suite (`.plans/EVAL-<name>/`) to convert golden examples into executable tests
- A description of the AI pipeline to test

## Workflow

### Step 1: Understand the Component

**Actions:**
1. Read the codebase to understand the AI component: prompt files, model config, input/output schemas, pipeline steps
2. Check for existing eval suites (`.plans/EVAL-<name>/`) — golden examples with expected outputs are the best source for test cases
3. Check for existing tests (`tests/`, `test_*.py`, `*_test.py`) to match the project's test conventions
4. Check root context files (`CLAUDE.md`, `AGENTS.md`) for test runner, framework, and conventions

**Identify these properties:**
- **Input type:** free text, structured JSON, file content, conversation history
- **Output type:** structured JSON (Pydantic model), classification label, extracted entities, boolean, routing decision
- **Output schema:** the exact Pydantic model, JSON schema, or type definition the output conforms to
- **Determinism:** Is temperature=0? Is structured output enforced (JSON mode, `response_format`)? If not deterministic, warn the user and suggest `/eval-suite` instead.
- **Call interface:** How to invoke the component in code (function signature, class method, API endpoint)

### Step 2: Determine Test Strategy

Based on the component type, select which assertion patterns apply:

| Output Type | Assertion Pattern | Example |
|---|---|---|
| Classification label | `assert result.category == "billing"` | Customer inquiry classifier |
| Structured JSON | `assert result.field == value` per field | Entity extraction, form parsing |
| Boolean decision | `assert result.decision is True` | Content moderation, eligibility check |
| Routing target | `assert result.route == "escalate"` | Ticket routing, intent detection |
| Enum/literal | `assert result.status in ["approved", "rejected"]` | Decision pipeline |
| Extraction with list | `assert "entity" in result.entities` | NER, keyword extraction |
| Numeric output | `assert abs(result.score - expected) < tolerance` | Scoring, rating systems |

**Soft assertions (for semi-deterministic outputs):**

Some fields are deterministic (category, required fields) while others vary (response text, explanation). Split assertions:

```python
# Hard assertions — must match exactly
assert result.category == "billing"
assert result.priority == "P2"

# Soft assertions — check properties, not exact text
assert len(result.response) > 10
assert "refund" in result.response.lower()
```

### Step 3: Gather Test Cases

**Source 1: Existing eval suite (preferred)**
If `.plans/EVAL-<name>/golden.jsonl` exists, convert golden examples:
- Each golden example with an `expected_output` becomes a test case
- The `scoring` field indicates which assertions to generate
- The `category` field maps to pytest markers (`@pytest.mark.happy_path`, `@pytest.mark.edge_case`)

**Source 2: Existing test data**
Check for fixture files (`events/`, `fixtures/`, `test_data/`, `tests/fixtures/`) — reuse existing test inputs.

**Source 3: Generate from the component**
If no test data exists, analyze the prompt and output schema to generate test cases:
- **Happy path (3-5):** One test per output category/label the component can produce
- **Edge cases (2-3):** Ambiguous inputs near decision boundaries
- **Format validation (1-2):** Verify output schema compliance
- **Regression anchors (1-2):** Critical inputs where a wrong answer causes real harm

For each test case, determine:
- **Input:** The complete input (realistic, not placeholder)
- **Expected output:** The exact expected value for each asserted field
- **Assertion type:** Hard (exact match) or soft (property check)

### Step 4: Detect Project Test Conventions

Before generating code, read the project's existing test setup:

**Check for:**
- Test runner: pytest (default), unittest, or other
- Test directory: `tests/`, `test/`, root-level `test_*.py`
- Fixture patterns: `conftest.py`, fixture files, factory functions
- Naming convention: `test_*.py` or `*_test.py`
- Markers or categories used: `@pytest.mark.slow`, `@pytest.mark.integration`
- Environment handling: `.env` loading, mock clients, test API keys
- Import patterns: how the project imports its own modules

**Defaults if no conventions found:**
- Framework: pytest
- Directory: `tests/ai/`
- Naming: `test_<component_name>.py`
- Fixtures: `conftest.py` in the test directory

### Step 5: Generate Test Code

Generate the test file(s) following the project's conventions. The output is **real, executable Python code** — not pseudocode or templates.

**File structure:**

```python
"""
AI output tests for <component name>.

Generated by /ai-test from <source: eval suite / manual / generated>.
Tests deterministic AI outputs with hard assertions.
For statistical quality evaluation, see /eval-suite and /prompt-test.
"""

import json
import pytest
from pathlib import Path

# Project-specific imports (adapt to the actual codebase)
from <module> import <function_or_class>


# --- Fixtures ---


@pytest.fixture
def ai_client():
    """Initialize the AI component under test."""
    # Adapt to the project's initialization pattern
    return <ComponentClass>()


@pytest.fixture
def load_event():
    """Load test event from fixture file."""
    def _load(filename: str) -> dict:
        with open(Path(__file__).parent / "fixtures" / filename) as f:
            return json.load(f)
    return _load


# --- Classification Tests ---


class TestClassification:
    """Test output classification accuracy."""

    @pytest.mark.happy_path
    def test_<category>_categorization(self, ai_client, load_event):
        """<Category> inputs should be classified as '<category>'."""
        event = load_event("<category>_test.json")
        result = ai_client.process(event["message"])
        assert result.category == "<expected_category>"
        assert len(result.response) > 10

    # ... one test per category/label


# --- Schema Validation Tests ---


class TestOutputSchema:
    """Test output format and schema compliance."""

    @pytest.mark.schema
    def test_output_has_required_fields(self, ai_client):
        """Every output must contain all required fields."""
        result = ai_client.process("Sample input")
        assert hasattr(result, "category")
        assert hasattr(result, "response")

    @pytest.mark.schema
    def test_category_is_valid_enum(self, ai_client):
        """Category must be one of the allowed values."""
        result = ai_client.process("Sample input")
        assert result.category in ["complaint", "feature_request", "billing", "other"]


# --- Edge Case Tests ---


class TestEdgeCases:
    """Test boundary and ambiguous inputs."""

    @pytest.mark.edge_case
    def test_ambiguous_input(self, ai_client):
        """Ambiguous input should still produce a valid category."""
        result = ai_client.process("<ambiguous input>")
        assert result.category in ["<valid_categories>"]
        assert len(result.response) > 0


# --- Regression Anchors ---


class TestRegressionAnchors:
    """Critical outputs that must not change between versions.
    Any failure here is a regression — investigate before shipping.
    """

    @pytest.mark.regression
    def test_<critical_case>(self, ai_client):
        """<Why this case is critical>."""
        result = ai_client.process("<critical input>")
        assert result.category == "<expected>"
```

**Generation rules:**
1. **Real imports** — use the actual module paths from the codebase, not placeholders
2. **Real inputs** — use realistic test data, not "Sample input" (except for schema tests)
3. **One test per assertion concern** — don't test classification and schema in the same test
4. **Descriptive names** — `test_billing_inquiry_classified_as_billing`, not `test_1`
5. **Docstrings on every test** — explain what the test verifies and why it matters
6. **Markers** — use `@pytest.mark.happy_path`, `@pytest.mark.edge_case`, `@pytest.mark.regression`, `@pytest.mark.schema` for selective running
7. **No mocks for the AI call** — these are integration tests that verify actual model output. Mock the environment (API keys, databases), not the model call.

### Step 6: Generate Fixture Files

For each test case, create the corresponding fixture file:

**JSON fixture format:**
```json
{
  "id": "billing-001",
  "message": "<the complete test input>",
  "expected": {
    "category": "billing",
    "response_contains": ["refund", "charge"]
  },
  "notes": "<why this test case exists>"
}
```

Write fixtures to the test directory (e.g., `tests/ai/fixtures/`). One fixture file per test case, or one file per category with multiple cases.

If converting from an existing eval suite, preserve the original IDs so test failures can be traced back to the eval suite.

### Step 7: Generate conftest.py (if needed)

If the project doesn't have a conftest.py that handles AI test setup, generate one:

```python
"""Shared fixtures for AI output tests."""

import os
import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables for AI API calls."""
    load_dotenv()


@pytest.fixture(scope="session")
def require_api_key():
    """Skip tests if API key is not set."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set — skipping AI tests")
```

### Step 8: Write to Disk

**Actions:**
1. Determine the test directory from Step 4
2. Write the test file(s):
   - `tests/ai/test_<component_name>.py` — the test code
   - `tests/ai/fixtures/<name>.json` — test fixture files
   - `tests/ai/conftest.py` — shared fixtures (if needed, don't overwrite existing)
3. If converting from an eval suite, also write a mapping file:
   - `tests/ai/EVAL_MAPPING.md` — maps test IDs to eval suite IDs for traceability

### Step 9: Validate Generated Tests

After writing the test files, attempt to run them:

1. **Syntax check:** `python -m py_compile tests/ai/test_<name>.py`
2. **Collection check:** `pytest tests/ai/test_<name>.py --collect-only` (verifies pytest can discover the tests)
3. **Run tests:** `pytest tests/ai/test_<name>.py -v` (actually execute)
4. Report results — if any tests fail, classify:
   - **Expected failure:** The test correctly catches a bug (document it)
   - **Test bug:** The assertion is wrong (fix the test)
   - **Flaky:** Non-deterministic output despite temperature=0 (add `@pytest.mark.flaky` or increase tolerance)

### Step 10: Present Summary

```
AI Tests Generated: <component name>
─────────────────────────────────────

Directory: tests/ai/
Source:    <eval suite / generated / manual>

Files:
  test_<name>.py       -- <N> tests (<N> happy path, <N> edge case, <N> regression, <N> schema)
  fixtures/            -- <N> fixture files
  conftest.py          -- shared fixtures (API key handling, env loading)
  EVAL_MAPPING.md      -- maps test IDs to eval suite (if applicable)

Test Results:
  Collected: <N>
  Passed:    <N>
  Failed:    <N>
  Skipped:   <N>

Run with:
  pytest tests/ai/test_<name>.py -v                     # all tests
  pytest tests/ai/ -m happy_path                        # happy path only
  pytest tests/ai/ -m regression                        # regression anchors only
  pytest tests/ai/ -m "not slow"                        # skip slow tests

Next steps:
  1. Review generated tests — adjust assertions where needed
  2. Add to CI/CD pipeline
  3. Run /eval-suite for statistical quality evaluation (complements these tests)
  4. As you find production bugs, add regression tests with /ai-test
```

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| `/eval-suite` | Produces JSONL datasets that `/ai-test` can convert into executable tests. `/eval-suite` is for statistical evaluation; `/ai-test` is for hard assertions. Use both. |
| `/prompt-test` | Runs interactive evaluation using rubrics. `/ai-test` produces code that runs without human interaction. |
| `/baseline` | Captures performance metrics. `/ai-test` catches regressions with hard assertions. |
| `/autoimprove` | Iteratively optimizes prompts. Run `/ai-test` after each round to verify deterministic outputs didn't regress. |

## Notes

- This skill generates **integration tests** that call the actual model API — they require API keys and incur token costs. Mark them appropriately for CI/CD (separate test stage, environment gating).
- Generated tests are a **starting point** — developers should review, adjust thresholds, and add cases from production bugs over time.
- For non-deterministic outputs (temperature > 0), assertions on exact values will be flaky. Use soft assertions (property checks, contains, length) or switch to `/eval-suite`.
- If the component uses structured output (Pydantic `response_format`, JSON mode), schema validation tests are nearly free — always include them.
- Test fixture files should be committed to the repo alongside the test code. They serve as documentation of expected behavior.
- When a production bug is found, add a regression test with `@pytest.mark.regression` before fixing. This ensures the fix sticks.
