## 1. How number systems actually work

Before we touch a single bit, we need to be honest about something we use every day without thinking: **how does a number even represent a value?**

Take the number **437**. We read it instantly as "four hundred thirty-seven" — but *why*? The secret is that **the same digit means different amounts depending on where it sits.** A `4` in the last position is worth 4; the same `4` two positions over is worth 400. Position carries weight.

## 2. Place value

The weight a position carries is called its **place value**: the amount that **one single unit** in that position is worth — *before* you multiply by whatever digit is sitting there. It belongs to the **position**, not to the digit.

Look at `437` broken apart:

| Position (from right, start at 0) | Place value | Digit | Digit × place value |
|---|---|---|---|
| 0 | **1**   | 7 | 7 × 1   = 7   |
| 1 | **10**  | 3 | 3 × 10  = 30  |
| 2 | **100** | 4 | 4 × 100 = 400 |

`400 + 30 + 7 = 437`.

The bolded column — `1, 10, 100` — are the place values. Position 2 is "the hundreds place" no matter what digit lands there: a `4`, a `9`, or a `0`. The digit just says *how many* of that place value you have — a `4` in the hundreds place means "four hundreds."

## 3. The one formula behind every number system

Place values aren't random — each one is a **power of the base**:

> Place value of position `i` = **`base^i`**.
> A digit `d` at position `i` contributes **`d × base^i`**.
> The whole number = the sum of every digit's contribution: **value = Σ dᵢ × baseⁱ**

For decimal the base is **10**, so the place values are `1, 10, 100, 1000, …` — the powers of 10.

## 4. Where does the base come from?

Here's the part most people never question: why base **10**?

Because decimal has exactly **ten distinct digits**: `0, 1, 2, 3, 4, 5, 6, 7, 8, 9`. Once you count past 9 you run out of symbols, so you carry into the next position. **The number of available digits *is* the base.**

This gives a rule we'll reuse constantly:

> In **any** base `b`, the allowed digits are `0` through `b − 1`, and each position's place value is a power of `b`.

Which opens the door to the next idea: **what if a number system had only two digits?**

## 5. Binary

Restrict the digits to just **`0` and `1`** — nothing else. By the rule above:
- only two digits → **base 2**
- allowed digits → `0` and `1`
- place values → powers of 2: `1, 2, 4, 8, 16, …` (`2^i`)

Same place-value machinery as decimal; the base is just 2 instead of 10. A binary digit can only be `0` ("zero of this place value") or `1` ("one of this place value"). Each such digit is called a **bit**.

**Example:** `1011` = `1×8 + 0×4 + 1×2 + 1×1` = `8 + 2 + 1` = **11**. The `0` at the 4's place means "skip 4" — each bit is just a yes/no switch for its place value.

## 6. Fixed width and value ranges

A number isn't stored in "as many bits as it needs" — it's stored in a **fixed row** of bits. In Java: `byte` = 8 bits, `int` = **32 bits**, `long` = 64 bits. This fixed width is what creates a **range** of representable values.

Count the patterns: with `n` independent bits, each bit is 0 or 1, so there are `2 × 2 × … = ` **`2^n`** distinct patterns. They represent the values `0, 1, …, 2^n − 1`. So (treating all bits as value bits, no negatives yet):

> `n` bits → **`2^n` distinct patterns** → range **`0 … 2^n − 1`**.
> All `n` bits set to 1 = the largest value = **`2^n − 1`**.

The `−1` is just because we start counting at 0.

- 8 bits → `2^8 = 256` patterns → range `0 … 255` (and `11111111` = `2^8 − 1` = 255).
- 32 bits → `2^32` patterns → range `0 … 2^32 − 1`.
