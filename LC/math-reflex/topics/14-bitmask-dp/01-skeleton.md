# Bitmask DP [1700]

DP where the state is a **subset of n elements**, encoded as a bitmask. Used when `n ≤ 16-20` — small enough that 2^n states fit in memory and time. The signature pattern of Q4-tier (1800+) difficulty.

Different from generic Bit Operations (#7) — there, bits are individual properties of a number. Here, bits represent **set membership**, and the DP transitions over subsets of elements.

## Empirical frequency

| Band | BITMASK-tagged | % of math |
|------|----------------|-----------|
| 1100-1399 | — | — |
| 1400-1499 | — | — |
| 1500-1599 | tail | ~1% |
| 1600-1699 | tail | ~1% |
| 1700-1799 | 4 | 5.6% |
| 1800-1899 | 11 | **14.1% (#3)** |
| 1900+ | recurring | ~10% |

**Total: ~25+ problems.** Appears at 1700 as recognisable pattern, becomes dominant at 1800.

## Why this is a separate topic from Bit Ops (#7)

Bit Ops covers low-level bitwise mechanics (set/unset/popcount/shifts). Bitmask DP covers the **DP design pattern** that uses those mechanics — state design, transitions, complexity analysis. Same operators, different reasoning layer.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Recognising bitmask DP — the n ≤ 20 cue [1700]

**Cards (2):**
- a.1 — Constraint `n ≤ 16` (sometimes `n ≤ 20`) is the loud cue: brute force is `n!` (infeasible), but `2^n × n` works (1.6M ops at n=20)
- a.2 — Look for "assign elements" / "permute" / "select subset" with no greedy structure — bitmask DP fills the gap

**Depends on:** Bit Operations → h (binary representation as state) [1500]

---

## b. State design — mask as subset [1700]

**Cards (3):**
- b.1 — `mask` = subset of `n` elements currently used/visited/assigned
- b.2 — `dp[mask]` semantics: typical forms are "min cost to reach this subset", "count of ways", "max profit from this assignment"
- b.3 — Sometimes paired with extra dimension: `dp[mask][i]` where i = current position / last element

---

## c. Transition — flip one bit at a time [1700]

**Cards (2):**
- c.1 — Forward: from `dp[mask]`, for each unset bit `i`, transition to `dp[mask | (1 << i)]`
- c.2 — Backward: from `dp[mask]`, for each set bit `i`, came from `dp[mask ^ (1 << i)]`

---

## d. Iterating over subsets / supersets [1700]

**Depends on:** Bit Operations → h.3 (subset enumeration) [1500]

**Cards (2):**
- d.1 — Iterate all subsets of `mask`: `for (int s = mask; s > 0; s = (s - 1) & mask) { ... }`
- d.2 — Iterate set bits of `mask`: `for (int m = mask; m != 0; m &= (m - 1)) { int bit = m & -m; int i = trailingZeros(bit); }`

---

## e. Standard problem shapes [1700]

**Cards (3):**
- e.1 — Travelling salesman variant: `dp[mask][last]` = min cost to visit `mask` ending at `last`
- e.2 — Assignment: `dp[mask]` = min cost to assign first `popcount(mask)` workers to jobs in `mask`
- e.3 — Partition into k groups: `dp[mask]` = whether `mask` can be split into k valid subsets

**LC anchor:** *Travelling Salesman* (LC 943 variants), *Assign Cookies* style, *Partition to K Equal Sum Subsets* (LC 698)

---

## f. SOS DP (Sum over subsets) [1800]

**Cards (2):**
- f.1 — Compute `f(mask) = Σ g(submask)` for all submasks, in O(n × 2^n) instead of O(3^n)
- f.2 — Implementation: iterate each bit position; for each mask with that bit set, add value from mask without bit

**LC anchor:** Niche but appears in advanced bitmask DP

---

## g. Bitmask + DP state [1800]

**Cards (2):**
- g.1 — `dp[mask][k]` patterns: mask = subset assigned, k = some auxiliary count (e.g., k workers assigned so far, but inferable from popcount)
- g.2 — Optimisation: drop redundant dimensions when `popcount(mask)` already captures count

**LC anchor:** *Campus Bikes II* (LC 1066), *Fair Distribution of Cookies* (LC 2305)

---

## h. Complexity bookkeeping [1700]

**Cards (2):**
- h.1 — Time: `O(2^n × transitions per state)` — typically `O(2^n × n)` or `O(2^n × n²)`
- h.2 — At n=16: 2^16 = 65k states, × n=16 = 1M ops — fits easily. At n=20: 2^20 = 1M, × 20 = 20M ops — borderline. At n=25: 33M × 25 = 800M — TLE.

---

## Card count

18 atomic cards across 8 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1699     | — = 0 cards (this topic doesn't open until 1700) |
| 1700-1799     | a (2) + b (3) + c (2) + d (2) + e (3) + h (2) = **14 cards** |
| 1800+         | + f (2) + g (2) = **18 cards (full)** |

## Notes for Socratic drill

- This topic doesn't open until 1700. Don't install bitmask DP cards while drilling 1500-1600 — they're inert until the right problems appear.
- Subtopic `a.1` (the n ≤ 20 cue) is the recognition step. Without it, candidates miss bitmask DP entirely. With it, they spot it instantly from the constraint.
- Subtopic `d.1` (subset enumeration via `s = (s - 1) & mask`) is the most-mind-blowing trick in the whole topic. Cross-referenced with Bit Ops `h.3`.
- Subtopic `h.2` (complexity boundary table) prevents the most common failure mode: trying bitmask DP when n is too big. Lock the boundary: n ≤ 16 safe, n ≤ 20 borderline, n ≥ 25 infeasible.
- Subtopic `f` (SOS DP) is the high-ceiling 1800+ pattern. Only install when 1800 band is active.
