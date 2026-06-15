# 17 — Advantage Shuffle

- **Link:** https://leetcode.com/problems/advantage-shuffle/ (LC 870)
- **Band:** 1600–1700 · sealed queue · blind deal #17 · Q3 (AR 54.6%) · **answer-key bucket = Two-Pointers (greedy)**
- **Bucket (OUR code):** **Greedy** (advantage-greedy implemented via **TreeMap** — `higherKey` for next-greater, `firstKey` to dump weakest). Credited by mechanic-in-code [[lc-credit-mechanic-not-label]] — NOT the answer-key's Two-Pointers (we never used the sort+two-pointer mechanic).
- **Dealt:** 2026-06-15 · **AC:** 2026-06-15 (**self-derived, first submission clean**). Approach proposed in chat (one naming slip `ceilingKey`→`higherKey` caught Socratically pre-code; the greedy was self-derived).
- **Result:** ✅ **CLEAN first-submission self-derived AC** — but **Greedy ride-along (already OWNED) → no new ownership rep. Two-Pointers stays 0/2.** Same pattern as #03 push-dominoes (answer-key Two-Pointers, our code wasn't). Clean-rate **11/15 → 12/16 (75%)**.

---

## The problem
Permute `nums1` to maximize the count of indices `i` with `nums1[i] > nums2[i]` (the "advantage"). Return any optimal permutation. `1 ≤ n ≤ 1e5`, `0 ≤ nums[i] ≤ 1e9`.

## Approach (self-derived) — advantage greedy via TreeMap
- TreeMap = multiset of `nums1` (value → count, for duplicates).
- For each `nums2` value, in original order: take `higherKey(v)` (the **smallest element strictly greater** than `v`) → that's an advantage; place it, decrement.
- If `higherKey(v) == null` (nothing beats `v`): **dump `firstKey()`** (smallest remaining) at this position — wins nothing, but keeps the result a valid length-`n` permutation and sacrifices the weakest piece.
- Output written into `nums1[i]` in `nums2`'s order (positions align; safe to overwrite `nums1` since counts live in the map).

## The load-bearing lemma (exchange argument)
> **The smallest remaining element is never the *unique* beater of any position.** If the smallest `m` beats `nums2[j]` (`m > nums2[j]`), then every other element (all ≥ `m`) beats it too. So dumping `m` on a position you can't win never throws away a piece some unwon position secretly needed.

This is *why* dump-smallest is optimal, and why "skip + append leftovers at the end" gives the identical count (leftover count = unfilled-position count). Both correct; inline dump-smallest is the one-pass cleaner form.

## Step 2 — worked example (`nums1=[12,24,8,32]`, `nums2=[13,25,32,11]`, expected count 3)
map `{8,12,24,32}`:
| nums2 | higherKey | place | map after |
|---|---|---|---|
| 13 | 24 | nums1[0]=24 (24>13 ✓) | {8,12,32} |
| 25 | 32 | nums1[1]=32 (32>25 ✓) | {8,12} |
| 32 | null → dump 8 | nums1[2]=8 (8>32 ✗) | {12} |
| 11 | 12 | nums1[3]=12 (12>11 ✓) | {} |

Output `[24,32,8,12]`, advantage = **3**. ✅

## Step 3 — named edge cases
1. **No element beats any** (all `nums2` ≥ max `nums1`) → all dumps; output = ascending leftovers; advantage 0.
2. **Duplicates in `nums1`** → TreeMap stores counts; decrement, remove key at 0. ✅
3. **Map never empty mid-loop** — n elements consumed once each; at step `i` map holds `n-i ≥ 1`. `firstKey`/`higherKey` never hit an empty map. ✅
4. **Ties are not advantages** — must use `higherKey` (strict `>`), NOT `ceilingKey` (`≥`); the failing case `nums1=[2,3], nums2=[2,3]` shows ceilingKey scores 0 where 1 is optimal. (Caught pre-code.)
5. **Overwriting `nums1[i]`** — safe; the result reads from the map, never from `nums1`.

## As-submitted solution (AC)
```java
class Solution {
    public int[] advantageCount(int[] nums1, int[] nums2) {
        TreeMap<Integer,Integer> map = new TreeMap<>();
        for (int num : nums1) map.put(num, map.getOrDefault(num, 0) + 1);
        int i = 0;
        for (int num : nums2) {
            Integer key = (map.higherKey(num) == null) ? map.firstKey() : map.higherKey(num);
            nums1[i++] = key;
            int freq = map.get(key);
            if (freq == 1) map.remove(key); else map.put(key, freq - 1);
        }
        return nums1;
    }
}
```
- Time `O(n log n)`, space `O(n)`.
- _(As-submitted called `higherKey` twice in the null branch; folded to one lookup above — same logic, minor cleanup. Not a bug.)_

## Lesson
- **"Maximize wins when matching one multiset against another" → advantage greedy: smallest-that-strictly-beats, else dump weakest.** The exchange lemma (smallest never the unique beater) is the proof.
- **Credit goes to the mechanic you used, not the problem's tag.** TreeMap-greedy ≠ two-pointer; this earned Greedy (owned), not the Two-Pointers debt. To close Two-Pointers, solve one *using* sort + two pointers.

## PENDING
- **No cold re-solve owed** (clean self-derived first-AC).
- **Day+14 revision (due 2026-06-29):** re-derive the dump-smallest lemma cold (the *why*, not the TreeMap boilerplate). [[lc-retrieval-not-reread]]
- **Two-Pointers still 0/2** — both queue picks (#03, #17) spent without credit → needs 2 fresh sort+two-pointer problems.
