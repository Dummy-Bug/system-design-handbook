"""
Classify each band problem into LearnYard subgroups using THREE signals:
1. doocs editorial tags (algorithmic)
2. doocs approach names (e.g. "DP + Monotonic Stack")
3. LC official topicTags (fallback)

Output: per-band TSV with LY subgroup assignments + supply counts.
"""
import csv, sys, os, re

BAND = "1500_1549"
LCTAGS = f"zerotrac-data/band_{BAND}_lctags.tsv"
DOOCS_SUM = f"editorials-data/band_{BAND}_summary.tsv"
OUT_TSV = f"editorials-data/band_{BAND}_subgroups.tsv"
OUT_SUPPLY = f"editorials-data/band_{BAND}_subgroup_supply.tsv"

# Build a (doocs-tag OR approach-keyword) → list of LY subgroups
# Each rule is a regex pattern → (main_topic, subgroup)
RULES = [
    # === Stack family ===
    (r'\bMonotonic Stack\b', ("Stack", "Monotonic Stack")),
    (r'\bStack\b.*\bString\b|\bString\b.*\bStack\b', ("Stack", "Stack with String")),
    (r'^Stack$|\bStack\b(?!.*Monotonic)', ("Stack", "Implementary Stack")),
    # === Queue family ===
    (r'\bMonotonic Queue\b', ("Queue", "Monotonic Queue")),
    # === Heap family ===
    (r'\bHeap\b.*\bGreedy\b|\bGreedy\b.*\bHeap\b|\bPriority Queue\b.*\bGreedy\b', ("Heap (Priority Queue)", "Heap-Greedy")),
    (r'\bK-?th\b.*\b(Element|Largest|Smallest|Number)\b', ("Heap (Priority Queue)", "Kth Element Problems")),
    (r'\bHeap\b|\bPriority Queue\b', ("Heap (Priority Queue)", "Implementary Questions")),
    # === Tries ===
    (r'\bTrie\b.*\bBit\b|\bBit\b.*\bTrie\b', ("Tries", "Trie with Bit Manipulation")),
    (r'\bTrie\b.*\bString\b|\bString\b.*\bTrie\b|^Trie$|\bTrie\b', ("Tries", "Trie involving String")),
    # === DP — SPECIFIC PATTERNS FIRST ===
    (r'\bBitmask\b.*\bDP\b|\bDP\b.*\bBitmask\b|\bDP\b.*\bBit Manipulation\b', ("Dynamic Programming Level 2", "DP with Bitmask")),
    (r'\bDigit DP\b', ("Dynamic Programming Level 2", "Digit DP")),
    (r'\bTree\b.*\b(DP|Dynamic Programming)\b|\bDP\b.*\bTree\b', ("Dynamic Programming Level 2", "DP on Trees")),
    (r'\bProbability\b.*\bDP\b|\bDP\b.*\bProbability\b', ("Dynamic Programming Level 2", "Dp with Probability")),
    (r'\bLongest Increasing Subsequence\b|\bLIS\b', ("Dynamic Programming Level 1", "Longest Increasing Subsequence")),
    (r'\bLongest Common Subsequence\b|\bLCS\b', ("Dynamic Programming Level 1", "Longest Common Subsequence")),
    (r'\bMatrix Chain Multiplication\b|\bMCM\b|\bInterval DP\b', ("Dynamic Programming Level 1", "Matrix Chain Multiplication")),
    (r'\bKadane\b', ("Dynamic Programming Level 1", "Kadane Algo")),
    (r'\bKnapsack\b', ("Dynamic Programming Level 1", "Knapsack DP")),
    (r'\bDP\b.*\bString\b|\bString\b.*\bDP\b|\bDynamic Programming\b.*\bString\b', ("Dynamic Programming Level 1", "DP on String")),
    (r'\bDP\b.*\bGrid\b|\bGrid\b.*\bDP\b|\bDP\b.*\bMatrix\b|\bDynamic Programming\b.*\bMatrix\b', ("Dynamic Programming Level 1", "DP On Grid")),
    (r'\b2D DP\b|\bTwo-?Dimensional DP\b', ("Dynamic Programming Level 1", "2 Dimensional DP")),
    (r'\bPrefix Sum\b.*\bDP\b|\bCumulative\b.*\bDP\b', ("Dynamic Programming Level 1", "Cummulative Sum")),
    # generic DP → Linear (last resort within DP)
    (r'\bDynamic Programming\b|^DP$|\bDP\b', ("Dynamic Programming Level 1", "Linear DP")),
    # === Graph subgroups ===
    (r'\bTopological Sort\b', ("Graphs", "Topological Sort")),
    (r'\bUnion[- ]?Find\b|\bDisjoint Set\b|\bDSU\b', ("Graphs", "Disjoint Set Union")),
    (r'\bDijkstra\b', ("Graphs", "Dijsktra Algorithm")),
    (r'\bBellman[- ]?Ford\b', ("Graphs", "Bellman Ford")),
    (r'\bFloyd[- ]?Warshall\b', ("Graphs", "Floyd Warshall")),
    (r'\bTSP\b|\bTravelling Salesman\b', ("Graphs", "Travelling Salesman Problem")),
    (r'\bMinimum Spanning Tree\b|\bMST\b|\bKruskal\b|\bPrim\b', ("Graphs", "Minimum Spanning Tree")),
    (r'\bShortest Path\b.*\bHeap\b|\bHeap\b.*\bShortest Path\b', ("Graphs", "Dijsktra Algorithm")),
    (r'\bCycle Detection\b|\bCycle in.*Graph\b', ("Graphs", "Cycle Detection")),
    (r'\bMulti[- ]?Source BFS\b', ("Graphs", "Multi Source BFS")),
    (r'\bFlood Fill\b|\bIsland\b|\bConnected Components.*Grid\b', ("Graphs", "Flood Fill")),
    (r'\bGraph\b', ("Graphs", "Graph Representation")),
    # === Binary Search subgroups ===
    (r'\bBinary Search on Answer\b|\bBinary Search\b.*\bGreedy\b|\bMin-?Max\b', ("Binary Search", "Binary Search On Answer")),
    (r'\bBinary Search\b.*\bMatrix\b', ("Binary Search", "Search on Matrix")),
    (r'\bUpper Bound\b|\bLower Bound\b', ("Binary Search", "Upper Bound and Lower Bound")),
    (r'\bBinary Search\b', ("Binary Search", "Upper Bound and Lower Bound")),
    # === Greedy (Part I covers everything in low bands) ===
    (r'\bGreedy\b', ("Greedy", "Part I")),
    # === Hashing ===
    (r'\bHash Table\b|\bHash Map\b|\bHashing\b|\bHash Set\b', ("Hashing", "Implementary Problems")),
    # === Sliding Window ===
    (r'\bFixed.?Size.*Sliding\b|\bSliding Window\b.*\bFixed\b', ("Sliding Window", "Fixed Size Sliding-Window")),
    (r'\bSliding Window\b', ("Sliding Window", "Dynamic Size Sliding-Window")),
    # === Two Pointers ===
    (r'\bTwo Pointers\b.*\bString\b|\bString\b.*\bTwo Pointers\b', ("2 Pointers", "Two Pointer on Strings")),
    (r'\bTwo Pointers\b', ("2 Pointers", "Two Pointer on Arrays")),
    # === Bit Manipulation ===
    (r'\bXOR\b|\bBitwise XOR\b', ("Bit Manipulation", "Bitwise XOR operator")),
    (r'\bBitwise OR\b', ("Bit Manipulation", "Bitwise OR operator")),
    (r'\bBitwise AND\b', ("Bit Manipulation", "Bitwise AND operator")),
    (r'\bBit Manipulation\b', ("Bit Manipulation", "Basic Bit Concepts")),
    # === Recursion & Backtracking ===
    (r'\bPermutation\b.*\bBacktrack\b|\bBacktrack\b.*\bPermutation\b', ("Recursion & Backtracking", "Permutation Problems")),
    (r'\bCombination\b.*\bBacktrack\b|\bBacktrack\b.*\bCombination\b|\bBacktrack\b.*\bMath\b', ("Recursion & Backtracking", "Combination Problems")),
    (r'\bSubsets?\b.*\bBacktrack\b|\bBacktrack\b.*\bSubsets?\b', ("Recursion & Backtracking", "Subsets Problems")),
    (r'\bBacktracking\b', ("Recursion & Backtracking", "Recursion Problems")),
    # === Game Theory ===
    (r'\bGame Theory\b', ("Game Theory", "Level I")),
    # === Advance Algorithm ===
    (r'\bSegment Tree\b|\bFenwick\b|\bBinary Indexed Tree\b', ("Advance algorithm", "Segment Tree / BIT")),
    # === Binary Tree / BST ===
    (r'\bBinary Search Tree\b|\bBST\b', ("Binary Search Tree", "Implementary")),
    (r'\bBinary Tree\b', ("Binary Tree", "Implementary")),
    # === Combinatorics & Geometry ===
    (r'\bGeometry\b', ("Combinatorics & Geometry", "Line")),
    (r'\bCombinatorics\b', ("Combinatorics & Geometry", "Combinatorics")),
    # === String Matching Algos ===
    (r'\bKMP\b|\bZ[- ]?Algo\b|\bRolling Hash\b|\bString Matching\b', ("String Matching Algos", "Pattern Matching")),
    # === Linked List / Matrix / Sorting (catch-all foundationals) ===
    (r'\bLinked List\b', ("Linked List", "Implementary")),
    (r'\bMatrix\b', ("Matrix", "Implementary")),
    (r'\bSorting\b(?!.*Greedy)', ("Sorting", "Implementary")),
    (r'\bPrefix Sum\b', ("Prefix Sum", "Implementary")),
]

# Load LC tags + doocs summary
band_meta = {}  # slug → dict
with open(LCTAGS) as f:
    r = csv.reader(f, delimiter="\t")
    next(r)
    for row in r:
        if len(row) < 9: continue
        rating, pid, title, slug, contest, qpos, diff, ar, tags = row
        band_meta[slug] = {"rating": rating, "id": pid, "title": title, "qpos": qpos, "ar": ar, "lc_tags": tags, "doocs_tags": "", "approaches": ""}

with open(DOOCS_SUM) as f:
    r = csv.reader(f, delimiter="\t")
    next(r)
    for row in r:
        if len(row) < 7: continue
        slug, pid, title, status, doocs_tags, approaches = row[:6]
        if slug in band_meta:
            band_meta[slug]["doocs_tags"] = doocs_tags
            band_meta[slug]["approaches"] = approaches

# Classify each problem
def classify(meta):
    """Return list of (main, sub) tuples. Apply rules in order, collect unique hits."""
    # Build a single signal string: doocs tags + approaches + lc tags (priority order)
    signals = []
    if meta["doocs_tags"]:
        signals.append(meta["doocs_tags"].replace("|", " | "))
    if meta["approaches"]:
        # filter out template noise
        appr = [a for a in meta["approaches"].split("|") if a and "tabs:start" not in a]
        signals.extend(appr)
    signals.append(meta["lc_tags"])
    blob = " ; ".join(signals)

    hits = []
    seen = set()
    for pat, (mt, sg) in RULES:
        if re.search(pat, blob, re.IGNORECASE):
            key = (mt, sg)
            if key not in seen:
                hits.append(key)
                seen.add(key)
    return hits

# Per-problem classification
with open(OUT_TSV, "w") as o:
    o.write("Slug\tID\tTitle\tQPos\tAR\tSubgroups\n")
    supply = {}
    for slug, m in band_meta.items():
        groups = classify(m)
        sg_str = "; ".join(f"{mt}/{sg}" for mt, sg in groups) if groups else "(unclassified)"
        o.write(f"{slug}\t{m['id']}\t{m['title']}\t{m['qpos']}\t{m['ar']}\t{sg_str}\n")
        for mt, sg in groups:
            supply.setdefault((mt, sg), []).append((slug, m["title"], m["qpos"], m["ar"]))

with open(OUT_SUPPLY, "w") as o:
    o.write("MainTopic\tSubgroup\tCount\tEasiest_Title\tEasiest_AR\tEasiest_QPos\tEasiest_Slug\n")
    for (mt, sg), probs in sorted(supply.items(), key=lambda x: -len(x[1])):
        # easiest = highest AR, tiebreak by Q-pos (lower better)
        sorted_probs = sorted(probs, key=lambda p: (-float(p[3].rstrip("%") or "0"), p[2]))
        e = sorted_probs[0]
        o.write(f"{mt}\t{sg}\t{len(probs)}\t{e[1]}\t{e[3]}\t{e[2]}\t{e[0]}\n")

# Stdout summary
print(f"=== Per-subgroup supply (≥1) — 1500-1549 ===")
print(f"{'Cnt':>3}  {'Main':<30}  Subgroup")
for (mt, sg), probs in sorted(supply.items(), key=lambda x: -len(x[1])):
    print(f"{len(probs):>3}  {mt:<30}  {sg}")
print(f"\n=== ≥3 supply (Group A eligible at this band) ===")
ge3 = [(mt, sg, len(p)) for (mt, sg), p in supply.items() if len(p) >= 3]
for mt, sg, n in sorted(ge3, key=lambda x: -x[2]):
    print(f"  {n:>3}  {mt} → {sg}")
