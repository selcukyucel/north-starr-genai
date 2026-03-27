# Landmine: [Landmine Name]

**Severity**: [CRITICAL / HIGH / MEDIUM / LOW — justify with evidence: instance count, affected files, blast radius]
**Threatens**: [Working / Unique / Simple / Clear / Easy / Developed / Brief — list the virtue(s) this landmine endangers. See `skills/_references/virtues/code-virtues.md`]
**Category**: [Threading / Memory / Performance / Logic / Integration / State / Error Handling / Architecture / Security / Testing / Prompt Engineering / RAG / Model Configuration / Guardrails / Cost]
**Language/Framework**: [Any / specify — must match the project's detected language, never hardcode]
**Last Updated**: [Date]

---

## Quick Summary

> [One-line description of the danger — include a specific number if possible, e.g., "30+ instances of silent error swallowing"]

---

## Symptoms

How you know you've hit this landmine:
- [Observable symptom 1 — specific to this codebase]
- [Observable symptom 2]
- [Observable symptom 3]

---

## Root Cause

[Why this happens — the technical explanation]

---

## The Trap

Why developers fall into this:
- [Reason 1 — why it seems correct]
- [Reason 2 — what makes it non-obvious]

---

## Safe Approach

<!-- Code examples MUST use the project's actual types, imports, and conventions.
     No placeholder names. Include file paths as comments showing where this code lives. -->

### Don't (dangerous)

```
[Code showing the dangerous pattern — use real project types and conventions]
```

**Why this breaks**: [Explanation]

### Do (safe)

```
[Code showing the correct approach — use real project types and conventions]
```

**Why this works**: [Explanation]

---

## Validation

How to verify you're safe:
- [ ] [Check 1]
- [ ] [Check 2]

### Detection in Existing Code

<!-- Include actual grep/search commands that work in this project -->

Search for: `[pattern to grep for]`
Look in: [specific directories or file patterns where this typically appears]

```bash
[Concrete grep/search command to find instances in this project]
```

---

## Real-World Impact

<!-- Cite specific instances found in the codebase: file names, line counts, blast radius.
     Don't write generic "this could cause problems" — show where it already has. -->

[What actually happens when this goes wrong — reference specific files and instances found during analysis]

- **[File/module]**: [specific impact description]
- **[File/module]**: [specific impact description]

## Prevention

- [Habit that prevents this]
- [Code review check — what to look for in PRs]
- [Automated check if applicable — linter rule, CI check]

## Blast Radius

[What downstream outputs are affected when this landmine triggers. E.g., "All classification outputs from the pipeline become unreliable. Affects the client dashboard and downstream automation triggers." Only include if this landmine affects AI outputs or pipelines.]

## Detection Lag

[How long before this failure is typically noticed. E.g., "Days to weeks — accuracy degrades gradually as embedding index drifts. No alert fires until threshold breach, which may be set too loosely." Only include if detection is non-trivial.]

## Client Impact

[How this affects end users / clients. E.g., "Client sees incorrect document classifications in their dashboard. Trust erosion — client may lose confidence in the automation." Only include if this has client-visible consequences.]

---

## Related

<!-- Every landmine MUST link to at least one safe pattern.
     Use relationship types to make the knowledge graph navigable:
     - Safe Patterns: patterns that avoid this landmine
     - Other Landmines: related dangers (same root cause or same area)
     - Caused by misapplying: patterns that lead here when done wrong -->

- **Safe Patterns**: [Patterns that avoid this landmine]
- **Other Landmines**: [Related dangers]
- **Caused by misapplying**: [Patterns that lead here when done wrong]

---

## Path Glob Guidance

<!-- When this template is used to generate a rule file, the frontmatter path glob
     must be as narrow as possible. Anti-patterns: **/* or **/src/**
     Good: **/src/api/routes/**/*.ts, **/models/**/*repository*
     Scope to the specific directories or file naming conventions where this danger exists. -->

**Origin**: [How/when this was discovered — e.g., "bootstrap analysis", "production incident", "code review"]
**Changelog**:
- **v1.0** ([Date]): Initial documentation
