# 30 — Find the Integer Added to Array II

- **Link:** https://leetcode.com/problems/find-the-integer-added-to-array-ii/ (LC 3132)
- **Dealt:** 2026-11-12, first problem after the 4.5-month DSA gap (restart under `../../../Current-Standing/12-Plan-Nov-2026.md`)
- **Rating / slot:** 1620 · Q2 · AR 33.0%
- **Result:** ⚠️ **AC after 1 WA, hinted → soft fail**, about 72 min, over the 30-min cap
- **Bucket (revealed post-solve):** answer key = **Two-Pointers** (sort + enumerate 3 candidates + two-pointer check). Our code = enumeration + sum equation + linear validation, so the two-pointer mechanic was not the load-bearing part.
- **Cold re-solve:** ⏳ owed (hinted), blank file, before the next new problem.

## Timeline

| Time | Min | What happened |
|---|---|---|
| 15:53 | 0 | Started reading |
| 15:57 | 4 | Read "guaranteed reachable with at least one x" as: several x can work, find the minimum |
| 15:58 | 5 | Noticed n ≤ 200, so O(n³) is fine |
| 16:04 | 10 | Approach: sums s1 and s2; remove a pair from nums1; solve (n1 − 2)·x = s2 − (s1 − pairSum) for x; take the min over pairs |
| 16:07 | 13 | Moved to code; Step 2 / Step 3 asked for, not done |
| 16:16 | 22 | Asked which is the minimum of −2 and −10 (was assuming −2) → clarified: −10, minimum is the smallest value |
| 16:23 | 30 | Cap passed |
| 16:50 | 57 | Stuck on picking the minimum; had been choosing the value closest to zero |
| 16:52 | 59 | Clarified again: minimum = smallest on the number line; given a hard stop of 17:05 |
| 16:55 | 62 | Found the case `[7,9,1,4] / [0,8]`: plain min gives −4, expected −1 |
| 16:57 | 64 | **Hint:** −4 matches the sum but not the arrays (`[7,9]−4 = [3,5] ≠ [0,8]`); a matching sum does not prove a candidate valid |
| 17:00 | 67 | Believed −4 was valid; the statement's definition of equal was quoted back |
| 17:01 | 68 | Realised: had ignored "same integers with the same frequencies" |
| ~17:05 | ~72 | Added `isValid` after sorting both arrays, fixed a wrong-index typo, **AC** (after 1 WA). Burned out by the end |

## The approach (ours)

1. Sort both arrays.
2. For every pair `(i, j)` of nums1 to remove, the sum equation gives the only possible x: `x = (s2 − (s1 − nums1[i] − nums1[j])) / (n1 − 2)`, skipped when not divisible.
3. The sum is necessary but not sufficient, so validate: walk nums1 skipping `i` and `j`, and check each `nums1[k] + x` equals the next element of nums2 (both sorted, so they line up in order).
4. Take `Math.min` over the valid x.

Complexity: O(n²) pairs × O(n) validation = **O(n³)** time plus the O(n log n) sorts; O(1) extra space beyond sorting. With n ≤ 200 that is at most about 8 million steps.

## WA-causes

- **WA-cause [read-error]:** treated "equal" as "same sum" and skipped the line defining it — "Two arrays are considered equal when they contain the same integers with the same frequencies." The sum equation alone accepted x = −4 for `[7,9,1,4] / [0,8]`.
- **WA-cause [incomplete-validation]:** an earlier version skipped `x == 0` with `continue`, but x = 0 is a valid answer.
- **WA-cause [wrong-index]:** `isValid` compared `nums1[i] + ans` where the loop variable was `k`; fixed to `nums1[k] + ans`. Sibling of the stale-read family (checklist item 16).
- **Meaning of minimum:** picked the value closest to zero instead of the smallest value. Not a bug family, a definition slip; it cost about 30 minutes.

## Process note

Step 2 (recompute the richest worked example) and Step 3 (named edge cases) were skipped. Tracing the examples against the statement's definition of equal would have exposed the read error before any code.

## Debrief — the answer-key approach (editorial, read after AC)

After sorting, two removed elements can only come from nums1, so nums2[0] must come from one of nums1[0], nums1[1] or nums1[2]. That gives just 3 candidates, `x = nums2[0] − nums1[i]` for i in 0..2. Check each with two pointers over the sorted arrays, allowing at most 2 skipped elements of nums1, and take the smallest x that passes. **O(n log n)** time.

**Reflex:** when the answer must map one sorted array onto another, the smallest element pins the answer to a handful of candidates. Enumerate candidates from the anchor instead of enumerating every pair.

## Final code (AC)

```java
class Solution {

    private boolean isValid(int ans, int i, int j, int[] nums1, int[] nums2) {
        int skipped = 0;
        for (int k = 0; k < nums1.length; k++) {
            if (k == i || k == j) {
                skipped += 1;
                continue;
            }
            if ((nums1[k] + ans) != nums2[k - skipped]) return false;
        }
        return true;
    }

    public int minimumAddedInteger(int[] nums1, int[] nums2) {
        Arrays.sort(nums1);
        Arrays.sort(nums2);

        int totalSum = 0;
        for (int i = 0; i < nums1.length; i++) {
            totalSum += nums1[i];
        }

        int expectedSum = 0;
        for (int i = 0; i < nums2.length; i++) {
            expectedSum += nums2[i];
        }

        int minX = Integer.MAX_VALUE;

        for (int i = 0; i < nums1.length; i++) {
            for (int j = i + 1; j < nums1.length; j++) {
                int pairSum = nums1[i] + nums1[j];
                int effectiveSum = expectedSum - (totalSum - pairSum);
                int n = nums1.length - 2;

                if ((effectiveSum) % n != 0) {
                    continue;
                }

                int possibleAnswer = effectiveSum / n;
                if (isValid(possibleAnswer, i, j, nums1, nums2)) {
                    minX = Math.min(possibleAnswer, minX);
                }
            }
        }
        return minX;
    }
}
```
