# 33 — Number of Ways Where Square of Number Equals Product of Two Numbers

- **Link:** https://leetcode.com/problems/number-of-ways-where-square-of-number-is-equal-to-product-of-two-numbers/
- **Band:** 1550–1600 · Phase 2 sealed queue deal #6 · Q2 · AR ~43%
- **Bucket (revealed post-solve):** Hashing (counting) · ✦ Invariant/Reframe (LIGHTER deck member). **NOT Math/NT** — our code uses no number-theory technique (no factorization/divisors/modular/nCr); the `long` cast is overflow hygiene and "square=product" is problem-reading, neither is a Math mechanic. Credit by [[lc-classify-by-own-solution]].
- **Dealt:** 2026-06-02 10:15:09 IST
- **AC:** 2026-06-02 10:39:09 IST
- **Result:** ✅ **CLEAN first-submission AC, ~22 min — SUB-CAP.** Counts toward ownership (Set-B disguised).

## Approach (our code)
Type-1 triplets = `nums1[i]² == nums2[j]*nums2[k]` (j<k), plus the symmetric type-2; total =
`helper(nums1,nums2) + helper(nums2,nums1)`. Per call: build a frequency map of **all pairwise products**
of the second array (`Map<Long,Integer>`, O(n²)), then for each element of the first array look up its
**square** and add the stored count.

```java
public int numTriplets(int[] nums1, int[] nums2) {
    return helper(nums1, nums2) + helper(nums2, nums1);
}
private int helper(int[] a, int[] b) {           // count i with a[i]^2 == b[j]*b[k], j<k
    Map<Long,Integer> map = new HashMap<>();
    int n = b.length;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            map.merge((long)b[i] * b[j], 1, Integer::sum);
    int count = 0;
    for (int x : a) count += map.getOrDefault((long)x * x, 0);
    return count;
}
```

## Key decisions (logged live, pre-code)
- **Scale read:** n ≤ 1e3 → all-pairs = 1e6 products per array → ~4MB map, well under 256MB. O(n²) is fine.
- **Overflow:** nums[i] ≤ 1e5 → product up to 1e10 > int (2.1e9) → **`(long)` cast on both product and square.**
- **Rejected two-pointer-on-sorted:** considered sort + two-pointer for the product, dropped it — duplicate
  handling would *increase* code complexity for no asymptotic win. (Good call: avoided self-inflicted bugs.)

## ✦ Reflex WIN (cross-problem, vs #27/#29/#32)
Used `Map<Long,Integer>` = a **count** map (product → #pairs), NOT `Map<_,Deque<index>>` storing positions.
This is the counter-heuristic from [[lc-index-bookkeeping-overmodel]] firing **one problem later**: asked
"count or positions?" and chose count. Reflex self-correcting, not just named.

## Perturbation probes
- **Operator / objective (`==` square → count):** load-bearing = we need *how many pairs hit a product*, not
  *which* pairs → a frequency count suffices (no index storage). Perturb to "return the pairs themselves" ⇒
  you'd need lists, not counts — and the problem would get genuinely harder. The count is the gift.
- **Scale (n=1e3, val=1e5):** n=1e3 is the spoiler that O(n²) all-pairs is *intended* (1e6 ops, trivial);
  val=1e5 is the spoiler that products overflow int → **long is mandatory, not optional.** Both bounds are
  calibrated, not decorative. Push n→1e5 and all-pairs dies (1e10) → you'd need a divisor/factor-counting
  approach instead. The small n is what *permits* the brute-pair frame.
- **Meta (one sentence):** "for each candidate square, how many unordered pairs of the other array multiply
  to it" — once said, the frequency-map falls out immediately.

### Scale axis worked out — the n ≤ 1e5 version (self-derived 2026-06-02, NT route)
At n ≤ 1e3 all-pairs O(n²)=1e6 is licensed → pure hashing, no math. Push to **n ≤ 1e5** and all-pairs = 1e10 dies;
the problem **forces number theory**. Derived approach:
1. Build `freq` map of `nums2` values.
2. For each `num` in `nums1`, target `S = num²`. **Do NOT factor S directly** — √S = √(num²) = num → O(n²) again
   (wall #1 hit & fixed). Instead **factor `num` in √num**, then **double every prime exponent** → factorization
   of `S` for free. (`6 = 2¹·3¹` → `36 = 2²·3²`.)
3. **Enumerate ALL divisors of S** by sweeping the exponent grid `∏ pᵢ^{0..2eᵢ}` — NOT by squaring num's divisors.
   (Wall #2: the `f1²·f2²` shortcut yields only the *square* divisors `{1,4,9,36}`, **misses `(2,18)`,`(3,12)`** of 36.)
4. For each divisor `d ≤ √S`: pair `(d, S/d)`. If `d == S/d` (i.e. `d == num`) add `C(freq[d],2)`; else add
   `freq[d]·freq[S/d]`. Count each unordered pair once.
- Cost ≈ O(n · (√num + #divisors)) — well under 1e10. **The constraint alone (1e3 vs 1e5) decides hashing vs
  factorization** — clearest demonstration of "constraints pick the method."


## Lesson
Clean, fast, correct because the constraints were read **before** coding (Step-analysis paid off) and the
structure was chosen by role ("count" not "positions"). Model rep for the over-model fix. Counts toward
**Hashing (counting)** first clean rep ONLY — no Math/NT mechanic was used.

## Secondary approach — NT divisor-enumeration (the n≤1e5 method, coded on the n≤1000 judge)
- **AC:** 2026-06-02 14:31:57 IST (submitted on LC 1577; passes since the method is correct, though n≤1000 doesn't require it).
- **Classification — HARD FAIL for Math/NT.** Heavily guided: the sieve overflow, prime-factorization-with-
  exponents (+leftover prime), the *factor-n-double-exponents* trick, and the divisor-enumeration grid loop
  (with the `sz` freeze) were all taught essentially line-by-line. **Does NOT count toward ownership** — it's a
  hard-fail *acquisition* of the divisor-enumeration / factorization primitives, not a derived solve.
- **Same problem as the clean rep**, just a second approach → adds **no distinct-problem rep** (clean or fail).
- **Hashing rep is unaffected:** the original first-AC (frequency-map of products, 22m sub-cap) remains the
  **clean Hashing rep**. This NT detour does not touch it.
- **Primitives acquired (hard-fail, drill to reflex):** Sieve of Eratosthenes (§3.7), prime factorization w/
  exponents (§3.8), divisor enumeration + n²-doubling (§4.12). See [[lc-derivation-budget-chunking]] — the
  problem felt ~1800 because all five had to be derived at once; each is individually a ~1400 brick.
- Final code (sieve + factorize + double-exponents + grid enumerate + pair-count) lives in this file's history /
  the session; canonical reference for the technique = syllabus §4.12.

## REVISION TARGET (Day+14)
Re-derive directly: the type-1+type-2 split, the frequency-map-of-products, the long cast. Re-answer the 3
probes from memory (esp. *why long is forced* and *why n=1e3 permits all-pairs*).
