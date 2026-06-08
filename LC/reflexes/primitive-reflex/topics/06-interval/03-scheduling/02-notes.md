# Interval Atom 03 — notes

## Non-overlapping Intervals (LC 435) — the announced rep

"Fewest removals to make the rest non-overlapping" = "keep the largest mutually-disjoint subset", with `removals = n − kept`. Reasoning about the *keep* version (classic activity selection) is cleaner because it's a pure max-selection.

## Deriving the rule from a tiny case

`[[1,3],[2,4],[3,5]]`, touching allowed. By hand: keep `[1,3]` and `[3,5]` (they touch at 3 → fine), drop `[2,4]` (overlaps both). Keep 2, remove 1.

Why `[1,3]` over `[2,4]` when they conflict? `[1,3]` **finishes earlier** (end 3 vs 4), so it frees the line from 3 onward and leaves room for `[3,5]`; `[2,4]` frees it only from 4. The competing rule that loses: "keep smaller start" — irrelevant; the **end** is what governs what fits next.

## The dead end (worth keeping) — sort by start breaks

The natural first move is sort by **start** and take greedily. Break it:

```
[[1,10],[2,3],[4,5],[6,7]]
```

Sorted by start (already so), "take first, then take the next whose start ≥ last kept end":
- take `[1,10]` (end 10) → `[2,3]`,`[4,5]`,`[6,7]` all start < 10 → all skipped → **keep 1, remove 3**.

By hand the optimum is keep `[2,3],[4,5],[6,7]`, remove only `[1,10]` → **remove 1**. The naive start-sort is wrong: a long early-starting interval hogs the whole line. The fix is to sort by the key the rule named — **end**:

```
[2,3],[4,5],[6,7],[1,10]
```
take `[2,3]`(3) → `[4,5]`(4≥3)✓(5) → `[6,7]`(6≥5)✓(7) → `[1,10]`(1≥7? no)✗ → keep 3. ✓

### Why earliest-end greedy is *optimal* (the exchange argument)

The interval that finishes first is in *some* optimal solution. Suppose an optimal set doesn't use it; its first interval finishes no earlier, so swap it for the earliest-finisher — still non-overlapping, same size. So taking the earliest-finisher never costs you anything, and induction does the rest. That's why a single greedy pass (no DP) is correct here.

## The move and the boundary

Sort by end, carry `lastEnd` (end of last kept), seed `Integer.MIN_VALUE` so the first is always kept:

```java
Arrays.sort(intervals, (a, b) -> Integer.compare(a[1], b[1]));
int lastEnd = Integer.MIN_VALUE, removals = 0;
for (int[] iv : intervals) {
    if (iv[0] >= lastEnd) lastEnd = iv[1];
    else removals++;
}
return removals;
```

The `>=` is the family's closed-vs-touching bit, here as keep-vs-skip: LC 435 allows touching, so `start == lastEnd` is **kept**, hence `>=`. If touching counted as a conflict it'd be `>`. (Min Arrows 452 is the `>` case — see costumes.)

## Step 2 — worked example `[[1,2],[2,3],[3,4],[1,3]]` → expected removal 1

Sort by end: `[1,2](2), [2,3](3), [1,3](3), [3,4](4)`. (Tie on end 3 between `[2,3]` and `[1,3]`; either order is fine.)

| iv | start ≥ lastEnd? | action | lastEnd | removals |
|---|---|---|---|---|
| [1,2] | 1 ≥ MIN ✓ | keep | 2 | 0 |
| [2,3] | 2 ≥ 2 ✓ | keep | 3 | 0 |
| [1,3] | 1 ≥ 3 ✗ | remove | 3 | 1 |
| [3,4] | 3 ≥ 3 ✓ | keep | 4 | 1 |

Result `1`. Note `[2,3]` is kept over the tied `[1,3]` and the `2 ≥ 2` / `3 ≥ 3` touches are kept — both the tie handling and the `>=` boundary exercised.

## Step 3 — edge cases

1. **Empty / single** `[]` or `[[1,2]]` → `0` removals — first always kept, nothing to remove.
2. **All identical** `[[1,2],[1,2],[1,2]]` → `2` — keep one, remove the rest (each later one fails `1 ≥ 2`).
3. **Touching chain** `[[1,2],[2,3],[3,4]]` → `0` — every `start == lastEnd` is kept via `>=`. If this returns 2 you wrote `>` by mistake.
4. **One swallowing many** `[[1,100],[1,2],[2,3],[3,4]]` → `1` (remove `[1,100]`) — the motivating case; verifies end-sort, not start-sort.
5. **Nested** `[[1,10],[2,3]]` → `1` — sorted by end `[2,3],[1,10]`; keep `[2,3]`, `[1,10]` conflicts (1 < 3) → remove. Earliest-end keeps the *smaller* nested one, correctly.

## Discriminator — the family's question, now answered "end"

merge (atom #1) sorts by **start** → *combine coverage*. Scheduling sorts by **end** → *greedily select a max disjoint subset*. Same intervals, opposite key, opposite goal. The tell: are you **covering** the line (union) or **picking the most non-conflicting** (count)? Picking → sort by end.

> **Logging honesty:** approach **fully self-derived via Socratic Q&A** — the by-hand answer, the "keep the earlier-finishing" rule, the recognition that start-sort breaks (ran the `[[1,10],...]` trap themselves), the sort-by-end fix, and the `>=` touching boundary. The Java code was provided by Claude on request and submitted (AC). Install grade; cold recognition comes from zerotrac.
