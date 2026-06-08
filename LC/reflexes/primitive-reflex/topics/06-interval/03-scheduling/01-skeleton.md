# Interval Atom 03 — Greedy scheduling (sort by end)

*2026-06-07*

## The problem (Non-overlapping Intervals, LC 435)

Return the **minimum number of intervals to remove** so the rest are non-overlapping (touching at an endpoint is allowed). Mirror form: **keep the maximum number of mutually non-overlapping intervals**, then `removals = n − kept`. This is classic **activity selection**.

## ① Trigger

"Pick the most non-conflicting intervals", "attend the most meetings", "fewest removals to de-conflict", "max activities in one room". The signal that flips this away from merge (atom #1): you're not unioning overlaps, you're **selecting a maximum disjoint subset** — a count/choice problem, not a coverage one. This is the family's first **sort-by-end** atom.

## ② Motivation — why sort by *end* (break the simpler tool)

The instinct is sort by **start** and take greedily. Break it on `[[1,10],[2,3],[4,5],[6,7]]`: sorted by start it's already in that order; take `[1,10]` first and it blocks everything → keep 1, remove 3. But the truth is keep `[2,3],[4,5],[6,7]` and remove only `[1,10]` → remove 1. Start-sort-take-first is wrong because a long early-starting interval hogs the line.

The fix is the rule itself: when intervals conflict, **keep the one that finishes earliest** — it leaves the most room for everything after. So **sort by end**, and the earliest-finisher is always the safe greedy pick. Sorted by end the same input is `[2,3],[4,5],[6,7],[1,10]` → keep 3, remove 1. ✓

(Greedy is provably optimal: the earliest-finishing interval is in *some* optimal solution — an exchange argument — so taking it never hurts.)

## ③ The move

Sort by **end**. Carry `lastEnd` = end of the last *kept* interval. Walk: if the next interval starts at or after `lastEnd`, keep it (advance `lastEnd`); else it's a conflict → skip (a removal).

```java
Arrays.sort(intervals, (a, b) -> Integer.compare(a[1], b[1]));   // by END, overflow-safe
int lastEnd = Integer.MIN_VALUE;
int removals = 0;
for (int[] iv : intervals) {
    if (iv[0] >= lastEnd) lastEnd = iv[1];   // keep
    else removals++;                         // conflict → remove
}
return removals;
```

`lastEnd = Integer.MIN_VALUE` seeds it so the first interval is always kept. The test is `>=` because **touching is allowed** (`[1,2]`,`[2,3]` don't conflict) — the family's closed-vs-touching bit again, here deciding `>=` vs `>`.

## ④ Costumes

- Non-overlapping Intervals (435) — min removals = `n − kept`.
- Maximum events / activity selection (1353 simple, "Maximum Number of Events") — count kept directly.
- **Min Arrows to Burst Balloons (452)** — sub-variant 3b: sort by end, shoot an arrow at the first end, skip every balloon it pierces (`start ≤ arrow`), new arrow at the next uncovered end. Same earliest-end greedy; here the boundary is `>` vs `>=` depending on whether a balloon touching the arrow counts as burst (452: it does → use `>`).

## ⑤ Reflex check

Prompt: *intervals → keep the most non-overlapping / fewest removals — move?*
Answer: *sort by END; carry `lastEnd`; `start ≥ lastEnd` → keep, advance `lastEnd`; else skip (removal). Earliest-finisher greedy is optimal; `≥` because touching is allowed.*
