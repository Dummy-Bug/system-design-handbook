# Special Triplets — First Attempt

## Problem

You are given an integer array nums. A special triplet is defined as a triplet of indices (i, j, k) such that: 0 <= i < j < k < n, where n = nums.length nums[i] == nums[j] * 2 nums[k] == nums[j] * 2 Return the total number of special triplets in the array. Since the answer may be large, return it modulo 109 + 7. Example 1: Input: nums = [6,3,6] Output: 1 Explanation: The only special triplet is (i, j, k) = (0, 1, 2), where: nums[0] = 6, nums[1] = 3, nums[2] = 6 nums[0] = nums[1] * 2 = 3 * 2 = 6 nums[2] = nums[1] * 2 = 3 * 2 = 6 Example 2: Input: nums = [0,1,0,0] Output: 1 Explanation: The only

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-01 |
| Link | https://leetcode.com/problems/special-triplets/ |
| Rating | 1510 |
| AC | Y |
| Time | 26min |
| Pattern | prefix-suffix count / fix-the-middle |
| Revision due | 2026-05-15 |
| Remark | Fix j as middle. left[j] = count of i<j where nums[i]==nums[j]*2, right[j] same for k>j. Answer = sum of left[j]*right[j]. Cast to long before multiply — product up to 10^10 overflows int. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
