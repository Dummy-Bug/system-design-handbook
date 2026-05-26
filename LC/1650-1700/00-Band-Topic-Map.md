# 1650-1700 Band — Full Topic Map (all 99 problems)

> [!danger] SPOILER — labels every problem with its solution pattern and set. Do not read before solving. Planning + post-solve debrief only.

Built 2026-05-26 by reading every statement (rating 1650-1700) from `zerotrac-data/content-tsv/`. Band is 10/10 solved but NOT graduated under ownership rule (rule 6) — most core buckets at 0/3 or 1/3.

---

## ⚠️ Cross-band finding (the headline)

Comparing against `1600-1650/00-Band-Topic-Map.md`: **four patterns are untouched across BOTH bands** — the user has now solved 17 problems (7 + 10) and *never once* done:

- **Monotonic stack**
- **Binary search on answer**
- **Tree DP** (in fact zero binary-tree problems among all 17 solved)
- **Union-Find / DSU** (approximated once via linear scan in 1650-1700 #9, but canonical DSU never written)

These are **systematic blind spots, not band-specific gaps.** 1700+ will punish them hard — they're prime Q3 material. Installing these is higher priority than anything else, and it must happen at 1650-ish difficulty before 1700+.

---

## Coverage summary

| Pattern | # in band | Done in band? | Priority |
|---------|-----------|---------------|----------|
| Hashing / prefix-state | ~14 | ✅✅✅ (#2,#6,#10) | low — strong |
| Greedy / lower-bound / observation | ~20 | ✅✅ (#1,#3) | low-med |
| Graph BFS/DFS / flood-fill | ~12 | ✅ (#5 multi-source) | med |
| Linear / grid / counting DP | ~12 | — | med-HIGH (knapsack/counting untouched) |
| Prefix/suffix precompute | ~4 | ✅✅ (#4,#8) | low |
| Math / bit / number theory | ~12 | ◐ (#7 vanilla) | **CORE — needs ownership** (math-reflex = recall only) |
| Heap / PQ greedy | ~7 | ❌ none | MED-HIGH gap |
| Design (data structure) | ~5 | ❌ none | med |
| **Monotonic stack** | 2-3 | ❌ none (both bands) | **TOP** |
| **Binary search on answer** | 2 | ❌ none (both bands) | **TOP** |
| **Tree DP** | ~6 | ❌ none (both bands) | **TOP** |
| **Union-Find / DSU** | ~3 | ❌ canonical never | **TOP** |
| **Topological sort** | 2 | ❌ none | HIGH |
| Sliding window (+ monotonic deque) | ~5 | ✅ window only (#?) | MED — deque variant untouched |
| Interval DP | 0-1 | — | absent/rare |

---

## Ownership tracker

Owned = **3 cold first-submission cleans**, reps 2-3 disguised/combined (rule 6). Marks: `◯` 0/3 · `◐` 1-2/3 · `●` owned. Only clean first-submission counts; soft-fail (#3,#8,#9) and hinted (#6) = 0.

| Core bucket | Cold cleans | Status | Need |
|-------------|-------------|--------|------|
| Greedy / lower-bound derivation | 1 (#1) | ◐ | 2 disguised |
| Hashing / prefix-state | 1 (#2,#10) | ◐ | 2 disguised |
| Graph BFS/DFS | 1 (#5) | ◐ | 2 disguised |
| Prefix/suffix precompute | 1 (#4) | ◐ | 2 disguised (#8 soft) |
| **Monotonic stack** (blind) | 0 | ◯ | acquisition + 3 |
| **Binary search on answer** | 0 in band | ◯ | 3 |
| **Tree DP** (blind) | 0 | ◯ | acquisition + 3 |
| **Union-Find** (blind) | 0 (#9 soft, linear-scan) | ◯ | acquisition + 3 |
| Topological sort | 0 | ◯ | 3 |
| Heap-greedy | 0 | ◯ | 3 |
| Sliding window + monotonic deque | 0 | ◯ | 3 |
| Counting / knapsack DP | 0 | ◯ | 3 |
| Math / number theory / bit | 1 (#7 vanilla) | ◐ | 2 disguised — math-reflex ≠ solving |

---

## What's already trained (the 10 solved, both axes)

Depth scored from how the solve actually went (verdicts, hints, WAs).

| # | Problem | rating | Breadth (pattern) | D×C | Note |
|---|---------|--------|-------------------|-----|------|
| 1 | Min Operations to Make Array Non-Decreasing | 1662 | greedy / lower-bound (Q1-Q4) | 6 | 1h31 — algorithm-first dead-ends, then lower-bound derivation |
| 2 | Min Absolute Distance Between Mirror Pairs | 1669 | hashing (reverse+map) | 4 | clean, 40min |
| 3 | Min Operations to Make Binary Palindrome | 1657 | nearest-X candidates + bits | 6 | missed the −1 candidate → WA |
| 4 | Find the Smallest Balanced Index | 1697 | prefix/suffix + overflow guard | 6 | MOD reflex wrong; rearrange-inequality fix |
| 5 | Multi-Source Flood Fill | 1671 | graph multi-source BFS | 4 | clean, sort-sources-by-color insight |
| 6 | Longest Subarray XOR-0 & Equal Even/Odd | ~1670 | 2D-state prefix hashing | 9 | hinted (1h43); bit-packed combined key |
| 7 | Number of Unique XOR Triplets I | 1663 | bit-width structural counting | 9 | 3h self-derived; Q2 @ 26.7% AR |
| 8 | Longest Common Prefix Adjacent After Removals | ~1670 | left/right precompute (remove-one) | 4 | prefix-vs-equality misread → WA |
| 9 | Path Existence Queries in a Graph I | ~1670 | connected components (lin scan) | 6 | sentinel/last-node bug → WA; DSU flagged as canonical-not-done |
| 10 | Closest Equal Element Queries | 1699 | hashing + array doubling (circular) | 6 | doubling insight for circular nearest |

**Breadth covered:** greedy/lower-bound, hashing (×3, incl 2D-state + doubling), prefix/suffix, graph BFS, connected-components, bit-structural, candidate-gen. **Richer than 1600-1650.**
**Depth:** very deep — two 9s (one 3h self-derived Q2, one hinted), five 6s. This band genuinely stretched derivation.
**Still untouched (the TOP gaps above):** monotonic stack, BS-on-answer, tree DP, canonical DSU.

---

## Problem sets

Problem sets not yet generated for this band. When ready, follow the **band setup protocol** in `LC/CLAUDE.md` (read all statements → fetch AR → classify → Phase 1 + Phase 2).

**Graduation (rule 6, ownership-based):** every core bucket must reach `●` (3 cold first-submission cleans, reps 2-3 disguised). Interval DP is absent at this band — shortfall completes at 1550-1600 (Stone Game).
