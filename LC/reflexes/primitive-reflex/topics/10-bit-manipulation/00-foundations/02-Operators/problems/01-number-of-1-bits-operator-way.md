# P1 (redo) — Number of 1 Bits, the operator way (LC 191)

**Task:** count the set bits (`1`s) in the binary representation of `n`.

This is the **operator version** of the P1 we first solved arithmetically in `01-Number-System/problems/01-number-of-1-bits.md`. That version used `%2`//`2` and could not handle a negative `n`; this one fixes it with `& 1` + `>>>`.

## Solution

```java
class Solution {
    public int hammingWeight(int n) {
        int setBits = 0;
        while (n != 0) {
            if ((n & 1) == 1) setBits++;
            n = n >>> 1;
        }
        return setBits;
    }
}
```

## The two operators doing the work

- **`n & 1`** reads the **lowest bit** as a raw bit (`0` or `1`). It masks away every place value except `2^0`, leaving exactly that bit. (Compare the arithmetic version's `n % 2` — for a *negative* `n` in Java, `n % 2` returns `-1` or `0` following the sign of the dividend, so it doesn't even report the bit correctly. `n & 1` always gives the true lowest bit.)
- **`n >>> 1`** advances to the next bit by walking down the raw 32-bit pattern, zero-filling from the top.

## Why `>>>` and not `>>` (the whole point of the redo)

`>>` fills the vacated top with the **sign bit**. For a negative `n` (top bit `1`), those `1`s keep regenerating — `n` collapses to `−1` (all ones) and **never reaches `0`**, so `while (n != 0)` spins forever.

`>>>` zero-fills, so the leading `1`s drain away one per shift and `n` is guaranteed to hit `0` in ≤ 32 steps. The loop terminates for **any** input, positive or negative.

This is exactly the §6/§7 sign-fill-vs-zero-fill distinction, and it closes the negative-`n` cliffhanger the arithmetic (`n / 2`) version left open.

*Status: clean self-derived AC. Identified the `>>>`-over-`>>` requirement unprompted ("or else the loop will never have stopped"). Closes Operators install-check item (redo P1 the operator way).*
