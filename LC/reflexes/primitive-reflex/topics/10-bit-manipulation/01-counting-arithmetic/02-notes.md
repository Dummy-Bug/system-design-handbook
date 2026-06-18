## 1. popcount — count set bits, answer-proportional

**Problem:** how many bits are `1` in `x`? `13 = 1101` → `3`.

### The naive tool (and why to beat it)
Test every position with the Sec. 0.4 idiom:
```java
int count = 0;
for (int i = 0; i < 32; i++)
    if ((x >> i & 1) == 1) count++;
```
Always **32 iterations** — work proportional to the *width*, not the answer. For a lone high bit
(`0b1000…0000`, one set bit) it still grinds all 32 positions.

### The bit way: loop `x &= x-1`
`x & (x-1)` **clears the lowest set bit** (Idioms Sec. 1). Repeat it until nothing is left:
```java
int count = 0;
while (x != 0) {
    x &= x - 1;     // clear lowest set bit
    count++;
}
return count;
```

Trace `13`:
```
1101   start
1100   after x&=x-1   (cleared bit 0)
1000   after x&=x-1   (cleared bit 2)
0000   after x&=x-1   (cleared bit 3)  → loop ends
```
Hit `0` in **3** steps; `13` had **3** set bits.

> **Why exactly (#set-bits) iterations:** each pass clears *exactly one* set bit and touches nothing else, so
> the loop runs once per set bit and stops the instant the last one is gone. `k` set bits → `k` steps → **O(k)**,
> vs O(32) for the naive scan. Sparse number (1 bit) = 1 step.

### Trigger (the reflex)
*"Count set bits, and I want work proportional to the answer / the builtin is banned"* →
`while(x!=0){ x&=x-1; count++; }`. Sits in the **per-bit counting** corner of the bit confusion matrix.

### Negatives — the Foundations cliffhanger, resolved
The Sec. 0.x **arithmetic stopgap** `n % 2` / `n /= 2` **breaks on negatives** (sign rules on `/` and `%`, not
shifting) — that was the open cliffhanger. The `x &= x-1` loop has no such issue: it works on the raw
two's-complement pattern and `x != 0` just asks "any bits left," so `-1` → 32 steps, `13` → 3 steps. No `>>>`
patch needed.

- arithmetic `%2`//`2` loop → **breaks** on negatives (old stopgap)
- `x &= x-1` loop → **works** on negatives ✓
- `Integer.bitCount(n)` → **works** on negatives ✓ (`bitCount(-1) == 32`) — the builtin optimized version


## 2. Counting Bits — popcount of every number `0..n` (LC 338)

**Problem:** return `ans[i]` = popcount of `i` for **every** `i` in `0..n`. Constraint `n` up to `10^5`.

### The simple tool, and why to beat it
Call atom-1 popcount on each number:
```java
for (int i = 0; i <= n; i++) ans[i] = popcount(i);   // O(n · bits) ≈ O(32n)
```
Correct, and fine at this constraint. But the intended solution is **O(n)** — *one* operation per number — by
reusing answers already computed (every `i' < i` is filled in).

### The insight (the whole problem)
Compare `i` with `i >> 1` = `i / 2` (drop the lowest bit):
- **even `i`** — appending a `0` adds no set bit → `popcount(i) == popcount(i/2)`
- **odd `i`**  — same bits as `i/2` **plus** the trailing `1` → `popcount(i) == popcount(i/2) + 1`

Both cases collapse to: add back the bit you dropped, which is `i & 1`.

> **`ans[i] = ans[i >> 1] + (i & 1)`** — the bit you shifted out (`i&1`) is exactly the count you lose.
> Valid as DP because `i >> 1 < i`, so `ans[i>>1]` is already filled. Once the shift insight lands, the rest is
> just formulating it as a DP state.

```java
public int[] countBits(int n) {
    int[] dp = new int[n + 1];          // dp[0] = 0
    for (int i = 1; i <= n; i++)
        dp[i] = dp[i >> 1] + (i & 1);   // halve + trailing bit
    return dp;
}
```

### Alt recurrence (same array, different "smaller number") — trivia, not the default
Instead of halving, clear the lowest set bit with `i & (i-1)` (Idioms part 1):
```java
dp[i] = dp[i & (i-1)] + 1;              // always +1: clearing lowest set bit removes exactly one 1
```
On `i = 11 = 1011`: `i&(i-1) = 1010 = 10` (one fewer set bit) → `dp[11] = dp[10] + 1 = 3`. ✓
`i & (i-1)` is strictly smaller (already computed) and has exactly one fewer set bit, so always `+1`.

> Two paths to the same DP — **keep `dp[i>>1] + (i&1)` as the default** (standard form); the `i&(i-1)+1`
> version just shows the recurrence isn't unique.

### Trigger (the reflex)
*"I need popcount for a whole range `0..n`, not one number"* → DP `dp[i] = dp[i>>1] + (i&1)`. Per-bit-counting
corner of the matrix; the leap is "reuse a smaller number's answer," not re-counting each from scratch.

## 3. Count total set bits in `1..N` (GfG — sum of popcounts over a range)

**Problem:** total number of `1` bits in *all* integers from `1` to `N`. `N = 5` → `1+1+2+1+2 = 7`.
Link: GfG "Count total set bits in all numbers from 1 to n" (LC has no standalone version; LC 338 is the *array*
variant, not the running total). Counting `0..N` vs `1..N` is identical — `0` has no set bits.

### The simple tool, and why it dies
Kernighan/`bitCount` every number and sum:
```java
long total = 0;
for (int i = 1; i <= N; i++) total += Integer.bitCount(i);   // ~O(N log N)
```
Fine for small `N`, but `N` up to `10^9` (or `10^18`) → tens of billions of ops → **TLE**. The per-*number*
loop is dead. A number up to `10^9` has only ~30 bits, so we want work proportional to **bit positions (~30)**,
not **integers (10^9)**.

### The reframe: count down columns, not across rows
Stack the numbers in binary. The naive method sums **across each row** (per number) — `N` rows. Instead sum
**down each column** (per bit position) — only ~30 columns, regardless of `N`.

```
        bit2 bit1 bit0
0..7:     0    0    0     bit0 column: 0 1 0 1 0 1 0 1   → block "0 1"      (period 2,  one 1)
          0    0    1     bit1 column: 0 0 1 1 0 0 1 1   → block "0 0 1 1"  (period 4,  two 1s)
          0    1    0     bit2 column: 0 0 0 0 1 1 1 1   → block "0000 1111"(period 8,  four 1s)
          ...
```

### Per-bit periodicity (the whole insight)
Column `b` is a repeating block of **`2^b` zeros then `2^b` ones**:
- `period = 2^(b+1)` (full block length)
- `half   = 2^b`     (number of 1s per block = its back half)

Count of 1s in column `b` over `count = N+1` numbers (`0..N`), in two pieces:
1. **full blocks:** `(count / period)` complete blocks, each giving `half` ones.
2. **leftover:** `rem = count % period` trailing numbers — a fresh block is `half` zeros *then* `half` ones, so
   ones = `max(0, rem - half)` (still in zeros if `rem ≤ half`; else the excess ticked into ones).

> **`onesAtBit(b) = (count / period) * half + max(0, count % period - half)`**, then **sum over all bits `b`**.

### Worked example — bit 1, numbers `0..10` (count = 11)
```
0 0 1 1 | 0 0 1 1 | 0 0 1
└block1┘  └block2┘  └leftover: 8,9,10┘
```
period 4, half 2. Full blocks `11/4 = 2` → `2*2 = 4`. Leftover `11%4 = 3` → block starts `0 0 1`, excess
`max(0, 3-2) = 1`. Total `4 + 1 = 5`. Hand-check: 1s at `2,3,6,7,10` = **5** ✓.

```java
long countSetBits(int N) {
    long totalSetBits = 0;
    for (int bit = 0; (1L << bit) <= N; bit++) {
        long blockSize    = 1L << (bit + 1);   // "0..0 1..1" block: 2^(bit+1) long
        long onesPerBlock = 1L << bit;          // back half of each block is 1s
        long rangeSize    = (long) N + 1;       // counting 0..N  →  N+1 numbers
        long fullBlocks   = rangeSize / blockSize;
        long leftover     = rangeSize % blockSize;
        totalSetBits += fullBlocks * onesPerBlock
                      + Math.max(0, leftover - onesPerBlock);
    }
    return totalSetBits;
}
```
`O(log N)`. (`long` + `1L<<bit` to avoid overflow when `N` is large.) Names say what they *are*:
`blockSize`/`onesPerBlock` (not period/half), `rangeSize` = `N+1` numbers (not an ambiguous `count`),
`fullBlocks`/`leftover` split out so the two-piece structure reads top-to-bottom.

### Trigger (the reflex)
*"Count something over a huge range `1..N` — can't iterate the range"* → **don't loop the numbers; find the
per-bit (or per-digit) periodicity and count column-by-column in O(log N).** This column-flip generalizes far
beyond bits — it's the seed of **digit-DP counting** (count numbers with property P in `[1,N]`). The felt-signal
is "N is up to 1e9/1e18 and I'm being asked to total a per-element quantity."

The builtin is what you'd ship; the hand-rolled loop is what the "implement it / no builtin" signal asks for.

## 4. Reverse bits (LC 190) — already installed in Foundations

Done in `00-foundations/02-Operators/problems/04-reverse-bits.md`. Two-pointer read/write: **read** bit at
`p` = `(x>>p)&1`, **write** bit `b` at `q` = `|=(b<<q)`; `i` up from 0, `j` down from 31, swap mirror slots.
Banked there: build place values with `1<<k` **not** `Math.pow` (overflow→clamp), and **AC ≠ correct** (a
constraint-masked bug passed). Not re-derived here.

## 5. Add two integers without `+` / `-` (LC 371) — XOR + carry

**Problem:** return `a + b` using only `& | ^ ~ << >>` — `+` and `-` are banned. `a,b ∈ [-1000,1000]`
(negatives in play; two's-complement handles them for free on raw bits). Link: https://leetcode.com/problems/sum-of-two-integers/

### Rebuild addition from one column
Adding two bits, no incoming carry:
```
0+0=0(c0)   0+1=1(c0)   1+0=1(c0)   1+1=0(c1)
```
- **sum bit** column `0,1,1,0` = `a ^ b`  — XOR is *addition that forgets the carry*.
- **carry**  column `0,0,0,1` = `a & b`  — AND marks *where a carry is born*.
- A carry born at column `i` must be applied at column `i+1` → shift it up: **`(a & b) << 1`**.

### Why operate on the whole number, not bit-by-bit
Bitwise `^` and `&` act on **all 32 columns in parallel** in one instruction — `a^b` is every column's sum-bit
at once. So we don't loop over positions. We loop because **carries cascade**: folding the shifted carry back in
can *create new* carries. Repeat until no carry remains.

> **`sum = a ^ b` (no-carry add) · `carry = (a & b) << 1` (carries moved up) · loop until `carry == 0`.**

```java
public int getSum(int a, int b) {
    while (b != 0) {            // b carries the carry
        int carry = (a & b) << 1;
        a = a ^ b;             // running sum (no carry)
        b = carry;            // fold carry in next round
    }
    return a;
}
```

### Trace `6 + 7` (= 13)
```
a=0110 b=0111 : sum=a^b=0001  carry=(0110&0111)<<1=0110<<1=1100
a=0001 b=1100 : sum=a^b=1101  carry=(0001&1100)<<1=0000<<1=0000 → STOP
→ 1101 = 13 ✓     (2 rounds — carry rippled 2 columns, not 4)
```

### Downstream value (why this matters beyond LC 371)
The literal problem is interview trivia, but the two ideas have legs:

1. **XOR = sum with no carry → the sum/XOR identity** (this is the payoff; reused in Module 3):
   > **`a + b = (a ^ b) + 2·(a & b)`**, and the corollary **`a + b == a ^ b  ⟺  a & b == 0`** (no shared bits).
   So problems saying *"sum equals XOR"* / *"chosen numbers' bits don't collide"* are really the disguised
   condition **"share no set bits"** (a subset/bitmask reframe). [[lc-derivation-budget-chunking]]
2. **"Operator banned → rebuild from `^ & <<`"** is the meta-reflex — directly reused by **1.6 divide without `/`**
   (rebuild ÷ from shift+subtract) and *multiply without `*`* (shift-and-add).

### Trigger (the reflex)
*"Add/subtract but `+`/`-` are banned"* → `^` for the no-carry sum, `(a&b)<<1` for the carry, loop till carry 0.
Bit-arithmetic corner of the matrix; this is the scope-boundary exception (genuinely-bit carry-arithmetic).

The builtin is what you'd ship; the hand-rolled loop is what the "implement it / no builtin" signal asks for.

## 6. Divide without `*` / `/` / `%` (LC 29) — batch-doubling subtraction

**Problem:** `dividend / divisor`, truncated toward zero, using only `+ - << >>` and comparisons. 32-bit signed,
range `[-2^31, 2^31-1]`. Link: https://leetcode.com/problems/divide-two-integers/

### The engine: subtract in doubling batches (binary long division)
Division = "how many `divisor`s fit in `dividend`." Naive = subtract `divisor` one at a time → up to ~2.1e9
subtractions for `(2^31-1)/1` → **TLE**. Special-casing small divisors doesn't generalize (2, 3, … all slow).

Fix: subtract **big batches**, each twice the previous. "How many 4s in 78":
```
1 four=4 · 2 fours=8 · 4 fours=16 · 8 fours=32 · 16 fours=64 · 32 fours=128(too big)
```
Each step: remove the **biggest batch ≤ what's left**, add that batch's *count* to the quotient.
```
78 − 64(=16 fours) → 14, quotient 16
14 −  8(= 2 fours) →  6, quotient 18
 6 −  4(= 1 four ) →  2, quotient 19
 2 < 4 → stop                          78/4 = 19 ✓  (3 subtractions, not 19)
```

> **The doubling IS a left shift.** "16 fours = 64" is `divisor<<4 = 64`; the `16` added is `1<<4`. Same `k`.
> **Subtract the VALUE (`divisor<<k` = 64), add the COUNT (`1<<k` = 16)** — the one easy-to-swap insight.
> Biggest batch first ⇒ ~31 outer steps (one per bit) ⇒ **O(log dividend)**.

### Overflow — two spots, both from the lopsided range `[-2^31, 2^31-1]`
`-2^31` has no positive twin (`+2^31` isn't an int). That asymmetry breaks two things:
1. **Result overflows:** the *only* pair whose quotient doesn't fit is `-2^31 / -1 = +2^31` → guard up front,
   return `Integer.MAX_VALUE`.
2. **Making positive overflows:** `Math.abs(-2^31)` returns `-2^31` again (can't fit `+2^31` in int) → the engine
   breaks. **Fix: cast to `long`** — `2^31` (and `2^32`) fit, so `abs` and every `<<` stay correct; cast back at
   the end.

### Code
```java
public int divide(int dividend, int divisor) {
    if (dividend == Integer.MIN_VALUE && divisor == -1) return Integer.MAX_VALUE;

    long a = Math.abs((long) dividend);
    long b = Math.abs((long) divisor);
    boolean negative = (dividend < 0) ^ (divisor < 0);

    long quotient = 0;
    while (a >= b) {
        long batch = b, count = 1;
        while (a >= (batch << 1)) {   // peek the NEXT double before committing → never overshoot
            batch <<= 1;
            count <<= 1;
        }
        a -= batch;                   // subtract the VALUE
        quotient += count;            // add the COUNT
    }
    return negative ? (int) -quotient : (int) quotient;
}
```
- **sign via XOR:** `(dividend<0) ^ (divisor<0)` = "exactly one negative" → result negative.
- inner loop builds the doubling list lazily; on exit `batch` = biggest batch ≤ `a`.
- check `batch << 1` (not `batch`) so you stop *before* overshooting.

### Recurring-bug guard (hit on first write)
- **Subtracted the count, not the value:** `dividend -= (1<<k)` instead of `dividend -= (divisor<<k)`. Add `1<<k`,
  subtract `divisor<<k`. They're different numbers (16 vs 64).
- **Precedence:** `dividend - divisor<<k` parses as `(dividend-divisor)<<k` — `-` binds tighter than `<<`.
  Parenthesize: `dividend - (divisor<<k)`. [[lc-java-shift-precedence-trap]]
- **`while(true)`** needs the stop condition `while (a >= b)`.
- strict `<` vs `<=` in the fit-check skips the exact-divisor case (`8/4`).

### Trigger (the reflex)
*"Divide/multiply but the operator is banned (or dividend is huge)"* → batch-doubling: shift the divisor up to
the biggest multiple that fits, subtract value / add `1<<k`, repeat. Same meta-move as 1.5 ("operator banned →
rebuild from shifts"); *multiply without `*`* is the mirror (shift-and-add). Bit-arithmetic corner.
