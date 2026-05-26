# Maximum Bitwise XOR After Rearrangement — First Attempt

## Problem

You are given two binary strings s and t​​​​​​​, each of length n. You may rearrange the characters of t in any order, but s must remain unchanged. Return a binary string of length n representing the maximum integer value obtainable by taking the bitwise XOR of s and rearranged t. Example 1: Input: s = "101", t = "011" Output: "110" Explanation: One optimal rearrangement of t is "011". The bitwise XOR of s and rearranged t is "101" XOR "011" = "110", which is the maximum possible. Example 2: Input: s = "0110", t = "1110" Output: "1101" Explanation: One optimal rearrangement of t is "1011". The

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-04 |
| Link | https://leetcode.com/problems/maximum-bitwise-xor-after-rearrangement/ |
| Rating | 1556 |
| AC | Y |
| Time | 10min |
| Pattern | greedy + char count |
| Revision due | 2026-05-18 |
| Remark | Count 0s and 1s in t. Walk s left to right (MSB-first). For each `s[i]`: if it's '1', try to pair with a '0' from t (XOR=1); else try to pair with a '1' from t. If matching char unavailable, append '0'. "XOR" framing misleads people into bit-DP — it's just greedy counting. |

---

> [!note] This band's log is compact (table + remark). Full verbatim thinking and solution code were not captured — only the logged insight/remark above survives.
