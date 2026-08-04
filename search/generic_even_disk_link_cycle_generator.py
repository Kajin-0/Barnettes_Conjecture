#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json,time
from collections import defaultdict
import networkx as nx

def ce(a,b): return (a,b) if a<b else (b,a)

def generate(B,n0,n1,n2):
    assert B%2==0
    boundary_edges=tuple(ce(i,(i+1)%B) for i in range(B)); bset=set(boundary_edges)
    k=n0+n1+n2
    def cycles(vertices,edges):
        adj={v:[] for v in vertices}
        for i,(a,b) in enumerate(edges):adj[a].append((b,i));adj[b].append((a,i))
        for v in adj:adj[v].sort()
        out=set()
        for s in sorted(vertices):
            seen={s};path=[s];pem=[]
            def dfs(u):
                for v,ei in adj[u]:
                    if v==s:
                        if len(path)>=4 and path[1]<path[-1]:
                            mask=(1<<ei)
                            for x in pem:mask|=1<<x
                            out.add(mask)
                        continue
                    if v<=s or v in seen:continue
                    seen.add(v);path.append(v);pem.append(ei);dfs(v);pem.pop();path.pop();seen.remove(v)
            dfs(s)
        return sorted(out)
    def decompositions(edges):
        target=tuple(1 if e in bset else 2 for e in edges);cy=cycles(sorted({x for e in edges for x in e}),edges)
        cv=[];cont=[[] for _ in edges]
        for mask in cy:
            inds=tuple(i for i in range(len(edges)) if mask>>i&1)
            if len(inds)<4 or len(inds)%2:continue
            ci=len(cv);cv.append(inds)
            for i in inds:cont[i].append(ci)
        from functools import lru_cache
        @lru_cache(None)
        def sol(rem,slots):
            if slots==0:return ((),) if not any(rem) else ()
            if sum(rem)<4*slots:return ()
            try:p=next(i for i,x in enumerate(rem) if x)
            except StopIteration:return ()
            ans=set()
            for ci in cont[p]:
                inds=cv[ci]
                if any(rem[i]<=0 for i in inds):continue
                nr=list(rem)
                for i in inds:nr[i]-=1
                for tail in sol(tuple(nr),slots-1):ans.add(tuple(sorted((ci,)+tail)))
            return tuple(ans)
        return cv,sol(target,n0)
    def validate(edges,cv,d):
        apex=B+k;tri=[]
        for z,ci in zip(range(B,B+n0),d):
            for ei in cv[ci]:tri.append(tuple(sorted((z,*edges[ei]))))
        for a,b in boundary_edges:tri.append(tuple(sorted((apex,a,b))))
        V=B+k+1
        if len(tri)!=2*V-4 or len(set(tri))!=len(tri):return None
        inc=defaultdict(list);ges=set()
        for ti,t in enumerate(tri):
            for e in (ce(t[0],t[1]),ce(t[0],t[2]),ce(t[1],t[2])):inc[e].append(ti);ges.add(e)
        if any(len(x)!=2 for x in inc.values()) or V-len(ges)+len(tri)!=2:return None
        adj=[set() for _ in range(V)]
        for a,b in ges:adj[a].add(b);adj[b].add(a)
        seen={0};st=[0]
        while st:
            u=st.pop()
            for v in adj[u]:
                if v not in seen:seen.add(v);st.append(v)
        if len(seen)!=V:return None
        for v in range(V):
            la=defaultdict(set)
            for t in tri:
                if v in t:
                    x=[q for q in t if q!=v];la[x[0]].add(x[1]);la[x[1]].add(x[0])
            if not la or any(len(s)!=2 for s in la.values()):return None
            q=[next(iter(la))];ss=set(q)
            while q:
                u=q.pop()
                for w in la[u]:
                    if w not in ss:ss.add(w);q.append(w)
            if len(ss)!=len(la):return None
        disk={e for e in ges if apex not in e};deg=[0]*(B+k)
        for a,b in disk:deg[a]+=1;deg[b]+=1
        if any(deg[v]%2!=1 for v in range(B)):return None
        if any(deg[v]%2 or deg[v]<4 for v in range(B,B+k)):return None
        if len(disk)!=3*k+2*B-3:return None
        return tuple(sorted(disk))
    def marked(disk,swap=False):
        G=nx.Graph()
        for v in range(B+k):
            if v<B:c=1+v%2
            elif v<B+n0:c=0
            elif v<B+n0+n1:c=1
            else:c=2
            if swap and c in (1,2):c=3-c
            G.add_node(v,kind=f'c{c}')
        G.add_edges_from(disk);hub=B+k;G.add_node(hub,kind='hub')
        for i in range(B):
            q=hub+1+i;G.add_node(q,kind='be');G.add_edges_from([(q,i),(q,(i+1)%B),(hub,q)])
        return G
    c1=list(range(0,B,2))+list(range(B+n0,B+n0+n1));c2=list(range(1,B,2))+list(range(B+n0+n1,B+k))
    cand=[ce(a,b) for a in c1 for b in c2 if ce(a,b) not in bset]
    found=[];buckets=defaultdict(list);nm=nx.algorithms.isomorphism.categorical_node_match('kind',None)
    for extras in itertools.combinations(cand,k-1):
        deg=defaultdict(int)
        for a,b in extras:deg[a]+=1;deg[b]+=1
        if any(deg[v]<2 for v in c1 if v>=B) or any(deg[v]<2 for v in c2 if v>=B):continue
        edges=tuple(sorted(bset|set(extras)));cv,ds=decompositions(edges)
        for d in ds:
            disk=validate(edges,cv,d)
            if disk is None:continue
            vars=[marked(disk,False)]
            if n1==n2:vars.append(marked(disk,True))
            hs=[nx.weisfeiler_lehman_graph_hash(g,node_attr='kind',iterations=8) for g in vars];key=min(hs)
            dup=False
            for idx in buckets[key]:
                if any(nx.is_isomorphic(g,found[idx][1],node_match=nm) for g in vars):dup=True;break
            if not dup:
                buckets[key].append(len(found));found.append((disk,vars[0]))
    return [[list(e) for e in x[0]] for x in found]

def distributions(k):
    for n0 in range(k,-1,-1):
      for n1 in range(k-n0,-1,-1):
        n2=k-n0-n1
        if n1<n2:continue
        yield n0,n1,n2

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('B',type=int);ap.add_argument('k',type=int);ap.add_argument('--out');a=ap.parse_args();res={};t=time.time()
 for d in distributions(a.k):
  arr=generate(a.B,*d);res[''.join(map(str,d))]=arr;print(a.B,a.k,d,len(arr),flush=True)
 if a.out:open(a.out,'w').write(json.dumps({'B':a.B,'k':a.k,'classes':res},separators=(',',':')))
 print('total',sum(map(len,res.values())),'sec',time.time()-t)
