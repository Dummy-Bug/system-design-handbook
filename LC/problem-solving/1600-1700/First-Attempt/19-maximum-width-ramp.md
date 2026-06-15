# 19 — Maximum Width Ramp

- **Link:** https://leetcode.com/problems/maximum-width-ramp/ (LC 962)
- **Band:** 1600–1700 · sealed queue · blind deal #19 · Q2 (AR 55.9%) · **answer-key bucket = Monotonic-Stack ★ (+Two-Ptr)**
- **Bucket (OUR code):** **Sorting + hashmap-of-positions** (sort values, sweep tracking min index). Credited by mechanic-in-code [[lc-credit-mechanic-not-label]] — **NOT Monotonic-Stack** (we never used a stack). Sorting = substrate, Hashing already owned → no gating bucket credited.
- **Dealt:** 2026-06-15 · **AC:** 2026-06-15 (**self-derived, first submission clean**; not a trivial idea — the sort+min-index sweep was genuinely derived).
- **Result:** ✅ **CLEAN first-submission self-derived AC** — clean-rate **12/17 → 13/18 (~72%)**. BUT the answer-key target was the **Monotonic-Stack ★ blind-spot**, and we solved it `O(n log n)` via sort instead → **Mono-Stack NOT credited, stays 1/2.** This is the **4th** debt/blind-spot dodged by a hashmap over-model ([[lc-index-bookkeeping-overmodel]] — `Map<value, Deque<index>>`).

---

## The problem
A *ramp* is `(i,j)`, `i<j`, `nums[i] ≤ nums[j]`; width `j-i`. Return max width (0 if none). `2 ≤ n ≤ 5e4`, `0 ≤ nums[i] ≤ 5e4`.

## Approach taken (sort + min-index sweep)
- `Map<value, Deque<index>>` of all positions; sort `nums`; iterate ascending value, poll the next index per value, track `minIndex` seen so far, `ans = max(ans, index - minIndex)`.
- Since values processed ascending, `minIndex` = smallest index among all values ≤ current → best left endpoint for current index as the right end. `O(n log n)`.
- **Over-model:** the `Map<value,Deque<index>>` is unnecessary — the LC index-sort form (`Integer[]` sorted by value, tie-break `i-j`) does the same in one structure. The deque bought nothing a stable sort tiebreak didn't. [[lc-index-bookkeeping-overmodel]] — counter-heuristic ("what is this structure buying me?") didn't fire.

## What was missed — the Monotonic-Stack mechanic (the actual target)
`O(n)`, two passes: build a **strictly-decreasing-value candidate stack** L→R (an earlier index with ≤ value dominates a later larger one as a left endpoint), then **sweep `j` R→L** popping while `nums[top] ≤ nums[j]` → each pop retires a candidate with its **farthest** right endpoint. User had *seen* the mono path but bailed to the map ("felt easier").
- **Reflex-gap surfaced + fixed:** the installed mono-stack atom (06) covers only **nearest** greater/smaller; this is the **farthest/widest** variant, never installed. → new **Stack Atom 09** created (`reflexes/primitive-reflex/topics/04-stack/09-monotonic-farthest/`). Install was Socratically led ⇒ **acquisition, not a rep** ⇒ Mono-Stack still 1/2; rep 2 owed cold on carried #9 max-chunks.

## Step 2 — worked example (`nums=[6,0,8,2,1,5]`, expected 4)
sorted values `[0,1,2,5,6,8]` → original indices `[1,4,3,5,0,2]`; sweep tracking `minIndex`:
| val | idx | minIndex before | idx-minIndex | ans |
|---|---|---|---|---|
| 0 | 1 | ∞ | — | 0 |
| 1 | 4 | 1 | 3 | 3 |
| 2 | 3 | 1 | 2 | 3 |
| 5 | 5 | 1 | **4** | **4** |
| 6 | 0 | 1 | -1 | 4 |
| 8 | 2 | 0 | 2 | 4 |

ans = **4**. ✅

## Step 3 — named edge cases
1. **No ramp** (strictly decreasing array) → every `idx-minIndex ≤ 0` → ans 0.
2. **Equal values** → all form valid ramps; deque/tiebreak must keep smaller index first (else widths shrink).
3. **`minIndex` sentinel** — `Integer.MAX_VALUE` works (`idx - MAX` is a harmless large negative, no underflow since `idx ≥ 0`); `n` is the cleaner sentinel.
4. **Value range** `≤ 5e4` → subtraction comparator safe; reflex `Integer.compare` for full-int-range problems.

## As-submitted solution (AC) — sort + position map
```java
class Solution {
    public int maxWidthRamp(int[] nums) {
        Map<Integer,Deque<Integer>> map = new HashMap<>();
        int n = nums.length;
        for (int i = 0; i < n; i++) {
            Deque<Integer> q = map.getOrDefault(nums[i], new ArrayDeque<>());
            q.offer(i); map.put(nums[i], q);
        }
        Arrays.sort(nums);
        int ans = 0, minIndex = Integer.MAX_VALUE;
        for (int i = 0; i < n; i++) {
            int index = map.get(nums[i]).poll();
            ans = Math.max(ans, index - minIndex);
            minIndex = Math.min(minIndex, index);
        }
        return ans;
    }
}
```
- Time `O(n log n)`, space `O(n)`.

## Canonical / cleanest forms
- **Lighter sort (de-over-modeled):** `Integer[] idx` sorted by `(nums[i]≠nums[j] ? nums[i]-nums[j] : i-j)`, sweep tracking `minIndex`. No map/deque. Same `O(n log n)`.
- **Optimal — monotonic candidate stack (Atom 09):** `O(n)`, two passes. *This is the rep-worthy mechanic and the one to reach for next time.*

## Lesson
- **Over-model bug, 4th occurrence:** reached for `Map<key,Deque<index>>` when a sort tiebreak (or better, a stack) suffices. The hashmap is the comfort tool that keeps dodging the target mechanic (push-dominoes→not two-ptr, advantage→not two-ptr, ramp→not mono-stack).
- **Trigger to install (Atom 09):** *"max width/span of a pair under an order condition" → monotonic candidate stack + reverse sweep.* The 06 reflex (nearest) does NOT cover this — that's why nothing fired.

## PENDING
- **No cold re-solve owed** (clean first-AC) — but **a fresh mono-stack rep IS owed** to close the blind-spot (carried #9 max-chunks), where Atom 09 must fire cold.
- **Day+14 revision (due 2026-06-29):** re-derive the Atom-09 mechanic cold (domination → decreasing candidate stack → reverse sweep). [[lc-retrieval-not-reread]]
- **Mono-Stack ★ still 1/2.** Over-model is the recurring failure to watch.
