# Modular Arithmetic [1100]

The math of "remainders" — operations on integers `mod p`. Starts shallow at 1100 (`n % 2`, simple divisibility checks) and grows into a deep topic at 1700+: modular inverses, Fermat's little theorem, counting permutations under `mod 10⁹+7`.

**This is the topic that grows fastest with rating.** At 1400 it's 16% of math (driven by simple divisibility), at 1600-1700 it's 12-18%, and at **1800 it becomes the #1 math topic at 22%** — every Q4-tier counting problem ends with "return the count mod 10⁹+7."

## Empirical frequency

| Band | MOD_ARITH-tagged | % of math |
|------|------------------|-----------|
| 1100-1399 | 17 (under MOD_DIV legacy tag) | 6% |
| 1400-1499 | — | 16% (#1 spike from "cyclic" problems) |
| 1500-1599 | 9 | 11.5% |
| 1600-1699 | 9 | 13.8% |
| 1700-1799 | 13 | 18.3% |
| 1800-1899 | 17 | **21.8% (#1)** |
| 1900+ | — | dominant |

**Total: 70+ problems.** Universal anchor topic — appears at every band from 1100 to 2500+.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Modulo operator basics [1100]

**Cards (3):**
- a.1 — `a % b` returns remainder in `[0, b-1]` for positive `a, b`
- a.2 — Java trap: `a % b` returns a **negative** value when `a < 0` (sign follows dividend). Fix: `((a % b) + b) % b` to normalise to `[0, b-1]`
- a.3 — `a % b == 0` ↔ `b` divides `a` (the divisibility test)

---

## b. Divisibility rules by digit pattern [1200]

**Cards (4):**
- b.1 — Divisible by 3 ↔ digit sum divisible by 3
- b.2 — Divisible by 9 ↔ digit sum divisible by 9
- b.3 — Divisible by 11 ↔ alternating digit sum divisible by 11
- b.4 — **Casting out nines (the general invariant b.1/b.2 are special cases of):** `N ≡ digitSum(N) ≡ sum of ANY partition of N's digits (mod 9)` — splitting digits into pieces and summing preserves the value mod 9. ⟹ **a partition of N's digits can sum to `S` only if `S ≡ N (mod 9)`** (a free pruning filter). Corollary: `a² ≡ a (mod 9)` ⟹ `a ≡ 0 or 1 (mod 9)`.

**Depends on:** Digit Operations → digit sum [1100]

**LC anchor:** *Smallest Even Multiple* (LC 2413); *Find the Punishment Number of an Integer* (LC 2698) — b.4 prunes candidates to `i ≡ 0,1 (mod 9)` since a partition of `i²`'s digits can sum to `i` only if `i ≡ i² (mod 9)`.

---

## c. Cyclic / modular wrap-around [1300]

**Cards (2):**
- c.1 — Circular array index: `arr[(i + k) % n]` for forward wrap, `arr[((i - k) % n + n) % n]` for backward
- c.2 — Cyclic distance between two indices: `min(|i - j|, n - |i - j|)` — and the alphabet variant `min(d, 26 - d)`

**LC anchor:** *Lex Smallest String After Operations With Constraint* (LC 3106), *Shift Distance Between Two Strings* (LC 3361)

---

## d. Addition / subtraction mod m [1400]

**Cards (2):**
- d.1 — `(a + b) % m = ((a % m) + (b % m)) % m` — reduce before adding to avoid overflow
- d.2 — Subtraction trap: `(a - b) % m` can be negative; use `((a - b) % m + m) % m`

---

## e. Multiplication mod m [1400]

**Cards (3):**
- e.1 — `(a × b) % m = ((a % m) × (b % m)) % m`
- e.2 — Overflow reflex: when `m ≈ 10⁹+7`, `(a % m) × (b % m)` is up to 10¹⁸ — fits in `long`, not `int`. Always cast to `long` before multiplying.
- e.3 — Mod-multiply template: `result = (result * a) % MOD` inside loop

**LC anchor:** *Unit Conversion I* (LC 3528)

---

## f. Sum mod m / running sum [1400]

**Cards (1):**
- f.1 — Accumulator pattern: `sum = (sum + a[i]) % m` per iteration — avoid `sum % m` only at the end

---

## g. Counting under `mod 10⁹+7` [1600]

**Cards (2):**
- g.1 — The canonical mod: `1_000_000_007` is prime. Always declare `static final long MOD = 1_000_000_007L`
- g.2 — Pattern: "return the count mod 10⁹+7" — apply `% MOD` after every add and every multiply in the recurrence

**LC anchor:** Most counting DP problems at 1500+ that don't fit in `long`

---

## h. Power mod / fast exponentiation [1600]

**Cards (3):**
- h.1 — Compute `a^n mod m` in O(log n) via repeated squaring
- h.2 — Recursive form: `pow(a, n) = pow(a², n/2)` if n even, `a * pow(a², n/2)` if n odd
- h.3 — Iterative form with bit walk on `n`

**LC anchor:** *Super Pow* (LC 372), *Count Anagrams* (LC 2514)

---

## i. Modular inverse [1700]

**Depends on:** Power mod [1600]

**Cards (3):**
- i.1 — Inverse of `a` mod `p` (p prime) = `a^(p-2) mod p` (Fermat's little theorem)
- i.2 — Division under mod = multiplication by modular inverse: `(a / b) % p = (a × inv(b)) % p`
- i.3 — Precompute inverse factorials for combinatorial counting under mod

**LC anchor:** *Number of Ways to Reorder Array to Get Same BST* (LC 1569)

---

## j. Modular nCr — precomputed factorials [1700]

**Depends on:** Modular inverse [1700], Permutations & Combinations → nCr formula [1500]

**Cards (2):**
- j.1 — Precompute `fact[i]` and `inv_fact[i]` arrays up to MAX_N
- j.2 — `nCr % p = (fact[n] × inv_fact[r] × inv_fact[n-r]) % p`

**LC anchor:** *Count Anagrams* (LC 2514), *Number of Music Playlists* (LC 920)

---

## k. CRT / linear congruences [1800]

**Cards (2):**
- k.1 — Solve `x ≡ a₁ (mod m₁)` and `x ≡ a₂ (mod m₂)` via Chinese Remainder Theorem when `gcd(m₁, m₂) = 1`
- k.2 — Identification — most LC problems hint at CRT via "find smallest n such that..." with multiple periodic constraints

---

## l. Pigeonhole on mod values [1800]

**Cards (2):**
- l.1 — `n+1` integers chosen from `[1, 2n]` ⟹ two share a residue mod `n` ⟹ one divides the other (classic pigeonhole)
- l.2 — Prefix-sum mod m: if `n > m`, two prefix sums share a residue ⟹ some subarray sum is divisible by m

**LC anchor:** *Continuous Subarray Sum* (LC 523), *Smallest All-Ones Multiple* (LC 3790)

---

## Card count

29 atomic cards across 12 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (3) = **3 cards** |
| 1200-1299     | + b (4) = **7 cards** |
| 1300-1399     | + c (2) = **9 cards** |
| 1400-1499     | + d (2) + e (3) + f (1) = **15 cards** |
| 1500-1599     | — = 15 cards |
| 1600-1699     | + g (2) + h (3) = **20 cards** |
| 1700-1799     | + i (3) + j (2) = **25 cards** |
| 1800+         | + k (2) + l (2) = **29 cards (full)** |

## Notes for Socratic drill

- Subtopic `a.2` (negative mod) is one of the highest-recurrence Java bugs in the syllabus. Java's `%` follows sign of dividend, so `(-3) % 5 = -2`, not `3`. The reflex `((a % b) + b) % b` closes this trap permanently.
- Subtopic `e.2` (long-cast before multiply) is the Java-impl checklist bug family. Already documented in the CLAUDE.md pre-submit checklist — install here makes it reflexive.
- Subtopic `g.1` is the universal contest constant — `1_000_000_007` should be muscle memory by 1500. Use Java's `_` separators for readability.
- Subtopics `h` (power mod) and `i` (inverse) are the bridge to combinatorial mod counting. Install in sequence — `j` (mod nCr) is a direct consequence of `i.3`.
- Subtopic `l` (pigeonhole on mod) is the unexpected reframe that unlocks several "find subarray with property X mod m" problems. The pattern is famous but rarely top-of-mind.
- Subtopic `b.4` (casting out nines) is the *unifying* fact behind b.1/b.2 — drill it as "value ≡ digit-sum ≡ partition-sum (mod 9)." The non-obvious payoff is the **partition-sum filter**: whenever a problem asks "can these digits be split to sum to S?", the mod-9 check is a free necessary condition. Origin: Punishment Number debrief 2026-06-11 — it's a *bonus prune on an already-fast solution*, so install the reflex but don't reach for it unless TLE forces it.
