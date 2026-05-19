# Bitmask Improvement Plan — DEFERRED

**Status:** Parked. Pick up when zerotrac band reaches **~1900-2000** (estimated ~July-August 2026 at current pace).

**Why deferred:** Bitmask DP appears with non-trivial frequency only from 1900+ rated problems (1-in-7 at 1900-2100, 1-in-4 at 2100-2300). At the current 1800-1900 band, it shows up 1-in-15 problems and almost always in the simpler "subset enumeration + per-subset check" shape — which has already been internalised once via Even Sum Subgraphs (LC, 1859, 2026-05-19). Doing a dedicated drilling campaign now is premature. The binding constraint right now is Q3 derivation across general patterns, not bitmask fluency specifically.

**Trigger to resume:**
- Active zerotrac band reaches **1900-2000** OR
- 3+ consecutive band problems blocked specifically because bitmask DP wasn't recognised OR
- Virtual contest Q3 stays unsolved because of an unrecognised bitmask DP shape

---

## Where the actual gap is

From the **Even Sum Subgraphs** session (LC, 1859, 2026-05-19) — the *recognition* and *enumeration* part were done correctly without help. Constraint reading (`n ≤ 13`) drove the choice naturally, and the subset-iteration mental model is now solid. The missing muscles are at the *next layer*:

1. **Bitmask DP — using a subset as a DP key.** The leap from "enumerate subsets and check each" to "`dp[mask] = optimal value for solving the subset mask`" is a separate cognitive step that hasn't been trained.
2. **The "state = (current position, visited bitmask)" pattern** — TSP-shape problems where bitmask handles the *set* of visited cities and a separate variable handles the *order tail*.
3. **Submask enumeration idiom** — `for (int sub = mask; sub > 0; sub = (sub - 1) & mask)`. Used for "partition mask into pieces" and "iterate all subsets of a subset." Comes up at 2100+.
4. **Composition with other algorithms** — bitmask is rarely the whole solution at higher ratings; it's usually one component (e.g., bitmask + Dijkstra in LC 847). The composition skill is what separates 1900-band candidates from 2200-band ones.

These are not knowledge gaps. They drill in.

---

## Frequency table — what to expect by rating band

| Band | Bitmask frequency | Shape |
|---|---|---|
| 1500-1700 | Rare (1-in-30) | Pure subset enumeration, trivial |
| 1700-1900 | Occasional (1-in-15) | Subset enum + per-subset check (the Even Sum Subgraphs shape) |
| **1900-2100** | **Common (1-in-7)** | Bitmask DP appears (TSP-shape, partition, assignment) |
| 2100-2300 | Frequent (1-in-4) | Bitmask DP is standard, often composed with another technique |
| 2300+ | Dominant (1-in-2) | One of the 5-6 hard templates, often with submask enumeration |

**Contest mapping:**
- Q1 / Q2: never bitmask
- Q3 (current contest bottleneck): bitmask appears ~1-in-4 contests
- Q4: bitmask appears ~1-in-2 contests

---

## The plan (when resumed)

### The ladder — 8 problems, ~3 weeks at 1/week

**Tier 1 — Pure subset enumeration (warm-up):**
1. **LC 78 — Subsets** — generate all subsets. Cleanest `1 << n` loop, no filtering.
2. **LC 2044 — Count Number of Maximum Bitwise-OR Subsets** — subset → property computation.

**Tier 2 — Subset enumeration + check (already covered via Even Sum Subgraphs):**
3. **LC 2305 — Fair Distribution of Cookies** — bitmask DP entry point. `dp[mask] = min max load`.
4. **LC 1986 — Minimum Number of Work Sessions to Finish the Tasks** — n ≤ 14, state combining.

**Tier 3 — Bitmask DP (TSP family — the gateway, drill twice):**
5. **LC 847 — Shortest Path Visiting All Nodes** — canonical `(current_node, visited_bitmask)`. Template for an entire family.
6. **LC 943 — Find the Shortest Superstring** — same shape as 847 with pairwise overlap precomputation.

**Tier 4 — Submask enumeration (advanced):**
7. **LC 1494 — Parallel Courses II** — `for (int sub = mask; sub > 0; sub = (sub - 1) & mask)` idiom.
8. **LC 698 — Partition to K Equal Sum Subsets** — bitmask of used items, partition-shape problem.

### Application protocol

- One bitmask problem **per week**, slotted in alongside the current zerotrac band
- Log each in the current band file with what bit op idiom was newly learned
- By problem 8, build a personal cheat sheet of recognised shapes
- LC 847 is the critical template — solve it twice (once for derivation, once for execution speed)

### The recognition drill

Before coding any bitmask problem, **force yourself to write one sentence**:
> "What is one state? What is the universe of items?"

If the answer is "the subset `{a, b, c}` of the original input items, where `n ≤ 20`" — bitmask.

This is the meta-skill. The 8 problems above are vehicles for building this reflex; the reflex itself is what matters.

---

## Bitmask cheat sheet (already internalised — keep for reference)

| Operation | Code |
|---|---|
| Test bit `i` | `(mask >> i) & 1` or `(mask & (1 << i)) != 0` |
| Set bit `i` | `mask \| (1 << i)` |
| Clear bit `i` | `mask & ~(1 << i)` |
| Toggle bit `i` | `mask ^ (1 << i)` |
| Clear lowest 1 | `mask & (mask - 1)` |
| Isolate lowest 1 | `mask & -mask` |
| Lowest 1 position | `Integer.numberOfTrailingZeros(mask)` |
| Popcount | `Integer.bitCount(mask)` |
| Empty subset | `0` |
| Full subset | `(1 << n) - 1` |
| Iterate all subsets | `for (int mask = 0; mask < (1 << n); mask++)` |
| Iterate set bits | `while (m != 0) { int b = Integer.numberOfTrailingZeros(m); ...; m &= m - 1; }` |
| Iterate submasks of `mask` | `for (int sub = mask; sub > 0; sub = (sub - 1) & mask)` |

---

## Litmus test for when bitmask applies

1. **State = subset of a small, fixed universe of N items** (where universe doesn't grow during execution)
2. **N ≤ 20-22** (for plain enumeration), **N ≤ 18-20** (for bitmask DP with `2^n × n` work)
3. **Order doesn't matter** — if it does, need `(position, mask)` combined state
4. **Inner work per subset fits in budget** — do the multiplication before coding

**Anti-patterns (bitmask doesn't apply):**
- `n > 25` — state space too large
- "New items appear during execution" (e.g., midpoint generation in Minimum Generations problem) — bitmask over original `n` can't capture them
- Sequence / permutation problems where order is part of the state
- Multiset problems with counts (need a different encoding)

---

## Time budget when resumed

- **Replace 1 zerotrac problem/week** with one from the bitmask ladder — same 30-min cap, same protocol
- **8 problems = ~2 months of weekly cadence** (paced 1/week to spread out the recognition reps)
- **Track:** log each in the active band file with the bit op idiom learned
- **Expected outcome:** by problem 8, bitmask DP is a recognised shape on first read, and execution is mechanical

Total commitment: ~1 problem/week × 8 weeks = trivial overhead, big payoff at 2000+ band.

---

## Sessions that exposed bitmask gaps (log future ones here)

| Date | Problem | Rating | Gap | Outcome |
|------|---------|--------|-----|---------|
| 2026-05-19 | LC — Even Sum Subgraphs | 1859 | None — recognition correct, brute force AC'd. Bitmask taught after as alternative. | AC at 46min, bitmask exposure recorded |
