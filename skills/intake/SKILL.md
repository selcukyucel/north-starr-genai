---
name: intake
description: Validate Vignola North Starr handoffs, discovery JSON, transcripts, or briefs before AI architecture work. Separate confirmed facts from assumptions, unknowns, deferred items, and conflicts; detect stale evidence; preserve MCP/tool mentions; and emit a machine-readable intake validation with no more than three blocking follow-ups.
---

# Intake — Evidence Gate

Turn discovery material into trustworthy architecture input. Do not design the
solution in this skill.

## Inputs

Accept one or more of:

- a Vignola `north_starr_handoff` JSON or Markdown export;
- a Vignola three-file export bundle containing `client-summary.json`,
  `architecture-profile.json`, and `north-starr-handoff.json`;
- a North Starr discovery artifact;
- a transcript, brief, PRD, or requirement;
- corrections or evidence supplied later.

When a file is provided, hash the exact bytes with SHA-256 before interpreting
it. Preserve its path, declared schema version, and hash.

When any member of the standard Vignola three-file bundle is supplied, inspect
all three sibling files. Treat `client-summary.json` as the client-response
view, `architecture-profile.json` as architect-authored interpretation, and
`north-starr-handoff.json` as the integration envelope. Do not collapse these
evidence levels into one.

For every source artifact record its `role` and `evidence_level`. For every
claim record whether it came from client words, client confirmation, a
transcript, architect interpretation, a system artifact, or external evidence,
plus the speaker or authority when known.

## Efficient bundle reading

Do not dump or reread the full three-file bundle. The exports deliberately
overlap and may contain long answers.

1. Run the handoff and bundle validators first.
2. Inspect a compact projection: top-level keys, hashes, engagement/profile
   status, response counts/statuses/questions, card statuses/evidence refs,
   recommendation, artifact references, and human boundaries.
3. Read client answers from `client-summary.json` once. Read only the specific
   answer needed for the current classification pass.
4. Read architect interpretation from `architecture-profile.json`; do not
   reread the duplicated profile embedded in the handoff.
5. Use `north-starr-handoff.json` for the envelope, hashes, references, and
   integration summary, not as a second copy of the client answers.
6. For a read-only envelope check, stop after structural validation and the
   requested concise semantic gaps. Do not perform a full intake synthesis.

Never run an unfiltered whole-file pretty print on all three exports.

## Workflow

### 1. Validate the envelope

For a Vignola JSON handoff, check it against
`../../schemas/vignola-handoff-0.1.0.schema.json`. When available, run:

```bash
python3 <plugin-root>/scripts/validate_artifacts.py handoff <path>
```

For the three-file export, run:

```bash
python3 <plugin-root>/scripts/validate_artifacts.py bundle <directory>
```

The bundle check requires the same engagement/profile state across the
architecture profile and handoff, the exact ordered 12-question client
catalogue, valid response/source-hash states, and a human boundary in every
client-facing or architect-authored export.

Reject malformed JSON, unsupported schema versions, invalid hash formats, or a
missing human boundary. A structurally valid file can still contain weak
evidence; continue to semantic validation.

### 2. Classify every material claim

Use only these states:

- `confirmed_fact` — explicitly stated or directly evidenced by an identified
  source;
- `inference` — a reasonable interpretation not confirmed by the client;
- `assumption` — a value proposed to let work continue;
- `unknown` — needed information is unavailable;
- `deferred` — intentionally postponed with an owner or future checkpoint;
- `conflict` — sources disagree or one answer contradicts another.

Do not treat `status: answered`, polished prose, or an architect selection as
proof that a claim is client-confirmed. Phrases such as “appears,” “likely,”
“inferred,” “should,” “must,” “near real time,” “high availability,” and
“large volume” require explicit evidence or remain inference/assumption.

Keep source wording separate from interpretation. Never silently convert an
inference into a requirement.

### 3. Check architecture readiness

Assess whether the evidence supports decisions about:

1. problem, affected people, and desired outcome;
2. current workflow and MVP boundary;
3. users, owners, and human authority;
4. authoritative data and systems;
5. tool or MCP access and side effects;
6. quality examples and evaluation criteria;
7. privacy, security, compliance, and forbidden outcomes;
8. latency, volume, availability, budget, and delivery constraints.

Six resolved client prompts can support a `provisional` intake. Twelve resolved
prompts support `ready` only when material conflicts and decision-blocking
unknowns are absent. Unknown and deferred are valid answers; they remain
visible.

### 4. Preserve integration and MCP signals

For every mentioned API, database, application, MCP server, connector, or
tool, record:

- name and authoritative owner;
- evidence references;
- whether the interface is a confirmed fact, inference, assumption, unknown, or
  conflict;
- what is missing: endpoint, transport, authentication, scopes, tenant/app
  boundary, tool allowlist, read/write authority, rate limits, timeout, or
  failure behavior.

Do not invent tools from a vendor's general product capabilities.

### 5. Ask only blocking follow-ups

Ask at most three questions. A question is blocking only when its answer can
change the recommended system shape, data boundary, human authority, or ability
to evaluate the first release. Group related gaps into one plain-language
question.

Continue provisionally when the unresolved item can be represented as an
assumption with an owner and validation checkpoint.

### 6. Write dual-format output

Create:

- `.north-starr/intake-validation.json`
- `.north-starr/intake-validation.md`

The JSON must validate against
`../../schemas/intake-validation.schema.json`. The Markdown is a concise view
of the same facts and must show:

1. readiness: `provisional`, `ready`, `blocked`, or `stale`;
2. confirmed facts;
3. assumptions and inferences;
4. unknowns, deferred items, and conflicts;
5. known systems/tools and missing interface details;
6. up to three blocking follow-ups;
7. source hashes and the human boundary.

Set freshness to `current`, `stale`, or `unknown`, with the time checked. If a
prior intake exists and an upstream hash changes, set the prior result to
`stale`; do not reuse its architecture readiness without revalidation. Missing
underlying source material is `unknown`, not falsely current.

## Boundaries

- Do not select a model, SDK, RAG design, agent topology, or infrastructure.
- Do not mark transcript-derived interpretation as client-confirmed.
- Do not erase unknowns because the prose sounds complete.
- Do not approve architecture or authorize implementation.
- Do not make network calls merely to fill missing client evidence.

Return the output paths and recommend the sibling `assess` skill as the next
step when the intake is `provisional` or `ready`.
