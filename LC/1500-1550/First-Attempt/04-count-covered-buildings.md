# Count Covered Buildings — First Attempt

## Problem

You are given a positive integer n, representing an n x n city. You are also given a 2D grid buildings, where buildings[i] = [x, y] denotes a unique building located at coordinates [x, y]. A building is covered if there is at least one building in all four directions: left, right, above, and below. Return the number of covered buildings. Example 1: Input: n = 3, buildings = [[1,2],[2,2],[3,2],[2,1],[2,3]] Output: 1 Explanation: Only building [2,2] is covered as it has at least one building: above ([1,2]) below ([3,2]) left ([2,1]) right ([2,3]) Thus, the count of covered buildings is 1. Exampl

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-01 |
| Link | https://leetcode.com/problems/count-covered-buildings/ |
| Rating | 1519 |
| AC | N |
| Time | 35min |
| Pattern | sort + adjacent-group check / two-pass |
| Revision due | 2026-05-15 |
| Remark | Sort by x, building has left+right coverage if both neighbors share same x → add to set. Sort by y, check both neighbors share same y → count. Bug: used `n` (grid size) as loop bound instead of `buildings.length`. Syntax cost 10min: memorise lambda `(a,b) -> a[0]!=b[0] ? a[0]-b[0] : a[1]-b[1]`. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
