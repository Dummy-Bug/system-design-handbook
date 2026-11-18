# 34 — Find the Most Competitive Subsequence

- **Link:** https://leetcode.com/problems/find-the-most-competitive-subsequence/ (LC 1673)
- **Dealt:** 2026-11-16 evening, fifth problem after the restart, widened one band up because the Stack bucket is dry in 1600-1699
- **Rating / slot:** 1802 · Weekly Contest 217 Q2 · AR 53.1%
- **Result:** 🟡 **Hinted, first-submission AC, 83 min.** LeetCode's hint at the 30-min cap, then three nudges from Claude (the allowed range for one pick, its two indexes, the link to #32). The heap mechanic and all of the code were self-derived.
- **Bucket (revealed post-solve):** **Greedy + Monotonic Stack.** Ours: window greedy with a min-heap for the range minimum.
- **Cold re-solve:** ✅ done 2026-11-16 evening with the monotonic stack. Approach and pop condition self-derived (two wrong conditions before the right one, checked one word at a time, no hints); final code shown by Claude. See the section below.

## Timeline

| Time | Min | What happened |
|---|---|---|
| 16:48 | 0 | Started reading |
| 16:58 | 10 | Read it as: find the smallest subsequence of length k |
| 17:14 | 26 | Stuck, not able to move the problem |
| 17:21 | 33 | Past the cap. Took LeetCode's hint (left elements have higher priority, build the answer left to right); its first half matched the reading already made |
| 17:31 | 43 | Proposed pick and skip; asked for a check → incorrect |
| ~17:33 | 45 | Nudge 1: the first pick must leave enough elements to its right, so which indexes can it come from |
| ~17:36 | 48 | Had the greedy in words (the smallest value as far left as possible, with enough elements left after it) but could not turn it into code. Nudge 2: name the start and end index of one pick |
| ~17:42 | 54 | Window greedy derived: for each pick, the smallest value in `[start, n − remaining]`, then `start = picked index + 1`. Costed it at O(n·k), about n², too slow |
| ~17:44 | 56 | Stuck on the range minimum. Nudge 3: both ends of the range only move right, the same shape as #32 |
| ~17:46 | 58 | Saw that the start is picked index + 1 and the end grows by one per pick; reopened #32 to recall the mechanic |
| 17:57 | 69 | A plain min-heap gives the range minimum |
| 18:11 | 83 | **AC** on the first submission |

## The approach (ours)

1. Push `(nums[i], i)` for every `i` in `[0, n − k]` into a min-heap ordered by value, then by index.
2. Repeat until `k` values are picked: poll the top. If its index is before `start`, it is stale; drop it for good, since `start` never moves left.
3. Otherwise it is the smallest value in the window. Record it, set `start = index + 1`, move `end` one to the right and push `(nums[end], end)` if `end < n`.

Why it works: the answer's first element must leave `k − 1` elements after it, so it comes from `[0, n − k]`, and the smallest value there is the best possible first element. Every later pick is the same question on `[start, n − remaining]`. After a pick, `start` jumps past the picked index and `end` moves one right, so both ends of the window only move right, and a heap with lazy deletion holds its minimum.

The tie-break by index matters: of two equal minimums, the earlier one leaves more elements to choose the rest from.

Complexity: each index is pushed once and polled at most once, **O(n log n)** time, O(n) space.

Checked against a brute force over 20,000 random small inputs: 0 mismatches.

## What carried over from #32

The range-minimum step is the #32 mechanic, a heap of (value, index) with stale entries popped once their index falls behind the window start. It was recalled only after the nudge named the window shape; the trigger to recognise on its own is: **a window whose two ends only move right, and a min or max needed from it.**

## Process note

The window greedy was in words at minute 48, but turning it into indexes needed a nudge. Writing one pick's start and end index on example 2 is the step that turns a greedy idea into a loop. Step 2 (recompute the richest worked example) would have forced exactly that.

## Debrief — the answer-key approach (monotonic stack)

Scan left to right. While the top of the stack is bigger than the current element and enough elements remain to still fill `k` (`top − 1 + (n − i) ≥ k`), pop it, since the smaller element can take its place. Then push the current element if the stack holds fewer than `k`. Each element is pushed and popped at most once, **O(n)**.

It is the same greedy rule applied one element at a time instead of one window at a time. Measured at n = 10⁵, k = n/2: heap 13.1 ms, stack 0.5 ms. Both pass.

```java
class Solution {
    public int[] mostCompetitive(int[] nums, int k) {
        int[] st = new int[k];
        int top = 0;
        int n = nums.length;
        for (int i = 0; i < n; i++) {
            while (top > 0 && st[top - 1] > nums[i] && top - 1 + (n - i) >= k) {
                top--;
            }
            if (top < k) {
                st[top++] = nums[i];
            }
        }
        return st;
    }
}
```

## Cold re-solve — monotonic stack (2026-11-16 evening)

Done after the session closed at 18:23, finished by 20:50; the exact start was not recorded. Goal: the stack version, not the heap again.

| Step | What happened |
|---|---|
| 1 | Approach: keep pushing bigger elements; when a smaller one arrives, pop while there are still enough elements left. Called it a plain stack, not a monotonic one. Check → approach correct, condition `n - k - stack.size() >= k` incorrect (it never looks at `i`). Pushing bigger and popping on a smaller one keeps the stack increasing, which is exactly a monotonic stack |
| 2 | Rule in words: after a pop, the elements left in the stack plus the elements from here to the end must still fill k. Check → reasoning correct, formula `nums.length - k - stack.size() - 1` still incorrect |
| 3 | `stack.size() - 1 + nums.length - i >= k` → correct |
| 4 | Asked for the full solution; Claude showed the code below |

The two pieces not stated before the code: once the stack holds k elements, a value that could not pop anything is skipped (`if (size < k)`), and an array of size k used as the stack is the answer itself.

Trace on `[2,4,3,3,5,4,9,6]`, k = 4:

```
 i  val   action                         stack
 0   2    push                           2
 1   4    push                           2 4
 2   3    pop 4 (1 + 6 >= 4), push       2 3
 3   3    push (3 > 3 is false)          2 3 3
 4   5    push                           2 3 3 5
 5   4    pop 5 (3 + 3 >= 4), push       2 3 3 4
 6   9    full, skip                     2 3 3 4
 7   6    full, skip                     2 3 3 4
```

```java
class Solution {
    public int[] mostCompetitive(int[] nums, int k) {

        int[] stack = new int[k];
        int size = 0;

        for (int i = 0; i < nums.length; i++) {

            while (size > 0 && stack[size - 1] > nums[i] && size - 1 + nums.length - i >= k) {
                size--;
            }

            if (size < k) {
                stack[size++] = nums[i];
            }
        }
        return stack;
    }
}
```

Checked: [2, 6] and [2, 3, 3, 4] on the examples, 0 mismatches against a brute force over 20,000 random inputs.

**What was missing at minute 26 of the first attempt:** the question that picks the stack's shape. When a new element arrives, which older elements does it make useless forever? Here: every bigger element before it, as long as enough elements remain to drop it. That answer gives the direction (left to right), the order (increasing) and the pop condition in one step.

**Reflex:** smallest (or largest) subsequence of length k → greedy pick of the smallest value in `[start, n − remaining]`; the range minimum comes from a heap with lazy deletion, or the whole thing collapses into a monotonic stack that pops while enough elements remain.

## Final code (AC)

```java
class Solution {

    public int[] mostCompetitive(int[] nums, int k) {

        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> {
            if (a[0] == b[0]) {
                return a[1] - b[1];
            }
            return a[0] - b[0];
        });

        for (int i = 0; i <= nums.length - k; i++) {
            pq.offer(new int[]{nums[i], i});
        }

        int[] result = new int[k];
        int resIdx = 0;
        int start = 0;
        int end = nums.length - k;

        while (resIdx != k) {
            
            int[] candidate = pq.poll();
            
            if (start <= candidate[1] && candidate[1] <= end) {
                result[resIdx++] = candidate[0];
                start = candidate[1] + 1;
                end++;
                if (end < nums.length) {
                    pq.offer(new int[]{nums[end], end});
                }
            }
        }
        return result;
    }
}
```
