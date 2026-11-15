# 32 — Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit

- **Link:** https://leetcode.com/problems/longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/ (LC 1438)
- **Dealt:** 2026-11-14 morning, third problem after the restart
- **Rating / slot:** 1672 · Weekly Contest 187 Q3 · AR 57.7%
- **Result:** ✅ **Clean first-submission AC, self-derived, 60 min, over the 30-min cap.** One approach check from Claude at 29 min, answered YES only, no hint. Counts as solved, but not at the 20-min readiness bar.
- **Bucket (revealed post-solve):** **Sliding-Window**, with the window max and min kept by two heaps (ours) or two monotonic deques (answer key).
- **Cold re-solve:** not owed (no hint, no WA, no editorial).

## Timeline

| Time | Min | What happened |
|---|---|---|
| 06:21 | 0 | Started reading |
| 06:25 | 4 | n ≤ 10⁵, so O(n²) is out; nums[i] and limit go up to 10⁹ |
| 06:27 | 6 | Noticed nums[i] is always positive |
| 06:50 | 29 | Approach: a max-heap and a min-heap of (value, index). Extend while the current element is within limit of both the max and the min; when a check breaks, pop from that heap and move the window start past the popped index; entries with an index before the start are stale and are popped when they surface. Put the complexity at O(n log n) |
| ~06:51 | 30 | Cap. Asked for a YES / NO on the approach only → YES |
| 06:51–07:21 | 30–60 | Coded |
| 07:21 | 60 | **AC** on the first submission |

## The approach (ours)

1. Window `[i, j]`. For each `j`, before adding `nums[j]`, pop from the min-heap while its top is more than `limit` from `nums[j]` or its index is before `i`; each pop of an offender moves `i` to `top index + 1`.
2. Push `nums[j]` into the min-heap, then do the same for the max-heap and push.
3. The window is now valid, so record `j − i + 1`.

Why it works: the tops of the two heaps are the window's min and max once stale entries are cleared, and every element left in the window is between them, so checking `nums[j]` against both tops is enough. `i` only moves forward (`Math.max`), so an old entry deeper in a heap is caught by `top[1] < i` when it reaches the top.

Complexity: each index is pushed and popped at most once per heap, **O(n log n)** time, O(n) space.

## Process note

Step 2 (recompute the richest worked example) and Step 3 (named edge cases) were not posted before coding. It cost nothing here, but coding took as long as deriving (about 30 min each), and the two steps are what shorten the coding half.

## Debrief — the answer-key approach (editorial)

Keep two deques of indices instead of heaps: the max-deque holds indices with decreasing values and the min-deque increasing values. On each new `r`, pop from the back of the max-deque while its value is less than `nums[r]`, and from the back of the min-deque while its value is greater, then push `r`. While `nums[maxFront] − nums[minFront] > limit`, move `l` right and drop a front index that falls below `l`. Each index enters and leaves each deque once, so **O(n)** time.

The heap version stays a valid AC, because the editorial also accepts the O(n log n) ordered-set version. The deque is the step from O(n log n) to O(n): an element that has a larger value to its right can never be the window max again, so it can be thrown away instead of kept in a heap.

**Reflex:** a sliding window that needs its max or min at every step → monotonic deque, O(n). A heap with lazy deletion is the O(n log n) fallback.

## Final code (AC)

```java
class Solution {

    public int longestSubarray(int[] nums, int limit) {

        PriorityQueue<int[]> minHeap = new PriorityQueue<>((a,b) -> Integer.compare(a[0] , b[0]));
        PriorityQueue<int[]> maxHeap = new PriorityQueue<>((a, b) -> Integer.compare(b[0] , a[0]));

        int maxLength = 1;
        int i = 0;
        for (int j = 0; j < nums.length; j++) {

            while (!minHeap.isEmpty()) {
                int[] top = minHeap.peek();
                if (Math.abs(top[0] - nums[j]) > limit || top[1] < i) {
                    i = Math.max(top[1] + 1, i);
                    minHeap.poll();
                } else
                    break;
            }

            minHeap.offer(new int[]{ nums[j], j });

            while (!maxHeap.isEmpty()) {
                
                int[] top = maxHeap.peek();
                
                if (Math.abs(top[0] - nums[j]) > limit || top[1] < i) {
                    i = Math.max(top[1] + 1, i);
                    maxHeap.poll();
                } else
                    break;
            }

            maxHeap.offer(new int[] { nums[j], j });
            maxLength = Math.max(maxLength , j - i + 1);
        }
        return maxLength;

    }
}
```
