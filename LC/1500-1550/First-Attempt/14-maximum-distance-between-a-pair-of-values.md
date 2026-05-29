# #14 — Maximum Distance Between a Pair of Values

**Link:** https://leetcode.com/problems/maximum-distance-between-a-pair-of-values/
**Date:** 2026-05-29 (Fri)
**Rating:** ~1500-1550 band (filed as Group A #8 Binary Search pick, but solved as **Two-Pointer** → credited to bucket #7)
**Time:** 14 min — solved ~12:37 PM — **AC clean, first attempt**
**Pattern as solved:** monotonic two-pointer (both arrays non-increasing) — **Two-Pointer ownership rep 1/3**

> **Bucket credit:** This was dealt as the Binary Search / Upper & Lower Bound acquisition pick, but solved cold with a monotonic two-pointer — so it is credited to the **Two-Pointer** bucket (#7, recovering from soft fail), NOT Binary Search. The BS bucket stays open and still needs a genuine `lowerBound`/`upperBound` rep. Count the mechanic exercised, not the file label.

---

## Problem

Two **non-increasing** integer arrays `nums1`, `nums2`. A pair `(i, j)` is *valid* if `i <= j` **and** `nums1[i] <= nums2[j]`. Return the maximum distance `j - i` over all valid pairs (0 if none).

## Approach (verbatim)

We want maximum distance, so we want the indices as far apart as the constraints allow. Walk from the ends: `x = nums1[i]` (left array), `y = nums2[j]` (right array). If `x <= y` the pair is valid — record `j - i` and move `i` left to push for a farther distance. We only move `j` left when `x > y`. Edge case: we can never let `i` go below... if it would, move `i` left. Keep going until a pointer falls off.

## Solution (as submitted)

```java
class Solution {
    public int maxDistance(int[] nums1, int[] nums2) {
        int m = nums1.length, n = nums2.length;
        int i = m - 1, j = n - 1;
        int maxDistance = 0;

        while (i >= 0 && j >= 0) {
            if (nums1[i] <= nums2[j]) {
                maxDistance = Math.max(maxDistance, j - i);
                i--;
            } else if (i < j) {
                j--;
            } else {
                i--;
                j--;
            }
        }
        return maxDistance;
    }
}
```

**Complexity:** O(m + n) time, O(1) space.

## Debrief notes

- **Correct, AC first try, 14 min — clean and quick.** The from-the-end walk works because both arrays are non-increasing: when `nums1[i] > nums2[j]`, `nums1[i]` is the problem and moving `i` left only makes it bigger, so the only productive move is to grow the budget on the `nums2` side (move `j` left to a larger value), guarded by `i < j` to keep `i <= j`.
- **The canonical idiom is the *forward* two-pointer** — slightly cleaner because it never needs the `i == j` special case:

  ```java
  int i = 0, j = 0, ans = 0;
  while (i < nums1.length && j < nums2.length) {
      if (nums1[i] > nums2[j]) i++;          // current nums1[i] too big → advance i
      else { ans = Math.max(ans, j - i); j++; }  // valid → try to stretch j
  }
  ```

  Both are O(m+n); the forward version is the one most editorials show. Your reverse version is equally valid — just carries the extra `else { i--; j--; }` branch.
- **Bucket note — Binary Search NOT exercised.** This was the band's *Binary Search / Upper & Lower Bound* pick, but you solved it with monotonic two-pointer. Binary search *is* genuinely applicable here (for each `i`, binary-search the furthest `j` with `nums2[j] >= nums1[i]` — O(m log n)), unlike the Trie phantom where sort dominated. So this is a softer case: the two-pointer is actually the *better* solution, but the upper/lower-bound BS mechanic specifically wasn't drilled. The AC counts as a clean solve; if you want the BS bucket genuinely owned, do a rep where you reach for `lowerBound`/`upperBound` as the tool. Band already has BS-on-answer installed separately (Group B), so this is a sub-skill gap, not a blind spot.
