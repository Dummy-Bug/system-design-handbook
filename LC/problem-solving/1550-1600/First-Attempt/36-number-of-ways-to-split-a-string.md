# 36 — Number of Ways to Split a String

- **Link:** https://leetcode.com/problems/number-of-ways-to-split-a-string/
- **Band:** 1550–1600 · Phase 2 sealed queue · ACTIVE-ORDER deal #2 (old numbered #25, added) · Q2
- **Bucket (revealed post-solve):** **Combinatorics — multiplication principle over the 2 boundary gaps** · ✦ Invariant/Reframe (STRONG member). Answer key files it under *DP » Count-ways (Linear)* by AR, but OUR code is pure gap-product counting (no DP table) — credit the mechanic we used: [[lc-credit-mechanic-not-label]], [[lc-classify-by-own-solution]]. Direct cousin of #28 (ways-to-split-array-into-good-subarrays).
- **Dealt:** 2026-06-08
- **AC:** 2026-06-08 _(self-derived, no hint)_
- **Result:** ❌→✓ **WA-then-AC = SOFT FAIL** (derivation clause exempts time, not implementation discipline; rep does NOT count toward ownership).
- **Cold re-solve:** ✅ done 2026-06-08 11:08 IST — correct O(n)/O(1) single-pass form (running boundary-gap product), self-derived.

---

## The problem
Split a binary string into 3 **non-empty** parts so each part has the **same number of `1`s**. Count the ways, mod 1e9+7. `n ≤ 1e5`.

## The derivation (self-led, Socratic debrief)
- Read constraints first: `n ≤ 1e5` → an O(n) / counting insight, not brute enumeration.
- Three cases:
  1. `total ones % 3 != 0` → **0**.
  2. `total ones == 0` → every split is valid → place **2 cuts** among the `n−1` gaps → **C(n−1,2) = (n−1)(n−2)/2**.
  3. else `k = ones/3`; answer = **product of the 2 boundary gaps** — (gap between the k-th and (k+1)-th one) × (gap between the 2k-th and (2k+1)-th one).

## Attempt 1 (WA) — the split-counter bug
Failing test: `100100010100110` (count=6 → `maxOnes=2`), expected ≠ 35.

```java
for (char c : s.toCharArray()){
    if (c == '1') ones += 1;
    if (ones == 0) continue;
    if (ones > maxOnes){ ones = 1; splits = (splits*split)%MOD; split = 1; }
    else { split += 1; }          // BUG: fires for EVERY position where 1 ≤ ones ≤ maxOnes
}
```

**WA-cause [wrong-counting-region]:** `split` accumulated across the *entire* `1 ≤ ones ≤ maxOnes` span — i.e. it counted cut positions *inside* the first group, not just in the trailing zero-gap after the k-th one. Only the gap where exactly `maxOnes` ones sit on the left is a valid cut (`ones == maxOnes`). **Invisible at `maxOnes == 1`** (then the span *is* the single boundary), which is why every hand-trial passed — it only diverges at `maxOnes ≥ 2`, exactly the failing input. The Step-3 edge ritual (a case with ≥2 ones per group) would have caught it pre-submit.

**Latent bug 2 [cast-before-mod]:** the all-zeros branch read `return (int)((n*(n+1))/2) % MOD;` — `(int)` binds before `% MOD`, truncating before the mod. Not triggered by the failing test (it has ones) but a real bug; same family as the cast-first-operand overflow trap. Fixed to `(int)(((n*(n+1))/2) % MOD)`.

## Attempt 2 (AC) — submitted
Fixed by only incrementing `split` when `ones == maxOnes`:

```java
for (char c : s.toCharArray()){
    if (c == '1') ones += 1;
    if (ones == maxOnes) split += 1;
    else if (ones > maxOnes){
        ones = 1;
        splits = (splits * split) % MOD;
        split = 0;
        if (ones == maxOnes) split = 1;
    }
}
return (int) splits;
```

## Canonical (cleanest) form — for the cold re-solve ([[lc-revise-to-cleanest-form]])
Locate the ones, subtract boundary indices directly so the "wrong region" bug is structurally impossible:

```java
public int numWays(String s) {
    int MOD = 1_000_000_007, n = s.length();
    List<Integer> ones = new ArrayList<>();
    for (int i = 0; i < n; i++) if (s.charAt(i) == '1') ones.add(i);
    int total = ones.size();
    if (total % 3 != 0) return 0;
    if (total == 0) return (int)((long)(n - 1) * (n - 2) / 2 % MOD);
    int k = total / 3;
    long way1 = ones.get(k)     - ones.get(k - 1);      // cut-1 gap
    long way2 = ones.get(2 * k) - ones.get(2 * k - 1);  // cut-2 gap
    return (int)(way1 % MOD * (way2 % MOD) % MOD);
}
```

## The cousin link — this vs #28 (the load-bearing lesson)
Both are **one-special-count-per-part ⇒ answer = product of inter-`1` gaps**. The free parameter is **how many cuts you're allowed = (#parts − 1)**:

| | #28 good-subarrays | #36 (this) |
|---|---|---|
| ones per part | exactly **1** | exactly **k = ones/3** |
| number of parts | **any** | **exactly 3** |
| cuts | ones − 1 | **2** |
| free gaps | **all** inter-one gaps | **only the 2** boundary gaps |
| answer | product of **all** gaps | product of **just those 2** gaps |

My WA was literally importing #28's "every gap is free" model into a 3-part problem where only the 2 boundary gaps are free. Same soft-fail family as #28 too (both WA-then-AC on the counting, both ~the same insight).

## Lesson
"Count the ways to partition with a fixed `c` special-elements per part" ⇒ **product of the boundary gaps**, and the number of boundary gaps you multiply = **(#parts − 1)**. Don't count intra-group positions — those are forced. Unbounded parts (#28) → all gaps; fixed parts (#36) → that many minus one.

## Two routes — multiplication vs count-ways DP (the recognition that matters)
A "number of ways to split" problem has **two** possible routes, and which one applies is decided by **independence of the cuts**:
- **Independent choices → multiplication principle (closed form):** **cut-1's location does NOT constrain cut-2's, so total = (choices for cut-1) × (choices for cut-2).** No DP table.
- **Interacting choices → count-ways DP:** if a later cut's validity *depends* on an earlier cut, the product breaks → `dp[i]` = ways up to `i`, summing over valid previous cut points.

**Decision reflex: first ask "are the cuts independent?"** Independent → multiply. Interact → DP.

Here the 2 cuts are independent (each can land anywhere in its own boundary gap, regardless of the other) → product of 2 gaps. The answer key files this under *DP » Count-ways* — that's just the general bucket; multiplication is the sharper tool *because* independence makes it available, and that independence is exactly why it's an Invariant/Reframe member.

## REVISION TARGET (Day+14)
Re-derive cold: the 3 cases, *why* only 2 gaps (parts−1 cuts), and the all-zeros `C(n−1,2)`. Reproduce the cleanest form, not the running-counter one. Re-state the #28-vs-#36 "free parameter = #cuts" contrast from memory.
