## a. Triangular sum — 1 + 2 + ... + n

The single most frequently used formula in this topic. If you're deriving this from scratch in a contest, you're losing 5-10 minutes on a fact that should cost zero.

**Formula:** `n * (n + 1) / 2`

It comes from the general AP formula (`k * (2a + (k-1) * d) / 2`) with `a = 1`, `d = 1`, `k = n` — simplifies cleanly to `n(n+1)/2`.

**Overflow reflex:** the product `n * (n+1)` overflows a Java `int` around n ≈ 65,000 (~6.5 × 10^4). Anything above 10^4 scale, cast to long. Write `(long) n * (n + 1) / 2` — never `(long)(n * (n+1) / 2)`. The overflow happens before the cast in the second form.

**Inverse — recovering n from sum S:**

Given `S = n(n+1)/2`, rearrange to `n² + n - 2S = 0`, then apply the quadratic formula:

```
n = (-1 + √(1 + 8S)) / 2
```

Take the positive root only. This appears in problems that give you a triangular number and ask which n produced it.

---

## b. General AP sum

Any sequence with a constant difference `d` between consecutive terms is an arithmetic progression. Recognise it when you see: evenly spaced numbers, multiples of d, consecutive integers, or any "every k-th element" structure.

**Two equivalent forms:**

Using first term `a`, step `d`, over `k` terms:
```
k * (2a + (k-1) * d) / 2
```

Using first term `f` and last term `l` over `k` terms:
```
k * (f + l) / 2
```

The second form is the more intuitive one — average of first and last, multiplied by count. Both give identical results; use whichever form the problem hands you the values for.

---

## c. Sum of integers in [L, R]

This is just the AP formula with `a = L`, `d = 1`, last term `R`.

- **Count:** `R - L + 1`
- **Sum:** `(R - L + 1) * (L + R) / 2`

The count formula `R - L + 1` is the prereq that unlocks everything — both endpoints are included, so it's not `R - L`. Off-by-one here causes wrong answers across a huge class of problems.

---

## d. Sum of evens and odds

**First n even numbers** — 2 + 4 + 6 + ... + 2n:

`a = 2`, `d = 2`, `k = n` → simplifies to **`n * (n + 1)`**

**First n odd numbers** — 1 + 3 + 5 + ... + (2n-1):

`a = 1`, `d = 2`, `k = n` → simplifies to **`n²`**

The odd result is worth locking as a standalone fact: the first n odd numbers always sum to a perfect square. Geometrically, each new odd number adds an L-shaped border to a square — you're literally building n² dot by dot.

Verify: 1 = 1², 1+3 = 4 = 2², 1+3+5 = 9 = 3², 1+3+5+7 = 16 = 4².

---

## e. Sum of multiples of d in [L, R]

**LC anchor:** *Sum Multiples* (LC 2652, rated 1182) — sum all integers in [1, n] divisible by 3, 5, or 7. Most people solve it with an O(n) loop and get AC because n ≤ 1000. The O(1) formula approach is what builds the reflex for harder problems where O(n) TLEs.

**Pattern:**

```
First multiple of d ≥ L  →  ceil(L/d) * d
Last multiple of d ≤ R   →  floor(R/d) * d
Count                    →  floor(R/d) - ceil(L/d) + 1
Sum                      →  count × (first + last) / 2
```

Once you have first, last, and count — it's just the AP endpoint form.

The `ceil/floor` mechanics will be installed properly in the Number Theory topic. For now lock the pattern: find the boundary multiples, then apply AP sum.

---

## Parked cards

**f.1 — digit positional sum [1400]:** `Σ d_i × 10^i` — install when 1400 band opens.

**g, h — sum of squares / cubes [1500]:** install when 1500 band opens.

**i — sum of products / pairwise sums [1600]:** the bridge to contribution technique — install when 1600 band opens.

**j — geometric series [1700]:** install when 1700 band opens.

**k — telescoping sums [1800]:** install when 1800 band opens.
