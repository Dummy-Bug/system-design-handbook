# P — Reverse Bits (LC 190)

**Task:** reverse the order of the 32 bits of `n`. Bit 0 ↔ bit 31, bit 1 ↔ bit 30, etc. (No bit *value* changes — only its position mirrors end-to-end.) The result is read as a raw 32-bit pattern (treat-as-unsigned), so a negative return is correct.

**Reverse ≠ flip.** Flip (`~`) changes each bit's value in place (`0↔1`). Reverse keeps values, mirrors positions.

## Accepted solution

```java
class Solution {
    public int reverseBits(int n) {
        int i = 0, j = 31, num = 0;
        while (i < j) {
            int b1 = (n >> i) & 1;
            int b2 = (n >>> j) & 1;
            num |= b1 * (1 << j);
            num |= b2 * (1 << i);
            i++;
            j--;
        }
        return num;
    }
}
```

Two pointers walk inward (`i` up from 0, `j` down from 31). Each step reads the two mirror-position bits and writes each into the other's slot: bit `i` → position `j`, bit `j` → position `i`. Loop ends at `i < j` (32 bits = 16 pairs, no middle element).

## The idiom: read a bit, write a bit

- **Read** bit at position `p`: `(x >> p) & 1` — shift it down to the bottom, mask off everything else. (`>>` vs `>>>` doesn't matter once you `& 1`.)
- **Write** bit value `b` into position `q`: `|= (b << q)` — shift the bit up to its slot and OR it in.

Extract-and-place — the two halves of moving bits around. This pair is reused constantly.

## Three bugs hit on the way (all worth banking)

**Bug 1 — not isolating the bit.** First attempt used `(n >> i) == 1`. `n >> i` shifts the *whole* number; comparing to `1` is only true when everything above bit `i` is zero. To read a single bit you **must mask**: `(n >> i) & 1`. (Trace `n=3, i=0`: `3 >> 0 = 3`, `3 == 1`? no → wrongly reports bit 0 as `0`.)

**Bug 2 — `Math.pow` overflows and clamps.** Original built place values with `(int) Math.pow(2, j)`. At `j = 31`, `2^31 = 2147483648` exceeds `Integer.MAX_VALUE`, and casting the `double` down **clamps to `2147483647`** (`0111…1`) — the wrong bit pattern. `Math.pow` returns a positive `double` and can *never* produce the sign-bit pattern.

The fix is `1 << j`. **Shifts wrap to the exact bit pattern; `Math.pow` + cast clamps to a wrong magnitude:**

| | result | right 32 bits? |
|---|---|---|
| `(int) Math.pow(2,31)` | `2147483647` = `0111…1` | ❌ |
| `1 << 31` | `−2147483648` = `1000…0` | ✅ exactly bit 31 |

`1 << 31` "overflows" only in that the *value* `2^31` doesn't fit as a positive `int` — but it wraps to `MIN_VALUE`, whose **bits** are exactly "only bit 31 set," which is precisely correct. Since the problem scores the bit pattern (not the signed decimal), the negative result is the right answer.

> **Rule: for bit work, build place values with `1 << k`, never `Math.pow`.** Shifts give exact integer bit patterns (incl. the sign bit); floating-point powers overflow and clamp.

**Bug 3 (rabbit hole avoided) — special-casing the sign.** When `Math.pow` broke at bit 31, the instinct was to special-case `n < 0` and the edge bits (`i=1, j=30`). Wrong fix — the loop bounds were fine; the *only* problem was `Math.pow`. Replacing it with `1 << j` removes the need for any sign branch, because `1 << 31` produces the sign-bit pattern automatically.

## The "AC ≠ correct" catch (the real lesson)

The buggy `Math.pow` version **got Accepted** — because the problem's constraints (`0 ≤ n ≤ 2^31 − 2`, *n is even*) hid the bug:

- output bit 31 comes from input bit 0; **`n` even → bit 0 = 0** → the overflowing `2^31` term is always `× 0` → harmless.
- input bit 31 is never set (`n ≤ 2^31 − 2`), so that side contributes nothing either.
- every other power is `≤ 2^30`, which fits in `int` fine.

So the poison term existed but its coefficient was always `0`. Feed an **odd** `n` (e.g. `n=1`, which should set output bit 31) and it breaks instantly.

> **AC ≠ correct.** A green check means "passed *these* tests under *these* constraints," not "the algorithm is sound." A latent bug can hide behind a constraint and silently resurface when the idea is reused without it. `1 << k` is correct *regardless* of constraints; `Math.pow` only happened to survive this one.

## `+=` vs `|=` for assembling bits

Because each position is set **at most once**, `+` and `|` give identical results — but `|=` is better:
- `+=` relies on no-collision; a double-write would **carry** and corrupt neighbours.
- `|=` is **idempotent** — a double-write just leaves the bit set, no carry.

And since `b ∈ {0,1}`, `b * (1 << j)` simplifies to `(b << j)`:
```java
num |= (b1 << j);
num |= (b2 << i);
```

*Status: AC. First problem requiring real debugging in this topic — 3 mechanical bugs (mask, Math.pow overflow, sign rabbit-hole), all implementation-rust, mapping was sound. Headline insights: `1 << k` not `Math.pow` for place values; AC ≠ correct (constraint-masked bug); read `(x>>p)&1` / write `|=(b<<q)` idiom; `|=` over `+=` for bit assembly.*
