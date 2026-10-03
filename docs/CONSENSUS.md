# Clause_Graph Consensus Model

## Why custom validation is necessary

Two validators can faithfully interpret the same prose with slightly different wording. Exact string equality over actor/action summaries would reject many substantively equivalent interpretations.

Clause_Graph therefore uses two bounded consensus calls with `gl.vm.run_nondet_unsafe`.

The leader derives a bounded result. The validator independently derives the material answer from the original source data before comparing protocol-relevant facts. This reduces anchoring on the leader candidate without making unstable explanatory prose part of equivalence.

## Boundary 1: normalization

### Leader task

The leader receives immutable charter purpose and immutable candidate clause text, then proposes one charterical semantic object:

```json
{
  "modality": "REQUIRE | PERMIT | PROHIBIT",
  "actor": "...",
  "action": "...",
  "object": "...",
  "condition": "...",
  "exception": "...",
  "scope": "...",
  "semantic_state": "CLEAR | AMBIGUOUS"
}
```

### Deterministic chartericalization

Before storage, the result is converted to bounded enums and strings.

A missing actor/action, unknown modality, or non-atomic clause fails closed to `AMBIGUOUS`.

### Validator task

The validator independently normalizes the original purpose and clause text. The leader and validator must agree on the protocol semantic state: CLEAR versus AMBIGUOUS. A disagreement in either direction rejects that leader proposal, so neither an overconfident CLEAR nor a leader-only conservative AMBIGUOUS state is finalized. For shared CLEAR state, deterministic checks compare modality, and whether a material condition or explicit exception is present; a bounded equivalence call then checks actor, action, object, condition, exception, and scope for substantive agreement. Minor wording differences are allowed; a missing or invented material fact is rejected. Shared AMBIGUOUS state is accepted without requiring identical ambiguity prose. The validator returns only a boolean acceptance decision.


## Boundary 2: relation analysis

### Leader task

The leader receives two immutable clause texts and their accepted semantic records and proposes one relation enum:

- `UNRELATED`
- `COMPATIBLE`
- `REDUNDANT`
- `SPECIALIZES`
- `CONFLICT`
- `AMBIGUOUS`

A conflict requires a plausible shared case in which both clauses apply but cannot both be satisfied.

### Validator task

The validator independently classifies the relationship from both original clause texts, both accepted semantic records, and the charter purpose. Consensus compares the authoritative relation kind only. `conflict_type`, `overlap`, and `reason_code` are explanatory metadata; they remain available in public relation views but are not used for admission, precedence, lifecycle, or `charter_hash`. A validator-derived `AMBIGUOUS` result fails closed against any confident leader classification; the leader must also be ambiguous for that edge to pass.

## Precedence is not consensus output

Priority is intentionally excluded from relation prompts.

After a `CONFLICT` edge is accepted, deterministic code resolves it using explicit stored priority or declared supersession.

This prevents validators or an LLM from becoming an implicit constitutional authority.

## Prompt-injection boundary

Charter purpose, clause text, and candidates are wrapped as untrusted data and prompts explicitly instruct the model not to obey instructions inside those blocks.

The same source material is re-presented to independent validators, so a leader cannot unilaterally exploit injected instructions to determine accepted state.

Clause_Graph still treats prompt injection as a model-layer risk, which is why outputs are bounded, validator-reviewed, and unable to choose priority.

## Consensus failure behavior

If validators reject a leader result, the transaction does not safely finalize with that semantic state.

The contract does not silently coerce rejected or malformed outputs into active charter.
