# Topic Install Ledger

Single source of truth for **which pattern is installed at which band** across the 1500-1899+ acquisition ladder. Updated whenever a new band's Phase 1 is generated.

Last updated: 2026-05-28 (after retroactive ≥3 audit + foundational-vs-advanced split + 1900-1949 generation).

> [!important] Granularity upgrade (2026-05-28)
> Install decisions are now made at **LearnYard subgroup granularity** (119 subgroups across 27 main topics), not broad LC-tag granularity. The canonical taxonomy is `learnyard-data/subgroups.tsv`. Per-band supply is computed by `scripts/classify_band_to_learnyard.py` using three stacked signals: doocs editorial algorithmic tags + doocs approach names + LC official tags. This caught two coarse-granularity errors at 1500-1549 (see "Subtopic corrections" below).

**Two pattern classes (rule formalized 2026-05-28):**
- **Foundational** — install at the FIRST band where the pattern appears, regardless of supply. The ≥3 rule does NOT apply. Examples: monotonic stack, tree DP, backtracking, plain binary search. Rationale: these are core CS patterns the user must own for 1700-rating contests; deferring them indefinitely on thin supply would leave permanent blind spots.
- **Advanced** — install ONLY at the first band with ≥3 viable (non-Design) in-band reps. If no band 1500-1899 has ≥3, the pattern is classified **outlier** and treated like Design (excluded as a target bucket). Examples: Segment Tree, Dijkstra, Bitmask DP.

See `LC/CLAUDE.md` Step 4 for the canonical rule.

---

## Foundational installs (regardless of supply)

| Pattern | Install band | Acquisition problem | Status |
|---------|--------------|---------------------|--------|
| Monotonic stack (blind-spot) | 1500-1549 | Sum of Subarray Ranges | ☐ planned · 1 cross-band clean at 1550-1600 #22 (Next Greater Node) |
| Tree DP / DFS (blind-spot) | 1500-1549 | Smallest Subtree with all the Deepest Nodes | ☐ planned |
| Backtracking | 1500-1549 | Maximum Split of Positive Even Integers | ☐ planned |
| Trie | 1500-1549 | Remove Sub-Folders from the Filesystem | ☐ planned |
| Greedy / observation | 1500-1549 | Construct K Palindrome Strings | ☐ planned |
| Linear / grid / counting DP | 1500-1549 | Count Sorted Vowel Strings | ☐ planned |
| Graph BFS/DFS (unweighted) | 1500-1549 | Find All Groups of Farmland | ☐ planned |
| Two-pointer / interval merge | 1500-1549 | Boats to Save People | ☐ planned |
| Plain binary search (lower_bound) | 1500-1549 | Maximum Distance Between a Pair of Values | ☐ planned |
| Sliding window | 1500-1549 in-band | Min Subarray Length Distinct Sum ≥ K (#1) | ✓ clean |
| Hashing / counting | 1500-1549 in-band | Count Special Triplets (#2), Rearrange K Substrings (#3) | ✓ clean |
| Heap / top-k / heap-greedy | 1500-1549 in-band | Max Product of Three After Replacement (#5) | ✓ clean |
| Math / number theory / bit | 1500-1549 in-band | Find Good Integers (#7), Largest Prime Consecutive Sum (#9) | ✓ clean (vanilla) |
| Binary search on answer | 1500-1549 in-band | Minimum K to Reduce Array Within Limit (#8) | ✓ clean |
| Prefix / sort-scan | 1500-1549 in-band | Count Special Triplets (#2), Special Array II (#6) | ✓ clean |
| Game theory | 1550-1599 | Alice and Bob Playing Flower Game | ✓ clean (47 min) |
| Interval DP (Matrix Chain) | 1550-1599 | Stone Game | ✓ clean (self-derived) |
| DP On Grid | 1550-1599 | Minimum Falling Path Sum | ☐ planned (subtopic re-audit 2026-05-28) |
| DP on String | 1550-1599 | Longest String Chain | ☐ planned (subtopic re-audit 2026-05-28) |
| Difference array / prefix-range | 1550-1599 derivation | Zero Array Transformation I (#8), Increment Submatrices 2D (#18) | ✓ via Phase 2 |
| Union-Find / DSU (blind-spot) | 1600-1649 | Number of Operations to Make Network Connected | ☐ planned · 7 in-band reps (subtopic re-audit 2026-05-28) |
| Multi Source BFS | 1600-1649 | Push Dominoes | ☐ planned (new foundational graph subtopic) |
| Recursion & Backtracking | 1600-1649 (LearnYard-sourced) | Subsets (LC 78) | ☐ planned · contest pool lacks pure backtracking → sourced from LearnYard |

## Advanced installs (only when ≥3 supply hits)

| Pattern | Install band | Acquisition problem | Cumulative supply by install band | Status |
|---------|--------------|---------------------|----------------------------------:|--------|
| Topological Sort | 1750-1799 | Loud and Rich | 1650-99: 2, 1700-49: 1, 1750-99: **3 (install)** | ☐ planned |
| Dijkstra / Shortest Path (weighted) | 1850-1899 | Find the City With the Smallest Number of Neighbors at a Threshold Distance | 1600-49: 1, 1700-49: 1, 1750-99: 2, 1800-49: 2 viable, 1850-99: **4 (install)** | ☐ planned |
| Bitmask DP | 1850-1899 | Fair Distribution of Cookies | 1700-49: 1, 1750-99: 1, 1800-49: 0, 1850-99: **4 (install)** | ☐ planned |

## Outliers / skip-class (never installed — treated like Design)

| Pattern | Reason | Total reps across 1500-1899 |
|---------|--------|----------------------------:|
| Design | CLAUDE.md rule (always) | n/a |
| Geometry | thin everywhere (2-3/band across 1700-2049) | ~8 across 6 bands, never densifies |
| Segment Tree / BIT | 0 viable Segment Tree across 9 bands; 1 BIT at 1900-49, 1 at 1950-99 — never ≥3 either | 2 viable in 9 bands |
| Monotonic deque / queue | never ≥3 in any single band | 1+1+2+0+0+2+1 = 7 split across 5 bands |
| Quickselect | 2 reps in 1650-99, 0 elsewhere | 2 across 8 bands |
| Rolling Hash | never ≥3 in any single band | 1+1+0+1+2+1+0 = 6 split across 5 bands |
| Minimum Spanning Tree | 2 reps in 7 bands, adjacent to Union-Find anyway | 2 across 7 bands |

When a problem with an outlier-class tag appears in Phase 2, it flows under its **substitute installed bucket** (e.g., Quickselect → Heap/top-k; Rolling Hash → Trie or Hashing+String; Mono Queue → Heap-greedy; MST → Union-Find).

---

## Per-band Phase 1 summary

| Band | Group A count | Topics |
|------|--------------:|--------|
| 1500-1549 | 9 + 6 in-band | mono stack, tree DP, backtracking, trie, greedy, linear/grid DP, graph BFS/DFS, two-pointer, plain BS + sliding window, hashing, heap, math/bit, BS-on-answer, prefix/sort-scan |
| 1550-1599 | 4 | game theory ✓, interval DP ✓ (both installed-via-solve) + DP-on-Grid, DP-on-String (new subtopics, subtopic re-audit) |
| 1600-1649 | 3 | Union-Find (7 reps, blind-spot) + Multi-Source BFS (new) + Backtracking (LearnYard-sourced — resolves 3-band phantom) |
| 1650-1699 | 0 | (4 prior picks dropped by 2026-05-28 audit: Topo Sort moved to 1750-99; Mono Queue / Quickselect / Rolling Hash → outliers) |
| 1700-1749 | 0 | (Segment Tree / Dijkstra / Bitmask DP / MST all thin; Geometry skipped) |
| 1750-1799 | 1 | Topological Sort |
| 1800-1849 | 0 | (Dijkstra 2 viable still <3; deferred to 1850-99) |
| 1850-1899 | 2 | Dijkstra, Bitmask DP |
| 1900-1949 | 0 | (no new patterns; all advanced still <3) |
| 1950-1999 | 0 | (no new patterns; advanced topics still <3; Segment Tree still 0 viable through 9 bands) |

---

## Subtopic corrections (2026-05-28 LearnYard re-audit, 1500-1549)

The broad-tag ledger had two errors, found when re-auditing 1500-1549 at LearnYard subgroup granularity with doocs editorial data:

1. **"Tree DP" was a phantom install.** The 1500-1549 pick (Smallest Subtree with all the Deepest Nodes) is **Binary Tree / Implementary** (traversal), not **DP on Trees** (LearnYard DP L2). doocs editorial confirms no DP. **DP on Trees has 0 reps at 1500-1549** — the blind-spot "tree DP" was never actually going to install here. It must install at the first band with ≥3 DP-on-Trees reps. The foundational "Binary Tree traversal" mechanic IS installed at 1500-1549.

2. **Bit Manipulation / Bitwise XOR is a distinct bucket from Math/NT.** 10 in-band XOR reps were being folded into "math/bit". LearnYard treats Bit Manipulation as its own top-level topic (4 subgroups). Now a separate Group A acquisition at 1500-1549.

3. **Backtracking is a phantom at 1500-1549 (found by editorial-correctness verification).** Both backtracking-tagged problems (Maximum Split of Positive Even Integers, Maximum Strength of a Group) have **Greedy / Binary-Enumeration** editorial solutions — confirmed across doocs tags, LC tags, AND editorial body. Zero genuine backtracking in the band. Removed from Group A; defers to the first band whose editorial solution is actually backtracking (permutations/combinations/subsets with pruning). **Same phantom class as DP-on-Trees: an LC "Backtracking" tag does not mean the intended solution is backtracking.**

> [!warning] Verification rule learned (2026-05-28)
> A topic only counts as installable at a band if the **editorial's actual solution** uses that pattern — not merely if the LC/doocs *tag* lists it. Tags are necessary, not sufficient. Both phantom installs (Tree DP, Backtracking) passed the tag check but failed the editorial check. **Always verify Group A picks against the doocs editorial approach before locking them.**

**Excluded as scaffolding (not derivation targets, like Design):** Sorting/Implementary, Matrix/Implementary, String Matching (the 1500-1549 "matches" were all incidental — actually Trie/two-pointer).

**Open item for future bands:** when processing 1550-1999, re-audit each at LearnYard subgroup granularity (not broad LC tags). Specifically hunt for the real **DP on Trees** install band. The coarse-tag Phase 1 files for 1550-1999 still need this same subtopic re-audit when each becomes active.

## LearnYard canonical taxonomy reference

27 main topics / 119 subgroups. Full list: `learnyard-data/subgroups.tsv`. Derivation-target main topics (excludes pure scaffolding like Sorting, Matrix, DSA Fundamentals, Programming Fundamentals):

- **Tries** (5): Introductory · Trie w/ Bit · Trie w/ String · Trie w/ Recursion · Trie w/ File System
- **DP Level 1** (10): Linear · 2D · Grid · Knapsack · LIS · LCS · DP-on-String · Cumulative Sum · Matrix Chain (Interval) · Kadane
- **DP Level 2** (5): Bitmask · Digit DP · **DP on Trees** · DP w/ Math · DP w/ Probability
- **Recursion & Backtracking** (5): Recursion · Permutation · Combination · Subsets · Path-on-Grid
- **Game Theory** (3): Level I / II / III
- **Graphs** (12): Representation · Cycle Detection · Topo Sort · Flood Fill · Multi-Source BFS · Dijkstra · Bellman Ford · Floyd Warshall · TSP · DSU · MST · Additional
- **Binary Search** (8): Introductory · Upper/Lower Bound · Search-on-Matrix · Missing/Repeating · Semi-Sorted · BS-on-Answer · Minmax · Kth Element
- **Greedy** (2): Part I / II
- **Bit Manipulation** (4): Basic · XOR · OR · AND
- **Heap (PQ)** (6 subgroups)
- **Stack** (4): incl Monotonic Stack
- **Queue** (3): incl Monotonic Queue
- **Binary Tree** (7), **Binary Search Tree** (3)
- **Sliding Window** (2): Fixed / Dynamic
- **2 Pointers** (2): Arrays / Strings
- **String Matching Algos** (2), **Combinatorics & Geometry** (4), **Advance algorithm** (3: Segment Tree / Fenwick)

## Audit history

- **2026-05-28** — Built initial ledger after generating Phase 1 for 1700-1949.
- **2026-05-28** — Adopted ≥3-in-band-reps rule after noticing the 1700-1749 over-acquisition (4 picks on thin supply).
- **2026-05-28** — Retroactive ≥3 audit: dropped Dijkstra from 1600-1649 (1 rep), and Topo Sort / Mono Queue / Quickselect / Rolling Hash from 1650-1699 (all <3).
- **2026-05-28** — Foundational-vs-advanced split formalized: 1500-1549 and 1550-1599 picks confirmed all foundational (no audit changes); ≥3 rule applies only to advanced topics.
- **2026-05-28** — 1900-1949 generated: no new installs; advanced topics confirmed still thin.
- **2026-05-28** — 1950-1999 generated: same shape; no new installs; outlier classifications hold. Segment Tree confirmed 0 viable across 9 bands.
- **2026-05-28** — LearnYard data fully extracted (1431 problems, 119 subgroups → `learnyard-data/`). doocs editorials fetched for 1500-1549 (112/112 → `editorials-data/`). Fetch scripts persisted to `scripts/`. 1500-1549 re-audited at subgroup granularity: relabeled Tree DP→Binary Tree traversal, added Bit/XOR bucket, dropped Sorting/Matrix/String-Matching as scaffolding. Phase 1 + band topic map + this ledger updated.
- **2026-05-28** — 1550-1599 re-audited at subgroup granularity. Editorials fetched (83/83). Game Theory + Interval DP confirmed installed-via-solve. **New subtopic acquisitions found: DP-on-Grid (Minimum Falling Path Sum) + DP-on-String (Longest String Chain)** — both genuinely new vs the 1500 floor, editorial-verified. Rejected: Score of Parentheses (editorial = counting, not stack), Iterator for Combination (Design), DP-on-Trees (absent again). **Exclusion bug found + fixed:** First-Attempt filenames don't always match LC slugs; classifier now needs filename↔slug aliases per band.
- **2026-05-28** — 1600-1649 re-audited at subgroup granularity. Editorials fetched (87/87), 8 solved excluded (no aliases needed). **Union-Find installed** (Network Connected, 7 in-band reps — the deferred blind-spot). **Multi-Source BFS** new foundational graph subtopic (Push Dominoes). **Backtracking resolved as a 3-band contest-pool phantom → sourced from LearnYard** (Subsets): rated contests systematically lack pure backtracking; LearnYard's curated R&B list (Subsets/Permutations/Combination Sum/N-Queens, mostly unrated) is the correct source. DP-on-Trees absent for the 3rd band — still homeless. Dijkstra (1 rep, editorial=BFS) deferred to 1850. **1650-1999 still need the same subgroup re-audit when active.**

---

## When to update

Update this ledger every time a new band's Phase 1 is generated, or when a re-audit changes an install/outlier classification. The "Per-band Phase 1 summary" table at the bottom is the quick-reference; the install/outlier tables above are the source-of-truth.
