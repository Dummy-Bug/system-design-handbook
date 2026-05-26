# Smallest Repunit Multiple of K — First Attempt

## Problem

You are given a positive integer k. Find the smallest integer n divisible by k that consists of only the digit 1 in its decimal representation (e.g., 1, 11, 111, ...). Return an integer denoting the number of digits in the decimal representation of n. If no such n exists, return -1. Example 1: Input: k = 3 Output: 3 Explanation: n = 111 because 111 is divisible by 3, but 1 and 11 are not. The length of n = 111 is 3. Example 2: Input: k = 7 Output: 6 Explanation: n = 111111. The length of n = 111111 is 6. Example 3: Input: k = 2 Output: -1 Explanation: There does not exist a valid n that is a m

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-05 |
| Link | (rep-unit divisible by k — minAllOneMultiple) |
| Rating | 1593 |
| AC | Y |
| Time | 30min |
| Pattern | pigeonhole + deterministic recurrence on mod |
| Revision due | 2026-05-19 |
| Remark | `num = num*10 + 1` overflows int after 9 iterations and long after 19; worst case needs ~k digits (up to 10^5). Track only `mod = (mod*10 + 1) % k` — state space is bounded by k values, cycle detection via Set. AC was self, but deeper "why long also fails" + pigeonhole bound on answer length (mod has k drawers, k+1 iterations forces repeat, deterministic transition ⇒ cycle) was taught by Claude — not solo derivation. Meta-pattern: finite state + deterministic transition ⇒ bounded search. See `defer.md` for follow-up problems. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
