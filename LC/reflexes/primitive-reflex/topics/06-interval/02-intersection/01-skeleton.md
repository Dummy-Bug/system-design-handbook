# Interval Atom 02 — Intersection (two lists)

*2026-06-07*

## The problem (Interval List Intersections, LC 986)

Two lists `A`, `B` of closed intervals, **each already pairwise-disjoint and sorted by start**. Return every interval that lies in *both* — the intersection of the two lists.

```
A = [[0,2],[5,10],[13,23],[24,25]]
B = [[1,5],[8,12],[15,24],[25,26]]
→ [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]
```

## ① Trigger

**Two** sorted lists of intervals, asked for what they share — "intersection", "common free time", "where both are busy/available". The tell that separates this from merge (atom #1): merge takes *one* pile and unions it; intersection takes *two* sorted piles and walks them together. Output intervals are each `⊆` an input interval from *each* list.

## ② Motivation — why two pointers (break the simpler tool)

The brute force: for every interval in `A`, test it against every interval in `B`, emit the overlaps. Correct, but `O(n·m)` — at `n = m = 10⁴` that's 10⁸ comparisons. The waste is that both lists are **sorted**, so once an `A`-interval ends before a `B`-interval starts, that `A`-interval is finished forever — no later `B` can reach back. A two-pointer walk exploits exactly that: never re-examine an interval you've passed. `O(n + m)`.

## ③ The move

Two pointers `i, j`. At each step, intersect the *current* pair and advance the one that's used up:

- **intersect** `A[i]` and `B[j]`: `lo = max(starts)`, `hi = min(ends)`. Keep `[lo, hi]` only if `lo <= hi` (else they don't overlap — `lo <= hi` *is* the overlap test, see notes).
- **advance** the pointer whose interval has the **smaller end** — it can't intersect anything later in the other list. On a tie, advance either (both ends are consumed).

```java
List<int[]> out = new ArrayList<>();
int i = 0, j = 0, n = firstList.length, m = secondList.length;
while (i < n && j < m) {
    int lo = Math.max(firstList[i][0], secondList[j][0]);
    int hi = Math.min(firstList[i][1], secondList[j][1]);
    if (lo <= hi) out.add(new int[]{lo, hi});
    if (firstList[i][1] < secondList[j][1]) i++;
    else j++;
}
```

## ④ Costumes

- Interval List Intersections (986) — the bare statement.
- Meeting Scheduler (1229) — *disguised*: walk two people's sorted slot lists, the answer is the first intersection of length `≥ duration`.
- Any "where are both X simultaneously" over two sorted timelines.

## ⑤ Reflex check

Prompt: *two sorted interval lists → what's common to both — move?*
Answer: *two pointers. intersect current pair = `[max(starts), min(ends)]`, keep if `lo ≤ hi`; advance the pointer with the smaller end. O(n+m) because sorted — a passed interval never comes back.*
