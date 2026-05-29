# #15 — Minimum Number of Operations to Make Array XOR Equal to K

**Link:** https://leetcode.com/problems/minimum-number-of-operations-to-make-array-xor-equal-to-k/
**Date:** 2026-05-29 (Fri)
**Rating:** ~1500-1550 band (Group A #9 — Bit Manipulation / Bitwise XOR acquisition)
**Time:** 4 min — **AC clean, first attempt**
**Pattern:** Bitwise XOR (XOR-fold the array, XOR with target, popcount the diff)

---

## Problem

Given an array `nums` and an integer `k`. In one operation you may flip any single bit of any element. Return the **minimum number of bit flips** so that the XOR of all elements equals `k`.

## Approach (verbatim)

Find the XOR of all elements. Then count how many bits differ between that XOR and `k` — that many flips are the answer. Neat realisation: if you XOR the running XOR with `k` as well, the number of **set bits** in the result *is* the answer.

## Solution (as submitted)

```java
class Solution {
    public int minOperations(int[] nums, int k) {
        int xor = 0;
        for (int num : nums) xor ^= num;
        xor ^= k;
        return Integer.bitCount(xor);
    }
}
```

**Complexity:** O(n) time, O(1) space.

## Why it works

XOR is bit-independent: bit `b` of the array's total XOR is just the parity of how many elements have bit `b` set. Flipping bit `b` of any one element toggles bit `b` of the whole XOR — and flipping it once is both necessary and sufficient to change that bit. So for each bit position the array XOR and `k` *disagree* on, you need exactly one flip; where they agree, zero.

"Number of positions where two numbers disagree" is exactly `popcount(a XOR b)` — the **Hamming distance**. Folding `k` into the running XOR (`xor ^= k`) and calling `Integer.bitCount` collapses "compare bit-by-bit" into one popcount.

## Debrief notes

- **Clean, 4 min, first try — instant pattern recognition.** This is the textbook Bitwise XOR idiom and you nailed both the insight (Hamming distance = answer) and the one-liner collapse (`xor ^= k; bitCount`).
- **Bucket acquired.** This closes the Bit Manipulation / Bitwise XOR bucket for the band. Consistent with prior XOR reps: 1450-1500 #7 (Longest Subsequence Non-Zero XOR) and the BIT-fold alt on Construct K Palindrome (#12 there).
- **Idiom worth keeping reflexive:** `Integer.bitCount(a ^ b)` = Hamming distance between `a` and `b`. Shows up anywhere a problem asks "minimum single-bit changes to turn X into Y."
