import csv, sys, os, re
BAND="1600_1649"
LCTAGS=f"zerotrac-data/band_{BAND}_lctags.tsv"
DOOCS=f"editorials-data/band_{BAND}_summary.tsv"
OUT_TSV=f"editorials-data/band_{BAND}_subgroups.tsv"
OUT_SUP=f"editorials-data/band_{BAND}_subgroup_supply.tsv"

solved=set(l.strip() for l in open("/tmp/solved1600.txt") if l.strip())
print(f"Excluding {len(solved)} solved", file=sys.stderr)

src=open("scripts/classify_band_to_learnyard.py").read()
s=src.index("RULES = [");d=0;i=s+len("RULES = ")
while i<len(src):
    if src[i]=='[':d+=1
    elif src[i]==']':
        d-=1
        if d==0:break
    i+=1
ns={};exec(src[s:i+1],ns);RULES=ns["RULES"]

meta={}
with open(LCTAGS) as f:
    r=csv.reader(f,delimiter="\t");next(r)
    for row in r:
        if len(row)<9:continue
        if row[3] in solved:continue
        meta[row[3]]={"id":row[1],"title":row[2],"qpos":row[5],"ar":row[7],"lc":row[8],"dt":"","ap":""}
with open(DOOCS) as f:
    r=csv.reader(f,delimiter="\t");next(r)
    for row in r:
        if len(row)<6:continue
        if row[0] in meta: meta[row[0]]["dt"]=row[4];meta[row[0]]["ap"]=row[5]

def classify(m):
    sig=[]
    if m["dt"]:sig.append(m["dt"].replace("|"," | "))
    if m["ap"]:sig+=[a for a in m["ap"].split("|") if a and "tabs:start" not in a]
    sig.append(m["lc"])
    blob=" ; ".join(sig)
    hits,seen=[],set()
    for pat,(mt,sg) in RULES:
        if re.search(pat,blob,re.I) and (mt,sg) not in seen:hits.append((mt,sg));seen.add((mt,sg))
    return hits

sup={}
with open(OUT_TSV,"w") as o:
    o.write("Slug\tID\tTitle\tQPos\tAR\tSubgroups\n")
    for slug,m in meta.items():
        g=classify(m)
        o.write(f"{slug}\t{m['id']}\t{m['title']}\t{m['qpos']}\t{m['ar']}\t{'; '.join(f'{a}/{b}' for a,b in g) or '(unclassified)'}\n")
        for a,b in g:sup.setdefault((a,b),[]).append((slug,m['title'],m['qpos'],m['ar']))
with open(OUT_SUP,"w") as o:
    o.write("MainTopic\tSubgroup\tCount\tEasiest_Title\tEasiest_AR\tEasiest_QPos\tEasiest_Slug\n")
    for (a,b),ps in sorted(sup.items(),key=lambda x:-len(x[1])):
        sp=sorted(ps,key=lambda p:(-float(p[3].rstrip('%') or '0'),p[2]));e=sp[0]
        o.write(f"{a}\t{b}\t{len(ps)}\t{e[1]}\t{e[3]}\t{e[2]}\t{e[0]}\n")
print(f"Unsolved classified: {len(meta)}")
for (a,b),ps in sorted(sup.items(),key=lambda x:-len(x[1])):
    print(f"{len(ps):>3}  {a:<28} {b}")
