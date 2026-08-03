#!/usr/bin/env python3
"""Relation-first CEGIS synthesis of a six-terminal Barnette selector."""
from __future__ import annotations

import argparse, hashlib, itertools, json, platform, time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver

from exact_six_port_closure_search import (
    all_pairings, ce, exact_language, exact_path_cover_state, states_compatible,
)
from sat_verify_face_constraints import graph_validation, solve_case

Edge = tuple[int, int]


def specs() -> list[dict[str, Any]]:
    out=[]
    for size in (2,4,6):
        for active in itertools.combinations(range(6),size):
            for pairing in all_pairings(active):
                out.append({"active":list(active),"pairing":[list(p) for p in pairing]})
    assert len(out)==75
    return out


def color_map(source:list[int],patch:list[int])->tuple[int,...]:
    out:[int|None]=[None]*6
    for c in (0,1):
        a=[i for i,x in enumerate(source) if x==c]
        b=[i for i,x in enumerate(patch) if x==1-c]
        if len(a)!=len(b): raise ValueError((source,patch))
        for i,j in zip(a,b,strict=True): out[i]=j
    return tuple(int(x) for x in out)


def g6(g:nx.Graph)->str:
    return nx.to_graph6_bytes(g,header=False).decode("ascii").strip()


def checkpoint(path:Path,payload:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    tmp.replace(path)


def edge_nogood(edges:Iterable[Edge],ev:dict[Edge,int])->list[int]:
    return [-ev[ce(*e)] for e in edges]


def obstruction_clause(obs:nx.Graph,ev:dict[Edge,int],offset:int)->list[int]:
    return sorted({-ev[e] for u,v in obs.edges() if (e:=ce(int(u)-offset,int(v)-offset)) in ev})


def crossing_clause(side:set[int],sep:set[int],ev:dict[Edge,int],offset:int)->list[int]:
    out=[]
    for (u,v),lit in ev.items():
        U,V=offset+u,offset+v
        if U in sep or V in sep: continue
        if (U in side)!=(V in side): out.append(lit)
    return sorted(set(out))


def lex_leq(clauses:list[list[int]],pool:IDPool,A:list[int],B:list[int],tag:str)->None:
    prev=None
    for k,(a,b) in enumerate(zip(A,B,strict=True)):
        clauses.append([-a,b] if prev is None else [-prev,-a,b])
        eq=pool.id(f"lex:{tag}:{k}")
        if prev is None:
            clauses += [[-eq,-a,b],[-eq,a,-b],[-a,-b,eq],[a,b,eq]]
        else:
            clauses += [[-eq,prev],[-eq,-a,b],[-eq,a,-b],[-prev,-a,-b,eq],[-prev,a,b,eq]]
        prev=eq


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--source-input",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--patch-order",type=int,required=True)
    p.add_argument("--seed",type=int,default=0)
    p.add_argument("--solver",default="g4")
    p.add_argument("--call-budget",type=int,default=10_000_000)
    p.add_argument("--max-iterations",type=int,default=100_000)
    p.add_argument("--wall-time",type=float,default=20_000)
    p.add_argument("--proof-solver",default=None)
    p.add_argument("--drat-trim",default=None)
    p.add_argument("--proof-timeout",type=float,default=3600)
    p.add_argument("--max-rounds",type=int,default=100_000)
    a=p.parse_args()
    if a.patch_order<8 or a.patch_order%2: raise SystemExit("even order >=8 required")
    q=a.patch_order//2
    a.output_dir.mkdir(parents=True,exist_ok=True)
    ck=a.output_dir/"checkpoint.json"
    source_data=json.loads(a.source_input.read_text())
    source=nx.from_graph6_bytes(source_data["source"]["graph6"].encode("ascii"))
    if not graph_validation(source)["barnette_predicates"]: raise SystemExit("bad source")
    removed=[ce(14,18),ce(10,17),ce(5,11)]
    face=[int(x) for x in source_data["face"]["vertices_cyclic_order"]]
    terminal={x for e in removed for x in e}
    source_ports=[x for x in face if x in terminal]
    core=source.copy(); core.remove_edges_from(removed)
    sl=exact_language(core,source_ports,a.call_budget)
    spos=[s for s in sl if s["classification"]=="verified_positive"]
    sunk=[s for s in sl if s["classification"]=="unknown"]
    if len(spos)!=26 or sunk: raise SystemExit(f"source language regression {len(spos)} {len(sunk)}")
    scol=nx.bipartite.color(source)
    source_colors=[int(scol[v]) for v in source_ports]

    L=list(range(q)); R=list(range(q,2*q)); ports=L[:3]+R[:3]
    patch_colors=[0,0,0,1,1,1]
    mapping=color_map(source_colors,patch_colors)
    relevant=[s for s in specs() if any(states_compatible(t,s,mapping) for t in spos)]

    pool=IDPool()
    ev={ce(u,v):pool.id(f"e:{u}:{v}") for u in L for v in R}
    clauses=[]
    P=set(ports)
    for v in L+R:
        inc=[lit for e,lit in ev.items() if v in e]
        clauses += CardEnc.equals(inc,2 if v in P else 3,vpool=pool,encoding=EncType.seqcounter).clauses
    for u,v in zip(L[3:],L[4:]):
        lex_leq(clauses,pool,[ev[ce(u,x)] for x in reversed(R)],[ev[ce(v,x)] for x in reversed(R)],f"{u}:{v}")

    start=time.time(); counts=Counter(); best=None; bestrec=None; learned=set(); final=None; incomplete=[]
    offset=max(source.nodes())+1

    def save(it:int,status:str)->None:
        checkpoint(ck,{"campaign":"relation-first-six-port-cegis","status":status,"iteration":it,
            "patch_order":a.patch_order,"seed":a.seed,"mapping":list(mapping),"relevant_states":len(relevant),
            "counts":dict(counts),"learned":len(learned),"best":best,"best_record":bestrec,
            "final_candidate":final,"incomplete":incomplete,"elapsed_s":time.time()-start})

    with Solver(name=a.solver,bootstrap_with=clauses) as solver:
        try: solver.set_phases([x if ((x*0x9E3779B1+a.seed)&1) else -x for x in ev.values()])
        except Exception: pass
        for it in range(1,a.max_iterations+1):
            if time.time()-start>a.wall_time:
                counts["wall_time"]+=1; save(it,"wall_time_exhausted"); break
            if not solver.solve():
                counts["synthesis_unsat"]+=1; save(it,"synthesis_unsat"); break
            model={x for x in solver.get_model() if x>0}
            edges=sorted(e for e,x in ev.items() if x in model)
            patch=nx.Graph(); patch.add_nodes_from(L+R); patch.add_edges_from(edges)
            counts["sat_candidates"]+=1

            planar,obj=nx.check_planarity(patch,counterexample=True)
            if not planar:
                c=obstruction_clause(obj,ev,0) or edge_nogood(edges,ev)
                solver.add_clause(c); counts["patch_nonplanar"]+=1; continue

            rel={v:offset+v for v in patch}
            assembled=core.copy(); assembled.add_edges_from((rel[u],rel[v]) for u,v in patch.edges())
            glue=[]
            for si,pi in enumerate(mapping):
                e=ce(source_ports[si],rel[ports[pi]]); assembled.add_edge(*e); glue.append(e)
            planar,obj=nx.check_planarity(assembled,counterexample=True)
            if not planar:
                c=obstruction_clause(obj,ev,offset) or edge_nogood(edges,ev)
                solver.add_clause(c); counts["assembled_nonplanar"]+=1; continue

            if not nx.is_connected(assembled): conn=0; sep=set(); comps=[set(x) for x in nx.connected_components(assembled)]
            else:
                conn=nx.node_connectivity(assembled)
                sep=set(nx.minimum_node_cut(assembled)) if conn<3 else set()
                h=assembled.copy(); h.remove_nodes_from(sep)
                comps=[set(x) for x in nx.connected_components(h)] if conn<3 else []
            if conn<3:
                added=0
                for comp in comps:
                    c=crossing_clause(comp,sep,ev,offset)
                    if c: solver.add_clause(c); added+=1
                if not added: solver.add_clause(edge_nogood(edges,ev))
                counts[f"connectivity_{conn}"]+=1; counts["separator_clauses"]+=added; continue

            counts["structurally_valid"]+=1
            clauses_now=[]; positive=0; unknown=[]
            for s in relevant:
                r=exact_path_cover_state(patch,ports,tuple(s["active"]),tuple(tuple(x) for x in s["pairing"]),a.call_budget)
                if r["classification"]=="unknown": unknown.append(r); continue
                if r["classification"]!="verified_positive": continue
                positive+=1
                c=tuple(sorted(-ev[ce(int(e[0]),int(e[1]))] for e in r["witness"]))
                if c not in learned: learned.add(c); clauses_now.append(list(c))
            if unknown:
                incomplete.append({"iteration":it,"patch_graph6":g6(patch),"unknown":unknown})
                solver.add_clause(edge_nogood(edges,ev)); counts["language_unknown"]+=1; save(it,"language_unknown"); continue
            if best is None or positive<best:
                best=positive; bestrec={"iteration":it,"patch_graph6":g6(patch),"edges":[list(e) for e in edges],"positive_relevant_states":positive}
                save(it,"new_best"); print(json.dumps({"iteration":it,"order":a.patch_order,"seed":a.seed,"new_best":best,"learned":len(learned)}),flush=True)
            if positive:
                if clauses_now:
                    for c in clauses_now: solver.add_clause(c)
                    counts["witness_clauses"]+=len(clauses_now)
                else:
                    solver.add_clause(edge_nogood(edges,ev)); counts["duplicate_witness_nogood"]+=1
                if it%25==0: save(it,"searching")
                continue

            checks=graph_validation(assembled)
            if not checks["barnette_predicates"]:
                incomplete.append({"iteration":it,"reason":"validation regression","checks":checks})
                solver.add_clause(edge_nogood(edges,ev)); save(it,"validation_regression"); continue
            cg6=g6(assembled); cid=f"relation-first-n{a.patch_order}-s{a.seed}-{hashlib.sha256(cg6.encode()).hexdigest()[:12]}"
            cdir=a.output_dir/cid; cdir.mkdir(parents=True,exist_ok=True)
            (cdir/"candidate.g6").write_text(cg6+"\n")
            (cdir/"candidate_edges.json").write_text(json.dumps([list(ce(*e)) for e in sorted(assembled.edges())],indent=2))
            proof=solve_case(assembled,{"case_id":cid+"-hamiltonicity","constraint_type":"whole_graph_hamiltonicity","include_edges":[],"exclude_edges":[]},cdir,a.solver,a.proof_solver,a.drat_trim,a.max_rounds,a.proof_timeout)
            final={"candidate_id":cid,"patch_graph6":g6(patch),"candidate_graph6":cg6,"patch_edges":[list(e) for e in edges],"glue_edges":[list(e) for e in sorted(glue)],"mapping":list(mapping),"graph_validation":checks,"whole_graph_result":proof}
            if proof["classification"]=="certified_negative" and proof.get("proof_verification",{}).get("verified",False):
                counts["certified_counterexample"]+=1; save(it,"certified_counterexample_candidate"); break
            if proof["classification"]=="verified_positive":
                save(it,"decomposition_contradiction"); raise SystemExit("zero-language contradiction")
            incomplete.append({"iteration":it,"reason":"whole graph unknown","candidate":final})
            save(it,"whole_graph_unknown"); break
        else:
            counts["max_iterations"]+=1; save(a.max_iterations,"max_iterations_exhausted")

    status=json.loads(ck.read_text())["status"] if ck.exists() else "not_started"
    summary={"date_utc":"2026-08-03","campaign":"relation-first-six-port-cegis","status":status,
        "patch_order":a.patch_order,"seed":a.seed,"source_positive_states":len(spos),"mapping":list(mapping),
        "candidate_edge_variables":len(ev),"target_patch_edges":(3*a.patch_order-6)//2,
        "relevant_patch_states":len(relevant),"counts":dict(counts),"best_compatibility":best,
        "best_record":bestrec,"learned_witness_count":len(learned),"final_candidate":final,
        "counterexample_found":bool(final and final.get("whole_graph_result",{}).get("classification")=="certified_negative" and final.get("whole_graph_result",{}).get("proof_verification",{}).get("verified",False)),
        "incomplete":incomplete,"complete_classification":not incomplete and status in {"synthesis_unsat","certified_counterexample_candidate"},
        "elapsed_s":time.time()-start,"software":{"python":platform.python_version(),"networkx":nx.__version__,"solver":a.solver}}
    (a.output_dir/"campaign_summary.json").write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2),flush=True)

if __name__=="__main__": main()
