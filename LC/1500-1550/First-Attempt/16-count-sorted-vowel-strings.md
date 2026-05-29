# #16 — Count Sorted Vowel Strings

**Link:** https://leetcode.com/problems/count-sorted-vowel-strings/
**Date:** 2026-05-29 (Fri)
**Rating:** ~1500-1550 band (Group A #5 — Dynamic Programming Level 1 / Linear DP acquisition)
**Time:** over cap — **AC, logic self-derived, syntax assist from Gemini (NOT a clean cold solve)**
**Pattern:** top-down memoized DP (counting DP); closed form C(n+4, 4)

---

## Problem

Count the number of strings of length `n` using only the 5 vowels `a e i o u` that are **lexicographically sorted** — every character is `>=` the one before it (e.g. `aa`, `ae`, `eo`, but not `ea`). Return the count.

## Approach (verbatim)

`n == 1` serves as the base case. DP state `f(prev, length)` = given the previous chosen value `prev` and a remaining `length`, how many sorted strings are possible. Recurrence: `f(prev, length) = Σ f(val, length-1)` for every `val >= prev` (the next char can be the same or any larger vowel).

## Solution (as submitted)

```java
class Solution {
    int[][] dp;

    public int countVowelStrings(int n) {
        dp = new int[n + 1][5];
        for (int i = 0; i <= n; i++) Arrays.fill(dp[i], -1);
        return helper(n, 0);
    }

    private int helper(int length, int prev) {
        if (length == 1) return 5 - prev;              // one slot left: can pick prev..u
        if (dp[length][prev] != -1) return dp[length][prev];

        int sum = 0;
        for (int i = 0; i < 5; i++)
            if (prev <= i) sum += helper(length - 1, i);

        return dp[length][prev] = sum;
    }
}
```

**Complexity:** O(n · 5 · 5) = O(n) states × O(5) transition. Space O(n · 5).

## Why the recurrence is right

A sorted string is built left-to-right where each character is `>=` the previous. So the only thing that constrains the next character is the *last value placed* (`prev`) — not the whole prefix. That's the DP insight: **state = (how many slots remain, what the floor value is)**. From state `(length, prev)` you try each vowel `i >= prev` as the next char and recurse on `(length-1, i)`. The base case `length == 1` has `5 - prev` choices (any vowel from `prev` to `u`).

> This is the classic "non-decreasing sequence count" shape — the same state design recurs in *Count Numbers with Non-Decreasing Digits*, *Combinations with repetition*, etc. **State = remaining length + lower-bound floor** is the reusable idea.

## Honest classification

- **Logic self-derived** — the state `(prev, length)` and the `Σ_{i>=prev}` recurrence were the user's own. That is exactly the derivation muscle this band trains, and it was done correctly.
- **Syntax assist from Gemini** — the user had the logic but reached out for Java syntax help (memo array init / helper plumbing). So this is **NOT a clean cold solve**. For an acquisition-only floor band, the self-derived recurrence installs the Linear DP mechanic, so the bucket is marked acquired — **but with this asterisk: it would NOT count as an ownership rep** (ownership requires a fully cold, no-assist, first-submission clean).
- Honest header counting (rule 7): record as *acquired, syntax-assisted*, not as a clean first-submission AC.

## What made it hard (debrief)

The 80% AR felt "fishy" because the AR reflects people who already know the two shortcut answers — but deriving it cold is genuinely non-trivial.

**1. Bottom-up (BUP) felt tough** — it is cleaner once you see it. Let `dp[v]` = number of sorted strings ending with vowel index `v` for the current length. Start all 1s (length 1), then each step replace `dp[v]` with the suffix-sum `dp[v] + dp[v+1] + ... + dp[4]`:

```java
public int countVowelStrings(int n) {
    int[] dp = {1, 1, 1, 1, 1};           // length 1: one string ending at each vowel
    for (int len = 2; len <= n; len++)
        for (int v = 3; v >= 0; v--)      // suffix sum from the right
            dp[v] += dp[v + 1];
    return dp[0] + dp[1] + dp[2] + dp[3] + dp[4];
}
```

O(n·5) time, O(5) space — no recursion. The "suffix sum from the right" is the BUP form of your `Σ_{i>=prev}`.

**2. The math you were chasing** — there *is* a closed form, and it's why this is a famous "aha": choosing a sorted length-`n` string from 5 vowels is exactly choosing a **multiset of size `n` from 5 types**, which is **stars and bars**:

```
C(n + 5 - 1, 5 - 1) = C(n + 4, 4)
```

Check: n=1 → C(5,4)=5 ✓; n=2 → C(6,4)=15 ✓. So the whole problem collapses to one binomial coefficient. Not seeing it cold is completely normal — stars-and-bars on a "count strings" problem is a disguised combinatorics identity, not an obvious move.

## Takeaways

- The memoized solve is correct and the state design was the right instinct.
- Reps to install: the **BUP suffix-sum** form (so DP-counting doesn't force recursion next time), and recognizing **multiset / stars-and-bars** when a problem says "non-decreasing / sorted selection from k types."
