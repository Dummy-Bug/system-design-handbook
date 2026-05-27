# Why Float Kills You in Competitive Programming

## The 32-bit split

`float` is 32 bits (4 bytes), same size as `int`. But those 32 bits are split into three parts:

- **1 bit** → sign (positive or negative)
- **8 bits** → exponent (how big/small — the "×10^6" part)
- **23 bits** → mantissa (the actual digits of the number)

Only 23 bits store the real digits. 2^23 = 8,388,608 — roughly **7 significant digits**. That's all a `float` can remember.

---

## What "7 digits of precision" means

Take `9013971.0` — that's 7 digits. Float stores it perfectly.

Now halve it: `4506985.5`. That's 8 digits of meaningful information. Float can only hold 7. So it silently rounds — stores `4506986.0` instead of `4506985.5`. The `.5` is lost forever.

Halve again. The real answer should be `2253492.75`. But float is working from its already-wrong `4506986.0`, and again only keeps 7 digits. More rounding. More error.

Each halving makes the number longer. Each time, float throws away the tail. After 20-30 halves, the accumulated rounding makes your total off by enough to return the wrong answer.

---

## When float breaks

If constraints say `nums[i] <= 10^7`, that's already 8 digits (`10000000`). Float's 7-digit limit can't even store the input accurately — let alone the decimals that follow from halving, dividing, or averaging.

**Float is safe up to ~10^6** (7 digits), and even then adding decimals makes it tight.

---

## Double: the fix

`double` = 64 bits (8 bytes):

- **1 bit** → sign
- **11 bits** → exponent
- **52 bits** → mantissa

52-bit mantissa → 2^52 ≈ 4.5 × 10^15 → roughly **15 significant digits**. That's enough for values up to 10^7 with plenty of decimal room.

---

## The rule

> [!danger] Never use `float` in competitive programming. Always `double`. Zero exceptions.

`float` exists for memory-constrained scenarios (GPU compute, massive arrays of millions of floats). In CP, correctness beats memory every time.

---

## The problem that taught this

**Minimum Operations to Halve Array Sum** (1550-1600 band, Phase 1). Used `Float` in a max-heap — passed 60/62 cases, WA'd on large inputs (~9 million). Switched to `Double` → instant AC. The input values were already 7 digits, so float couldn't even store them cleanly before any halving started.
