# Math Improvement Plan — DEFERRED

**Status:** Parked. Pick up when contest rating crosses **~1700** or when math-derivation problems start blocking contest performance consistently.

**Why deferred:** Pure-math derivation problems are rare in real interviews (Google L4 / SDE-2 design + algo rounds). They show up occasionally in contest Q2/Q3 but the bulk of the rating climb to 1700 is pattern-based (DP, graph, two pointers, monotonic stack, etc.). Math problems require a separate, significant time investment that doesn't pay off until later bands. Skip for now.

**Trigger to resume:**
- Contest rating ≥ 1700 OR
- 3+ consecutive contests where the blocker on Q2/Q3 is math derivation (not pattern recognition) OR
- Targeting FAANG L5/SDE-3+ where math-heavy problems become more common

---

## Where the actual gap is

From the **Count Distinct Perfect Pairs** session (LC 1715, 2026-05-18) — got stuck for 30 min on opening `|a-b|`, combining inequalities, and reducing two abs-value conditions to `y ≤ 2x`. The missing muscles, in order:

1. **Mechanical opening of `|x|`** — splitting on `sign(x)` cleanly, not on what feels intuitive
2. **Combining inequalities** — when you add/subtract two inequalities, the direction rules
3. **Noticing trivial constraints** — recognizing when `a ≥ 0` falls out of a chain and the inequality is satisfied for free
4. **WLOG framing** — "assume x ≤ y without loss of generality" to cut case count in half
5. **Symmetry pruning** — when four sign cases reduce to one by symmetry

These are *techniques*, not knowledge. They drill in.

---

## Reframe — this is NOT Google-level math

What tripped today is high school algebra. Google L4 problems essentially never need anything beyond:

- Absolute value + case analysis
- Linear/quadratic inequalities (AM-GM at the high end)
- Modular arithmetic basics
- Counting / combinatorics basics (nCr, inclusion-exclusion)
- Bit manipulation math (XOR properties)
- Expected value / probability basics

No olympiad geometry, no real analysis, no advanced number theory. It feels like a wall because most engineers skip this layer — the day job never asks for it. Fixable gap, not a ceiling.

---

## The plan (when resumed)

### Foundation rebuild — ~8-12 weeks, 20 min/day

| Resource | Why | Time |
|---|---|---|
| **AoPS Intro to Algebra** — chapters on Absolute Value, Inequalities, Special Factorizations | Gold standard. Teaches contest-style algebra from scratch. Designed for ~13-year-olds doing AMC, perfectly paced for adults | ~6 weeks, 20 min/day |
| **CP-Algorithms** (cp-algorithms.com) — Algebra section + Number Theory basics | Free, CS-flavored, no fluff. GCD, modular inverse, sieve, fast exponentiation | ~2 weeks |
| **USACO Guide — Silver/Gold Math** | Curated math problems with editorial reasoning | Ongoing |

Backup option (no textbook): **Khan Academy Algebra II + Precalculus** — same ground, free, slower payoff.

### Application drilling — parallel, ~2 problems/week

LC filter: `math` tag, rating 1500-1800. Pick ones with an inequality or counting derivation step:

- 781. Rabbits in Forest
- 829. Consecutive Numbers Sum
- 858. Mirror Reflection
- 866. Prime Palindrome
- 891. Sum of Subsequence Widths
- 902. Numbers At Most N Given Digit Set
- 940. Distinct Subsequences II
- 1015. Smallest Integer Divisible by K

Codeforces math tag is purer than LC — start at rating 1400-1600, work up.

### The specific drill for the abs-value / inequality gap

Take 20 problems of the form "find all (a,b) such that some inequality holds." For each:

1. Write out every sign case explicitly
2. Open every absolute value mechanically
3. After simplifying each case, check: did it reduce to the same condition? (it usually does — that's the WLOG insight)

**Do this on paper, not in your head.** The whole point is to build the mechanical habit you don't have yet.

---

## Time budget when resumed

- **Replace 1 zerotrac problem/week** with a math-tagged LC problem — same 30-min cap, same protocol
- **Weekend (Sat morning, 45 min):** one chapter of AoPS + exercises
- **Track:** add `math-log.md` to LC folder, log every math-derivation problem separately to measure the curve

Total: ~3 hours/week. Expected visible improvement in ~6 weeks, gap closed in ~6 months.

---

## What "Google level" actually requires

- **L4 / SDE-2:** solid command of the 6 areas listed above + ability to derive inequalities on the fly. The Perfect Pairs problem was exactly at that bar
- **L5 / SDE-3+:** same math, applied to harder problem framings. Math itself doesn't get harder
- **Google Research / TPM-quant:** different track — actual undergrad math (linear algebra, probability, optimization). Not the current target

---

## Sessions that exposed math gaps (log future ones here)

| Date | Problem | Rating | Gap |
|------|---------|--------|-----|
| 2026-05-18 | LC — Count Distinct Perfect Pairs | 1715 | Opening abs values, combining inequalities, WLOG reduction |
