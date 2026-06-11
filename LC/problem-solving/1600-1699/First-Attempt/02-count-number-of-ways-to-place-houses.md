# 02 — Count Number of Ways to Place Houses

- **Link:** https://leetcode.com/problems/count-number-of-ways-to-place-houses/
- **Band:** 1600–1699 · sealed queue · blind deal #2 · Q2 (AR 44.0%)
- **Bucket (revealed post-solve):** **DP » Linear** (Fibonacci recurrence). Trap-carrier: square + overflow.
- **Dealt:** 2026-06-10
- **Result:** ❌ **HINTED + WA-then-AC** — derivation Socratic (axis-switch reached via Claude's Qs); then **first submission WA** (overflow — no mod inside the loop) → fixed → AC. Double non-counting (hinted *and* soft-fail). **DP-Linear still owes 2.** Acquisition/learning rep; counts **against** the band clean-rate metric.
- **AC:** 2026-06-10 (version 2, mod-in-loop). Perturbation debrief still pending.

---

## The problem
A street has `n` plots on each of 2 sides. Place houses so that **no two houses are adjacent on the same side** (across sides is fine). Count placements, mod 1e9+7.

## Attempt 1 — user, combinatorial (count by number of houses) — *stalled*
Idea: on one side, sum over `k` = number of houses placed, of (ways to place `k` non-adjacent houses in `n` plots):
- `k=0` → 1
- `k=1` → `n`
- `k=2` → `C(n,2) − (n−1)` ✅ (all pairs minus the `n−1` adjacent pairs) — **correct**
- `k=3` → **stuck** — inclusion-exclusion for "no two of 3 adjacent" gets ugly.

User's read: "not able to get nc3 … I'm cooked." → the **count-by-quantity axis** forces messy inclusion-exclusion. That stall is the signal to change what's being counted.

## The pivot — Socratic (HINTED)
Claude initially dumped the full answer, user said *"do it Socratically"*, redone as Q&A:

- **Q1 (Claude):** states of a single plot? → **user:** "two — filled or empty." ✅
- **Q2 (Claude):** let `f(i)` = valid ways for first `i` plots; split on plot `i`'s state — empty → ? , filled → forces what? → **user:** "if we place `i`, we skip `i-1` and go to `i-2`… it's linear DP!" → derived **`f(i) = f(i-1) + f(i-2)`** (Fibonacci). ✅
- **Q3 (Claude, user declined further hints to finish solo):**
  - (a) base cases `f(0)`, `f(1)` — *user solving*
  - (b) two sides are independent — is the total `2·f(n)` or something else? *(this targets the user's earlier "double it" instinct — the answer is `f(n)²`, multiplicative, since each left arrangement pairs with each right arrangement — user to confirm solo)*

## Key facts established (the install content)
- **Recurrence:** `f(i) = f(i-1) + f(i-2)`, base `f(0)=1` (empty street), `f(1)=2` (empty / one house).
- **Two sides:** independent ⇒ answer = **`f(n)²`** mod, **not** `2·f(n)` (the multiplicative-vs-additive catch).
- **Trap [overflow]:** `f(n)` ~1e9, so `f(n)*f(n)` overflows `int` → reduce `f(n) % MOD` first, then `((long)x * x) % MOD`.
- **Retro-insight:** `Σ_k C(n−k+1, k) = Fibonacci` — Attempt 1's counting wasn't *wrong*, just the hard road; the DP collapses the whole sum into two additions.

## Lesson / reflex to bank
**"Count arrangements under a no-two-adjacent (or per-position) constraint" → do NOT count by quantity (forces inclusion-exclusion) → decide per position → linear DP.** Axis-switch from *how-many* to *what-does-this-position-do* is the linear-DP trigger.

## WA-cause / miss tag
**[wrong-axis]** — chose count-by-quantity (combinatorial) over decide-per-position (DP); correct but self-defeating, stalled at `k=3`. Plus latent **[multiplicative-vs-additive]** (the "double it" → should be square) and **[overflow]** on the square.

## The overflow / mod lesson (Socratic — the REAL WA)

**WA:** first submission (no mod in the loop) failed at `n = 1000` — got `542247860`, expected `500478595`.
```java
long next = (prev + secondPrev);        // ✗ no mod → prev explodes past long
```
**User's misconception:** *"the sum will never exceed ~10⁸, so how is it overflow?"*

**Break (Socratic):**
- Ratio of consecutive terms `3/2, 5/3, 8/5, 13/8 → ≈ 1.6` (golden ratio φ). A **constant factor > 1 every step** ⇒ multiplying, not adding ⇒ **exponential**: `f(n) ≈ 1.6ⁿ`.
- "Multiply by `c`, `n` times = `cⁿ`" (repeated multiplication *is* exponentiation — `n` multiplications ⇒ exponent `n`).
- Scale: a `long` holds ≈ `9.2×10¹⁸ ≈ 2⁶³`. `f(n)` blows past that around **n ≈ 90** (Fibonacci overflows `long` near `F(92)`). By `n = 1000`, `f` has **~200 digits** → `prev` has wrapped `long` many times → garbage → WA.
- **Misconception corrected:** "answer mod 1e9+7" bounds the **answer**, NOT the **intermediate Fibonacci values** — those are unbounded.

**Fix (version 2, AC):** `% MOD` every step. Does two jobs at once:
1. keeps every value `< 1e9` so `prev + secondPrev` can never overflow `long`;
2. preserves the answer via **modular distributivity**: `(a + b) % m == ((a % m) + (b % m)) % m` — mod distributes over `+` and `×`, so reducing early is safe.

> **Why mod distributes (thread closed 2026-06-10):** write `a = q₁·m + r₁`, `b = q₂·m + r₂`; then `a + b = (q₁+q₂)·m + (r₁+r₂)`. The `(q₁+q₂)·m` chunk is a whole multiple of `m` ⇒ contributes 0 to the remainder, so `(a+b) % m` depends only on `r₁+r₂` ⇒ `= ((a%m)+(b%m)) % m` (same for `×`). **Reflex:** the multiple-of-MOD part of a running value is dead weight for the remainder — peeling it off every step is free *and* keeps values small (no overflow).

```java
long next = (prev + secondPrev) % MOD;  // ✓ mod every step
...
return (int) ((prev * prev) % MOD);     // square fits in long since prev < 1e9
```

**Reflex to bank [mod-timing]:** *In any accumulating recurrence whose values grow (Fibonacci/exponential, running products, factorials), take `% MOD` at EVERY step — never only at the end. "Answer mod M" never means "values stay near M."* Pairs with **[overflow]**: cast to `long` before a product (`(long)x * x`).

## WA-cause tags
- **[wrong-axis]** — count-by-quantity (combinatorial) over decide-per-position (DP); stalled at `k=3`.
- **[mod-timing / overflow]** — modded only at the end; exponential intermediate values overflowed `long` ⇒ WA at `n=1000`.

## PENDING
- Perturbation debrief — **to be worked Socratically in chat first, then logged** ([[lc-perturbation-before-write]]). No probes pre-written here.
- Revision Day+14: re-derive the per-position recurrence cold; reproduce `f(n)²` + **mod-every-step** + the `(long)` square guard; re-state why mod distributes.
