# P — Hamming Distance (LC 461)

**Task:** the Hamming distance between two integers is the number of bit positions where they **differ**. Return it.

## Solution

```java
class Solution {
    public int hammingDistance(int x, int y) {
        int xor = x ^ y;
        int bits = 0;
        while (xor != 0) {
            if ((xor & 1) == 1) bits++;
            xor = xor >>> 1;
        }
        return bits;
    }
}
```

## The insight: "differ" is exactly XOR, then count the 1s

Two sub-problems chained:
1. **Where do `x` and `y` differ?** XOR's per-bit rule is "`1` when the bits differ." So `x ^ y` produces a number with a `1` in **exactly** the positions where `x` and `y` disagree — the differing positions are now marked as set bits.
2. **How many differ?** Count the set bits in `x ^ y` — which is just P1 (Number of 1 Bits), reused verbatim (`& 1` to read the lowest bit, `>>> 1` to advance).

So Hamming distance = popcount(`x ^ y`). The whole problem collapses to "turn *differ* into *set bit* via XOR, then run the set-bit counter."

*Status: clean self-derived AC. Composed two installed pieces — XOR-marks-differences (Sec. 3) + the `&1`/`>>>` set-bit walk (P1). First problem that **chains** two operator idioms rather than using one.*
