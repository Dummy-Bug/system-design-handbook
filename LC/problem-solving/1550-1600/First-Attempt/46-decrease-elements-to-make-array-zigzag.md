# 46 — Decrease Elements To Make Array Zigzag

- **Link:** https://leetcode.com/problems/decrease-elements-to-make-array-zigzag/ (LC 1144, rating 1559)
- **Format:** single timed problem under the 2026-11-22 format (15-minute target, 30-minute cap), unseen. Dealt from `_Blind-Queue.md` #5.
- **Bucket (revealed after the solve):** enumeration: try the even indexes as peaks, then the odd ones, and take the cheaper.
- **Timer:** 2026-11-26, 08:07, paused 08:18-08:26, stopped at 08:58 with 43 minutes on the clock; resumed 2026-11-27, 07:55.
- **AC:** 2026-11-27, 08:06, 54 minutes: 17 to the idea, 37 coding.
- **Result:** AC on the first submission, self-derived, over the 30-minute cap. The first code attempt failed the example test cases when run and was not submitted. The working idea came at 17 minutes, so the cap did not stop the solve. Does not count toward coverage: enumeration stays at 0.

**Rewritten question:** only the valleys can move, so for each choice of valley indexes (all odd or all even), push every valley to one below its smaller neighbour, and return the cheaper choice.

## The problem

One move decreases any element by 1. An array is zigzag when every even-index element is greater than its neighbours, or every odd-index element is. Return the fewest moves that make `nums` zigzag. `1 <= nums.length <= 1000`, `1 <= nums[i] <= 1000`.

## Timeline

| Time  | What                                                                                                                                                                                                                         |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 08:07 | Timer started.                                                                                                                                                                                                               |
| 08:10 | Idea: two passes. First pass, make each even-index element the smallest number bigger than its odd neighbours; second pass, the same with the odd indexes. Works on the example test cases. Moving on to Step 3, edge cases. |
| 08:13 | Observed: an element can only be decreased, never increased, and the condition reads A[0] > A[1] < A[2]. So to make an even-index element greater than its neighbours, the odd neighbours have to be decreased instead.      |
| 08:15 | Step 3 found a case that breaks the earlier approach: [1,2,1], where the answer should be 2 but the earlier approach would give 4. Thinking further about whether there is one more twist.                                   |
| 08:16 | Correction: 2 is the answer for the even-index pass on [1,2,1]; the odd-index pass gives 0, so the overall answer is 0.                                                                                                      |
| 08:16 | Next check: whether increasing the current element gives the same result as decreasing its neighbours.                                                                                                                       |
| 08:18 | Timer paused.                                                                                                                                                                                                                |
| 08:26 | Timer resumed, 11 minutes on the clock.                                                                                                                                                                                      |
| 08:32 | Steps 2 and 3 done in the notebook, approach holds. Starting to code.                                                                                                                                                        |
| 08:57 | First code attempt, below: fails the example test cases. Confused by the arithmetic of how much to decrease.                                                                                                                 |
| 08:58 | Timer stopped, to finish later. Asked for a correctness check on the approach, with the arithmetic of the decrease suspected wrong: correct.                                                                                 |
| 07:55 | 2026-11-27: timer resumed, 43 minutes on the clock from 2026-11-26.                                                                                                                                                          |
| 08:06 | 2026-11-27: fixed the decrease to nums[i] minus the neighbour plus 1. AC on the first submission.                                                                                                                            |
| 08:51 | Follow-up: took the shorter version step by step (9 steps), then started coding it from memory without looking.                                                                                                              |
| 08:55 | Follow-up recode from memory: right logic, but cost sized new int[n] instead of new int[2], which crashes on a one-element array when cost[1] is read. Checked by running.                                                   |
| 08:57 | Fixed cost to new int[2]; the shorter version is AC.                                                                                                                                                                         |

## First code attempt (failed the examples when run)

The decrease subtracted the neighbour plus 1, `even[i] - (even[i - 1] + 1)`, where the amount needed is the gap plus 1, `even[i] - even[i - 1] + 1`.

```java
class Solution {
    public int movesToMakeZigzag(int[] nums) {

        int n = nums.length;

        int [] even = new int[n];
        int [] odd = new int[n];

        for (int i = 0; i < n; i++){
            odd[i] = nums[i];
            even[i] = nums[i];
        }

        int ans1 = 0;

        for (int i = 1; i < n; i += 2){

            if (even[i - 1] <= even[i]){
                even[i] = even[i] - (even[i - 1] + 1);
                ans1 += even[i - 1] + 1;
            }
            if (i != n - 1 && even[i + 1] <= even[i]){
                even[i] = even[i] - (even[i + 1] + 1);
                ans1 += even[i + 1] + 1;
            }
        }

        int ans2 = 0;

        for (int i = 0; i < n; i+=2){

            if (i != 0 && odd[i - 1] <= odd[i]){
                odd[i] = odd[i] - (odd[i - 1] + 1);
                ans2 += odd[i - 1] + 1;
            }
            if (i != n- 1 && odd[i + 1] <= odd[i]){
                odd[i] = odd[i] - (odd[i + 1] + 1);
                ans2 += odd[i + 1] + 1;
            }
        }
        return Math.min(ans1 , ans2);
    }

}
```

## The accepted code

```java
class Solution {
    public int movesToMakeZigzag(int[] nums) {

        int n = nums.length;

        int [] even = new int[n];
        int [] odd = new int[n];

        for (int i = 0; i < n; i++){
            odd[i] = nums[i];
            even[i] = nums[i];
        }

        int ans1 = 0;

        for (int i = 1; i < n; i += 2){

            if (even[i - 1] <= even[i]){
                int d = even[i] - even[i - 1] + 1;
                ans1 += d;
                even[i] = even[i] - d;

            }
            if (i != n - 1 && even[i + 1] <= even[i]){
                int d = even[i] - even[i + 1] + 1;
                ans1 += d;
                even[i] = even[i] - d;
            }
        }

        int ans2 = 0;

        for (int i = 0; i < n; i+=2){

            if (i != 0 && odd[i - 1] <= odd[i]){
                int d = odd[i] - odd[i - 1] + 1;
                ans2 += d;
                odd[i] = odd[i] - d;
            }
            if (i != n- 1 && odd[i + 1] <= odd[i]){
                int d = odd[i] - odd[i + 1] + 1;
                ans2 += d;
                odd[i] = odd[i] - d;
            }
        }
        return Math.min(ans1 , ans2);
    }

}
```

## Debrief

- **The idea was quick, the arithmetic was not:** 17 minutes to the idea, 37 coding. The 08:13 observation carried it: only decreases are allowed, so the peaks never move and only the valleys are pushed down.
- **The arithmetic:** to get x below a neighbour y, x has to reach y − 1, which takes x − y + 1 moves. The first attempt subtracted y + 1. Working one number through by hand, x = 6 and y = 2 needs 5 moves, would have caught it.
- **The copies are not needed.** Each pass decreases only one parity, and the neighbours it compares against are the other parity, which that pass never changes. So both passes can read straight from `nums`.
- **The shorter version:** the two checks in a row bring an element to one below its smaller neighbour, so its cost is max(0, nums[i] − min(left, right) + 1). One loop sums that cost into the bucket for its own parity, and the answer is the smaller bucket:

```java
class Solution {
    public int movesToMakeZigzag(int[] nums) {
        int n = nums.length;
        int[] cost = new int[2];
        for (int i = 0; i < n; i++) {
            int left = i > 0 ? nums[i - 1] : Integer.MAX_VALUE;
            int right = i < n - 1 ? nums[i + 1] : Integer.MAX_VALUE;
            cost[i % 2] += Math.max(0, nums[i] - Math.min(left, right) + 1);
        }
        return Math.min(cost[0], cost[1]);
    }
}
```

Checked by running: both the accepted code and the shorter version give 2 and 4 on the two LeetCode examples, and match a brute force that tries every decreased array on 5,000 random small cases, with no mismatch. The shorter version was not submitted to LeetCode.
