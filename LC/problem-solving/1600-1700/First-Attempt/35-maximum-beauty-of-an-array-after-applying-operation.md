# 35 — Maximum Beauty of an Array After Applying Operation

- **Link:** https://leetcode.com/problems/maximum-beauty-of-an-array-after-applying-operation/ (LC 2779)
- **Dealt:** 2026-11-16 night, sixth problem after the restart, dealt after the tree problem all-nodes-distance-k-in-binary-tree was skipped
- **Rating / slot:** 1638 · Weekly Contest 354 Q2 · AR 58.4%
- **Result:** 🔴 **Editorial, then taught; first-submission AC on 2026-11-17 at 06:29.** Night attempt: stuck at the 30-min cap, LeetCode's two hints, editorial opened at minute 45 without being studied, stopped at minute 47. Morning: the reduction was taught Socratically from hint 2; the sliding window, the Step 2 trace and all of the code were the user's own.
- **Bucket (revealed post-solve):** **Sorting + Sliding Window.** Other editorial routes: binary search for each left end, difference array over the ranges.
- **Cold re-solve:** ⏳ owed, from a blank editor.

## Timeline

| Time | Min | What happened |
|---|---|---|
| 21:12 | 0 | Started reading |
| 21:20 | 8 | Stuck on example 1: could not see why the answer is 3 and not 4, for example by turning everything into [2,2,2,2]. Re-read the problem |
| 21:24 | 12 | Cleared it: with k = 2 the 6 can only come down to 4, not 2, so at most three elements can share one value, either 2 or 4 |
| 21:29 | 17 | First approach, brute force: take each value as the target, count how many elements can reach it, keep the largest count. O(n²), so started looking for an optimisation |
| 21:32 | 20 | On paper, rewrote each element of example 1 as the range it can reach: [2,4], [4,8], [-1,3], [0,4]. Looked for a way to use the ranges |
| 21:42 | 30 | Cap |
| 21:43 | 31 | Could not make the ranges into anything concrete. Since the answer lies in 1..n, tried binary search on the answer for O(n log n) |
| 21:50 | 38 | Stopped: too tough |
| 21:52 | 40 | LeetCode hint 1, sort the array. Had already sorted it, still no approach |
| 21:55 | 43 | LeetCode hint 2 read, could not understand what it means. Claude explained it in chat; not read by the user |
| 21:57 | 45 | Opened the editorial, saw it lists three solutions, did not study them |
| 21:59 | 47 | Stopped for the night; to be taught in the morning |

## Stuck note

1. **Understood:** each element can become any value in [x − k, x + k], and the beauty is the largest number of elements that end up on one shared value.
2. **Tried:** brute force over target values (O(n²)), rewriting each element as its range on paper, binary search on the answer between 1 and n.
3. **Stuck at:** could not turn the ranges into a fast way to count the best shared value.

## How it felt

At minute 38: too tough for me. At minute 43, after hint 2: this level might be too much. At minute 45, on seeing three editorial solutions: could not come up with even one of them.

## Morning session (2026-11-17, 05:48–06:29)

Taught from LeetCode's second hint, one question at a time.

| Step | What happened |
|---|---|
| 1 | Two numbers a ≤ b, k = 2, drawn as ranges: 1 and 4 meet, 1 and 6 do not. Rule stated by the user: they meet when the top of the smaller range reaches the bottom of the bigger one, a + k ≥ b − k |
| 2 | Rearranged by the user to b − a ≤ 2k, which is the hint's condition |
| 3 | Proposed by the user: sort, slide j left to right, move i right while the condition fails, keep the longest window |
| 4 | Claude filled the gap the window skips: why checking only the smallest and largest is enough for a whole group, and why sorting makes the best group a contiguous stretch (see below) |
| 5 | Step 2 by the user: example 1 traced through the window, 3 reproduced |
| 6 | Step 3: first offered the given examples as edge cases. Corrected: Step 2 recomputes the given examples, Step 3 is inputs they do not cover, found by pushing each constraint bound to its extreme. Then three named cases (table below) |
| 7 | Code checked by running, then submitted: **AC** on the first submission |

## The approach

1. **Two elements.** a can reach [a − k, a + k] and b can reach [b − k, b + k]. They can land on one shared value when a + k ≥ b − k, that is b − a ≤ 2k.
2. **A whole group.** The values the smallest and largest can both reach are [max − k, min + k]. Any middle element m has min ≤ m ≤ max, so its range [m − k, m + k] contains that stretch. So a group can meet exactly when max − min ≤ 2k, and only that one pair needs checking. Checked against 20,000 random sorted arrays: 0 mismatches.
3. **Why a subarray.** After sorting, if the smallest and largest of a group fit, everything sorted between them fits too, so the best group is always a contiguous stretch A[i..j] with A[j] − A[i] ≤ 2k.
4. **Counting it.** Sliding window: move j right, move i right while A[j] − A[i] > 2k, keep the largest j − i + 1. i never passes j, because A[j] − A[j] = 0.

Complexity: **O(n log n)** for the sort, O(n) for the window.

**What was missing on the night:** the ranges were on paper at minute 20. The one step not taken was asking when two ranges overlap and writing it as an inequality; that turns the picture into a condition on the sorted array.

**Reflex:** each element can move by up to k and the question is how many can be made equal → draw each as [x − k, x + k], they overlap exactly when max − min ≤ 2k, sort, longest window.

## Edge cases (Step 3)

| Name | Input | Expected | What it tests |
|---|---|---|---|
| All equal | [1,1,1,1], k = 10 | 4 | the whole array fits |
| Max values | [10⁵, …], k = 10⁵ | n | 2k = 2 × 10⁵ and differences ≤ 10⁵, so `int` is safe |
| Single element | [5], k = 0 | 1 | smallest n and smallest k |

Run before submitting: 3, 4, 1 on the examples and the single element, 100000 on n = 10⁵ in 2 ms, 0 mismatches against a brute force over 20,000 random small inputs.

## Final code (AC)

```java
class Solution {
    public int maximumBeauty(int[] nums, int k) {
        
        Arrays.sort(nums);

        int maxBeauty = 0;
        
        int i = 0;
        for (int j = 0; j < nums.length; j++){

            while( nums[j] - nums[i]  > 2*k ){
                i++;
            }
            maxBeauty = Math.max(maxBeauty , j - i + 1);
        }
        return maxBeauty;
    }
}
```
