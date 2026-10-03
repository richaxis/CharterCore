# Clause_Graph Architecture

## Design objective

Clause_Graph is designed as a reusable semantic-consistency primitive, not as a policy application.

The contract owns a versioned graph in which clause text, semantic interpretation, pairwise relations, deterministic precedence, lifecycle status, and consumer-facing charter hashes are all explicit on-chain state.

## Layer separation

Clause_Graph has three layers.

### Layer 1: immutable source nodes

A `Clause` begins with authoritative text submitted by the charter owner. The text is stored permanently with a Keccak hash.

Clause_Graph does not provide an edit method. Semantic amendments are represented by new nodes. This prevents history from being rewritten underneath old relation receipts.

### Layer 2: consensus semantic graph

GenLayer consensus handles two questions that ordinary deterministic code cannot safely answer for arbitrary prose:

1. What atomic norm does this text express?
2. What is the semantic relationship between two clause nodes?

Those answers are bounded into enums and short charterical fields before storage.

### Layer 3: deterministic governance mechanics

Priority, admission, versioning, supersession, repeal, restoration, counts, consistency, and charter hashing are deterministic.

This keeps normative authority outside the model.

## Charter lifecycle

```text
create_charter
      |
      v
 empty charter
      |
      v
 propose_clause
      |
      +--> normalize by consensus
      |
      +--> compare with every live historical node
      |
      +--> persist relation edges
      |
      +--> deterministic blocker evaluation
                 |
          +------+------+
          |             |
        ACTIVE        BLOCKED
          |             |
          |         priority change
          |             |
          |         activate_blocked_clause
          |             |
          +-------------+
          |
      repeal / supersede
```

## Why blocked nodes stay in the graph

A blocked clause may later become activatable because governance changes its explicit priority or because another active clause is repealed.

If blocked nodes were ignored by later proposals, a previously blocked clause could eventually be activated without ever being compared to clauses added after it.

Clause_Graph avoids that gap by comparing each candidate against every currently live historical node, including `BLOCKED` nodes.

That invariant allows deterministic later activation without rerunning old semantic interpretation.

## Strict versus permissive charter

Strict mode is appropriate when downstream systems want a fail-closed clause set. Unresolved semantic relationships cannot enter active charter.

Permissive mode is useful for drafting, research, and governance processes that want unresolved conflicts to remain visible in active state.

The mode is immutable per charter so consumers know the admission policy that produced the charter hash.

## Clause_Graph version versus revision

`revision` tracks every persisted governance change, including blocked proposals and blocked-clause priority changes.

`charter_version` changes only when active charterical state changes.

This distinction prevents a rejected proposal from falsely appearing as a new constitution version while still preserving complete charter history.

## Clause_Graph hash contents

The hash includes active clauses and active-active relation edges. Blocked, repealed, and superseded nodes remain queryable but do not alter current charter.

This allows a consumer to pin exactly the clause system it depended upon.

## Complexity bound

A complete pairwise graph grows quadratically. Clause_Graph therefore limits each
charter to 24 nodes: at most 276 unique edges and at most 23 comparisons for
the 24th proposal. Superseded nodes remain in the bounded historical comparison
set because they may be restored later; repealed nodes remain excluded because
there is no repeal-restoration operation.

The contract treats semantic partitioning as part of architecture: large policy systems should use multiple coherent charters instead of a single unbounded graph.
