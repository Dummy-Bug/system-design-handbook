# 05 — Find the Punishment Number of an Integer

- **Link:** https://leetcode.com/problems/find-the-punishment-number-of-an-integer/
- **Band:** 1600–1699 · sealed queue · blind deal #5 · Q3 (AR 81.7%)
- **Bucket:** **Backtracking** (partition-the-digit-string, try all split points).
- **Dealt:** 2026-06-10
- **AC:** 2026-06-11 _(first-submission AC, 30m — at cap; self-derived)_
- **Result:** ✅ **clean first-submission AC, self-derived.** → **Backtracking 2/2 → OWNED ●.** Second bucket closed this band (after Union-Find). Clean-rate now **4/5 (80%)**.

---

## The problem
Punishment number of `n` = Σ `i²` over all `i ∈ [1,n]` such that the decimal string of `i²` can be partitioned into contiguous substrings whose integer values **sum to `i`**.

## Approach — backtracking partition (self-derived)
For each `i`, run a backtracking partition over `str(i²)`: at each position try every prefix length, subtract its value from the remaining target, recurse; success = consumed the whole string with target hitting exactly 0.

## Solution (clean first-AC)
```java
public int punishmentNumber(int n) {
    int count = 0;
    for (int i = 1; i <= n; i++)
        if (canPartition(0, Integer.toString(i * i), i))
            count += i * i;
    return count;
}

private boolean canPartition(int index, String s, int sum) {
    int n = s.length();
    if (index >= n) return sum == 0;
    for (int i = index; i < n; i++) {
        int num = Integer.parseInt(s.substring(index, i + 1));
        if (sum - num >= 0) {
            if (canPartition(i + 1, s, sum - num)) return true;
        } else break;                       // num only grows as the prefix extends → prune
    }
    return false;
}
```

## The capped→uncapped arc (self-derived; design refinement, NOT a hint-unlock)
- User self-derived the backtracking-partition idea **and** independently flagged `i=1000` as the edge case, with a valid handling (3-digit cap + special-case `1000`). That was already a complete, correct, self-derived path.
- Claude's input: argued the **uncapped** general version is cleaner/more robust (no magic `3`, no special-case carve-out, correct for any `n`). User shipped uncapped.
- Adjudicated **self-derived** ([[lc-no-vanilla-reps]] spirit): the algorithm + the critical edge were the user's; the swap to uncapped is a *design refinement of their own approach*, not the insight that unlocked the solve. Counts.

## WINS
1. **Default-to-general design landed.** Took the uncapped version → `i=1000` handled with **no special-case, no magic number**. Opposite of #03's over-model; the "specialize only when forced" reflex applied.
2. **`break` prune** — once a prefix value exceeds the remaining target, all longer prefixes do too (extending only grows the number), so stop. Clean.

## Time complexity — derivation (revision goal: produce this from scratch)
Two layers: **outer loop × cost of `canPartition` per `i`.**
1. Outer `for i = 1..n` → **O(n)**.
2. `canPartition` on a length-`d` string: `d−1` gaps, each cut / not-cut → **2^(d−1)** ways to chop → **O(2^d)** per `i`. _(Each node also does O(d) `substring`+`parseInt` → a minor `×d` factor.)_
3. `d` = digits of `i²`; `digits(X) = ⌊log₁₀X⌋ + 1`, so `d = digits(n²) ≈ 2·log₁₀(n)`. For `n ≤ 1000`: `n² ≤ 10⁶` → `d ≤ 7`.
4. Combine: **Total = O(n · 2^d)** ≈ `10³ · 2⁷ ≈ 1.3×10⁵` (≈`10⁶` with the per-node `×d`) **≪ 10⁸ → no TLE.** Closed form in `n`: `2^d ≈ n^{0.6}` ⟹ `≈ O(n^{1.6})`.

The `3^n` instinct was the trap — it put `n` in the exponent; the real exponent is the bounded digit-count `d ≈ 7`.

## Lesson
- **Design:** default to the general solution; specialize only when profiling forces it (capped+special-case was correct but brittle — magic number tied to the constraint).
- **TC:** the skill is *coming up with* the bound (the 4-step derivation above) — once you split it into outer × inner and see the exponent is the digit-count, the rest is arithmetic.

## PENDING
- Perturbation debrief — Socratic in chat first, then logged ([[lc-perturbation-before-write]]). No probes pre-written.
- Revision Day+14: re-derive uncapped backtracking cold; **re-derive the TC from scratch (the 4 steps — outer × inner, gaps→2^d, d=digits(n²))**; re-state the default-to-general design rule.
