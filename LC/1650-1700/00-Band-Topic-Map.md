# 1650-1700 Band — Full Topic Map (all 99 problems)

> [!danger] SPOILER — labels every problem with its solution pattern and set. Do not read before solving. Planning + post-solve debrief only.

Built 2026-05-26 by reading every statement (rating 1650-1700) from `zerotrac-data/content-tsv/`. Band is 10/10 solved (graduation audit pending — audit notes 6/10 first-submission). This map serves revision targeting + identifying carry-forward gaps into 1700+.

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
| Math / bit / number theory | ~12 | ✅✅ (#7,#3) | low (math-reflex) |
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

## GAP PATTERNS → Set A (breadth / prereq ladder, study-OK)

One canonical rep per untouched pattern, verified from statements.

| Pattern | Problem | rating | The move |
|---------|---------|--------|----------|
| Monotonic stack | **Car Fleet** | 1678 | sort by position desc, stack of arrival times; a fleet forms when a slower car ahead caps you. *The* canonical stack problem. |
| Binary search on answer | **Minimum Speed to Arrive on Time** | 1675 | BS on speed; `feasible(s)=Σceil(dist/s) ≤ hour`. Float `hour` is the comprehension trap. |
| Tree DP | **Maximum Product of Splitted Binary Tree** | 1674 | post-order subtree sums, total−sub = other side, maximize product. |
| Union-Find | **Minimum Score of a Path Between Two Cities** | 1679 | the whole connected component of city 1 matters; min edge weight in it (DSU or BFS). Clean DSU intro. |
| Topological sort | **Find All Possible Recipes from Given Supplies** | 1678 | Kahn's algorithm; ingredients → recipe dependency DAG. |
| Sliding window + monotonic deque | **Longest Continuous Subarray Abs Diff ≤ Limit** | 1672 | window + two monotonic deques (max & min). Combines a strong gap (deque) with a known pattern. |
| Heap-greedy | **Reorganize String** | 1681 | max-heap by remaining count, always place the most frequent that isn't the last placed. |

(Stretch DSU: Power Grid Maintenance [1699] — DSU with deletion/structure.)

## Set B (derivation × comprehension — solve cold, unsolved problems)

Pattern may be familiar; chosen for non-obvious reframe + misreadable statement. `D×C`.

| Problem | rating | D×C | The trap |
|---------|--------|-----|----------|
| Count Submatrices With Equal Frequency of X and Y | 1672 | 3×3=**9** | 2D prefix on two counts simultaneously; dense statement |
| Minimum Addition to Make Integer Beautiful | 1680 | 3×3=**9** | greedy digit-carry (round up to kill low digits); easy to misframe |
| Count Collisions of Monkeys on a Polygon | 1662 | 3×2=6 | `2^n − 2` complementary counting; "no collision" reframe |
| Minimum Operations to Make the Array Alternating | 1662 | 2×3=6 | top-2 frequencies per parity class; misreadable indices |
| Maximize Area of Square Hole in Grid | 1677 | 3×2=6 | longest run of consecutive missing bars → side; misreadable bars model |
| Number of Ways to Select Buildings | 1656 | 3×2=6 | count "010"/"101" subsequences via running DP of prefixes |

---

## The plan for this band

This band is already 10/10 logged, so the two sets here are **carry-forward training**, not graduation-filling:
1. **Set A is mandatory before 1700+** — the four TOP gaps (stack, BS-on-answer, tree DP, DSU) are cross-band blind spots that 1700+ will expose as unsolvable Q3s. Install them at this difficulty first.
2. **Set B** continues the derivation engine on the comprehension sub-axis.
3. **Revision (due 2026-05-30)** of the 10 solved is separate — approach recall, not re-read.
