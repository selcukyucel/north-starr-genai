# Pattern: [Pattern Name]

**Category**: [Architecture / Data / UI / Testing / Integration / Performance / Infrastructure / Security / Error Handling / Prompt Engineering / RAG / Model Configuration / Guardrails]
**Virtues**: [Working / Unique / Simple / Clear / Easy / Developed / Brief — list the primary virtue(s) this pattern serves. See `skills/_references/virtues/code-virtues.md`]
**Language/Framework**: [Any / specify — must match the project's detected language, never hardcode]
**Last Updated**: [Date]

---

## When to Use

**Good For**:
- [Specific situation where this pattern applies — reference actual module or layer names from the project]
- [Situation 2]

**Not Good For**:
- [When to use a different approach — name the alternative pattern if one exists]

---

## Problem It Solves

[What pain or friction does this pattern address? Why does it exist?]

**Without This Pattern**: [What goes wrong — be specific to this codebase, not generic]
**With This Pattern**: [What improves]

---

## The Pattern

### Core Idea

[1-2 sentence summary of the approach]

### Step-by-Step

<!-- Code examples MUST use the project's actual types, imports, and conventions.
     No placeholder names like MyService or doSomething() unless the project uses those names.
     Include file paths as comments showing where this code lives in the project. -->

#### Step 1: [First Step]

```
[Code example — use the project's language, reference real types and imports]
```

**Why**: [Rationale]

#### Step 2: [Second Step]

```
[Code example]
```

**Why**: [Rationale]

### Complete Example

<!-- A full working example demonstrating the pattern end-to-end.
     Should be copy-pasteable with minimal modification. -->

```
[Full working example demonstrating the pattern with real project types]
```

---

## Best Practices

- [Do this — why]
- [Do that — why]

## Common Mistakes

### Mistake 1: [Description]
```
[Wrong approach — use real project conventions to show what the mistake looks like here]
```
**Fix**:
```
[Correct approach]
```

---

## Variations

- **[Variation name]**: [When and how to use this variant — reference where in the codebase this variation appears]

## Testing This Pattern

[How to verify the pattern is correctly applied]

```
[Test example using the project's test framework and conventions]
```

## Performance Considerations

- [Consideration and mitigation — only include if relevant to this pattern]

## Model Compatibility

[Which models this pattern works with, known incompatibilities. E.g., "Works with Claude 3.5 Sonnet and GPT-4. GPT-3.5-turbo struggles with structured output format." Only include if this pattern involves model interaction.]

## Cost Impact

[How this pattern affects token usage. E.g., "Few-shot examples add ~500 tokens per request. At 10K requests/day, this adds ~$15/day on Claude Sonnet." Only include if this pattern has cost implications.]

## Eval Criteria

[How to evaluate this pattern's outputs. E.g., "Score on: format compliance (binary), factual accuracy (1-5 scale), response relevance (1-5 scale). Threshold: 90% of outputs score 4+ on accuracy." Only include if this pattern produces AI outputs.]

---

## Related

<!-- Every pattern MUST link to at least one other pattern or landmine.
     Use relationship types to make the knowledge graph navigable:
     - Composes with: patterns used together in the same flow
     - Alternative to: different approach to the same problem
     - Prevents: landmines this pattern avoids
     - Misapplication causes: landmines that result from doing this pattern wrong -->

- **Composes with**: [Patterns used together with this one]
- **Alternative to**: [Different approaches to the same problem]
- **Prevents**: [Landmine rules this pattern avoids]
- **Misapplication causes**: [Landmine rules that result from doing this wrong]

---

## Path Glob Guidance

<!-- When this template is used to generate a rule file, the frontmatter path glob
     must be as narrow as possible. Anti-patterns: **/* or **/src/**
     Good: **/src/api/routes/**/*.ts, **/models/**/*repository*
     Include file naming conventions in the glob when the pattern applies to
     specifically-named files (e.g., *ViewModel*, *_test.py, *Service*). -->

**Changelog**:
- **v1.0** ([Date]): Initial documentation
