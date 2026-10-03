# CharterCore

CharterCore is a GenLayer Intelligent Contract for building machine-readable operating charters for autonomous protocols and agents.

Instead of treating natural-language policy as an opaque string, CharterCore turns each clause into a consensus-checked semantic record. New clauses are compared against the existing charter, classified for compatibility or conflict, and assigned deterministic precedence when a conflict can be resolved by priority.

## Why it exists

Autonomous systems need policies that can be inspected and verified by other contracts. A plain text policy is difficult for a contract to interpret consistently. CharterCore creates a persistent semantic layer between natural-language clauses and downstream contract logic.

## Core primitive

A charter contains immutable clauses. Each clause has:

- a semantic interpretation established through GenLayer consensus
- a status and priority
- a content digest and semantic digest
- pairwise compatibility records with other active clauses
- conflict classification when applicable
- amendment and supersession lineage

The contract can expose a stable charter digest that another contract can pin before acting.

## Consensus model

1. A proposer submits a natural-language clause.
2. Validators independently normalize the clause into a constrained semantic schema.
3. The contract validates the returned schema and semantic digest.
4. The new clause is compared against active clauses through independent semantic classification.
5. Conflict subtype and relationship must satisfy the contract's equivalence checks.
6. Deterministic priority resolves resolvable conflicts; unresolved conflicts remain blocked in strict mode.

The contract never treats a model response as authoritative merely because it is syntactically valid.

## Repository

- `contracts/charter.py` — Intelligent Contract
- `tests/test_charter.py` — Direct Mode tests
- `docs/ARCHITECTURE.md` — state and lifecycle
- `docs/CONSENSUS.md` — validator and equivalence design
- `docs/INTEGRATION.md` — downstream integration
- `docs/THREAT_MODEL.md` — failure and adversarial cases
- `frontend/` — static builder dashboard

## Important

This repository contains a deployment template, not a fabricated live deployment receipt. Run the tests and deploy the contract through the current GenLayer tooling before publishing an address.
