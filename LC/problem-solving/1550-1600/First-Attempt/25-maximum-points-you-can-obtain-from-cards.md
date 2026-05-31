### #25 — Maximum Points You Can Obtain From Cards
**Link:** https://leetcode.com/problems/maximum-points-you-can-obtain-from-cards/
**Date attempted:** 2026-05-30
**AC at:** 2026-05-30 07:30 IST
**Rating:** 1550–1600 band (Phase 2 — sealed queue, deal-list #15)
**Time:** 24 min — first-submission AC ✓ (self-derived, under cap)
**Pattern (debrief):** Sliding Window · Prefix Sum — Q2, AR 57.7%

---

**Verbatim thinking:**

- struggled on the index arithmetic: "if I have `k-1` as an index, how much do I travel back from `n-1` to reach the same exact index?" — settled it: subtract `k` from `n-1`, i.e. the window starts at `n-k`.
- reframed "take k cards from the two ends" as a fixed-size **circular window of size k** that starts at `n-k` and wraps past the end using modulo.

**Insight:**
Picking k cards from the front and back = sliding a length-k window around the *circular* array. Anchor the window start at `n-k`, advance both pointers, and index with `% n` to wrap. The max window sum over that circular sweep is the answer. (Equivalent dual: minimize the contiguous length-`n-k` middle window — but the circular-window framing is what the user derived.)

**Key gotcha:**
- Window grow phase vs slide phase: while `j - i + 1 < k` keep adding (`j++`); once full, add `cardPoints[j%n]`, score, then drop `cardPoints[i%n]` and advance both.
- Loop guard `i <= n` rather than `< n` so the final wrapped window is scored.

**Complexity:**
O(n) time, O(1) space.

**Alternative approaches (not explored):**
1. **Total − min middle window:** `sum(all) − min subarray sum of length n-k`. Single non-wrapping sliding window, no modulo. O(n) / O(1).
2. **Prefix/suffix sums:** precompute prefix of first i and suffix of last k-i, maximize `pre[i] + suf[k-i]` over i in 0..k. O(n) / O(n).

**Solution code (as submitted):**

```java
class Solution {
    public int maxScore(int[] cardPoints, int k) {

        int n = cardPoints.length;

        int i = n - k ;
        int j = i;

        int maxPoints = 0;
        int currPoints = 0;

        while ( i <= n){

            if (j - i + 1 < k){
                currPoints += cardPoints[j];
                j++;
                continue;
            }

            currPoints += cardPoints[j%n];
            maxPoints = Math.max(currPoints,maxPoints);
            currPoints -= cardPoints[i%n];

            i++;
            j++;

        }
        return maxPoints;
    }
}
```
