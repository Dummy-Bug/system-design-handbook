## a. Iterate digits of n

Two directions, two natural tools.

**Right-to-left via arithmetic** is the reflex for grabbing digits one at a time without allocating anything:

```java
while (n > 0) {
    System.out.println(n % 10);
    n /= 10;
}
```

For `n = 4729`, this prints `9, 2, 7, 4` — rightmost first. The two operations work in lockstep: `n % 10` peels off the last digit, `n /= 10` shifts the rest down by one position. Termination is `n > 0` — important to remember, otherwise you either get an infinite loop (forgot to update `n`) or skip `n = 0` entirely.

**Left-to-right via string conversion** is the reflex when you actually want the digits in reading order:

```java
String s = Integer.toString(n);
for (int i = 0; i < s.length(); i++) {
    int d = s.charAt(i) - '0';
    System.out.println(d);
}
```

For `n = 4729`, this prints `4, 7, 2, 9`. The string already reads left-to-right — no reversing needed. Reversing the string would flip you back to right-to-left, which defeats the point.

The critical Java trap here is `s.charAt(i) - '0'`. **Never write `(int) s.charAt(i)`** — that returns the ASCII code (48 for `'0'`, 57 for `'9'`), not the digit value. This is the same recurring bug from the pre-submit checklist that bit at 1650-1700 and again at 1800-1850. Reflex: char-to-digit conversion is always `c - '0'`.

The two choices map naturally to direction:

- Need right-to-left? Use arithmetic (`% 10` / `/= 10`) — no allocation.
- Need left-to-right? Use string conversion — the string is already in reading order.

---

## b. Digit count of n

Three ways to count digits, one of them quietly broken.

**`Long.toString(n).length()` — the safe default.** Convert to string, take length. Exact, handles `n = 0` correctly (returns 1), and there's no floating-point involvement. This should be the reflex for digit count unless you specifically need to avoid allocation.

**`(int)(Math.log10(n) + 1)` — looks elegant, has a trap.** The formula is right mathematically: a number with `L` digits satisfies `10^(L-1) ≤ n < 10^L`, so `floor(log10(n)) + 1 = L`. But Java's `Math.log10(1000)` doesn't return exactly `3.0` — it returns `2.9999999999999996`. Cast to int truncates downward, giving `(int)(2.999... + 1) = (int)(3.999...) = 3`. The formula says 1000 has 3 digits. Off by one, silent.

The root cause: `Math.log10(x)` is computed internally as `ln(x) / ln(10)`. `ln(10)` is an irrational number, so when stored in a `double` it gets rounded to the nearest representable binary value — slightly off. That rounding error propagates through the division, and the result lands just below the true integer value. The `+1` trick from the pre-submit checklist (used for `Math.pow` and `Math.sqrt`) **does not save you here** — the error goes downward, so even after adding 1 the int cast still truncates to the wrong value.

This is the same family as `0.1 + 0.2 = 0.30000000000000004`. There, `0.1` and `0.2` themselves can't be stored exactly in binary because they're repeating binary fractions (`0.1` in binary is `0.000110011001100...` forever, just like `1/3` in decimal). The two stored approximations don't add to exactly `0.3` either, so the visible result has a tiny error. Different cause from `log10` — there it was an irrational constant, here it's repeating fractions — but same outcome: floating-point can never be trusted for exact integer reasoning.

**Reflex rule: never use `Math.log10` for digit count. Default to `Long.toString(n).length()`.**

**Manual loop — exact but has an `n = 0` trap.**

```java
int count = 0;
while (n > 0) { count++; n /= 10; }
```

For `n = 0`, the loop never enters and returns `count = 0`. But `0` has one digit, not zero. Two fixes: special-case it (`if (n == 0) return 1;`) or use a `do-while`:

```java
int count = 0;
do { count++; n /= 10; } while (n > 0);
```

The manual loop is useful when you're already iterating digits for some other purpose (sum, reverse, walk) — you get the count as a free side effect. If digit count is the only thing you need, use `Long.toString().length()`.

---

## c. Sum of digits of n

Same skeleton as iterating digits, with `+=` instead of `print`:

```java
int sum = 0;
while (n > 0) {
    sum += n % 10;
    n /= 10;
}
```

For `n = 4729`: peels off `9, 2, 7, 4`, accumulates to `22`.

No `n = 0` trap here — `digit_sum(0) = 0` mathematically, and the loop returns `0`. Coincidence works in your favor.

The general pattern: any "compute a digit-derived quantity of n" problem uses this `while (n > 0) { ... n /= 10; }` skeleton with different per-digit operations inside (sum, max, count of specific digit, etc.). Treat it as a single mental template — same loop, swap the inner line.

---

## d. Reverse digits of n

Build the reversed number by placing each grabbed digit into the rightmost position of the accumulator:

```java
long rev = 0;
while (n > 0) {
    rev = rev * 10 + n % 10;
    n /= 10;
}
```

Walk for `n = 4729`:

| iter | `n % 10` | `rev` before | `rev` after | `n` after |
|------|----------|--------------|-------------|-----------|
| 1 | 9 | 0 | 9 | 472 |
| 2 | 2 | 9 | 92 | 47 |
| 3 | 7 | 92 | 927 | 4 |
| 4 | 4 | 927 | 9274 | 0 |

The key line is `rev = rev * 10 + n % 10`. The `* 10` shifts the existing accumulator left by one digit position, opening a slot at the rightmost position. `+ n % 10` fills that slot with the newly grabbed digit. Each iteration adds one digit to the right end of `rev` — and because digits are grabbed right-to-left from `n` but placed at the right end of `rev`, the final result is reversed.

**Overflow trap.** For LC 7 (*Reverse Integer*), inputs span the full 32-bit int range (`±2.1 × 10^9`). A valid input like `1_534_236_469` reverses to `9_646_324_351`, which overflows int. The bug doesn't show up only at the end — it appears mid-loop, silently:

```java
int rev = 0;            // wrong type
while (n > 0) {
    rev = rev * 10 + n % 10;   // int * int overflows BEFORE assignment
    n /= 10;
}
```

Even if you declared the assignment target as `long`, the multiplication still happens in `int` first — same trap as the pre-submit checklist's `long j = i * i` (overflows int before assignment). The fix: declare `rev` as `long` from the start, so every operation along the way is long arithmetic:

```java
long rev = 0;
while (n > 0) {
    rev = rev * 10 + n % 10;
    n /= 10;
}
if (rev > Integer.MAX_VALUE || rev < Integer.MIN_VALUE) return 0;
return (int) rev;
```

The `long` accumulator buys you headroom to detect the overflow after the fact. Without it, the overflow has already silently happened and there's no way to recover.

**Reflex rule:** any time you build a number digit-by-digit and the input could approach int range, declare the accumulator as `long`. Same rule as pre-submit checklist #1.

---

## e. Digit palindrome check

Reverse the number and compare:

```java
long original = n;     // save before mutating
long rev = 0;
while (n > 0) {
    rev = rev * 10 + n % 10;
    n /= 10;
}
return rev == original;
```

The non-obvious bit: the reversal loop **destroys `n`** (reduces it to zero). If you don't save the original value before the loop, you'll end up comparing `rev == 0`, which is almost never what you want.

**Edge case for LC 9 (*Palindrome Number*):** negative numbers are never palindromes — `-121` reversed is `121-`, which isn't a number. Handle as `if (n < 0) return false;` upfront.

The string version (`s.equals(new StringBuilder(s).reverse().toString())`) also works and avoids the overflow concern entirely. Pick by context — for a one-off LC problem, string is fine. For a tight inner loop, arithmetic.

---

## f. Place value — extracting the i-th digit

**Right-indexed (0-indexed from the right):**

```java
int digit_i = (n / pow10(i)) % 10;
```

Two-step intuition:

1. Dividing by `10^i` drops the `i` rightmost digits, shifting the desired digit into the ones position.
2. `% 10` peels off the ones position.

Walk for `n = 4729`:

| i | `n / 10^i` | `% 10` | digit |
|---|------------|--------|-------|
| 0 | 4729 / 1 = 4729 | 9 | 9 |
| 1 | 4729 / 10 = 472 | 2 | 2 |
| 2 | 4729 / 100 = 47 | 7 | 7 |
| 3 | 4729 / 1000 = 4 | 4 | 4 |

Reflex line: *"divide-then-mod = i-th digit from right."*

**Left-indexed (0-indexed from the left)** requires knowing the digit count first, then converting the index:

```java
int L = Long.toString(n).length();
int digit_i_from_left = (n / pow10(L - 1 - i)) % 10;
```

The conversion is `i-th from left = (L - 1 - i)-th from right`. For `n = 4729` (`L = 4`), the leftmost digit (`i = 0`) is the `3rd` from the right, which is `4`. Consistent with f.1.

Two-step reflex: *"count digits, then divide-then-mod with the flipped index."*

**Practical note:** if a problem lets you choose the indexing direction, right-indexing is cheaper — it doesn't need a digit count step. Left-indexing is only mandatory when the problem describes positions in reading order.

---

## g. Modifying / replacing a specific digit

The slick way: don't deconstruct the whole number — only adjust the contribution of the digit you're changing.

**The intuition.** A number in decimal is just a sum of place-value contributions:

```
4729 = 4×1000 + 7×100 + 2×10 + 9×1
     = 4×10³  + 7×10² + 2×10¹ + 9×10⁰
```

Each digit at position `i` (from the right) contributes exactly `digit × 10^i` to the total. The `7` at position 2 in `4729` contributes `7 × 100 = 700` to the value.

To replace that `7` with a `3`: the contribution should change from `700` to `300`. The number changes by exactly `300 - 700 = -400`. **No other digit's contribution moves.**

```java
int oldDigit = (n / pow10(i)) % 10;                       // f.1
int newN = n + (newDigit - oldDigit) * pow10(i);
```

For `n = 4729`, `i = 2`, `newDigit = 3`:

- `oldDigit = (4729 / 100) % 10 = 47 % 10 = 7`
- `newN = 4729 + (3 - 7) × 100 = 4729 - 400 = 4329`  ✓

**The reflex insight:** every digit at position `i` is just `d × 10^i` in disguise. To change one digit, adjust the number by the **delta** of its place-value contribution. Never tear the whole number apart and rebuild — that's `O(L)` work for an `O(1)` change.

---

## h. Building n from a digit array

Given `int[] digits = {4, 7, 2, 9}` (left-to-right reading order), reconstruct `n = 4729`:

```java
int n = 0;
for (int d : digits) {
    n = n * 10 + d;
}
```

Walk:

| iter | `d` | `n` before | `n` after |
|------|-----|------------|-----------|
| 1 | 4 | 0 | 4 |
| 2 | 7 | 4 | 47 |
| 3 | 2 | 47 | 472 |
| 4 | 9 | 472 | 4729 |

**Same line of code as d.1** — `acc = acc * 10 + new_digit` — but the input direction is different:

- **d.1 (reverse digits):** input grabbed right-to-left from n → output ends up reversed.
- **h.1 (build from array):** input iterated left-to-right from array → output preserves original order.

The line `acc * 10 + new_digit` always places the new digit at the **rightmost position** of `acc`. Whether the final result reads "reversed" or "original" depends entirely on the order in which digits are fed in.

**Overflow:** if the array represents a number near int range (10+ digits), declare `long n = 0L;` — same overflow trap as d.2. The `* 10` happens before any potential cast, so the accumulator type must be long from the start.

---

## i. Powers of 10 reflex

When you see a constraint like `n ≤ 10^9` in an LC problem, you need to instantly know:

- The decimal value (`1,000,000,000`)
- Whether it fits in `int` or `long`
- Whether a product or sum involving it will overflow

**The table to lock cold:**

| Power | Value | Name |
|-------|-------|------|
| `10^3` | 1,000 | thousand |
| `10^6` | 1,000,000 | million |
| `10^9` | 1,000,000,000 | billion — **LC default constraint** |
| `10^12` | 1,000,000,000,000 | trillion |
| `10^15` | 10¹⁵ | quadrillion / PB |
| `10^18` | 10¹⁸ | quintillion / EB |

**Overflow boundaries:**

| Type | Range | Largest power of 10 that fits |
|------|-------|-------------------------------|
| `int` (32-bit) | `±2.1 × 10^9` | **10^9** (10^10 overflows) |
| `long` (64-bit) | `±9.2 × 10^18` | **10^18** (10^19 overflows) |

**The danger-zone reflexes** (matching pre-submit checklist #1):

- `nums[i] × nums[j]` with both around `10^9` → product up to `10^18` → fits long, overflows int. Use `(long) a * b`.
- Sum of `n = 10^5` elements each up to `10^9` → total up to `10^14` → fits long, overflows int. Use long accumulator.
- `a × b × c` with each around `10^6` → product up to `10^18` → still needs long.
- Anything reaching `10^19` → even long overflows → need `BigInteger` or modular arithmetic.

The mapping `10^k → k zeros` needs to be reflex — no finger-counting in a contest.

---

## j. Digit-sum identities — mod 9 reflex

**The theorem:** for any positive integer `n`:

```
n ≡ digit_sum(n) (mod 9)
```

**Why it works.** Every power of 10 leaves remainder 1 when divided by 9:

```
10  = 9 + 1       → 10  ≡ 1 (mod 9)
100 = 99 + 1      → 100 ≡ 1 (mod 9)
10^k ≡ 1 (mod 9)  for all k ≥ 0
```

So when you expand `n` by place value and take mod 9, every power of 10 collapses to 1:

```
133 = 1×100 + 3×10 + 3×1
    ≡ 1×1   + 3×1  + 3×1   (mod 9)
    = 1 + 3 + 3 = 7         (mod 9)
```

The place values disappear under mod 9 — the value of `n` collapses to just the **sum of its digits**, mod 9. Verify directly: `133 = 14×9 + 7`, so `133 mod 9 = 7`. And `digit_sum(133) = 7`. Match.

**What this unlocks:**

1. **Divisibility by 9.** `n % 9 == 0` ⟺ `digit_sum(n) % 9 == 0`. The grade-school "sum the digits, check if divisible by 9" trick is exactly this theorem.
2. **Divisibility by 3.** Same reasoning — `10 ≡ 1 (mod 3)` as well, so `digit_sum(n) % 3 == 0` ⟺ `n % 3 == 0`.
3. **Fast `n % 9` for huge `n`.** Even if `n` has 100 digits and overflows every numeric type, you can compute `n % 9` by summing its digits in O(digit count). Useful when `n` is given as a string.
4. **LC 258 *Add Digits*** — direct application.

**The reflex line to lock:** *"mod 9 collapses to digit sum, because powers of 10 are all ≡ 1 mod 9."* Generalises to mod 3 by the same reasoning.

**Note on j.2 (digital root closed form).** There's a one-line formula for digital root: `1 + (n - 1) % 9`. It's a clever shortcut for exactly one problem (LC 258), and not worth memorising as reflex. The underlying theorem (j.1) is the high-leverage piece — once you have that, you can re-derive the formula in 30 seconds if needed, or just write the simple iterative version. The shortcut is parked.

---

## k. Numbers with restricted-digit set

How many L-digit numbers can you form using only digits from a given set `S`?

**The reframe that unlocks it: digits can repeat by default.** In digit-counting problems, the same digit is allowed to appear in multiple positions unless the problem explicitly forbids it. So `333`, `555`, `777` are all valid 3-digit numbers built from `{2, 5, 7}`. This is **not** a combinations problem (`nCr` picks distinct elements) and **not** a permutations problem (`nPr` arranges distinct elements). It's **sequences with repetition allowed** — each position is an independent choice from the set.

The multiplication principle handles this directly: if each of `L` positions has `k` independent choices, the total count is `k × k × ... × k = k^L`.

**Warmup: count 3-digit numbers using only `{2, 5, 7}`.**

Each position: 3 choices. 3 positions, all independent. Total = `3^3 = 27`.

(If you wrote `C(3, 3) = 1` or `P(3, 3) = 6`, you fell into the "no repetition" trap. The right answer comes from repetition being allowed.)

**The leading-zero twist.** Count 3-digit numbers using only `{0, 2, 5}`.

If you blindly applied `|S|^L = 3^3 = 27`, you'd be counting strings like `025` and `007` as valid 3-digit numbers. But `025` is just `25` — a 2-digit number with a leading zero, not a 3-digit number.

The fix is **only the first position loses the `0` choice** — the remaining positions are unaffected. First position: 2 choices (`{2, 5}`). Other 2 positions: 3 choices each. Total = `2 × 3 × 3 = 18`.

Enumerate to verify: `200, 202, 205, 220, 222, 225, 250, 252, 255, 500, 502, 505, 520, 522, 525, 550, 552, 555` — eighteen 3-digit numbers.

**The two cases:**

- `0 ∉ S` → all `L` positions free → count = `|S|^L`
- `0 ∈ S` → first position rejects `0` → count = `(|S| - 1) × |S|^(L-1)`

**The reflex insight:** don't memorise the formula. Memorise the *reasoning* — "each position is an independent choice from the set; first position rejects 0 if 0 is in the set; multiply choices across positions." The formula re-derives itself in five seconds from that reasoning. That's the muscle, not the symbols.

**LC anchor:** *Numbers At Most N Given Digit Set* (LC 902). This exact formula becomes **Part A** of the digit walk — counting all numbers with strictly fewer digits than `N`. The harder Part B (the tight-prefix walk over `N`'s own digits) lives in card m.

---

## l. Sum of digit_sum across a range

Compute `digit_sum(1) + digit_sum(2) + ... + digit_sum(n)`.

The naive way is O(n): loop `i` from 1 to `n`, compute `digit_sum(i)` for each, accumulate. Fine for `n = 100`. Breaks at `n = 10^9` (a billion iterations, way past the LC time budget).

**The closed-form trick: decompose by digit position, not by number.**

Instead of summing across rows (one row per number), sum across **columns** (one column per digit position). The trick reduces O(n) work to O(L) work where L is the digit count.

**Worked example for `[0, 99]`.**

Write every number in `[0, 99]` as a 2-digit number with a leading zero where needed:

```
00, 01, 02, ..., 09     ← tens column = 0, ones column cycles 0-9
10, 11, 12, ..., 19     ← tens column = 1, ones column cycles 0-9
20, 21, 22, ..., 29     ← tens column = 2
...
90, 91, 92, ..., 99     ← tens column = 9
```

The sum of all digit_sums equals the sum of the tens column plus the sum of the ones column.

**Tens column:** the digit "holds steady" at value `d` for an entire block of 10 numbers, then jumps to `d+1`. Each digit `0-9` appears exactly 10 times. Column sum = `(0+1+...+9) × 10 = 45 × 10 = 450`.

**Ones column:** the digit "cycles" `0, 1, ..., 9, 0, 1, ..., 9, ...` — different pattern, same end result. Each digit `0-9` appears exactly 10 times. Column sum = `45 × 10 = 450`.

**Total for `[0, 99]`** = `450 + 450 = 900`.

**Scaling to `[0, 999]`.** Three columns now (hundreds, tens, ones). The same argument applies, with one new question: **how many times does each digit appear in each column?**

The clean way to see it — multiplication principle (the k.1 muscle, applied again):

> *"How many numbers in `[0, 999]` have a `5` in the ones column?"*
>
> You're counting numbers that look like `??5`. The hundreds digit can be any of `0-9` (10 choices), the tens digit can be any of `0-9` (10 choices), the ones digit is fixed at 5. By multiplication: `10 × 10 = 100` numbers.

So digit `5` appears `100` times in the ones column. The same argument works for digits `0` through `9`, and for the tens and hundreds columns. **Each digit `0-9` appears `100` times in every column.**

Per-column sum: `(0+1+...+9) × 100 = 45 × 100 = 4500`. Three columns: total = `3 × 4500 = 13,500`.

**Generalising to `[0, 10^L - 1]`.**

For any L-column range, fix one column at any digit. The other `L-1` columns are independent choices of 10 digits each. By multiplication, the count is:

```
10 × 10 × ... × 10   (L-1 times)   =   10^(L-1)
```

So each digit `0-9` appears `10^(L-1)` times in each column. Per-column sum = `45 × 10^(L-1)`. There are `L` columns. **Total = `L × 45 × 10^(L-1)`.**

Verify:
- L=1 (`[0, 9]`): `1 × 45 × 1 = 45` ✓ (= 0+1+...+9)
- L=2 (`[0, 99]`): `2 × 45 × 10 = 900` ✓
- L=3 (`[0, 999]`): `3 × 45 × 100 = 13,500` ✓
- L=4 (`[0, 9999]`): `4 × 45 × 1000 = 180,000`

**The whole insight in one sentence:** *"Split by columns, each digit appears equally often in each column, multiply through."* The formula `L × 45 × 10^(L-1)` is the consequence — don't memorise it, re-derive it from the reasoning.

**The catch — only the clean case is closed-form.** This entire derivation assumes `n = 10^L - 1` (a clean boundary like 9, 99, 999, 9999). For an arbitrary `n` like `4729`, the columns no longer have each digit appearing equally often — there's a **"tight prefix"** problem where most digits can't cycle through the full `0-9` because the value can't exceed `n`. That's exactly the **digit walk** machinery (card m), which splits the count into:

- **Part A:** numbers with strictly fewer digits than `n` (closed-form, as above)
- **Part B:** numbers with exactly `n`'s digit count — walk `n`'s digits left-to-right and handle the tight prefix carefully

So l.1 is the clean half of m. Master the column-decomposition reflex here, then m extends it to handle the messy tight prefix.
