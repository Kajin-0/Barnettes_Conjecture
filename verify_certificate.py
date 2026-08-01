#!/usr/bin/env python3
"""Validate a graph6 Barnette candidate and a Hamiltonian edge certificate."""
import argparse, json
from pathlib import Path
import networkx as nx

def main():
    p=argparse.ArgumentParser()
    p.add_argument("graph6",type=Path)
    p.add_argument("cycle",type=Path)
    a=p.parse_args()
    G=nx.from_graph6_bytes(a.graph6.read_text().strip().encode("ascii"))
    raw=json.loads(a.cycle.read_text())
    edges = raw.get("cycle_edges", raw.get("edges", raw)) if isinstance(raw, dict) else raw
    edges=[tuple(map(int,e)) for e in edges]
    H=nx.Graph();H.add_nodes_from(G);H.add_edges_from(edges)
    checks={
      "simple":not G.is_multigraph() and nx.number_of_selfloops(G)==0,
      "cubic":all(d==3 for _,d in G.degree()),
      "bipartite":nx.is_bipartite(G),
      "planar":nx.check_planarity(G)[0],
      "vertex_connectivity_at_least_3":nx.node_connectivity(G)>=3,
      "cycle_edge_count":len(edges)==G.number_of_nodes(),
      "cycle_edges_in_graph":all(G.has_edge(*e) for e in edges),
      "cycle_degree_2":all(H.degree(v)==2 for v in G),
      "cycle_connected":nx.is_connected(H),
    }
    checks["barnette"]=all(checks[k] for k in ("simple","cubic","bipartite","planar","vertex_connectivity_at_least_3"))
    checks["hamiltonian_certificate_valid"]=all(checks[k] for k in ("cycle_edge_count","cycle_edges_in_graph","cycle_degree_2","cycle_connected"))
    print(json.dumps(checks,indent=2))
    raise SystemExit(0 if checks["barnette"] and checks["hamiltonian_certificate_valid"] else 1)
if __name__=="__main__":main()
