# 12 — Minimum Number of Seconds to Make Mountain Height Zero

- **Link:** https://leetcode.com/problems/minimum-number-of-seconds-to-make-mountain-height-zero/
- **Band:** 1600–1699 · sealed queue · blind deal #12 · Q2 (AR 58.3%) · **answer-key bucket = Binary-Search on answer**
- **Bucket (OUR code):** **Heap** — greedy "assign each unit of height to the worker with the smallest resulting cumulative time." Credited by mechanic-in-code, not the answer-key label [[lc-credit-mechanic-not-label]]. (User deliberately chose heap first; knows the BS route — that's the owed cold re-solve.)
- **Dealt:** 2026-06-13 (solved in-head on a walk, typed submissions after)
- **AC:** 2026-06-13 (**self-derived, no hints**) — but **2× WA before AC**.
- **Result (Heap route):** ⚠️ **SOFT FAIL — WA-then-AC (×2), self-derived.** Per rule 6A a WA resets the rep → **no ownership credit; Heap stays 1/2.** Clean-rate now **8/11 (73%)**.
- **Result (Binary-Search route, attempted 2026-06-15):** ❌ **HARD FAIL — could not self-derive; full code provided (editorial).** Got the BS skeleton + `high` bound right (AP sum `n/2·[2a+(n-1)d]` with `a=d=maxTime`), but **stalled on the `helper` feasibility function** (the §3.11 inverse-triangular: max `k` with `wt·k(k+1)/2 ≤ T`) and had multiple compile/precedence bugs. Conceptual lever given first, then full code on request. **Binary-Search debt stays 0/2 — NOT closed.** This is exactly the carried BS debt; it's still owed clean cross-band.

---

## The problem
`mountainHeight`, and `workerTimes[i]`. A worker with time `wt` reducing the height by `x` (total, that worker) costs `wt·(1+2+…+x) = wt·x(x+1)/2` seconds. All workers act **in parallel**; the sum of all workers' `x` must equal `mountainHeight`. The total time is the **max** over workers of their individual time. **Minimize** that max.

## Approach (self-derived) — heap, assign one unit at a time to the cheapest-next worker
- Each "unit" of height assigned to a worker is its next increment. A worker that has already done `k` units and takes one more (its `(k+1)`-th) pays an **extra** `wt·(k+1)`, bringing its cumulative to `wt·(k+1)(k+2)/2`.
- Greedy: keep each worker's **cumulative time** in a min-heap keyed by *what its cumulative becomes after one more unit*. Pop the cheapest, give it the unit, push it back with the updated cumulative. Do this `mountainHeight` times.
- Answer = the **max** cumulative ever realized (the last/biggest pop). Each pop sets `ans = max(ans, cumulative)`.

## The two WAs (self-derived debugging)
**WA #1 — wrong heap priority key.**
```java
new PriorityQueue<>((a,b) -> Long.compare(a[0]*a[1], b[0]*b[1]));  // keys on t·k
```
`t·k` is neither the cumulative (`t·k(k+1)/2`) nor the next-marginal cost (`t·(k+1)`). The heap popped the wrong worker → over-assigned. `[1,7]`, h=5 → got **15**, expected **10**.
> **WA-cause [wrong-comparator/priority-key]:** ordered the heap by an expression that isn't the quantity being minimized. The key must be the *next cumulative time*, the thing the answer is a max over.

**WA #2 — stored aggregate desynced from its count.**
Stored `{t, k, sum}` and keyed on `sum`, but on push did `{t, k+1, sum}` while `sum` was recomputed from the **old** `n = k` (`sum = n*(t+t*n)/2`) — so the cumulative lagged the count by one step, and the pushed priority was stale. `[1,5]`, h=5 → still **15**.
> **WA-cause [stale-derived-field]:** a record carried both a count `k` and a value `sum` derived from it, and `k` was advanced without recomputing/advancing `sum` in lockstep. Classic [[lc-index-bookkeeping-overmodel]]-adjacent bug: store the aggregate *incrementally*, never recompute it from a count you're mutating separately.

## The fix (AC) — carry cumulative incrementally
`nextSum = sum + (k+1)*t` — one multiply, always in lockstep with `k`. No closed-form recompute, no desync.

## Step 2 — worked example reproduced (`[1,7]`, h=5, expected 10)
Heap entries `{wt, unitsDone, cumulativeAfterThoseUnits}`; pop min cumulative, `ans=max`, push next.

| pop | entry popped | ans | pushed back |
|---|---|---|---|
| 1 | {1,1,**1**} | 1 | {1,2,3} |
| 2 | {1,2,**3**} | 3 | {1,3,6} |
| 3 | {1,3,**6**} | 6 | {1,4,10} |
| 4 | {7,1,**7**} | 7 | {7,2,21} |
| 5 | {1,4,**10**} | 10 | {1,5,15} |

5 pops (= height). `ans = 10`. ✅ Worker0 did 4 units (cost 10), worker1 did 1 (cost 7), max = 10 — matches.

## Step 3 — named edge cases
1. **Overflow** — `mountainHeight ≤ 1e5`, `wt ≤ 1e6`. Cumulative ~ `wt·h²/2` ≈ `1e6·1e10/2` ≈ `5e15` ≫ `int`. Everything `long` (the WA-free version keeps `t`, `k`, `sum` all `long`).
2. **Single worker** — all `mountainHeight` units go to it; cumulative = `wt·h(h+1)/2`. Heap still works (one entry, popped repeatedly).
3. **Equal worker times** — heap distributes round-robin; answer balanced across them.
4. **One very slow worker** — its first unit's `wt` may exceed several units of a fast worker; the heap naturally starves it (never popped if its next cumulative stays largest).
5. **Priority-key correctness** — must key on *next cumulative*, not marginal or `t·k` (the WA#1 trap).

## As-submitted solution (AC)
```java
class Solution {
    public long minNumberOfSeconds(int mountainHeight, int[] workerTimes) {
        PriorityQueue<long[]> pq =
            new PriorityQueue<>((a, b) -> Long.compare(a[2], b[2]));   // key: cumulative
        for (int t : workerTimes) pq.offer(new long[]{t, 1, t});       // {wt, nextUnits=1, cumulativeIfDoes1=t}
        long ans = 0;
        while (mountainHeight-- > 0) {
            long[] cur = pq.poll();
            long t = cur[0], k = cur[1], sum = cur[2];
            ans = Math.max(ans, sum);
            long nextSum = sum + (k + 1) * t;       // incremental — stays in lockstep with k
            pq.offer(new long[]{t, k + 1, nextSum});
        }
        return ans;
    }
}
```
- Time `O(mountainHeight · log W)`, `W` = #workers.
- Heap **is** load-bearing here (the greedy correctness rests on always extending the cheapest cumulative).

## Binary-Search route — attempted 2026-06-15, HARD FAIL (editorial), code below
- Monotone: if total time budget `T` suffices, any larger `T` also suffices.
- For a worker `wt` in budget `T`: max units `k` with `wt·k(k+1)/2 ≤ T` — §3.11 inverse-triangular (inner BS, or the quadratic). Sum `k` over workers; feasible iff `Σk ≥ mountainHeight`.
- Outer BS `T ∈ [1, maxTime·h(h+1)/2]`. **Traps:** overflow in `wt·k(k+1)/2` and in `high` (cast `long` before multiply); float-sqrt if using the closed form (§3.5) — inner BS sidesteps it.
- **What actually broke (why it's a hard fail):** the BS skeleton + `high` bound came out fine, but the **`helper` feasibility never got written self-derived** — couldn't reach "ask each worker independently: max units in budget `T`." Full code was provided. **BS debt NOT closed, stays 0/2.**

```java
class Solution {
    private boolean helper(long budget, int mountainHeight, int[] workerTimes) {
        long total = 0;
        for (int wt : workerTimes) {
            long lo = 0, hi = mountainHeight, best = 0;
            while (lo <= hi) {
                long k = lo + ((hi - lo) >> 1);
                if ((long) wt * k * (k + 1) / 2 <= budget) { best = k; lo = k + 1; }
                else hi = k - 1;
            }
            total += best;
            if (total >= mountainHeight) return true;
        }
        return total >= mountainHeight;
    }
    public long minNumberOfSeconds(int mountainHeight, int[] workerTimes) {
        int maxTime = 0;
        for (int t : workerTimes) maxTime = Math.max(t, maxTime);
        long low = 1, high = (long) maxTime * mountainHeight * (mountainHeight + 1) / 2;
        long ans = high;
        while (low <= high) {
            long mid = low + ((high - low) >> 1);
            if (helper(mid, mountainHeight, workerTimes)) { ans = mid; high = mid - 1; }
            else low = mid + 1;
        }
        return ans;
    }
}
```

## ⚠️ Recurring bug banked — shift binds LOOSER than `+`/`-` (Java precedence)
The midpoint `low + (high - low) >> 1` is a **trap**: `>>`/`<<`/`&`/`|`/`^` all sit **below** `+`/`-` in Java's precedence table (opposite of most people's intuition). So:
- `low + (high - low) >> 1`  parses as  `(low + high - low) >> 1` = `high >> 1` = **`high/2`** (wrong — the `low` cancels).
- Correct: **`low + ((high - low) >> 1)`** — parenthesize the shift so it halves the *range* before adding `low` back.
- Numeric check `low=4, hi=10`: correct → `4 + (6>>1) = 7` ✓; wrong → `10>>1 = 5` ✗.
- **Rule:** whenever `+`/`-` is mixed with a shift/bitwise op, parenthesize the bitwise part. (Only `*`/`/`/`%` bind *tighter* than `+`, so `low + (high-low)/2` is safe without the inner parens — but the shift form is not.) This bit the outer `mid` AND was the question on the inner BS — bank it on the pre-submit checklist.

## Lesson
- **"Minimize the max cost when work is split in parallel, each extra unit costs more" → heap of cumulative costs, repeatedly extend the cheapest** (or binary-search the answer). Both are standard; pick heap when increments are cheap to compute, BS when the per-budget feasibility count is.
- **Two recurring bookkeeping bugs surfaced — both pre-submit-checklist items:** (1) the heap key must literally be *the quantity you're optimizing*, computed for the *next* state; (2) never store a derived aggregate beside the count it depends on and advance them separately — carry the aggregate **incrementally**.
- **Step-3's overflow note was right; the WAs were not overflow** — they were modeling/bookkeeping. Step-2 on `[1,7]` *would* have caught WA#1 before submit (the table desyncs immediately) — running it pre-submit is the fix.

## PENDING
- **Cold re-solve (owed — soft fail on Heap + hard fail on BS):** redo the **Binary-Search-on-answer** version COLD and self-derived → only THEN does BS debt 0/2 → 1/2. The whole feasibility-reframe ("each worker independently, max units in budget T = §3.11 inverse-triangular") is the thing to make reflexive. [[lc-cold-resolve-scope]]
- **Day+14 revision:** reproduce the heap version cleanly (key on cumulative, incremental update) AND the BS version cold. [[lc-revise-to-cleanest-form]]
- **Perturbation debrief** — PENDING, work Socratically first [[lc-perturbation-before-write]] (candidate probe: cost grows *linearly* per unit `wt·x` instead of triangular `wt·x(x+1)/2` — does heap-greedy still hold? does it collapse to a simpler formula?).
