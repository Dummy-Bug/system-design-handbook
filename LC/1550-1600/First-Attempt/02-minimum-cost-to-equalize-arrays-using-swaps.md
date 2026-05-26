# Minimum Cost to Equalize Arrays Using Swaps — First Attempt

## Problem

You are given two integer arrays nums1 and nums2 of size n. You can perform the following two operations any number of times on these two arrays: Swap within the same array: Choose two indices i and j. Then, choose either to swap nums1[i] and nums1[j], or nums2[i] and nums2[j]. This operation is free of charge. Swap between two arrays: Choose an index i. Then, swap nums1[i] and nums2[i]. This operation incurs a cost of 1. Return an integer denoting the minimum cost to make nums1 and nums2 identical. If this is not possible, return -1. Example 1: Input: nums1 = [10,20], nums2 = [20,10] Output:

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-04 |
| Link | https://leetcode.com/problems/minimum-cost-to-equalize-arrays-using-swaps/ |
| Rating | 1579 |
| AC | Y |
| Time | 100min |
| Pattern | frequency-map + excess pairing |
| Revision due | 2026-05-18 |
| Remark | Build combined freq map + per-array maps. For each value: if total freq odd → -1. Excess = (freq1-freq2)/2. Track swap1/swap2 (pending excess from each side) — pair them before adding to contribution since one paid swap resolves one excess from each side simultaneously. `(freq&1)!=0` needs parens around `freq&1` due to Java operator precedence. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
