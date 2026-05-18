# 13 — Bit Manipulation

Java's `Integer` and `Long` classes ship a set of static methods that compile down to single CPU instructions on most JVMs (`LZCNT`, `TZCNT`, `POPCNT`, `BSR`). Always prefer these over hand-rolled shift-and-mask loops — faster, shorter, and harder to get wrong.

For 64-bit values, use `Long.*` versions of the same methods. `int` is 32 bits, `long` is 64 bits — this matters when computing bit-length (`32 - lz` vs `64 - lz`).

---

## Tier 1 — high-frequency contest methods

### `Integer.bitCount(n)` — popcount (count of set bits)

Returns the number of `1` bits in the 32-bit representation of `n`. Often called the Hamming weight.

```java
Integer.bitCount(5);    // 5 = 101 → 2
Integer.bitCount(7);    // 7 = 111 → 3
Integer.bitCount(0);    // 0
Integer.bitCount(-1);   // 32 (all bits set in two's complement)
```

**Where you'll meet it:** Hamming distance problems, subset-DP where you filter masks by their cardinality, "count numbers in [0,n] with exactly k set bits," etc.

---

### `Integer.numberOfTrailingZeros(n)` — position of lowest set bit

Returns the count of `0` bits below the lowest `1` bit. Equivalent to: "what bit position is the rightmost set bit at?"

```java
Integer.numberOfTrailingZeros(12);  // 12 = 1100 → 2 (lowest set bit is at index 2)
Integer.numberOfTrailingZeros(1);   // 1 = 0001 → 0
Integer.numberOfTrailingZeros(8);   // 8 = 1000 → 3
Integer.numberOfTrailingZeros(0);   // 32 (no set bits)
```

**THE bitmask DP idiom — memorize this pair:**

```java
// iterate through every set bit in mask, lowest to highest
int mask = 0b10110;  // bits 1, 2, 4 are set
while (mask != 0) {
    int bit = Integer.numberOfTrailingZeros(mask);  // 1, then 2, then 4
    // process bit position
    mask &= mask - 1;  // clears the lowest set bit
}
```

`mask &= mask - 1` is the classic "clear lowest bit" trick. Pairs perfectly with `numberOfTrailingZeros` for "iterate over set bits."

---

## Tier 2 — useful when the problem demands it

### `Integer.numberOfLeadingZeros(n)` — bit-length, next power of 2

Returns the count of `0` bits above the highest `1` bit. Used to compute the bit-length of `n` or to find the next power of 2.

```java
Integer.numberOfLeadingZeros(1);    // 31 (binary: 0...0001, 31 zeros before the 1)
Integer.numberOfLeadingZeros(8);    // 28 (binary: 0...01000)
Integer.numberOfLeadingZeros(0);    // 32

// bit-length of n (how many bits to represent n)
int bitLength = 32 - Integer.numberOfLeadingZeros(n);

// next power of 2 ≥ n (for n ≥ 1)
int nextPow2 = 1 << (32 - Integer.numberOfLeadingZeros(n - 1));
```

**Where you'll meet it:** range queries (sparse tables need `log2(n)`), bucketing by bit length, problems where XOR results are bounded by the bit-width of the input.

---

### `Integer.highestOneBit(n)` — value of the top bit

Returns the value (not position) of `n` rounded down to the nearest power of 2.

```java
Integer.highestOneBit(5);    // 4 (5 = 101 → topmost set bit is the 4)
Integer.highestOneBit(8);    // 8
Integer.highestOneBit(15);   // 8
Integer.highestOneBit(0);    // 0
```

**Use case:** "round down to nearest power of 2." Compare with `Integer.lowestOneBit(n)` below.

---

### `Integer.lowestOneBit(n)` — value of the bottom bit

Returns the value of the lowest set bit. Equivalent to the classic `n & -n` trick.

```java
Integer.lowestOneBit(12);   // 4 (12 = 1100 → lowest set bit value is 4)
Integer.lowestOneBit(7);    // 1 (7 = 0111)
Integer.lowestOneBit(0);    // 0
```

**Where you'll meet it:** Fenwick tree (BIT) updates and queries, where `i += i & -i` is the canonical step.

---

## Tier 3 — exist, just know they're there

### `Integer.toBinaryString(n)` — int → binary string

```java
Integer.toBinaryString(10);  // "1010"
Integer.toBinaryString(-1);  // "11111111111111111111111111111111"
```

No leading zeros. For padded output, use `String.format` or pad manually.

---

### `Integer.parseInt(s, 2)` — binary string → int

```java
Integer.parseInt("1010", 2);  // 10
Integer.parseInt("111", 2);   // 7
```

The second arg is the radix — works for bases 2 through 36.

---

### `Integer.reverse(n)` — reverse all 32 bits

```java
Integer.reverse(1);   // -2147483648 (the 1 bit moves from position 0 to position 31)
Integer.reverse(8);   // 268435456 (bit at position 3 moves to position 28)
```

Niche — used in problems like LC-190 "Reverse Bits."

---

## Long versions

All of the above have `Long.*` equivalents that operate on 64 bits. Reach for them when your bitmask exceeds 32 bits (more than 32 items in a state, or you're packing two 32-bit values into one long like in the prefix XOR + diff problem).

```java
Long.bitCount(mask);
Long.numberOfTrailingZeros(mask);
Long.numberOfLeadingZeros(mask);    // subtract from 64, not 32
Long.highestOneBit(mask);
Long.lowestOneBit(mask);
Long.toBinaryString(mask);
```

**Gotcha for bit-length on `long`:** `64 - Long.numberOfLeadingZeros(n)`, not 32. Easy to forget when you copy code from an `int` version.

---

## Quick reference table

| Method | Returns | Common use |
|--------|---------|------------|
| `bitCount(n)` | count of set bits | Hamming weight, mask filtering |
| `numberOfTrailingZeros(n)` | position of lowest set bit | bitmask DP iteration |
| `numberOfLeadingZeros(n)` | leading zeros | bit-length via `32 - lz` |
| `highestOneBit(n)` | value of top bit | next power of 2 |
| `lowestOneBit(n)` | value of bottom bit | Fenwick tree step (`n & -n`) |
| `toBinaryString(n)` | binary as string | print, manipulate as chars |
| `parseInt(s, 2)` | int from binary string | parse binary input |
| `reverse(n)` | bit-reversed value | bit-reversal problems |

---

## Packing two ints into one long — the bit-packing trick

Common pattern when you need a hashable key for an `(int x, int y)` pair (e.g., 2D coordinates in a HashSet). Idea: a `long` is 64 bits, an `int` is 32 bits → both fit, x in the top half, y in the bottom half.

### The naive attempt (broken)

```java
long key = ((long) x << 32) | y;   // WRONG when y is negative
```

Two pieces of context needed to understand why this breaks:

**1. Why `(long)` before the shift.**

`x << 32` operates on an `int`. Java's int shifts are taken modulo 32, so `x << 32` is `x << 0` = x unchanged. The cast forces a 64-bit shift, which actually moves x into bits 32-63.

**2. Why OR-ing `y` directly breaks for negatives.**

When `y` (an `int`) is widened to a `long` for the OR operation, Java performs **sign extension** — it copies the sign bit into all the new upper bits.

```
y = -1 as int                 1111 1111 1111 1111 1111 1111 1111 1111  (32 ones)
y widened to long             1111...1111 1111 1111 1111 1111 1111 1111 1111 1111  (64 ones)
```

Concrete collision: `(x = 0, y = -1)` and `(x = -1, y = -1)` both produce the all-ones long. Different pairs, same key — dedup fails.

### The fix — zero out y's upper 32 bits before OR-ing

Three equivalent ways, ordered most-readable → most-cryptic:

**Cleanest — use `Integer.toUnsignedLong`:**
```java
long key = ((long) x << 32) | Integer.toUnsignedLong(y);
```
The JDK built-in widens int to long treating the int as unsigned — no sign extension. Reads like English. **Preferred.**

**Computed mask:**
```java
long key = ((long) x << 32) | ((long) y & ((1L << 32) - 1));
```
Mask is `(1L << 32) - 1` — a long with the lower 32 bits set, upper 32 zero. AND-ing zeros out the extended sign bits.

**Hex literal mask:**
```java
long key = ((long) x << 32) | ((long) y & 0xFFFFFFFFL);
```
Same as above, mask written as a hex literal. Most compact, least obvious to readers.

### Why this is unique

After the fix:
- Top 32 bits of `key` = exactly the 32-bit pattern of `x`
- Bottom 32 bits of `key` = exactly the 32-bit pattern of `y`

Every distinct `(x, y)` produces a distinct long, regardless of sign. No range constants needed — works for any int values.

### When to use vs the multiplication trick

| Trick | Needs constant | Sign-safe | Speed |
|---|---|---|---|
| Multiplication `x * R + y` | Yes (R ≥ y range) | Yes (if R big enough) | Fast |
| Bit pack `(x << 32) \| toUnsignedLong(y)` | No | Yes | Fastest |

Bit pack wins when you don't know or don't want to compute the value range. Multiplication wins when the range is small and obvious (e.g., 200001 for `±10⁵` coords).

---

## When to extract vs inline

These methods are cheap — always inline them. Don't wrap `Integer.bitCount(n)` in a helper called `popcount(n)`. The JDK method names are the standard contest vocabulary; readers (and future you) already know them.

The one place to extract is when the bit operation is part of a larger predicate — e.g., `isValidMask(int mask)` that combines `bitCount`, parity checks, and value constraints. The helper hides the combination logic, not the individual bit ops.
