# Phase 1 — Acquisition (1950-2000)

**Group A is EMPTY at this band.** Same shape as 1900-1949: every foundational pattern is acquired at a lower band, and every advanced/outlier pattern still fails the ≥3 rule here.

Generated 2026-05-28.

**Sources used:**
- LC tags + AR + difficulty: live-fetched from LC GraphQL → `zerotrac-data/band_1950_1999_lctags.tsv` (66 problems, all 1950-1999).
- Topic-install ledger: see `LC/topic-install-ledger.md` for the running state.

---

## Candidate sweep — deferred / outlier / new candidates

| Topic | Class | 1950-1999 reps | Verdict |
|-------|-------|---------------:|---------|
| Segment Tree | advanced (outlier) | 0 | stays outlier — 0 viable across 1500-1999 (9 bands) |
| Binary Indexed Tree (BIT) | advanced (outlier) | 1 | stays outlier — 1+1 across 1500-1999 |
| Shortest Path / Dijkstra | **installed @ 1850-1899** | 1 | n/a (installed; this is a Phase 2 derivation rep) |
| Bitmask DP | **installed @ 1850-1899** | 2 | n/a (installed; Phase 2 derivation reps) |
| Minimum Spanning Tree | advanced (outlier) | 0 | stays outlier |
| Monotonic Queue | advanced (outlier) | 1 | stays outlier — 7 split across 1500-1999, never ≥3 |
| Quickselect | advanced (outlier) | 0 | stays outlier — 2 across 8 bands |
| Rolling Hash | advanced (outlier) | 0 | stays outlier — 6 split across 5 bands |
| Digit DP | new candidate | 0 | n/a — absent |
| String Matching / KMP / Z-algo | new candidate | 0 | n/a — absent |
| Suffix Array / Suffix Tree | new candidate | 0 | n/a — absent |
| Bipartite matching | new candidate | 0 | n/a — absent |
| Strongly Connected Components / Tarjan | new candidate | 0 | n/a — absent |
| Eulerian path/circuit | new candidate | 0 | n/a — absent |
| Geometry | permanent SKIP | 1 | stays skipped |

**No genuinely new pattern surfaces at 1950-1999.** Band-tag profile is DP-heavy (24) + Hashing (20) + Math (14) + Greedy (14) — all foundational and acquired at 1500-1549.

---

## Group A — empty

No acquisitions at this band.

---

## Group B — Already acquired in a lower band → Phase 2 only at 1950-1999

Every 1950-1999 problem in these buckets is a **disguised/combined derivation rep** for Phase 2 ownership.

See `LC/topic-install-ledger.md` for the full installed-list (foundational + advanced sections). Highlights for problems likely to appear in this band:
- Topological Sort: 3 reps here — strong Phase 2 derivation supply (installed @ 1750-1799)
- Union-Find: 3 reps here (installed @ 1600-1649)
- Monotonic Stack: 1 rep (installed @ 1500-1549; this counts toward cross-band ownership for that blind-spot bucket)
- Backtracking: 3 reps
- DP / Hashing / Math: dominant supply

---

## Already solved in this band

No prior `LC/1950-2000.md` exists — band untouched under any protocol. No exclusions.

---

## What comes next

There's no Group A to work through. Generate `1950-2000/_Sealed-Queue-Phase2.md` from the 66 unsolved problems — disguised reps per Group B bucket, shuffled blind. The DP-heavy supply here is good for the 3 cold cleans on linear/grid DP, the Topo Sort reps continue the 1750-99 install's ownership, and the dense Union-Find supply (3 reps) reinforces 1600-1649's install.
