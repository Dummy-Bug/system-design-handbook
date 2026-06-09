# 38 — Maximize Greatness of an Array

- **Link:** https://leetcode.com/problems/maximize-greatness-of-an-array/
- **Band:** 1550–1600 · Phase 2 sealed queue · re-shuffled-order deal (post-2026-06-08 shuffle) · undealt top-of-list #1
- **Bucket (revealed post-solve):** **Greedy / Two-Pointers** (sort + same-direction read/write count). Credit by [[lc-classify-by-own-solution]]: final AC code is the same-direction two-pointer count.
- **Dealt:** 2026-06-09
- **AC:** 2026-06-09 07:46 IST _(correct two-pointer reached, but **after** Claude diagnosed the WA bug and supplied the corrected frame)_
- **Result:** ❌ **WA-then-HARD-FAIL.** First submission WA (`[42,8,75,28,35,21,13,21]` → 7, expected 6). Fix + correct approach were **Claude-supplied** (bug diagnosis + the `n−maxFreq` characterization + the two-pointer), so this is **assisted = hard fail, NOT a clean rep.** No ownership credit for Greedy/Two-Pointers.

## The problem
Permute `nums` into `perm`. **Greatness** = count of indices `i` with `perm[i] > nums[i]`. Return the maximum greatness over all permutations.

## What I submitted first (WA)
Sort, then scan groups of equal values from the **top** down, accumulating `ans += Math.min(freq, j)` at each group boundary, where `j` = index of the group's bottom element = count of elements strictly below the group.

```java
int ans = 0, j = nums.length - 1, freq = 1;
Arrays.sort(nums);
while (j-1 >= 0){
    if (nums[j] == nums[j-1]){ freq++; j--; continue; }
    ans += Math.min(freq, j);
    freq = 1; j--;
}
return ans;
```

## WA-cause [logic-frame: shared-resource double-count → wrong bottleneck]
The mental model — "largest tops 2nd-largest, 2nd tops 3rd, …" — is correct **only for distinct values**. The code's failure is structural, **not** a terminating condition (which is what I believed at first):

- `min(freq, j)` charges each upper group against the pool of elements **below it**, but that pool is **shared** across all upper groups. Summing per-group `min` **re-counts** lower elements. On the failing input the base `8` is topped by the `{21,21}` group AND again by `{13}` → `8` counted twice → +1 overcount (7 vs 6).
- General characterization: the code returns **`n − (frequency of the SMALLEST value)`**, but the answer is **`n − (MAXIMUM frequency anywhere)`**. It anchors the bottleneck at the smallest value (drops the bottom group, caps by cumulative-below); the true bottleneck (max frequency) can sit anywhere. Right only when the smallest value is the mode.
  - Proof 2: `[1,1,2,3,3,3]` → code gives `6−minFreq(2)=4`, correct is `6−maxFreq(3)=3`.

## Correct approaches
**(a) `n − maxFreq`** — sort, find the longest equal run, subtract:
```java
Arrays.sort(nums);
int maxFreq = 1, freq = 1;
for (int j = 1; j < nums.length; j++){
    freq = (nums[j] == nums[j-1]) ? freq+1 : 1;
    maxFreq = Math.max(maxFreq, freq);
}
return nums.length - maxFreq;
```

**(b) Same-direction two-pointer (the submitted fix):**
```java
Arrays.sort(nums);
int i = 0;
for (int j = 0; j < nums.length; j++)
    if (nums[j] > nums[i]) i++;
return i;
```
`j` = read head (all n); `i` = slow head, advances only when a strictly-smaller unused base exists (`nums[j] > nums[i]`). Duplicates auto-stall `i` exactly once → it computes `n − maxFreq` implicitly.

## Primitive-reflex link (NOT written to the reflex folder per user)
The two-pointer fix is a **costume of Two-Pointers Atom 2 (same-direction, single array)**: read head over all n, slow head advances only on a qualifying element. Two twists vs the installed costumes: (1) **action is degenerate** — no overwrite/swap, `i` is purely a count/boundary; (2) **qualify references the slow head** (`nums[j] > nums[i]`), not a fixed prior value — and sortedness lives in that qualify condition (the §④ insight). Recognition costume only; deliberately NOT filed as a new atom.

## Lesson
- "Maximize positions where a permuted value beats the original" on a multiset ⇒ matching toppers to strictly-smaller bases ⇒ **answer = n − maxFreq** ⇒ sort + same-direction two-pointer count.
- The recurring trap: a per-element/per-group greedy that **sums against a shared resource** without decrementing it → double counts. Counter-check: "is the pool each step draws from disjoint, or shared?" If shared, a running `min`-sum overcounts.

## Perturbation debrief ([[lc-perturbation-debrief]]) — worked Socratically in chat 2026-06-09, then written
Target = the **optimized solution** (sort + two-pointer count / `n − maxFreq`), not the WA group-sum. Three suspicious specifics poked; each turned out load-bearing.

**Probe 1 — strict `>` → non-strict `>=`.** With the array sorted and `i`,`j` starting together, `nums[j] >= nums[i]` is *always* true (sorted), so `i` runs to `n`. Answer becomes trivially `n` — the identity permutation already "satisfies" every position via self-ties. **Finding:** the entire difficulty lives in the single `>` character; strictness is what makes duplicates the bottleneck.

**Probe 2 — same multiset → a second array `b`.** Assign elements of a different array `b` (same length) to positions of `nums`, maximize count of `b[i] > nums[i]`. Change: sort *both*, `i` over sorted `nums` (bases), `j` over sorted `b` (toppers), qualify `b[j] > nums[i]`. This is **Advantage Shuffle (LC 870)**. **Finding:** "same array" was never load-bearing for the mechanic — it's just the special case `b == nums`. The atom is really *two sorted sequences*, so the costume drifts **Atom 2 (single array) → Atom 3 (two sequences)**.
```java
Arrays.sort(nums); Arrays.sort(b);
int i = 0;
for (int j = 0; j < b.length; j++) if (b[j] > nums[i]) i++;
return i;
```

**Probe 3 — count of wins → total magnitude `Σ max(0, perm[i] − nums[i])`.** The two-pointer does **NOT** carry over; the greedy *inverts*. Count wants the **smallest topper that beats each base** (conserve big elements → more wins, minimal margin); magnitude wants the **largest topper on the smallest base** (maximal margin). Optimal = reverse-pair the sorted array = `(sum of top half) − (sum of bottom half)`, via a **converging** two-pointer:
```java
Arrays.sort(nums);
int lo = 0, hi = nums.length - 1; long total = 0;
while (lo < hi) { total += nums[hi] - nums[lo]; lo++; hi--; }
return total;
```
**Finding (deepest):** flipping the objective flips the pointer motion — **count = same-direction (Atom 2) `→ →`; magnitude = converging (Atom 1) `→ ←`.** Same sort, same skeleton; "count vs magnitude" is the load-bearing word that selects min-margin vs max-margin greedy, hence the motion.

**Net:** all three specifics (strict `>`, same-multiset, count-not-magnitude) are load-bearing. The reusable trigger trio: *strictness ⇒ duplicates are the bottleneck; same-vs-two arrays ⇒ Atom 2 vs Atom 3; count-vs-magnitude ⇒ same-direction vs converging motion.*

## REVISION TARGET (Day+14)
Cold, blank page: (1) state the answer is `n − maxFreq` and *why* (most-frequent value is the bottleneck — its copies can't top each other); (2) re-derive the two-pointer that computes it; (3) re-explain why the original `min(freq, j)` group-sum double-counts the shared lower pool. **This was a hard fail — it owes a full cold re-solve before it can count toward any rep.**
