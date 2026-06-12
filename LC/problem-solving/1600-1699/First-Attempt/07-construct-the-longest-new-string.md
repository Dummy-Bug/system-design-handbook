# 07 — Construct the Longest New String

- **Link:** https://leetcode.com/problems/construct-the-longest-new-string/
- **Band:** 1600–1699 · sealed queue · blind deal #7 · Q2 (AR 54.8%)
- **Bucket:** answer key files it **DP » Linear**; **OUR code = closed-form Math/Greedy** (no `dp[]`, no recurrence) → credit **Math/Greedy**. **DP-Linear NOT credited — stays 0/2.**
- **Dealt:** 2026-06-12
- **AC:** 2026-06-12 05:57 _(36m **OVER-CAP**; self-derived → **derivation clause** → counts as pass)_
- **Result:** ✅ **clean first-submission AC, self-derived.** Bucket credited = **Math/Greedy (already OWNED)** → no new ownership. Clean-rate now **6/7 (86%)**; clean streak = 5 (#03–#07).
- **Bucket reality:** out-derived the intended DP. The debt-bucket (DP-Linear) you were chasing is **still 0/2** — closed-form construction is the cleaner contest answer but pays no DP debt. Mirror of #04 (greedy ride-along left DP-String open).

---

## The problem
Given `x` copies of `"AA"`, `y` copies of `"BB"`, `z` copies of `"AB"`, concatenate **some** of them into one string containing **neither `"AAA"` nor `"BBB"`**. Return the max possible length.

## Approach — closed-form construction (self-derived)
Reason about how the blocks chain without creating a triple:
- **`AB` blocks are always free.** `"AB"+"AB"+…` = `"ABAB…AB"` has no triple, and the chain starts with `A` / ends with `B`, so it slots into the middle of an `AA…AA | ABAB… | BB…BB` arrangement. All `z` of them contribute → `+2z`.
- **`AA` / `BB` must alternate** (`AABBAABB…`) so no two same-letter blocks touch.
  - If `x == y`: every block alternates perfectly → use **all** → `2x + 2y = 4x` chars.
  - If `x != y`: alternation lets you use `min(x,y)` of the smaller and **`min(x,y)+1`** of the larger (one extra on an end) → `2·m + 2·(m+1)` chars, `m = min(x,y)`.

## Solution (clean first-AC)
```java
class Solution {
    public int longestString(int x, int y, int z) {
        if (x == y) return 4*x + 2*z;
        int m = Math.min(x, y);
        return 2*m + 2*(m + 1) + 2*z;
    }
}
```

## Why the `+1` (the load-bearing insight)
Alternating `A`/`B` blocks, the count of the larger type can exceed the smaller by exactly **one** before you'd be forced to place two of it adjacently (`…AABB AA` is fine; a second trailing `AA` would make `…AAAA`). So `larger = m+1`, `smaller = m`.

## Edge checks (reproduced pre-submit)
- `x=0,y=0`: `x==y` → `2z` (just the AB chain). ✓
- `x=0,y=3,z=0`: `m=0` → `0 + 2 + 0 = 2` — only **one** `BB` usable (two would make `BBBB`). ✓
- `x=0,y=3,z=2`: `m=0` → `0 + 2 + 4 = 6` — `"BB"+"ABAB"`; can't fit a 2nd `BB` anywhere without `BBB`. ✓
- `x=2,y=5,z=1`: `m=2` → `4 + 6 + 2 = 12`. ✓

## WINS
1. **Saw the closed form instead of reaching for DP.** Recognized the structure collapses to counting + the alternation `+1` rule — O(1), no table. The intended solution was a small DP; the cleaner answer was arithmetic.
2. **Clean first submission** — the easy slip here is the `+1` (off-by-one on which side gets the extra block) and forgetting `z` always fully counts. Both right first try.

## Lesson
- **When the state space is "how many of each fixed block can chain," look for the closed form before the DP table** — adjacency-constrained counting often collapses to `min` + a small boundary bonus.
- **Debt-bucket caution:** out-deriving the intended pattern is great for the contest but leaves the targeted debt unpaid. DP-Linear is *still* 0/2 — it needs a problem where DP is the route I actually take (or one with no slick closed form).

## PENDING
- Perturbation debrief — Socratic in chat first, then logged ([[lc-perturbation-before-write]]). No probes pre-written.
- Revision Day+14: re-derive the alternation `+1` rule and the "`z` always free" argument cold from scratch.
