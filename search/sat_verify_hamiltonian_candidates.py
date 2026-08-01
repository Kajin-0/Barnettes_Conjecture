#!/usr/bin/env python3
"""Prove or refute Hamiltonicity with independently checked SAT evidence.

The base CNF enforces selected degree two at every vertex. SAT models are
2-factors. If a model is disconnected, a valid subtour clause is added for
each component, requiring at least one selected edge to cross its cut. Degree
two makes every selected cut cardinality even, so this excludes the component
and requires at least two crossing edges in every future model.

A connected model is an explicit Hamiltonian cycle and is independently
validated. If the accumulated final CNF is UNSAT, it is solved again by an
external proof-producing solver and its DRAT proof is checked independently.
Every added subtour clause is satisfied by every Hamiltonian cycle, so a
checked UNSAT proof certifies non-Hamiltonicity.
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


def ce(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def exactly_k_small(literals: list[int], k: int) -> list[list[int]]:
    n = len(literals)
    if k < 0 or k > n:
        return [[]]
    clauses: list[list[int]] = []
    for subset in itertools.combinations(literals, k + 1):
        clauses.append([-literal for literal in subset])
    for subset in itertools.combinations(literals, n - k + 1):
        clauses.append(list(subset))
    return clauses


def validate_cycle(graph: nx.Graph, selected_edges: list[tuple[int, int]]) -> dict[str, Any]:
    chosen = [ce(*edge) for edge in selected_edges]
    subgraph = nx.Graph()
    subgraph.add_nodes_from(graph)
    subgraph.add_edges_from(chosen)
    checks = {
        "selected_edge_count": len(chosen),
        "expected_edge_count": graph.number_of_nodes(),
        "all_edges_in_graph": all(graph.has_edge(*edge) for edge in chosen),
        "no_duplicate_edges": len(chosen) == len(set(chosen)),
        "degree_two": all(subgraph.degree(vertex) == 2 for vertex in graph),
        "connected": nx.is_connected(subgraph),
    }
    checks["valid"] = (
        checks["selected_edge_count"] == checks["expected_edge_count"]
        and checks["all_edges_in_graph"]
        and checks["no_duplicate_edges"]
        and checks["degree_two"]
        and checks["connected"]
    )
    return checks


def barnette_checks(graph: nx.Graph) -> dict[str, Any]:
    connected = nx.is_connected(graph)
    planar, _ = nx.check_planarity(graph)
    simple = nx.number_of_selfloops(graph) == 0 and not graph.is_multigraph()
    connectivity = nx.node_connectivity(graph) if connected else 0
    checks = {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "simple": simple,
        "cubic": all(degree == 3 for _, degree in graph.degree()),
        "bipartite": nx.is_bipartite(graph),
        "planar": planar,
        "connected": connected,
        "vertex_connectivity": int(connectivity),
    }
    checks["barnette"] = (
        checks["simple"]
        and checks["cubic"]
        and checks["bipartite"]
        and checks["planar"]
        and checks["vertex_connectivity"] >= 3
    )
    return checks


def write_dimacs(path: Path, clauses: list[list[int]]) -> tuple[int, int]:
    variables = max((abs(lit) for clause in clauses for lit in clause), default=0)
    with path.open("w", encoding="ascii") as handle:
        handle.write(f"p cnf {variables} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    return variables, len(clauses)


def external_unsat_proof(
    cnf_path: Path,
    proof_path: Path,
    proof_solver: str | None,
    drat_trim: str | None,
) -> dict[str, Any]:
    generation = {
        "attempted": bool(proof_solver),
        "command": None,
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "unsat_exit_code": False,
        "proof_bytes": 0,
    }
    if proof_solver:
        command = [proof_solver, "--no-binary", str(cnf_path), str(proof_path)]
        process = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=1800,
            check=False,
        )
        generation.update(
            {
                "command": command,
                "returncode": process.returncode,
                "stdout": process.stdout[-12000:],
                "stderr": process.stderr[-12000:],
                "unsat_exit_code": process.returncode == 20,
                "proof_bytes": proof_path.stat().st_size if proof_path.exists() else 0,
            }
        )

    verification = {
        "attempted": bool(drat_trim),
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "verified": False,
    }
    if (
        drat_trim
        and generation["unsat_exit_code"]
        and proof_path.exists()
        and proof_path.stat().st_size > 0
    ):
        process = subprocess.run(
            [drat_trim, str(cnf_path), str(proof_path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=1800,
            check=False,
        )
        verification.update(
            {
                "returncode": process.returncode,
                "stdout": process.stdout[-12000:],
                "stderr": process.stderr[-12000:],
                "verified": process.returncode == 0,
            }
        )
    return {"generation": generation, "verification": verification}


def solve_graph(
    case: dict[str, Any],
    output_dir: Path,
    solver_name: str,
    proof_solver: str | None,
    drat_trim: str | None,
) -> dict[str, Any]:
    case_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(case.get("case_id", "case")))
    case_dir = output_dir / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    graph = nx.from_graph6_bytes(case["graph6"].encode("ascii"))
    checks = barnette_checks(graph)
    edges = sorted(ce(*edge) for edge in graph.edges())
    edge_variable = {edge: index + 1 for index, edge in enumerate(edges)}
    clauses: list[list[int]] = []
    for vertex in graph:
        incident = [edge_variable[ce(vertex, neighbor)] for neighbor in graph.neighbors(vertex)]
        clauses.extend(exactly_k_small(incident, 2))

    started = time.time()
    rounds = 0
    subtour_clauses = 0
    known_cuts: set[tuple[int, ...]] = set()
    result: dict[str, Any]

    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        while True:
            rounds += 1
            satisfiable = solver.solve()
            if not satisfiable:
                cnf_path = case_dir / "hamiltonicity.cnf"
                proof_path = case_dir / "hamiltonicity.drat"
                variables, clause_count = write_dimacs(cnf_path, clauses)
                if proof_path.exists():
                    proof_path.unlink()
                proof = external_unsat_proof(
                    cnf_path,
                    proof_path,
                    proof_solver,
                    drat_trim,
                )
                verified = proof["verification"]["verified"]
                result = {
                    "classification": (
                        "certified_non_hamiltonian" if verified else "provisional_non_hamiltonian"
                    ),
                    "hamiltonian": False,
                    "cnf": str(cnf_path),
                    "proof": str(proof_path),
                    "cnf_variables": variables,
                    "cnf_clauses": clause_count,
                    "proof_generation": proof["generation"],
                    "proof_verification": proof["verification"],
                }
                break

            model = {literal for literal in solver.get_model() if literal > 0}
            selected = [edge for edge, variable in edge_variable.items() if variable in model]
            validation = validate_cycle(graph, selected)
            if validation["valid"]:
                witness_path = case_dir / "hamiltonian_cycle.json"
                witness = {
                    "case_id": case_id,
                    "cycle_edges": [list(edge) for edge in selected],
                    "validation": validation,
                }
                witness_path.write_text(json.dumps(witness, indent=2), encoding="utf-8")
                result = {
                    "classification": "verified_hamiltonian",
                    "hamiltonian": True,
                    "witness": str(witness_path),
                    "cycle_validation": validation,
                }
                break

            selected_graph = nx.Graph()
            selected_graph.add_nodes_from(graph)
            selected_graph.add_edges_from(selected)
            components = list(nx.connected_components(selected_graph))
            new_clauses = []
            for component in components:
                if len(component) == graph.number_of_nodes():
                    continue
                complement = set(graph) - set(component)
                canonical_side = (
                    frozenset(component)
                    if len(component) <= len(complement)
                    else frozenset(complement)
                )
                crossing_variables = sorted(
                    {
                        edge_variable[ce(u, v)]
                        for u in canonical_side
                        for v in graph.neighbors(u)
                        if v not in canonical_side
                    }
                )
                key = tuple(crossing_variables)
                if key in known_cuts:
                    continue
                known_cuts.add(key)
                new_clauses.append(crossing_variables)
            if not new_clauses:
                result = {
                    "classification": "unknown",
                    "hamiltonian": None,
                    "reason": "disconnected model yielded no new subtour cut",
                    "cycle_validation": validation,
                }
                break
            for clause in new_clauses:
                clauses.append(clause)
                solver.add_clause(clause)
            subtour_clauses += len(new_clauses)

    result.update(
        {
            "case_id": case_id,
            "barnette_checks": checks,
            "rounds": rounds,
            "subtour_clauses": subtour_clauses,
            "elapsed_s": time.time() - started,
        }
    )
    (case_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def normalize_cases(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return data
    if "candidate_cases" in data:
        return data["candidate_cases"]
    if "candidates" in data:
        candidates = data["candidates"]
        ranks = set(
            data.get("summary", {}).get("provisional_candidate_ranks", [])
            + data.get("summary", {}).get("unknown_candidate_ranks", [])
        )
        if ranks:
            candidates = [candidate for candidate in candidates if candidate.get("rank") in ranks]
        return [
            {
                "case_id": candidate.get("case_id", f"candidate-{candidate.get('rank', index)}"),
                "graph6": candidate["graph6"],
                "metadata": candidate,
            }
            for index, candidate in enumerate(candidates)
        ]
    if "graph6" in data:
        return [data]
    raise ValueError("unsupported input format")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--solver", default="g4")
    parser.add_argument("--proof-solver", default=None)
    parser.add_argument("--drat-trim", default=None)
    parser.add_argument("--max-cases", type=int, default=100)
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    cases = normalize_cases(data)[: args.max_cases]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    results = []
    for index, case in enumerate(cases, 1):
        print(
            json.dumps(
                {"whole_graph_case": index, "total": len(cases), "id": case.get("case_id")}
            ),
            flush=True,
        )
        results.append(
            solve_graph(
                case,
                args.output_dir,
                args.solver,
                args.proof_solver,
                args.drat_trim,
            )
        )

    counts: dict[str, int] = {}
    for result in results:
        counts[result["classification"]] = counts.get(result["classification"], 0) + 1
    certified_counterexamples = [
        result
        for result in results
        if result["classification"] == "certified_non_hamiltonian"
        and result["barnette_checks"]["barnette"]
    ]
    summary = {
        "input_cases": len(cases),
        "classification_counts": counts,
        "certified_non_hamiltonian": counts.get("certified_non_hamiltonian", 0),
        "certified_barnette_counterexamples": len(certified_counterexamples),
        "counterexample_found": bool(certified_counterexamples),
        "elapsed_s": time.time() - started,
        "solver": args.solver,
        "proof_solver": args.proof_solver,
        "python": platform.python_version(),
    }
    output = {"summary": summary, "results": results}
    (args.output_dir / "whole_graph_sat_summary.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
