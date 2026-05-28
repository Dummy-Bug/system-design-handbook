import csv

# LC-tag → LearnYard subgroup mapping
# Each rule: lambda(tag_set) → list of (main, sub) it matches
def classify(tags_str):
    T = set(t.strip() for t in tags_str.split(","))
    hits = []

    # === Stack subgroups ===
    if "Monotonic Stack" in T:
        hits.append(("Stack", "Monotonic Stack"))
    elif "Stack" in T and "String" in T:
        hits.append(("Stack", "Stack with String"))
    elif "Stack" in T:
        hits.append(("Stack", "Implementary Stack"))

    # === Queue subgroups ===
    if "Monotonic Queue" in T:
        hits.append(("Queue", "Monotonic Queue"))

    # === Heap ===
    if "Heap (Priority Queue)" in T:
        if "Sorting" in T or "Greedy" in T:
            hits.append(("Heap (Priority Queue)", "Heap-Greedy"))
        hits.append(("Heap (Priority Queue)", "Implementary Questions"))

    # === Trie ===
    if "Trie" in T:
        if "Bit Manipulation" in T:
            hits.append(("Tries", "Trie with Bit Manipulation"))
        elif "String Matching" in T or "String" in T:
            hits.append(("Tries", "Trie involving String"))
        else:
            hits.append(("Tries", "Introductory Questions"))

    # === DP L1 / L2 ===
    if "Dynamic Programming" in T:
        if "Bitmask" in T:
            hits.append(("Dynamic Programming Level 2", "DP with Bitmask"))
        elif "Tree" in T or "Binary Tree" in T:
            hits.append(("Dynamic Programming Level 2", "DP on Trees"))
        elif "Probability and Statistics" in T:
            hits.append(("Dynamic Programming Level 2", "Dp with Probability"))
        elif "Math" in T and not "String" in T:
            hits.append(("Dynamic Programming Level 2", "DP with Math"))
        elif "String" in T:
            hits.append(("Dynamic Programming Level 1", "DP on String"))
        elif "Matrix" in T or "Grid" in T:
            hits.append(("Dynamic Programming Level 1", "DP On Grid"))
        elif "Prefix Sum" in T:
            hits.append(("Dynamic Programming Level 1", "Cummulative Sum"))
        else:
            hits.append(("Dynamic Programming Level 1", "Linear DP"))

    # === Graph subgroups ===
    has_graph = "Graph Theory" in T or "Breadth-First Search" in T or "Depth-First Search" in T or "Matrix" in T
    if "Topological Sort" in T:
        hits.append(("Graphs", "Topological Sort"))
    elif "Union Find" in T:
        hits.append(("Graphs", "Disjoint Set Union"))
    elif "Shortest Path" in T:
        if "Heap (Priority Queue)" in T:
            hits.append(("Graphs", "Dijsktra Algorithm"))
        else:
            hits.append(("Graphs", "Bellman Ford"))
    elif "Minimum Spanning Tree" in T:
        hits.append(("Graphs", "Minimum Spanning Tree"))
    elif has_graph:
        if "Matrix" in T and ("Breadth-First Search" in T or "Depth-First Search" in T):
            if "Multi-Source BFS" in tags_str or T & {"Breadth-First Search"}:
                hits.append(("Graphs", "Flood Fill"))
        elif "Graph Theory" in T:
            hits.append(("Graphs", "Graph Representation"))

    # === Binary Search subgroups ===
    if "Binary Search" in T:
        if "Greedy" in T or "Math" in T:
            hits.append(("Binary Search", "Binary Search On Answer"))
        elif "Matrix" in T:
            hits.append(("Binary Search", "Search on Matrix"))
        else:
            hits.append(("Binary Search", "Upper Bound and Lower Bound"))

    # === Greedy ===
    if "Greedy" in T:
        hits.append(("Greedy", "Part I"))

    # === Hashing ===
    if "Hash Table" in T:
        hits.append(("Hashing", "Implementary Problems"))

    # === Sliding Window ===
    if "Sliding Window" in T:
        hits.append(("Sliding Window", "Dynamic Size Sliding-Window"))

    # === Two Pointers ===
    if "Two Pointers" in T:
        if "String" in T:
            hits.append(("2 Pointers", "Two Pointer on Strings"))
        else:
            hits.append(("2 Pointers", "Two Pointer on Arrays"))

    # === Bit Manipulation ===
    if "Bit Manipulation" in T:
        if "Trie" not in T:
            hits.append(("Bit Manipulation", "Bitwise XOR operator"))

    # === Recursion & Backtracking ===
    if "Backtracking" in T:
        if "Math" in T or "Combinatorics" in T:
            hits.append(("Recursion & Backtracking", "Combination Problems"))
        else:
            hits.append(("Recursion & Backtracking", "Recursion Problems"))

    # === Game Theory ===
    if "Game Theory" in T:
        hits.append(("Game Theory", "Level I"))

    # === Segment Tree / BIT (Advance algorithm) ===
    if "Segment Tree" in T or "Binary Indexed Tree" in T:
        hits.append(("Advance algorithm", "Segment Tree"))

    # === Binary Tree / BST ===
    if "Binary Tree" in T and "Dynamic Programming" not in T:
        hits.append(("Binary Tree", "Implementary"))
    if "Binary Search Tree" in T:
        hits.append(("Binary Search Tree", "Implementary"))

    # === Combinatorics & Geometry ===
    if "Geometry" in T:
        hits.append(("Combinatorics & Geometry", "Line"))
    if "Combinatorics" in T and "Dynamic Programming" not in T:
        hits.append(("Combinatorics & Geometry", "Combinatorics"))

    # === Math / Number Theory (no dedicated LY topic — record under DP-with-Math or skip) ===
    # Math without DP is foundational, classified under Bit Manipulation if XOR is present, else generic
    # If only Math+Array → no LY subgroup match; record as "Math (no LY subgroup)"
    if "Number Theory" in T or ("Math" in T and "Dynamic Programming" not in T and "Geometry" not in T and "Combinatorics" not in T and "Bit Manipulation" not in T):
        hits.append(("(Math — no LY subgroup)", "Number Theory / Math"))

    return hits

supply = {}
band_total = 0
with open("zerotrac-data/band_1500_1549_lctags.tsv") as f:
    r = csv.reader(f, delimiter="\t")
    next(r)
    for row in r:
        if len(row) < 9: continue
        band_total += 1
        slug, qpos, ar, tags = row[3], row[5], row[7], row[8]
        for mt, sg in classify(tags):
            supply.setdefault((mt, sg), []).append((row[2], qpos, ar))  # title, qpos, ar

print(f"Band total: {band_total} problems")
print()
print(f"=== Supply per LearnYard subgroup (≥1 in 1500-1549) ===")
print(f"{'Count':>5}  {'Main Topic':<32}  Subgroup")
for (mt, sg), probs in sorted(supply.items(), key=lambda x: -len(x[1])):
    print(f"{len(probs):>5}  {mt:<32}  {sg}")

print(f"\n=== Subgroups with ≥3 supply (Group A candidates) ===")
ge3 = [(mt, sg, len(probs)) for (mt, sg), probs in supply.items() if len(probs) >= 3]
ge3.sort(key=lambda x: -x[2])
for mt, sg, n in ge3:
    print(f"  {n:>3}  {mt} → {sg}")
