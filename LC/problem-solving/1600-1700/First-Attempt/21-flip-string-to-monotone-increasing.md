# 21 — Flip String to Monotone Increasing

- **Link:** https://leetcode.com/problems/flip-string-to-monotone-increasing/
- **Band:** 1600–1699 · sealed queue · blind deal #22 · Q2 (AR 61.9%)
- **Bucket:** answer key files it **DP » String**; OUR code = boundary-enumeration + suffix-zero prefix count.
- **Dealt:** 2026-06-16
- **AC:** 2026-06-16 _(first submission)_
- **Result:** ❌ **AC first-sub BUT EDITORIAL-level help → NO REP.** **DP-String stays 0/2.** clean-rate **14/20 = 70%** (on the floor).

---

## What happened (honest classification)
User first proposed a **local greedy**: "from the left, at the first `1` count 1s vs 0s; if 1s ≥ 0s flip the 0s." Claude (correctly, on request "how?") broke it with counterexample **`10011`** — greedy says flip 2 zeros, but flipping the single leading `1` costs 1. Then, when user vented "these types keep fucking me up," Claude **over-helped**: volunteered the family name, the exact `cost(k) = ones-before-k + zeros-at/after-k` formula, and the "try every boundary with prefix sums" method. User implemented Claude's approach → AC.

→ This is editorial-level (full approach handed over), not a mere hint. Same no-rep outcome as #11 / #12-BS. **Coaching error noted: should have stopped at the counterexample and let the user re-derive.**

## The problem
Min flips (`0↔1`) to make a binary string monotone increasing (`0…0 1…1`).

## Approach that ACed (boundary enumeration)
```
cost(i) = (#1s in [0,i))      // flip these to 0
        + (#0s in [i, n))     // flip these to 1
answer  = min over i = 0..n of cost(i)
```

## Solution (as submitted — user's code)
```java
class Solution {
    public int minFlipsMonoIncr(String s) {
        int n = s.length();
        int[] zeroCount = new int[n];
        if (s.charAt(n - 1) == '0') zeroCount[n - 1] = 1;
        for (int i = n - 2; i >= 0; i--) {
            if (s.charAt(i) == '0') zeroCount[i] += zeroCount[i + 1] + 1;
            else zeroCount[i] = zeroCount[i + 1];
        }
        int minFlips = n, countOnes = 0;
        for (int i = 0; i < n; i++) {
            minFlips = Math.min(minFlips, countOnes + zeroCount[i]);
            if (s.charAt(i) == '1') countOnes += 1;
        }
        minFlips = Math.min(minFlips, countOnes);
        return minFlips;
    }
}
```
`zeroCount[i]` = suffix zeros; `countOnes` = prefix ones; loop covers boundaries `0..n-1`, final line covers `k = n`. Correct, O(n) time, O(n) space.

## Canonical DP-String form (taught, for reference — NOT what earns the rep)
Two-state rolling DP, O(1) space:
```java
int dp0 = 0, dp1 = 0;            // dp0 = still 0-region, dp1 = entered 1-region
for (char c : s.toCharArray()) {
    int n0 = dp0 + (c == '1' ? 1 : 0);
    int n1 = Math.min(dp0, dp1) + (c == '0' ? 1 : 0);
    dp0 = n0; dp1 = n1;
}
return Math.min(dp0, dp1);
```
`min(dp0, dp1)` *slides the boundary for you* instead of enumerating it. The one-way `0→1` state edge (no edge back) encodes "monotone" structurally. The boundary-enumeration view is the simpler/honest model; the 2-state machine only earns its keep with 3+ regions or interacting regions.

## Lesson (recognition that DID transfer)
- **Family:** "minimum changes to force a fixed SHAPE" (monotone / non-decreasing / mountain / alternating / all-equal).
- **Meta-move:** when the answer is a *shape with one free parameter*, stop hunting a local greedy — **name the parameter (the boundary), write cost as a function of it, minimize over all values.** Prefix/suffix sums make each O(1).
- Same shape of move as binary-search-on-answer (parametrize + scan instead of be-clever). See [[reasoning-primitives/03-exchange-argument]] neighbor logic.
- **Why the local greedy failed:** boundary placement is a *tradeoff between two sides*; can't be priced locally (counterexample `10011`).

## PENDING
- **Owe 2 FRESH non-queue DP-String picks** — both queue picks (#04, #22) spent without credit.
- Revision Day+14: re-derive `cost(i)` boundary frame cold on a *different* shape-target string problem (no help).
