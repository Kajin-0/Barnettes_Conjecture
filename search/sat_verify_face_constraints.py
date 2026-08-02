#!/usr/bin/env python3
"""Proof-producing verification of facial Hamiltonian edge constraints.

For each case, encode a spanning 2-factor with selected-edge variables, force
all ``include_edges`` selected and all ``exclude_edges`` unselected, then add
valid subtour-elimination cuts lazily until either:

* a connected 2-factor (Hamiltonian cycle) is found and independently checked;
* the accumulated CNF is UNSAT; or
* the configured resource bound is reached.

A negative is certified only when CaDiCaL reproduces UNSAT for the final CNF
and drat-trim accepts the emitted textual DRAT proof. PySAT UNSAT alone is not
reported as mathematical evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable

import networkx as nx
from pysat.solvers import Solver

Edge = tuple[int, int]


def ce(u: int, v: int) -> Edge:
    return (u, v) if u < v else (v, u)


def exactly_k_small(lits: list[int], k: int) -> list[list[int]]:
    """Direct CNF for exact-k; graph degrees are at most three here."""
    n = len(lits)
    if k < 0 or k > n:
        return [[]]
    clauses: list[list[int]] = []
    for subset in itertools.combinations(lits, k + 1):
        clauses.append([-lit for lit in subset])
    for subset in itertools.combinations(lits, n - k + 1):
        clauses.append(list(subset))
    return clauses


def at_least_two(lits: Iterable[int]) -> list[list[int]]:
    """CNF requiring at least two literals to be true."""
    values = sorted(set(int(lit) for lit in lits))
    if len(values) < 2:
        return [[]]
    clauses = [values]
    clauses.extend([[-lit] + [other for other in values if other != lit] for lit in values])
    return clauses


def write_dimacs(path: Path, clauses: list[list[int]]) -> dict[str, int]:
    max_var = max((abs(lit) for clause in clauses for lit in clause), default=0)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii") as handle:
        handle.write(f"p cnf {max_var} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    return {"variables": max_var, "clauses": len(clauses)}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_edges(raw: Iterable[Iterable[int]]) -> list[Edge]:
    return [ce(int(edge[0]), int(edge[1])) for edge in raw]


def validate_cycle(
    graph: nx.Graph,
    selected: Iterable[Edge],
    include_edges: set[Edge],
    exclude_edges: set[Edge],
) -> dict[str, Any]:
    selected_list = [ce(*edge) for edge in selected]
    selected_set = set(selected_list)
    graph_edges = {ce(*edge) for edge in graph.edges()}
    witness = nx.Graph()
    witness.add_nodes_from(graph)
    witness.add_edges_from(selected_set)
    checks: dict[str, Any] = {
        "all_edges_in_graph": selected_set <= graph_edges,
        "no_duplicate_edges": len(selected_list) == len(selected_set),
        "selected_edge_count": len(selected_set),
        "expected_edge_count": graph.number_of_nodes(),
        "degree_two": all(witness.degree(vertex) == 2 for vertex in graph),
        "connected": nx.is_connected(witness),
        "includes_required": include_edges <= selected_set,
        "avoids_excluded": selected_set.isdisjoint(exclude_edges),
    }
    checks["valid"] = all(
        (
            checks["all_edges_in_graph"],
            checks["no_duplicate_edges"],
            checks["selected_edge_count"] == checks["expected_edge_count"],
            checks["degree_two"],
            checks["connected"],
            checks["includes_required"],
            checks["avoids_excluded"],
        )
    )
    return checks


def graph_validation(graph: nx.Graph) -> dict[str, Any]:
    planar, _ = nx.check_planarity(graph)
    result: dict[str, Any] = {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "simple": not graph.is_multigraph() and nx.number_of_selfloops(graph) == 0,
        "connected": nx.is_connected(graph),
        "cubic": all(graph.degree(vertex) == 3 for vertex in graph),
        "bipartite": nx.is_bipartite(graph),
        "planar": planar,
        "node_connectivity": nx.node_connectivity(graph) if nx.is_connected(graph) else 0,
    }
    result["three_connected"] = result["node_connectivity"] >= 3
    result["barnette_predicates"] = all(
        result[key]
        for key in ("simple", "connected", "cubic", "bipartite", "planar", "three_connected")
    )
    return result


def run_process(command: list[str], timeout: float) -> dict[str, Any]:
    started = time.time()
    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-12000:],
            "stderr": completed.stderr[-12000:],
            "timed_out": False,
            "elapsed_s": time.time() - started,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-12000:] if isinstance(exc.stderr, str) else "",
            "timed_out": True,
            "elapsed_s": time.time() - started,
        }


def solve_case(
    graph: nx.Graph,
    case: dict[str, Any],
    output_dir: Path,
    solver_name: str,
    proof_solver: str | None,
    drat_trim: str | None,
    max_rounds: int,
    proof_timeout: float,
) -> dict[str, Any]:
    safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(case["case_id"]))
    case_dir = output_dir / safe_id
    case_dir.mkdir(parents=True, exist_ok=True)

    include_edges = set(normalize_edges(case.get("include_edges", [])))
    exclude_edges = set(normalize_edges(case.get("exclude_edges", [])))
    graph_edges = sorted(ce(*edge) for edge in graph.edges())
    graph_edge_set = set(graph_edges)

    malformed_reasons: list[str] = []
    if not include_edges <= graph_edge_set:
        malformed_reasons.append("required edge absent from graph")
    if not exclude_edges <= graph_edge_set:
        malformed_reasons.append("excluded edge absent from graph")
    if include_edges & exclude_edges:
        malformed_reasons.append("same edge both included and excluded")
    if malformed_reasons:
        outcome = {
            "case_id": case["case_id"],
            "classification": "malformed",
            "reasons": malformed_reasons,
        }
        (case_dir / "result.json").write_text(json.dumps(outcome, indent=2), encoding="utf-8")
        return outcome

    edge_var = {edge: index + 1 for index, edge in enumerate(graph_edges)}
    clauses: list[list[int]] = []
    for vertex in graph:
        incident = [edge_var[ce(vertex, neighbor)] for neighbor in graph.neighbors(vertex)]
        clauses.extend(exactly_k_small(incident, 2))
    clauses.extend([[edge_var[edge]] for edge in sorted(include_edges)])
    clauses.extend([[-edge_var[edge]] for edge in sorted(exclude_edges)])

    started = time.time()
    rounds = 0
    added_subtour_constraints = 0
    known_crossing_sets: set[tuple[int, ...]] = set()
    outcome: dict[str, Any]

    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        while rounds < max_rounds:
            rounds += 1
            satisfiable = solver.solve()
            if not satisfiable:
                cnf_path = case_dir / "final.cnf"
                proof_path = case_dir / "final.drat"
                dimacs = write_dimacs(cnf_path, clauses)
                if proof_path.exists():
                    proof_path.unlink()

                proof_generation: dict[str, Any] = {
                    "attempted": bool(proof_solver),
                    "unsat_exit_code": False,
                    "proof_bytes": 0,
                }
                if proof_solver:
                    proof_generation.update(
                        run_process(
                            [proof_solver, "--no-binary", str(cnf_path), str(proof_path)],
                            proof_timeout,
                        )
                    )
                    proof_generation["unsat_exit_code"] = proof_generation.get("returncode") == 20
                    proof_generation["proof_bytes"] = proof_path.stat().st_size if proof_path.exists() else 0

                proof_verification: dict[str, Any] = {
                    "attempted": bool(drat_trim),
                    "verified": False,
                }
                if (
                    drat_trim
                    and proof_path.exists()
                    and proof_path.stat().st_size > 0
                    and proof_generation.get("unsat_exit_code")
                ):
                    proof_verification.update(
                        run_process([drat_trim, str(cnf_path), str(proof_path)], proof_timeout)
                    )
                    proof_verification["verified"] = proof_verification.get("returncode") == 0

                classification = (
                    "certified_negative" if proof_verification["verified"] else "provisional_negative"
                )
                outcome = {
                    "case_id": case["case_id"],
                    "classification": classification,
                    "sat": False,
                    "include_edges": [list(edge) for edge in sorted(include_edges)],
                    "exclude_edges": [list(edge) for edge in sorted(exclude_edges)],
                    "rounds": rounds,
                    "added_subtour_constraints": added_subtour_constraints,
                    "dimacs": dimacs,
                    "cnf_path": str(cnf_path),
                    "cnf_sha256": sha256_file(cnf_path),
                    "proof_path": str(proof_path),
                    "proof_sha256": sha256_file(proof_path) if proof_path.exists() else None,
                    "proof_generation": proof_generation,
                    "proof_verification": proof_verification,
                }
                break

            positive_model = {literal for literal in solver.get_model() if literal > 0}
            selected = [edge for edge, variable in edge_var.items() if variable in positive_model]
            validation = validate_cycle(graph, selected, include_edges, exclude_edges)
            if validation["valid"]:
                witness_path = case_dir / "hamiltonian_cycle.json"
                witness = {
                    "case_id": case["case_id"],
                    "selected_edges": [list(edge) for edge in selected],
                    "validation": validation,
                }
                witness_path.write_text(json.dumps(witness, indent=2), encoding="utf-8")
                outcome = {
                    "case_id": case["case_id"],
                    "classification": "verified_positive",
                    "sat": True,
                    "include_edges": [list(edge) for edge in sorted(include_edges)],
                    "exclude_edges": [list(edge) for edge in sorted(exclude_edges)],
                    "rounds": rounds,
                    "added_subtour_constraints": added_subtour_constraints,
                    "witness_path": str(witness_path),
                    "witness_sha256": sha256_file(witness_path),
                    "witness_validation": validation,
                }
                break

            selected_graph = nx.Graph()
            selected_graph.add_nodes_from(graph)
            selected_graph.add_edges_from(selected)
            components = list(nx.connected_components(selected_graph))
            new_clauses: list[list[int]] = []
            for component in components:
                if len(component) == graph.number_of_nodes():
                    continue
                crossing_vars = tuple(
                    sorted(
                        edge_var[ce(u, v)]
                        for u in component
                        for v in graph.neighbors(u)
                        if v not in component
                    )
                )
                if crossing_vars in known_crossing_sets:
                    continue
                known_crossing_sets.add(crossing_vars)
                new_clauses.extend(at_least_two(crossing_vars))
                added_subtour_constraints += 1

            if not new_clauses:
                outcome = {
                    "case_id": case["case_id"],
                    "classification": "unknown",
                    "sat": True,
                    "reason": "disconnected model produced no new valid subtour constraint",
                    "rounds": rounds,
                    "witness_validation": validation,
                }
                break
            for clause in new_clauses:
                clauses.append(clause)
                solver.add_clause(clause)
        else:
            outcome = {
                "case_id": case["case_id"],
                "classification": "unknown",
                "reason": "maximum lazy-connectivity rounds reached",
                "rounds": rounds,
                "added_subtour_constraints": added_subtour_constraints,
            }

    outcome["elapsed_s"] = time.time() - started
    (case_dir / "result.json").write_text(json.dumps(outcome, indent=2), encoding="utf-8")
    return outcome


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--max-rounds", type=int, default=10000)
    parser.add_argument("--proof-timeout", type=float, default=900.0)
    parser.add_argument("--max-cases", type=int, default=100)
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    graph = nx.from_graph6_bytes(data["source"]["graph6"].encode("ascii"))
    graph_checks = graph_validation(graph)
    if not graph_checks["barnette_predicates"]:
        raise SystemExit(f"candidate graph failed Barnette predicates: {graph_checks}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    results: list[dict[str, Any]] = []
    for index, case in enumerate(data.get("cases", [])[: args.max_cases], 1):
        print(json.dumps({"case": index, "id": case["case_id"]}), flush=True)
        result = solve_case(
            graph,
            case,
            args.output_dir,
            args.solver,
            args.proof_solver,
            args.drat_trim,
            args.max_rounds,
            args.proof_timeout,
        )
        results.append(result)
        print(
            json.dumps(
                {
                    "id": case["case_id"],
                    "classification": result["classification"],
                    "rounds": result.get("rounds"),
                }
            ),
            flush=True,
        )

    counts: dict[str, int] = {}
    for result in results:
        counts[result["classification"]] = counts.get(result["classification"], 0) + 1
    summary = {
        "input": str(args.input),
        "graph_validation": graph_checks,
        "cases_available": len(data.get("cases", [])),
        "cases_attempted": len(results),
        "classification_counts": counts,
        "certified_three_edge_obstructions": counts.get("certified_negative", 0),
        "verified_positive_contradictions": counts.get("verified_positive", 0),
        "remaining_unknown_or_provisional": sum(
            count
            for key, count in counts.items()
            if key not in ("certified_negative", "verified_positive")
        ),
        "counterexample_found": False,
        "elapsed_s": time.time() - started,
        "software": {
            "python": platform.python_version(),
            "networkx": nx.__version__,
            "solver": args.solver,
        },
    }
    output = {"summary": summary, "results": results}
    summary_path = args.output_dir / "face_constraint_verification_summary.json"
    summary_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
