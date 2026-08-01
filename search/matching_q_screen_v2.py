#!/usr/bin/env python3
"""Collision-safe all-parent perfect-matching Q-state screen."""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

import networkx as nx

from cyclic_cut_patch_search import enumerate_patch_tasks
from matching_q_screen import TARGETS, sample_task


def namespace_tasks(tasks, graph_index):
    output=[]
    for task in tasks:
        item=dict(task)
        item['local_key']=str(task['key'])
        item['key']=f"g{graph_index}-{task['key']}"
        output.append(item)
    keys=[task['key'] for task in output]
    if len(keys)!=len(set(keys)):
        raise RuntimeError(f'duplicate task key in graph {graph_index}')
    return output


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--verified',type=Path,required=True)
    parser.add_argument('--graphs',type=int,default=8)
    parser.add_argument('--trials',type=int,default=64)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--seed',type=int,default=20260801)
    args=parser.parse_args()

    data=json.loads(args.verified.read_text())['results'][:args.graphs]
    all_results={}
    graph_metadata={}
    started=time.time()
    args.output.parent.mkdir(parents=True,exist_ok=True)

    for record in data:
        graph_index=int(record['pool_index'])
        graph=nx.from_graph6_bytes(record['graph6'].encode())
        raw_tasks,cuts=enumerate_patch_tasks(graph,graph_index)
        tasks=namespace_tasks(raw_tasks,graph_index)
        graph_metadata[str(graph_index)]={
            'cuts':cuts,
            'patch_sides':len(tasks),
            'n':len(graph),
            'sha256':hashlib.sha256(record['graph6'].encode()).hexdigest(),
        }
        payloads=[
            (record['graph6'],task,args.trials,args.seed+graph_index*100000+i)
            for i,task in enumerate(tasks)
        ]
        before=len(all_results)
        with cf.ProcessPoolExecutor(max_workers=args.workers) as executor:
            for result in executor.map(sample_task,payloads,chunksize=4):
                if result['key'] in all_results:
                    raise RuntimeError(f"duplicate result key {result['key']}")
                all_results[result['key']]=result
        if len(all_results)-before!=len(tasks):
            raise RuntimeError('result cardinality mismatch')
        graph_results=[r for r in all_results.values() if r['key'].startswith(f'g{graph_index}-')]
        summary=Counter()
        for result in graph_results:
            for state in TARGETS:
                summary[state+'_found']+=int(state in result['found'])
            summary['both_found']+=int(TARGETS<=set(result['found']))
        print(json.dumps({'graph':graph_index,**graph_metadata[str(graph_index)],**summary}),flush=True)
        output={
            'driver_version':2,
            'task_key_scheme':'g<graph>-c<cut>-s<side>',
            'task_keys_unique':True,
            'parameters':{'trials':args.trials,'graphs':args.graphs,'seed':args.seed},
            'elapsed_s':time.time()-started,
            'graphs':graph_metadata,
            'results':all_results,
        }
        args.output.write_text(json.dumps(output,indent=2))

    expected=sum(meta['patch_sides'] for meta in graph_metadata.values())
    if len(all_results)!=expected:
        raise RuntimeError(f'{len(all_results)} results for {expected} patches')
    total=Counter()
    for result in all_results.values():
        for state in TARGETS:
            total[state+'_found']+=int(state in result['found'])
        total['both_found']+=int(TARGETS<=set(result['found']))
        total['patches']+=1
    print(json.dumps({'final':dict(total),'elapsed_s':time.time()-started},indent=2))


if __name__=='__main__':
    main()
