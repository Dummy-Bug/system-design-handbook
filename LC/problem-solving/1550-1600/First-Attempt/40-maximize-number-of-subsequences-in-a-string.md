# 40 — Maximize Number of Subsequences in a String

- **Link:** https://leetcode.com/problems/maximize-number-of-subsequences-in-a-string/
- **Band:** 1550–1600 · Phase 2 sealed queue · ACTIVE-ORDER deal (old numbered #15) · Q2
- **Bucket (revealed post-solve):** **Greedy + Combinatorics** (running count of `pattern[0]`; best single insertion is `p0` at front or `p1` at end) · ✦ Invariant/Reframe (STRONG member). Both mechanic buckets already OWNED ● — credit the mechanic in OUR code ([[lc-credit-mechanic-not-label]]); this counts as a **reframe-muscle rep** (no clean-rep gate), not a bucket rep.
- **Dealt:** 2026-06-09 (walk-think)
- **AC:** 2026-06-09 _(hinted — Claude pointed at the `pattern[0]==pattern[1]` case after WA)_
- **Result:** ❌→✓ **WA-then-AC + hinted = SOFT FAIL** ("softest fail ever" per user — fix was a clean self-derived combinatorics branch, but first submission was WA *and* a hint was given → does NOT count toward ownership).
- **Cold re-solve:** ⏳ pending.

---

## The problem
Add **exactly one** character (either `pattern[0]` or `pattern[1]`) anywhere in `text` to **maximize** the number of times `pattern` (length 2) appears as a **subsequence**. Return that max count. `pattern` chars may be equal.

## The derivation (the reframe)
- A `pattern` subsequence = a `p0` somewhere before a `p1`.
- Inserting `p0` only ever helps when placed at the **very front** (then it pairs with *every* later `p1`) → gain = `count(p1)`.
- Inserting `p1` only ever helps at the **very end** (pairs with *every* earlier `p0`) → gain = `count(p0)`.
- So answer = `base + max(count(p0), count(p1))`, computed in one pass while accumulating the running base count.

## Attempt 1 (WA) — equal-char case
Failing test: `pattern = "rr"` (both chars identical), long `text`.

```java
if (c == pattern.charAt(0)){ p1Count++; p2Count++; }
else if ( c == pattern.charAt(1)){            // unreachable when p0 == p1
    skippedP1 += p1Count ;
    addedP1   += p1Count + 1;
}
```

**WA-cause [missing-edge-rule]:** the running-pair model bakes in a hidden assumption — *every character is either a left-element (`p0`) or a right-element (`p1`), never both.* That disjointness is what guarantees no element pairs with itself. When `p0 == p1` the assumption **collapses** and no `if`/`else if` rearrangement saves it:

- With `else if`: the second branch is **unreachable** → both `added/skipped` stay 0 → returns garbage.
- Tried `if` + `if` instead (user verified): every `r` fires **both** branches in one iteration; since `p1Count++` runs first, the current `r` counts as pairing **with itself** → accumulates `1+2+…+k = k(k+1)/2` instead of the true base `C(k,2) = k(k-1)/2`. Self-pairing inflation.

So the equal-char case genuinely needs its **own closed-form branch**, not a patch to the scan.

## Attempt 2 (AC) — combinatorics branch
With `k` copies of the shared char, base subsequences = `C(k,2)`; inserting one more → `C(k+1,2) = base + k`:

```java
if (pattern.charAt(1) == pattern.charAt(0)){
    return ( (p1Count + 1) * (p1Count) ) / 2;   // C(k+1, 2)
}
skippedP1 += p1Count;                            // = base + insert p1 at end
return Math.max(addedP1, skippedP1);             // addedP1 = base + insert p0 at front
```

(For the distinct-char path: `skippedP1` = running base + final `p1Count` = base + "insert `p1` at end"; `addedP1` = running base + `count(p1)` = base + "insert `p0` at front".)

## Canonical (cleanest) form — for the cold re-solve ([[lc-revise-to-cleanest-form]])
Unify both cases by counting first, then adding the best single char. The `p0==p1` case needs no special branch if you compute the base honestly (each `p1` pairs only with `p0`s strictly before it — equal chars handled because you add to `base` *before* incrementing the shared counter):

```java
public long maximumSubsequenceCount(String text, String pattern) {
    char a = pattern.charAt(0), b = pattern.charAt(1);
    long base = 0, cntA = 0, cntB = 0;
    for (char c : text.toCharArray()) {
        if (c == b) base += cntA;   // b pairs with every a seen so far (count b BEFORE bumping a when a==b)
        if (c == a) cntA++;
        if (c == b) cntB++;
    }
    return base + Math.max(cntA, cntB);
}
```
When `a==b`: each char hits `base += cntA` then `cntA++` then `cntB++`, so `base = 0+1+…+(k-1) = C(k,2)` and `max(cntA,cntB)=k` → `C(k+1,2)`. Same answer, **no special branch** — the ordering (count the pair *before* bumping the left counter) is what removes the self-pairing bug structurally.

## Lesson
**Any "count pairs while scanning" solution silently assumes the two roles are disjoint.** The moment the *same element can fill both roles* (here `pattern[0]==pattern[1]`), the running model either short-circuits (`else if`) or self-pairs (`if`+`if`) → switch to closed form, or order the update so the pair is counted *before* the left-counter is bumped. This is the load-bearing edge that the Step-3 ritual (an explicit `p0==p1` case) would have caught pre-submit.

## REVISION TARGET (Day+14)
Re-derive cold: why "front or end" is optimal (insert `p0` only at front → pairs with all later `p1`; symmetric for `p1`), the `max(count(p0), count(p1))` gain, and the `p0==p1` collapse → `C(k+1,2)`. Reproduce the single-branch canonical form (count-before-bump), not the two-branch one.
