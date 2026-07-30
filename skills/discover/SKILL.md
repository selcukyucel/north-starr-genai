---
name: discover
description: Run a minimum-complexity client discovery conversation when no Vignola handoff exists. Ask at most 12 plain-language questions one at a time, accept answered/unknown/deferred responses with optional evidence, separate client facts from architect interpretation, and emit a machine-readable discovery artifact ready for intake validation.
---

# Discover — 12-Question Client Spine

Use this as the conversational fallback when the client has no Vignola handoff.
If a Vignola handoff exists, use the sibling `intake` skill instead.

## Conversation rules

- Ask one question at a time.
- Use the client's language. Do not introduce architecture terminology.
- Accept a plain answer, `unknown`, or `deferred`.
- Offer optional evidence only when it is useful.
- Confirm the captured meaning before moving on when the answer is ambiguous.
- Do not insert your own recommendation into the client's answer.
- Keep architect inferences and assumptions in separate fields.
- Do not ask technical catalogue questions automatically.

Six resolved questions are enough for an explicitly `provisional` intake. All
twelve are recommended. Unknown and deferred count as resolved states but
remain visible.

## The 12 questions

Ask these in order, adapting only the short conversational lead-in:

1. What problem are we trying to solve, and who is affected?
2. How is this work handled today, from start to finish?
3. If this succeeds, what should improve, and how would you notice?
4. Who will use, operate, approve, or be affected by the system?
5. What everyday, difficult, and unsafe examples should it handle?
6. What must the first release do, and deliberately leave out?
7. What information and systems are needed, and which sources are
   authoritative?
8. What may each user see or do, and what must remain out of reach?
9. What could go wrong, what must never happen, and what should happen under
   uncertainty or failure?
10. What makes a result correct, useful, complete, and testable?
11. What response time, usage, availability, budget, and delivery constraints
    apply?
12. Who owns the outcome, operation, remaining risk, and authority to stop or
    restore the service?

## Capture

For each response, store:

- `question_id`: `INTAKE-001` through `INTAKE-012`;
- the exact question text;
- `status`: `answered`, `unknown`, or `deferred`;
- `answer`: client wording, or null for unknown/deferred;
- optional evidence references and content hashes;
- speaker/owner when known;
- separate `architect_notes`, each labeled `inference` or `assumption`.

Never mark inferred requirements, proposed thresholds, or polished summaries as
client-confirmed.

## Review

After question 6, offer a provisional review:

- confirmed client answers;
- architect assumptions;
- unknown/deferred items;
- conflicts;
- no more than three important follow-ups.

After question 12, show the same groups and ask the client to correct the
capture. This is confirmation of discovery content, not architecture approval.

## Output

Write:

- `.north-starr/discovery.json`
- `.north-starr/discovery.md`

The JSON must validate against `../../schemas/discovery.schema.json`. Include
the exact 12-question catalogue, response states, evidence hashes, source
hashes, and human boundary. The Markdown is a concise client-readable rendering
with no internal IDs in its visible headings.

Then run the sibling `intake` skill against the JSON and recommend `assess`
only after intake validation.

## Boundaries

- Do not recommend AI, RAG, agents, SDKs, models, or infrastructure during the
  meeting.
- Do not turn missing numbers into invented targets.
- Do not exceed twelve client questions unless the client explicitly requests
  a deeper session.
- Do not approve architecture or implementation.
