### #31 — Count Paths With the Given XOR Value

**Link:** https://leetcode.com/problems/count-paths-with-the-given-xor-value/
**Date attempted:** 2026-06-01
**Rating:** 1550–1600 band (Phase 2 — sealed queue, deal-list #4)
**AC at:** 2026-06-01 _(self-derived, no hint)_
**Time:** 46 min — **first submission AC** (over 30-min cap)
**Status:** ✅ **CLEAN first-submission AC.** Over cap → **derivation-over-speed clause applied**
(self-derived, first sub AC, no WA, no hint → counts as a clean ownership rep).
**Pattern (debrief):** **DP » Grid (XOR-state)** · Bit · Matrix — Q2, AR 40.7%.
**Ownership milestone:** first clean `DP » Grid` rep (bucket was 0). Disguised — XOR is smuggled in as a
bounded DP dimension; the "grid-DP" label is never announced. NOT an Invariant/Reframe problem (it's a
genuine DP-table mechanism, correctly excluded from that bucket in the 83-editorial audit).

---

**Constraints that unlocked it (read first — the user led with these):**
- grid values `< 16` ⇒ XOR of any path is also `< 16` ⇒ the XOR axis is bounded to 16 states.
- `m, n ≤ 300` ⇒ `m·n ≤ 90000`; total states `m·n·16 ≈ 1.4M` ⇒ 3D DP is trivially affordable.

**Approach (own derivation):**
- State `f(i, j, x)` = number of paths from `(0,0)` to `(i,j)` whose path-XOR equals `x`.
- Transition (top-down, recursing toward the origin): to be at `(i,j)` still needing total XOR `x`,
  the predecessor must have needed `x ^ grid[i][j]` (because XOR is its own inverse):
  `f(i,j,x) = f(i-1,j, x^grid[i][j]) + f(i,j-1, x^grid[i][j])` (mod 1e9+7).
- Base: at `(0,0)`, exactly 1 path iff `grid[0][0] == x`, else 0.
- Answer: `f(m-1, n-1, k)`. (Safe: constraint `0 ≤ k < 16`, so `dp[..][k]` never overflows the 16-wide axis.)

**The crux (invertibility):** the whole solution works *only* because XOR is self-inverse — that's what
makes the backward transition `x → x ^ grid[i][j]` valid. Swap XOR for AND/OR and the model collapses
(no inverse). This is the comprehension test, not the AC.

**Solution code (attempt 1, AC) — top-down memoization:**

```java
class Solution {

    int [][][] dp;
    int MOD = 1000000007;

    public int countPathsWithXorValue(int[][] grid, int k) {
        int m = grid.length , n = grid[0].length;
        dp = new int[m][n][16];
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++)
                Arrays.fill(dp[i][j], -1);
        return helper(m-1, n-1, k, grid);
    }

    private int helper(int i, int j, int x, int[][] grid){
        if (i < 0 || j < 0) return 0;
        if (i == 0 && j == 0) return ((grid[0][0] ^ x) == 0) ? 1 : 0;
        if (dp[i][j][x] != -1) return dp[i][j][x];

        int xor = grid[i][j] ^ x;
        int up   = helper(i - 1, j, xor, grid);
        int left = helper(i, j - 1, xor, grid);
        return dp[i][j][x] = (up + left) % MOD;
    }
}
```

**Note (naming nit, not a bug):** the locals `left`/`right` in the original submission are actually the
*up* (`i-1`) and *left* (`j-1`) predecessors — renamed here for clarity. Logic was correct.

---

**Bottom-up (tabulation) variant — written directly, self-derived (AC):**

```java
class Solution {
    public int countPathsWithXorValue(int[][] grid, int k) {
        int MOD = 1000000007;
        int m = grid.length, n = grid[0].length;
        int[][][] dp = new int[m][n][16];

        for (int x = 0; x < 16; x++)              // base: only path to (0,0) is the cell itself
            if (grid[0][0] == x) dp[0][0][x] = 1;

        for (int i = 0; i < m; i++) {             // row-major = dependency order for a grid
            for (int j = 0; j < n; j++) {
                for (int x = 0; x < 16; x++) {     // 3rd loop: fill the whole 16-wide vector per cell
                    if (i == 0 && j == 0) continue;
                    int xor = grid[i][j] ^ x;       // requirement to demand from predecessors
                    if (i == 0)       dp[0][j][x] = dp[0][j-1][xor];                       // only from left
                    else if (j == 0)  dp[i][0][x] = dp[i-1][0][xor];                       // only from up
                    else              dp[i][j][x] = (dp[i-1][j][xor] + dp[i][j-1][xor]) % MOD;
                }
            }
        }
        return dp[m-1][n-1][k];
    }
}
```

**The BUP-specific skill here = iteration order, not translation.** The recurrence/state is identical to
the memo; the only new thing tabulation forces is *sweeping cells in an order where both predecessors are
already filled.* For a **grid** that's just **row-major** (top→bottom, left→right) — reflexive, which is why
"memo → BUP" felt trivial. The muscle to actually build is naming that order for the shapes where it's NOT
reflexive: **interval DP** (by increasing length), **bitmask** (by mask value), **tree** (post-order),
**digit** (position-by-position). Drill BUP directly on *those*, not on grids.

**Why bother with BUP at all (concrete payoff):** only tabulation can be **space-optimized**. This `[m][n][16]`
collapses to a rolling **two rows** `[2][n][16]` (each row needs only the row above + the cell to its left),
i.e. `O(n·16)` memory instead of `O(m·n·16)` — exactly the fix that rescues the `≤1000`-value case from
Axis 3's MLE. The memo cannot do this. So direct-BUP fluency = the ability to clear memory-tight problems.

---

**Space-optimized rolling two-row variant — THE CANONICAL FORM (target for revision):**

> ⚠️ This version was reached **with help** (tapped out on the rolling mechanic) — so it does NOT add an
> ownership rep; #31's clean rep stands on the original top-down memo first-AC. The point of recording it
> is that revision must reproduce *this* form directly, solo.

```java
class Solution {
    public int countPathsWithXorValue(int[][] grid, int k) {
        int MOD = 1000000007;
        int m = grid.length, n = grid[0].length;

        int[][] prev = null;
        for (int i = 0; i < m; i++) {
            int[][] cur = new int[n][16];            // fresh row each iteration
            for (int j = 0; j < n; j++) {
                for (int x = 0; x < 16; x++) {
                    if (i == 0 && j == 0) {           // base
                        cur[0][x] = (grid[0][0] == x) ? 1 : 0;
                        continue;
                    }
                    int xor = grid[i][j] ^ x;
                    int fromUp   = (i > 0) ? prev[j][xor]  : 0;   // row above
                    int fromLeft = (j > 0) ? cur[j-1][xor] : 0;   // same row, already filled
                    cur[j][x] = (fromUp + fromLeft) % MOD;
                }
            }
            prev = cur;                              // roll
        }
        return prev[n-1][k];
    }
}
```

Rolling mechanic = two lines: `cur = new int[n][16]` at the top of each row, `prev = cur` at the bottom.
`O(n·16)` memory. **Gotchas that bit on the first try (don't repeat):** (1) dropped the outer `for i` loop
— no `i` loop = no rolling; (2) `curr.clone()` is a *shallow* copy (inner `[16]` shared) and the wrong
model anyway — allocate fresh, don't snapshot; (3) leftover 3D names `dp[i][j][x]` → `cur[j][x]`.
Single-row in-place is unsafe here (per-cell you read index `x^g` and write index `x` → aliasing); two
rows (or a `[16]` temp per cell) is the fix.

---

## Perturbation Debrief ([[lc-perturbation-debrief]])

Worked Socratically post-AC. The AC was by *instinct* (pattern-match: grid DP → carry a dimension →
recurse to neighbors); these probes are what convert instinct into an owned model. AC is a weak signal —
the model was fragile, this problem just never perturbed it hard enough to expose the gap.

**Axis 1 — Operator (XOR → AND/OR). The load-bearing property = INVERTIBILITY, not associativity.**
- The transition recovers the requirement to hand the subproblem: full XOR to `(i,j)` = `A ^ B` where
  `A` = XOR before the cell, `B = grid[i][j]`. Need `A ^ B = K` ⇒ solve `A = K ^ B`. That solve works
  **only because XOR is its own inverse** (`B ^ B = 0`).
- Common wrong answer: "associativity." AND is *also* associative/commutative — so that can't be the
  distinguishing property. The real one is self-inverse.
- **AND / OR break it:** no inverse (once a bit is ANDed to 0 the info is gone) ⇒ `A = K ^ B` has no
  analog ⇒ DP collapses. `+ / −` would survive (subtraction is the inverse).
- **Transferable lesson:** for any "path/subset with accumulated-value == k" problem, the accumulation
  operation must be **invertible** — that, not "it's a grid," is why this works.

**Axis 2 — Meta (one-sentence restatement). Exposed a real gap.**
- First (fragile) attempt: *"expected xor at (i,j) from neighbors"* — two soft spots: "from neighbors"
  and silence on whether `grid[i][j]` is counted.
- Pinned via the base case: code fires at `(0,0)` on `x == grid[0][0]` (not `x == 0`) ⇒ `x` **includes**
  the cell. Clean sentence: **`f(i,j,x)` = number of paths from `(0,0)` to `(i,j)` whose *inclusive* XOR
  == `x`; answer = `f(m-1,n-1,k)`.**
- Tell that "running xor == k" is wrong: if `x` were always `k`, the 3rd dimension would be **constant**
  — the only reason it's a DP axis is that `x` **varies** per subproblem. `k` is just which slice you
  read at the end, not what the state means.

**Bonus insight — the convention is a free choice (two equivalent builds):**
| | Inclusive (this code) | Exclusive |
|---|---|---|
| `x` counts `grid[i][j]`? | yes | no |
| base at `(0,0)` | `x == grid[0][0]` | `x == 0` |
| top query | `f(m-1,n-1,k)` | `f(m-1,n-1, k ^ grid[m-1][n-1])` |

Consistency rule: **base case and top-level query must use the same convention.** Inclusive base + an
exclusive query (`k ^ grid[last]`) would silently disagree = the bug. This code is consistently inclusive.

**Axis 3 — Scale (why exactly `< 16`). The bound is calibrated to the laziest correct solution.**
- `16` isn't magic — it's `2^(bit-width of max value)`. XOR of values each `< 2^b` stays in `[0, 2^b)`,
  so the 3rd dimension = `2^b`. Values `< 16 = 2⁴` ⇒ 4 bits ⇒ 16 states. The single thing it sizes is the
  `[16]` axis, which multiplies into states, **memory, and time**.
- **"Couldn't it handle `≤ 1000` easily?" — No, and the trap is instructive.** Price the *submitted*
  full `int[m][n][V]` array:
  - `< 16`: `300·300·16 = 1.44M` ints ≈ **5.8 MB**. Trivial.
  - `≤ 1000` (→ `2^10 = 1024`): `300·300·1024 = 92.16M` ints ≈ **369 MB** → **MLE** (> 256 MB limit).
- **Memory breaks before time.** At `≤1000` the time is `~9·10⁷` ops (<1s, fine) — it's *memory* that
  dies first. "Handles it easily" must be checked on **both** axes; they don't fail together.
- **The first fix is implementation, not algorithm.** The *idea* survives `≤1000`; the *full-array build*
  doesn't. Dropping the `[m][n][V]` memo to a **rolling two-row bottom-up** = `2·300·1024 ≈ 0.6M` ints ≈
  **2.5 MB** → fine again. So `< 16` is precisely what lets the naive full-3D-array pass with no memory trick.
- **Transferable reflex (generalizes well beyond DP):** a suspiciously small bound on the **values**
  (not the length) is the setter saying *"make this value a state / index on it."* `values<16` → value as a
  DP axis; small range → counting/bucket/frequency-array/pigeonhole (cf. #04); tiny universe → bitmask /
  enumerate the domain. Big value bound (`10⁹`) = value **can't** be a state → greedy/math/sort/two-pointer/
  coordinate-compress. General law: **constraints are a spoiler for the method** — read them *before*
  designing; the small bound says what's *invited*, the big bound says what's *forbidden*. (See the
  `n → complexity → method` table; "answer mod 1e9+7" is itself a spoiler = you're *counting*, not optimizing.)

**Debrief takeaways (the owned model, beyond the AC):**
1. Works because XOR is **invertible** (self-inverse) — not because it's a grid, not associativity.
2. State is `f(i,j,x)` over a **varying** `x`; `k` is just the slice you read. Two equivalent conventions
   (inclusive/exclusive); base case and top query must agree.
3. `< 16` is a **memory** calibration for the full-array build; memory breaks before time; rolling array
   rescues a looser bound. Small value-bound ⇒ "make the value a state."

> **⏳ REVISION TARGET (set 2026-06-01):** solve `#31` **directly as the space-optimized rolling two-row
> BUP** — no memo crutch, no full 3D array. Must produce, cold and solo:
> 1. **Perfect state definition** — `f(i,j,x)` = #paths from `(0,0)` to `(i,j)` whose *inclusive* XOR == `x`
>    (not "running xor == k"; `k` is only the final slice read).
> 2. **Recurrence** `cur[j][x] = prev[j][x^g] + cur[j-1][x^g]` with the `(0,0)` base and row-major order.
> 3. **Rolling mechanic** clean (fresh `cur` per row, `prev = cur`), `O(n·16)` memory — without the 3
>    gotchas above (missing `i` loop / shallow clone / 3D-name leftovers).
> 4. **Re-answer the 3 perturbation axes from memory** ([[lc-perturbation-debrief]]): invertibility
>    (XOR→AND breaks), the `<16 = 2⁴` memory calibration (memory-before-time), and "small value-bound ⇒
>    make the value a state." Survive all three cold ⇒ genuinely owned.
