# Bit Operations [1100]

Manipulating individual bits of an integer — set, unset, toggle, query, count. The non-XOR side of bitwise reasoning (XOR is split into its own topic #8 because its identity-based reasoning is structurally distinct).

Stays consistently 12-15% of math across **every band from 1100 to 1800**. Unlike geometry (peaks at 1700) or mod arithmetic (peaks at 1800), bit ops are a flat anchor — you'll see them at every rating.

## Empirical frequency

| Band | BIT_OPS-tagged | % of math |
|------|---------------|-----------|
| 1100-1399 | 40 (under BIT_XOR legacy, includes XOR) | 14% |
| 1400-1499 | — | 7% |
| 1500-1599 | 10 | 12.8% |
| 1600-1699 | 10 | 15.4% |
| 1700-1799 | 10 | 14.1% |
| 1800-1899 | 9 | 11.5% |
| 1900+ | tail | — |

**Total: ~70+ problems** if you count the 1100 BIT_XOR pool. Universal anchor topic.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Bit indexing — read [1100]

**Cards (2):**
- a.1 — Check if bit i is set: `(n >> i) & 1` or `(n & (1 << i)) != 0`
- a.2 — Bit numbering convention: bit 0 = LSB (rightmost)

---

## b. Bit indexing — write [1100]

**Cards (3):**
- b.1 — Set bit i: `n |= (1 << i)`
- b.2 — Unset bit i: `n &= ~(1 << i)`
- b.3 — Toggle bit i: `n ^= (1 << i)`

---

## c. Popcount — count of set bits [1100]

**Cards (2):**
- c.1 — Java built-in: `Integer.bitCount(n)` for int, `Long.bitCount(n)` for long
- c.2 — Manual loop: `while (n != 0) { count++; n &= (n - 1); }` (Brian Kernighan trick)

**LC anchor:** *Sum of Values at Indices With K Set Bits* (LC 2859)

---

## d. Powers of 2 reflex [1100]

**Cards (3):**
- d.1 — `2^10 = 1024 ≈ 10³`, so `2^20 ≈ 10⁶`, `2^30 ≈ 10⁹`
- d.2 — `1 << 30` fits in int (max int ≈ 2.1 × 10⁹), `1 << 31` overflows — use `1L << 31` for long
- d.3 — Power of 2 check: `n > 0 && (n & (n - 1)) == 0`

**Depends on:** Digit Operations → powers of 10 reflex [1400] (parallel concept)

**LC anchor:** *Power of Two* (LC 231)

---

## e. Bitwise operators table [1200]

**Cards (4):**
- e.1 — AND `&`: `1 & 1 = 1`, else 0. Used as filter.
- e.2 — OR `|`: `0 | 0 = 0`, else 1. Used as merge.
- e.3 — NOT `~`: flips all bits. `~0 = -1` in Java (two's complement)
- e.4 — Left shift `<<` multiplies by 2, right shift `>>` divides by 2 (sign-preserving). Use `>>>` for unsigned right shift.

---

## f. Bit-manipulation idioms [1300]

**Cards (4):**
- f.1 — Lowest set bit isolated: `n & (-n)` (returns the bit, not the index)
- f.2 — Clear lowest set bit: `n & (n - 1)`
- f.3 — Check if n is power of 2: `n > 0 && (n & (n - 1)) == 0`
- f.4 — Index of lowest set bit: `Integer.numberOfTrailingZeros(n)` (returns 32 if n == 0)

---

## g. Iterate set bits [1400]

**Cards (1):**
- g.1 — Iterate just the set bits: `for (int m = n; m != 0; m &= (m - 1)) { int bit = m & (-m); ... }`

---

## h. Binary representation as state [1500]

**Cards (3):**
- h.1 — Set of size ≤ 32 (or 64) can be represented as a single int/long mask
- h.2 — Union, intersection, difference of sets via `|`, `&`, `~ ... &`
- h.3 — Subset enumeration: `for (int s = mask; s > 0; s = (s - 1) & mask) { ... }` iterates all non-empty subsets of `mask`

**LC anchor:** *Maximum Strength of a Group* (LC 2708)

---

## i. Bit-by-bit greedy [1500]

**Cards (2):**
- i.1 — When max/min answer involves choosing bits, decide bit-by-bit from MSB downward — greedy works because higher bits dominate
- i.2 — "Maximise XOR / OR with constraint" → walk bits from high to low, commit each bit if possible

**LC anchor:** *Minimize XOR* (LC 2429), *Max XOR After Operations* (LC 2317)

---

## j. AND / OR aggregation over array [1600]

**Cards (2):**
- j.1 — AND of subarray is monotonically non-increasing as the subarray extends (AND only clears bits, never sets)
- j.2 — OR of subarray is monotonically non-decreasing — OR only sets bits

**LC anchor:** *Longest Nice Subarray* (LC 2401), *Find OR Value of Subarray* (LC 3080)

---

## k. Bitmask state in DP [1700]

**Note:** Full bitmask DP gets its own topic (#14). This subtopic is just the identification step.

**Cards (1):**
- k.1 — Recognise "n ≤ 16-20 elements, track subset of used" pattern as the cue for `dp[mask]` formulation

**Depends on:** Bitmask DP topic [1700]

---

## l. Bit-level invariants [1800]

**Cards (2):**
- l.1 — XOR-AND-OR algebraic identities (e.g., `a + b = (a ^ b) + 2 × (a & b)`)
- l.2 — Trie over bits for max-XOR / min-AND queries on a stream (identification only; trie impl outside this topic)

**LC anchor:** *Sum of Two Integers* (LC 371), *Maximum XOR of Two Numbers in Array* (LC 421)

---

## Card count

29 atomic cards across 12 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (2) + b (3) + c (2) + d (3) = **10 cards** |
| 1200-1299     | + e (4) = **14 cards** |
| 1300-1399     | + f (4) = **18 cards** |
| 1400-1499     | + g (1) = **19 cards** |
| 1500-1599     | + h (3) + i (2) = **24 cards** |
| 1600-1699     | + j (2) = **26 cards** |
| 1700-1799     | + k (1) = **27 cards** |
| 1800+         | + l (2) = **29 cards (full)** |

## Notes for Socratic drill

- Subtopic `a`-`d` is the biggest 1100 install in the whole syllabus (10 cards). Big install but unlocks ~14% of every band. High ROI.
- Subtopic `d.2` (overflow on `1 << 31`) ties to the Java-impl checklist. Pair install with conversions reference.
- Subtopic `f` (the four idioms) is where most candidates fumble — they remember the words "Kernighan" / "trailing zeros" but blank on the exact expression. Install these as direct code patterns, not as named tricks.
- Subtopic `h.3` (subset enumeration via `s = (s - 1) & mask`) is the single most-mind-blowing trick in this whole topic — install it cold and you'll spot it instantly in bitmask DP problems.
- Subtopic `j` (AND/OR monotonicity) unlocks sliding-window solutions to several 1600+ problems. The monotonicity is the insight; sliding window is just the consequence.
