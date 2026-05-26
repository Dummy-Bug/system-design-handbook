# Maximum Product of Three Elements After One Replacement — First Attempt

## Problem

You are given an integer array nums. You must replace exactly one element in the array with any integer value in the range [-105, 105] (inclusive). After performing this single replacement, determine the maximum possible product of any three elements at distinct indices from the modified array. Return an integer denoting the maximum product achievable. Example 1: Input: nums = [-5,7,0] Output: 3500000 Explanation: Replacing 0 with -105 gives the array [-5, 7, -105], which has a product (-5) * 7 * (-105) = 3500000. The maximum product is 3500000. Example 2: Input: nums = [-4,-2,-1,-3] Output: 1

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-01 |
| Link | https://leetcode.com/problems/maximum-product-of-three-elements-after-one-replacement/ |
| Rating | 1529 |
| AC | Y |
| Time | 16min |
| Pattern | min-heap of size 3 / top-k tracking |
| Revision due | 2026-05-15 |
| Remark | Keep 3 largest in min-heap. Replace smallest with 10^5. Answer = max * secondMax * 100000. Cast to long — product of three 10^5 values = 10^15, overflows int. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
