## The problem

You're a thief with a knapsack that holds at most **`C` units of weight**. There are `n` items. Each item `i` has weight `w[i]` and value `v[i]`.

The defining rule of **0/1**: each item exists **exactly once**. For each item you make a binary choice — **take it** or **leave it**. No fractions, no copies.

Maximize total value carried without exceeding capacity `C`.

Concrete instance used throughout:

```
C = 5
item 0: weight 2, value 3
item 1: weight 3, value 4
item 2: weight 4, value 5
```

---

## Step 1 — the decision and the leftover problem

Stand in front of one item. The decision is binary, but it's **gated by feasibility**:

- If `w[i] <= c` (it fits): two options — **take** or **leave**.
- If `w[i] > c` (too heavy): one option — **leave** (take isn't even on the table).

After each choice, two things change — *which items remain* and *how much capacity is left*:

- **Take item `i`:** capacity drops by `w[i]`, value gained `v[i]`, move to the next item.
- **Leave item `i`:** capacity unchanged, value gained 0, move to the next item.

---

## Step 2 — define the state (in plain English first)

```
f(i, c) = best value obtainable using items 0..i, with capacity c
```

Two state variables → **2D DP**.

### Which argument moves, and how

- **`i`** decreases on **every** call (we always advance to the next item).
- **`c`** decreases **only sometimes** — exactly when we *take* — by `w[i]`.

### Convention matters: forward vs backward

The recursion direction must match how the state is phrased. Both are valid — pick one and stay consistent:

| State definition | Items it covers | Recurse toward | Base case |
|---|---|---|---|
| "items from `i` **onward**" (suffix) | `i, i+1, …, n-1` | `i → i+1` | `i == n` |
| "items `0..i`" (prefix) | `0, 1, …, i` | `i → i-1` | `i < 0` |

We commit to **prefix / backward**: `f(i, c)` = items `0..i`, recurse `i → i-1`, base `i < 0`.

---

## Step 3 — base cases

The recursion stops collecting value when either resource runs out:

- **`i < 0`** — out of items → return **0**.
- **`c == 0`** — out of capacity, nothing more fits → return **0**.

(With the feasibility gate in place, the `c == 0` case is handled implicitly — no item of weight ≥ 1 can be taken — but stating it is harmless and explicit.)

---

## The brute-force recursion

```java
// f(i, c) = best value using items 0..i, with capacity c
int f(int i, int c, int[] w, int[] v) {
    if (i < 0) return 0;              // out of items → no more value

    int skip = f(i - 1, c, w, v);    // leave item i: same capacity, move on

    int take = 0;
    if (w[i] <= c) {                 // feasibility gate (note: <=, not <)
        take = v[i] + f(i - 1, c - w[i], w, v);  // take: pay weight, gain value
    }

    return Math.max(take, skip);
}
// top-level call: f(n - 1, C, w, v)
```

`skip` is computed unconditionally; `take` only when the item fits. If it doesn't fit, `take` stays 0 and `max` falls back to `skip`.

> [!warning] The gate is `w[i] <= c`, **not** `<`. If `w[i] == c` you can still take the item and fill the bag exactly. `<` wrongly forbids that — a classic off-by-one knapsack bug.

---

## Prove it's broken — measure before optimising

Every call branches into two (`take`, `skip`), and depth is `n` (each call drops `i` by 1):

```
Time = branching ^ depth = 2^n
```

Scale feel (10⁸ ops/sec):

- `n = 30` → ~10⁹ → ~10 s
- `n = 40` → ~10¹² → ~3 hr
- `n = 50` → ~10¹⁵ → ~4 months

LeetCode knapsack constraints are routinely `n ≤ 100+`, so brute force is dead on arrival.

---

## Where the waste lives

The same `(i, c)` pair gets recomputed across different take/skip paths. Reaching capacity `c` with items `0..i` via "take A, skip B" lands on the **identical subproblem** as "skip A, take B" when weights collide — and the recursion re-solves it from scratch each time. Since `(i, c)` fully determines the answer, recomputation is pure waste.

That's the cue to memoize — cache on the **2D key `(i, c)`**.

---

## The fix — memoization

```java
int[][] memo;   // sized [n][C+1], every cell initialised to -1

int f(int i, int c, int[] w, int[] v) {
    if (i < 0) return 0;                       // base: not cached, just return

    if (memo[i][c] != -1) return memo[i][c];   // cache hit

    int skip = f(i - 1, c, w, v);

    int take = 0;
    if (w[i] <= c) {
        take = v[i] + f(i - 1, c - w[i], w, v);
    }

    return memo[i][c] = Math.max(take, skip);  // compute, store, return
}
// caller: memo = new int[n][C+1]; fill each row with -1; return f(n-1, C, w, v);
```

The recurrence, base case, and gate are **byte-for-byte the brute force**. The only additions: the sentinel array, the cache-hit check at the top, the store-on-the-way-out at the bottom.

> [!important] Why sentinel `-1`, not `0`? A knapsack answer can legitimately be `0` (take nothing). So `0` can't double as "not computed yet." Use `-1` as the sentinel for "empty cell."

---

## Complexity — and how to count subproblems

```
Time = (number of distinct subproblems) × (work per subproblem)
```

**Counting subproblems — the principle:**

> Number of distinct subproblems = number of distinct argument-tuples `f` can ever be called with = (distinct values of `i`) × (distinct values of `c`).

A "subproblem" *is* a distinct `(i, c)` pair, and memoization guarantees each is computed at most once.

- **`i`** walks `n-1, n-2, …, 0` → **`n`** distinct values (`i < 0` returns without being stored).
- **`c`** starts at `C`, only ever decreases, stays in `[0, C]` → at most **`C+1`** distinct values.

```
distinct (i, c) pairs  ≤  n × (C+1)
```

So:

```
Time  = O(n × C)
Space = O(n × C) table + O(n) recursion stack depth
```

From **O(2ⁿ)** down to **O(n·C)**. For `n=100, C=1000` ≈ 10⁵ ops — instant.

### Why "≤", not "="

`n × (C+1)` is the **full grid** = an upper bound. Whether every cell is actually reached depends on the weights (with `C=5, weights {2,3,4}`, some capacities never appear). But for complexity we want the worst-case guarantee, and we literally allocate the full `int[n][C+1]` table — so we bound by the grid. The bound is tight for adversarial inputs (e.g. all weights `= 1`, where every `c ∈ 0..C` is reachable at every `i`).

> [!important] **Pseudo-polynomial.** `O(n·C)` depends on the *magnitude* `C`, not just input size. If `C = 10⁹`, the table has ~10¹¹ cells and this approach collapses — always read `C` off the constraints before committing to it.

---

---

## Bottom-up (normal 2D table)

Bottom-up fills the same `(i, c)` table the recursion would, but with plain loops in an order where every cell's dependencies already exist — no recursion, no stack.

### Dependencies and fill order

From the recurrence, computing `dp[i][c]` needs exactly two cells:

```
dp[i-1][c]            (skip)
dp[i-1][c - w[i]]     (take, only if w[i] <= c)
```

Both live in the **previous row** `i-1`. So if we fill rows with `i` **increasing**, the entire previous row is finished before the current row starts. Dependencies always ready. ✓

### Where does the base case live?

> In recursion the base case is a **branch** (`if (i<0) return 0`). In tabulation that same base case must become **storage** — a cell/row/column of the table.

Two ways to store it (both correct):

| Convention | Table size | Base lives as |
|---|---|---|
| **Phantom row** | `[n+1][C+1]` | an all-zero row 0 = "no items"; item `i` → row `i+1` |
| **Seed row 0** | `[n][C+1]` | row 0 filled with only-item-0's answer directly |

We use **seed row 0** — it keeps the table at `[n][C+1]`, matching the memo dimensions.

### Code

```java
int[][] dp = new int[n][C + 1];

// base row: only item 0 available
for (int j = 0; j <= C; j++)
    dp[0][j] = (j >= w[0]) ? v[0] : 0;

for (int i = 1; i < n; i++) {
    for (int j = 0; j <= C; j++) {
        dp[i][j] = dp[i - 1][j];                 // skip item i
        if (w[i] <= j)                           // gate → j - w[i] safe
            dp[i][j] = Math.max(dp[i][j], v[i] + dp[i - 1][j - w[i]]);
    }
}
return dp[n - 1][C];
```

> [!warning] The same `w[i] <= j` gate from the brute force is mandatory here too — without it, `j - w[i]` goes negative and the array index throws. The gate makes the access provably safe.

### Trace

`C = 5`, items `(w,v) = (2,3), (3,4), (4,5)`:

```
          j=0  1   2   3   4   5
i=0 (2,3)  0   0   3   3   3   3
i=1 (3,4)  0   0   3   4   4   7
i=2 (4,5)  0   0   3   4   5   7
```

`dp[2][5] = 7` ✓ — take items 0 and 1 (weight 2+3=5, value 3+4=7).

### Complexity

```
Time  = O(n × C)   — every cell once, O(1) work each
Space = O(n × C)   — full table, no recursion stack
```

> [!note] The seed-row-0 convention assumes **positive weights**. A zero-weight item (takeable even at `c=0`) is handled more cleanly by the phantom-row convention. Rare corner — park it.

---

## Space optimization — O(n·C) → O(C)

Every term in the recurrence reads from **row `i-1` only** — never further back. So you don't need the whole table; you need **one row** alive at a time. Collapse the 2D table to a 1D array `dp[C+1]`, reused as `i` advances.

### Stepping stone — two arrays (`prev` / `curr`)

The honest first version keeps two separate arrays so reads can't collide with writes: read from `prev` (row `i-1`), write to `curr` (row `i`).

```java
int[] prev = new int[C + 1];
for (int j = 0; j <= C; j++)
    prev[j] = (j >= w[0]) ? v[0] : 0;          // base row: only item 0

for (int i = 1; i < n; i++) {
    int[] curr = new int[C + 1];               // fresh row each iteration
    for (int j = 0; j <= C; j++) {
        curr[j] = prev[j];                     // skip → read prev
        if (w[i] <= j)
            curr[j] = Math.max(curr[j], v[i] + prev[j - w[i]]);  // take → also prev
    }
    prev = curr;                               // row i becomes previous
}
return prev[C];
```

Because both reads come from `prev` (never written this row) and `curr` is brand-new, **the `j` direction doesn't matter here.** The direction problem only appears when we fold the two arrays into one — so this version quarantines the hard part.

> [!note] `prev = curr` here is **not** the alias trap from `2D.md`. That trap needs the *same two arrays reused* every round. Here `curr` is `new` each iteration, so `prev = curr` just retargets `prev` at a finished, independent row.
>
> ```
> Time O(n·C)   Space O(C)   (two rows = O(2C) = O(C))
> ```

### The fork — fold into ONE array, and the loop direction

Fold `prev`/`curr` into a single in-place array: `dp[j] = max(dp[j], v[i] + dp[j - w[i]])`. Now reads and writes share one array, so **direction decides correctness.** Watch one item (`w=2, v=3`), capacity 5, `dp` starting all zeros:

**LOW → HIGH (`j = 2..5`) — WRONG for 0/1:**
```
j=2:  dp[2]=max(0, 3+dp[0]=0)=3      0 0 [3] 0 0 0
j=3:  dp[3]=max(0, 3+dp[1]=0)=3      0 0  3 [3] 0 0
j=4:  dp[4]=max(0, 3+dp[2]=3)=6  ←   0 0  3  3 [6] 0     dp[2] already updated this round
j=5:  dp[5]=max(0, 3+dp[3]=3)=6  ←   0 0  3  3  6 [6]    → item used TWICE
```
Reading `dp[2]` after it was updated = reusing the same item → that's **unbounded** behaviour, a bug for 0/1.

**HIGH → LOW (`j = 5..2`) — CORRECT for 0/1:**
```
j=5:  dp[5]=max(0, 3+dp[3]=0)=3      0 0 0 0 0 [3]
j=4:  dp[4]=max(0, 3+dp[2]=0)=3      0 0 0 0 [3] 3
j=3:  dp[3]=max(0, 3+dp[1]=0)=3      0 0 0 [3] 3 3
j=2:  dp[2]=max(0, 3+dp[0]=0)=3      0 0 [3] 3 3 3
```
Every smaller index `j - w[i]` is still **untouched = the old (row `i-1`) value** when read → item used at most once.

> [!important] Sweeping `j` **high → low** keeps each `dp[j - w[i]]` at its previous-row value at read time — the single array *simulates* reading from `prev`. **0/1 knapsack ⇒ iterate capacity downward.** (Iterating upward is exactly what unbounded knapsack wants — next file.)

### Final 1D code (canonical 0/1 form)

```java
int[] dp = new int[C + 1];            // all zeros = no items used yet

for (int i = 0; i < n; i++) {
    for (int j = C; j >= w[i]; j--) { // HIGH → LOW; j >= w[i] is the feasibility gate
        dp[j] = Math.max(dp[j], v[i] + dp[j - w[i]]);
    }
}
return dp[C];
```

```
Time  = O(n × C)
Space = O(C)
```

### Why no `array.clone()`?

`clone()` only matters when **two arrays** might alias. Here there is **one** array, so there's nothing to copy.

| Version | Arrays alive | clone needed? |
|---|---|---|
| Two-array `prev`/`curr` | 2 | No — `new` each round dodges aliasing |
| Single-array (downward) | 1 | **N/A — nothing to alias with** |

The work the separate `prev` array used to do — supply the previous row's value at `dp[j - w[i]]` — is now done entirely by the **downward sweep**. You'd only reach for `clone()` if you kept `prev`/`curr` as two arrays *and reused them* across iterations (then `prev = curr` aliases and corrupts — the `2D.md` trap). One array + downward sweep removes both the second array and the copy.

> [!tip] One array + downward sweep is the canonical 0/1 knapsack form: O(C) space, half the memory of two-array, zero copy cost.

---

> **Next file (`unbounded.md`):** same single array, but sweep capacity **upward** — letting `dp[j - w[i]]` read the *already-updated* (current-row) value is precisely "use this item again." The whole 0/1 → unbounded delta is one loop direction.
