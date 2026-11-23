# 38 — Maximize Greatness of an Array (re-solve)

- **Link:** https://leetcode.com/problems/maximize-greatness-of-an-array/ (LC 2592, rating 1569, AR 61.7%)
- **Format:** single timed problem, old re-solve under the 2026-11-22 format (15-minute target, 30-minute cap). First attempt: `First-Attempt/38-maximize-greatness-of-an-array.md`, 2026-06-09.
- **Bucket:** greedy / two pointers: sort, then match each number with the smallest number that beats it.
- **Timer:** 2026-11-23, 06:09.
- **AC:** 06:25, 16 minutes.
- **Result:** clean first-submission AC, self-derived. The only exchange during the solve was a yes or no correctness check on the idea. Counts toward coverage under greedy, since the code is a heap match with no two pointers: greedy 2 of 2. Re-solves have counted under the 30-minute rule since 2026-11-23.

| Attempt       | Time       | WAs | Help                       | Approach                                                              |
| ------------- | ---------- | --: | -------------------------- | --------------------------------------------------------------------- |
| 1, 2026-06-09 | not logged |   1 | Claude diagnosed and fixed | group by group from the top, `min(group size, numbers below)`         |
| 2, 2026-11-23 | 16 min     |   0 | none                       | min-heap of all numbers; each sorted number polls its smallest beater |

## The problem

Permute `nums` into `perm`. Greatness is the number of indices with `perm[i] > nums[i]`. Return the largest greatness over all permutations.

## How it was solved

| Time  |     At | What                                                                                                      |
| ----- | -----: | --------------------------------------------------------------------------------------------------------- |
| 06:09 |  0 min | Timer started.                                                                                            |
| 06:18 |  9 min | Idea: a priority queue; for each `nums[i]`, find the number greater than it that is as small as possible. |
| 06:18 |  9 min | Asked whether the idea was correct; the one-word answer was yes.                                          |
| 06:25 | 16 min | AC on the first submission.                                                                               |

## Why June failed and today did not

June counted; today matched. The June code walked the sorted array one group of equal values at a time and added `min(group size, numbers below the group)`, so every group was measured against the full set of smaller numbers, even when a group above had already used them. Today each number takes its smallest beater out of the heap with `poll()`, so a number is used once and nothing is counted twice.

On `[1,1,2,3,3,3]`, where the answer is 3:

| Approach           | What happens                                                                       | Result |
| ------------------ | ---------------------------------------------------------------------------------- | -----: |
| June, by groups    | the three 3s beat min(3, 3) = 3, using 1, 1 and 2; the 2 beats min(1, 2) = 1 again |      4 |
| Today, by matching | `poll()` removes each used number                                                  |      3 |

Run: the June code gives 4 here and 7 on the June failing case `[42,8,75,28,35,21,13,21]`, where 6 is expected, and still passes both examples (4 and 3).

## AC code

```java
class Solution {
    public int maximizeGreatness(int[] nums) {
        
        PriorityQueue<Integer> pq = new PriorityQueue<>();


        for (int i = 0; i < nums.length; i++){
            pq.offer(nums[i]);
        }

        Arrays.sort(nums);

        int ans = 0;
        for (int i = 0; i < nums.length; i++){

            while(!pq.isEmpty()){
                int num = pq.poll();
                if (num > nums[i]){
                    ans += 1;
                    break;
                }
            }
            if (pq.isEmpty()) return ans;
        }
        return ans;
    }
}
```

## The one move: the heap is the sorted array again

The heap holds the same numbers as the sorted array, and polling it gives them in the same order as walking an index along `nums`. So a second index does the heap's job: `i` is the smallest number not yet beaten, `j` is the next candidate, and `i` moves only when `nums[j] > nums[i]`. This is the over-modelling family in `extendedClaude.md`: a structure where an index is enough. Both are O(n log n); the gain is 6 lines instead of 15, and coding time is the measured bottleneck. It is the same code June ended on, after Claude's fix.

```java
class Solution {
    public int maximizeGreatness(int[] nums) {
        Arrays.sort(nums);
        int i = 0;
        for (int j = 0; j < nums.length; j++) {
            if (nums[j] > nums[i]) i++;
        }
        return i;
    }
}
```

Run: 4 and 3 on the two examples, and the same output as the AC code on 200,000 random inputs.
