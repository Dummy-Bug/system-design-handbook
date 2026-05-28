# Phase 1 — Acquisition (1850-1900)

**Group A has TWO acquisitions** — Dijkstra and Bitmask DP. Both have been deferred across 4 prior bands (1700-1849) waiting for ≥3 viable in-band reps. 1850-1899 finally delivers 4 each.

Generated 2026-05-28.

**Sources used:**
- LC tags + AR + difficulty: live-fetched from LC GraphQL → `zerotrac-data/band_1850_1899_lctags.tsv` (85 problems, all 1850-1899).
- Already-solved exclusions: `LC/1850-1900.md` exists with 5 problems logged under the old protocol; none of them are the Group A picks below (verified via slug match).

---

## Candidate sweep — six bands' worth of deferreds now decided

| Topic | Reps at 1850-1899 | Viable | Cumulative 1500-1899 | Verdict |
|-------|------------------:|-------:|---------------------:|---------|
| **Dijkstra / Shortest Path** | **4** | 4 | 11 across 4 bands | **ACQUIRE** — 1855 (Q3, 72.8%) easiest |
| **Bitmask DP** | **4** | 4 | 6 split across 3 bands | **ACQUIRE** — 1882 (Q4, 81.5%) easiest by AR; 1887 Fair Cookies (Q3, 69.9%) is the classic-textbook rep |
| **Segment Tree / BIT** | 0 | 0 | 0 viable across 7 bands | confirmed **outlier — skip-class** |
| **MST** | 1 (Min Cost Connect All Points, Q3, 71.0%) | 1 | 2 split across 2 bands | **outlier — skip-class** (adjacent to Union-Find anyway) |
| **Geometry** | (not surveyed here) | — | n/a | stays SKIPPED |

---

## Group A — Acquire here

Topic-visible, study-OK. Must be clean first-submission AC to count. Picks are easiest non-Design rep per bucket (highest AR / lowest Q-position).

| # | Topic | Why new here | Problem | AR | QPos | LC tags (verified) | Link |
|---|-------|--------------|---------|-----|------|--------------------|------|
| 1 | **Dijkstra / Shortest Path** (weighted, FIRST install) | absent at 1500-1700; thin at 1700-1849 | Find the City With the Smallest Number of Neighbors at a Threshold Distance | 72.8% | Q3 | Dynamic Programming, **Graph Theory, Shortest Path** | https://leetcode.com/problems/find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance/ |
| 2 | **Bitmask DP** (state-compression DP, FIRST install) | bitmask-as-state never installed; brute-force was the substitute below | Fair Distribution of Cookies | 69.9% | Q3 | Array, **Dynamic Programming, Bit Manipulation, Bitmask**, Backtracking | https://leetcode.com/problems/fair-distribution-of-cookies/ |

> [!note] Picks rationale
> **Dijkstra → Find the City...** is the cleanest acquisition: pure weighted-graph Dijkstra (or Floyd-Warshall is also valid given small V), 72.8% AR, no compound pattern baggage. The other 3 Dijkstra problems in the band (Edge Reversals, Last Room II, Convert String) are richer derivation reps for Phase 2.
> **Bitmask DP → Fair Distribution of Cookies** is the textbook bitmask-DP problem (assign k workers to subsets of cookies, mask = which cookies assigned). Higher-AR alternative (1882 Max Score Words, 81.5%) is more contrived and partly brute-forceable. Cookies forces the bitmask DP framing cleanly.

---

## Group B — Already acquired in a lower band → Phase 2 only

Every 1850-1899 problem in these buckets is a **disguised/combined derivation rep**.

Cumulative installed buckets (post 2026-05-28 audit): greedy, hashing, sliding window, two-pointer, plain BS, BS-on-answer, prefix/sort-scan, diff array, math/NT/bit, heap-greedy, linear/grid DP, interval DP, graph BFS/DFS unweighted, tree DP, monotonic stack, union-find, **topological sort (1750-1799)**, backtracking, trie, game theory.

**Outlier / skip-class** (NOT installed anywhere — problems with these tags flow as derivation reps under substitute buckets): monotonic deque/queue, quickselect, rolling hash, Segment Tree/BIT, MST, Geometry, Design.

---

## Already solved in this band (excluded from Phase 2)

`LC/1850-1900.md` shows 5 problems logged under the old protocol — they contribute to Phase 2 ownership when the rebuilt queue is generated, not to Group A above. (Specific slugs verified to not collide with Find the City... or Fair Distribution of Cookies.)

---

## Tracker (Group A — deal blind, one bare link per "next")

| # | Topic | Phase 1 | Status |
|---|-------|---------|--------|
| 1 | Dijkstra / Shortest Path | ☐ | — |
| 2 | Bitmask DP | ☐ | — |

---

## Deferred / skipped acquisitions — final state at 1500-1899

| Topic | Final verdict |
|-------|---------------|
| Dijkstra / Shortest Path | ✓ installed at 1850-1899 |
| Bitmask DP | ✓ installed at 1850-1899 |
| Segment Tree / BIT | **outlier — skip-class** (0 viable in 7 bands) |
| MST | **outlier — skip-class** (2 reps in 6 bands, adjacent to Union-Find) |
| Geometry | SKIP entirely (set 2026-05-28) |
| Design | SKIP entirely (CLAUDE.md rule, always) |

If 1900+ bands ever show ≥3 viable Segment Tree or MST reps, revisit — otherwise these stay skip-class.

---

## Phase 1 serving protocol

- On "next" / "give me a problem", emit **one bare LC link** — no topic, no AR, no hint.
- Topic revealed only at debrief.
- Phase 1 problems are study-OK *after* the 30-min cap; goal is to install the mechanic. Still must be clean first-submission AC to count toward acquisition.

---

## What comes next

After Group A's 2 acquisitions clean here, generate `1850-1900/_Sealed-Queue-Phase2.md` from the ~78 unsolved problems — disguised reps per Group B bucket, shuffled blind. The blind-spot trio (monotonic stack, tree DP, union-find) should pick up cross-band ownership reps from this band's Phase 2.
