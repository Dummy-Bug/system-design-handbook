# Weekly Contest 529

**Date:** 2026-11-22 (Sun), 08:00 IST, logged 08:00–09:05.
**Result:** rank 7457 of 22,942 (top 32.5%), score 8, finish time 01:00:21.
**Ratings:** no zerotrac rating yet for any of the four; titles and slugs were not captured, so the problems are named by their function.

| Q   | Function              | Result          | Note                                                 |
| --- | --------------------- | --------------- | ---------------------------------------------------- |
| Q1  | countDominantElements | WA then AC (+5) | AC at 00:11:05; the ends used strict > instead of >= |
| Q2  | minCost               | AC              | AC at 00:55:21, first submission, about 44 minutes   |
| Q3  | signal activation     | not attempted   | read, felt way above current level                   |
| Q4  | not opened            | not attempted   |                                                      |

**Two solved.** Left with 26 minutes on the clock, heading towards burnout. Q2 took the soul out of me, in the user's words. Without the Q1 WA the finish would have been 00:55:21 instead of 01:00:21.

---

## Q1 — countDominantElements (WA then AC)

An element counts when it is at least the average of its existing neighbours; an end element has only one neighbour.

**WA-cause [impl-bug]:** the middle used `>=`, but the two ends and the `n == 2` case used strict `>`, so an end equal to its neighbour was not counted. `[3,3]` returned 0 instead of 2.

First attempt (WA):

```java
class Solution {
    public int countDominantElements(int[] nums) {

        int n = nums.length;
        if (n == 1) return 1;

        if (n == 2){
            if (nums[0] > nums[1]) return 1;
            else if (nums[1] > nums[0]) return 1;
            else return 0;
        }

        int count = 0;
        if (nums[0] > nums[1]) count++;
        if (nums[n - 1] > nums[n - 2]) count++;

        for (int i = 1; i < n - 1; i++){

            double average = ( (double)nums[i - 1] + nums[i + 1] )/2.0;

            if ( (double)nums[i] >= average ){
                count++;
            }
        }
        return count;

    }
}
```

Second attempt (AC):

```java
class Solution {
    public int countDominantElements(int[] nums) {
        int n = nums.length;
        if (n == 1) return 1;
        if (n == 2){
            if (nums[0] == nums[1]) return 2;
            return 1;
        }
        int count = 0;
        if (nums[0] >= nums[1]) count++;
        if (nums[n - 1] >= nums[n - 2]) count++;
        for (int i = 1; i < n - 1; i++){
            double average = ( (double)nums[i - 1] + nums[i + 1] )/2.0;
            if ( (double)nums[i] >= average ){
                count++;
            }
        }
        return count;
    }
}
```

**One rule instead of four cases:** sum the neighbours that exist and count them; the element counts when `nums[i] * cnt >= sum`. A lone element has `cnt = 0`, so `0 >= 0` holds. No doubles, no special cases. Run against the AC version: same output on the examples (1, 2, 1) and on 200,000 random arrays.

```java
class Solution {
    public int countDominantElements(int[] nums) {
        int n = nums.length, count = 0;
        for (int i = 0; i < n; i++) {
            int sum = 0, cnt = 0;
            if (i > 0)     { sum += nums[i - 1]; cnt++; }
            if (i < n - 1) { sum += nums[i + 1]; cnt++; }
            if (nums[i] * cnt >= sum) count++;
        }
        return count;
    }
}
```

**Habit:** before submitting, test equal values at each boundary, such as `[3,3]`.

---

## Q2 — minCost (AC first submission)

Harder than a usual Q2. The moves: one final value taken from a middle index is enough; the cost depends on position times value; for a run of equal values, the prefix cost uses the left end of the run and the suffix cost the right end, and a side is free when the run touches that edge; the cost needs `long`.

AC code, as submitted (the debug print was left in):

```java
class Solution {
    public long minCost(int[] nums) {

        long ans = Long.MAX_VALUE;

        int n = nums.length;
        int i = 1;
        while( i < n - 1){

            long prefixCost = 0;

            int left = i;
            while(left > 0 && nums[left] == nums[left - 1]){
                left--;
            }
            if (left != 0){
                prefixCost = (long)nums[i]*i;
            }

            long suffixCost = 0;

            int right = i;
            while(right < n -1 && nums[right] == nums[right + 1]){
                right++;
            }
            if (right != n - 1){
                suffixCost = ((long)n - right - 1)*nums[right];
                System.out.println(right + " " + nums[right] + " " + suffixCost);
            }

            ans = Math.min(ans , prefixCost + suffixCost);
            i = right + 1;
        }
        return ans;
    }
}
```

---

## Q3 — signal activation in a directed graph (not attempted)

Directed graph with delays; node 0 is active at time 0; a node activates at the earliest time signals have arrived from at least `requiredSignals[i]` distinct incoming neighbours, then sends one signal along each outgoing edge. Return each node's activation time, or -1. `n ≤ 10⁵`, `edges ≤ 10⁵`, delay up to 10⁹.

Read and dropped: felt way above current level. **Upsolve:** waits for its zerotrac rating; skip if 1600 or above.
