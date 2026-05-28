## a. Parity arithmetic rules

The three rules that govern everything else in this topic. They feel obvious written out, but under contest pressure "obvious" becomes a 3-minute derivation if they're not reflex.

**Sum and difference:**

- Even ± even = even
- Odd ± odd = even
- Even ± odd = odd

The same rule applies to subtraction — this trips people up because subtraction feels different, but parity doesn't care about direction. `7 - 3 = 4` (odd - odd = even). `8 - 3 = 5` (even - odd = odd). Identical to addition.

**Product:**

The rule is simpler than addition — one even factor is enough to make the whole product even.

- Any factor even → product even
- All factors odd → product odd

One even number poisons the whole product. This is why 2 is called "the only even prime" — it's the parity disruptor. `3 × 5 × 7 = 105` (odd). `3 × 5 × 6 = 90` (even — one even factor does it).

**Powers:**

Parity of `a^k` = parity of `a`, regardless of k:

- Odd base → result always odd
- Even base → result always even

`3^100` is odd. `4^100` is even. You never need to compute the actual value — just look at the base.

---

## b. Bit-0 as parity reflex

Two ways to check parity in Java:

```java
n % 2 == 1   // mod form
(n & 1) == 1 // bit form
```

`n & 1` is preferred in tight loops — single bitwise AND, no division.

Critical Java trap: `n % 2` can return `-1` for negative integers (Java's mod preserves sign of dividend). So `n % 2 == 1` will be false for odd negative numbers. Safe version is `n % 2 != 0`. But `n & 1` has no such issue — returns 0 for even, 1 for odd, always. Default to `n & 1`.

---

## c. Parity-preserving vs parity-flipping operations

Adding or subtracting an **even** number preserves parity. `n + 4`, `n - 100`, `n + 0` — the parity of `n` is unchanged.

Adding or subtracting an **odd** number flips parity. `n + 3`, `n - 7` — even becomes odd, odd becomes even.

This unlocks a powerful invariant: if a sequence of operations only involves adding even numbers, parity is locked. Any time you see a problem where the operations have fixed parity structure, check if the answer is forced by invariant before doing any computation.

---

## d. "Can target be reached?" parity check

Parity as a **necessary condition for reachability**. Before computing anything, check parity. If it fails, the answer is immediately 0 or "impossible".

The classic form: you have an array of integers and a target sum. Count the odds. If count of odds is even, the sum is even. If count of odds is odd, the sum is odd. If target parity doesn't match — done. No arrangement, permutation, or subset selection changes this.

But passing the parity check doesn't mean the target is reachable. Parity rules out impossible cases; it doesn't confirm possible ones. This is necessary-only, not necessary-and-sufficient. The parity check is a filter, not a solver.

---

## e. Parity of a sum or count

Sum parity equals parity of count of odd elements.

More precisely: in any collection of integers, the sum is even if and only if the number of odd elements is even. The even elements contribute nothing to parity — they're invisible to this analysis. Only count the odds.

`{2, 4, 3, 6, 7}` — two odd elements (3, 7), count is even → sum is even. `2+4+3+6+7 = 22`. Confirmed.

`{2, 4, 3, 6, 7, 9}` — three odd elements, count is odd → sum is odd. `22+9 = 31`. Confirmed.

**e.2 — counting pairs with odd sum.** A sum `x + y` is odd exactly when one of the two is odd and the other even. So to count pairs `(x, y)` drawn from two ranges where `x ∈ [1, n]` and `y ∈ [1, m]`, you don't iterate — you multiply parity-class counts and add both directions:

```
oddCount(n)  × evenCount(m)   ← x odd, y even
+ evenCount(n) × oddCount(m)   ← x even, y odd
```

where `oddCount(k) = ceil(k/2) = (k+1)/2` and `evenCount(k) = floor(k/2) = k/2`.

The reflex is: **"count pairs with odd sum" → parity buckets, not a loop over sums.** The trap is reaching for an O(n+m) loop over every possible odd sum (clamping pair counts per sum) — that works but is 40 minutes of fiddly derivation for a one-liner.

Anchor: *Alice and Bob Playing Flower Game* — Alice wins iff `x + y` is odd, so the answer is exactly this pair count. For `n=9, m=5`: `5×2 + 4×3 = 22`. (It further collapses to `floor(nm/2)` algebraically, but that simplification is problem-specific and not worth memorizing — the parity-bucket product is the reusable move.)

---

## f. XOR as per-bit parity

XOR of bit-i across n numbers = 1 if an odd count of those numbers have bit-i set, 0 if even count.

XOR is parity, applied per bit. This is why XOR appears constantly in problems that ask "how many elements have property X" — when X is a bit condition, XOR accumulates the count's parity automatically.

---

## g. Adjacent-parity grouping

To interleave elements such that no two adjacent elements share the same parity, the counts of evens and odds must be nearly equal.

Valid interleaving exists iff `|count_even - count_odd| ≤ 1`.

If one group outnumbers the other by 2 or more, you'll inevitably have two same-parity elements forced adjacent. The check is on count, not sum — don't let "sum of evens" distract you.

---

## h. Bipartite graphs and parity

A graph is bipartite if and only if it has no odd-length cycle.

The 2-coloring interpretation: assign color 0 or 1 to each node such that every edge connects nodes of different colors. This is possible precisely when every cycle alternates colors — which requires the cycle length to be even. One odd cycle creates a contradiction in the coloring.

Bipartite ⟺ no odd cycle ⟺ consistent 2-coloring exists.

In practice: run BFS/DFS, assign colors, detect contradiction. If you find an edge between two same-color nodes, the graph has an odd cycle and is not bipartite.

---

## Parked cards

**i.1 — Even/odd subset split:** revisit after Pair/Triple Count covers subset enumeration. The result (2^(n-1) even-sum subsets, 2^(n-1) odd-sum subsets) follows from a pairing argument, but installing it cold before the pairing logic is solid would be shallow.

**j.1 — Parity as DP state dimension:** revisit at 1800 band when DP state design is active.
