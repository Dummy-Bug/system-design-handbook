# Matrix Exponentiation & Linear Recurrences [1700]

When a linear recurrence (Fibonacci, tiling, transition DP) needs to compute the n-th term for very large n (n up to 10⁹ or 10¹⁸), matrix exponentiation reduces O(n) recurrence evaluation to O(d³ log n) where d is the recurrence dimension.

Niche but signature topic at 1800+ — appears in problems that explicitly say "compute the value at step n where n ≤ 10⁹". Without matrix exp, those problems are unsolvable in time limit.

## Empirical frequency

| Band | Tag | Count | % of math |
|------|-----|-------|-----------|
| 1100-1699 | — | 0 | — |
| 1700-1799 | FIB | 1 | 1.4% |
| 1800-1899 | MATRIX_EXP + FIB | 1 + 3 | ~5% combined |
| 1900+ | recurring | — | — |

**Total: ~8 problems** at ≤1900 — small but each is a Q3 / Q4 gate.

## When this topic fires

Three identification cues — any one means "consider matrix exp":

1. **Linear recurrence** — `f(n) = c₁ × f(n-1) + c₂ × f(n-2) + ... + cₖ × f(n-k)`
2. **n is huge** — n ≤ 10⁹ or 10¹⁸ (O(n) DP would TLE)
3. **Small state dimension** — k ≤ 50 or so (cube of dimension fits in time)

If all three hold, matrix exp is the binding step.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Linear recurrence — identification [1700]

**Cards (2):**
- a.1 — `f(n) = c₁ × f(n-1) + c₂ × f(n-2) + ... + cₖ × f(n-k)` — k-th order linear recurrence
- a.2 — Common examples: Fibonacci `f(n) = f(n-1) + f(n-2)`, Tribonacci, climbing stairs with custom step set

**LC anchor:** *Fibonacci Number* (LC 509 — small n form), *Climbing Stairs* (LC 70)

---

## b. Fibonacci closed form (Binet's) [1700]

**Cards (1):**
- b.1 — `F(n) = (φⁿ - ψⁿ) / √5` where `φ = (1+√5)/2`, `ψ = (1-√5)/2`. Float-precision warning — exact integer arithmetic needs matrix form.

---

## c. Matrix multiplication primer [1800]

**Cards (3):**
- c.1 — Matrix-matrix product: `C[i][j] = Σₖ A[i][k] × B[k][j]` — O(d³)
- c.2 — Identity matrix: `I[i][j] = 1 if i == j else 0` — multiplicative identity
- c.3 — Matrix-vector product: `(M × v)[i] = Σⱼ M[i][j] × v[j]` — O(d²)

---

## d. Recurrence → transition matrix [1800]

**Cards (3):**
- d.1 — For Fibonacci `[f(n+1), f(n)] = [[1,1],[1,0]] × [f(n), f(n-1)]` — the transition matrix encodes the recurrence
- d.2 — General k-th order: matrix is k×k, with shifted-identity below and recurrence coefficients in the top row
- d.3 — n-th term computed via `Mⁿ × initial_vector`

---

## e. Matrix exponentiation by squaring [1800]

**Depends on:** Modular Arithmetic → power mod [1600]

**Cards (2):**
- e.1 — `Mⁿ` computed in O(d³ log n) via repeated squaring (same algorithm as integer fast pow)
- e.2 — Result entry is `f(n) mod p` when each matrix multiply applies `% p`

**LC anchor:** *String Transformations I* (LC 3335 — 1806 rated — 26-state alphabet evolution), *Number of Music Playlists*

---

## f. State design for non-standard recurrences [1900]

**Cards (1):**
- f.1 — When recurrence is not pure-linear (e.g., depends on parity, position mod k, or auxiliary count), augment state to make it linear

---

## Card count

12 atomic cards across 6 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1699     | — = 0 cards |
| 1700-1799     | a (2) + b (1) = **3 cards** |
| 1800-1899     | + c (3) + d (3) + e (2) = **11 cards** |
| 1900+         | + f (1) = **12 cards (full)** |

## Notes for Socratic drill

- This topic doesn't open until 1700, and the full matrix-exp machinery (c, d, e) doesn't open until 1800. Don't install ahead of band.
- Subtopic `e.2` (matrix exp under mod) ties tightly to Modular Arithmetic `h` (power mod). Install in sequence — same fast-pow algorithm at higher dimension.
- Subtopic `f` (state augmentation) is the high-ceiling 1900+ trick. Out of scope for ≤1800 targets.
- Implementation cost: writing the 30-line matrix-pow template under contest pressure is half the install. Practice the boilerplate (matrix multiply + matrix pow + identity) so it comes out fast.
- LC-specific: at 1800-1900, only ~1 problem per band actually requires matrix exp. The install is high-cost per-use, but each use is unblocked entirely — without the install, the problem is impossible.
