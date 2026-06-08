### #28 — Ways to Split Array Into Good Subarrays
**Link:** https://leetcode.com/problems/ways-to-split-array-into-good-subarrays/
**Date attempted:** 2026-05-31
**Rating:** 1550–1600 band (Phase 2 — sealed queue, deal-list #1)
**AC at:** 2026-06-01 _(self-derived, no hint)_
**Time:** ~70 min total — WA on first submission, AC after self-debug (over cap)
**Status:** ❌→✓ **WA-then-AC = SOFT FAIL** (derivation clause exempts time, not implementation discipline; rep does NOT count toward ownership)
**Pattern (debrief):** Combinatorics — **multiplication principle** over gaps between consecutive `1`s. (Answer key files it under DP » Count-ways/Linear by AR, but OUR code is pure gap-product counting, no DP table — credit the mechanic we used: [[lc-credit-mechanic-not-label]].) Q3, AR 35.1%.

---

**Derivation log (own reasoning, ~60 min):**
- Scan from left: until we hit a prefix with `sum == 1` there is no good subarray; when `leftSum == 1` we can split, but must also check the remaining right side still has `sum >= 1` to be a valid split. Felt "fishy."
- Realised the statement counts **ways to split** (number of ways to partition into good subarrays), not the number of good subarrays. Worked small cases:
  - `[1,0,0,1]` → 3 ways. (Noted #good-subarrays would be 6 — different quantity.)
  - `[1,0,0,0,1]` → 4 ways.
  - `[0,1,1,0]` → only 1 way, giving 2 good subarrays.

**Attempt 1 (WA):**
- Approach: find index of first `1` (`left`), index of last `1` (`right`), answer = `right - left` (and `1` if `left == right`, `0` if no `1`).
- Failing test: `[1,0,0,1,0,0,1]` → expected **9**, got **6**.

**Solution code (attempt 1, WA):**

```java
class Solution {
    public int numberOfGoodSubarraySplits(int[] nums) {

        int left = -1 , right = -1 , n = nums.length;

        for (int i = 0; i < n; i++){
            if (nums[i] == 1){
                left = i;
                break;
            }
        }

        if (left == -1) {
            return 0;
        }

        for (int j = n - 1; j >= left; j--){
            if (nums[j] == 1){
                right = j;
                break;
            }
        }

        if (left == right){
            return 1;
        }

        return right - left;
    }
}
```

**WA-cause [wrong-approach]:** `right - left` is not the count (verified wrong by
`[1,0,0,1,0,0,1]`: 6 vs 9). Correct mechanism deliberately **not recorded here** —
to be filled in only after the cold re-derivation, to keep the retry clean.

---

**Attempt 2 (AC) — fixed code:**

```java
class Solution {
    public int numberOfGoodSubarraySplits(int[] nums) {

        int MOD = 1000000007;

        int n = nums.length;
        int i ;
        for (i = 0; i < n; i++){
            if (nums[i] == 1){
                break;
            }
        }

        if (i == n){
            return 0;
        }

        int j = i + 1;
        long count = 1L;

        while (j < n){

            if (nums[j] == 1){
                count = ( count * (j - i) )%MOD;
                i = j;
            }
            j++;
        }

        return (int)count;
    }
}
```

**The insight that fixed it (multiplication principle):**
- A good subarray must contain **exactly one** `1`. So every partition assigns each
  `1` to its own subarray, and the only freedom is **where to cut between two
  adjacent `1`s**.
- Between consecutive ones at indices `prev` and `cur`, the cut can land in any of
  the `cur - prev` slots → `cur - prev` independent choices.
- Total ways = **product** of `(cur - prev)` over all adjacent `1`-pairs (mod 1e9+7).
  Leading/trailing zeros contribute **no** choice (they must attach to the first/last
  `1`), which is exactly why the code only multiplies *between* ones.
- `[1,0,0,1,0,0,1]`: gaps 3 and 3 → `3 × 3 = 9`. ✓ (old `right-left` gave 6.)
- Why MOD even though splits ≪ subarrays: the **product** of gaps blows up fast
  (each gap up to ~1e5, up to ~5e4 ones) → genuinely needs modular arithmetic.

**Lesson:** "count the ways to partition" with a one-special-element-per-part
constraint ⇒ the answer is a **product of inter-element gap sizes**, not a span or a
sum. The trap was conflating *#good-subarrays* (additive, big) with *#ways-to-split*
(multiplicative over gaps). 60 of the 70 min went to disentangling those two
quantities — the code itself is ~15 lines.

> **⏳ REVISION TARGET:** re-derive the multiplication-principle argument cold (why
> product of gaps, why MOD), not just retype the loop. The mechanic, not the syntax,
> is what decayed here.

---

**Note:** also solvable via DP in O(n) (count-ways prefix-sum). Park it — revisit this
and similar problems later, at higher bands, when DP itself becomes the thing being
struggled with.

---

## Two routes — multiplication vs count-ways DP (the recognition that matters)
A "number of ways to split" problem has **two** possible routes, and which one applies is decided by **independence of the cuts**:
- **Independent choices → multiplication principle (closed form):** **each cut's location does NOT constrain the others, so total = (choices for cut-1) × (choices for cut-2) × …** No DP table.
- **Interacting choices → count-ways DP:** if a later cut's validity *depends* on an earlier cut, the product breaks → `dp[i]` = ways up to `i`, summing over valid previous cut points.

**Decision reflex: first ask "are the cuts independent?"** Independent → multiply. Interact → DP.

Here the cuts (one between every adjacent pair of `1`s) are mutually independent → **product of ALL inter-`1` gaps**. The answer key files this under *DP » Count-ways* — that's just the general bucket; multiplication is the sharper tool *because* independence makes it available. (Cousin: #36 number-of-ways-to-split-a-string — same principle, but fixed at 3 parts ⇒ only 2 independent cuts ⇒ product of 2 gaps.)
