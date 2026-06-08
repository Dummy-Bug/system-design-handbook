# Interval Atom 01 — Merge / union

*2026-06-07*

## The problem (Merge Intervals, LC 56)

Given a list of intervals `[start, end]`, some overlapping, return the smallest list of intervals covering exactly the same points — overlapping ones fused into one. `[[1,3],[2,6],[8,10],[15,18]]` → `[[1,6],[8,10],[15,18]]` (`[1,3]` and `[2,6]` overlap → `[1,6]`; the other two are disjoint).

## ① Trigger

You're handed intervals and asked for their **union** — "merge the overlapping ones", "fewest intervals covering the same range", "free/busy time", "combined coverage". The output is *fewer* intervals than the input, each a fused run. Whenever the question is "collapse overlapping ranges into maximal runs," it's this atom.

## ② Motivation — why sort-by-start (break the simpler tool)

Try it with **no sorting**, one left-to-right pass comparing each interval to the previous: `next.start ≤ prev.end → fuse`. On `[[1,3],[2,6],[8,10],[15,18]]` it works. Now shuffle the *same set*: `[[8,10],[1,3],[15,18],[2,6]]`. The pass compares `[1,3]` against `[8,10]` (no fuse), `[15,18]` against `[1,3]` (no fuse), `[2,6]` against `[15,18]` (no fuse) — and reports four disjoint intervals. The `[1,3]`+`[2,6]` merge is missed entirely.

The single comparison "is this interval glued to the *one* before it?" is only valid if the intervals that could glue are actually *adjacent in the scan*. **Sorting by start guarantees that**: once sorted, any interval that overlaps an earlier one overlaps the *running merged tail* specifically, so one variable (the current run) is enough. Sorting is what reduces "compare against all previous" to "compare against the last."

## ③ The move

Sort by `start`. Carry the current run `cur` (the tail of the output list). For each next interval:

- **`next.start ≤ cur.end`** → they touch/overlap → extend in place: `cur.end = max(cur.end, next.end)`.
- **else** → disjoint → flush: append `next` as the new `cur`.

Two pieces people drop:
- the fused end is `max(cur.end, next.end)`, **not** `next.end` — the earlier interval can fully swallow the later (`[1,8]`+`[2,5]` = `[1,8]`).
- `cur.start` never changes — sorted by start, the earlier start always wins, so only `cur.end` moves.

```java
Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));   // NOT a[0]-b[0] (overflow)
List<int[]> out = new ArrayList<>();
out.add(intervals[0].clone());
for (int i = 1; i < intervals.length; i++) {
    int[] cur = out.get(out.size() - 1);
    if (intervals[i][0] <= cur[1])
        cur[1] = Math.max(cur[1], intervals[i][1]);   // mutate the tail in place
    else
        out.add(intervals[i].clone());
}
return out.toArray(new int[0][]);
```

`cur` is the same array reference held in the list, so mutating `cur[1]` updates the tail directly — no remove-then-re-add.

## ④ Costumes

- Merge Intervals (56) — the bare statement.
- Summary Ranges (228) — consecutive integers are length-1 intervals; merge the runs.
- Partition Labels (763) — *disguised*: each letter's [firstIndex, lastIndex] is an interval; the partitions are the merged runs.
- Employee Free Time (759) — merge everyone's busy intervals, then the **gaps** between merged runs are the answer.
- Meeting Rooms I (252) — "can attend all?" = "does any pair overlap?" = the merge never had to fuse anything.
- Insert Interval (57) — sub-variant: list is pre-sorted, walk and merge the spill around the one inserted interval.

## ⑤ Confusion matrix

| Confused with | Discriminator |
|---|---|
| just sort the intervals | sorting only reorders; merge **collapses** overlapping runs → output has *fewer* intervals. The sort is a *pre-step*, not the answer |
| `<` vs `<=` in the fuse test | use `<=` because intervals are **closed** — touching at a point (`[1,5]`,`[5,10]`) counts as overlap → `[1,10]`. Strict `<` only if the problem says touching does NOT count (see notes) |
| fused end = `next.end` | wrong when the earlier interval swallows the later (`[1,8]`+`[2,5]`); always `max(cur.end, next.end)` |

*(Sibling interval atoms — sort-by-end scheduling, sweep-line concurrency — are not yet installed; their discriminators get added to this matrix when they are. The family-level routing lives in `00-syllabus.md`.)*

## ⑥ Reflex check

Prompt: *intervals → fuse overlapping ones into maximal runs (union) — move?*
Answer: *sort by start; carry the tail `cur`; `next.start ≤ cur.end` → `cur.end = max(cur.end, next.end)`; else append. `<=` because closed intervals touch-merge; end is `max` because of swallowing. Sort-by-start is what makes "compare to the last" sufficient.*
