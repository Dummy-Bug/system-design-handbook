# Arithmetic Sums (AP) [1100]

Closed-form formulas for summing arithmetic progressions, ranges, and standard sequences. Replaces O(n) summation with O(1) formula evaluation. Used inside thousands of problems as a sub-step — "what's the sum of 1 to n?", "how many multiples of d in [L, R] and what's their sum?", "total of a + (a+d) + ... over k terms?".

Caps in usefulness around Band 1800 — beyond that, summation depth shifts to telescoping over DP recurrences (still here at 1800) and generating functions (different topic).

## Empirical frequency

| Band | AP-tagged problems | Notes |
|------|--------------------|-------|
| 1100-1399 | 68 (under SUM_ARITH legacy tag, 23.8% of math problems in that band) | Highest density of any band — anchor zone |
| 1400-1499 | 4 (AP_SUM=2 + SUM_ARITH=2) | |
| 1500-1599 | 2 | |
| 1600-1699 | 3 | |
| 1700-1799 | 2 | |
| 1800-1899 | 2 | |
| 1900+ | 0 | Absorbed into MOD_ARITH / DP-derived sums |

**Total: ~81 problems where AP sum is the binding math step**, heavily concentrated at 1100-1399. This is a *low-band anchor* — most useful for making Q1 fast, less so for higher-rated problems.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Triangular sum [1100]

**Cards (3):**
- a.1 — Formula for `1 + 2 + ... + n`
- a.2 — Overflow reflex: when does this overflow int?
- a.3 — Inverse: given the sum, recover n

---

## b. Arithmetic progression sum (general) [1100]

**Cards (3):**
- b.1 — Formula for `a + (a+d) + (a+2d) + ... + (a+(k-1)d)` over k terms
- b.2 — Formula via first-term and last-term form: `k(first+last)/2`
- b.3 — Recognising when a problem reduces to AP sum

---

## c. Sum of integers in `[L, R]` [1200]

**Depends on:** Triangular sum [1100]

**Cards (1):**
- c.1 — Closed form for `L + (L+1) + ... + R`

---

## d. Sum of even numbers / sum of odd numbers in `[L, R]` [1300]

**Cards (2):**
- d.1 — Sum of first n even numbers
- d.2 — Sum of first n odd numbers

---

## e. Sum of multiples of d in `[L, R]` [1300]

**Depends on:** Arithmetic progression sum [1100]

**Cards (1):**
- e.1 — Closed form for `Σ (multiples of d in [L, R])`

---

## f. Sum of digit-positional values [1400]

**Cards (1):**
- f.1 — `Σ d_i × 10^i` for digits of n — appears in digit-sum problems

---

## g. Sum of squares [1500]

**Cards (2):**
- g.1 — Formula for `1² + 2² + ... + n²`
- g.2 — Recognising when problem reduces to sum-of-squares

---

## h. Sum of cubes [1500]

**Cards (1):**
- h.1 — Formula for `1³ + 2³ + ... + n³` (and its relation to triangular sum)

---

## i. Sum of products / pairwise sums [1600]

**Cards (2):**
- i.1 — `Σ_{i<j} (a_i × a_j)` in terms of `(Σ a_i)² - Σ a_i²`
- i.2 — `Σ_{i<j} (a_i + a_j) = (n-1) × Σ a_i`

---

## j. Geometric series sum [1700]

**Cards (2):**
- j.1 — Formula for `1 + r + r² + ... + r^(n-1)` when r ≠ 1
- j.2 — Special case r = 2: `2^n - 1`

---

## k. Telescoping sums [1800]

**Cards (2):**
- k.1 — Recognising telescoping pattern (`f(k) - f(k-1)` summed collapses to endpoints)
- k.2 — Common telescoping identity: `1/(k(k+1)) = 1/k - 1/(k+1)`

---

## Card count

19 atomic cards across 11 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (3) + b (3) = **6 cards** |
| 1200-1299     | + c (1) = **7 cards** |
| 1300-1399     | + d (2) + e (1) = **10 cards** |
| 1400-1499     | + f (1) = **11 cards** |
| 1500-1599     | + g (2) + h (1) = **14 cards** |
| 1600-1699     | + i (2) = **16 cards** |
| 1700-1799     | + j (2) = **18 cards** |
| 1800+         | + k (2) = **19 cards (full)** |

## Notes for Socratic drill

- Subtopic `a` (triangular sum) is the single most frequently invoked formula in this whole topic — and likely the one that took 20 minutes to derive last time. Card `a.1` graduates first; everything else builds on it.
- The cast-to-long reflex (`a.2`) is a Java-impl pre-submit check, but it lives here because the formula is where the overflow happens. Pair this with the Java syntax notes in `02-syntax/05-conversions.md`.
- Subtopic `i` (sum of products / pairwise sums) is the bridge to *contribution technique* — covered later in the Pair / Triple Count topic. `i.1` and `i.2` install the algebraic identity; the contribution interpretation gets installed there.
