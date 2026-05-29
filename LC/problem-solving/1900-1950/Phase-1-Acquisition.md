# Phase 1 — Acquisition (1900-1950)

**Group A is EMPTY at this band.** By 1900-1949 every foundational pattern is acquired at a lower band, and every advanced/outlier pattern still fails the ≥3 rule here.

Generated 2026-05-28.

**Sources used:**
- LC tags + AR + difficulty: live-fetched from LC GraphQL → `zerotrac-data/band_1900_1949_lctags.tsv` (68 problems, all 1900-1949).
- Topic-install ledger: see `LC/topic-install-ledger.md` for the running state.

---

## Candidate sweep — every deferred / outlier / new candidate

| Topic | Class | 1900-1949 reps | Verdict |
|-------|-------|--------------:|---------|
| Segment Tree | advanced (outlier) | 0 | stays outlier — 0 viable across 1500-1949 (8 bands) |
| Binary Indexed Tree (BIT) | advanced (outlier) | 1 | stays outlier |
| Shortest Path / Dijkstra | advanced, **already installed @ 1850-1899** | 0 | n/a (installed) |
| Bitmask DP | advanced, **already installed @ 1850-1899** | 1 | n/a (installed; this is a Phase 2 derivation rep) |
| Minimum Spanning Tree | advanced (outlier) | 0 | stays outlier |
| Monotonic Queue | advanced (outlier) | 2 | stays outlier — never ≥3 in 1500-1949 |
| Quickselect | advanced (outlier) | 0 | stays outlier |
| Rolling Hash | advanced (outlier) | 1 | stays outlier — never ≥3 in 1500-1949 |
| Digit DP | new candidate | 0 | n/a — absent |
| String Matching / KMP / Z-algo | new candidate | 0 | n/a — absent |
| Suffix Array / Suffix Tree | new candidate | 0 | n/a — absent |
| Geometry | permanent SKIP | 0 | stays skipped |

**No genuinely new pattern surfaces at 1900-1949.** Band-tag profile is binary-search-heavy (18 reps) + DP (17) + hashing (14) + greedy (14) — all foundational and acquired at 1500-1549.

---

## Group A — empty

No acquisitions at this band.

---

## Group B — Already acquired in a lower band → Phase 2 only at 1900-1949

Every 1900-1949 problem in these buckets is a **disguised/combined derivation rep** for Phase 2 ownership. Full installed-list:

Foundational (acquired at first appearance, regardless of supply):
- Monotonic stack, tree DP, backtracking, trie, greedy, linear/grid DP, graph BFS/DFS (unweighted), two-pointer, plain binary search · all at **1500-1549**
- Sliding window, hashing/counting, heap/top-k, math/NT/bit, BS-on-answer, prefix/sort-scan · all in-band at **1500-1549**
- Game theory, interval DP · at **1550-1599** (clean ✓ ✓)
- Union-Find · at **1600-1649**
- Difference array / 2D · derivation **1550-1599**

Advanced (acquired only when ≥3 in-band supply exists):
- Topological Sort · at **1750-1799**
- Dijkstra / Shortest Path · at **1850-1899**
- Bitmask DP · at **1850-1899**

(See `LC/topic-install-ledger.md` for the full ledger.)

---

## Already solved in this band

`LC/1900-1950.md` does not exist yet — this band is untouched under any protocol. No exclusions.

---

## What comes next

There's no Group A to work through. Generate `1900-1950/_Sealed-Queue-Phase2.md` from the 68 unsolved problems — disguised reps per Group B bucket, shuffled blind. Phase 2 reps here continue to bump ownership counts for monotonic stack (4 reps), Topo Sort (whatever appears), Union-Find (2), etc.
