#!/usr/bin/env python3
"""Independently verify provisional missing-Q candidates with proof-producing SAT.

The SAT encoding uses selected-edge variables, exact degree constraints, a
binary component assignment fixed by the requested terminal pairing, and lazy
connectivity cuts. Positive models are independently validated as two spanning
paths. If the accumulated relaxation is UNSAT, the final CNF is solved again by
an independent proof-producing solver and the resulting DRAT proof is checked
with drat-trim before the state is classified as a certified negative.

Because the accumulated CNF is a relaxation of the exact connected-pair-cover
problem, a checked UNSAT proof is sufficient evidence that the requested Q
state does not exist. A timeout or proof-check failure remains unknown.
"""
from __future__ import annotations

import argparse
import itertools
import json
import platform
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import networkx as nx
from pysat.solvers import Solver

import patch_gluing_search as pl


def exactly_k_small(lits: list[int], k: int) -> list[list[int]]:
    """CNF for exact-k, optimized for the degree-2/3 lists used here."""
    n = len(lits)
    if k < 0 or k > n:
        return [[]]
    clauses: list[list[int]] = []
    for subset in itertools.combinations(lits, k + 1):
        clauses.append([-lit for lit in subset])
    for subset in itertools.combinations(lits, n - k + 1):
        clauses.append(list(subset))
    return clauses


def validate_q_witness(
    patch: nx.Graph,
    terminals: tuple[int, int, int, int],
    pairing: pl.Pairing,
    selected: list[tuple[int, int]],
) -> dict[str, Any]:
    edge_set = {pl.ce(*edge) for edge in selected}
    patch_edges = {pl.ce(*edge) for edge in patch.edges()}
    H = nx.Graph()
    H.add_nodes_from(patch)
    H.add_edges_from(edge_set)
    terminal_set = set(terminals)
    degree_ok = all(H.degree(v) == (1 if v in terminal_set else 2) for v in patch)
    components = list(nx.connected_components(H))
    actual_pairs = []
    for component in components:
        ids = sorted(i for i, terminal in enumerate(terminals) if terminal in component)
        if len(ids) == 2:
            actual_pairs.append(tuple(ids))
    actual = pl.canonical_pairing(actual_pairs) if len(actual_pairs) == 2 else None
    expected = pl.canonical_pairing(pairing)
    result = {
        "all_edges_in_patch": edge_set <= patch_edges,
        "edge_count": len(edge_set),
        "expected_edge_count": patch.number_of_nodes() - 2,
        "degree_constraints": degree_ok,
        "components": len(components),
        "actual_pairing": actual,
        "expected_pairing": expected,
        "pairing_matches": actual == expected,
    }
    result["valid"] = (
        result["all_edges_in_patch"]
        and result["edge_count"] == result["expected_edge_count"]
        and result["degree_constraints"]
        and result["components"] == 2
        and result["pairing_matches"]
    )
    return result


def write_dimacs(path: Path, clauses: list[list[int]]) -> int:
    max_var = max((abs(lit) for clause in clauses for lit in clause), default=0)
    with path.open("w", encoding="ascii") as handle:
        handle.write(f"p cnf {max_var} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    return max_var


def write_proof(path: Path, proof: Any) -> int:
    if proof is None:
        path.write_text("", encoding="ascii")
        return 0
    lines = proof if isinstance(proof, (list, tuple)) else [proof]
    normalized = []
    for line in lines:
        if isinstance(line, bytes):
            line = line.decode("ascii")
        text = str(line).strip()
        if text:
            normalized.append(text)
    path.write_text("\n".join(normalized) + ("\n" if normalized else ""), encoding="ascii")
    return len(normalized)


def solve_case(
    case: dict[str, Any],
    output_dir: Path,
    solver_name: str,
    drat_trim: str | None,
    proof_solver: str | None,
) -> dict[str, Any]:
    case_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", case["case_id"])
    case_dir = output_dir / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    parent = nx.from_graph6_bytes(case["parent_graph6"].encode("ascii"))
    patch = parent.subgraph(case["patch_nodes"]).copy()
    spec_raw = case["spec"]
    terminals = tuple(int(x) for x in spec_raw["terminals"])
    pairing = pl.pairing_from_key(case["state"])
    (i0, i1), (j0, j1) = pairing
    a, b = terminals[i0], terminals[i1]
    c, d = terminals[j0], terminals[j1]

    edges = sorted(pl.ce(*edge) for edge in patch.edges())
    edge_var = {edge: index + 1 for index, edge in enumerate(edges)}
    node_var = {v: len(edges) + index + 1 for index, v in enumerate(sorted(patch))}
    clauses: list[list[int]] = []

    terminal_set = set(terminals)
    for v in patch:
        incident = [edge_var[pl.ce(v, w)] for w in patch.neighbors(v)]
        clauses.extend(exactly_k_small(incident, 1 if v in terminal_set else 2))

    for (u, v), x in edge_var.items():
        zu, zv = node_var[u], node_var[v]
        clauses.append([-x, -zu, zv])
        clauses.append([-x, zu, -zv])

    clauses.extend([[node_var[a]], [node_var[b]], [-node_var[c]], [-node_var[d]]])

    started = time.time()
    rounds = 0
    added_cut_clauses = 0
    known_cuts: set[tuple[int, ...]] = set()
    outcome: dict[str, Any]

    with Solver(name=solver_name, bootstrap_with=clauses, with_proof=True) as solver:
        while True:
            rounds += 1
            satisfiable = solver.solve()
            if not satisfiable:
                cnf_path = case_dir / "instance.cnf"
                proof_path = case_dir / "proof.drat"
                write_dimacs(cnf_path, clauses)
                if proof_path.exists():
                    proof_path.unlink()

                proof_generation = {
                    "attempted": bool(proof_solver),
                    "command": None,
                    "returncode": None,
                    "stdout": "",
                    "stderr": "",
                    "unsat_exit_code": False,
                    "proof_bytes": 0,
                }
                if proof_solver:
                    # CaDiCaL usage is `cadical [ dimacs [ proof ] ]`.
                    # Its default proof format is binary; force textual DRAT so
                    # the evidence is portable and directly checked by
                    # drat-trim.
                    command = [
                        proof_solver,
                        "--no-binary",
                        str(cnf_path),
                        str(proof_path),
                    ]
                    generated = subprocess.run(
                        command,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=600,
                        check=False,
                    )
                    proof_generation.update(
                        {
                            "command": command,
                            "returncode": generated.returncode,
                            "stdout": generated.stdout[-8000:],
                            "stderr": generated.stderr[-8000:],
                            "unsat_exit_code": generated.returncode == 20,
                            "proof_bytes": (
                                proof_path.stat().st_size if proof_path.exists() else 0
                            ),
                        }
                    )
                else:
                    # Diagnostic fallback only. Some PySAT backends expose no
                    # proof. This path can never certify a negative unless the
                    # independent checker below accepts the resulting file.
                    write_proof(proof_path, solver.get_proof())
                    proof_generation["proof_bytes"] = proof_path.stat().st_size

                verification = {
                    "attempted": bool(drat_trim),
                    "returncode": None,
                    "stdout": "",
                    "stderr": "",
                    "verified": False,
                }
                if (
                    drat_trim
                    and proof_path.exists()
                    and proof_path.stat().st_size > 0
                    and (not proof_solver or proof_generation["unsat_exit_code"])
                ):
                    process = subprocess.run(
                        [drat_trim, str(cnf_path), str(proof_path)],
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=600,
                        check=False,
                    )
                    verification.update(
                        {
                            "returncode": process.returncode,
                            "stdout": process.stdout[-8000:],
                            "stderr": process.stderr[-8000:],
                            "verified": process.returncode == 0,
                        }
                    )
                classification = (
                    "certified_negative"
                    if verification["verified"]
                    else "provisional_negative"
                )
                outcome = {
                    "classification": classification,
                    "sat": False,
                    "cnf": str(cnf_path),
                    "proof": str(proof_path),
                    "proof_generation": proof_generation,
                    "proof_verification": verification,
                }
                break

            model = set(lit for lit in solver.get_model() if lit > 0)
            selected = [edge for edge, variable in edge_var.items() if variable in model]
            validation = validate_q_witness(patch, terminals, pairing, selected)
            if validation["valid"]:
                witness_path = case_dir / "sat_witness.json"
                witness = {
                    "case_id": case["case_id"],
                    "state": case["state"],
                    "selected_edges": selected,
                    "validation": validation,
                }
                witness_path.write_text(json.dumps(witness, indent=2), encoding="utf-8")
                outcome = {
                    "classification": "verified_positive",
                    "sat": True,
                    "witness": str(witness_path),
                    "witness_validation": validation,
                }
                break

            z1 = {v for v, variable in node_var.items() if variable in model}
            z0 = set(patch) - z1
            selected_graph = nx.Graph()
            selected_graph.add_nodes_from(patch)
            selected_graph.add_edges_from(selected)
            new_clauses: list[list[int]] = []

            for group, root, zero_group in ((z1, a, False), (z0, c, True)):
                subgraph = selected_graph.subgraph(group)
                for component in nx.connected_components(subgraph):
                    if root in component:
                        continue
                    crossing = [
                        edge_var[pl.ce(u, v)]
                        for u in component
                        for v in patch.neighbors(u)
                        if v not in component
                    ]
                    membership_guard = [
                        node_var[v] if zero_group else -node_var[v] for v in component
                    ]
                    clause = membership_guard + sorted(set(crossing))
                    key = tuple(sorted(clause))
                    if key not in known_cuts:
                        known_cuts.add(key)
                        new_clauses.append(clause)

            if not new_clauses:
                outcome = {
                    "classification": "unknown",
                    "sat": True,
                    "reason": (
                        "SAT model failed exact witness validation but yielded "
                        "no new valid connectivity cut"
                    ),
                    "witness_validation": validation,
                }
                break
            for clause in new_clauses:
                clauses.append(clause)
                solver.add_clause(clause)
            added_cut_clauses += len(new_clauses)

    outcome.update(
        {
            "case_id": case["case_id"],
            "state": case["state"],
            "patch_n": patch.number_of_nodes(),
            "patch_m": patch.number_of_edges(),
            "rounds": rounds,
            "base_and_cut_clauses": len(clauses),
            "added_connectivity_cuts": added_cut_clauses,
            "elapsed_s": time.time() - started,
        }
    )
    (case_dir / "result.json").write_text(
        json.dumps(outcome, indent=2), encoding="utf-8"
    )
    return outcome


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--max-cases", type=int, default=100)
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    cases = data.get("candidate_cases", [])[: args.max_cases]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    results = []
    for index, case in enumerate(cases, 1):
        print(
            json.dumps(
                {"sat_case": index, "total": len(cases), "id": case["case_id"]}
            ),
            flush=True,
        )
        results.append(
            solve_case(
                case,
                args.output_dir,
                args.solver,
                args.drat_trim,
                args.proof_solver,
            )
        )

    counts: dict[str, int] = {}
    for result in results:
        counts[result["classification"]] = counts.get(result["classification"], 0) + 1
    summary = {
        "input_candidate_cases": len(data.get("candidate_cases", [])),
        "cases_attempted": len(cases),
        "classification_counts": counts,
        "certified_missing_q_states": counts.get("certified_negative", 0),
        "verified_false_milp_negatives_or_timeouts": counts.get(
            "verified_positive", 0
        ),
        "elapsed_s": time.time() - started,
        "solver": args.solver,
        "proof_solver": args.proof_solver,
        "python": platform.python_version(),
    }
    output = {"summary": summary, "results": results}
    (args.output_dir / "sat_q_verification_summary.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
