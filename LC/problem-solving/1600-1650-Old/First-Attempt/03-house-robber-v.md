# House Robber V — First Attempt

## Problem

You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed and is protected by a security system with a color code.

You are given two integer arrays nums and colors, both of length n, where nums[i] is the amount of money in the i^th house and colors[i] is the color code of that house.

You cannot rob two adjacent houses if they share the same color code.

Return the maximum amount of money you can rob.

 

Example 1:

Input: nums = [1,4,3,5], colors = [1,1,2,2]

Output: 9

Explanation:

	Choose houses i = 1 with nums[1] = 4 and i = 3 with nums[3] = 5 because they are non-adjacent.

	Thus, the total amount robbed is 4 + 5 = 9.

Example 2:

Input: nums = [3,1,2,4], colors = [2,3,2,2]

Output: 8

Explanation:

	Choose houses i = 0 with nums[0] = 3, i = 1 with nums[1] = 1, and i = 3 with nums[3] = 4.

	This selection is valid because houses i = 0 and i = 1 have different colors, and house i = 3 is non-adjacent to i = 1.

	Thus, the total amount robbed is 3 + 1 + 4 = 8.

Example 3:

Input: nums = [10,1,3,9], colors = [1,1,1,2]

Output: 22

Explanation:

	Choose houses i = 0 with nums[0] = 10, i = 2 with nums[2] = 3, and i = 3 with nums[3] = 9.

	This selection is valid because houses i = 0 and i = 2 are non-adjacent, and houses i = 2 and i = 3 have different colors.

	Thus, the total amount robbed is 10 + 3 + 9 = 22.

 

Constraints:

	1 <= n == nums.length == colors.length <= 10^5

	1 <= nums[i], colors[i] <= 10^5

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-08 |
| Link | https://leetcode.com/problems/house-robber-v/description/ |
| Rating | 1619 |
| AC | Y |
| Time | 60min |
| Pattern | DP — state definition + T(C) derivation + space optimization |
| Revision due | 2026-05-22 |
| Remark | First DP in years. Derived state definition `dp[i] = max money from houses 0 to i` from constraints. Calculated T(C): exponential without memo (2^n like Fibonacci tree), O(n) with memo (n states × O(1) work). Top-down → bottom-up → O(1) space via rolling vars (first, second). Integer overflow bug: used int[] instead of long[] for sum up to 10^10. |

---

> [!note] Verbatim thinking and full solution code were **not captured** on the first attempt (it predates the per-attempt archive). Only the logged insight/remark above survives. Full verbatim + inlined code begin from the second attempt onward.
