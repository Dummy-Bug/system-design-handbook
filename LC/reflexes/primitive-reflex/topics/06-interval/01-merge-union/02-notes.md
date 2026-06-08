# Interval Atom 01 — notes

## Merge Intervals (LC 56) — the announced rep

Given a list of intervals `[start, end]`, return the smallest list covering exactly the same points — every group of overlapping intervals fused into one. `[[1,3],[2,6],[8,10],[15,18]]` → `[[1,6],[8,10],[15,18]]`. The defining difficulty isn't the fuse rule (that part is one comparison) — it's that **two intervals that should merge can sit anywhere in the input**, arbitrarily far apart, possibly chaining through a third (`[1,4]`,`[3,8]`,`[7,10]` all collapse to `[1,10]` even though `[1,4]` and `[7,10]` don't touch directly). The whole atom is about turning "every interval can interact with every other" into "every interval only interacts with the one next to it."

### The dead end (worth keeping — it's what motivates the sort)

The tempting move: one left-to-right pass, fuse each interval into the previous if `next.start ≤ prev.end`. On the *already-sorted* example it works perfectly, which is exactly the trap — it looks complete. Then run the **same set, shuffled**: `[[8,10],[1,3],[15,18],[2,6]]`.

| compare | `next.start ≤ prev.end`? | result |
|---|---|---|
| `[1,3]` vs `[8,10]` | `1 ≤ 10`… but `[1,3]` ends at 3, before 8 — no real overlap | no fuse |
| `[15,18]` vs `[1,3]` | `15 ≤ 3`? no | no fuse |
| `[2,6]` vs `[15,18]` | `2 ≤ 18`? the test passes but they don't overlap | bogus |

The single comparison "am I glued to the *one* before me?" is only meaningful if the interval before me is the one most likely to glue — i.e. the closest-starting one seen so far. In unsorted order the "previous" is just whoever happened to be adjacent in the array, which is noise. `[1,3]` and `[2,6]` — the genuine merge — are never even compared.

### Deriving it by breaking the simpler tool

The fix isn't a cleverer comparison, it's removing the disorder. **Sort by `start`.** Now a structural guarantee kicks in: after sorting, if interval `i` overlaps *any* earlier interval, it overlaps the **running merged tail** specifically. Why — every earlier interval starts at or before `i`, so the only way `i` can reach back into any of them is to reach into the one whose end stretches furthest, and that furthest end is exactly what the merged tail carries. So the entire history collapses into a single interval you compare against: the tail. "Compare against all previous" becomes "compare against the last." That collapse is the only thing sorting buys — but it's everything; it's what makes a one-variable sweep correct.

This is the scale argument too: naive all-pairs overlap is `O(n²)` (at `n = 10⁵`, 10¹⁰ ops — TLE); sort + single sweep is `O(n log n)`.

### The move, and the two pieces people drop

Sort by start. Carry the current run `cur` = the tail of the output list. For each next interval:

- `next.start ≤ cur.end` → touch/overlap → **extend in place**: `cur.end = max(cur.end, next.end)`.
- else → disjoint → **flush**: append `next` as the new `cur`.

**Drop #1 — the fused end is `max`, not `next.end`.** Counterexample `[1,8]`+`[2,5]`: they overlap (`2 ≤ 8`), but `[2,5]` sits *inside* `[1,8]`. Taking `next.end` would shrink the run to `[1,5]`, silently dropping coverage. The earlier interval *swallows* the later one → `max(cur.end, next.end)` = `[1,8]`.

**Drop #2 — `cur.start` never changes.** Sorted by start, the earlier start always wins, so only `cur.end` ever moves. (This also means the start-tie tiebreak is irrelevant: `[1,2]`,`[1,5]` in either order → `[1,5]`, because `max` absorbs the order. Merge needs no secondary sort key — *unlike* some sibling atoms that do.)

```java
Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));   // NOT a[0]-b[0]
List<int[]> out = new ArrayList<>();
out.add(intervals[0].clone());
for (int i = 1; i < intervals.length; i++) {
    int[] cur = out.get(out.size() - 1);          // same array ref held in the list
    if (intervals[i][0] <= cur[1])
        cur[1] = Math.max(cur[1], intervals[i][1]);// mutate the tail in place
    else
        out.add(intervals[i].clone());
}
return out.toArray(new int[0][]);
```

### Step 2 — worked example `[[1,4],[3,8],[7,10],[15,18]]` (the chaining case)

After sort (already sorted here). `cur` = the current tail.

| next | `start ≤ cur.end`? | action | output so far |
|---|---|---|---|
| `[1,4]` | — (seed) | `cur = [1,4]` | `[1,4]` |
| `[3,8]` | `3 ≤ 4` ✓ | `cur.end = max(4,8) = 8` | `[1,8]` |
| `[7,10]` | `7 ≤ 8` ✓ | `cur.end = max(8,10) = 10` | `[1,10]` |
| `[15,18]` | `15 ≤ 10`? ✗ | flush, new `cur = [15,18]` | `[1,10]`, `[15,18]` |

Result `[[1,10],[15,18]]`. Note `[1,4]` and `[7,10]` never touch directly — the merge chains through `[3,8]`, and the running `cur.end` is what carries the reach forward. This is the case the dead-end one-pass could never get right.

### Step 3 — edge cases

1. **Single interval** `[[5,7]]` → `[[5,7]]` — seeds `cur`, loop never runs.
2. **Touching at a point** `[[1,5],[5,10]]` → `[[1,10]]` — `5 ≤ 5` fuses (closed intervals; see below). This is the `<=`-not-`<` case.
3. **Full containment** `[[1,10],[2,3],[4,5]]` → `[[1,10]]` — each inner interval is swallowed; `max` keeps `cur.end = 10`.
4. **All disjoint** `[[1,2],[3,4],[5,6]]` → unchanged — every comparison fails, every interval flushes.
5. **Reverse-sorted input** `[[8,10],[1,5]]` → sort fixes order first → `[[1,5],[8,10]]`; without the sort this is the dead-end failure.

## The insight — "which endpoint do I sort by?" and the load-bearing `<=`

The family's one question is never "what algorithm?" but **"which endpoint do I sort by?"** Merge/union is the **sort-by-start** answer: *start → combine*. That single choice (plus the `max` fold) is the whole atom.

The other load-bearing specific is the `=` in `<=`. Perturb it to strict `<`: now `[1,5]`,`[5,10]` — which touch at the point 5 — stop merging and come back as two intervals instead of `[1,10]`. That input is **legal**, so the `=` is real work, not decoration. What it encodes: **the problem treats endpoint-touching as overlap** — intervals are *closed*, they include both ends, so sharing one point is enough to fuse.

### Why that bit is family-wide, not a one-card fact

"Does endpoint-touch count as overlap?" reappears in every interval atom, just re-dressed:

- **Sweep-line concurrency** (sibling atom, not yet installed): does a meeting *ending* at `t` clash with one *starting* at `t`? If a room frees instantly (touch is OK), you must process the `−1` event *before* the `+1` at equal time, or concurrency spuriously spikes. Same decision, expressed as event tie-ordering.
- **Greedy scheduling** (sibling atom, not yet installed): "non-overlapping" — does `end == start` count as a conflict? It flips keep-vs-drop on the next interval.

So the reflex this atom installs is bigger than merge itself: **on any interval problem, first pin down whether endpoint-touch counts as overlap.** That one bit decides `<` vs `<=` here, and event tie-ordering in sweep-line. Read the statement and examples for it before writing the condition.

## Implementation cleanups (from the AC)

- **`(a,b) -> a[0] - b[0]` is a comparator-overflow trap.** Safe on LC 56 (small, non-negative), but the subtraction overflows the instant the two keys straddle the int range, silently flipping order. `Integer.compare(a[0], b[0])` is the reflex — then constraints never need rechecking. (Filed under `02-syntax/`, not math-reflex: it's a Java-idiom trap with no number to recall, unlike the value-arithmetic overflow cards.)
- **No remove-then-re-add.** The tail array from `out.get(size-1)` is the *same reference* in the list; mutate `cur[1]` directly. The first solve did `remove + new int[]{...} + add` — ~4 lines of churn for one in-place assignment.

## Perturbation findings — the one specific that varies

The skeleton (sort by start, carry the tail, extend-or-flush) is fixed; the load-bearing specific is **whether touch counts as overlap** → `<=` vs `<`. Closed intervals (LC 56) → `<=`. A "strictly overlapping" variant would flip to `<`. Everything else about the atom is invariant.

> **Logging honesty:** the announced rep was **fully self-derived** (by-hand answer, fuse condition, `max` end via the swallow case, sort necessity via the shuffled-set break, start-tie irrelevance) with **no hints and no wrong attempts**, scaffolded by Socratic questioning → install grade. Cold recognition isn't drilled via a reserved blind deal — zerotrac throws plenty of disguised interval problems (Partition Labels, free-time, etc.) in the normal grind, which is where the recognition muscle gets exercised.
