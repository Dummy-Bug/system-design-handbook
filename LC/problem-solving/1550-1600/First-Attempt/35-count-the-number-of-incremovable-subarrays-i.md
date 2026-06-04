# 35 — Count the Number of Incremovable Subarrays I

- **Link:** https://leetcode.com/problems/count-the-number-of-incremovable-subarrays-i/
- **Band:** 1550–1600 · Phase 2 sealed queue deal #8 · Q1 · AR ~56.6%
- **Bucket (revealed post-solve):** **Two Pointers (array)** + prefix/suffix monotonic decomposition + ✦ Invariant/Reframe ([[lc-classify-by-own-solution]]). The optimal mechanic used is the **part-II** method (~2000-rated), self-architected on the part-I problem.
- **Dealt:** 2026-06-02
- **AC events:**
  - **Brute force** — 2026-06-02, <10 min, first-submission AC. **Trivial (n ≤ 50) → no gated-bucket credit.** This was the intended part-I solution (the low constraint was the tell).
  - **O(n) two-pointer** — 2026-06-03 ~07:18 IST, 26 min, first-submission AC (sub-cap).

## Result / classification — SOFT-HINTED ACQUISITION (does NOT count toward the 3 clean reps)
The morning O(n) AC was clean and sub-cap. **User reports NOT reading the detailed editorial** (the 4-step
skeleton / the "two independent bounds" bug) — only a **frame-confirming "you're almost there, one insight left"
signal**. So the architecture and the final insight were genuinely self-derived. It still does **not** tick the
clean-rep box for two reasons: (1) "you've almost solved it" *certifies the frame* — information you never get in
a real cold solve, so it gates the rep; (2) the full editorial sat in-channel, readable overnight, which the
protocol must treat conservatively ("optimistic counting is the root of skip-3"). → **Two Pointers (array)
soft-hinted acquisition — one notch below clean, not a fail.** Clean rep owed on the *next* disguised
two-pointer problem, cold and unassisted.

## The real trophy — overnight consolidation (the load-bearing lesson of this entry)
- **2026-06-02:** 120 min hard-stuck on this exact O(n) two-pointer approach. Bailed at the (extended) cap.
  Took the brute-force AC for part I; left the optimal unfinished.
- **Slept on it.**
- **2026-06-03 morning:** blank-page cold retry → **clean first-submission AC in 26 min.**
- This is [[lc-retrieval-not-reread]] / spaced-retrieval demonstrated on *self*, in one day. The 120 min
  wasn't wasted — it *loaded* the problem; sleep consolidated it; the morning retrieval proved it. **Lesson:
  when stuck past the cap with a live approach, stop and sleep — do not grind. The grind was the 90 wasted min;
  the sleep was the unlock.** Reinforces the new **30 → 60 hard-ceiling** cap rule (stop, don't extend forever).

## Approach (our code)
The non-increasing middle chunk **must** lie inside every removed subarray (you can't leave a descent). So:
1. **Longest strictly-increasing prefix** ends at `left` (`nums[0..left]`).
2. If the whole array is already increasing (`left == n-1`) → every subarray is removable → `n(n+1)/2`.
3. **Longest strictly-increasing suffix** starts at `right` (`nums[right..n-1]`).
4. Count valid removals: iterate how many prefix elements we **keep** (`i` = kept count, `left+1 … 0`). For each
   kept prefix end `nums[i-1]`, two-pointer-advance `j` over the suffix until `nums[j] > nums[i-1]`; the suffix
   may then start anywhere in `[j … n]` (n = keep no suffix). Empty prefix (`i==0`) → all suffix-keeps valid.

```java
class Solution {
    public int incremovableSubarrayCount(int[] nums) {
        int n = nums.length;
        int left = 0;
        for (int i = 1; i < n; i++) {
            if (nums[i - 1] >= nums[i]) break;
            left = i;
        }
        if (left == n - 1) return (n * (n + 1)) / 2;   // whole array already strictly increasing

        int right = n - 1;
        for (int i = n - 2; i >= 0; i--) {
            if (nums[i] >= nums[i + 1]) break;
            right = i;
        }

        int count = 0;
        for (int i = left + 1; i >= 0; i--) {            // i = # prefix elements kept (0..left+1)
            if (i != 0 && nums[i - 1] >= nums[right]) {
                int j = right;
                while (j < n && nums[i - 1] >= nums[j]) j++;   // advance suffix start past the junction
                if (j == n) count += 1;                        // only empty-suffix keep works
                else        count += n - j + 1;                // suffix may start at j..n
            } else {
                count += n - right + 1;                        // empty/small prefix: all suffix-keeps valid
            }
        }
        return count;
    }
}
```
O(n) time, O(1) space.

## Load-bearing insight (yours, verbatim)
> "the subarray present between two monotonic-increasing arrays will always need to be removed to satisfy the
> incremovable property."

That single observation is what reduces the search: the removed window is forced to contain the entire
non-increasing middle; the only freedom is **how much of the increasing prefix/suffix you additionally chop**,
joined where `nums[kept-prefix-end] < nums[kept-suffix-start]`. Two independent bounds, one junction → two pointers.

## Why the brute force teaches nothing here
n ≤ 50 → O(n³) = 125k, trivially licensed. The constraint was the spoiler that brute is *intended* for part I.
The growth lives entirely in the O(n) method (part II, n ≤ 10⁵) — which is why the side-quest, not the brute,
was the real work. ([[lc-derivation-budget-chunking]]: the optimal felt ~2000 because prefix/suffix-decompose +
independent-bounds + merge-count had to be assembled at once.)

## Perturbation probes
_(settled Socratically in chat before writing — [[lc-perturbation-before-write]])_

**Load-bearing assumption = removal is exactly ONE contiguous subarray.**
That single rule forces the removed window to span from the *first* descent to the *last* (with multiple descents,
e.g. `[1,2,1,3,1,4]`, you can't pick off the two dips individually — one contiguous cut must swallow everything
between them). The only remaining freedom is how far to extend the cut into the clean increasing ends → prefix/suffix
two-pointer, O(n). Strictness is *not* load-bearing.

| Perturbation | Effect on the method |
|---|---|
| **Remove a subsequence** (drop contiguity — the load-bearing rule) | becomes **count *all* strictly-increasing subsequences** (the kept set, every length + empty) → counting DP `dp[i]=1+Σ_{j<i, nums[j]<nums[i]} dp[j]`, O(n²) / O(n log n) BIT. **Two-pointer dead.** |
| Remove **two** disjoint subarrays | middle no longer forced into a single block → heavy casework, different problem |
| strict → non-decreasing | **trivial** — only flips `>` vs `>=`; structure unchanged. |

**The tell:** changing "strictly" barely moves anything; changing "one contiguous" detonates the whole approach.
**Contiguity is load-bearing; strictness is cosmetic.** That is the one thing to carry forward from this problem.

## Follow-up — DEFERRED (the subsequence-removal DP variant)
The perturbation above ("remove a subsequence" → **count all strictly-increasing subsequences**) is itself a
worthwhile problem, but **deferred — out of current-band scope:**
- **O(n²) count-DP** `dp[i] = 1 + Σ_{j<i, nums[j]<nums[i]} dp[j]` — ~**1650**. One step off the LIS skeleton
  ("count instead of length"); the recurrence is already extracted, so coding it adds little new.
- **O(n log n) Fenwick/BIT version** (large n) — ~**1900–2000**. Needs coordinate compression + a BIT storing
  **prefix-sums of dp**. The BIT is an **uninstalled blind-spot data structure**, slated cross-band/later —
  building it now would jump the ladder (rule 8).
- **Decision:** revisit after a few revisions / when Fenwick-BIT is formally installed. Don't chase it mid-band
  (it's the meta-version of the "one insight away" tangent). When promoted, it becomes a real queued problem,
  not a hypothetical.

## REVISION TARGET (Day+14)
Re-derive cold the O(n) two-pointer: why the non-increasing middle is forced into every removal, and why the
prefix-keep and suffix-keep are *independent* bounds meeting at one `<` junction. Must be **unassisted** to
upgrade this from acquisition to a clean Two-Pointers ownership rep.
