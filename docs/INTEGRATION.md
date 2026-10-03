# Clause_Graph Integration Guide

## Consumer pattern: pin a constitution

A downstream contract can store:

```text
charter_id
expected_charter_hash
```

Before a sensitive transition, it calls Clause_Graph:

```python
charter = IClause_Graph(charter_address)
valid = charter.view().is_consistent_for(charter_id, expected_charter_hash)
```

If `valid` is false, the consumer can fail closed because either the charter is inconsistent or active charterical state changed since the consumer pinned it. For a resolved-conflict charter, also inspect `charter_status` and `get_charter_links` before executing an action in an affected scope.

## Consumer pattern: inspect current charter

`get_active_clauses(charter_id)` returns active clauses with normalized semantics and priority.

`get_charter_links(charter_id)` returns the bounded active-active graph,
including relation kind, semantic hashes, and deterministic conflict resolution.
Consumers must read this view when resolved conflicts are meaningful to execution.

`charter_status(charter_id)` makes the distinction explicit:

- `COHERENT`: no active conflict or ambiguity;
- `RESOLVED_CONFLICTS`: conflicts exist, but every active conflict has deterministic precedence;
- `UNRESOLVED`: at least one active conflict has no deterministic winner;
- `AMBIGUOUS`: at least one active relation is semantically ambiguous.

`consistent=true` means no unresolved or ambiguous active relation. It does not
mean that no conflict edge exists.

A consumer can use this as trusted shared context for a separate adjudication contract without repeating normalization work.

## Consumer pattern: inspect a conflict

`relation_between(left_clause_id, right_clause_id)` exposes semantic relation, conflict subtype, overlap description, deterministic resolution, and semantic hashes used by the edge.

This is useful for governance tooling or another Intelligent Contract deciding whether a candidate action enters a disputed part of the clause graph.

## Ownership composition

The charter owner is an address. It can be a normal account or another contract-controlled address depending on the governance architecture.

Clause_Graph itself does not implement voting. It is intentionally a primitive for semantic consistency and charter state.

## Recommended integration invariant

For high-stakes consumers, pin all of:

1. Clause_Graph contract address;
2. charter ID;
3. expected charter hash.

Do not trust only a human-readable charter name.

## Version handling

`revision` changes for any persisted charter governance change.

`charter_version` changes only when active charterical state changes.

Consumers interested only in operative clauses should track `charter_version` and `charter_hash`. Audit systems interested in failed or blocked proposals may also track `revision`.
