#!/usr/bin/env python3
"""Offline CharterCore preflight.

This does not replace GenVM Direct Mode. It makes the repository auditable even
on a machine without the GenLayer runtime by checking Python syntax, expected
contract surface, consensus boundaries, and deterministic semantic normalization
helpers through a minimal import stub.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "charter.py"


class _Generic:
    @classmethod
    def __class_getitem__(cls, _item):
        return cls


class _Map(dict, _Generic):
    pass


class _Array(list, _Generic):
    pass


class _Int(int):
    pass


class _Address(str):
    pass


class _Keccak:
    def __init__(self, data: bytes):
        self._data = data

    def hexdigest(self) -> str:
        return hashlib.sha3_256(self._data).hexdigest()


class _Decorator:
    def __call__(self, fn):
        return fn

    @property
    def payable(self):
        return self


class _Public:
    view = _Decorator()
    write = _Decorator()


class _Event:
    def emit(self):
        return None


class _Return:
    def __init__(self, calldata=None):
        self.calldata = calldata


class _VM:
    Return = _Return


class _Message:
    sender_address = _Address("0x0000000000000000000000000000000000000001")
    raw = types.SimpleNamespace(datetime="2026-01-01T00:00:00+00:00")


class _GL:
    Contract = object
    Event = _Event
    public = _Public()
    vm = _VM()
    message = _Message()

    @staticmethod
    def contract_interface(cls):
        return cls


def _install_stub() -> None:
    module = types.ModuleType("genlayer")
    module.gl = _GL()
    module.allow_storage = lambda cls: cls
    module.TreeMap = _Map
    module.DynArray = _Array
    module.u8 = _Int
    module.u32 = _Int
    module.u256 = _Int
    module.Address = _Address
    module.Keccak256 = _Keccak
    sys.modules["genlayer"] = module


def _load_contract():
    _install_stub()
    spec = importlib.util.spec_from_file_location("charter_contract", CONTRACT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ast_checks(source: str) -> list[str]:
    tree = ast.parse(source)
    class_names = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    fn_names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

    required_classes = {"CharterCore", "Charter", "Clause", "Relation", "ICharterCore"}
    required_methods = {
        "create_charter", "propose_clause", "set_blocked_clause_priority",
        "activate_blocked_clause", "repeal_clause", "restore_superseded_clause",
        "get_charter", "get_clause", "get_relation", "relation_between",
        "get_active_clauses", "blocking_reason", "is_consistent", "is_consistent_for",
        "current_charter_hash",
    }

    checks = []
    assert required_classes <= class_names, required_classes - class_names
    checks.append("required storage/interface classes present")
    assert required_methods <= fn_names, required_methods - fn_names
    checks.append("public lifecycle and consumer surface present")
    assert source.count("gl.vm.run_nondet_unsafe") == 2
    checks.append("exactly two explicit custom consensus boundaries")
    assert "CHARTERCORE / INDEPENDENTLY NORMALIZE CLAUSE" in source
    assert "CHARTERCORE / COMPARE INDEPENDENT NORMALIZATIONS" in source
    assert "CHARTERCORE / INDEPENDENTLY CLASSIFY CLAUSE RELATION" in source
    checks.append("validator prompts independently verify leader semantics and relations")
    assert "Priority is NOT part of this semantic judgement" in source
    checks.append("semantic conflict detection separated from deterministic precedence")
    assert "MAX_CLAUSES_PER_BOOK = 24" in source
    checks.append("pairwise consensus cost is explicitly bounded")
    assert "charter_hash" in source and "is_consistent_for" in source
    checks.append("cross-contract charter pinning surface present")
    return checks


def _helper_checks(c) -> list[str]:
    checks = []
    sem = c.charter_semantics({
        "atomic": True,
        "modality": "PROHIBIT",
        "actor": " treasury   operator ",
        "action": "execute withdrawal",
        "object": "funds",
        "condition": "fewer than three approvals",
        "exception": "",
        "scope": "treasury",
        "ambiguity": "CLEAR",
        "ambiguity_reason": "",
    })
    assert sem["modality"] == c.MODALITY_PROHIBIT
    assert sem["actor"] == "treasury operator"
    assert sem["semantic_state"] == c.SEMANTIC_CLEAR
    assert len(sem["semantic_hash"]) == 64
    assert c.valid_semantics_shape(sem)
    checks.append("clear atomic semantics normalize and hash")

    ambiguous = c.charter_semantics({
        "atomic": False,
        "modality": "REQUIRE",
        "actor": "council",
        "action": "act",
        "ambiguity": "CLEAR",
    })
    assert ambiguous["semantic_state"] == c.SEMANTIC_AMBIGUOUS
    assert ambiguous["ambiguity_reason"] == "NON_ATOMIC_OR_UNCLEAR"
    checks.append("non-atomic input fails closed to AMBIGUOUS")

    rel = c.charter_relation({
        "relation": "CONFLICT",
        "conflict_type": "MODAL",
        "overlap": " emergency   withdrawal ",
        "reason_code": "permission prohibition clash",
    })
    assert rel["kind"] == c.REL_CONFLICT
    assert rel["conflict_type"] == c.CONFLICT_MODAL
    assert rel["overlap"] == "emergency withdrawal"
    assert c.valid_relation_shape(rel)
    checks.append("conflict relation normalizes into bounded enums")

    nonconflict = c.charter_relation({
        "relation": "COMPATIBLE",
        "conflict_type": "MODAL",
        "overlap": "same domain",
        "reason_code": "compatible",
    })
    assert nonconflict["conflict_type"] == c.CONFLICT_NONE
    checks.append("non-conflicts cannot smuggle a conflict subtype")

    assert c.pair_key(7, 9, 2) == c.pair_key(7, 2, 9) == "7:2:9"
    checks.append("relation lookup keys are order-independent")
    assert c.clause_status_name(c.CLAUSE_ACTIVE) == "ACTIVE"
    assert c.relation_name(c.REL_CONFLICT) == "CONFLICT"
    assert c.resolution_name(c.RES_UNRESOLVED) == "UNRESOLVED"
    checks.append("consumer-facing enum names are stable")
    return checks


def main() -> int:
    source = CONTRACT.read_text(encoding="utf-8")
    compile(source, str(CONTRACT), "exec")
    checks = ["contract compiles as Python"]
    checks += _ast_checks(source)
    contract = _load_contract()
    checks += _helper_checks(contract)

    print(f"CharterCore offline preflight: {len(checks)}/{len(checks)} checks passed")
    for index, check in enumerate(checks, 1):
        print(f"  {index:02d}. PASS - {check}")
    print("\nGenVM consensus/runtime behavior is covered separately by tests/test_charter.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
