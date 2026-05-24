# Pair / Triple Count [1100]

Counting pairs `(i, j)` with `i < j` and some property — and the natural extension to triplets `(i, j, k)` with `i < j < k`. This is the most-frequent counting primitive on LC. It appears as the *entire problem* at low bands and as a *sub-step* inside harder problems at higher bands.

The naive O(n²) or O(n³) brute force is rarely the intended solution past Band 1400. The actual reflex needed is reframing — "fix-the-middle", "contribution per element", "hashmap-of-complement", or "sort + two pointers" — each turns the count into O(n log n) or O(n).

Caps in standalone usefulness around Band 1800. Past that, pair/triple counting fuses with monotonic stack (contribution), segment tree (range pair queries), or generating functions (combinatorial counts).

## Empirical frequency

| Band | PAIR_COUNT | TRIPLE_COUNT | Total |
|------|-----------|--------------|-------|
| 1100-1399 | 28 (under PAIR_TRIP legacy tag, 9.8% of math) | combined | 28 |
| 1400-1499 | 6 | 2 | 8 |
| 1500-1599 | 6 | 6 | 12 |
| 1600-1699 | 8 | 2 | 10 |
| 1700-1799 | 5 | 2 | 7 |
| 1800-1899 | 4 | 2 | 6 |
| 1900+ | 0 | 0 | 0 |

**Total: ~71 problems** where pair or triple counting is the binding math step. Spread evenly across 1100-1800.

## Subtopic structure

Each subtopic is rated `[required-from XXXX]`. Card titles only. Content unpacked via Socratic drill on install.

---

## a. Pair count formula [1100]

**Cards (4):**
- a.1 — Formula for unordered pairs from n elements
- a.2 — Concrete drill: n=10, n=20, n=100
- a.3 — Cast-to-long reflex for n ≥ ~46000
- a.4 — Inverse: given pair count, recover n

---

## b. Triplet count formula [1200]

**Depends on:** Pair count [1100]

**Cards (3):**
- b.1 — Formula for unordered triples from n elements
- b.2 — Concrete drill: n=10, n=20, n=100
- b.3 — Cast-to-long reflex

---

## c. Within-group pair sum (bucket pairs) [1300]

**Cards (1):**
- c.1 — Total pairs when items are grouped into buckets of sizes `[g₁, g₂, …]`

**LC anchor:** *Number of Good Pairs* (LC 1512), *Count Number of Bad Pairs* (LC 2364)

---

## d. Delta vs cumulative when iterating [1400]

The recurring bug class — adding `C(k,2)` when you meant `k-1`, or vice versa.

**Cards (2):**
- d.1 — At the k-th arrival of an element, NEW pairs added = `k-1`
- d.2 — At the k-th arrival, CUMULATIVE total pairs = `k(k-1)/2`

**LC anchor:** *Caesar Cipher Pairs* (LC 3146) — the 20-min derivation problem

---

## e. Counting pairs via complement hashmap [1400]

**Cards (2):**
- e.1 — "Pairs with sum = target" → hashmap of `target - a[i]`
- e.2 — "Pairs with diff = k" → hashmap, lookup both `a[i] + k` and `a[i] - k`

**LC anchor:** *Two Sum* (LC 1), *Count Pairs With Absolute Difference K* (LC 2006)

---

## f. Sorted two-pointer for pairs [1500]

**Cards (1):**
- f.1 — Sorted array + two pointers converging to count pairs in O(n)

**LC anchor:** *Two Sum II* (LC 167), *Count Pairs Sum Less Than K*

---

## g. Fix-the-middle for triplets [1500]

**Cards (2):**
- g.1 — Fix `j`, count valid `i < j` on the left and valid `k > j` on the right; answer = `Σ left[j] × right[j]`
- g.2 — Prefix/suffix arrays as the standard implementation

**LC anchor:** *Special Triplets* (LC 3265 — your 1500-1550 #2)

---

## h. Counting pairs by sorting + index relation [1600]

**Cards (1):**
- h.1 — "Pairs (i,j) with `a[i] + a[j] < threshold` while preserving an index constraint"

**LC anchor:** *Count the Number of Fair Pairs* (LC 2563)

---

## i. Counting inversions [1600]

**Depends on:** *Merge sort* algorithmic prereq (outside math syllabus)

**Cards (2):**
- i.1 — Inversion = pair `(i, j)` with `i < j` and `a[i] > a[j]`
- i.2 — Counted in O(n log n) via merge sort (or Fenwick tree)

---

## j. Contribution technique (per-element pair contribution) [1700]

The reframing that unlocks 1700+ pair-sum problems: instead of iterating all pairs, ask "how many pairs does element `a[i]` appear in, multiplied by its contribution".

**Depends on:** Sum of products identity → Arithmetic Sums i.1 [1600]

**Cards (2):**
- j.1 — `Σ_{i<j} (a_i + a_j) = (n-1) × Σ a_i` — direct identity
- j.2 — General contribution form: "fix an element, count how many pairs include it as the role-X member, multiply"

**LC anchor:** *Sum of Subarray Ranges* (LC 2104), *Sum of Subarray Minimums* (LC 907)

---

## k. Range-pair counting under index constraint [1700]

**Cards (1):**
- k.1 — Pairs `(i, j)` where `j - i ≤ k` and some value condition holds — sliding window + freq map

---

## l. Counting triples by fix-middle + algebraic reframe [1800]

**Depends on:** Fix-the-middle [1500], Algebraic rearrangement (cross-topic, future)

**Cards (1):**
- l.1 — `a[i] + a[k] = 2 × a[j]` (arithmetic-mean triples) → fix `j`, count via hashmap

**LC anchor:** *Number of Arithmetic Triplets* (LC 2367 — easier variant)

---

## Card count

22 atomic cards across 12 subtopics.

| Target rating | Required cards (cumulative) |
|---------------|------------------------------|
| 1100-1199     | a (4) = **4 cards** |
| 1200-1299     | + b (3) = **7 cards** |
| 1300-1399     | + c (1) = **8 cards** |
| 1400-1499     | + d (2) + e (2) = **12 cards** |
| 1500-1599     | + f (1) + g (2) = **15 cards** |
| 1600-1699     | + h (1) + i (2) = **18 cards** |
| 1700-1799     | + j (2) + k (1) = **21 cards** |
| 1800+         | + l (1) = **22 cards (full)** |

## Notes for Socratic drill

- Subtopic `d` (delta vs cumulative) is the *exact* failure mode from Caesar Cipher Pairs. Two atomic cards. Once installed, that 20-minute leak closes permanently.
- Subtopic `a` is foundational — every other subtopic in this topic builds on it. Graduate `a` first.
- Subtopic `j` (contribution) is the bridge between counting and monotonic stack — it's the reframe that unlocks ~half of 1700+ pair-sum problems. High-value install once it becomes mandatory.
- Subtopics `e`, `f`, `g` are three different *implementation patterns* for the same conceptual problem (count pairs / triplets). Install them as alternatives, not redundancies — knowing which to reach for is the actual skill.
