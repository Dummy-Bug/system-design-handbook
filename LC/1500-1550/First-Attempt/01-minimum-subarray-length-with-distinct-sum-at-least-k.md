# Minimum Subarray Length with Distinct Sum at Least K — First Attempt

## Problem

You are given an integer array nums and an integer k. Return the minimum length of a subarray whose sum of the distinct values present in that subarray (each value counted once) is at least k. If no such subarray exists, return -1. Example 1: Input: nums = [2,2,3,1], k = 4 Output: 2 Explanation: The subarray [2, 3] has distinct elements {2, 3} whose sum is 2 + 3 = 5, which is ​​​​​​​at least k = 4. Thus, the answer is 2. Example 2: Input: nums = [3,2,3,4], k = 5 Output: 2 Explanation: The subarray [3, 2] has distinct elements {3, 2} whose sum is 3 + 2 = 5, which is ​​​​​​​at least k = 5. Thus,

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-01 |
| Link | https://leetcode.com/problems/minimum-subarray-length-with-distinct-sum-at-least-k/ |
| Rating | 1505 |
| AC | Y |
| Time | 27min |
| Pattern | sliding-window / distinct-sum tracking |
| Revision due | 2026-05-15 |
| Remark | Add `nums[j]` to sum when freq==0 (first occurrence); subtract `nums[i]` when freq==1 (last copy leaving). Standard shrink-while-valid window. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
