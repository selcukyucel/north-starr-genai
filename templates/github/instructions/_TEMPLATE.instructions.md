---
applyTo: "**/*"
---

<!-- Use this template when creating new pattern or landmine rules via /learn -->
<!-- For patterns: use the Pattern sections below -->
<!-- For landmines: use the Landmine sections below -->

# Pattern: [Pattern Name]

**Category**: [Architecture / Data / UI / Testing / Integration / Performance / Infrastructure / Security / Error Handling / Prompt Engineering / RAG / Model Configuration / Guardrails]
**Virtues**: [Working / Unique / Simple / Clear / Easy / Developed / Brief — list the primary virtue(s) this pattern serves]
**Language/Framework**: [Any / specify — must match the project's detected language, never hardcode]
**Last Updated**: [Date]

---

## When to Use

**Good For**:
- [Specific situation where this pattern applies]
- [Situation 2]

**Not Good For**:
- [When to use a different approach — name the alternative pattern if one exists]

---

## Problem It Solves

**Without This Pattern**: [What goes wrong — be specific to this codebase]
**With This Pattern**: [What improves]

---

## The Pattern

### Core Idea

[1-2 sentence summary of the approach]

### Step-by-Step

```
[Code example — use the project's language, reference real types and imports]
```

**Why**: [Rationale]

### Complete Example

```
[Full working example demonstrating the pattern end-to-end]
```

---

## Best Practices

- [Do this — why]
- [Do that — why]

## Common Mistakes

### Mistake 1: [Description]
```
[Wrong approach — use real project conventions]
```
**Fix**:
```
[Correct approach]
```

---

## Variations

- **[Variation name]**: [When and how to use this variant]

## Testing This Pattern

[How to verify the pattern is correctly applied]

```
[Test example using the project's test framework]
```

## Performance Considerations

- [Consideration and mitigation — only include if relevant]

## Model Compatibility

[Which models this pattern works with, known incompatibilities. Only include if this pattern involves model interaction.]

## Cost Impact

[How this pattern affects token usage. Only include if this pattern has cost implications.]

## Eval Criteria

[How to evaluate this pattern's outputs. Only include if this pattern produces AI outputs.]

---

## Related

- **Composes with**: [Patterns used together with this one]
- **Alternative to**: [Different approaches to the same problem]
- **Prevents**: [Landmine rules this pattern avoids]
- **Misapplication causes**: [Landmine rules that result from doing this wrong]

---

**Changelog**:
- **v1.0** ([Date]): Initial documentation

---
---

<!-- LANDMINE TEMPLATE — use this structure for danger zones and known traps -->

# Landmine: [Landmine Name]

**Severity**: [CRITICAL / HIGH / MEDIUM / LOW — justify with evidence]
**Threatens**: [Working / Unique / Simple / Clear / Easy / Developed / Brief — virtue(s) this landmine endangers]
**Category**: [Threading / Memory / Performance / Logic / Integration / State / Error Handling / Architecture / Security / Testing / Prompt Engineering / RAG / Model Configuration / Guardrails / Cost]
**Language/Framework**: [Any / specify — must match the project's detected language]
**Last Updated**: [Date]

---

## Quick Summary

> [One-line description of the danger]

---

## Symptoms

- [Observable symptom 1]
- [Observable symptom 2]
- [Observable symptom 3]

---

## Root Cause

[Why this happens — the technical explanation]

---

## The Trap

- [Reason 1 — why it seems correct]
- [Reason 2 — what makes it non-obvious]

---

## Safe Approach

### Don't (dangerous)

```
[Code showing the dangerous pattern — use real project types]
```

**Why this breaks**: [Explanation]

### Do (safe)

```
[Code showing the correct approach — use real project types]
```

**Why this works**: [Explanation]

---

## Validation

- [ ] [Check 1]
- [ ] [Check 2]

### Detection in Existing Code

```bash
[Concrete grep/search command to find instances]
```

---

## Real-World Impact

- **[File/module]**: [specific impact description]

## Prevention

- [Habit that prevents this]
- [Code review check]

## Blast Radius

[What downstream outputs are affected when this landmine triggers. Only include if this affects AI outputs or pipelines.]

## Detection Lag

[How long before this failure is typically noticed. Only include if detection is non-trivial.]

## Client Impact

[How this affects end users / clients. Only include if this has client-visible consequences.]

---

## Related

- **Safe Patterns**: [Patterns that avoid this landmine]
- **Other Landmines**: [Related dangers]
- **Caused by misapplying**: [Patterns that lead here when done wrong]

---

**Origin**: [How/when this was discovered]
**Changelog**:
- **v1.0** ([Date]): Initial documentation
