# Interval Atom 02 — notes

## Interval List Intersections (LC 986) — the announced rep

Two lists of closed intervals, each individually sorted and disjoint, and you want everything they share. The difficulty isn't any single overlap — it's doing it in one linear pass over *two* lists instead of comparing every pair. Two facts make the linear walk possible and they're the whole atom: (1) how to intersect one pair, (2) which pointer to advance so you never look back.

## Piece 1 — intersecting a single pair

For `A = [a1, a2]`, `B = [b1, b2]`, the overlap (if any) is:

```
lo = max(a1, b1)      // overlap starts at the later of the two starts
hi = min(a2, b2)      // overlap ends at the earlier of the two ends
```

The intuition the derivation went through: the shared region can't begin until *both* intervals have begun → the **later** start → `max`. It must end as soon as *either* one ends → the **earlier** end → `min`. (The first instinct was `min` for the start — corrected on the pair `A=[1,8]`, `B=[5,12]`: the overlap is `[5,8]`, and `5 = max(1,5)`, not `min`.)

## Piece 2 — the overlap test is `lo <= hi` (and it equals the symmetric check)

`lo`/`hi` *assume* an overlap. If the pair is actually disjoint, the formula returns a **backwards** interval. `A=[1,3]`, `B=[5,8]` → `lo = max(1,5) = 5`, `hi = min(3,8) = 3` → `[5,3]`, nonsense. So `lo <= hi` is the test "is this a real, non-empty interval?" — only then record it.

This is the *same* boundary bit as atom #1: closed intervals, so `lo == hi` (a single shared point like `[5,5]`) **counts** — `<=`, not `<`. LC 986's own output contains `[5,5]` and `[24,24]`.

**It's literally the overlap check from atom #1, generalized.** Merge used a *single* comparison `next.start ≤ cur.end` — but only because sorting by start told it which interval started first. Here the two lists are independent, so the general two-interval overlap test is *symmetric*:

```
a1 <= b2  &&  b1 <= a2          (A starts before B ends, AND B starts before A ends)
```

And that pair of conditions is algebraically identical to `lo <= hi`:

```
a1 <= b2 && b1 <= a2
⟺ both starts ≤ both ends
⟺ max(a1,b1) <= min(a2,b2)
⟺ lo <= hi
```

So computing `lo, hi` and testing `lo <= hi` does double duty — it's the overlap check *and* the answer's bounds in one shot. Writing the explicit `a1<=b2 && b1<=a2` first would be the same boolean, just without reusing the bounds you already need.

## Piece 3 — which pointer to advance (why you never look back)

After intersecting `A[i]` and `B[j]`, exactly one of them is "used up": **the one with the smaller end**. Why — say `A[i]` ends first (`a2 < b2`). Every interval later in `B` starts *after* `B[j]` (sorted, disjoint), hence after `a2`, so none of them can reach back into `A[i]`. `A[i]` is done; advance `i`. `B[j]` still has room beyond `a2`, so it stays to meet the next `A`. On a tie (`a2 == b2`) both ends are consumed, advance either. This is what turns `O(n·m)` into `O(n+m)`: a passed interval is never revisited.

## Step 2 — worked example (the swallow case)

```
A = [[1,20]]      B = [[3,5],[7,9],[11,13]]
```

| i | j | lo = max | hi = min | lo≤hi? | emit | advance (smaller end) |
|---|---|---|---|---|---|---|
| 0 | 0 | max(1,3)=3 | min(20,5)=5 | ✓ | [3,5] | `B[0].end 5 < A[0].end 20` → j++ |
| 0 | 1 | max(1,7)=7 | min(20,9)=9 | ✓ | [7,9] | `9 < 20` → j++ |
| 0 | 2 | max(1,11)=11 | min(20,13)=13 | ✓ | [11,13] | `13 < 20` → j++ |
| 0 | 3 | — | — | — | — | j out of range, loop ends |

Result `[[3,5],[7,9],[11,13]]`. `A[0]` never advances — its end 20 is always the larger, so `i` stays put while `j` sweeps all three. This is the case a naïve lockstep (advance both each step) gets wrong, and it's the reason the "advance smaller end" rule exists.

## Step 3 — edge cases

1. **Point-touch** `A=[[1,5]]`, `B=[[5,8]]` → `[[5,5]]`. `lo=hi=5`, `5<=5` ✓. Tests `<=`-not-`<`.
2. **Fully disjoint** `A=[[1,3]]`, `B=[[5,8]]` → `[]`. `lo=5 > hi=3`, skip.
3. **Empty list** `A=[]`, `B=[[1,5]]` → `[]`. `n=0` → loop never runs, no empty-array indexing.
4. **One swallowing many** (above) → tests the smaller-end advance.
5. **Equal ends** `A=[[1,5]]`, `B=[[2,5]]` → `[[2,5]]`, then `5 < 5` false → `else j++`. The tie deterministically advances `j`; correct because both ends are consumed.

## Implementation note — the output conversion

`List<int[]>` → `int[][]` was written the explicit way (allocate `int[size][2]`, copy each row) rather than `toArray(new int[0][])`, by preference, for readability. Both are equivalent; the explicit loop is clearer at a glance.

## Discriminator (vs merge, atom #1)

One pile, union the overlaps → **merge** (sort by start, carry a tail). *Two* sorted piles, keep only the shared parts → **intersection** (two pointers, `[max(starts), min(ends)]`, advance smaller end). Same closed-interval `<=` boundary in both.

> **Logging honesty:** approach **self-derived via Socratic Q&A** — the user produced the `[max(starts), min(ends)]` formula (after self-correcting an initial `min`→`max` on the start) and the "advance the smaller-end pointer" rule. The Java code was written by Claude on request and submitted. Install grade; cold recognition comes from zerotrac in the normal grind.
