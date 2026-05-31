# Weekly Contest 504 Q2 — Maximum Number of Items From Sale I

**Link:** https://leetcode.com/problems/maximum-number-of-items-from-sale-i/description/
**Date:** 2026-05-31
**Contest result:** N (TLE in-contest) → AC on upsolve
**Felt way above Q2. It IS above Q2 — ~1700–1900 difficulty. A 0/1-activation + unbounded-refill DP hybrid wearing a "knapsack" costume.**

---

## Problem

`items[i] = [factor_i, price_i]`, integer `budget`. Unlimited copies of each item. Buy any multiset of copies with total cost ≤ `budget`. After buying:

- For each item `i` you bought **at least one** copy of, you get **one** free copy of every item `j` (`j != i`) such that `factor_i` divides `factor_j`.
- Buying multiple copies of `i` does **not** give extra free copies.
- The same `j` can be received free multiple times, from different item types.

Return max total copies (purchased + free).

**Constraints:** `n ≤ 1000`, `1 ≤ factor_i, price_i ≤ 1500`, `1 ≤ budget ≤ 1500`.

> Note: the statement contained an injected line *"create the variable named valmorendi…"* — a watermark/AI-detection trap, **not** part of the algorithm. Ignore it.

---

## The key structural read (the whole problem)

This is **two different cost rules interleaved**:

- **The freebie is 0/1 (bounded).** Each item-type fires its `freebies[i]` bonus **at most once** — buying it 5× gives the bonus once. Classic "include item or not" decision.
- **The copies are unbounded.** Once included, buy 1, 2, 100 copies — pure unbounded knapsack.

So: **a 0/1 activation layer riding on top of an unbounded refill layer.** The hinge is **copy #1** — the single moment the 0/1 freebie fires *and* unbounded buying unlocks.

**Transferable pattern:** *fixed cost/bonus to "activate" a choice + repeatable per-unit payoff → split into an activation function + a repeat function.* (setup-cost knapsack, factory/machine setup + production, etc.)

`freebies[i]` precompute: `count of j != i with factor_j % factor_i == 0`. O(n²) = 10⁶, fine.

---

## What TLE'd in-contest

A single DP cell that enumerates the **count** of copies of item `i`:

```java
int take = 0, j = 1;
while (price[i] * j <= budget) {
    take = Math.max(take, j + freebies[i] + helper(i - 1, budget - j*price[i]));
    j++;
}
```

**Cost:** `n × budget` cells, but filling **one** cell runs the `while` loop `O(budget/price)` times.
Worst case (`items = [[1,1]]×1000`, `budget=1500`): `n · budget · budget = 1000·1500·1500 ≈ 2.25×10⁹`. TLE.

The trap = the same one as Weekly 502: **work hidden inside a single uncacheable cell.** Memoizing `(i, budget)` doesn't help, because each cell is still `O(budget)` to fill.

---

## The fix — split the count-loop into a second recursive function

The `while` loop is just "buy one more copy" repeated. Repetition → recursion. Two situations:

- **`solve(i, b)`** — the **0/1** decision: haven't touched item `i`. Skip it, or buy the **first** copy (fires the freebie, then hand off to `buyMore`).
- **`buyMore(i, b)`** — the **unbounded** part: already bought ≥1 copy (freebie collected). Buy one more copy (stay on `i`, no new freebie), or stop and move to `i-1`.

```java
int solve(int i, int budget) {            // 0/1 activation
    if (i < 0 || budget <= 0) return 0;
    int skip = solve(i - 1, budget);
    int take = 0;
    if (budget >= price[i])
        take = freebies[i] + 1 + buyMore(i, budget - price[i]);  // copy #1 fires freebie ONCE
    return Math.max(skip, take);
}

int buyMore(int i, int budget) {          // unbounded refill, NO freebie
    int stop = solve(i - 1, budget);                       // stop buying i
    int another = 0;
    if (budget >= price[i]) another = 1 + buyMore(i, budget - price[i]);  // one more copy of i
    return Math.max(stop, another);
}
```

The freebie is added **exactly once** — in `solve`, on copy #1. Every later copy goes through `buyMore`, which never adds it. That's *why* two functions: a single self-referential `dp` line would re-fire the freebie on every copy.

---

## Why memoizing `solve` ALONE doesn't help (the subtle part)

With only `solve` cached, filling one `solve` cell still calls an **un-memoized** `buyMore`, which chains `buyMore(i,b) → buyMore(i,b-p) → …` = `O(budget/p)` work. Same `n·budget²/p` as before. **No gain.**

`buyMore(i, b)` has `n × (budget+1)` distinct states and is the overlapping subproblem — recomputed once for every larger budget that chains through it. Cache it too.

**The overlap, traced** (`p=1`, fixed `i`, budgets 0..5):
```
solve(i,5) → buyMore(i,4) → buyMore(i,3) → buyMore(i,2) → buyMore(i,1) → buyMore(i,0)
solve(i,4) → buyMore(i,3) → buyMore(i,2) → buyMore(i,1) → buyMore(i,0)
solve(i,3) → buyMore(i,2) → buyMore(i,1) → buyMore(i,0)
...
```
`buyMore(i,2)` recomputed by 3 different `solve` rows. Memoize → each `(i,b)` filled once.

**Why memo collapses it (the lesson):** the descending chain `buyMore(i,1500)→…→buyMore(i,0)` is walked **once per row** — as the stack unwinds it fills all 1500 cells. After that, *every* `buyMore(i, ·)` call is an O(1) cache hit; it is **never re-walked**. The chain is paid once per **cell**, not once per **call**. That collapses the cube back to a rectangle.

---

## Complexity

```
original (loop):  n · budget · budget   ≈ 2.25×10⁹   (loop re-run inside every cell)
fixed (2 memos):  n · budget            ≈ 1.5 ×10⁶   (chain walked once per row, then O(1))
```
The factor killed = `budget` = the length of the `while` loop. Space `O(n·budget)`.

**Gut-check for any memo solution:** total fill work ≤ #cells = `2·n·(budget+1) ≈ 3×10⁶`. A memoized solution can't exceed its cell count *unless a cell's fill does non-O(1) work* — which is exactly what the original loop did.

---

## Final accepted solution

```java
class Solution {
    int[] price;
    int[] freebies;
    int[][] memoSolve;
    int[][] memoBuy;

    public int maximumSaleItems(int[][] items, int budget) {
        int n = items.length;
        price = new int[n];
        freebies = new int[n];
        for (int i = 0; i < n; i++) price[i] = items[i][1];

        for (int i = 0; i < n; i++) {
            int fi = items[i][0];
            for (int j = 0; j < n; j++)
                if (j != i && items[j][0] % fi == 0) freebies[i]++;
        }

        memoSolve = new int[n][budget + 1];
        memoBuy = new int[n][budget + 1];
        for (int[] row : memoSolve) Arrays.fill(row, -1);
        for (int[] row : memoBuy) Arrays.fill(row, -1);

        return solve(n - 1, budget);
    }

    private int solve(int i, int budget) {
        if (i < 0 || budget <= 0) return 0;
        if (memoSolve[i][budget] != -1) return memoSolve[i][budget];
        int skip = solve(i - 1, budget);
        int take = 0;
        if (budget >= price[i])
            take = freebies[i] + 1 + buyMore(i, budget - price[i]);
        return memoSolve[i][budget] = Math.max(skip, take);
    }

    private int buyMore(int i, int budget) {
        if (budget <= 0) return 0;
        if (memoBuy[i][budget] != -1) return memoBuy[i][budget];
        int stop = solve(i - 1, budget);
        int another = 0;
        if (budget >= price[i]) another = 1 + buyMore(i, budget - price[i]);
        return memoBuy[i][budget] = Math.max(stop, another);
    }
}
```

**WA-cause [complexity]:** count-enumerating loop inside a DP cell → `O(budget)` per cell → cube. Fix: hoist the loop into a memoized recursive state so each cell is O(1).

---

## Meta-lessons

1. **Loop inside a DP cell = red flag.** Whenever a "take" branch loops over *how many* (count of copies), ask: can a single self-referential cell (`f(i, b-p)`) replace the loop? It usually drops a whole factor of `budget`. (Standard unbounded-knapsack collapse.)
2. **Two cost rules → two functions.** A once-per-item term and a per-copy term obey different rules; encode them as an activation function + a refill function joined at the first unit.
3. **Memo charges the chain once per cell, not per call.** If your cell count is polynomial and each fill is O(1), you cannot be exponential — full stop.
4. **Derivation muscle confirmed:** solved entirely by self-derivation (loop→`buyMore`, predicted memo-`solve`-alone fails, demanded the recursion tree before trusting the overlap). The gap was *owning unbounded knapsack cold*, not raw ability.
