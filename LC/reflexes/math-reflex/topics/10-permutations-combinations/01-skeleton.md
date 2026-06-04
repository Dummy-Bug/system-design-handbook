# Permutations & Combinations [1100]

Counting arrangements (`n!`, `nPr`) and selections (`nCr`, `n choose k`). The combinatorial backbone — once installed, "how many ways to..." problems collapse from search to formula.

Appears consistently 9-12% across all bands from 1100 to 1900. The shape of usage changes with rating: at 1100 it's plain `n!` and `nC2`, at 1500 it's nCr-from-factorials, at 1700-1800 it's nCr-under-mod plus Catalan / multinomial.

## Empirical frequency

| Band | PERM_COMB-tagged | % of math |
|------|------------------|-----------|
| 1100-1399 | 26 | 9.1% |
| 1400-1499 | — | 12% |
| 1500-1599 | 7 | 9.0% |
| 1600-1699 | — | 9% |
| 1700-1799 | 8 | 11.3% |
| 1800-1899 | 7 | 9.0% |
| 1900+ | tail | — |

**Total: ~50+ problems.** Universal mid-frequency anchor.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Factorial — n! [1100]

**Cards (3):**
- a.1 — `n!` = n × (n-1) × ... × 1; `0! = 1` by convention
- a.2 — Growth: `10! ≈ 3.6 × 10⁶`, `12! ≈ 4.8 × 10⁸`, `13!` overflows int, `20!` overflows long
- a.3 — Overflow boundary table: precompute factorials only up to safe range

**LC anchor:** *Find Permutation of Length N with Given Property* (factorial enumeration problems)

---

## b. Permutation count — nPr [1200]

**Cards (2):**
- b.1 — `nPr = n! / (n-r)!` = arrangements of r items from n distinct
- b.2 — Special cases: `nP1 = n`, `nPn = n!`, `nP2 = n × (n-1)`

---

## c. Combination count — nCr [1200]

**Cards (3):**
- c.1 — `nCr = n! / (r! × (n-r)!)` = unordered selections of r from n distinct
- c.2 — Quick forms: `nC0 = nCn = 1`, `nC1 = n`, `nC2 = n(n-1)/2`, `nC3 = n(n-1)(n-2)/6`
- c.3 — Symmetry: `nCr = nC(n-r)` — compute with smaller r to save work

**LC anchor:** *Pascal's Triangle* (LC 118)

---

## d. Pascal's triangle recurrence [1300]

**Cards (2):**
- d.1 — `nCr = (n-1)Cr + (n-1)C(r-1)` — the recurrence
- d.2 — Build `C[n+1][r+1]` table in O(n²) when r is unbounded; use for small n (n ≤ 1000)

---

## e. Counting arrangements with repetition [1300]

**Cards (2):**
- e.1 — "Strings of length n over an alphabet of size k": `k^n` (each position independently chosen)
- e.2 — Permutations of multiset: `n! / (n₁! × n₂! × ... × nₖ!)` (divide by group factorials for indistinguishable items)

---

## f. Stars and bars (lite) [1300]

**Cards (1):**
- f.1 — "Distribute n identical items into k distinct boxes, no restriction": `C(n + k - 1, k - 1)`

**LC anchor:** *Distribute Candies Among Children I* (LC 2928 — n=3 boxes case)

**Note:** Full Stars & Bars (with bounds, inclusion-exclusion) is topic #11 — split out because the bounded variants are structurally distinct.

---

## g. nCr without factorial — multiplicative [1400]

**Cards (2):**
- g.1 — `nCr = ∏(i=1 to r) (n - r + i) / i` — multiply numerator and divide denominator term by term, no intermediate overflow
- g.2 — Why: avoids computing `n!` when n is large (e.g., n = 10⁵, r = 5)

---

## h. Counting with constraints — inclusion-exclusion [1500]

**Cards (2):**
- h.1 — `|A ∪ B| = |A| + |B| - |A ∩ B|` — two-set form
- h.2 — General: `|A₁ ∪ ... ∪ Aₙ| = Σ|Aᵢ| - Σ|Aᵢ ∩ Aⱼ| + Σ|Aᵢ ∩ Aⱼ ∩ Aₖ| - ...`

**LC anchor:** *Count Number of Special Subsequences*, problems with multiple forbidden patterns

---

## i. nCr under mod p (precomputed) [1700]

**Depends on:** Modular Arithmetic → j (precomputed factorials) [1700]

**Cards (2):**
- i.1 — Precompute `fact[i]` and `inv_fact[i]` arrays up to MAX_N
- i.2 — `nCr % p = (fact[n] × inv_fact[r] × inv_fact[n-r]) % p`

**LC anchor:** *Count Anagrams* (LC 2514), *Number of Music Playlists* (LC 920)

**Note:** Cross-references topic 6 (Modular Arithmetic). Same cards, different home topic — install once, used from both.

---

## j. Catalan numbers [1700]

**Cards (3):**
- j.1 — `C(n) = (1/(n+1)) × C(2n, n)` — the n-th Catalan number
- j.2 — First few: 1, 1, 2, 5, 14, 42, 132, ...
- j.3 — Recurrence: `C(n) = Σ(i=0 to n-1) C(i) × C(n-1-i)`
- j.3b — Identification: count of valid bracket sequences, binary trees, monotonic paths below diagonal

**LC anchor:** *All Possible Full Binary Trees* (LC 894), *Generate Parentheses* (LC 22)

---

## k. Multinomial coefficient [1800]

**Cards (1):**
- k.1 — `(n; n₁, n₂, ..., nₖ) = n! / (n₁! × n₂! × ... × nₖ!)` — generalisation of nCr to k groups

---

## l. Derangements [1900]

**Cards (1):**
- l.1 — D(n) = number of permutations with no fixed point = `n! × Σ(i=0 to n) ((-1)^i / i!)` ≈ `n! / e`

**Note:** Niche — install only if targeting 1900+ specifically.

---

## Card count

24 atomic cards across 12 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (3) = **3 cards** |
| 1200-1299     | + b (2) + c (3) = **8 cards** |
| 1300-1399     | + d (2) + e (2) + f (1) = **13 cards** |
| 1400-1499     | + g (2) = **15 cards** |
| 1500-1599     | + h (2) = **17 cards** |
| 1600-1699     | — = 17 cards |
| 1700-1799     | + i (2) + j (4) = **23 cards** |
| 1800-1899     | + k (1) = **24 cards** |
| 1900+         | + l (1) = **25 cards (full)** |

## Notes for Socratic drill

- Subtopic `a.2` (factorial overflow boundary) is the Java-impl trap — `13!` overflows int, `21!` overflows long. Lock this as a sibling fact to the digit-overflow card (Digit Ops i.2) and AP overflow (Arithmetic Sums a.2).
- Subtopic `c.2` (quick nCr forms `nC2 = n(n-1)/2`, `nC3 = n(n-1)(n-2)/6`) is the highest-recurrence formula in this topic. This is also the formula that took the user 20 minutes to derive originally — Pair/Triple Count topic #3 covers the pair side; this card covers the formula side.
- Subtopic `g` (multiplicative nCr without factorial) is the "I have n=10⁵, r=5" reflex. Skip the factorial table, multiply term by term.
- Subtopic `i` (nCr under mod) is the same cards as Modular Arithmetic `j`. Cross-referenced — install once, used twice.
- Subtopic `j` (Catalan) is the 1700+ trick. Spotting Catalan structure (valid brackets, BST count, monotonic paths) is the muscle; computing the value is just the formula.
- Subtopic `l` (derangements) is gated behind 1900+ targets — niche, install only if needed.
