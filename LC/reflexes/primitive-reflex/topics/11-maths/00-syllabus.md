# Maths — Family Syllabus (Number Theory · Combinatorics · Contribution · Game/Parity)

> Standalone maths family in the **primitive-reflex** track. Built 2026-06-19. **Self-contained by design — requires
> ZERO knowledge of the separate `math-reflex/` folder** (that older band-organized *recall* track is left untouched;
> this family re-installs everything it needs at the deeper trigger→move level). The family's job is **trigger
> reflexes** — *recognize* the (often disguised) math question → *recall* the move → *produce* the code — since at
> 1400–1800 the gap is mapping, not arithmetic.
>
> **Provenance:** Scaler Academy *Maths I–IV* (the **necessary floor** — topic spine for Number Theory + nCr-mod)
> ∪ the empirical **band-tag taxonomy** (zerotrac 1400–1799, editorial-grounded — supplies Foundations / Contribution
> / Parity that Scaler omits). A recency scan of the latest LC ids surfaced **no emergent math topic**. cp-algorithms
> and `math-reflex/` were **not** consulted.

Discriminator (the confusion matrix that makes math-mapping fast): **is this question about —**
- *divisibility / remainder / primes / gcd* → **Number Theory** (M1), or
- *counting arrangements / selections* → **Combinatorics** (M2), or
- *summing a quantity over all pairs / subarrays* → **Contribution** (M3), or
- *who-wins / can-I-reach-X / odd-even invariant* → **Game-Theory & Parity** (M4)?

(Digit-level work, overflow, mod-rules, and series sums are the **Foundations** alphabet (M0) — used *inside* all four.)
That split is the core mapping skill for maths.

## ⚠ Scope boundary — what is NOT in this family
- **Geometry** — deferred (M6 stub; ~53 in-band but low contest value at 1700, your call).
- **Probability / expectation** — deferred (M5 stub; supply = 1 below 1800, genuinely doesn't exist yet at this level).
- **Advanced number theory** (matrix exponentiation, Euler totient, Sprague–Grundy, extended-Euclid inverse, Catalan,
  nCr-mod precompute arrays) — **appended on band entry at 1800+**, not built now.
- **Pure string/palindrome** → string family. **Meta-cognitive "tricks"** → `patterns/deck.md`. **Bit/XOR** → already
  its own family (`10-bit-manipulation/`).

> **Supply policy:** catalog + drill **1400–1800 now**; append the 1800–1900 atoms when that band's data is assembled
> (mirrors bits keeping Modules 5–6 as deferred stubs).

## Install + test loop (per atom)
1. **Classic** — the simpler tool solves it.
2. **Break the simpler tool** — a constraint forces the math move → derive it (Socratic).
3. **Extract the trigger** — the felt-signal + where it sits in the confusion matrix. *Notes written only after deriving.*
4. **Holdout** — a blind 1400–1800 band problem mapped <30 min self-derived = installed. (The band itself is the
   holdout deck; no separate deck — recognition is certified in vivo during the grind.)

## Modules (basic → advanced)

| # | Module | Atoms | Supply | Status | Syllabus |
|---|--------|-------|--------|--------|----------|
| 0 | **Foundations** (the alphabet) | overflow/long-cast · mod-rules (`(a±b)%m`, `(a·b)%m`, safe-neg) · constraint→budget · digit-ops · AP/triangular/square sums · powers-of-2 anchor | 44 | ▢ NEXT | `00-foundations/00-syllabus.md` |
| 1 | **Number Theory** | GCD/LCM (Euclid) · modpow (binary exp) · modular inverse (Fermat) · sieve+SPF · prime factorization · divisors (count Π(eᵢ+1)/enumerate/n²-trick) · remainder-bucket & prefix-mod reframes | 67 | ▢ | `01-number-theory/00-syllabus.md` |
| 2 | **Combinatorics** | pair/triple count (fix-the-middle) · nCr/Pascal/**nCr mod p** · permutations & **permutation rank** · stars-and-bars · inclusion–exclusion | 64 | ▢ | `02-combinatorics/00-syllabus.md` |
| 3 | **Contribution** | sum-over-all-subarrays/pairs (each element × #containing) · contribution w/ monotonic boundaries *(links Stack family)* | 19 | ▢ | `03-contribution/00-syllabus.md` |
| 4 | **Game-Theory & Parity** | parity invariant (reachability / make-X-exactly) · last-move/turn parity · optimal-play (Divisor/Stone) · pigeonhole (prefix-mod repeat) | 34 | ▢ | `04-game-theory-parity/00-syllabus.md` |
| 5 | **Probability** (linearity of expectation, indicators) | — | 1 | ⏸ DEFERRED (~1800+) | `05-probability/00-syllabus.md` |
| 6 | **Geometry** | — | 53 | ⏸ DEFERRED | `06-geometry/00-syllabus.md` |

**Active install scope = Modules 0–4.** Modules 5–6 kept in the syllabus, deferred. Install order = M0 → M1 → M2 → M3 → M4
(Foundations first, then the generative cores; Number Theory is the heart — best supply + the whole Scaler spine).

## Scaler floor mapping (the "necessary" topics that MUST be covered)
| Scaler unit | Concepts | → Atom(s) |
|---|---|---|
| **Maths I** | A,B & Modulo · Pair Sum Divisible by M · Implement Power Function · Prime Modulo Inverse | 0.2, 1.7, 1.2, 1.3 |
| **Maths II** | Enumerating GCD · GCD · All-Pairs GCD · Largest Co-Prime · Divisor Game | 1.1, 3.1, 4.3 |
| **Maths III** | Prime Sum · Count of Divisors · Count Distinct Prime · Sieve idioms | 1.4, 1.5, 1.6 |
| **Maths IV** | Compute nCr%m · Compute nCr%p · Sorted Permutation Rank (+Repeats) | 2.2, 2.3 |
> Scaler concept slides live at `Scaler-Academy/.../03 Maths/Maths {I–IV}/0 Main.pdf` — read per-module at build time
> (PDF text-extraction blocked locally; needs `brew install poppler`). Scaler is the floor, **not** sufficient: M0/M3/M4
> come from the band data, which Scaler doesn't teach.

## Supply (per-module, zerotrac 1400–1799, editorial-grounded tags)
M0 = 44 · M1 = 67 · M2 = 64 · M3 = 19 · M4 = 34 — all ≥2× the ownership bar. Dominant tags: MOD_ARITH 61, PERM_COMB 34,
PAIR_COUNT 29, PARITY 35, SUBARRAY_COUNT 16, CONTRIBUTION 12. Per-atom problem lists assembled at module entry.

## Sources
- **Scaler Academy** *Advanced DSA I → 03 Maths → Maths I–IV* (concept floor).
- **zerotrac** `band_1400_1499 … band_1700_1799 _final.tsv` (math-tagged supply + verified ratings).
- **LearnYard** `combinatorics-geometry.tsv`, **AlgoMaster** `maths-geometry.tsv` (cross-reference only).
- Recency scan of latest LC ids (≤3934) — no emergent topic found.
