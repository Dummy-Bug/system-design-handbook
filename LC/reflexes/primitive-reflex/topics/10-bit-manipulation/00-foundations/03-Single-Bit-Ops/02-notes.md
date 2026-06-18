## 1. The single-bit mask: `1 << i`

Every single-bit operation is built from one small tool — a mask that picks out exactly one position. That mask is `1 << i`: take a lone `1` and slide it left to position `i`.

```
1 << 0 = 0001   (1 at bit 0)
1 << 1 = 0010   (1 at bit 1)
1 << 2 = 0100   (1 at bit 2)
1 << 3 = 1000   (1 at bit 3)
```

So `1 << i` is a number with a **single `1` at position `i`** and `0` everywhere else (its value is `2^i`).

It is worth being careful with the word "set" here: `1 << i` does not *set* anything by itself — it is just **a selector pointing at position `i`**, the *address* of the bit we care about. The actual verbs (test it, turn it on, turn it off, flip it) come from combining this mask with an operator.

### Width caveat on `1 << i`

For a 32-bit `int`:
- **`i` = 0…30** — ordinary positive power of two, fully safe.
- **`i` = 31** — `1 << 31 = 0x80000000 = Integer.MIN_VALUE`, negative *as a value*. But for **masking** (`& | ^`, which work on the raw bit pattern) it is still correct — the pattern *is* "bit 31 set." It only causes trouble if you use the mask **arithmetically** or compare it expecting a positive number.
- **`i` ≥ 32** — genuinely wrong: the shift amount wraps **mod 32**, so `1 << 32 = 1 << 0 = 1` (a different bit). Silent failure.

> For masking, `1 << i` is fine through `i = 31`; it only wraps at `i ≥ 32`. Use **`1L << i`** (a 64-bit `long` mask) when addressing bit 31+ arithmetically, or any bit of a value wider than 32 bits.

## 2. Testing a bit: is bit `i` set?

To ask "is bit `i` of `x` a `1`?", combine `x` with the mask `1 << i` using **`&`**. AND keeps a bit only where *both* sides have a `1`; since the mask is `1` at just position `i` and `0` elsewhere, the result can only be nonzero **at** position `i`, and only if `x` also has a `1` there.

Test bit 2 of `x = 0110`:

```
x        = 0110
1 << 2   = 0100
x & mask = 0100   → nonzero → bit 2 is SET
```

Test bit 0 of the same `x = 0110`:

```
x        = 0110
1 << 0   = 0001
x & mask = 0000   → zero → bit 0 is CLEAR
```

### The `!= 0`, not `== 1` trap

Notice the value in the *set* case: `x & (1 << 2)` came back as `0100` = **4**, not `1`. In general `x & (1 << i)` returns either `0` (bit clear) or **`2^i`** (bit set) — the place value, never a clean `1`.

So the correct test compares against `0`:

```java
if ((x & (1 << i)) != 0) { ... }   // bit i is set
```

Writing `== 1` instead is a classic bug: it is only true when `i = 0` (where `2^0 = 1`) and silently fails for every other position.

> **Test bit `i` (boolean form):** `(x & (1 << i)) != 0`. The result is `2^i` when set, so compare to `0`, not `1`.

### The value form: `(x >> i) & 1`

When you want the bit as a clean `0`/`1` number (to add into a sum, or build another number with it), use the other arrangement: shift `x` **right** by `i` so bit `i` lands at position 0, then `& 1` to read just that lowest bit.

Reading bit 2 of `x = 0110`:

```
x >> 2       = 0001          (bit 2 slid down to position 0)
(x >> 2) & 1 = 0001 & 0001 = 1
```

The two forms are the same question approached from opposite directions:

| Form | Expression | Returns | Use when |
|---|---|---|---|
| **boolean** | `(x & (1 << i)) != 0` | true / false | you just need yes/no |
| **value** | `(x >> i) & 1` | clean `0` or `1` | you need the bit *as a number* |

The boolean form brings the **mask up** to where the bit is; the value form brings the **bit down** to where the mask (`1`) is. The value form is exactly the read used in counting set bits and in Reverse Bits.

## 3. Setting a bit: force bit `i` to `1`

To turn bit `i` on (regardless of its current value) while leaving every other bit untouched, combine `x` with the mask `1 << i` using **`|`**.

Set bit 0 of `x = 0100`:

```
x        = 0100
1 << 0   = 0001
x | mask = 0101          (bit 0 on; bits 1–3 unchanged)
```

Why the other bits survive: at every position except `i` the mask bit is `0`, and OR with `0` **keeps** the other bit (Operators Sec. 2). Only at position `i` is the mask `1`, which forces that bit on.

It is **idempotent** — `1 | 1 = 1`, so setting an already-set bit leaves it set. Safe to apply repeatedly.

> **Set bit `i`:** `x | (1 << i)`.

## 4. Clearing a bit: force bit `i` to `0`

Recall `&` **clears where the mask is `0` and keeps where the mask is `1`.** So to clear *only* bit `i` and keep everything else, the mask must be **`0` at position `i` and `1` everywhere else** — the exact opposite of `1 << i`.

Build that by flipping every bit of `1 << i` with the bitwise NOT (`~`, Sec. 4 — not arithmetic `-`):

```
1 << 2      = 0100        (single 1 at position 2)
~(1 << 2)   = 1011        (flip all → 0 at position 2, 1s elsewhere)
```

AND it with `x`. Clearing bit 2 of `x = 0110`:

```
x             = 0110
~(1 << 2)     = 1011
x & ~(1 << 2) = 0010        (bit 2 cleared; bits 0,1,3 kept)
```

Also idempotent — if bit `i` was already `0`, AND-ing with a `0` there keeps it `0`, and the `1`s elsewhere keep the rest.

> **Clear bit `i`:** `x & ~(1 << i)`.

### Works for negatives too (all four verbs do)

These operations act on the raw 32-bit pattern via `& | ^ ~`, which are **sign-agnostic** — a negative number is just a bit pattern. Clearing bit 1 of `x = −2`:

```
−2            = …11111110     (two's complement)
~(1 << 1)     = …11111101
x & ~(1<<1)   = …11111100     = −4
```

`−2` is `…1110` → bit 1 cleared → `…1100 = −4`. The sign bit and all others ride along untouched.

> **test / set / clear / toggle all work on negatives unchanged** — pure bit-pattern ops. The only sign-sensitive operator is `>>` (arithmetic, sign-filling), which is why bit-*walking* loops use `>>>`. Addressing a single bit never cares about sign.

## 5. Toggling a bit: flip bit `i`

To flip bit `i` (`0→1` or `1→0`) and leave the rest, combine `x` with `1 << i` using **`^`**. At position `i` the mask is `1`, and XOR with `1` **flips** (Sec. 3); everywhere else the mask is `0`, and XOR with `0` **keeps**.

Toggle bit 2 of `x = 0110`, twice:

```
x                = 0110
x ^ (1<<2)       = 0010      (bit 2 flipped 1→0)
again ^ (1<<2)   = 0110      (flipped back 0→1 — back to original)
```

> **Toggle bit `i`:** `x ^ (1 << i)`.

Unlike set and clear, toggle is **not idempotent — it is self-inverse**: applying it twice returns the original (`x ^ m ^ m = x`, Sec. 3). That captures the difference between "force to a value" (`|` set, `&~` clear) and "flip" (`^` toggle).

## Summary — the four verbs

Every single-bit operation = **`1 << i` picks the position, an operator does the verb:**

| Verb | Idiom | Operator role | Repeat behavior |
|---|---|---|---|
| **Test** (boolean) | `(x & (1 << i)) != 0` | `&` inspects (result is `2^i`, compare `!= 0`) | — |
| **Test** (value `0/1`) | `(x >> i) & 1` | bring bit down, mask `1` | — |
| **Set** → 1 | `x \| (1 << i)` | `\|` forces on | idempotent |
| **Clear** → 0 | `x & ~(1 << i)` | `&` with inverted mask | idempotent |
| **Toggle** (flip) | `x ^ (1 << i)` | `^` flips | self-inverse (twice = undo) |

Odd/even is just **test at `i = 0`**: `x & 1` (Operators Sec. 1).

All five compare/keep the other bits because the mask is `0` (or `1` for the clear-mask) everywhere except position `i` — and at non-`i` positions each operator's "keep" rule (`|0`, `&1`, `^0`) leaves them alone.
