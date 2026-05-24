# GCD / LCM & Number Theory [1100]

The divisibility side of math — factors, multiples, primes, GCD, LCM. Where modular arithmetic asks "what's the remainder?", number theory asks "what divides what, and how do they relate?"

Lower-frequency topic per-band but **universal across bands** — every band from 1100 to 2500+ has at least a handful of GCD/LCM/prime problems. Total appearances stack up to ~30+ problems in the 1100-1899 range.

Tightly fused with the **Modular Arithmetic** topic — `gcd` enables modular inverse via extended Euclidean, and prime structure unlocks Fermat's little theorem.

## Empirical frequency

| Band | GCD_LCM | PRIME | DIVISORS | Combined |
|------|---------|-------|----------|----------|
| 1100-1399 | 5 (1.7%) | — | — | ~6% |
| 1400-1499 | tail | tail | tail | ~3% |
| 1500-1599 | 2 (2.6%) | 3 (3.8%) | — | ~7% |
| 1600-1699 | tail | tail | tail | ~5% |
| 1700-1799 | tail | 2 (2.8%) | tail | ~5% |
| 1800-1899 | 4 (5.1%) | 1 (1.3%) | 1 (1.3%) | ~8% |
| 1900+ | — | recurring | — | — |

**Total: ~30 problems** where number-theory reasoning is the binding step.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Factors and multiples — definitions [1100]

**Cards (3):**
- a.1 — `d` is a factor (divisor) of `n` iff `n % d == 0`
- a.2 — `n` is a multiple of `d` iff `n % d == 0` (the same relation, named from the other side)
- a.3 — Every positive integer has factors `1` and itself; primes have exactly these two

---

## b. Counting divisors of n [1200]

**Cards (2):**
- b.1 — Iterate `i` from 1 to `√n`; each `i` that divides `n` contributes 2 divisors (`i` and `n/i`), except when `i² == n` (counts once)
- b.2 — Time complexity: O(√n) for single n. Don't iterate to n.

**LC anchor:** *Number of Divisors of n*

---

## c. Sum of divisors of n [1200]

**Cards (1):**
- c.1 — Same `√n` loop as b.1, but accumulate `i + n/i` instead of counting

---

## d. ceil(a/b) and floor(a/b) integer arithmetic [1300]

**Cards (3):**
- d.1 — `floor(a / b) = a / b` in Java for positive a, b
- d.2 — `ceil(a / b)` without floats: `(a + b - 1) / b` for positive a, b
- d.3 — Trap: `Math.ceil((double) a / b)` works but introduces float precision risk for large values; prefer the integer form

---

## e. Prime check — trial division [1300]

**Cards (2):**
- e.1 — `n` is prime iff no `d` in `[2, √n]` divides n. Loop `i = 2` to `i*i <= n`.
- e.2 — Edge cases: n=1 not prime, n=2 prime, even-n>2 not prime

**LC anchor:** *Count Primes* (LC 204)

---

## f. Sieve of Eratosthenes [1400]

**Cards (3):**
- f.1 — Generate all primes up to N in O(N log log N) — for each prime p, mark p², p²+p, ... as composite
- f.2 — Start marking from `p*p`, not `2*p` — smaller multiples already marked by smaller primes
- f.3 — Memory: `boolean[N+1]` — works for N up to ~10⁷ in Java

**LC anchor:** *Prime Pairs With Target Sum* (LC 2761), *Count Primes* (LC 204)

---

## g. GCD — Euclidean algorithm [1300]

**Cards (3):**
- g.1 — Definition: `gcd(a, b)` = largest integer that divides both
- g.2 — Recursive: `gcd(a, b) = gcd(b, a % b)`, base `gcd(a, 0) = a`
- g.3 — Java: no built-in `gcd` for `int` — use `BigInteger.gcd` or write your own (5-line method)

---

## h. LCM — from GCD [1300]

**Depends on:** GCD [1300]

**Cards (2):**
- h.1 — `lcm(a, b) = a * b / gcd(a, b)` — derived from `gcd × lcm = a × b`
- h.2 — Overflow: `a * b` overflows int when a, b near 10⁹ — cast to long, or compute as `a / gcd(a, b) * b` to defer multiply

**LC anchor:** *Maximum Factor Score of Array* (LC 3334), *Number of Subarrays With LCM Equal to K* (LC 2470)

---

## i. GCD of an array [1400]

**Cards (2):**
- i.1 — `gcd(a[0], a[1], ..., a[n-1])` = fold gcd left-to-right
- i.2 — `gcd(a, 0) = a` makes 0 the identity element — useful when initialising fold

---

## j. Coprime / relatively prime [1400]

**Cards (2):**
- j.1 — `a` and `b` are coprime iff `gcd(a, b) = 1`
- j.2 — Coprime test invocations: "Walk diagonal of grid lattice", "lattice points visible from origin"

---

## k. Prime factorisation [1500]

**Cards (2):**
- k.1 — Trial division: for `p = 2, 3, ..., √n`, while `n % p == 0` divide out and accumulate exponent
- k.2 — Time complexity: O(√n) for single n. For multiple n, precompute smallest prime factor (SPF) array via modified sieve.

**LC anchor:** *Find the Count of Numbers Which Are Not Special* (LC 3233 — count of n with exactly 2 proper divisors = prime squares)

---

## l. Linear sieve / SPF (smallest prime factor) [1700]

**Depends on:** Sieve [1400]

**Cards (1):**
- l.1 — Modified sieve stores `spf[i] = smallest prime factor of i`. Enables O(log n) factorisation per query.

---

## m. GCD-related identities [1700]

**Cards (3):**
- m.1 — `gcd(a, b) = gcd(a-b, b)` — subtraction form
- m.2 — `gcd(a, b) × lcm(a, b) = a × b` — product identity
- m.3 — `gcd` distributes over commutative ops: `gcd(ka, kb) = k × gcd(a, b)`

---

## n. Lattice points on segment via GCD [1700]

**Depends on:** GCD [1300], Geometry → h.1 [1500] (cross-link)

**Cards (1):**
- n.1 — Lattice points strictly between `(x₁, y₁)` and `(x₂, y₂)` = `gcd(|dx|, |dy|) - 1`. Endpoint-inclusive form: +2 = `gcd + 1`.

---

## o. Pigeonhole on divisibility [1800]

**Cards (1):**
- o.1 — Among `n+1` integers in `[1, 2n]`, some pair has one dividing the other (classic pigeonhole — each integer has a unique odd part)

**LC anchor:** *Smallest Integer Divisible by K* (LC 1015)

---

## p. Extended Euclidean & modular inverse [1800]

**Depends on:** GCD [1300], Modular Arithmetic → modular inverse [1700]

**Cards (1):**
- p.1 — Extended Euclidean finds integer `x, y` such that `ax + by = gcd(a, b)`. When `gcd(a, m) = 1`, `x` is the modular inverse of `a` mod `m`. Alternative to Fermat's little theorem for non-prime moduli.

---

## Card count

32 atomic cards across 16 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (3) = **3 cards** |
| 1200-1299     | + b (2) + c (1) = **6 cards** |
| 1300-1399     | + d (3) + e (2) + g (3) + h (2) = **16 cards** |
| 1400-1499     | + f (3) + i (2) + j (2) = **23 cards** |
| 1500-1599     | + k (2) = **25 cards** |
| 1600-1699     | — = 25 cards |
| 1700-1799     | + l (1) + m (3) + n (1) = **30 cards** |
| 1800+         | + o (1) + p (1) = **32 cards (full)** |

## Notes for Socratic drill

- Subtopic `b.1` (count divisors in O(√n)) is the foundational number-theory pattern — every "divisors of n" problem starts here. Install cold first.
- Subtopic `d.2` (`ceil(a/b) = (a + b - 1) / b`) closes the float-cast trap from the CLAUDE.md checklist (item #2: `(int) Math.pow` and friends). Install as paired reflex with the float-cast warning.
- Subtopic `g` (Euclidean GCD) is one of the highest-leverage installs in the syllabus — unlocks GCD/LCM, coprime checks, lattice-point geometry, and modular inverse. Five-line method should be writable from memory.
- Subtopic `h.2` (LCM overflow via `a / gcd × b`) is the contest-recurring bug — most candidates write `a * b / gcd` and hit overflow at 10⁹. The defer-multiply form (`a / gcd × b`) avoids it.
- Subtopic `l` (linear sieve / SPF) is the bridge between sieve and per-number factorisation. Install when 1700 band opens.
- Subtopic `p` (extended Euclidean) is the alternative to Fermat for modular inverse — needed only when the modulus is non-prime. Install at 1800.
