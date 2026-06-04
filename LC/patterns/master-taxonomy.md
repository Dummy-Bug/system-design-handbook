# Master Pattern Taxonomy — LearnYard ∪ AlgoMaster

> Built 2026-05-29. The canonical pattern list for classifying any problem in any band.
> Merge of three sources: **[LY]** LearnYard DSA sheet (`learnyard-topics.md` + band classification TSVs),
> **[A15]** AlgoMaster [15 LeetCode patterns](https://blog.algomaster.io/p/15-leetcode-patterns),
> **[A20]** AlgoMaster [20 DP patterns](https://blog.algomaster.io/p/20-patterns-to-master-dynamic-programming).
>
> Merge rule: if the same pattern appears in multiple sources → one merged entry tagged with all sources.
> If a pattern is unique to one source → kept via union (tagged with its single source).
> `()` after a LearnYard subgroup = problem count on the LearnYard sheet.

---

## Arrays & Two Pointers

| Pattern | Sources | Notes |
|---|---|---|
| Two Pointer on Arrays (8) | [LY][A15] | "Two Pointers" in AlgoMaster |
| Two Pointer on Strings (5) | [LY][A15] | |
| Fast & Slow Pointers | [A15] | union-only — cycle detection on linked structures |

## Sliding Window

| Pattern | Sources | Notes |
|---|---|---|
| Dynamic Size Sliding-Window | [LY][A15] | |
| Fixed Size Sliding-Window | [A15] | AlgoMaster sub-variant |

## Prefix Sum

| Pattern | Sources | Notes |
|---|---|---|
| Prefix Sum / Difference Array | [LY][A15] | LearnYard "Prefix Sum/Implementary"; includes 1D & 2D diff-array |

## Hashing

| Pattern | Sources | Notes |
|---|---|---|
| Hashing / Implementary Problems | [LY] | union-only — not an AlgoMaster pattern (substrate) |
| Canonical-form counting | [LY] | (sorted-key grouping) |

## Sorting

| Pattern | Sources | Notes |
|---|---|---|
| Sorting / Implementary | [LY] | union-only — substrate, not an AlgoMaster pattern |

## Stack

| Pattern | Sources | Notes |
|---|---|---|
| Implementary Stack | [LY] | |
| Stack with String | [LY] | |
| Monotonic Stack | [LY][A15] | ★ blind-spot pattern |

## Linked List

| Pattern | Sources | Notes |
|---|---|---|
| Implementary | [LY] | |
| In-place Reversal | [A15] | union-only |

## Heap (Priority Queue)

| Pattern | Sources | Notes |
|---|---|---|
| Implementary Questions | [LY] | |
| Top-K Elements | [A15] | merged — heap/quickselect for k largest/smallest |

## Intervals

| Pattern | Sources | Notes |
|---|---|---|
| Overlapping Intervals | [A15] | union-only — merge/insert/sweep on intervals |

## Binary Search

| Pattern | Sources | Notes |
|---|---|---|
| Introductory Problems (3) | [LY] | |
| Upper Bound and Lower Bound (23) | [LY][A15] | "Modified Binary Search" in AlgoMaster |
| Search on Matrix (4) | [LY] | |
| Missing and Repeating Number (5) | [LY] | |
| Binary Search on Semi-Sorted Space (9) | [LY] | rotated arrays |
| Binary Search On Answer (26) | [LY] | ★ blind-spot until owned |
| Minmax Problems (6) | [LY] | |
| Finding the K-th Element (7) | [LY] | |

## Matrix

| Pattern | Sources | Notes |
|---|---|---|
| Matrix / Implementary | [LY][A15] | "Matrix Traversal" in AlgoMaster |

## Trees

| Pattern | Sources | Notes |
|---|---|---|
| Binary Tree / Implementary | [LY] | |
| Binary Search Tree / Implementary | [LY] | inorder → sorted-array tricks |
| Binary Tree Traversal | [A15] | merged — pre/in/post/level order |
| Tree construction (Divide & Conquer) | [LY] | from preorder+inorder, etc. (NOT tree-DP) |

## Graphs

| Pattern | Sources | Notes |
|---|---|---|
| Graph Representation (29) | [LY] | |
| DFS | [LY][A15] | |
| BFS | [LY][A15] | LearnYard: Multi Source BFS (7) |
| Cycle Detection (9) | [LY] | |
| Topological Sort (17) | [LY] | |
| Flood Fill (7) | [LY] | |
| Dijkstra (17) | [LY] | |
| Bellman Ford (3) | [LY] | |
| Floyd Warshall (8) | [LY] | |
| Travelling Salesman (1) | [LY] | |
| Disjoint Set Union / Union-Find (13) | [LY] | ★ blind-spot pattern |
| Minimum Spanning Tree (8) | [LY] | |
| Additional Graph Algorithm (3) | [LY] | |

## Recursion & Backtracking

| Pattern | Sources | Notes |
|---|---|---|
| Recursion Problems (20) | [LY] | |
| Permutation Problems (3) | [LY][A15] | |
| Combination Problems (11) | [LY][A15] | |
| Subsets Problems (4) | [LY][A15] | subset enumeration |
| Path on Grid Problems (2) | [LY] | |

## Greedy

| Pattern | Sources | Notes |
|---|---|---|
| Part I (40) | [LY] | union-only — not an AlgoMaster pattern but a huge real bucket |
| Part II (18) | [LY] | |

## Bit Manipulation

| Pattern | Sources | Notes |
|---|---|---|
| Basic Bit Concepts (18) | [LY] | union-only |
| Bitwise XOR (17) | [LY] | |
| Bitwise OR (5) | [LY] | |
| Bitwise AND (7) | [LY] | |

## Game Theory

| Pattern | Sources | Notes |
|---|---|---|
| Level I (9) | [LY] | union-only |
| Level II (13) | [LY] | |
| Level III (3) | [LY] | |

## Combinatorics & Geometry

| Pattern | Sources | Notes |
|---|---|---|
| Combinatorics (15) | [LY] | |
| Line (7) | [LY] | |
| Rectangle (8) | [LY] | |
| Circle (6) | [LY] | |

## Tries

| Pattern | Sources | Notes |
|---|---|---|
| Introductory Questions (4) | [LY] | ★ blind-spot pattern |
| Trie involving String (16) | [LY] | |
| Trie with Bit Manipulation (5) | [LY] | |
| Trie involving Recursion (5) | [LY] | |
| Trie involving File System (2) | [LY] | |

## String Matching

| Pattern | Sources | Notes |
|---|---|---|
| Pattern Matching | [LY] | KMP / Z / Rabin-Karp |

## Advanced

| Pattern | Sources | Notes |
|---|---|---|
| Segment Tree / BIT | [LY] | |

---

## ✦ Invariant / Reframe (NON-STANDARD bucket)

> **Tag:** `Invariant/Reframe`. Added 2026-06-01. This is **not a mechanism bucket** like all the
> others above — it is a **cross-cutting skill axis** that sits *across* the pattern list, the way
> difficulty does. A problem here is usually *also* filed under a real bucket (Stack, Math, Greedy,
> Game Theory…); this tag is added **alongside** that bucket, never instead of it.

| Pattern | Sources | Notes |
|---|---|---|
| Invariant / Reframe (insight-gated brain-teasers) | — (own axis) | the trick IS the problem; simulation is the trap |

**What it is:** problems where the win is *refusing to simulate the process* and instead finding a
quantity that is invariant / additive / conserved, then counting it directly. The move —
**"don't simulate, find the invariant"** — is the transferable skill; the specific observation in
any one problem is disposable.

**Why NON-STANDARD (read before treating it like a normal bucket):**
- **No shared mechanism.** Owning 3 invariant problems does NOT make the 4th easier the way 3
  monotonic-stack problems do — each reframe is a fresh insight. So the "2 clean self-derived ACs = owned" gate
  does **not** apply and this bucket **never blocks band graduation** (rule 6).
- **It's a deck, not a count.** Grow & review: every insight-gated problem gets logged with *the trap*
  and *the reframe* in ≤2 lines. Reviewed for the move, not graduated.
- **Cross-cutting.** Always tagged in addition to the problem's real mechanism bucket.
- **Why it earns a bucket anyway (not a side-folder):** so band revision auto-sweeps it. A separate
  deck file would get orphaned; a bucket row in each `00-Band-Topic-Map.md` surfaces every revision pass.
- This is the **derivation muscle** the whole 1700 plan targets (the diagnosed gap is derivation, not
  pattern recognition) — so it is deliberately the one bucket we track *because it's hard*, not because
  it's a reusable tool.

Seed members: count-collisions-on-a-road (1550–1600 #30).

---

## Dynamic Programming (merged LearnYard L1/L2 + AlgoMaster 20)

LearnYard splits DP into Level 1 / Level 2; AlgoMaster names 20 recurrence shapes. Merged:

| DP pattern | Sources | LearnYard home |
|---|---|---|
| Linear DP (15) | [LY] | DP L1 |
| Fibonacci sequence | [A20] | → Linear DP |
| Count Distinct Ways | [A20] | → Linear DP (counting) |
| Kadane's Algorithm (7) | [LY][A20] | DP L1 / Kadane Algo |
| 2-Dimensional DP (29) | [LY] | DP L1 |
| DP on Grid (16) | [LY][A20] | DP L1 / "DP on Grids" |
| Knapsack DP (20) — 0/1 | [LY][A20] | DP L1 |
| Unbounded Knapsack | [A20] | → Knapsack DP |
| Subset Sum | [A20] | → Knapsack DP |
| Longest Increasing Subsequence (15) | [LY][A20] | DP L1 / LIS |
| Longest Common Subsequence (14) | [LY][A20] | DP L1 / LCS |
| DP on String (17) | [LY] | DP L1 |
| Palindromic Subsequence | [A20] | → DP on String / 2D DP |
| Edit Distance | [A20] | → DP on String / 2D DP |
| String Partition | [A20] | → DP on String |
| Cumulative Sum (15) | [LY] | DP L1 |
| Matrix Chain Multiplication (18) | [LY][A20] | DP L1 / Interval DP |
| Catalan Numbers | [A20] | → DP with Math / Combinatorics |
| DP with Bitmask (16) | [LY][A20] | DP L2 / "Bitmasking DP" |
| Digit DP (8) | [LY][A20] | DP L2 |
| DP on Trees (19) | [LY][A20] | DP L2 — ★ blind-spot pattern |
| DP with Math (13) | [LY] | DP L2 |
| DP with Probability (8) | [LY][A20] | DP L2 / "Probability DP" |
| DP on Graphs | [A20] | union-only — state DP over graph |
| State Machine DP | [A20] | union-only — buy/sell-stock family |

---

## Source-coverage summary

- **AlgoMaster-only (union, not in LearnYard):** Fast & Slow Pointers, LinkedList In-place Reversal, Overlapping Intervals, State Machine DP, DP on Graphs, Catalan Numbers (as a named pattern).
- **LearnYard-only (union, not an AlgoMaster pattern):** Greedy, Hashing, Sorting, Bit Manipulation, Game Theory, Combinatorics & Geometry, String Matching, Tries, Segment Tree/BIT, and most of the Graph/Binary-Search sub-algorithms (Dijkstra, Bellman-Ford, MST, TSP, etc.).
- **Blind-spot patterns (rule 6B — each needs 2 clean self-derived ACs):** Monotonic Stack, DP on Trees, Disjoint Set Union. Also watch: Binary Search On Answer, Tries.
- **Substrate (not derivation buckets):** Hashing/Implementary, Sorting/Implementary, Simulation, plain Array iteration — appear as LearnYard buckets but don't count as ownership targets.
- **Non-standard cross-cutting axis:** `Invariant/Reframe` — tracked as a bucket (so revision sweeps it) but with no clean-rep gate and never blocks graduation. Tagged alongside a problem's real mechanism bucket.
