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
| Math / number theory | ~9 | ⚠️ #4,#6 both hinted → 0 clean | **CORE — needs ownership** (math-reflex = recall only) |
| Bit operations / XOR | ~5 | ◐ #1,#7 vanilla | **CORE — distinct from math** (bitmask, XOR prefix, bit-width) |
| Sliding window / prefix | ~10 | ✅ (#10) | med |
| Hashing / counting | ~8 | — | med |
| Linear / grid / counting DP | ~8 | — | med-HIGH |
| Graph BFS/DFS / flood-fill | ~6 | ✅ (#9 tree BFS) | med |
| Difference array / prefix-range | ~3 | ✅ (#8) | low |
| Game theory | ~3 | ✅ (#3) | low |
| **Monotonic stack** | ~3 | ❌ none | **TOP** |
| **Tree DP** | ~2 | ❌ none | **TOP** |
| **Union-Find / DSU** | ~2 | ❌ none | deferred → 1600-1650 (too few here) |
| **Heap / PQ greedy** | ~3 | ❌ none | HIGH |
| **Interval DP** | 1 (Stone Game) | ❌ none | MED — rare, grab it here |
| Binary search on answer | ~0 | n/a | absent (1600+ topic) |
| **Binary search (plain — floor/ceil/lower_bound)** | ~3 (Closest Nodes, Time Based KV, Search Suggestions) | ◐ acquisition done | **CORE — added 2026-05-28** (taxonomy originally conflated this with BS-on-answer and missed it) |

---

## Ownership tracker (LearnYard subtopic granularity — re-audited 2026-05-28)

Owned = **3 cold first-submission cleans**, reps 2-3 disguised/combined (rule 6). Marks: `◯` 0/3 · `◐` 1-2/3 · `●` owned. Soft-fail/hinted = 0.

**Subtopic re-audit (2026-05-28):** all 24 solved problems re-classified into LearnYard subgroups via their doocs editorials (`editorials-data/band_1550_1599/`), combined with the logged clean/soft outcomes. Buckets are now LearnYard subgroups, not broad LC tags. **Clean = first-submission AC** from the 24 solved; soft-fail/hinted listed but credit 0.

| LearnYard subgroup | Cold cleans | Status | Clean reps (✓) / non-counting (✗) | Need |
|--------------------|-------------|--------|-----------------------------------|------|
| Greedy / Part I | 3 | ● | ✓#1 Max Bitwise XOR · ✓#5 Min Cost Acquire · ✓#20 Pancake · ✗#2 soft · ✗#6 hinted | OWNED |
| Game Theory / Level I | 3 | ● | ✓#3 Final Element · ✓#13 Stone Game · ✓#23 Flower Game | OWNED |
| Prefix Sum / Implementary | 3 | ● | ✓#14 Binary Subarrays · ✓#17 Fair Array · ✓#18 Increment Submatrices 2D · ✗#8 off-by-one soft | OWNED |
| Bit Manipulation / Basic Bit (XOR) | 2 | ◐ | ✓#1 Max Bitwise XOR · ✓#19 Count Max-OR Subsets · (#7 trivial sim, not counted) | 1 disguised |
| Sliding Window / Dynamic Size | 2 | ◐ | ✓#10 Power K-Size · ✓#14 Binary Subarrays | 1 disguised |
| Graphs / Graph Representation (traversal) | 2 | ◐ | ✓#9 Unit Conversion · ✓#16 Restore Array | 1 disguised |
| Matrix Chain / **Interval DP** | 1 | ◐ | ✓#13 Stone Game | 2 (shortfall — no more in-band) |
| **Stack / Monotonic Stack** (blind-spot) | 1 | ◐ | ✓#22 Next Greater Node (FIRST blind-spot clean ✓) | 2 disguised |
| DP Level 1 / Linear DP | 1 | ◐ | ✓#17 Fair Array (linear/prefix) | 2 disguised |
| Hashing / Implementary | 2 | ◐ | ✓#14 Binary Subarrays · ✓#16 Restore Array · ✗#2 soft · ✗#4 hinted · ✗#12 hinted | 1 disguised |
| **DP Level 1 / DP On Grid** (new acq) | 0 | ◯ | acquisition pending (Minimum Falling Path Sum) | acq + 3 |
| **DP Level 1 / DP on String** (new acq) | 0 | ◯ | acquisition pending (Longest String Chain) | acq + 3 |
| (Math / Number Theory — no LY subgroup) | 0 | ◯ | ✗#4 hinted · ✗#6 hinted | 3 — math-reflex ≠ solving |
| Heap (PQ) / Heap-Greedy | 0 | ◯ | ✗#21 Min Ops Halve soft (float trap) | re-solve + cross-band |
| Recursion & Backtracking | 0 | ◯ | ✗#11 Happy Strings soft · (#19 is bit-enum, not backtracking) | NOT installable — defer (see Phase-1) |
| Binary Search / Upper & Lower Bound | 0 | ◯ | ✗#24 Closest Nodes soft (TLE→AC) | 3 |
| **DP on Trees** (blind-spot) | 0 | ◯ | ✗#15 Construct BST hinted (and it's tree *construction*, not DP-on-Trees) | acq + 3 — STILL homeless, absent here |
| ~~Union-Find~~ (blind-spot) | — | — | deferred → 1600-1649 (7 reps) | — |

> [!danger] Two phantom corrections carried from the 1500-1549 / subtopic re-audit
> - **"Tree DP"** in the old tracker was conflated: #15 Construct BST is tree *construction* (editorial: DFS + Binary Search), not DP-on-Trees. **DP-on-Trees is absent at 1550-1599** and still has no install band.
> - **Backtracking** is not installed: #11 Happy Strings soft-failed, #19 is bit-subset enumeration (not backtracking). No clean genuine backtracking here → deferred.

> [!note] Scaffolding subgroups excluded (not ownership targets)
> Sorting (#12, #20 partial), Matrix (#18), Two-Pointer-on-Strings, Stack/Implementary, Stack-with-String — present in solves but excluded as derivation targets (like Design).

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

## Problem sets

Problem sets are generated per the **band setup protocol** in `LC/CLAUDE.md`. See:
- `Phase-1-Acquisition.md` — **RE-BASED 2026-05-28.** The acquisition floor is **1500-1550**, so this band's Group A acquires only the two genuinely-new patterns: **game theory + interval DP**. All other patterns were acquired at 1500-1550, and their 1550-1600 problems (Pancake Sorting, Binary Subarrays, etc.) are now **Phase 2 derivation reps** for this band, not acquisitions.
- `_Sealed-Queue-Phase2.md` — derivation problems (shuffled blind, topic hidden until after solve).
- AR data at `zerotrac-data/band_1550_1599_with_ar.tsv`.

**Graduation (rule 6, ownership-based):** every core bucket above must reach `●` (3 cold first-submission cleans, reps 2-3 disguised). For topics with <3 in-band problems (game theory, heap, mono stack, interval DP), the band contributes what it has — shortfalls complete in adjacent bands naturally, not by cross-band peeking. **Union-Find is deferred to 1600-1650** (only ~2 here). (Design is excluded at every band — not a derivation/ownership target.)
