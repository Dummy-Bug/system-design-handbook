# Stars & Bars Identities [1300]

The "distribute n identical items into k distinct boxes" family of counting identities. Solves problems that would otherwise require recursive enumeration in a single `C(...)` formula.

Looks small on the frequency table (1-3% per band) but appears in *exactly* the problems where candidates burn time enumerating — Q2 / easy Q3 problems where the formula is the only way to fit time limits. High-leverage despite low count.

## Empirical frequency

| Band | STARS_BARS-tagged | % of math |
|------|-------------------|-----------|
| 1100-1399 | tail (inside PERM_COMB) | — |
| 1400-1499 | tail | — |
| 1500-1599 | 1 | 1.3% |
| 1600-1699 | tail | — |
| 1700-1799 | 2 | 2.8% |
| 1800-1899 | tail | — |
| 1900+ | tail | — |

**Total: ~10 problems where stars & bars is the binding step.** Low count, but high-impact when it appears — typically gates a Q2 or Q3.

## Why this is a separate topic from Perm/Comb (#10)

The basic distribution form (`C(n + k - 1, k - 1)`) lives in Perm/Comb f.1. This topic covers the **bounded** variants and the inclusion-exclusion overlay that turns stars & bars from a 1-line formula into a Q3-tier identification.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Basic stars & bars [1300]

**Cards (2):**
- a.1 — Distribute n identical items into k distinct boxes, no restriction: `C(n + k - 1, k - 1)`
- a.2 — Equivalent: number of non-negative integer solutions to `x₁ + x₂ + ... + xₖ = n` is `C(n + k - 1, k - 1)`

**LC anchor:** *Count Sorted Vowel Strings* (LC 1641 — 5 boxes, total n)

**Note:** Same as Perm/Comb f.1 — cross-referenced. Install once.

---

## b. Stars & bars with positive constraint [1400]

**Cards (1):**
- b.1 — Each box must have ≥ 1 item: substitute `yᵢ = xᵢ - 1`, reduces to `C(n - 1, k - 1)`

---

## c. Stars & bars with upper bound on one variable [1500]

**Cards (1):**
- c.1 — One variable bounded `xᵢ ≤ U`: count total via `C(n + k - 1, k - 1)`, subtract count where `xᵢ ≥ U + 1` via substitution

---

## d. Stars & bars with bounds on ALL variables (inclusion-exclusion) [1700]

**Cards (3):**
- d.1 — Each `xᵢ ≤ Uᵢ`: apply inclusion-exclusion over "subset of vars exceeding bound"
- d.2 — Formula: `Σ_{S ⊆ vars} (-1)^|S| × C(n - Σ(Uᵢ + 1 for i in S) + k - 1, k - 1)` (zero out terms where argument < 0)
- d.3 — When k ≤ 3 (most LC problems), this collapses to ≤ 8 terms — feasible by hand

**LC anchor:** *Distribute Candies Among Children II* (LC 2929 — k=3 with bounds)

---

## e. Lattice paths / monotonic grid walks [1600]

**Cards (2):**
- e.1 — Number of paths from `(0, 0)` to `(m, n)` using only right/up steps: `C(m + n, m)`
- e.2 — With forbidden cells / obstacles: subtract paths-through-obstacle via complementary counting

---

## f. Counting with at-most-k constraint [1700]

**Cards (1):**
- f.1 — "Count of n-tuples with sum ≤ K": add a slack variable `xₖ₊₁` and reduce to equality form

---

## g. Multiset / repetition counting [1700]

**Cards (1):**
- g.1 — "Number of ways to write n as an ordered sum of k positive integers" = `C(n-1, k-1)` (compositions of n into k parts)

---

## Card count

11 atomic cards across 7 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | — = 0 cards |
| 1200-1299     | — = 0 cards |
| 1300-1399     | a (2) = **2 cards** |
| 1400-1499     | + b (1) = **3 cards** |
| 1500-1599     | + c (1) = **4 cards** |
| 1600-1699     | + e (2) = **6 cards** |
| 1700-1799     | + d (3) + f (1) + g (1) = **11 cards (full)** |

## Notes for Socratic drill

- Subtopic `a` (basic stars & bars) is the cornerstone — same install as Perm/Comb `f`. Cross-reference, don't duplicate.
- Subtopic `d` (bounds on all variables via I-E) is the 1700+ trick that makes *Distribute Candies II* solvable in O(1) per query. Without it, the problem requires DP. The I-E formula is mechanical once `d.2` is locked.
- Subtopic `e` (lattice paths) is the geometric form — same identity, dressed up as a grid problem. Recognise the equivalence and the problem collapses.
- The whole topic is small (11 cards) but every card is high-leverage when it appears — these are the "I would never have seen this without the install" tricks.
