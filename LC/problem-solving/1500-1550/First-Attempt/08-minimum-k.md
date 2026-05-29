# Minimum K — First Attempt

## Problem

You are given a positive integer array nums. For a positive integer k, define nonPositive(nums, k) as the minimum number of operations needed to make every element of nums non-positive. In one operation, you can choose an index i and reduce nums[i] by k. Return an integer denoting the minimum value of k such that nonPositive(nums, k) <= k2. Example 1: Input: nums = [3,7,5] Output: 3 Explanation: When k = 3, nonPositive(nums, k) = 6 <= k2. Reduce nums[0] = 3 one time. nums[0] becomes 3 - 3 = 0. Reduce nums[1] = 7 three times. nums[1] becomes 7 - 3 - 3 - 3 = -2. Reduce nums[2] = 5 two times. num

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-02 |
| Link | https://leetcode.com/problems/minimum-k/ |
| Rating | 1531 |
| AC | Y |
| Time | 26min |
| Pattern | binary search on answer |
| Revision due | 2026-05-16 |
| Remark | Binary search k from 1 to 10^5. Total ops = sum of ceil(num/k), check ≤ k². `ceil(num/k)` needs double cast: `Math.ceil((double)num/k)`. `mid*mid` overflows int — use `(long)mid*mid`. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
