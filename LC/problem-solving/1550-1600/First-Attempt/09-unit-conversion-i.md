# Unit Conversion I — First Attempt

## Problem

There are n types of units indexed from 0 to n - 1. You are given a 2D integer array conversions of length n - 1, where conversions[i] = [sourceUniti, targetUniti, conversionFactori]. This indicates that a single unit of type sourceUniti is equivalent to conversionFactori units of type targetUniti. Return an array baseUnitConversion of length n, where baseUnitConversion[i] is the number of units of type i equivalent to a single unit of type 0. Since the answer may be large, return each baseUnitConversion[i] modulo 109 + 7. Example 1: Input: conversions = [[0,1,2],[1,2,3]] Output: [1,2,6] Expla

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-07 |
| Link | https://leetcode.com/problems/unit-conversion-i/ |
| Rating | 1591 |
| AC | Y |
| Time | 30min |
| Pattern | BFS/DFS on tree + running product |
| Revision due | 2026-05-21 |
| Remark | Build adjacency list from conversions (guaranteed tree rooted at 0). BFS from node 0: `result[child] = result[parent] * factor % MOD`. All paths are unique (tree property) so no revisit handling beyond a visited check. Syntax struggle: `List<int[]>[]` — declare as `List<int[]>[] adj = new ArrayList[n]` then init each slot. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
