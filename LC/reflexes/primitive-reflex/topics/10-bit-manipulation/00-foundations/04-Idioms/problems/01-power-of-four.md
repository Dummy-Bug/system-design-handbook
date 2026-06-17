# P — Power of Four (LC 342)

**Task:** return whether `n` is a power of four (`1, 4, 16, 64, …`). `n` may be `0` or negative.

## Accepted solution

```java
class Solution {
    public boolean isPowerOfFour(int n) {
        if (n <= 0) return false;
        int evenMask = 0x55555555;
        return ((n & (n - 1)) == 0) && ((n & evenMask) != 0);
    }
}
```

## The insight: power of two AND the single bit is at an even position

`4^i = (2^2)^i = 2^(2i)` — so a power of four is a power of two whose lone set bit sits at an **even** position (`2i` is always even):

```
powers of 4:  1=0001, 4=0100, 16=010000   ← even position
pow2 not 4:   2=0010, 8=1000, 32=100000   ← odd position
```

Three conditions, each O(1):
1. **positive** — `n > 0` (rejects `0` and negatives, the necessary-not-sufficient guard).
2. **power of two** — `(n & (n-1)) == 0` (drops the lowest set bit; for one-bit numbers that empties it).
3. **bit at even position** — `(n & 0x55555555) != 0`. `0x55555555` is the constant with `1`s at every even position (`…0101 0101`, each nibble = `5`). If the single bit is even-positioned it survives the AND (nonzero); if odd-positioned it's killed. Hardcoded constant → no O(bits) mask-building loop.

## Why no position extraction
Rather than *finding* which position the bit is at (which would cost an extra step like counting trailing zeros, then checking parity), the even-positions mask tests "is the bit on *any* even position?" in one AND. Build the test as a single constant, not a search.

> ⚠ Parenthesize: `(n & (n-1)) == 0` — `==` binds tighter than `&` in Java. [[lc-java-shift-precedence-trap]]

*Status: clean self-derived AC. Uses Idioms §1 (`x & (x-1)` drops lowest set bit) + §3 (power-of-four = pow2 on even position via `0x55555555`). Also exercises the `n & (n-1)` power-of-two mechanic (closes the rep deferred from Operators).*
