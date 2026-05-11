# Biweekly Contest 182 — Q2: Minimum Flips to Make Binary String Coherent

**Date:** 2026-05-09
**Link:** https://leetcode.com/problems/minimum-flips-to-make-binary-string-coherent/
**Result:** Not solved in contest (110 min spent)
**Note:** Problem was harder than typical Q2 — community confirmed harder than Q3/Q4. ~28% solve rate vs typical 50-70%.

---

## The Problem

Given a binary string `s`, a string is **coherent** if it doesn't contain `"011"` or `"110"` as a subsequence. Return minimum flips to make `s` coherent.

---

## Where I Got Stuck

Went **bottom-up** — processed character by character, tracking left/right counts of 0s and 1s, trying to decide greedily whether to flip each character.

```java
if (cl1 >= 2 || cr_1 >= 2){
    // this 0 is dangerous, flip it
    flips++;
}
```

This broke because flipping a character changes the counts for future characters — greedy decisions cascade and corrupt each other.

---

## The Key Insight — Enumerate Valid Outputs First

> [!important] Mindset shift
> **Bottom-up (what I did):** Start from the input, process character by character, decide per character whether to flip.
>
> **Top-down (the insight):** Forget the input. Ask: *what does a VALID string even look like?* List ALL possible valid final shapes first.

### Why is a string coherent?

A string is coherent if every `0` has **at most 1 one to its left** AND **at most 1 one to its right**.

From this rule, the ONLY valid shapes are:

```
Shape 1: 000...0        → all zeros
Shape 2: 111...1        → all ones
Shape 3: 0..010..0      → single 1 anywhere, zeros around it
Shape 4: 10..01         → starts AND ends with 1, zeros only in between
```

Any other shape has some `0` with 2+ ones on one side → forms "110" or "011".

### Then the problem becomes trivial

For each shape, cost = number of mismatches with `s`. Take the minimum.

```java
int ones = count of '1's in s;
int zeros = n - ones;

int cost1 = ones;                          // flip all 1s → all zeros
int cost2 = zeros;                         // flip all 0s → all ones
int cost3 = ones == 0 ? 1 : ones - 1;     // keep one 1, flip rest

// shape 4: s[0]=1, s[n-1]=1, middle all zeros
int middleOnes = ones - (s[0]=='1'?1:0) - (s[n-1]=='1'?1:0);
int cost4 = (s[0]=='0'?1:0) + (s[n-1]=='0'?1:0) + middleOnes;

return min(cost1, cost2, cost3, cost4);
```

**Time: O(n). Space: O(1).**

---

## The Trigger for Next Time

> [!tip] Contest trigger — use when stuck after 20 min
> Stop processing the input. Ask: **"What are ALL the valid forms the final answer can take?"**
> List them. Compute cost to reach each. Take the minimum.
> This is **enumerating valid outputs** — top-down, not bottom-up.

---

## Full Solution

```java
class Solution {
    public int minFlips(String s) {
        int n = s.length();
        int ones = 0;
        for (char c : s.toCharArray()) if (c == '1') ones++;
        int zeros = n - ones;

        int cost1 = ones;
        int cost2 = zeros;
        int cost3 = ones == 0 ? 1 : ones - 1;

        int cost4 = Integer.MAX_VALUE;
        if (n >= 2) {
            int middleOnes = ones
                - (s.charAt(0) == '1' ? 1 : 0)
                - (s.charAt(n-1) == '1' ? 1 : 0);
            cost4 = (s.charAt(0) == '0' ? 1 : 0)
                  + (s.charAt(n-1) == '0' ? 1 : 0)
                  + middleOnes;
        }

        return Math.min(Math.min(cost1, cost2), Math.min(cost3, cost4));
    }
}
```
