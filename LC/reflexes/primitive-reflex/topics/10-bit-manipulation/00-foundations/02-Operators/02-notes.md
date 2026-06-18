## 0. Operators work per-bit

The Number System section dealt with a number as a single *value*Operators look at a number as a **row of bits** and act on those bits directly.

The key idea for the bitwise-logic operators (`&`, `|`, `^`, `~`): line two numbers up in columns, and **each output bit depends only on the two bits sitting in that same column.** The columns do not talk to each other — there is no carry, no borrow, nothing rippling sideways (unlike ordinary addition). Column 3's result is decided by column 3 alone.

That independence is what makes these operators so useful: you can reason about one bit at a time.

## 1. AND (`&`)

The per-column rule:

> An output bit is `1` **only when both** input bits are `1`. In every other case it is `0`.

As a truth table for a single column:

| a | b | a & b |
|---|---|-------|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | **1** |

Worked example — `6 & 3`:

```
6 = 0110
3 = 0011
    ----
    0010   = 2
```

Going column by column from the right: `0&1=0`, `1&1=1`, `1&0=0`, `0&0=0` → `0010` = 2.

### AND is the "masking" operator

The real power of `&` shows up when you treat **one operand as a filter** (a *mask*) over the other. Look again at `6 & 3`, reading `3 = 0011` as the mask:

```
6 = 0110
3 = 0011   ← mask
    ----
    0010
```

In each column, two things can happen depending on the mask bit:

- **mask bit `1` → pass through.** The other number's bit survives unchanged — whatever it was, `0` or `1`. (Column 1: mask `1`, 6's bit `1` → stays `1`. Column 0: mask `1`, 6's bit `0` → stays `0`.)
- **mask bit `0` → clear.** The position is forced to `0`, no matter what the other bit was. (Column 2: mask `0`, 6's bit `1` → killed to `0`.)

So the one-line summary:

> `&` is a per-bit gate: **mask bit `1` keeps**, **mask bit `0` clears.** Let some bits survive, zero the rest — that is *masking*.

### Idiom: `n & 1` is the odd/even test

If you only care about a number's **lowest bit**, AND it with a mask that has a single `1` in the lowest position — that mask is just `1` (`…0001`). Everything above the lowest place value gets cleared, leaving only the `2^0` (ones) place:

- `n & 1 = 1` → the ones place is set → `n` is **odd**
- `n & 1 = 0` → the ones place is clear → `n` is **even**

This works precisely because `&` masks away every place value except `2^0`, so what's left is exactly the parity bit. (Note `n & 1` returns the *value* of that bit — `0` or `1` — not always `1`.)

### Two masks to know cold

| Expression | Result | Why |
|---|---|---|
| `n & 0` | `0` | an all-zero mask clears every bit — nothing survives |
| `n & (all ones)` | `n` | an all-one mask keeps every bit — `n` passes through unchanged |

`all ones` means a mask filled with `1`s across the width you care about (e.g. `1111` for 4 bits). These are the two extremes of masking: clear everything, or keep everything.

## 2. OR (`|`)

The per-column rule:

> An output bit is `1` when **either** input bit is `1` — so it is `0` **only when both** are `0`.

Truth table for a single column:

| a | b | a \| b |
|---|---|--------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 1 |

Worked example — `6 | 3`:

```
6 = 0110
3 = 0011
    ----
    0111   = 7
```

Column by column from the right: `0|1=1`, `1|1=1`, `1|0=1`, `0|0=0` → `0111` = 7.

### OR is the "setting" operator

Treat one operand as the mask again, reading `3 = 0011`:

```
6 = 0110
3 = 0011   ← mask
    ----
    0111
```

- **mask bit `1` → set.** The position is forced to `1`, no matter what the other bit was.
- **mask bit `0` → pass through.** The other number's bit survives unchanged.

So:

> `|` is a per-bit gate: **mask bit `1` forces the position to `1` (set)**, **mask bit `0` keeps the other bit.** OR turns chosen bits *on* and leaves the rest alone.

### The duality with AND

AND and OR are mirror images — they just keep on **opposite** mask values:

| | mask bit `1` | mask bit `0` |
|---|---|---|
| `&` (clear-tool) | keep | **clear → 0** |
| `\|` (set-tool) | **set → 1** | keep |

`&` clears where the mask is `0`; `|` sets where the mask is `1`. Pick the operator by the job: need to *turn bits off* → AND with a mask; need to *turn bits on* → OR with a mask.

### Two masks to know cold

| Expression | Result | Why |
|---|---|---|
| `n \| 0` | `n` | an all-zero mask sets nothing — `n` passes through unchanged (identity) |
| `n \| (all ones)` | `all ones` | an all-one mask forces every bit on |

Note the extremes are swapped versus AND: for `&` the *all-ones* mask is the identity; for `|` it is the *all-zero* mask that is the identity.

## 3. XOR (`^`)

XOR means *exclusive* or — "one or the other, but not both." The per-column rule:

> An output bit is `1` when the two input bits **differ**; `0` when they are the **same**.

Truth table for a single column:

| a | b | a ^ b |
|---|---|-------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

Worked example — `6 ^ 3`:

```
6 = 0110
3 = 0011
    ----
    0101   = 5
```

Column by column from the right: `0^1=1`, `1^1=0`, `1^0=1`, `0^0=0` → `0101` = 5.

### XOR is the "toggling" operator

Read `3 = 0011` as the mask:

```
6 = 0110
3 = 0011   ← mask
    ----
    0101
```

- **mask bit `1` → flip.** The other number's bit is toggled (`0→1`, `1→0`).
- **mask bit `0` → keep.** The other bit passes through unchanged.

So:

> `^` is a per-bit gate: **mask bit `1` flips (toggles)** the other bit, **mask bit `0` keeps it.** XOR is the **toggling** operator.

### The whole family in one table

All three bitwise-logic gates keep the other bit on one mask value and do their action on the other:

| | mask bit `1` | mask bit `0` | job |
|---|---|---|---|
| `&` | keep | **clear → 0** | turn bits *off* |
| `\|` | **set → 1** | keep | turn bits *on* |
| `^` | **flip** | keep | *toggle* bits |

### Two masks to know cold

| Expression | Result | Why |
|---|---|---|
| `n ^ 0` | `n` | mask of `0`s flips nothing — `n` passes through (identity) |
| `n ^ (all ones)` | flip every bit (`~n` within that width) | mask of `1`s toggles every position |

### The headline property: XOR is its own inverse

XOR with itself wipes to zero, because every column has two equal bits and "same → `0`":

> `x ^ x = 0`

Combined with the identity `x ^ 0 = x`, this means XOR-ing by the same value **twice cancels out**:

> `a ^ b ^ b = a ^ (b ^ b) = a ^ 0 = a`

XOR undoes itself. Apply `^ b` once and it's "encrypted"; apply `^ b` again and you're back to the original — there is no separate inverse operator, XOR *is* its own inverse.

The consequence that powers a whole class of problems: XOR a pile of numbers together, and **anything that appears an even number of times cancels to `0`**, leaving only the odd-occurrence value behind. (That's the trick behind finding the lone unpaired number in O(1) space — developed later; here we only install the property.)

Identities to hold cold:

> `x ^ x = 0` · `x ^ 0 = x` · self-inverse: `a ^ b ^ b = a`.

## 4. NOT (`~`)

`~` is the only **unary** operator here — it takes a single operand (no mask, no second number). The rule:

> flip **every** bit: `0 → 1`, `1 → 0`.

Example in 4 bits:

```
~ (0101) = 1010
```

Flipping all bits is exactly the **one's complement** from Sec. 9 (the `1111 − x` step that never borrows).

### What `~x` equals as a value: `−x − 1`

Two's complement defined `−x = ~x + 1`. Rearranged, that tells us the *value* of `~x`:

> `~x = −x − 1`

So flipping every bit is **not** the same as negating — it lands one short of `−x`. That off-by-one is precisely the `+1` that two's complement adds back.

Check with `x = 5` (4 bits):
- `~5`: `0101 → 1010`, and `1010` in two's complement = `−8 + 2 = −6`.
- formula: `−x − 1 = −5 − 1 = −6`. ✓

Quick values: `~0 = −1` · `~5 = −6` · `~(−1) = 0`.

### Width caveat (real `int`)

In a true 32-bit `int`, `~` flips **all 32 bits**, not just the low 4. So `~5` is not `1010` but `…11111010` — the leading zeros become leading ones. The *value* is unchanged (`−6`), because the negative-place-value top bit accounts for all those high `1`s. The 4-bit view is just a convenient window; the `~x = −x − 1` identity holds at any width.

---

# Group B — Shifts (`<< >> >>>`)

The Group A operators combined two numbers column by column. Shifts are different: they **slide all the bits of one number sideways** by `k` positions. Because sliding a bit changes which place value it sits in, shifts have a clean *arithmetic* meaning — they multiply or divide by powers of two.

## 5. Left shift (`<<`)

> `x << k` slides every bit **left** by `k` positions, filling the vacated right side with `0`s.

Example in 4 bits — `3 << 1`:

```
3 = 0011
3 << 1 = 0110   = 6      (each bit moved one place left, a 0 filled in on the right)
```

`3` became `6` — it **doubled**. In general:

> `x << k` = `x × 2^k`.

The reason is place value (Sec. 3 of the Number System notes). Sliding a bit left by one position moves it from place value `2^i` to `2^(i+1)` — it now contributes twice as much. Every bit doubles, so the whole number doubles. (This is the same move as the `2S` doubling trick used to prove `2^k − 1`: multiplying by 2 *is* a left shift.)

### ⚠ The fixed-width traps in `<<`

A left shift assumes nothing about whether the result still fits in the type's width — and when it doesn't, the failure is **silent** (no error, just a wrong value). Two distinct traps, same root cause (fixed width).

**Trap 1 — `1 << 31` comes out negative.** Write `1` in full 32-bit form and slide the lone `1` bit left by 31:

```
1        = 00000000 00000000 00000000 00000001   (bit at position 0)
1 << 31  = 10000000 00000000 00000000 00000000   (bit at position 31)
```

Position 31 is the **top bit**, and from Sec. 9 its place value in two's complement is **`−2^31`**, not `+2^31`. So:

```
1 << 31  =  −2^31  =  −2147483648  =  Integer.MIN_VALUE
```

You almost certainly *wanted* `+2^31 = 2147483648`, but that value does not fit in an `int` (max is `2^31 − 1`). The bit landed on the sign bit and the number went negative — the same silent overflow as `abs(MIN_VALUE)` in Sec. 9.

*When it actually hurts:* if you build a mask `1 << i` only to **test or set a bit**, the bit *pattern* is still correct, so masking works even at `i = 31`. It bites only when the shifted value is used in **arithmetic** — e.g. `sum += 1 << 31` adds roughly minus-two-billion instead of plus-two-billion.

**Trap 2 — `1 << 32` is `1`, not `0`.** Intuitively, sliding a single bit left by 32 in a 32-bit number should push it off the end and leave `0`. It does not. Java reduces the shift amount **mod 32** for `int` (only the low 5 bits of the count are used, and 5 bits cover `0…31`):

```
1 << 32   →   1 << (32 mod 32)   →   1 << 0   =   1
1 << 33   →   1 << 1             =   2
```

So any shift of `32` or more silently **wraps around** instead of zeroing. (For `long`, the rule is mod **64**.) This is exactly how a loop like `for (i = 0; i <= 32; i++) mask = 1 << i;` goes wrong — the `i = 32` iteration quietly produces `1` again, not `0`.

**The fix — use a `long` literal `1L << k`:**

```
1L << 31  =  +2147483648    (positive and correct — bit 31 is an ordinary place value in a 64-bit long)
1L << 32  =  4294967296     (a real shift, no wrap — long wraps at mod 64)
```

`1L` is 64 bits wide, so its sign bit is at position **63** and shifts wrap at 64. Bit 31 is just a normal positive place value there. **Rule of thumb: the moment you shift past bit 30, write `1L << k`** (and narrow back to `int` only once you're sure the result fits).

Both traps are the same lesson as Sec. 8–Sec. 9: an `int` has exactly 32 fixed slots, and a shift that assumes more than that wraps silently.

## 6. Right shift (`>>`) — arithmetic, sign-filling

> `x >> k` slides every bit **right** by `k` positions.

Example in 4 bits — `12 >> 1`:

```
12 = 1100
12 >> 1 = 0110   = 6      (= 12 / 2)
```

So right shift **divides** by powers of two:

> `x >> k` = `⌊x / 2^k⌋` — integer division, rounding **down** (toward −∞).

But there's a subtlety left shift didn't have: when bits slide right, what fills the **vacated left side**? The answer is forced by wanting division to keep working on **negatives**.

Take `−4 = 1100` and ask for `−4 >> 1`, which should be `−4 / 2 = −2`. We know `−2 = 1110`. Slide `1100` right by 1 and see what the new top bit must be:

```
1100 >> 1  →  ?110
```

- Fill the left with `0` → `0110 = +6`. **Wrong** — the sign flipped to positive.
- Fill the left with `1` → `1110 = −2`. **Correct.**

So to preserve sign, the vacated bits must be filled with a **copy of the sign bit** (`0` for positives, `1` for negatives). This is called an **arithmetic right shift**, and it is what Java's `>>` does:

> `>>` fills the left with the **sign bit**, which keeps the sign correct and makes `>>` match `⌊x / 2^k⌋` even for negatives.

## 7. Unsigned right shift (`>>>`) — logical, zero-filling

The `0`-fill we just rejected for division is itself a real, separate operator: **`>>>`**, the logical (unsigned) right shift. It **always** fills the left with `0`, regardless of sign.

```
−4 >>  1  =  1110  = −2      (sign bit 1 fills in — arithmetic)
−4 >>> 1  =  0110  = +6      (0 fills in — logical)
```

So why would anyone want the `0`-fill that breaks division? **Because sometimes a number is a bag of 32 bits, not a signed value** — when you iterate over bits, hash, or pack flags, you want the top to drain to `0`, sign-agnostic.

The decisive case is **walking every bit of a number down to `0`**. Watch `>>` fail at it. Take `−4 = …11111100`:

```
−4 >> 1 = …11111110
   >> 1 = …11111111   (= −1)
   >> 1 = …11111111   (= −1, stuck forever)
```

The sign-bit fill keeps regenerating `1`s from the top, so a negative number under `>>` collapses to `−1` (all ones) and **never reaches `0`** — a loop `while (n != 0) n >>= 1;` spins forever. Now `>>>`:

```
−4 >>> 1 = 0111…1110    (0 fills from the top)
...                      (the leading 1s get eaten, one per shift)
after ≤ 32 shifts → 0    ← terminates ✓
```

The `0`-fill drains the high bits, so the loop is finite for any input, positive or negative.

> **`>>` (sign-fill) is for arithmetic** — ÷2 that keeps the sign.
> **`>>> ` (zero-fill) is for bit-walking** — treat the value as a raw 32-bit pattern; the top drains to `0` so the process is finite and sign-agnostic.

### This is the fix to the P1 negative-`n` cliffhanger

P1 (Number of 1 Bits) counted set bits with `n % 2` (read lowest bit) and `n / 2` (advance). That arithmetic keeps the sign, so a negative `n` never terminated / miscounted — exactly the `>>` failure above. The operator version fixes it:

```java
while (n != 0) {
    count += n & 1;   // read the lowest bit
    n >>>= 1;         // advance, zero-filling — terminates for negative n too
}
```

`n & 1` reads the lowest bit as a raw bit; `n >>>= 1` walks down the 32-bit pattern and is guaranteed to reach `0`.

### Bonus real-world use

Binary-search midpoint `mid = (lo + hi) >>> 1`: if `lo + hi` overflows into a negative `int`, the unsigned shift still yields the correct midpoint, where `(lo + hi) / 2` would give a negative index. Same idea — treat the sum as raw bits, not a signed value.
