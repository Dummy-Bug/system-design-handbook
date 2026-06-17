# P — Number Complement (LC 476)

**Task:** flip every bit in the binary representation of `num` — but only within `num`'s **own bit-length** (no leading zeros). `num = 5 = 101` → `010 = 2`.

## Accepted solution

```java
class Solution {
    public int findComplement(int num) {
        int bitLength = 32 - Integer.numberOfLeadingZeros(num);
        int mask = (1 << bitLength) - 1;
        return num ^ mask;
    }
}
```

## The insight: flip-within-width = XOR with a width-matched all-ones mask

Flipping bits is `^ (all ones)` (§3: XOR with a `1` toggles). But here "all ones" must be **exactly as wide as `num`**, not all 32 bits — the problem ignores leading zeros.

- `bitLength = 32 - Integer.numberOfLeadingZeros(num)` = number of significant bits (MSB position + 1). For `5`: `32 − 29 = 3`.
- `mask = (1 << bitLength) - 1` = a run of `bitLength` ones (the §6 `2^k − 1` fact). For `5`: `(1<<3) - 1 = 7 = 111`.
- `num ^ mask` flips exactly those bits. `5 ^ 7 = 2`. ✓

## Two bugs hit on the way

**Bug 1 — fixed-width mask (`(1<<31)-1`).** First attempt flipped all 31 low bits, so `num`'s leading zeros became ones: `5 ^ 0x7FFFFFFF = 2147483642`, not `2`. **The mask must match `num`'s width**, not a hardcoded constant. (Complement is width-bounded — that's the whole subtlety of the problem.)

**Bug 2 — value-vs-position trap with `highestOneBit`.** Next attempt used `Integer.highestOneBit(num)` thinking it returned the bit *index*. It returns the bit **value** (a power of two): `highestOneBit(5) = 4` (the pattern `100`), not `2`. Then `1 << (4+1) = 32`, `mask = 31`, `5 ^ 31 = 26`. ✗

> **`1 << k` needs `k` to be a bit *position*.** `highestOneBit` gives a *value*. Don't feed a value where a position is expected.
> - bit **value** of MSB: `Integer.highestOneBit(num)` → `4` for `5`
> - bit **position** of MSB: `31 - Integer.numberOfLeadingZeros(num)` → `2` for `5`
> - bit **length** (what we want): `32 - Integer.numberOfLeadingZeros(num)` → `3` for `5`
>
> *(Alt one-liner using the value directly: `mask = (Integer.highestOneBit(num) << 1) - 1` — `(2^p << 1) - 1 = 2^(p+1) - 1`, all ones up to the MSB, no position needed.)*

## Naming lesson
The width variable was first called `msb` — wrong. It's not the MSB *position*; it's the **bit-length**. Name a variable for what it holds (`bitLength`/`width`/`numBits`), or the off-by-one between position and length will bite.

*Status: AC after 2 bugs (both conceptual, not plumbing): fixed-width-mask, then value-vs-position confusion. Headline insights: complement is width-bounded → XOR with a width-matched `(1<<bitLength)-1` mask; `highestOneBit` returns value not index; position vs length off-by-one.*
