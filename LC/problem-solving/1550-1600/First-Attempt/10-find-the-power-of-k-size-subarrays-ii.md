# Find the Power of K-Size Subarrays II — First Attempt

## Problem

You are given an array of integers nums of length n and a positive integer k. The power of an array is defined as: Its maximum element if all of its elements are consecutive and sorted in ascending order. -1 otherwise. You need to find the power of all subarrays of nums of size k. Return an integer array results of size n - k + 1, where results[i] is the power of nums[i..(i + k - 1)]. Example 1: Input: nums = [1,2,3,4,3,2,5], k = 3 Output: [3,4,-1,-1,-1] Explanation: There are 5 subarrays of nums of size 3: [1, 2, 3] with the maximum element 3. [2, 3, 4] with the maximum element 4. [3, 4, 3] w

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-07 |
| Link | https://leetcode.com/problems/find-the-power-of-k-size-subarrays-ii/description/ |
| Rating | 1595 |
| AC | Y |
| Time | 30min |
| Pattern | sliding window / consecutive run tracking |
| Revision due | 2026-05-21 |
| Remark | Track start `i` of current consecutive run — reset `i = j` whenever `nums[j] != nums[j-1]+1`. Window `[j-k+1, j]` is valid iff run length `j-i+1 >= k`. If valid, answer is `nums[j]`; else -1. Clean O(n) single pass. `i++` after recording a valid window keeps `i` anchored correctly for the next slide. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
