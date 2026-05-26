# Find Good Integers — First Attempt

## Problem

You are given an integer n. An integer x is considered good if there exist at least two distinct pairs (a, b) such that: a and b are positive integers. a <= b x = a3 + b3 Return an array containing all good integers less than or equal to n, sorted in ascending order. Example 1: Input: n = 4104 Output: [1729,4104] Explanation: Among integers less than or equal to 4104, the good integers are: 1729: 13 + 123 = 1729 and 93 + 103 = 1729. 4104: 23 + 163 = 4104 and 93 + 153 = 4104. Thus, the answer is [1729, 4104]. Example 2: Input: n = 578 Output: [] Explanation: There are no good integers less than

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-02 |
| Link | https://leetcode.com/problems/find-good-integers/ |
| Rating | 1534 |
| AC | Y |
| Time | 42min |
| Pattern | precompute / two-nested-loops cube enumeration |
| Revision due | 2026-05-16 |
| Remark | Precompute all a³+b³ in TreeMap (sum→count). Good if count≥2 (not ==2). `Math.pow(i,3)` TLE → use `i*i*i`. Static block to run once. Float trap: `(int)Math.pow(1e9,1.0/3)` returns 999 — always `+1` after cast. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
