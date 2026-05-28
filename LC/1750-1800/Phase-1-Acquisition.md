# Phase 1 — Acquisition (1750-1800)

**Group A has ONE acquisition: Topological Sort.** Revised 2026-05-28 — the retroactive ≥3-rule audit moved Topological Sort here from 1650-1700 (which only had 2 reps); 1750-1799 has 3 reps and becomes the install band.

Generated 2026-05-28; revised same day.

**Sources used:**
- LC tags + AR + difficulty: live-fetched from LC GraphQL → `zerotrac-data/band_1750_1799_lctags.tsv` (94 problems, all 1750-1799).
- Already-solved exclusions: `LC/1750-1800.md` shows 0/10 — nothing to exclude.

---

## Group A — Acquire here

Topic-visible, study-OK. Must be clean first-submission AC to count. Pick is highest-AR Q3 non-Design rep for the bucket.

| # | Topic | Why new here | Problem | AR | QPos | LC tags (verified) | Link |
|---|-------|--------------|---------|-----|------|--------------------|------|
| 1 | **Topological Sort** (FIRST install per ≥3 rule) | absent at 1500-1649; 1650-1699 had only 2 reps (failed ≥3); 1750-1799 has 3 — install band | Loud and Rich | 63.5% | Q3 | Array, **Graph Theory, Topological Sort**, Depth-First Search | https://leetcode.com/problems/loud-and-rich/ |

> [!note] All three Topo Sort reps in this band
> Loud and Rich [1783, Q3, 63.5%] · All Ancestors of a Node in a DAG [1788, Q3, 62.2%] · Tree Diameter [1792, Q3, 61.3%]. The other two become Phase 2 derivation reps for ownership.

---

## Candidate sweep — every other potentially-new pattern at 1750-1799

The deferred topics from 1700-1749 + new candidates that surfaced at this band.

| Topic | In-band reps | Cumulative | Verdict |
|-------|-------------:|-----------:|---------|
| **Segment Tree / BIT** | 0 | 0 viable across 7 bands | trending **outlier — skip-class** |
| **Dijkstra / Shortest Path** | 2 (Min Time Visit Disappearing Nodes Q3 37.8%; Cheapest Flights K Stops Q3 41.8%) | 3 split across 1700-49 + 1750-99 | **DEFER** → install at 1850-1899 (4 reps) |
| **Bitmask DP** | 1 (Min Time to Break Locks I Q2 32.6%) | 2 split | **DEFER** → install at 1850-1899 (4 reps) |
| **Monotonic Queue** | 2 | 4 split across 3 bands | **outlier — skip-class** (never ≥3 single band) |
| **Quickselect** | 0 | 2 across 6 bands | **outlier — skip-class** |
| **Rolling Hash** | 0 | 3 split across 4 bands | **outlier — skip-class** (never ≥3 single band) |
| **MST** (new candidate) | 1 (Connecting Cities With Min Cost Q3 63.5%, also Union-Find tagged) | 1 | **DEFER** → adjacent to Union-Find; revisit at 1800+ |
| **Geometry** | 1 (Minimum Area Rectangle Q3 55.4%) | n/a | stays SKIPPED (set 2026-05-28) |

---

## Group B — Already acquired in a lower band → Phase 2 only at 1750-1799

Every 1750-1799 problem in these buckets is a **disguised/combined derivation rep** for Phase 2 ownership at this band.

| Topic | Acquired at | Acquisition problem |
|-------|-------------|---------------------|
| Greedy / observation | 1500-1550 Phase 1 | Construct K Palindrome Strings |
| Linear / grid / counting DP | 1500-1550 Phase 1 | Count Sorted Vowel Strings |
| Graph BFS/DFS (unweighted) | 1500-1550 Phase 1 | Find All Groups of Farmland |
| Two-pointer / interval merge | 1500-1550 Phase 1 | Boats to Save People |
| Plain binary search (lower_bound) | 1500-1550 Phase 1 | Maximum Distance Between a Pair of Values |
| Monotonic stack (blind-spot) | 1500-1550 Phase 1 | Sum of Subarray Ranges |
| Tree DP / DFS (blind-spot) | 1500-1550 Phase 1 | Smallest Subtree with all the Deepest Nodes |
| Backtracking | 1500-1550 Phase 1 | Maximum Split of Positive Even Integers |
| Trie | 1500-1550 Phase 1 | Remove Sub-Folders from the Filesystem |
| Sliding window | 1500-1550 in-band | Min Subarray Length Distinct Sum ≥ K (#1) |
| Hashing / counting | 1500-1550 in-band | Count Special Triplets (#2), Rearrange K Substrings (#3) |
| Heap / top-k / heap-greedy | 1500-1550 in-band | Max Product of Three After Replacement (#5) |
| Math / number theory / bit | 1500-1550 in-band | Find Good Integers (#7), Largest Prime Consecutive Sum (#9) |
| Binary search on answer | 1500-1550 in-band | Minimum K to Reduce Array Within Limit (#8) |
| Prefix / sort-scan | 1500-1550 in-band | Count Special Triplets (#2) prefix; Special Array II (#6) |
| Game theory | 1550-1600 Phase 1 | Alice and Bob Playing Flower Game |
| Interval DP | 1550-1600 Phase 1 | Stone Game |
| Difference array / prefix-range | 1550-1600 derivation | Zero Array Transformation I (band #8), Increment Submatrices 2D (#18) |
| Union-Find / DSU (blind-spot) | 1600-1650 Phase 1 | Number of Operations to Make Network Connected |

> [!important] What this means for ownership at 1750-1799
> Group B topics earn their 3 cold cleans here entirely through Phase 2 — each disguised 1750-1799 problem counts toward that bucket's ownership tally.

> [!warning] Removed-from-Group-B by 2026-05-28 audit
> Topological Sort, Monotonic Queue, Quickselect, and Rolling Hash were previously listed as "installed at 1650-1700" in older Group B sections. The ≥3-rule audit moved Topo Sort here (now Group A above); the other three are outliers and don't appear as Group B installs anywhere through 1850-1899.

---

## Already solved in this band

`LC/1750-1800.md` shows 0/10 solved — no exclusions from Phase 2 selection.

---

## Tracker (Group A — deal blind, one bare link per "next")

| # | Topic | Phase 1 | Status |
|---|-------|---------|--------|
| 1 | Topological Sort | ☐ | — |

---

## Deferred / skipped acquisitions — rolling forward

| Topic | Status | Where it lands |
|-------|--------|----------------|
| Segment Tree / BIT | trending outlier | 0 viable in 7 bands; skip-class |
| Dijkstra / Shortest Path (weighted) | DEFER → 1850-1899 | install there (4 reps) |
| Bitmask DP | DEFER → 1850-1899 | install there (4 reps) |
| Monotonic Queue | outlier — skip-class | never ≥3 in 1500-1899 |
| Quickselect | outlier — skip-class | 2 reps in 6 bands |
| Rolling Hash | outlier — skip-class | never ≥3 in 1500-1899 |
| MST | trending outlier | adjacent to Union-Find |
| Geometry | SKIP entirely | not a target bucket |

---

## What comes next

After the single Group A acquisition (Topological Sort) clean here, generate `1750-1800/_Sealed-Queue-Phase2.md` from the ~93 unsolved problems — disguised reps per Group B bucket, shuffled blind.
