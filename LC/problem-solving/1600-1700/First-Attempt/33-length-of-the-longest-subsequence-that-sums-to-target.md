# 33 — Length of the Longest Subsequence That Sums to Target

- **Link:** https://leetcode.com/problems/length-of-the-longest-subsequence-that-sums-to-target/ (LC 2915)
- **Dealt:** 2026-11-14 morning, fourth problem after the restart
- **Rating / slot:** 1659 · Biweekly Contest 116 Q3 · AR 39.8%
- **Result:** ✅ **Clean first-submission AC, self-derived, 27 min, inside the 30-min cap.** One approach check from Claude at 13 min, answered with one word (correct), no hint. Not yet at the 20-min readiness bar.
- **Bucket (revealed post-solve):** **DP-Knapsack** (0/1), the take/skip of #31 with the remaining target as the second dimension.
- **Cold re-solve:** not owed (no hint, no WA, no editorial).

## Timeline

| Time | Min | What happened |
|---|---|---|
| 08:14 | 0 | Started reading |
| 08:27 | 13 | Recognised it as the take/skip of #31, taking the max. Worst case n², but n and target are both ≤ 1000, so n × target fits. Asked for a check → correct |
| 08:27–08:41 | 13–27 | Coded |
| 08:41 | 27 | **AC** on the first submission |

## The recurrence

```
helper(i, t) = longest subsequence of nums[i..] summing to exactly t, or -1 if none

helper(i, t) = max( helper(i+1, t),                      skip nums[i]
                    helper(i+1, t - nums[i]) + 1 )       take nums[i], only if that call is not -1

t == 0              → 0     target reached, nothing more needed
t < 0 or i == n     → -1    overshot, or ran out with t still owed

answer = helper(0, target)
```

States: `i` has n values and `t` has target + 1 values, so at most 1000 × 1001 ≈ 10⁶ states with O(1) work each. **O(n · target)** time and space.

## What carried over from #31

- **Sentinel checked before adding:** `if (take != -1) take += 1;`, so an impossible branch is never counted as a real length. This is the bug that cost #31 its WA, not repeated.
- **Bounds before the memo read:** `t < 0` returns before `dp[i][target]` is touched, so a negative index is never read.
- **State written and ranges multiplied before rejecting DP:** the #31 reflex, applied at minute 13.

## Process note

Step 2 (recompute the richest worked example) and Step 3 (named edge cases) were not posted before coding. The time split was 13 min to the approach and 14 min to code, both shorter than #32.

## Debrief — the answer-key approach (editorial)

Same recurrence, written bottom-up: `f[i][j] = max(f[i−1][j], f[i−1][j−x] + 1)` with `f[0][0] = 0` and every other start at −∞. Each row depends only on the row before, so one array of size target + 1, iterated with `j` from high to low, brings space down to **O(target)**.

**Reflex:** pick a subset whose sum hits an exact target, n · target small → 0/1 knapsack over (index, remaining sum).

## Final code (AC)

```java
class Solution {

    private Integer[][] dp;

    public int lengthOfLongestSubsequence(List<Integer> nums, int target) {
        dp = new Integer[nums.size()][target+1];

        return helper(0,target,nums);
    }

    private int helper(int i , int target , List<Integer> nums){
        
        if (target == 0) return 0;

        if (target < 0 || nums.size() == i) return -1;

        if (dp[i][target] != null) return dp[i][target];
        
        int skip = helper(i + 1, target , nums);
        int take = helper(i + 1, target - nums.get(i),nums);
        
        if (take != -1) take += 1;
        return dp[i][target] = Math.max(skip , take);
        
    }
}
```
