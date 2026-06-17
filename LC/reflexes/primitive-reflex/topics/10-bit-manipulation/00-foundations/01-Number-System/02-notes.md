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

**Reading binary → decimal** is just the place-value sum. Example: `1011` = `1×8 + 0×4 + 1×2 + 1×1` = `8 + 2 + 1` = **11**. The `0` at the 4's place means "skip 4" — each bit is a yes/no switch for its place value.

## 6. A key fact: a run of 1s is one less than the next power

This small fact is load-bearing for everything below, so we pin it down now:

> The value with the bottom `k` bits **all set to 1** equals **`2^k − 1`**.

**Why (carry proof):** add 1 to a run of all-ones and the carry ripples all the way up, landing exactly on the next power:
```
  0111   (4+2+1 = 7, the bottom 3 bits)
+    1
------
  1000   (= 8 = 2³)
```
So `all-ones-below-k + 1 = 2^k`, which means **`all-ones-below-k = 2^k − 1`**.

Examples: `0111 = 2³−1 = 7` · `1111 = 2⁴−1 = 15` · `11111111 = 2⁸−1 = 255`.

**A second proof: the doubling trick (GP sum).** The carry proof above is the bit-view; here's the algebra-view, and they're the same truth. The value of `k` ones is the geometric sum
```
S = 2^0 + 2^1 + 2^2 + ... + 2^(k-1)      (k terms)
```
Multiply the whole thing by 2 — every term shifts up one power (a ×2 *is* a left shift):
```
 S =  2^0 + 2^1 + ... + 2^(k-1)
2S =        2^1 + ... + 2^(k-1) + 2^k
```
Subtract. Every middle term (`2^1` … `2^(k-1)`) appears in **both** rows and cancels, leaving only the new top term and the lost bottom term:
```
2S − S = 2^k − 2^0
   S   = 2^k − 1
```
This is exactly the carry proof in algebra: `2S` is `S` shifted left one bit, and the subtraction lands you one short of `2^k`. It also matches the general GP formula `S = a·(rⁿ−1)/(r−1)` with `a=1, r=2, n=k` → `(2^k − 1)/1 = 2^k − 1`.

This fact does double duty: it's **why decimal→binary greedy is forced** (§7) and it **bounds the largest value storable in `n` bits** (§8).

## 7. Decimal → binary (the reverse direction)

Reading binary sums the place values. Converting *to* binary runs that backwards: given a decimal number, find which place values sum to it. The **greedy method**:

> Repeatedly take the **largest place value ≤ the remaining number**, set that bit to `1`, and subtract it. Place values that don't fit get `0`. Stop when the remainder hits 0.

Convert **11** (place values `8, 4, 2, 1`):

| Step | Remaining | Largest fitting power | Bit set | New remaining |
|---|---|---|---|---|
| 1 | 11 | 8 (≤11)   | 8's bit = 1 | 11 − 8 = 3 |
| 2 | 3  | 4 too big | 4's bit = 0 | 3 |
| 3 | 3  | 2 (≤3)    | 2's bit = 1 | 3 − 2 = 1 |
| 4 | 1  | 1 (≤1)    | 1's bit = 1 | 0 ✓ |

Bits in order `8 4 2 1` → **`1011`** = 11. ✓

**Why greedy is forced (not just lucky):** by §6, each place value `2^k` is **larger than the sum of all smaller place values combined** (which is `2^k − 1`). So if `2^k` fits into `N`, you **must** take it — skipping it leaves you a max of `2^k − 1 < 2^k ≤ N`, unreachable. This is also why a binary representation is **unique**: every bit is forced, no choices. And after subtracting `2^k` the remainder is always `< 2^k`, so each place value is decided exactly once.

### The other method: repeated division by 2

There's a second, more mechanical way — the one you'd actually code. It comes from a parallel with decimal.

In decimal, how do you peel digits off `437`? `437 % 10 = 7` gives the **last digit**, and `437 / 10 = 43` **drops** it. The key realization:

> **`N % b` gives the last digit of `N` *written in base `b`*; `N / b` drops that digit.**

Dividing by the **base** is what exposes digits in that base. So for *binary* digits, use base 2:
- `N % 2` → the **last bit** (lowest, the 1's place)
- `N / 2` → `N` with that bit dropped (the rest shifted down)

*(Why `% 2` is the last bit: write `N = … + b₁·2 + b₀·1`. Every term but `b₀` has a factor of 2, so the remainder mod 2 is exactly `b₀`.)*

Repeat until `N` hits 0. Convert **11**:

| N | N % 2 (bit) | N / 2 |
|---|---|---|
| 11 | **1** | 5 |
| 5  | **1** | 2 |
| 2  | **0** | 1 |
| 1  | **1** | 0 ← stop |

Remainders come out **lowest bit first**: `1, 1, 0, 1`. But we write binary **highest bit first**, so **reverse** them → **`1011`** = 11. ✓ (Same answer as greedy.)

> **Note on the input:** here `11` means the decimal quantity *eleven*. `% / ` are ordinary decimal arithmetic on that quantity; the output `1011` is its binary spelling. Caution: `% 10` and `% 2` ask different questions about the same number — e.g. for *twelve*, `12 % 10 = 2` (last decimal digit) but `12 % 2 = 0` (last bit, since `12 = 1100`). They match only by coincidence.

**Greedy vs division-by-2:** same result. Greedy reads bits **high→low** (no reversing); division-by-2 reads them **low→high** (reverse at the end) and is the cleaner thing to code.

## 8. Fixed width and value ranges

A number isn't stored in "as many bits as it needs" — it's stored in a **fixed row** of bits. In Java: `byte` = 8 bits, `int` = **32 bits**, `long` = 64 bits. This fixed width is what creates a **range** of representable values.

Count the patterns: with `n` independent bits, each bit is 0 or 1, so there are `2 × 2 × … × 2` (`n` times) = **`2^n`** distinct patterns. They represent the values `0, 1, …, 2^n − 1`. So (treating all bits as value bits, no negatives yet):

> `n` bits → **`2^n` distinct patterns** → range **`0 … 2^n − 1`**.
> The largest value is all `n` bits set = `2^n − 1` (the §6 fact).

The `−1` is just because we start counting at 0.

- 8 bits → `2^8 = 256` patterns → range `0 … 255` (and `11111111 = 2^8 − 1 = 255`).
- 32 bits → `2^32` patterns → range `0 … 2^32 − 1`.

## 9. Storing negative numbers

A Java `int` can be negative — but §8 just used up **all** `2^32` patterns on the non-negative values `0 … 2^32−1`. There are no patterns left over. So something has to give.

The trade-off: **split the patterns into two halves — roughly half for non-negatives, half for negatives.** That immediately halves the largest positive we can store. (This is why a 32-bit `int` runs `−2^31 … +2^31 − 1`, not `0 … 2^32−1`.)

The interesting question is *how* to assign the negative patterns. Let's look at the obvious idea first, watch it fail, and let that failure design the real scheme.

### The obvious idea that fails: sign-magnitude

Use the **leftmost bit as a sign flag** — `0` = positive, `1` = negative — and let the remaining bits hold the magnitude. In 4 bits:

- `0101` → front bit `0` (positive), magnitude `101` = 5 → **+5**
- `1101` → front bit `1` (negative), magnitude `101` = 5 → **−5**

Seems reasonable. It has two fatal problems.

**Problem 1 — two different zeros.**
- `0000` → +0
- `1000` → −0

The same value has two patterns. That wastes a pattern *and* poisons every comparison (is `+0 == −0`? you'd have to special-case it).

**Problem 2 — ordinary addition breaks.**
We'd love `(+5) + (−5)` to come out `0` using plain column-by-column binary addition. Try it:
```
  0101   (+5)
+ 1101   (−5)
------
 10010   → keep only 4 bits → 0010 = 2     ✗ not 0
```
It gives **2**, not 0. So sign-magnitude can't use a normal adder for signed numbers — the hardware would need a separate, sign-aware subtractor. Unacceptable.

### The fix: two's complement

Problem 2 tells us exactly what to wish for:

> **Design goal:** define `−x` as whatever pattern makes `x + (−x) = 0` using *plain* binary addition — same adder, no sign checks.

The trick that makes this possible: in `n` bits, **any carry out of the top bit falls off and disappears.** So the pattern `1` followed by `n` zeros — the value `2^n` — *becomes* `0000…0` once it overflows. That means we don't need `x + (−x)` to be literally 0 — we just need it to be `2^n`, which overflows away to 0.

So: find the 4-bit pattern `P` for `−5` such that `0101 + P = 10000` (which overflows to 0).

```
  0101   (5)
+ P
------
 10000        →  P = 10000 − 0101 = 1011
```

`P = 1011`. And as a plain value, `1011 = 11 = 16 − 5 = 2^4 − 5`. That's the definition:

> **`−x` is stored as the pattern for `2^n − x`.** This is **two's complement**.

It works by construction: `x + (2^n − x) = 2^n`, which overflows to `0`. ✓
Check: `−5 = 1011`, and `0101 + 1011 = 10000` → drop the carry → `0000`. ✓

### The shortcut: `−x = ~x + 1`

Computing `2^n − x` by subtraction every time is annoying. Watch — split the definition by subtracting and adding 1:
```
−x = 2^n − x = (2^n − 1) − x + 1
```
Now focus on the middle piece, `(2^n − 1) − x`. The value `2^n − 1` is **all ones** (in 4 bits, `1111` — the §6 fact). Subtracting `x` from all-ones, column by column, is always `1−0=1` or `1−1=0` — **it never borrows** — so every bit of `x` simply **flips**:
```
  1111
− 0101   (x = 5)
------
  1010   ← that's 0101 with every bit flipped
```
"Flip every bit" *is* the bitwise NOT operator, `~`. So `(2^n − 1) − x = ~x`, and therefore:

> **`−x = ~x + 1`** — "flip all the bits, then add 1."

Check: `5 = 0101` → flip → `1010` → `+1` → `1011 = −5`. ✓

This is the single most useful fact about two's complement. It's also *why* the idiom `x & -x` isolates the lowest set bit (we'll use that in atom 0.9).

### Reading the sign

Look at the leftmost bit across two's-complement values:
- `0101`=+5, `0011`=+3, `0111`=+7 → all start with **0**
- `1011`=−5, `1101`=−3, `1111`=−1 → all start with **1**

So the **leftmost bit tells you the sign** — `0` = non-negative, `1` = negative. We never *declared* it a sign bit (unlike sign-magnitude); it just falls out of the `2^n − x` scheme.

### Decoding a pattern — two ways that always agree

**Way 1 — the leftmost bit has a *negative* place value.** This is the deepest way to see two's complement, and it shows the top bit is *not* ignored — it's the heaviest bit, just pulling **downward**. In `n` bits, every bit has its normal place value except the leftmost, which is **`−2^(n−1)`**:

```
position:     3      2      1      0
place value: −8     +4     +2     +1      ← only the top bit is negative
```

Then you just read it like any positional number:

| Pattern | Read with place values | Value |
|---|---|---|
| `0100` | `0·(−8) + 1·4 + 0·2 + 0·1` | **+4** |
| `1100` | `1·(−8) + 1·4 + 0·2 + 0·1` = −8+4 | **−4** |
| `1110` | `1·(−8) + 1·4 + 1·2 + 0·1` = −8+4+2 | **−2** |

Notice: a positive number (`0100`) just reads straight, because its top bit is `0` and contributes nothing. A negative number's top `1` contributes the big `−8`, and the lower bits pull it back up toward zero.

**Way 2 — flip and add 1 to get the magnitude.** For a negative pattern (leading `1`), take its two's complement (`~x + 1`); the result is the magnitude, then attach `−`.

- `1110`: `~ → 0001`, `+1 → 0010` = 2 → value **−2**
- `1100`: `~ → 0011`, `+1 → 0100` = 4 → value **−4**

Both ways give the same answer because they're the same fact. **Way 1 is usually faster for decoding** (read it straight); **flip-and-add-1 is what you use for encoding** (going from `−2` to its bits). Same dictionary, two directions.

> Vocabulary: **1's complement** = flip all bits (`~x`). **2's complement** = `~x + 1`. The magnitude of a negative pattern is its 2's complement.

### The lopsided range

Here is every 4-bit two's-complement pattern (`2^4 = 16` of them):

| Pattern | Value | | Pattern | Value |
|---------|-------|---|---------|-------|
| `0000`  | 0     | | `1000`  | **−8** |
| `0001`  | +1    | | `1001`  | −7    |
| `0010`  | +2    | | `1010`  | −6    |
| `0011`  | +3    | | `1011`  | −5    |
| `0100`  | +4    | | `1100`  | −4    |
| `0101`  | +5    | | `1101`  | −3    |
| `0110`  | +6    | | `1110`  | −2    |
| `0111`  | **+7**| | `1111`  | −1    |

**16 patterns, 16 distinct values, no duplicates** (the win over sign-magnitude — no two zeros). The split is **8 non-negatives** (`0 … +7`) and **8 negatives** (`−1 … −8`) — `2^(n−1)` on each side.

But notice the **asymmetry**: positives run `+1 … +7` (7 values), negatives run `−1 … −8` (8 values). One **extra negative**, `−8`, has no positive twin: there's a `+7` but no `+8`, because `+8` would need pattern `1000` — already taken by `−8`.

> `n`-bit two's complement range = **`−2^(n−1) … +2^(n−1) − 1`** (one more negative than positive).
> For n=4: `−2³ … +2³−1` = `−8 … +7`. For a real `int`: `Integer.MIN_VALUE = −2^31`, `Integer.MAX_VALUE = +2^31 − 1`.

**Why `−8` "loops to itself":** negate it via flip+1 → `1000 → 0111 → +1 → 1000`. You get `1000` back — `−(−8)` gives `−8`, not `+8`, because `+8` doesn't exist in 4 bits; the negation overflowed.

**The real-world bug this causes:** `−Integer.MIN_VALUE` and `Math.abs(Integer.MIN_VALUE)` both return the *negative* `MIN_VALUE` (negating `−2^31` needs `+2^31`, which doesn't exist). A genuine source of bugs.

### What "overflow" actually means here (it's silent, not a crash)

The word *overflow* is misleading — it sounds like an error. In Java, **integer overflow is not an exception and not a crash; it is silent two's-complement wraparound.** The arithmetic just proceeds, the top carry falls off, and you're left with a wrapped (wrong) value — no signal, no log, program continues. So "`abs(MIN_VALUE)` overflows" and "`abs(MIN_VALUE)` returns the negative number" are the *same statement*: the overflow **is** what produces the negative result, not an alternative to it.

Trace it through the actual `Math.abs`:
```java
public static int abs(int a) {
    return (a < 0) ? -a : a;
}
```
For `a = Integer.MIN_VALUE = −2^31`:
- `a < 0` is true → it returns `-a`.
- `-a` is computed as `~a + 1` (two's-complement negation — flip then add 1).
- `MIN_VALUE` = `1000…0` (32 bits). Flip → `0111…1` (= `MAX_VALUE` = `2^31 − 1`). Add 1 → `1000…0` = `MIN_VALUE` again.

So `-a == a == MIN_VALUE`, still negative. The *mathematical* answer `+2^31` is one past the ceiling `2^31 − 1` → it has nowhere to live in 32 bits → it wraps to `−2^31`. **That wrap is the overflow.**

The real danger is the *silence*: `abs()` looks like it must return something non-negative, and this single input quietly breaks that promise with no warning. (Same effect for the unary `-Integer.MIN_VALUE`.)
