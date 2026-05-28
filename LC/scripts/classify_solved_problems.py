import csv, os, re

# Map First-Attempt filename → real slug (aliases)
ALIAS = {
  "happy-strings": "the-k-th-lexicographical-string-of-all-happy-strings-of-length-n",
  "construct-bst-from-preorder": "construct-binary-search-tree-from-preorder-traversal",
  "restore-array-from-adjacent-pairs": "restore-the-array-from-adjacent-pairs",
}

# Solved files in order
solved_files = []
for fn in sorted(os.listdir("1550-1600/First-Attempt")):
    m = re.match(r'^(\d+)-(.+)\.md$', fn)
    if m:
        num = int(m.group(1)); name = m.group(2)
        slug = ALIAS.get(name, name)
        solved_files.append((num, name, slug))

# Load editorials summary for classification signals
edsum = {}
with open("editorials-data/band_1550_1599_summary.tsv") as f:
    r = csv.reader(f, delimiter="\t"); next(r)
    for row in r:
        if len(row)<6: continue
        edsum[row[0]] = {"tags": row[4], "appr": row[5]}

# Load classifier RULES
src = open("scripts/classify_band_to_learnyard.py").read()
start = src.index("RULES = ["); depth=0; i=start+len("RULES = ")
while i < len(src):
    if src[i]=='[':depth+=1
    elif src[i]==']':
        depth-=1
        if depth==0:break
    i+=1
ns={}; exec(src[start:i+1], ns); RULES=ns["RULES"]

# lc tags
lctags={}
with open("zerotrac-data/band_1550_1599_lctags.tsv") as f:
    r=csv.reader(f,delimiter="\t"); next(r)
    for row in r:
        if len(row)>=9: lctags[row[3]]=row[8]

def classify(slug):
    sig=[]
    if slug in edsum:
        if edsum[slug]["tags"]: sig.append(edsum[slug]["tags"].replace("|"," | "))
        if edsum[slug]["appr"]:
            sig += [a for a in edsum[slug]["appr"].split("|") if a and "tabs:start" not in a]
    sig.append(lctags.get(slug,""))
    blob=" ; ".join(sig)
    hits,seen=[],set()
    for pat,(mt,sg) in RULES:
        if re.search(pat,blob,re.I) and (mt,sg) not in seen:
            hits.append(f"{mt}/{sg}"); seen.add((mt,sg))
    return hits

for num, name, slug in solved_files:
    g = classify(slug)
    print(f"#{num:2} {name[:45]:<45} → {'; '.join(g[:3]) if g else '(unclassified)'}")
