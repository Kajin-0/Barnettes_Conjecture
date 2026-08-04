#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json,hashlib,time
import networkx as nx
from collections import defaultdict
from pathlib import Path

B=12
BOUNDARY_EDGES=tuple((i,(i+1)%B) if i<(i+1)%B else ((i+1)%B,i) for i in range(B))
BOUNDARY_SET=set(BOUNDARY_EDGES)

def ce(a,b): return (a,b) if a<b else (b,a)

def simple_cycles_undirected(vertices, edges):
    adj={v:[] for v in vertices}
    for i,(a,b) in enumerate(edges):
        adj[a].append((b,i));adj[b].append((a,i))
    for v in adj: adj[v].sort()
    out=[]
    for s in sorted(vertices):
        seen={s}; path=[s]; pem=[]
        def dfs(u):
            for v,ei in adj[u]:
                if v==s:
                    if len(path)>=4 and path[1] < path[-1]:
                        mask=0
                        for x in pem: mask |= 1<<x
                        mask |= 1<<ei
                        out.append(mask)
                    continue
                if v<=s or v in seen: continue
                seen.add(v);path.append(v);pem.append(ei)
                dfs(v)
                pem.pop();path.pop();seen.remove(v)
        dfs(s)
    return sorted(set(out))

def decompose_cycles(edges,n0):
    m=len(edges)
    target=tuple(1 if e in BOUNDARY_SET else 2 for e in edges)
    cycles=simple_cycles_undirected(sorted({x for e in edges for x in e}),edges)
    cv=[]
    containing=[[] for _ in range(m)]
    for mask in cycles:
        inds=tuple(i for i in range(m) if (mask>>i)&1)
        if len(inds)<4 or len(inds)%2: continue
        idx=len(cv); cv.append((mask,inds))
        for i in inds: containing[i].append(idx)
    from functools import lru_cache
    @lru_cache(None)
    def solve(rem,slots):
        if slots==0:
            return ((),) if not any(rem) else ()
        if sum(rem) < 4*slots: return ()
        try:pivot=next(i for i,x in enumerate(rem) if x)
        except StopIteration:return ()
        ans=set()
        for ci in containing[pivot]:
            inds=cv[ci][1]
            if any(rem[i]<=0 for i in inds):continue
            nr=list(rem)
            for i in inds:nr[i]-=1
            for tail in solve(tuple(nr),slots-1):
                ans.add(tuple(sorted((ci,)+tail)))
        return tuple(sorted(ans))
    return cycles,cv,list(solve(target,n0))

def validate_complex(k,n0,n1,n2,edges,cv,decomp):
    c0=list(range(B,B+n0)); apex=B+k
    triangles=[]
    for z,ci in zip(c0,decomp):
        for ei in cv[ci][1]:
            a,b=edges[ei];triangles.append(tuple(sorted((z,a,b))))
    for a,b in BOUNDARY_EDGES: triangles.append(tuple(sorted((apex,a,b))))
    if len(triangles)!=2*(B+k+1)-4 or len(set(triangles))!=len(triangles): return None
    incid=defaultdict(list); graph_edges=set()
    for ti,t in enumerate(triangles):
        for e in (ce(t[0],t[1]),ce(t[0],t[2]),ce(t[1],t[2])):
            incid[e].append(ti);graph_edges.add(e)
    if any(len(x)!=2 for x in incid.values()): return None
    V=B+k+1;F=len(triangles);E=len(graph_edges)
    if V-E+F!=2: return None
    adj=[set() for _ in range(V)]
    for a,b in graph_edges: adj[a].add(b);adj[b].add(a)
    seen={0};stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:seen.add(v);stack.append(v)
    if len(seen)!=V:return None
    for v in range(V):
        ladj=defaultdict(set)
        for t in triangles:
            if v in t:
                x=[q for q in t if q!=v]
                ladj[x[0]].add(x[1]);ladj[x[1]].add(x[0])
        if not ladj or any(len(s)!=2 for s in ladj.values()):return None
        st=next(iter(ladj));ss={st};q=[st]
        while q:
            u=q.pop()
            for w in ladj[u]:
                if w not in ss:ss.add(w);q.append(w)
        if len(ss)!=len(ladj):return None
    disk_edges={e for e in graph_edges if apex not in e}
    dadj=[0]*(B+k)
    for a,b in disk_edges:dadj[a]+=1;dadj[b]+=1
    if any(dadj[v]%2!=1 for v in range(B)):return None
    if any(dadj[v]%2 or dadj[v]<4 for v in range(B,B+k)):return None
    if len(disk_edges)!=3*k+21:return None
    return tuple(sorted(disk_edges))

def colored_marked_graph(edge_set,n0,n1,n2,swap=False):
    k=n0+n1+n2
    G=nx.Graph()
    for v in range(B+k):
        if v<B:c=1+(v%2)
        elif v<B+n0:c=0
        elif v<B+n0+n1:c=1
        else:c=2
        if swap and c in (1,2):c=3-c
        G.add_node(v,kind=f'c{c}')
    G.add_edges_from(edge_set)
    hub=B+k;G.add_node(hub,kind='hub')
    for i in range(B):
        q=hub+1+i;G.add_node(q,kind='boundary_edge')
        G.add_edge(q,i);G.add_edge(q,(i+1)%B);G.add_edge(hub,q)
    return G

def add_colored_class(found,buckets,edge_set,n0,n1,n2):
    variants=[colored_marked_graph(edge_set,n0,n1,n2,False)]
    if n1==n2:variants.append(colored_marked_graph(edge_set,n0,n1,n2,True))
    hs=[nx.weisfeiler_lehman_graph_hash(g,node_attr='kind',iterations=8) for g in variants]
    key=min(hs)
    nm=nx.algorithms.isomorphism.categorical_node_match('kind',None)
    for idx in buckets[key]:
        rep=found[idx][1]
        if any(nx.is_isomorphic(g,rep,node_match=nm) for g in variants):return False
    idx=len(found);found.append((edge_set,variants[0]));buckets[key].append(idx);return True

def generate(n0,n1,n2,outpath=None, progress=False):
    k=n0+n1+n2
    c1=list(range(0,B,2))+list(range(B+n0,B+n0+n1))
    c2=list(range(1,B,2))+list(range(B+n0+n1,B+k))
    candidates=[ce(a,b) for a in c1 for b in c2 if ce(a,b) not in BOUNDARY_SET]
    total=0;struct=0;decomps=0;valid=0;found=[];buckets=defaultdict(list);started=time.time()
    for extras in itertools.combinations(candidates,k-1):
        total+=1
        deg=defaultdict(int)
        for a,b in extras:deg[a]+=1;deg[b]+=1
        if any(deg[v]<2 for v in c1 if v>=B) or any(deg[v]<2 for v in c2 if v>=B):continue
        struct+=1
        edges=tuple(sorted(BOUNDARY_SET|set(extras)))
        cycles,cv,ds=decompose_cycles(edges,n0)
        decomps+=len(ds)
        for d in ds:
            disk=validate_complex(k,n0,n1,n2,edges,cv,d)
            if disk is None:continue
            valid+=1
            add_colored_class(found,buckets,disk,n0,n1,n2)
        if progress and total%250000==0:
            print(json.dumps({'total':total,'struct':struct,'decomps':decomps,'valid':valid,'classes':len(found),'sec':time.time()-started}),flush=True)
    arr=[[list(e) for e in disk] for disk,_ in found]
    result={'distribution':[n0,n1,n2],'k':k,'extra_sets':total,'structural':struct,'decompositions':decomps,'valid_complexes':valid,'disk_classes':len(arr),'elapsed_s':time.time()-started}
    if outpath:
        Path(outpath).write_text(json.dumps({'summary':result,'disks':arr},separators=(',',':')),encoding='utf-8')
        result['sha256']=hashlib.sha256(Path(outpath).read_bytes()).hexdigest()
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('n0',type=int);ap.add_argument('n1',type=int);ap.add_argument('n2',type=int);ap.add_argument('--out');ap.add_argument('--progress',action='store_true');a=ap.parse_args()
    print(json.dumps(generate(a.n0,a.n1,a.n2,a.out,a.progress),indent=2))
if __name__=='__main__':main()
