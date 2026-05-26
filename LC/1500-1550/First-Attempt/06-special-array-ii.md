# Special Array II — First Attempt

## Problem

An array is considered special if every pair of its adjacent elements contains two numbers with different parity. You are given an array of integer nums and a 2D integer matrix queries, where for queries[i] = [fromi, toi] your task is to check that subarray nums[fromi..toi] is special or not. Return an array of booleans answer such that answer[i] is true if nums[fromi..toi] is special. Example 1: Input: nums = [3,4,1,2,6], queries = [[0,4]] Output: [false] Explanation: The subarray is [3,4,1,2,6]. 2 and 6 are both even. Example 2: Input: nums = [4,3,1,6], queries = [[0,2],[2,3]] Output: [false

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-01 |
| Link | https://leetcode.com/problems/special-array-ii/ |
| Rating | 1523 |
| AC | Y |
| Time | <30min |
| Pattern | segment-id prefix / parity grouping |
| Revision due | 2026-05-15 |
| Remark | Approach derived solo, code written by ChatGPT — not a clean rep. Assign segment ID, increment when adjacent elements share same parity. Query [l,r] special iff segment[l]==segment[r]. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
