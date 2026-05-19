# LearnYard DSA Sheet — Extraction Runbook

LearnYard's DSA sheet (`https://learnyard.com/practice/dsa`) is a Next.js SPA — `curl` of the URL only returns a loading shell. The entire topic tree and problem list is bundled into a single client-side JS chunk. This file is the happy-path recipe to extract any topic's problem list in seconds.

---

## Happy path (4 steps, ~30 sec total)

### Step 1 — Find the current bundle filename

The bundle name changes on every deploy (`page-<hash>.js`). Grab the current one:

```bash
curl -sL "https://learnyard.com/practice/dsa" -A "Mozilla/5.0" \
  | grep -oE 'src="[^"]*app/practice/dsa/page-[^"]+\.js[^"]*"' \
  | head -1
```

You'll get something like:
```
src="/_next/static/chunks/app/practice/dsa/page-5e4aeb85938a732d.js?dpl=..."
```

### Step 2 — Download the bundle locally

```bash
curl -sL "https://learnyard.com/_next/static/chunks/app/practice/dsa/page-<HASH>.js" \
  -A "Mozilla/5.0" -o /tmp/learnyard-dsa.js
```

(Strip the `?dpl=...` query string when downloading — not required.)

### Step 3 — List all topic groups (PROBLEM_GROUPS)

```bash
grep -oE 'PROBLEM_GROUPS\["[A-Z_]+"\] = "[^"]+"' /tmp/learnyard-dsa.js
```

Sample output (full list at time of writing):
```
PROBLEM_GROUPS["BASIC"] = "Basic"
PROBLEM_GROUPS["BASIC_ARRAY_AND_STRING"] = "Array and String"
PROBLEM_GROUPS["BASIC_MATHS"] = "Basic Maths"
PROBLEM_GROUPS["BIT_MANIPULATION"] = "Bit Manipulation"
PROBLEM_GROUPS["BINARY_SEARCH"] = "Binary Search"
PROBLEM_GROUPS["BINARY_TREE"] = "Binary Tree"
PROBLEM_GROUPS["GRAPHS"] = "Graphs"
PROBLEM_GROUPS["STRING_MATCHING_ALGOS"] = "String Matching Algos"
PROBLEM_GROUPS["COMBINATORICS_GEOMETRY"] = "Combinatorics & Geometry"
PROBLEM_GROUPS["GAME_THEORY"] = "Game Theory"
PROBLEM_GROUPS["ADVANCED_ALGO_SEGMENT_FENWICK"] = "Advance algorithm"
PROBLEM_GROUPS["DYNAMIC_PROGRAMMING_2"] = "Dynamic Programming 2"
```

### Step 4 — Extract the problem list for the target group

Once you know the group name (e.g. `COMBINATORICS_GEOMETRY`), the topic tree has structure:

```
title: PROBLEM_GROUPS.<GROUP_NAME>
subgroups: [
  { id, title: "Line",        problems: ["1186", "1187", ...] }
  { id, title: "Rectangle",   problems: [...] }
  ...
]
```

Each problem is defined elsewhere in the same bundle as:
```
id: "1186",
title: "Check if it is a Straight Line",
status: PROBLEM_STATUS.UNSOLVED,
tags: [...],
difficulty: ...PROBLEM_DIFFICULTY.EASY,
problemLink: "https://leetcode.com/..."
```

Use this Python script. **Two gotchas baked into this version** (don't simplify them out):

1. The group block uses nested arrays — a lazy regex like `[\s\S]*?\]\s*\}` matches the *inner* subgroup's `]}` not the outer one. Use a bracket-balanced walker instead.
2. Problem records have **inconsistent field order** — most use `problemLink` *before* `difficulty`, but ~36 problems (the geometry/combinatorics block) use `difficulty` *before* `problemLink`. A single fixed-order regex only catches one variant. Parse each record's body, then search for fields by key independently.

```python
python3 << 'EOF'
import re

GROUP = "COMBINATORICS_GEOMETRY"   # <-- change to target group key
BUNDLE = "/tmp/learnyard-dsa.js"

data = open(BUNDLE).read()

# 1. Build id -> (title, difficulty, link) map — tolerant of field order
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

# 2. Find the subgroups: [...] block for the target group — bracket-balanced
def extract_subgroups_block(data, group):
    m = re.search(r'title:\s*PROBLEM_GROUPS\.' + group + r'\b', data)
    if not m:
        return None
    sub_idx = data.find("subgroups:", m.start())
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

block = extract_subgroups_block(data, GROUP)
if not block:
    raise SystemExit(f"Group {GROUP} not found")

# 3. Walk each subgroup, resolve problems, print
subgroup_pat = re.compile(r'title:\s*"([^"]+)"[\s\S]*?problems:\s*\[([^\]]+)\]')
for sm in subgroup_pat.finditer(block):
    sub_title = sm.group(1)
    ids = re.findall(r'"(\d+)"', sm.group(2))
    print(f"\n## {sub_title} ({len(ids)})")
    for pid in ids:
        if pid in problems:
            t, d, l = problems[pid]
            print(f"  [{d:6}] {t}  —  {l}")
        else:
            print(f"  [{pid}] NOT FOUND")
EOF
```

Replace `GROUP = "..."` with any key from Step 3. Re-runs in <1 sec.

**For multiple groups in one go:** wrap step 3 in a loop over a list of group keys, or generate a full topic dump as in `learnyard-topics.md`.

---

## Why this works

LearnYard ships the *entire* DSA sheet (groups, subgroups, all problem metadata) as static data inside the page's JS chunk. There's no API call to fetch it at runtime — it's all in `page-<hash>.js`. So once you have the bundle locally, the topic tree and problem list are just regex extractions.

The only fragile bit is the bundle filename, which is content-hashed and changes on every deploy. Step 1 always finds the current name.

---

## Useful one-liners

**Count problems in every group (sanity check):**
```bash
python3 -c "
import re
data = open('/tmp/learnyard-dsa.js').read()
for g in re.findall(r'PROBLEM_GROUPS\[\"([A-Z_]+)\"\]', data):
    pat = re.compile(r'title:\s*PROBLEM_GROUPS\.' + g + r'[\s\S]*?subgroups:\s*\[([\s\S]*?)\n\s*\]')
    m = pat.search(data)
    if m:
        ids = re.findall(r'\"\d+\"', m.group(1))
        print(f'{g:40} {len(ids)} problems')
"
```

**Find a specific problem by name:**
```bash
grep -oE 'id: "[0-9]+",[^}]*title: "[^"]*<KEYWORD>[^"]*"' /tmp/learnyard-dsa.js
```

**Total problem count on the sheet:**
```bash
grep -cE '^\s*id:\s*"[0-9]+",$' /tmp/learnyard-dsa.js
```

---

## Last verified

- 2026-05-18 — bundle was `page-5e4aeb85938a732d.js`, 872 KB, contained 1604 parseable problems
- 10 groups extracted into `learnyard-topics.md`: Tries, DP Level 1, DP Level 2, Recursion & Backtracking, Game Theory, Graphs, Binary Search, Greedy, Bit Manipulation, Combinatorics & Geometry

## Group key reference

Common group keys (from `PROBLEM_GROUPS["..."]`):

| Key | Display name |
|---|---|
| `BASIC_ARRAY_AND_STRING` | Array and String |
| `BASIC_MATHS` | Basic Maths Level 1 |
| `MATH_2` | Math Level 2 |
| `RECURSION_BASICS` | Recursion Basics |
| `SORTING` | Sorting |
| `TWO_POINTERS` | 2 Pointers |
| `PREFIX_SUM` | Prefix Sum |
| `MATRIX` | Matrix |
| `HASHING` | Hashing |
| `SLIDING_WINDOW` | Sliding Window |
| `LINKED_LIST` | Linked List |
| `STACK` | Stack |
| `QUEUE` | Queue |
| `BINARY_SEARCH` | Binary Search |
| `BIT_MANIPULATION` | Bit Manipulation |
| `RECURSION_BACKTRACKING` | Recursion & Backtracking |
| `TREE_BST` | Tree + BST |
| `HEAP_PRIORITY_QUEUE` | Heap (Priority Queue) |
| `TRIES` | Tries |
| `GREEDY` | Greedy |
| `DYNAMIC_PROGRAMMING_1` | Dynamic Programming Level 1 |
| `DYNAMIC_PROGRAMMING_2` | Dynamic Programming Level 2 |
| `BST` | Binary Search Tree |
| `BINARY_TREE` | Binary Tree |
| `GRAPHS` | Graphs |
| `STRING_MATCHING_ALGOS` | String Matching Algos |
| `COMBINATORICS_GEOMETRY` | Combinatorics & Geometry |
| `GAME_THEORY` | Game Theory |
| `ADVANCED_ALGO_SEGMENT_FENWICK` | Advance algorithm |
