# Probability & Expected Value [1100]

Probability calculations — uniform/conditional probability, expected value (sum of outcome × probability), random-walk identities. Distinct from counting (#3, #10) because the question shifts from "how many?" to "what's the chance?" or "what's the average outcome?"

Mid-frequency at low bands (3.5% at 1100) — but most low-band probability problems collapse to "favourable / total" once enumerated. Becomes more substantial at 1800+ (3.8%) where expected-value DP emerges as a distinct pattern.

## Empirical frequency

| Band | PROB-tagged | % of math |
|------|-------------|-----------|
| 1100-1399 | 10 | 3.5% |
| 1400-1499 | tail | ~2% |
| 1500-1599 | tail | ~1% |
| 1600-1699 | 1 | 1.5% |
| 1700-1799 | tail | ~1% |
| 1800-1899 | 3 | 3.8% |
| 1900+ | tail | — |

**Total: ~15 problems** where probability or expected value is the binding step.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Probability fundamentals [1100]

**Cards (3):**
- a.1 — `P(event) = favourable outcomes / total outcomes` for finite uniform sample space
- a.2 — Probability is always in `[0, 1]` — invariant check
- a.3 — Complement: `P(not A) = 1 - P(A)` — often the easier form to compute

---

## b. Uniform random pick [1200]

**Cards (1):**
- b.1 — "Pick a random index" → each index has probability `1/n` → `Random.nextInt(n)` in Java

**LC anchor:** *Random Pick with Weight* (LC 528 — non-uniform variant), *Insert Delete GetRandom O(1)* (LC 380)

---

## c. Independent events — multiplication rule [1300]

**Cards (1):**
- c.1 — `P(A and B) = P(A) × P(B)` when A and B are independent

---

## d. Mutually exclusive — addition rule [1300]

**Cards (1):**
- d.1 — `P(A or B) = P(A) + P(B)` when A and B can't both occur

---

## e. Conditional probability [1500]

**Cards (1):**
- e.1 — `P(A | B) = P(A and B) / P(B)` — "given B happened, chance of A"

---

## f. Expected value — discrete sum [1600]

**Cards (2):**
- f.1 — `E[X] = Σ x × P(X = x)` over all outcomes x
- f.2 — Linearity: `E[X + Y] = E[X] + E[Y]` always (even if X, Y dependent)

**LC anchor:** *New 21 Game* (LC 837)

---

## g. Geometric / waiting-time expectation [1700]

**Cards (1):**
- g.1 — If a single trial succeeds with probability `p`, expected number of trials until first success = `1/p`

---

## h. Expected-value DP [1800]

**Cards (3):**
- h.1 — State design: `E[state] = Σ P(transition) × (gain + E[next state])`
- h.2 — Bounded random walks: `dp[pos][steps] = (1/k) × Σ dp[neighbour][steps-1]`
- h.3 — Floating-point in Java: use `double`, accept ~1e-9 precision; some LC problems require exact fractions instead

**LC anchor:** *Number of Ways to Stay in the Same Place* (LC 1269), *Knight Probability in Chessboard* (LC 688)

---

## i. Probability under mod 10⁹+7 [1900]

**Depends on:** Modular Arithmetic → modular inverse [1700]

**Cards (1):**
- i.1 — When answer is a fraction `p/q`, return `p × inv(q) % MOD` instead of a float

**Note:** Niche — install only at 1900+ target.

---

## Card count

13 atomic cards across 9 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (3) = **3 cards** |
| 1200-1299     | + b (1) = **4 cards** |
| 1300-1399     | + c (1) + d (1) = **6 cards** |
| 1400-1499     | — = 6 cards |
| 1500-1599     | + e (1) = **7 cards** |
| 1600-1699     | + f (2) = **9 cards** |
| 1700-1799     | + g (1) = **10 cards** |
| 1800-1899     | + h (3) = **13 cards** |
| 1900+         | + i (1) = **14 cards (full)** |

## Notes for Socratic drill

- Subtopic `a.3` (complement) is the highest-recurrence trick — "probability of at least one X" is almost always easier as `1 - P(no X)`. Install as a reflex.
- Subtopic `f.2` (linearity of expectation) is the single most-powerful identity in this topic — works even when variables aren't independent. Most 1700+ probability problems collapse via linearity.
- Subtopic `h` (expected-value DP) is the 1800-band pattern. Same shape as counting DP but values are probabilities, not counts.
- Subtopic `i` (probability under mod) is rare on LC but signature of CP-style probability problems. Install only at 1900+.
- This topic has the smallest empirical footprint of the syllabus — but probability problems are notorious for being unsolvable without the install. High-stakes when it appears.
