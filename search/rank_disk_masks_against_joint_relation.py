#!/usr/bin/env python3
"""Rank disk mask projections against an exact two-seam relation.

This is a prioritization heuristic. Whole-graph construction, embedding checks,
and exact classification remain mandatory because forest partitions matter.
"""
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path

def maps(n):
    for d in (1,-1):
        for o in range(n): yield tuple((o+d*i)%n for i in range(n))
def trans(mask,mp): return sum(1<<mp[i] for i in range(len(mp)) if mask>>i&1)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--boundary-size',type=int,required=True);ap.add_argument('--joint-relation',type=Path,required=True);ap.add_argument('--signatures',type=Path,nargs='+',required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();B=a.boundary_size;ALL=(1<<B)-1
    R=defaultdict(set)
    for line in a.joint_relation.read_text().splitlines():
        p=line.split()
        if len(p)>=3 and p[2]=='positive':R[int(p[0])].add(int(p[1]))
    S=defaultdict(set)
    for f in a.signatures:
        for line in f.read_text().splitlines():g,s=line.split(' ',1);S[g].add(int(s.split(':',1)[0]))
    rows=[]
    for g,M0 in S.items():
        M=set(M0)|{ALL^x for x in M0}
        for mi,mp in enumerate(maps(B)):
            T={trans(x,mp) for x in M};surv={x for x,Y in R.items() if Y&T};pairs=sum(len(Y&T) for Y in R.values());rows.append({'surviving_source_masks':len(surv),'compatible_mask_pairs':pairs,'disk_mask_count':len(T),'disk':g,'map':mi})
    rows.sort(key=lambda x:(x['surviving_source_masks'],x['compatible_mask_pairs'],x['disk_mask_count'],x['disk'],x['map']));a.output.write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
