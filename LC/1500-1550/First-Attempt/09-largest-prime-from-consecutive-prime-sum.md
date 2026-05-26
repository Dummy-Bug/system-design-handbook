# Largest Prime from Consecutive Prime Sum — First Attempt

## Problem

You are given an integer n. Return the largest prime number less than or equal to n that can be expressed as the sum of one or more consecutive prime numbers starting from 2. If no such number exists, return 0. Example 1: Input: n = 20 Output: 17 Explanation: The prime numbers less than or equal to n = 20 which are consecutive prime sums are: 2 = 2 5 = 2 + 3 17 = 2 + 3 + 5 + 7 The largest is 17, so it is the answer. Example 2: Input: n = 2 Output: 2 Explanation: The only consecutive prime sum less than or equal to 2 is 2 itself. Constraints: 1 <= n <= 5 * 105

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-04 |
| Link | https://leetcode.com/problems/largest-prime-from-consecutive-prime-sum/ |
| Rating | 1547 |
| AC | Y |
| Time | 26min |
| Pattern | sieve + consecutive prime sum + TreeSet floor |
| Revision due | 2026-05-18 |
| Remark | Sieve up to 5×10^5. Accumulate running sum from first prime (2). When sum is also prime → add to TreeSet. `floor(n)` for query. `(long)i*i` in sieve inner loop — not `long j = i*i` (overflows int before assignment). Static block for one-time precompute. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
