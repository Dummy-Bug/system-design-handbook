## 1. How number systems actually work

Before we touch a single bit, we need to be honest about something we use every day without thinking: **how does a number even represent a value?**

Take the number **437**. We read it instantly as "four hundred thirty-seven" — but *why*? Look closer at what each digit is really doing:

| Digit | Position (from right, starting at 0) | What it's worth |
|-------|--------------------------------------|-----------------|
| 7     | 0                                    | 7 × 1   = **7**   |
| 3     | 1                                    | 3 × 10  = **30**  |
| 4     | 2                                    | 4 × 100 = **400** |

Add them up: `400 + 30 + 7 = 437`.

The crucial idea: **the same digit means different amounts depending on where it sits.** A `4` in the last position is worth 4; the same `4` two positions over is worth 400. Position carries weight.

This is called a **positional number system**, and there's one formula behind all of it:

> A digit `d` at position `i` (counting from the right, starting at 0) contributes **`d × base^i`**.
> The whole number is just the sum of every digit's contribution: **value = Σ dᵢ × baseⁱ**

For decimal, that base is **10**, so the positions are worth `1, 10, 100, 1000, …` — the powers of 10.

## 2. Where does the 10 come from?

Here's the part most people never question: why base **10**?

Because decimal has exactly **ten distinct digits**: `0, 1, 2, 3, 4, 5, 6, 7, 8, 9`. Once you count past 9, you run out of symbols, so you carry over into the next position. The number of available digits *is* the base.

This gives us a rule we'll reuse constantly:

> In **any** base `b`, the allowed digits are `0` through `b − 1`, and each position is worth a power of `b`.

Keep this in your head, because it's the doorway to the next idea: **what if a number system only had two digits?**
