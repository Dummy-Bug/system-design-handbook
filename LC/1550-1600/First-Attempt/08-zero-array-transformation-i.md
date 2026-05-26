# Zero Array Transformation I — First Attempt

## Problem

You are given an integer array nums of length n and a 2D array queries, where queries[i] = [li, ri]. For each queries[i]: Select a subset of indices within the range [li, ri] in nums. Decrement the values at the selected indices by 1. A Zero Array is an array where all elements are equal to 0. Return true if it is possible to transform nums into a Zero Array after processing all the queries sequentially, otherwise return false. Example 1: Input: nums = [1,0,1], queries = [[0,2]] Output: true Explanation: For i = 0: Select the subset of indices as [0, 2] and decrement the values at these indice

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-07 |
| Link | https://leetcode.com/problems/zero-array-transformation-i/ |
| Rating | 1580 |
| AC | Y |
| Time | 29min |
| Pattern | difference array / range increment |
| Revision due | 2026-05-21 |
| Remark | Each query [l,r] gives every index in range up to 1 decrement budget. Build diff array of "max decrements available per index", prefix-sum it, check `nums[i] <= budget[i]` for all i. Bug: wrote `diff[i] += 1; diff[j] += 1; diff[j+1] -= 1` — double-counting the right endpoint. Correct range-increment is just `diff[i] += 1; diff[j+1] -= 1` (no special case for i==j). |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
