# P — Power of Two (LC 231)

**Task:** return whether `n` is a power of two (`1, 2, 4, 8, …`). Constraint allows `n` to be `0` or negative, so edge handling matters.

## Accepted solution (highest==lowest set bit)

```java
class Solution {
    public boolean isPowerOfTwo(int n) {
        return n > 0 && Integer.highestOneBit(n) == Integer.lowestOneBit(n);
    }
}
```

## The insight: a power of two has exactly ONE set bit

`1=1`, `2=10`, `4=100`, `8=1000` — each is a single `1`. So the highest set bit and the lowest set bit are the **same** bit → `highestOneBit(n) == lowestOneBit(n)`.

## But "one set bit" is necessary, NOT sufficient — the edge cases

The bare `highestOneBit == lowestOneBit` test wrongly returns `true` for:
- **`n = 0`**: `highestOneBit(0) = lowestOneBit(0) = 0` → `0 == 0` → true. But `0` is not a power of two.
- **`n = Integer.MIN_VALUE = 0x80000000`**: this is the **sign bit** — exactly one set bit — so `highest == lowest == MIN_VALUE` → true. But `−2^31` is negative, not a power of two. (It *does* fit in `int`; it **is** MIN_VALUE. The flaw isn't "doesn't fit" — it's that a single *sign* bit still counts as one set bit.)

Other negatives are fine without a guard: any negative except MIN_VALUE has the sign bit **plus** other bits, so `highest != lowest` → false.

## The fix: guard the property, not the values

First fix enumerated the exceptions: `if (n == 0 || n == Integer.MIN_VALUE) return false;`. That works, but both are just instances of one property: **a power of two must be positive.** So:

```java
return n > 0 && (highest == lowest);
```

`n > 0` rejects `0`, MIN_VALUE, and every other negative in one stroke.

> **Lesson: when you catch yourself listing special-case values (`0`, `MIN_VALUE`, …), find the *property* they violate and guard that.** Property-guards are shorter and don't miss a value you forgot to enumerate.

## Reinforces the Reverse-Bits lesson
"It works lol" on the examples ≠ correct. The naive version passed the obvious cases and failed `0` / MIN_VALUE — the same **AC ≠ correct** trap. Checking `n = 0` and `n = MIN_VALUE` by hand caught it.

> The classic `n & (n - 1) == 0` solution is **deferred to the Idioms topic (atom 0.10)**, where `n & (n-1)` is derived cold. Solving it that way now would be pattern-matching a told answer, not a self-derived rep — so this problem keeps only the highest/lowest-bit solution, and Power of Two is revisited as the `n & (n-1)` install in `04-Idioms`.

*Status: AC. Self-derived (highest==lowest-bit, with positivity guard). Headline insights: power of two ⇔ exactly one set bit; one-set-bit is necessary but not sufficient (`0` and MIN_VALUE slip through → must also be positive); property-guard (`n > 0`) over value-enumeration; reinforces AC ≠ correct.*
