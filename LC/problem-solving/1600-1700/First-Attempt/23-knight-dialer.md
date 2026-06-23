# 23 — Knight Dialer

- **Link:** https://leetcode.com/problems/knight-dialer/
- **Dealt:** 2026-06-23 (replenishment deal #24)
- **Result:** ✅ **CLEAN first-submission AC, self-derived, ~50m OVER-CAP** → derivation clause
- **Bucket (credit by our code):** **DP » Linear** → **0/2 → 1/2**
- **AR / slot:** 61.9% / Q2

## Clean-status note
No WA. Brute-force first draft (void recursion accumulating a global) **failed on LC "Run" sample test 3**
(large `n` timeout) — this is pre-submit dev feedback, **not a submission**. User self-diagnosed "needs DP",
converted to memoized return-value recursion, and the **first SUBMISSION was the AC**. Self-derived, no hint
(Claude stayed silent through the stuck period + break). 50m > 30m cap → **derivation-over-speed clause** →
counts as a clean ownership rep.

## The leap (reusable DP reflex)
Stuck version: `void helper(...)` mutating a global `ans` = brute-force recursion, **exponential**, and the
declared `dp` was unusable (nothing to cache — no return value).
Fix = the core DP conversion:
> **Make the recursion RETURN the subanswer over a cacheable state, then memoize on its arguments.**
Once `helper(num, target)` returns "ways from this state", state `(num, target)` has a value → memoize →
`O(10·n)`. State space = `10 digits × n jumps`.

```java
private long helper(int num, int target) {
    if (target == 0) return 1L;
    if (dp[num][target] != -1) return dp[num][target];
    long count = 0L;
    for (int next : map.get(num)) count = (count + helper(next, target - 1)) % MOD;
    return dp[num][target] = count;
}
// answer = Σ_{d=0..9} helper(d, n-1)
```
Adjacency = knight moves on the phone pad; `5` has no moves (dead start beyond n=1).

## Step 2 / Step 3 (retroactive — solve was clean)
- **Worked example:** `n=1` → every start has `target=0` → returns 1 → `ans=10` ✓. `n=2` → from each digit, count of neighbors, summed = 20.
- **Edges:** `n=1` (no jumps, answer 10); digit `5` contributes only at `n=1`; mod each accumulation; `long` to avoid overflow before mod; `dp` sized `[10][n+1]`.

## Perturbation (debrief — OPEN, not yet worked Socratically)
Posed but not resolved in chat: (a) why `n-1` remaining jumps (first press is the placement, not a jump);
(b) each layer depends only on the previous ⇒ **O(1) space** via 10 rolling counts (drop the `target` dim);
(c) for astronomically large `n`, matrix exponentiation on the 10×10 transition → `O(log n)`.
→ revisit at Day+14 revision per [[lc-perturbation-debrief]].

## Credit
DP » Linear **1/2** (1 more rep owed; deal #28 count-ways-to-build-good-strings is the intended 2nd).
Band clean-rate: **16/21 ≈ 76%**.
