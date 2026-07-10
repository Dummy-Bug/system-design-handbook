# 27 — Count Ways To Build Good Strings

- **Link:** https://leetcode.com/problems/count-ways-to-build-good-strings/ (LC 2466)
- **Dealt:** 2026-06-24 (replenishment deal #28)
- **Result:** ⚠️❌ **WA-then-AC (soft fail) + debugging help → NO REP**
- **Bucket (target):** **DP » Linear** → stays **1/2**
- **AR / slot:** ~57% / Q2

## Clean-status note
Submitted, got WA on `low=high=5, zero=2, one=4` (expected 0, got 4), then the two bugs were
found **with my help** → not self-derived + WA-then-AC. DP-Linear **stays 1/2** (rep 1 = #23 knight-dialer).
A clean 2nd DP-Linear rep is still owed.

## The DP state — two equivalent framings
The string is built by appending **blocks**: a run of exactly `zero` 0s, or a run of exactly `one` 1s.

- **"Exactly-x" (canonical):** `dp[x] = number of good strings of length exactly x`.
  Answer = `Σ dp[x] for x in [low, high]`.
- **"≤x" (cumulative — what my code used):** `dp[x] = number of good strings of length in [1, x]`.
  Answer = `dp[high] − dp[low−1]` (a cumulative count differenced into a range count).

Both are valid; same exponential growth. My code took the cumulative route.

## The recurrence — derived from the *last block*
A good string of length `n` ends in either a `zero`-run or a `one`-run (mutually exclusive):
- ends in `zero` 0s → the prefix is a good string of length `n − zero` → `dp[n − zero]` ways
- ends in `one` 1s → the prefix is a good string of length `n − one` → `dp[n − one]` ways

```
dp[n] = dp[n − zero] + dp[n − one]
```

## Two bugs (both real, both cost the rep)

### Bug 1 — read the memo table at an unvisited index `[stale-memo]`
v2 replaced the second `helper(low−1)` call with a **direct read** `dp[low−1]`, assuming memoization
had filled that slot. **Memoization only populates the states the recursion actually reaches.**
On `low=high=5, zero=2, one=4`, `helper(5)` steps by −2/−4 → visits only `dp[5], dp[3], dp[1]`;
**`dp[4]` is never touched and stays `−1`.** So `lowCount = dp[4] = −1`, `highCount = 3` →
`3 − (−1) = 4` (wrong; true answer 0, since `2a+4b=5` has no solution — LHS always even).
**Fix:** *invoke* `helper(low−1)`, don't read the array. It reuses cached subresults and fills the gaps;
no need to refill `dp` between the two calls since `dp[length]` depends only on `length`.

### Bug 2 — modular subtraction can go negative `[mod-underflow]`
`highCount` and `lowCount` are **already reduced mod MOD** before subtracting. Mod is **not order-preserving**:
in true value `high ≥ low`, but the *reduced* values can flip. Scale check (MOD=100): true 210−190=20, but
`210%100=10`, `190%100=90` → `10−90 = −80`. Java's `%` keeps the **sign of the dividend** → returns −80, not 20.
**Fix:** `((a − b) % MOD + MOD) % MOD`.

## Why mod at *every* step, not just at the end — overflow proof
The recurrence `dp[n] = dp[n−zero] + dp[n−one]` is **at least exponential**, so it overflows `long`
(`≈ 2^63 ≈ 9.2×10^18`) far below the input cap (`high ≤ 10^5`):

- **Fastest growth — `zero=one=1`:** both terms point at the same `dp[n−1]` → `dp[n] = 2·dp[n−1]` → `2^n`.
  Crosses `2^63` at **n ≈ 63**.
- **Slowest exponential — `zero=1, one=2`:** `dp[n] = dp[n−1] + dp[n−2]` = **Fibonacci** → `φ^n`, `φ=1.618`.
  (`φ` is the root of `r² = r + 1`, found by substituting `dp[n]≈r·dp[n−1]`.)
  Crosses `2^63` at `n > 63·log2 / log φ ≈ 18.96 / 0.209 ≈ **90**`.

Either way overflow hits by length ~63–90, vs the allowed `10^5` → guaranteed overflow.
**General recipe:** find the recurrence's exponential base `b`; overflow length `≈ 63 / log₂(b)`.
If below max input size → mod intermediately. (And modding intermediately is *exactly* what destroys the
`high ≥ low` ordering, forcing the `+MOD` fix in Bug 2.)

## Step 2 / Step 3
- **Worked example (the WA case):** `low=high=5, zero=2, one=4`. Length-5 strings need `2a+4b=5` → no
  non-negative solution (LHS even) → **0**. My buggy v2 returned 4; corrected v3 returns 0. ✓
- **Edges:** `low=high` (single length); `2a+by=n` infeasible → 0; `low=1` → `helper(0)=0` base; `high`
  large → overflow forces per-step mod; reduced `high < low` → `+MOD` rescue.

## Canonical (corrected, [[lc-revise-to-cleanest-form]])
```java
long highCount = helper(high, zero, one);
long lowCount  = helper(low - 1, zero, one);          // INVOKE, don't read dp[low-1]
return (int) (((highCount - lowCount) % MOD + MOD) % MOD);
// inside helper: return dp[length] = (zeroCount + oneCount) % MOD;  // mod EVERY step
```

## Credit
DP-Linear **stays 1/2** (WA-then-AC + debugging help). Band clean-rate: **17/24** (non-clean solve).
Retire from queue; do not re-deal.
