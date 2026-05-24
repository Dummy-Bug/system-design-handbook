# Game Theory [1100]

Two-player adversarial games — Alice vs Bob, optimal play. The math is about determining who wins from a given position, often via parity, modular arithmetic, or DP. Rarely requires full minimax — most LC game-theory problems collapse to a clean invariant once spotted.

Mid-frequency at low bands (3.8% at 1100, where most problems are "spot the parity trick"). Drops sharply at 1500-1700 (1-4%) as problems narrow to specific Nim-like or DP-based games. Rises again at 1900+ as full Sprague-Grundy emerges — but that's past your target.

## Empirical frequency

| Band | GAME-tagged | % of math |
|------|-------------|-----------|
| 1100-1399 | 11 | 3.8% |
| 1400-1499 | tail | ~2% |
| 1500-1599 | 3 | 3.8% |
| 1600-1699 | tail | ~2% |
| 1700-1799 | 1 | 1.4% |
| 1800-1899 | tail | ~1% |
| 1900+ | recurring (Sprague-Grundy) | — |

**Total: ~20 problems** where game-theory reasoning is the binding step.

## The two-phase structure

Most LC game problems split into:
1. **Parity / invariant tricks (1100-1500)** — the answer reduces to "is some count odd?" or "is some modular condition met?"
2. **Minimax DP (1500-1800)** — explicit state DP with both players optimising

This topic covers both. The third phase (Sprague-Grundy / Nim variants) is out of scope for ≤1800 targets.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. The two-player invariant — "who plays the last move?" [1100]

**Cards (2):**
- a.1 — In a game with finite moves, the player who can't move loses. So "Alice wins" usually means "Alice makes the last move."
- a.2 — Count total moves; if odd, first player (Alice) makes the last one → Alice wins. If even, Bob wins.

**LC anchor:** *Stone Game* (LC 877 — answer is always "Alice wins" because Alice picks the parity she wants)

---

## b. Parity-based games [1100]

**Depends on:** Parity → a [1100]

**Cards (2):**
- b.1 — When moves change a parity invariant, the winner is determined by initial parity + move count
- b.2 — Recognition pattern: each player "takes" an even or odd quantity, and the final answer's parity is forced

**LC anchor:** *Divisor Game* (LC 1025 — Alice wins iff n is even, by parity)

---

## c. Pick-from-ends game (prefix-sum decision) [1200]

**Cards (1):**
- c.1 — When a player can pick from either end, the total stays fixed — Alice maximises her share. If total of `arr[0..n-1]` has fixed parity, Alice often wins by picking the larger-parity sum.

**LC anchor:** *Stone Game* (LC 877) — Alice picks either all even-indexed or all odd-indexed stones

---

## d. Mod-k forced-win conditions [1300]

**Cards (1):**
- d.1 — When each move removes 1, 2, or k items, the losing positions are typically those where `n % (k+1) == 0`

**LC anchor:** *Nim Game* (LC 292) — Bob wins iff `n % 4 == 0`

---

## e. Minimax DP — recursion form [1500]

**Cards (3):**
- e.1 — State: position / remaining items. Each player picks the move that **maximises their own score** = minimises opponent's
- e.2 — Recurrence: `dp[state] = max over moves m of (gain(m) - dp[next(state, m)])`
- e.3 — The subtraction in the recurrence captures "opponent will optimise against me"

**LC anchor:** *Stone Game VII* (LC 1690), *Stone Game IV* (LC 1510)

---

## f. Reframe to "can current player win?" boolean [1500]

**Cards (1):**
- f.1 — When the win/loss question is yes/no (no score involved), `dp[state] = true` if any move leads to a `false` state for the opponent

**LC anchor:** *Stone Game IV* (LC 1510)

---

## g. Score-tracking minimax [1600]

**Cards (2):**
- g.1 — `dp[i][j]` = max score difference current player can achieve from `arr[i..j]`
- g.2 — Final answer: `dp[0][n-1] > 0` means first player wins

**LC anchor:** *Stone Game VII* (LC 1690)

---

## h. Nim XOR rule [1800]

**Cards (1):**
- h.1 — In classic Nim with piles `[p₁, p₂, ..., pₖ]`, the first player wins iff XOR of all piles ≠ 0. Otherwise second player wins.

**LC anchor:** *Game of Nim* family (rare on LC; common in CP)

---

## i. Sprague-Grundy intuition [1900]

**Cards (1):**
- i.1 — Identification only: every impartial game position has a Grundy number = `mex(Grundy values of reachable positions)`. Position has Grundy 0 ↔ losing. Composite games XOR their Grundy values.

**Note:** Out of scope for ≤1800 targets.

---

## Card count

14 atomic cards across 9 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (2) + b (2) = **4 cards** |
| 1200-1299     | + c (1) = **5 cards** |
| 1300-1399     | + d (1) = **6 cards** |
| 1400-1499     | — = 6 cards |
| 1500-1599     | + e (3) + f (1) = **10 cards** |
| 1600-1699     | + g (2) = **12 cards** |
| 1700-1799     | — = 12 cards |
| 1800+         | + h (1) = **13 cards** |
| 1900+         | + i (1) = **14 cards (full)** |

## Notes for Socratic drill

- Subtopic `a` (last-move = winner) is the reframe that solves 1/3 of game-theory problems at 1100-1500 instantly. Without it, candidates simulate; with it, they apply parity.
- Subtopic `d` (mod-k losing positions) is the *Nim Game* trick — `n % 4 == 0` is the entire solution. Lock the pattern, not the specific value.
- Subtopic `e.3` (the subtraction in `max - dp[next]`) is the most-confused step in minimax. Both players use the same `max`, but with the subtraction it expresses "I want to maximise (my gain - opponent's optimal future)."
- Subtopic `h` (Nim XOR) is iconic but rare on LC. Install it for completeness at 1800; don't waste reps if it's not appearing.
- Subtopic `i` (Sprague-Grundy) is full game-theory theory — out of scope unless targeting 1900+. Mention only.
