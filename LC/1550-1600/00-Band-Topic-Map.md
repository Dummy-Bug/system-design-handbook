# 1550-1600 Band — Full Topic Map (all 83 problems)

> [!danger] SPOILER — labels every problem with its solution pattern and set. Do not read before solving. Planning + post-solve debrief only.

Built 2026-05-26 by reading every statement (rating 1550-1599) from `zerotrac-data/content-tsv/all_1500_with_content.tsv`. Band is 10/10 solved (graduated 2026-05-07; audit notes 9/10 first-submission, 1 hint).

---

## Cross-band finding (now 3 bands, 27 solved)

Across **1550-1600 + 1600-1650 + 1650-1700 = 27 solved problems**, these stay untouched:
- **Monotonic stack** — present in all 3 bands, never solved.
- **Tree DP** — never solved (1550-1600 #9 Unit Conversion is tree *traversal*, not tree DP).
- **Union-Find / DSU** — never solved canonically.

**Binary-search-on-answer** is the exception to the "always available" claim: it's **nearly absent at 1550-1600** (≈0), appears at 1600-1650 (4), thins at 1650-1700 (2). So it's a *1600+* pattern — can't install it here, must install it in the 1600-1650 band.

**New this band: Interval DP is available** — **Stone Game [1590]** is the first true interval/minimax DP across all three bands (1600-1700 had none). If you want an interval-DP rep, it lives here, not higher.

---

## Coverage summary

| Pattern | # in band | Done in band? | Priority |
|---------|-----------|---------------|----------|
| Greedy / observation | ~22 | ✅✅✅✅ (#1,#2,#5,#6) | low — strong |
| Math / number theory / bit | ~14 | ✅✅ (#4,#7) | low (math-reflex) |
| Sliding window / prefix | ~10 | ✅ (#10) | med |
| Hashing / counting | ~8 | — | med |
| Linear / grid / counting DP | ~8 | — | med-HIGH |
| Graph BFS/DFS / flood-fill | ~6 | ✅ (#9 tree BFS) | med |
| Difference array / prefix-range | ~3 | ✅ (#8) | low |
| Design (data structure) | ~5 | — | med |
| Game theory | ~3 | ✅ (#3) | low |
| **Monotonic stack** | ~3 | ❌ none | **TOP** |
| **Tree DP** | ~2 | ❌ none | **TOP** |
| **Union-Find / DSU** | ~2 | ❌ none | **TOP** |
| **Heap / PQ greedy** | ~3 | ❌ none | HIGH |
| **Interval DP** | 1 (Stone Game) | ❌ none | MED — rare, grab it here |
| Binary search on answer | ~0 | n/a | absent (1600+ topic) |

---

## Ownership tracker

Owned = **3 cold first-submission cleans**, reps 2-3 disguised/combined (rule 6). Marks: `◯` 0/3 · `◐` 1-2/3 · `●` owned. Prior vanilla cleans cap a bucket at 1/3. Soft-fail/hinted = 0.

| Core bucket | Cold cleans | Status | Need |
|-------------|-------------|--------|------|
| Greedy / observation | 1 (#1,#2,#5 vanilla) | ◐ | 2 disguised |
| Game theory | 1 (#3) | ◐ | 2 disguised |
| Sliding window | 1 (#10) | ◐ | 2 disguised |
| Graph / tree traversal | 1 (#9) | ◐ | 2 disguised |
| Difference array / prefix-range | 0 (#8 had a bug) | ◯ | 3 |
| Hashing / counting | 0 | ◯ | 3 |
| Linear / grid / counting DP | 0 | ◯ | 3 |
| Design | 0 | ◯ | 3 |
| **Heap-greedy** (gap) | 0 | ◯ | 3 |
| **Monotonic stack** (blind) | 0 | ◯ | acquisition + 3 |
| **Tree DP** (blind) | 0 | ◯ | acquisition + 3 |
| **Union-Find** (blind) | 0 | ◯ | acquisition + 3 |
| **Interval DP** (Stone Game — only rep ≤1700) | 0 | ◯ | acquisition + 3 |

---

## What's already trained (the 10 solved, both axes)

Depth scored from how the solve actually went (times, hints, bugs). This band's log is compact (no full verbatim/code), so depth is inferred from the remark.

| # | Problem | rating | Breadth (pattern) | D×C | Note |
|---|---------|--------|-------------------|-----|------|
| 1 | Maximum Bitwise XOR After Rearrangement | 1556 | greedy + char count | 2 | 10min; "XOR misleads into bit-DP" comprehension trap |
| 2 | Min Cost to Equalize Arrays Using Swaps | 1579 | freq-map + excess pairing | 6 | 100min; operator-precedence bug `(freq&1)` |
| 3 | Final Element After Subarray Deletions | 1591 | game theory / 1-move reduction | 6 | 46min; turn-1 reduction insight (misdirection) |
| 4 | Smallest Repunit Multiple of K | 1593 | pigeonhole + mod recurrence | 6 | hinted (pigeonhole bound taught); overflow |
| 5 | Min Cost to Acquire Required Items | 1580 | greedy + case analysis | 4 | mirror-case copy-paste bug (self-caught) |
| 6 | Max Sum of Three Numbers Divisible by Three | 1585 | mod bucketing + greedy | 4 | hinted ("mod 3 → drill"); TreeSet-dedup + max-tracking bugs |
| 7 | XOR After Range Multiplication Queries I | 1556 | direct simulation | 1 | <15min trivial |
| 8 | Zero Array Transformation I | 1580 | difference array | 4 | diff-array off-by-one (`diff[j+1]-=1`) |
| 9 | Unit Conversion I | 1591 | tree BFS + running product | 4 | tree *traversal*, not tree DP |
| 10 | Find the Power of K-Size Subarrays II | 1595 | sliding window / run tracking | 2 | clean O(n) |

**Breadth covered:** greedy (×4), game theory, number theory, simulation, diff array, tree BFS, sliding window. **Heavily greedy/math** — consistent with a low band.
**Depth:** moderate — three 6s, no 9s. Less stretch than 1650-1700 (expected; easier band). Two hints (#4, #6).
**Untouched (TOP gaps):** monotonic stack, tree DP, DSU — same blind spots. Plus heap-greedy and the lone interval-DP (Stone Game).

---

## GAP PATTERNS → Set A (breadth / prereq ladder, study-OK)

| Pattern | Problem | rating | The move |
|---------|---------|--------|----------|
| Monotonic stack | **Next Greater Node In Linked List** | 1570 | classic next-greater via decreasing stack of pending indices. |
| Tree DP | **Count the Number of Good Nodes** | 1565 | post-order DFS carrying subtree info up; count nodes whose subtree satisfies a condition. |
| Union-Find | **The Earliest Moment When Everyone Become Friends** | 1558 | sort events by time, union, stop when one component remains. Canonical DSU intro. |
| Interval DP | **Stone Game** | 1590 | `dp[i][j]` = best score-diff on pile range; minimax. The only interval-DP rep ≤1700 — grab it here. |
| Heap-greedy | **Minimum Operations to Halve Array Sum** | 1550 | max-heap, always halve the current largest. |

(Alt stack: Score of Parentheses [1562]. Alt tree: Time Needed to Inform All Employees [1561]. Alt DSU: Properties Graph [1565].)

## Set B (derivation × comprehension — solve cold, unsolved)

| Problem | rating | D×C | The trap |
|---------|--------|-----|----------|
| Minimum Operations to Make a Special Number | 1588 | 3×3=**9** | reframe to "keep a subsequence ending in 00/25/50/75"; deletion-count is misleading |
| Decrease Elements To Make Array Zigzag | 1558 | 2×3=6 | two parity passes (even-low vs odd-low), each element pays max(0, self−min(neighbors)−... ); easy to misframe |
| Ways to Split Array Into Good Subarrays | 1597 | 3×2=6 | product of gaps between consecutive 1s; off-by-one on the gap definition |
| Maximum Number of Operations to Move Ones to the End | 1593 | 3×2=6 | count how each 1 carries past trailing 0s; observation, not simulation |
| Number of Ways Where Square = Product of Two | 1593 | 2×3=6 | hash square counts; two symmetric triplet types, dense statement |

---

## The plan for this band

Already 10/10 logged (graduated), so the two sets are **carry-forward training**, not graduation-filling:
1. **Set A** installs the cross-band blind spots at the *easiest* level they're available — stack, tree DP, DSU here, plus the lone interval-DP (Stone Game) which exists nowhere higher ≤1700.
2. **Set B** continues the comprehension-depth engine.
3. **BS-on-answer is not installable here** (absent) — that primitive must come from the 1600-1650 band.
