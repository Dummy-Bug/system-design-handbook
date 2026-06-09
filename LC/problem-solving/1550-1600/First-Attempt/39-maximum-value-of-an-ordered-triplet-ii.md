# 39 — Maximum Value of an Ordered Triplet II

- **Link:** https://leetcode.com/problems/maximum-value-of-an-ordered-triplet-ii/
- **Band:** 1550–1600 · Phase 2 sealed queue · walk-think deal · dealt 2026-06-09
- **Bucket (revealed post-solve):** **Prefix Sum / prefix-suffix extrema** (running prefix-max + suffix-max array). Credit by [[lc-classify-by-own-solution]]: our code maintains a left running max and a right suffix-max, then scans the middle.
- **Dealt:** 2026-06-09 (walk-think)
- **AC:** 2026-06-09 10:27 IST _(self-derived, no hint, **no WA on judge**)_
- **Result:** ✅ **CLEAN first-submission AC, ~20 min SUB-CAP.** Counts toward ownership.

## The problem
Indices `i < j < k`. Triplet value = `(nums[i] − nums[j]) * nums[k]`. Return the **max** over all triplets, or **0** if every triplet value is negative. `n ≤ 1e5`, `nums[i] ≤ 1e6` (positive) → O(n³) brute is dead; product can overflow `int` → needs `long`.

## Approach (our code)
Fix the **middle** index `j`. The value factorizes into three independent extremes:
- best `nums[i]` for `i < j` = **running prefix-max** `leftMax`,
- the chosen `nums[j]`,
- best `nums[k]` for `k > j` = **suffix-max** `rightMax[j+1]` (precomputed right-to-left).

For each `j`: `currMax = (leftMax − nums[j]) * (long)rightMax[j+1]`. Track the max. Because `nums[k] > 0`, multiplying the largest available `rightMax` is always best when `(leftMax − nums[j]) > 0`. The `>= 0` guard + `ans = 0` start handles the all-negative case.

```java
int n = nums.length;
int[] rightMax = new int[n];
rightMax[n-1] = nums[n-1];
for (int i = n-2; i >= 2; i--) rightMax[i] = Math.max(nums[i], rightMax[i+1]);
long ans = 0L; int leftMax = nums[0];
for (int j = 1; j < n-1; j++){
    long currMax = (leftMax - nums[j]) * (long)rightMax[j+1];
    if (currMax >= 0L) ans = Math.max(ans, currMax);
    leftMax = Math.max(leftMax, nums[j]);
}
return ans;
```

## Why it's correct / clean
- **Fix-the-middle** is the unlock: the two outer factors decouple into independent prefix/suffix extremes, collapsing O(n³) → O(n).
- **Overflow caught:** the `(long)` cast on the product (`(leftMax−nums[j]) * rightMax`, up to ~1e6·1e6 = 1e12 > int). This is the exact recurring-bug class that's bitten earlier solves — handled pre-submission here.
- **Tight bounds:** `rightMax` only filled for `[2, n-1]` (the only indices ever read as `j+1`); `rightMax[0..1]` left untouched. Correct, not a bug.

## Canonical form (O(1) space, single pass) — derived Socratically 2026-06-09
The submitted solution is correct but uses an **O(n) `rightMax[]` array**. The cleaner canonical form is **O(1) space, one forward pass** ([[lc-revise-to-cleanest-form]]).

**The unlock (derived):** fixing the **middle** `j` forces looking both ways → whichever direction you sweep, one of `{i, k}` is in the *future*, so it can't be a running scalar (that's exactly why `k` needed an array). **Fix the rightmost index `k` instead** → both `i` and `j` fall in `k`'s past → everything is a backward-accumulated scalar, no array.

**Trap caught Socratically:** you can't pair a global `leftMax` with a global `leftMin` — that lets the max sit *after* the min, violating `i < j` (e.g. `[1,5]` → `leftMax−leftMin = 4`, but the only legal pair gives `1−5 = −4`). Fix: maintain `maxDiff = max over i<j of (nums[i]−nums[j])` incrementally — when an element becomes a `j`, pair it only with the `leftMax` of *strictly-earlier* indices.

```java
public long maximumTripletValue(int[] nums) {
    int n = nums.length;
    long ans = 0L;
    int maxDiff = 0, leftMax = nums[0];
    for (int k = 2; k < n; k++){
        int j = k - 1;
        maxDiff = Math.max(maxDiff, leftMax - nums[j]); // fold j: best (i−j), i strictly < j
        ans     = Math.max(ans, maxDiff * (long)nums[k]); // score k: i,j both < k
        leftMax = Math.max(leftMax, nums[j]);           // fold i last → never pairs with itself
    }
    return ans;
}
```

**The invariant = the whole lesson:** the order `maxDiff → ans → leftMax` (or equivalently the `j = k-1` stagger) enforces that *every role reads only strictly-earlier state*. Reorder it and an element pairs with itself, breaking `i < j < k`. The `0` floor on `maxDiff` collapses the all-negative case to `0` because `nums[k] > 0`. Two equivalent ways to enforce strictness: **index stagger** (`j = k-1`) or **update order** (single index, three ordered folds).

## Lesson
"Maximize a product/expression over an ordered triplet `i<j<k`" ⇒ **fix the middle, decouple the ends into prefix-max & suffix-max.** The reusable trigger: when an expression splits into one factor from the left of `j` and one from the right, precompute both extreme-scans and sweep `j` in O(n). Remember the `long` cast whenever two ≤1e6 values multiply.

## REVISION TARGET (Day+14)
Cold, blank page — re-derive the **O(1) canonical**, not the O(n) original: (1) why fixing the *middle* forces an array but fixing the *rightmost* `k` makes everything a backward scalar; (2) the `leftMax`/`leftMin` ordering trap (`[1,5]` counterexample) → maintain `maxDiff` incrementally; (3) the forced update order `maxDiff → ans → leftMax` (or `j=k-1` stagger) = "read only strictly-earlier state"; (4) the `long`-cast overflow point + the `0`-floor-because-`nums[k]>0`.
