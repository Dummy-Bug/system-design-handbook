import re, os, sys
from urllib.parse import urlparse

BUNDLE = "/tmp/learnyard-dsa.js"
OUT_DIR = "/Users/home/Desktop/wiki/LC/learnyard-data"
os.makedirs(OUT_DIR, exist_ok=True)

data = open(BUNDLE).read()

# Build id → (title, difficulty, link) map — tolerant of field order
record_pat = re.compile(r'\{\s*id:\s*"(\d+)",\s*(.*?)\}', re.DOTALL)
problems = {}
for m in record_pat.finditer(data):
    pid, body = m.group(1), m.group(2)
    if 'PROBLEM_STATUS' not in body or 'problemLink' not in body:
        continue
    title_m = re.search(r'title:\s*"([^"]+)"', body)
    diff_m  = re.search(r'PROBLEM_DIFFICULTY\.(\w+)', body)
    link_m  = re.search(r'problemLink:\s*"([^"]+)"', body)
    if title_m and link_m:
        diff = diff_m.group(1) if diff_m else "?"
        problems[pid] = (title_m.group(1), diff, link_m.group(1))
print(f"Total problem records: {len(problems)}", file=sys.stderr)

# List groups
group_keys = re.findall(r'PROBLEM_GROUPS\["([A-Z_0-9]+)"\]\s*=\s*"([^"]+)"', data)
group_keys = [(k, v) for k, v in group_keys if k != "ANY"]

def extract_subgroups_block(group):
    m = re.search(r'title:\s*PROBLEM_GROUPS\.' + group + r'\b', data)
    if not m: return None
    sub_idx = data.find("subgroups:", m.start())
    if sub_idx < 0: return None
    start = data.find("[", sub_idx)
    depth, i = 0, start
    while i < len(data):
        if data[i] == '[': depth += 1
        elif data[i] == ']':
            depth -= 1
            if depth == 0:
                return data[start+1:i]
        i += 1
    return None

def slug_of(url):
    try:
        p = urlparse(url)
        if "leetcode.com" in p.netloc:
            mm = re.search(r"/problems/([^/]+)", p.path)
            return mm.group(1) if mm else ""
    except Exception:
        pass
    return ""

def source_of(url):
    try:
        p = urlparse(url)
        if "leetcode.com" in p.netloc: return "leetcode"
        if "geeksforgeeks.org" in p.netloc: return "gfg"
        if "atcoder.jp" in p.netloc: return "atcoder"
        if "codeforces.com" in p.netloc: return "codeforces"
        if "codechef.com" in p.netloc: return "codechef"
        if "hackerrank.com" in p.netloc: return "hackerrank"
        if "spoj.com" in p.netloc: return "spoj"
        if "cses.fi" in p.netloc: return "cses"
        if "naukri.com" in p.netloc: return "naukri"
        if p.netloc: return p.netloc
    except Exception:
        pass
    return "unknown"

subgroup_pat = re.compile(r'title:\s*"([^"]+)"[\s\S]*?problems:\s*\[([^\]]+)\]')
def safe(name):
    return re.sub(r"[^a-z0-9]+","-", name.lower()).strip("-")

all_rows = []
subgroup_counts = []
missing_ids = []

for gkey, gname in group_keys:
    block = extract_subgroups_block(gkey)
    if not block:
        print(f"  ⚠ Group not found in tree: {gkey}", file=sys.stderr)
        continue
    rows = []
    for sm in subgroup_pat.finditer(block):
        sub_title = sm.group(1)
        ids = re.findall(r'"(\d+)"', sm.group(2))
        cnt = 0
        for pid in ids:
            if pid in problems:
                t, d, l = problems[pid]
                # strip query string for cleanliness
                clean_l = l.split("?")[0]
                rows.append((gname, sub_title, d.capitalize() if d != "?" else "?", t, slug_of(clean_l), source_of(clean_l), clean_l))
                cnt += 1
            else:
                missing_ids.append(pid)
        subgroup_counts.append((gname, sub_title, cnt))
    # Per-group TSV
    if rows:
        with open(f"{OUT_DIR}/{safe(gname)}.tsv","w") as o:
            o.write("Subgroup\tDifficulty\tTitle\tSlug\tSource\tLink\n")
            for r in rows:
                o.write("\t".join(r[1:]) + "\n")
    all_rows.extend(rows)

# Master TSV
with open(f"{OUT_DIR}/all_problems.tsv","w") as o:
    o.write("MainTopic\tSubgroup\tDifficulty\tTitle\tSlug\tSource\tLink\n")
    for r in all_rows:
        o.write("\t".join(r) + "\n")

# Subgroups index
with open(f"{OUT_DIR}/subgroups.tsv","w") as o:
    o.write("MainTopic\tSubgroup\tProblemCount\n")
    for mt, sg, c in subgroup_counts:
        o.write(f"{mt}\t{sg}\t{c}\n")

# Sources summary
with open(f"{OUT_DIR}/sources.tsv","w") as o:
    src_counts = {}
    for r in all_rows:
        src_counts[r[5]] = src_counts.get(r[5], 0) + 1
    o.write("Source\tCount\n")
    for s, c in sorted(src_counts.items(), key=lambda x: -x[1]):
        o.write(f"{s}\t{c}\n")

print(f"\nTotal rows extracted: {len(all_rows)}")
print(f"Total subgroups: {len(subgroup_counts)}")
print(f"Missing problem ID references: {len(set(missing_ids))}")
print(f"Files: {sorted(os.listdir(OUT_DIR))}")
