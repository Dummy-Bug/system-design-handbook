# 1500-1550 Band — Full Topic Map (all 112 problems)

> [!danger] SPOILER — labels every problem with its solution pattern and set. Do not read before solving. Planning + post-solve debrief only.

Built 2026-05-26 by reading every statement (rating 1500-1549) from `zerotrac-data/content-tsv/all_1500_with_content.tsv`. Band is 9/10 logged (1 failure — #4 Count Covered Buildings AC:N).

---

## Cross-band corrections (now 4 bands, 36 solved)

Two earlier claims were **wrong**, corrected by reading this band:

1. **Binary search on answer is NOT a blind spot.** The user *solved* it here — **#8 "Minimum K to Reduce Array Within Limit"** (BS on k, `Σceil(num/k) ≤ k²`). It's also available as **Find the Smallest Divisor Given a Threshold [1541]**. So BS-on-answer was first done at 1500-1550, vanishes at 1550-1600, returns at 1600-1650. Drop it from the never-touched list.

2. **The confirmed never-touched list is now just three:** **monotonic stack, tree DP, union-find** — across all 36 solved (1500-1700).
   - Monotonic stack present here (Sum of Subarray Ranges, Beautiful Towers I) — not solved.
   - Tree DP present here (Smallest Subtree with all the Deepest Nodes) — not solved.
   - **Union-Find is scarce at 1500-1550** (≈1) — its canonical reps live at 1550-1600+ (Earliest Moment Friends).

---

## Coverage summary

| Pattern | # in band (~) | Done in band? | Priority |
|---------|---------------|---------------|----------|
| Greedy / observation | ~25 | ✅ (several) | low |
| Math / number theory / bit | ~22 | ✅✅ (#7,#9) | low (math-reflex) |
| Hashing / counting | ~15 | ✅✅ (#2,#3) | low-med |
| Sliding window | ~10 | ✅ (#1) | med |
| Linear / grid / counting DP | ~10 | — | med-HIGH |
| Sort + scan / prefix | ~8 | ✅ (#4 failed, #6, #9) | med |
| Design (data structure) | ~7 | — | med |
| Graph BFS/DFS / flood-fill | ~6 | — | med |
| Two-pointer / interval merge | ~5 | — | med |
| Heap / top-k | ~4 | ✅ (#5) | low-med |
| **Monotonic stack** | ~4 | ❌ none | **TOP** |
| **Tree DP** | ~3 | ❌ none | **TOP** |
| Binary search on answer | ~2 | ✅ (#8) | done — reinforce |
| **Union-Find** | ~1 | ❌ none | gap, but scarce — install at 1550-1600 |
| Interval DP | 0 | — | absent (only Stone Game @1550-1600) |

---

## Ownership tracker

Owned = **3 cold first-submission cleans**, reps 2-3 disguised/combined (rule 6). Marks: `◯` 0/3 · `◐` 1-2/3 · `●` owned. Prior vanilla cleans cap a bucket at 1/3 (reps 2-3 must be disguised, none done yet). Soft-fail/hinted/failed = 0.

| Core bucket | Cold cleans | Status | Need |
|-------------|-------------|--------|------|
| Sliding window | 1 (#1) | ◐ | 2 disguised |
| Hashing / counting | 1 (#2,#3 vanilla) | ◐ | 2 disguised |
| Heap / top-k | 1 (#5) | ◐ | 2 disguised |
| Binary search on answer | 1 (#8) | ◐ | 2 disguised |
| Greedy / observation | 0 | ◯ | 3 |
| Linear / grid / counting DP | 0 | ◯ | 3 |
| Sort + scan / prefix | 0 (#4 failed) | ◯ | 3 |
| Design | 0 | ◯ | 3 |
| Graph BFS/DFS | 0 | ◯ | 3 |
| Two-pointer / interval merge | 0 | ◯ | 3 |
| **Monotonic stack** (blind) | 0 | ◯ | acquisition + 3 |
| **Tree DP** (blind) | 0 | ◯ | acquisition + 3 |

(Union-find scarce here → own it at 1550-1600. Interval DP absent → Stone Game @1550-1600.)

---

## What's already trained (the 9 logged, both axes)

Depth from the compact remarks (times, bugs, AC/fail).

| # | Problem | rating | Breadth (pattern) | D×C | Note |
|---|---------|--------|-------------------|-----|------|
| 1 | Min Subarray Length Distinct Sum ≥ K | 1505 | sliding window | 4 | 27min clean |
| 2 | Count Special Triplets | 1510 | fix-middle prefix/suffix count | 2 | overflow → cast long |
| 3 | Rearrange K Substrings to Target | 1514 | freq-count chunk match | 2 | 14min; Set-vs-Map (dup chunks) |
| 4 | Count Covered Buildings | 1519 | sort + adjacent-group | — | **AC:N (failed)** — loop-bound bug (`n` vs `buildings.length`) + 10min lambda syntax |
| 5 | Max Product of Three After One Replacement | 1529 | heap top-3 | 2 | overflow → long |
| 6 | Special Array II | 1523 | prefix segment-id / parity | 4 | code by ChatGPT — not a clean rep |
| 7 | Integers With Multiple Sum of Two Cubes | 1534 | precompute + enumeration | 4 | 42min; `Math.pow` float trap (the +1) |
| 8 | Minimum K to Reduce Array Within Limit | 1531 | **binary search on answer** | 4 | 26min; `(long)mid*mid`, ceil cast |
| 9 | Largest Prime from Consecutive Prime Sum | 1547 | sieve + prefix + TreeSet floor | 4 | 26min; `(long)i*i` sieve overflow |

**Breadth covered:** sliding window, prefix/freq counting, heap, sort+scan, parity-segment, number theory/sieve, **BS-on-answer**.
**Depth:** **low** — all D≤4, no derivation-heavy problems, one outright failure. Expected for the easiest band.
**The failure mode here is IMPLEMENTATION, not derivation/comprehension** — every entry has a Java bug (overflow ×3, float trap, Set-vs-Map, loop bound, lambda syntax). Contrast 1600+ where read-error/derivation dominate. So the trend across bands:

```
1500-1550:  failures = IMPLEMENTATION (overflow, float, API, syntax)
1550-1600:  failures = impl + early derivation
1600-1650:  failures = COMPREHENSION (read-error)
1650-1700:  failures = derivation + comprehension (deep)
```

---

## GAP PATTERNS → Set A (breadth / prereq ladder, study-OK)

| Pattern | Problem | rating | The move |
|---------|---------|--------|----------|
| Monotonic stack | **Sum of Subarray Ranges** | 1504 | contribution technique: for each element, prev/next-smaller and prev/next-greater spans via monotonic stacks. The canonical mono-stack lesson. |
| Tree DP | **Smallest Subtree with all the Deepest Nodes** | 1534 | post-order returns `(depth, subtree-root)`; combine at parent (same idiom as LCA-of-deepest-leaves). |
| BS-on-answer (reinforce) | **Find the Smallest Divisor Given a Threshold** | 1541 | `feasible(d)=Σceil(num/d) ≤ threshold`. You did #8; this is a second clean rep. |
| Heap-greedy | **Largest Values From Labels** | 1501 | greedy by value desc with a per-label cap; heap/sort. |

(Alt stack: Beautiful Towers I [1519]. Alt tree: Delete Nodes And Return Forest [1511]. **Union-Find: scarce here — install at 1550-1600 instead.**)

## Set B (derivation × comprehension — solve cold, unsolved)

| Problem | rating | D×C | The trap |
|---------|--------|-----|----------|
| Global and Local Inversions | 1516 | 3×2=6 | every local inversion is global → check no element moves >1 from sorted pos; one-line condition, non-obvious |
| Count Triplets That Form Two Arrays of Equal XOR | 1524 | 3×2=6 | prefix-XOR: `pre[i]==pre[k+1]` ⇒ any j in between works; reframe from O(n³) |
| Determine if Two Strings Are Close | 1530 | 2×3=6 | two conditions: same char-set AND same multiset of frequencies; easy to half-state |
| Minimum Adjacent Swaps to Alternate Parity | 1548 | 3×2=6 | two target assignments (even-first / odd-first), sum of positional gaps; pick min |
| Tuple with Same Product | 1530 | 2×2=4 | count equal products, each contributes 8 tuples; combinatorial factor easy to miss |

---

## The plan for this band

Already 9/10 logged, so the two sets are **carry-forward training**:
1. **Set A** — install monotonic stack (Sum of Subarray Ranges) and tree DP (Smallest Subtree with Deepest Nodes) at the easiest level they appear. Reinforce BS-on-answer (already done) with Find the Smallest Divisor.
2. **Set B** — comprehension/derivation reps, though depth ceilings are lower here than 1600+.
3. **Union-Find: do NOT force it here** (scarce) — install at 1550-1600 (Earliest Moment Friends).
4. **The standout band lesson: implementation discipline** — overflow/float/API bugs caused most of the friction. The pre-submit checklist in `CLAUDE.md` is the direct fix.
