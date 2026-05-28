# Phase 1 — Acquisition (1800-1850)

**Group A is EMPTY at this band.** Same outcome as 1700-1799: every potentially-new pattern still has <3 viable in-band reps. Whole band collapses to Phase 2 derivation reps.

Generated 2026-05-28.

**Sources used:**
- LC tags + AR + difficulty: live-fetched from LC GraphQL → `zerotrac-data/band_1800_1849_lctags.tsv` (80 problems, all 1800-1849).
- Already-solved exclusions: `LC/1800-1850.md` exists with 5 logged solves under the old protocol; these don't intersect the deferred-topic candidates.

---

## Candidate sweep — every potentially-new pattern at 1800-1849

The four deferred topics from earlier bands get checked first.

| Topic | In-band reps | Viable (non-Design) | Cumulative 1500-1849 | Verdict |
|-------|-------------:|--------------------:|---------------------:|---------|
| **Segment Tree / BIT** | 0 | 0 | 0 viable across 7 bands | trending **outlier** — likely skip-class |
| **Dijkstra / Shortest Path** | 3 | **2** (1811 Design Graph is Q4 Design-tagged → excluded) | 1700-49: 1, 1750-99: 2, 1800-49: 2 viable = 5 split | **DEFER AGAIN** → 1850-1899 has 4 reps, install there |
| **Bitmask DP** | 0 | 0 | 1700-49: 1, 1750-99: 1, 1800-49: 0 = 2 split | **DEFER AGAIN** → 1850-1899 has 4, install there |
| **MST** | 0 | 0 | 1750-99: 1, 1800-49: 0 = 1 | trending **outlier** — adjacent to Union-Find anyway |
| **Geometry** | 0 | 0 | n/a | stays SKIPPED |

### Detail — Dijkstra reps at 1800-1849
- 1811 Design Graph With Shortest Path Calculator (Q4, 65.2%) — **Design-tagged → excluded**
- 1845 Minimum Time to Reach Destination in Directed Graph (Q3, 45.7%)
- 1846 Path with Maximum Probability (Q3, 65.5%)

Only 2 viable here; combined with 1850-1899's 4 fresh reps, the install lands at **1850-1899** (4 same-band reps satisfies the ≥3 threshold with healthy margin).

---

## Group A — empty

No acquisitions at this band.

---

## Group B — Already acquired in a lower band → Phase 2 only

Every 1800-1849 problem in these buckets is a **disguised/combined derivation rep** for Phase 2 ownership.

Cumulative installed buckets at this point (after 2026-05-28 ≥3-rule audit): greedy, hashing, sliding window, two-pointer, plain BS, BS-on-answer, prefix/sort-scan, diff array, math/NT/bit, heap-greedy, linear/grid DP, interval DP, graph BFS/DFS unweighted, tree DP, monotonic stack, union-find, **topological sort (installed at 1750-1799, not 1650-1700)**, backtracking, trie, game theory.

**Removed from installed list by 2026-05-28 audit:** monotonic deque/queue, quickselect, rolling hash — all outliers (never ≥3 in any band 1500-1899). Problems with these LC tags here flow as derivation reps under their installed-substitute buckets (heap-greedy / heap / hashing+string).

---

## Already solved in this band

`LC/1800-1850.md` shows 5 problems logged under the old protocol — these contribute to Phase 2 ownership counts when the rebuilt queue is generated, not to Phase 1 acquisition.

---

## Deferred / skipped acquisitions — rolling forward

| Topic | Status | Where it lands |
|-------|--------|----------------|
| Segment Tree / BIT | trending outlier | check 1900+; otherwise skip-class |
| **Dijkstra / Shortest Path** | DEFER → **1850-1899** | install there (4 reps, ≥3 threshold met) |
| **Bitmask DP** | DEFER → **1850-1899** | install there (4 reps) |
| MST | trending outlier | adjacent to Union-Find, likely skip |
| Geometry | SKIP entirely | not a target bucket |

---

## What comes next

There's no Group A to work through. Generate `1800-1850/_Sealed-Queue-Phase2.md` from the ~75 unsolved problems — disguised reps per Group B bucket, shuffled blind.
