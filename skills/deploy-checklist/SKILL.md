---
name: deploy-checklist
description: Pre-deployment verification checklist for AI automations. Verifies evals pass, baselines show no regressions, guardrails are tested, costs are reviewed, monitoring is configured, and rollback plan is documented.
argument-hint: <deployment name or automation>
---

# Deploy Checklist — AI Deployment Verification

## Purpose

Pre-deployment verification checklist for AI automations. Before any AI automation goes live (or is updated in production), this skill runs a structured pass/fail verification across every dimension that matters: correctness, safety, cost, observability, and recoverability.

This is the complexity gate applied to deployment. No automation ships without a green checklist or explicitly acknowledged blockers. The output is a persistent artifact that serves as both a go/no-go decision document and a historical record of what was verified before each deployment.

Run this **after** implementation is complete and **before** deploying to production. Ideally, all referenced artifacts (eval results, baselines, guardrail reports, cost projections) already exist in `.plans/`. If they do not, the checklist will flag their absence as a blocker.

## Pre-flight: Auto-sync Check

Before starting, read the root `CLAUDE.md` (if it exists). If `## How to Approach Tasks` appears AFTER `## Tech Stack` or `## Architecture`, the file has an outdated section order. Silently run `/sync` to fix it before continuing with this skill.

## Input

The user provides the name of the automation or deployment being verified. This can be:
- A specific automation name (e.g., "support-classifier", "invoice-extractor")
- A feature or pipeline name (e.g., "rag-pipeline-v2", "lead-scoring-update")
- A reference to a `.plans/` artifact that describes the work being deployed

## Workflow

### Step 1: Read the Automation Being Deployed

**Actions:**
1. Identify the automation or change being deployed from the user's input
2. Read the relevant codebase: prompts, model configurations, pipeline configs, application code
3. Check root context files (`CLAUDE.md`, `AGENTS.md`) for architecture and deployment conventions
4. Read `.plans/` for all related artifacts:
   - `PLAN-*.md` or `TASKS-*.md` — the implementation plan for this work
   - `INVERT-*.md` — risk analysis that identified what could go wrong
   - `DECISIONS.md` — prior decisions that constrain deployment
   - `LEARNINGS.md` — lessons from prior deployments
5. Build a clear picture of **what is changing** relative to what is currently in production
6. Note any environment-specific considerations (staging vs production, feature flags, canary deployment)

### Step 2: Check Eval Suite Results

**Actions:**
1. Look for eval results in `.plans/EVAL-*/results.md` or similar eval output files
2. For each eval suite found, verify:
   - All test cases ran (no skipped or errored tests)
   - Pass rate meets the threshold defined in the eval spec (default: 100% for golden file tests, configurable for statistical evals)
   - No regressions from previous eval runs
3. If eval results reference specific metrics (accuracy, F1, latency percentiles), record the values
4. If no eval results exist, flag as **BLOCKER**: "No eval results found. Run evals before deployment."

**Checklist item:** `Eval Suite` — PASS (all thresholds met) / FAIL (details) / BLOCKER (no evals found)

### Step 3: Compare Against Baseline

**Actions:**
1. Look for baseline documents in `.plans/BASELINE-*.md`
2. Compare current eval results against the baseline:
   - Accuracy: current >= baseline (no regression)
   - Latency: current p50 and p95 within acceptable range of baseline
   - Token usage: current within expected range (flag if >20% increase)
   - Output quality: any qualitative regressions noted in eval comments
3. If baseline exists but current metrics are worse, flag as **FAIL** with specific regression details
4. If no baseline exists, flag as **WARNING**: "No baseline found. Current results will become the baseline."

**Checklist item:** `Baseline Comparison` — PASS (no regressions) / FAIL (regressions found) / WARNING (no baseline)

### Step 4: Check Guardrail Validation

**Actions:**
1. Look for guardrail reports in `.plans/GUARDRAILS-REPORT-*.md` or `.plans/GUARDRAILS-*.md`
2. Verify each guardrail specified in the report:
   - Input guardrails implemented and tested (PII detection, injection filtering, input validation, rate limiting)
   - Output guardrails implemented and tested (content filtering, format validation, confidence thresholds, hallucination checks)
   - Human escalation triggers configured and routed correctly
   - Fallback behavior defined and tested for every guardrail
   - Audit logging configured for guardrail triggers
3. Cross-reference with the risk analysis (`INVERT-*.md`) — are all HIGH and MEDIUM risks covered by guardrails?
4. If guardrail spec exists but implementation is incomplete, flag specific gaps
5. If no guardrail spec exists, flag as **BLOCKER** for HIGH-risk automations, **WARNING** for LOW-risk

**Checklist item:** `Guardrail Validation` — PASS (all guardrails tested) / FAIL (gaps found) / BLOCKER (no guardrails for high-risk system)

### Step 5: Review Cost Projections

**Actions:**
1. Look for cost analysis in `.plans/COST-*.md`
2. Verify the following cost dimensions:
   - Token cost per request (input + output) at current model and pricing
   - Projected monthly cost at expected volume (1x, 10x scale)
   - Cost ceiling or budget limit defined
   - Alert threshold configured (e.g., alert at 80% of budget)
   - Comparison to previous deployment cost (if upgrading)
3. Check for cost-optimization measures:
   - Caching strategy documented (system prompt caching, response caching, embedding caching)
   - Batch processing used where appropriate
   - Model selection justified (not using expensive model where cheaper suffices)
4. If costs exceed approved budget, flag as **BLOCKER**
5. If no cost analysis exists, flag as **WARNING** with rough estimate based on code review

**Checklist item:** `Cost Review` — PASS (within budget) / FAIL (over budget) / WARNING (no cost analysis)

### Step 6: Verify Monitoring Configuration

**Actions:**
1. Check for monitoring setup in the codebase and deployment configs:
   - **Accuracy monitoring**: mechanism to detect output quality degradation (eval sampling, user feedback loop, automated quality checks)
   - **Latency monitoring**: alerts for p50 and p95 latency exceeding thresholds
   - **Error rate monitoring**: alerts for error rate spikes (model errors, timeout errors, validation errors)
   - **Cost monitoring**: alerts for daily/weekly spend exceeding thresholds
   - **Token usage monitoring**: tracking of input/output token consumption per request and in aggregate
   - **Drift detection**: mechanism to detect input distribution shift or model behavior change
   - **Guardrail trigger rate**: monitoring for unusual spikes in guardrail activations
2. Verify dashboards exist or are defined (even if the dashboard spec is in a config file or plan)
3. **Verify alert routing** — for each alert, confirm WHO gets paged, through WHAT channel, with WHAT urgency. Document in the output:

   | Alert | Condition | Who | Channel | Urgency |
   |-------|-----------|-----|---------|---------|
   | Error rate spike | > 5% for 5 min | <person/team> | <Slack/PagerDuty/email> | P1 |
   | Cost spike | > 150% of daily budget | <person/team> | <channel> | P2 |
   | Latency degradation | p95 > 2x baseline | <person/team> | <channel> | P2 |
   | Accuracy drift | eval score drops > 5% | <person/team> | <channel> | P1 |
   | Guardrail spike | trigger rate > 3x normal | <person/team> | <channel> | P2 |

   If any alert has no assigned person or no channel, flag as **FAIL** for that alert.

4. If monitoring is partially configured, list what is missing
5. If no monitoring exists, flag as **BLOCKER**

**Checklist item:** `Monitoring & Alerting` — PASS (all dimensions covered, all alerts routed) / FAIL (gaps or unrouted alerts) / BLOCKER (no monitoring)

### Step 7: Verify Rollback Plan

**Actions:**
1. Check for a documented rollback plan — in `.plans/`, deployment configs, or runbooks
2. Verify the rollback plan covers:
   - **How to revert**: specific steps to roll back to the previous version (code, prompts, model config, data)
   - **Rollback trigger**: conditions under which rollback should be initiated (error rate threshold, accuracy drop, cost spike)
   - **Rollback testing**: has the rollback been tested? (even a dry run counts)
   - **Data rollback**: if the deployment changes data formats, embeddings, or indexes, how to revert those
   - **Rollback time**: estimated time from decision to full rollback
   - **Partial rollback**: can you roll back individual components (e.g., just the prompt, just the model version)?
3. If no rollback plan exists, flag as **BLOCKER**
4. If rollback plan exists but has not been tested, flag as **WARNING**

**Checklist item:** `Rollback Plan` — PASS (documented and tested) / WARNING (documented, not tested) / BLOCKER (no plan)

### Step 8: Check Operational Readiness

**Actions:**
1. **Rate limiting**: verify rate limits are configured for all external-facing endpoints
2. **API keys and credentials**: verify secrets are stored securely (environment variables, secrets manager — not hardcoded)
3. **Fallback behavior**: verify the system degrades gracefully when dependencies fail (model provider down, database unavailable, rate limited)
4. **Environment configuration**: verify environment-specific configs are correct for the target environment AND check for staging/production differences that could cause failures:

   | Setting | Staging Value | Production Value | Match? |
   |---------|-------------|-----------------|--------|
   | Model endpoint | <staging endpoint> | <production endpoint> | <yes/mismatch — flag if different model version> |
   | API keys | <staging key name> | <production key name> | <both valid?> |
   | Database/vector DB | <staging instance> | <production instance> | <same schema? same data freshness?> |
   | Rate limits | <staging limits> | <production limits> | <production more restrictive?> |
   | Feature flags | <staging flags> | <production flags> | <match intended rollout?> |
   | Eval data | <staging test inputs> | <production distribution> | <representative? flag if staging data doesn't match production patterns> |

   Common env-diff traps: staging uses a cheaper model that behaves differently, staging has a stale embedding index, staging rate limits are 10x more generous than production, staging test inputs are all happy-path (no adversarial inputs in production distribution).

5. **Feature flags**: if using feature flags for rollout, verify flag configuration and rollout percentage
6. **Load testing**: has the system been tested under expected peak load? (flag as WARNING if not)
7. **Dependency health**: are all external dependencies (model APIs, databases, third-party services) healthy and accessible from production?

**Checklist item:** `Operational Readiness` — PASS (all verified) / FAIL (issues found) / WARNING (partial verification)

### Step 8b: Risk Mitigation Verification

If `.plans/INVERT-*.md` exists for this deployment, map each HIGH and MEDIUM risk to its mitigation across ALL deployment dimensions — not just guardrails.

| Risk (from /ai-invert) | Severity | Classification | Mitigation | Verified By |
|------------------------|----------|---------------|-----------|-------------|
| <risk name> | HIGH | NEW/AMPLIFIED | <specific mitigation: guardrail, eval test case, monitoring alert, rollback trigger, or operational procedure> | <which checklist item covers it: e.g., Guardrail Validation, Eval Suite case golden-012, Monitoring alert "cost-spike", Rollback trigger "error-rate > 5%"> |

**Rules:**
- Only check NEW and AMPLIFIED risks (PRE-EXISTING risks are not introduced by this deployment)
- Every HIGH risk must have at least one mitigation — unmapped HIGH risks are **BLOCKERS**
- Every MEDIUM risk should have a mitigation — unmapped MEDIUM risks are **WARNINGS**
- Mitigations can come from any dimension: evals, guardrails, monitoring, rollback triggers, operational procedures, or manual review processes

**Checklist item:** `Risk Coverage` — PASS (all HIGH risks mitigated) / FAIL (unmapped HIGH risks) / WARNING (unmapped MEDIUM risks) / N/A (no invert analysis exists)

### Step 9: Client Notification

**Actions:**
1. Determine if this deployment affects client-facing behavior:
   - New features or capabilities visible to clients
   - Changes to existing behavior (output format, response time, accuracy)
   - Downtime or maintenance window required
   - Pricing or usage limit changes
2. If client-facing changes exist:
   - Verify notification draft is prepared (email, changelog entry, in-app notification)
   - Verify notification timing is planned (before, during, or after deployment)
   - Verify support team is briefed on the changes
3. If no client-facing changes, note as "N/A — internal change only"

**Checklist item:** `Client Notification` — PASS (prepared) / N/A (no client-facing changes) / FAIL (needed but not prepared)

### Step 10: Produce Checklist and Write to Disk

**Actions:**
1. Compile all checklist items into a single document with the following structure
2. Create `.plans/` directory if it does not exist
3. Generate a short kebab-case name from the deployment (e.g., `support-classifier-v2`, `rag-pipeline-update`)
4. Write to `.plans/DEPLOY-<name>.md` with this format:

```markdown
# Deployment Checklist: <deployment name>

**Created:** <date>
**Automation:** <brief description of what is being deployed>
**Environment:** <target environment — staging / production>
**Overall Status:** <GO / NO-GO>
**Blockers:** <count> | **Warnings:** <count> | **Passes:** <count>

## Summary

<1-3 sentence summary of deployment readiness. If NO-GO, state the blockers clearly.>

## Checklist

| # | Item | Status | Details |
|---|------|--------|---------|
| 1 | Eval Suite | <PASS/FAIL/BLOCKER> | <details> |
| 2 | Baseline Comparison | <PASS/FAIL/WARNING> | <details> |
| 3 | Guardrail Validation | <PASS/FAIL/BLOCKER> | <details> |
| 4 | Cost Review | <PASS/FAIL/WARNING> | <details> |
| 5 | Monitoring & Alerting | <PASS/FAIL/BLOCKER> | <details> |
| 6 | Rollback Plan | <PASS/FAIL/BLOCKER/WARNING> | <details> |
| 7 | Operational Readiness | <PASS/FAIL/WARNING> | <details> |
| 8 | Risk Coverage (/ai-invert) | <PASS/FAIL/WARNING/N/A> | <details> |
| 9 | Client Notification | <PASS/FAIL/N/A> | <details> |

## Blockers

<List each BLOCKER with details and what must be done to resolve it. If no blockers, state "None — clear to deploy.">

### Blocker 1: <item name>
- **Issue:** <what is missing or failing>
- **Resolution:** <what needs to happen>
- **Owner:** <who should resolve this>
- **Estimated effort:** <time to resolve>

## Warnings

<List each WARNING with details and recommended action. Warnings do not block deployment but should be addressed soon after.>

### Warning 1: <item name>
- **Issue:** <what is incomplete or concerning>
- **Recommended action:** <what to do>
- **Timeline:** <when to address>

## Artifacts Referenced

- <list all .plans/ files consulted during this checklist>

## Deployment Notes

<Any additional context for the person executing the deployment — timing, sequence, feature flags, canary percentage, smoke test steps after deployment.>

## Post-Deployment Verification

- [ ] Smoke test: <specific test to run immediately after deployment>
- [ ] Monitor error rate for <duration> after deployment
- [ ] Monitor latency p95 for <duration> after deployment
- [ ] Monitor cost for <duration> after deployment
- [ ] Verify guardrails are active in production (send test inputs)
- [ ] Confirm alerts are firing correctly (trigger a test alert if possible)
```

5. **GO / NO-GO determination:**
   - If ANY item is **BLOCKER**: overall status is **NO-GO**
   - If no blockers but warnings exist: overall status is **GO with warnings**
   - If all items are PASS or N/A: overall status is **GO**
6. Inform the user: "Deployment checklist saved to `.plans/DEPLOY-<name>.md` — Status: <GO/NO-GO>"

## Notes

- This skill is language-agnostic and framework-agnostic — it verifies readiness, not implementation details
- Read actual code, configs, and `.plans/` artifacts before making pass/fail judgments — never assess based on assumptions
- A BLOCKER means deployment must not proceed until the issue is resolved. Do not soften blockers to warnings for convenience
- A WARNING means deployment can proceed but the issue should be tracked and addressed promptly
- If referenced artifacts (eval results, baselines, guardrail reports) do not exist, that is itself a signal — flag it appropriately based on risk level
- This checklist is a snapshot in time. If significant changes are made after the checklist is generated, re-run the checklist
- The checklist output feeds into team review — keep the language precise and actionable, not vague
- For incremental deployments (canary, blue-green), note the deployment strategy in the Deployment Notes section
- Cross-reference with `/incident-playbook` if one exists — the playbook should cover failure modes for this specific deployment
- If this is a first deployment (no prior version in production), the baseline check becomes "establish baseline" rather than "compare to baseline"
