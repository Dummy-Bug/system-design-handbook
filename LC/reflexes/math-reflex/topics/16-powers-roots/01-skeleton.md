# Powers & Roots [1100]

Integer powers (`n²`, `n³`, `n^k`), roots (`√n`, `∛n`), and the precision traps that come with them. The "is `n` a perfect square?" / "is `n` a power of 5?" family — small in formula count but huge in bug-density because of Java's float-cast pitfalls.

This is the topic that owns the **`(int) Math.sqrt(n)` precision bug** — already documented in CLAUDE.md item #2 of the Java pre-submit checklist. The cards here lock the workaround as reflex.

## Empirical frequency

| Band | POWER_ROOT-tagged | % of math |
|------|-------------------|-----------|
| 1100-1399 | 13 | 4.5% |
| 1400-1499 | tail | ~2% |
| 1500-1599 | 3 | 3.8% |
| 1600-1699 | tail | ~2% |
| 1700-1799 | 1 | 1.4% |
| 1800-1899 | 2 | 2.6% |
| 1900+ | tail | — |

**Total: ~25 problems** where power/root reasoning is the binding step. Most are 1100-1500 where the precision trap bites hardest.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Integer square / cube [1100]

**Cards (2):**
- a.1 — Square: `n * n`. Cube: `n * n * n`. Overflow boundary: `n² > Integer.MAX_VALUE` when n ≥ ~46340 (~4.6 × 10⁴) — cast to long
- a.2 — Compute `n²` not `Math.pow(n, 2)` — `Math.pow` returns double, introduces precision loss

---

## b. Perfect-square check [1100]

**Cards (2):**
- b.1 — Compute `s = (int) Math.sqrt(n)`, then verify `s * s == n`. **Never trust `Math.sqrt` alone** — float precision drops s by 1 for some n
- b.2 — Robust form: `s = (int) Math.sqrt(n); while ((long)(s+1) * (s+1) <= n) s++;` — handles the off-by-one

**LC anchor:** *Valid Perfect Square* (LC 367)

---

## c. Integer square root [1100]

**Cards (2):**
- c.1 — Definition: `isqrt(n) = floor(√n)` — the largest integer s with `s² ≤ n`
- c.2 — Robust compute: `(int) Math.sqrt(n)` then adjust ±1; or binary search on `s² ≤ n`

**LC anchor:** *Sqrt(x)* (LC 69)

---

## d. Integer cube root [1300]

**Cards (1):**
- d.1 — `(int) Math.cbrt(n)` has the same precision trap as sqrt — verify `s * s * s == n` after casting, adjust ±1

**LC anchor:** *Largest 3-Same-Digit Number in String* (LC 2264 variant — cube counting), problems counting cubes in [L, R]

---

## e. Math.pow precision trap [1200]

**Cards (4):**
- e.1 — `(int) Math.pow(1e9, 1.0/3) = 999` not 1000 — float-cast loses one. Always add `+ 1` and re-verify
- e.2 — Reflex: never trust `Math.pow` returning an exact integer. Either use integer arithmetic or verify post-cast
- e.3 — **`(int) Math.pow(10, i)` for place value — the silent-success trap.** It *works* (powers of 10 ≤ 10¹⁵ are exact doubles), which is worse than failing: the bug hides until the base isn't a clean power. Reflex fix → integer-only: precomputed `long[] POW10` or peel digits with `n % 10; n /= 10`. Never reach for `Math.pow` to extract a digit.
- e.4 — **Why the cast is sometimes safe (the root fact):** a `double` represents every integer exactly up to `2^53 ≈ 9.0 × 10¹⁵`; beyond that the gaps exceed 1, so `(long)` casts of large `Math.pow` / `Math.sqrt` results lose information. Powers of 10 are exact only up to `10¹⁵` for this reason. "Small value → looks fine; large value → corrupts" is the same boundary.

**Note:** e.1/e.2 are CLAUDE.md item #2 of the Java pre-submit checklist. e.3 born from *Sum of Digit Differences of All Pairs* (1600-1650, 2026-05-26) — `(int)Math.pow(10,i)` AC'd silently and only the review flagged it. e.4 is the math fact underneath the whole family. Lock all four.

---

## f. Powers of 10 reference [1400]

**Cards (1):**
- f.1 — `10⁹` fits int (max int ≈ 2.1×10⁹). `10¹⁰` needs long. `10¹⁸` fits long. `10¹⁹` overflows long.

**Note:** Same card as Digit Ops `i.2` — cross-referenced.

---

## g. Powers of 2 reference [1400]

**Cards (1):**
- g.1 — `2¹⁰ ≈ 10³`, so `2²⁰ ≈ 10⁶`, `2³⁰ ≈ 10⁹`. `1 << 30` safe int, `1L << 62` safe long.

**Note:** Same card as Bit Ops `d.1`, `d.2` — cross-referenced.

---

## h. Power-of-n detection [1300]

**Cards (3):**
- h.1 — Power of 2: `n > 0 && (n & (n - 1)) == 0` (cross-ref Bit Ops f.3)
- h.2 — Power of 3 / 4 / 5: divide repeatedly while divisible by base; check `n == 1` at end
- h.3 — Power of base k: `while (n % k == 0) n /= k;` then `n == 1`

**LC anchor:** *Power of Two* (LC 231), *Power of Three* (LC 326), *Power of Four* (LC 342)

---

## i. n-th root via binary search [1500]

**Cards (2):**
- i.1 — Binary search `s` in `[0, n]` to find largest s with `s^k ≤ n` — O(log n × k multiplications)
- i.2 — Overflow guard during search: `s^k` can overflow long before exceeding n — use saturating multiply or BigInteger pow

**LC anchor:** *Powx N* (LC 50), *Reach a Number* type problems

---

## j. Counting perfect squares / cubes in range [1500]

**Depends on:** Integer square root [1100]

**Cards (2):**
- j.1 — Count perfect squares in `[L, R]` = `isqrt(R) - isqrt(L - 1)`
- j.2 — Count perfect cubes in `[L, R]` = `icbrt(R) - icbrt(L - 1)`

**LC anchor:** *Integers With Multiple Sum of Two Cubes* (LC 3890)

---

## k. Sum-of-powers enumeration [1700]

**Cards (1):**
- k.1 — Enumerate pairs `(a, b)` with `a^k + b^k ≤ N` — outer loop a up to `N^(1/k)`, inner b up to root. Time O(N^(2/k)).

**LC anchor:** *Integers With Multiple Sum of Two Cubes* (LC 3890), *Sum of x-th Powers* (LC 2787)

---

## Card count

21 atomic cards across 11 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (2) + b (2) + c (2) = **6 cards** |
| 1200-1299     | + e (4) = **10 cards** |
| 1300-1399     | + d (1) + h (3) = **14 cards** |
| 1400-1499     | + f (1) + g (1) = **16 cards** |
| 1500-1599     | + i (2) + j (2) = **20 cards** |
| 1600-1699     | — = 20 cards |
| 1700-1799     | + k (1) = **21 cards (full)** |

## Notes for Socratic drill

- Subtopic `b.2`, `e.1`, and `e.3` are the cornerstone bug-prevention cards in this topic. All close documented CLAUDE.md Java traps. Highest install priority. `e.4` is the *why* (the `2^53` exact-integer boundary) — install it alongside e.3 so the fix is understood, not memorized.
- Subtopic `a.1` (n² overflow at n ≈ 46340) ties to the same overflow family as AP triangular sum (a.2) and digit-positional values. Lock the boundary as a sibling reflex.
- Subtopics `f` and `g` (powers of 10 and 2 reference tables) are cross-referenced from Digit Ops and Bit Ops respectively. Install once, used from three topics.
- Subtopic `h` (power-of-n detection) — the binary AND trick for power of 2 is one of the most-asked LC reflex questions in interview screens. Lock cold.
- Subtopic `k` (sum-of-powers enumeration) is the 1700+ technique that turns "count of n that can be written as sum of two cubes" from infeasible to O(N^(2/3)). Niche but each appearance is a Q3 gate.
