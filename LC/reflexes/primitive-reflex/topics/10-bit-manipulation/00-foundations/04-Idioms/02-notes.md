## 1. `x & (x - 1)` drops the lowest set bit

This is the first "magic" idiom — and it falls straight out of the Sec. 6B borrow shape.

Recall what `x - 1` does to the bits (Sec. 6B): the **lowest set bit** flips `1 → 0`, every `0` **below** it flips to `1`, and every bit **above** it is unchanged. Lay `x` and `x-1` side by side, using `1100` as a concrete case:

```
x     = 1 1 0 0
x - 1 = 1 0 1 1
        -------
x&(x-1)=1 0 0 0      ← lowest set bit (position 2) cleared
```

### Why it works for *every* `x` (not just this example)

Take any `x ≠ 0` and let its lowest set bit sit at position `p`. By the **definition** of "lowest set bit," `x` must have this shape — `1` at `p`, all `0`s below `p`, and some arbitrary pattern `H` above:

```
x     =  H…H   1   0…0   (p zeros below)
x - 1 =  H…H   0   1…1   (same H; bit p now 0; ones below)
```

AND them, region by region:

| Region | `x` | `x-1` | `x & (x-1)` |
|---|---|---|---|
| above `p` | `H` | `H` (unchanged) | `H` → **preserved** |
| at `p` | `1` | `0` | `0` → **cleared** |
| below `p` | `0` | `1` | `0` → stays `0` |

Result = `x` with bit `p` turned off, nothing else touched. We assumed **nothing** about `H` or `p`, so it holds for all `x`. The only fact used — "all zeros below the lowest set bit" — is true *by definition*.

Edge case `x = 0`: no set bit; `0 - 1 = -1 = …1111`, and `0 & (-1) = 0`. Returns `0`, no special-casing needed.

> **`x & (x - 1)` drops (clears) the lowest set bit.**

## 2. Power-of-two check

A power of two (`1, 2, 4, 8` = `1, 10, 100, 1000`) has **exactly one set bit**. So dropping that one bit must leave `0`:

```
x is a power of two  ⟺  x has one set bit  ⟺  (x & (x-1)) == 0
```

But "(x & (x-1)) == 0" alone is **not sufficient** — it also passes `x = 0` (zero set bits: `0 & -1 = 0`) and negatives like `MIN_VALUE`. A power of two must also be **positive**. So:

```java
return x > 0 && (x & (x - 1)) == 0;
```

> ⚠ **Parenthesize:** `(x & (x-1)) == 0`. In Java `==` binds *tighter* than `&`, so `x & (x-1) == 0` parses as `x & ((x-1)==0)` — wrong. [[lc-java-shift-precedence-trap]]

(This is the bit-native version of Power of Two, deferred from the Operators topic where it was first solved via `highestOneBit == lowestOneBit`.)

## 3. Power-of-four check

A power of four is also a power of two — `4^i = (2^2)^i = 2^(2i)` — so it still has exactly one set bit. The extra condition: that bit sits at an **even position** (`2i` is always even). Compare:

```
powers of 4:  1=0001, 4=0100, 16=010000, 64=01000000   ← bit at even position
pow2 not 4:   2=0010, 8=1000, 32=100000                ← bit at odd position
```

So: **power of two AND its single bit is at an even position.** To test "bit at an even position" without finding the exact position, AND with a mask that has `1`s at *every* even position at once. That mask is the constant `0x55555555`:

```
…0101 0101 0101 0101   (bits 0,2,4,… set)   each nibble = 0101 = 5
= 0x55555555           (eight 5's, hardcoded — O(1), no loop)
```

If the single bit lands on an even position it survives the AND (nonzero); on an odd position it's killed (zero).

```java
return n > 0 && (n & (n - 1)) == 0 && (n & 0x55555555) != 0;
```

Everything here is **O(1)**: the power-of-two check is one AND, the even-position check is one AND with a compile-time constant. (For a 64-bit `long`, the mask is `0x5555555555555555L`.)

Arithmetic alternative: powers of four satisfy `n % 3 == 1`, so `n > 0 && (n & (n-1)) == 0 && n % 3 == 1` also works — but the mask version is the bit-native one.

## 4. `x & -x` isolates the lowest set bit

The companion to `x & (x-1)`: where that one *drops* the lowest set bit, `x & -x` *keeps only* it. It's built on `-x = ~x + 1` (Sec. 4).

Work it on `x = 1100`:

```
x      = 1 1 0 0
~x     = 0 0 1 1        (flip every bit, Sec. 4)
-x     = 0 1 0 0        (~x + 1)
         -------
x & -x = 0 1 0 0        ← only the lowest set bit (position 2) survives
```

### Why only the lowest set bit survives

Compare `x` and `-x`, split at the lowest set bit (position 2 here):

```
x  = 1 | 1 0 0
-x = 0 | 1 0 0
     ↑   └─┬─┘
   above   at-and-below the lowest set bit
```

- **at and below** the lowest set bit: `x` and `-x` are **identical** (`100` = `100`).
- **above** the lowest set bit: `x` and `-x` are **opposite** (one is `1`, the other `0`).

That split is exactly what flip-then-add-1 produces: `~x` flips everything, then `+1` ripples a carry up through the low run of `1`s (the flipped trailing zeros), turning them back to `0` and landing a `1` right on the lowest-set-bit position — which re-aligns the bottom region with `x`, while the top region stays flipped.

AND the two:
- **above** (opposite bits): `1 & 0 = 0` → whole top region cleared.
- **at** the lowest set bit (`1` in both): `1 & 1 = 1` → survives.
- **below** (both `0`): `0 & 0 = 0`.

So the only bit that is `1` in *both* `x` and `-x` is the lowest set bit — everything else dies.

> **`x & -x` isolates the lowest set bit** (a number with just that one bit). Also called **lowbit** — the core step of Fenwick / Binary Indexed Trees.

### The matched pair

| Idiom | Effect on the lowest set bit |
|---|---|
| `x & (x - 1)` | **drops** it (clears → 0), keeps the rest |
| `x & -x` | **isolates** it (keeps only it, clears the rest) |

⚠ Edge: `x & -x` on `Integer.MIN_VALUE` returns `MIN_VALUE` (its lowest set bit *is* the sign bit) — fine as a bit pattern, watch arithmetic use. And `0 & -0 = 0` (no set bit to isolate).

## 5. Low-`k` mask and keep / clear low `i` bits

### The low-`k` all-ones mask: `(1 << k) - 1`

Straight from the pieces you have: `1 << k` = `2^k`, and from Sec. 6 `2^k − 1` = a run of `k` ones. So:

```
(1 << 3) - 1 = 1000 - 1 = 0111      (bits 0,1,2 set)
```

> **`(1 << k) - 1`** = `k` ones in the low positions (bits `0 .. k-1`). The general-purpose "bottom-`k`-bits" mask.

### Keep / clear the low `i` bits

With that mask (i ones at the bottom, zeros above):

- **keep** only the low `i` bits (zero everything above): `x & ((1 << i) - 1)` — AND keeps where the mask is `1`.
- **clear** the low `i` bits (zero the bottom, keep above): `x & ~((1 << i) - 1)` — invert the mask (`0`s at bottom, `1`s above) and AND.

> **Keep low `i`:** `x & ((1<<i) - 1)` · **Clear low `i`:** `x & ~((1<<i) - 1)`.

The clear-mask uses the same "invert to swap keep↔clear" move as clearing a single bit (`~(1<<i)` in Single-Bit-Ops Sec. 4) — just a wider mask.

⚠ **Precedence:** subtraction binds *tighter* than `&` in Java, so `(1<<i) - 1 & x` does parse as `((1<<i)-1) & x` — but always parenthesize the mask explicitly (`x & ((1<<i)-1)`) so intent is unmistakable. [[lc-java-shift-precedence-trap]]

⚠ **Width:** `(1 << k) - 1` for `k = 32` is wrong on `int` (`1<<32` wraps mod 32 → `1`, giving mask `0`). For a full 32-bit mask use `-1` (all ones) or `1L`.

### Number complement = the same mask, XOR'd

Flipping every bit *within a width* (Operators P5 / atom 0.13) is just XOR with this mask: `x ^ ((1 << bits) - 1)`. Nothing new — `(1<<k)-1` builds the width-matched all-ones, and `^` flips (Sec. 3).

## 6. Char case bit (ASCII bit 5)

Characters are stored as numbers (ASCII), so bit ops work on them. The key fact: **uppercase and lowercase of the same letter differ in exactly one bit — bit 5 (value 32).**

```
'A' = 65 = 0100 0001
'a' = 97 = 0110 0001
                ↑ bit 5
```

`97 − 65 = 32 = 2^5`. This is by design: ASCII puts uppercase in a 32-wide block starting at `64` and lowercase in one starting at `96`, so the two blocks differ only in bit 5. The offset is `32` (a power of two = one bit), **not** `26`, precisely so case conversion is a single bit flip instead of an addition. (The 6 leftover slots per block, codes 91–96, hold punctuation `[ \ ] ^ _ \``.)

### Convert / test case = set / clear / toggle bit 5

Lowercase has bit 5 = `1`, uppercase has bit 5 = `0`. So the Single-Bit-Ops verbs on bit 5 (mask `32`) do all the case work — directly on `c`, no pre-masking (setting bit 5 leaves every other bit untouched):

| Goal | Idiom |
|---|---|
| to **lowercase** (set bit 5) | `c \| 32` |
| to **uppercase** (clear bit 5) | `c & ~32` |
| **toggle** case (flip bit 5) | `c ^ 32` |
| **is lowercase?** (test bit 5) | `(c & 32) != 0` |
| **is uppercase?** | `(c & 32) == 0` (and it's a letter) |

Trace `'A' → lowercase`:
```
65 = 0100 0001
32 = 0010 0000
 |  ----------
     0110 0001  = 97 = 'a'   ✓   (only bit 5 changed)
```

### Letter → alphabet index 1–26: `c & 31`

Because each block starts at a multiple of 32 (low 5 bits all zero), the letter's position **1–26 lives entirely in the low 5 bits**. Mask them off with `31` (`= 0b11111 = (1<<5)-1`, the "keep low 5 bits" idiom from Sec. 5):

```
'A' = 65 = 0100 0001,  65 & 31 = 00001 = 1
'C' = 67 = 0100 0011,  67 & 31 = 00011 = 3
'z' = 122= 0111 1010, 122 & 31 = 11010 = 26
```

`c & 31` gives the index 1–26 for **either** case — the high case/block bits are masked away. (Works only because the block offset is a power of two.)

> **Case bit (bit 5 = 32):** `c | 32` lower · `c & ~32` upper · `c ^ 32` toggle · `(c & 32)` tests case · **`c & 31`** → alphabet index 1–26.

## 7. `x | (x + 1)` sets the rightmost unset bit

The mirror of `x & (x-1)`: where that clears the rightmost **set** bit, this sets the rightmost **unset** (`0`) bit.

```
x        = 1 0 1 1
x + 1    = 1 1 0 0        (carry ripples through the trailing 1s)
x|(x+1)  = 1 1 1 1        ← bit 2 (the rightmost 0) turned on
```

Why: `x + 1` carries through the trailing `1`s — flipping them to `0` and turning the first `0` into a `1`. OR-ing with the original `x` restores those trailing `1`s (they're `1` in `x`) and keeps the newly-created `1`, so the only net change is the rightmost `0` becoming `1`.

> **`x | (x + 1)`** sets the rightmost `0` bit. (Mirror of `x & (x-1)`, which clears the rightmost `1` bit.)
