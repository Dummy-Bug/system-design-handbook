# P1 — Number of 1 Bits (LC 191)

**Task:** count the `1` bits in a non-negative integer `n`. `11 = 1011 → 3`.

**Solution (self-derived, clean AC):**
```java
class Solution {
    public int hammingWeight(int n) {
        int setBits = 0;
        final int BASE = 2;
        while (n > 0) {
            setBits += n % BASE;
            n = n / BASE;
        }
        return setBits;
    }
}
```
Tooling used: only the `%2` / `/2` digit-peeling loop from Foundations Sec. 7 — **no bitwise operators**.

### The understanding

1. **Magnitude vs representation.** A quantity like *eleven* is the same thing in every base — `11` (dec), `13` (oct), `B` (hex), `1011` (bin). Only the *spelling* changes. We never convert `n` to a string; we operate on the quantity.

2. **`% b` extracts the last base-`b` digit; `/ b` drops it.** This is the engine. Dividing by the **base** is what exposes digits *in that base*:
   - `n % 2` → lowest **binary** bit, `n / 2` → drop it (what we used here).
   - `n % 8` / `n / 8` → octal digits; `n % 16` / `n / 16` → hex digits.
   - **The loop is base-agnostic — the divisor is the only knob.** Count octal digits instead of bits? Change `BASE` to 8. Nothing else moves.

3. **Conversion and reading are the *same* loop.** We don't build `1011` and then scan it. Each `% 2` *produces* the next binary digit live, and we count the `1`s as they fall out. The binary string never exists in memory. (Contrast Sec. 7, where we *collected + reversed* the remainders to build the number; here we only need the count, so we discard them.)

   **Generalized — the `%b` / `/b` loop *is* the base-`b` digit iterator.** Running it always walks the number's base-`b` digits, lowest-first; the conversion is happening whether or not you save the output. The only thing that varies is the **consumer** of each digit:
   - *keep & collect* (reverse at the end) → you've **built** the representation (Sec. 7 conversion).
   - *inspect & discard* → you **examine** the representation without storing it (count `1`s here; check alternating bits; sum digits; …).

   So this is a reusable **recognition trigger**:
   > process a number's digits in base `b` → `while (n > 0) { digit = n % b; n /= b; }`
   > — decimal digit problems (digit sum, reverse number, palindrome number, digit-DP) → `%10`, `/10`; binary → `%2`, `/2`; any base → swap the divisor.

   A whole class of "do something per digit / per bit" problems collapses to this one loop.

4. **`n % 2` is the odd/even test.** "Is `n` odd?" ⟺ "is the lowest bit `1`?" The first (wrong) instinct was `% 10` — right idea (check the last digit), wrong base. Swapping to `% 2` makes the odd/even intuition exactly correct.

5. **Idiom:** `setBits += n % 2` (no `if`). Since `n % 2 ∈ {0,1}`, the test and the count fuse into one line.

### Where it breaks: negative `n` (and why no patch saves it)

The `%2` / `/2` solution is correct **only for `n ≥ 0`**. For negative `n` it fails at the root:
- `while (n > 0)` never even enters (the sign makes the condition false), so the loop reads **zero** bits.
- Even with `while (n != 0)`, Java's `%` keeps the dividend's sign (`-3 % 2 = -1`) and `/` rounds toward zero — neither walks the *stored* two's-complement bits. `/2` is **arithmetic division** (about value), not bit-dropping; the two only coincide for non-negatives.

By Sec. 9, `-3` is stored as `1111…1101` → its true bit count is **31** (32 bits, one `0`).

**Patches we tried — all failed, and the failures are the lesson:**

| Patch | On `-3` | On `-2` (truth = 31) | Verdict |
|---|---|---|---|
| `return setBits - 1` | loop ran 0×, `0-1 = -1` | −1 | ✗ off by *everything* |
| `count bits of Math.abs(n)` | `abs(-3)=3` → 2 | `abs(-2)=2` → 1 | ✗ (2 vs 31, 1 vs 31) |
| `32 - (setBits(abs(n)) - 1)` | `32-(2-1) = 31` ✓ | `32-(1-1) = 32` | ✗ (works for −3 by luck, fails −2) |

**Why every patch is doomed:** they all compute the answer for `n` **from `abs(n)`** — the positive version. But `+3 = 0000…0011` (2 ones) and `−3 = 1111…1101` (31 ones) are **unrelated** bit patterns. The reason they're unrelated: two's complement is `~m + 1`, and that `+1` ripples through a *different* number of trailing bits for each value (depends on `m`'s trailing zeros) — so there is **no fixed formula** from `popcount(|n|)` to `popcount(n)`.

**The real fix (not a cleverer formula):** stop deriving the bits from `|n|` — just **read `n`'s actual stored bits directly**, one at a time, regardless of sign. That needs tools that view *raw bits* instead of doing value-arithmetic:
- `n & 1` → the lowest stored bit (sign-blind)
- `n >>> 1` → drop it, walking all 32 bits (unsigned shift, fills with 0)

`&` and `>>>` are **operators** — the next section. → **Deferred to operators; redo this problem the operator way there.**

*Status: clean self-derived AC for `n ≥ 0`. Negative/unsigned case: patches proven dead-end (computing from `|n|` can't work); correct fix = raw-bit reading via `&` / `>>>`, deferred to the operators section.*
