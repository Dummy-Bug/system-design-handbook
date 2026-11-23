# 42 — Count Number of Trapezoids I

- **Link:** https://leetcode.com/problems/count-number-of-trapezoids-i/ (LC 3623, rating 1580, AR 48.1%)
- **Format:** single timed problem under the 2026-11-22 format (15-minute target, 30-minute cap), unseen.
- **Bucket (revealed after the solve):** math / counting: count points per y with a hash map, then count pairs of segments across two different levels with a running sum. The editorial calls it enumeration.
- **Dealt:** 2026-11-22, about 21:50. The user first asked for a different problem because it looked math-heavy, then came back to it after seeing that math is about 23% of 1500-1599 with no solves yet.
- **Timer:** 21:53.
- **Result:** editorial. One WA (204 of 555), then the step-by-step explanation after the cap. The fixed code was checked locally and deliberately not submitted: it gets submitted at the cold re-solve, once the solution has been forgotten. Does not count toward coverage: math stays at 0 of 2.
- **Cold re-solve owed:** 2026-11-23 or later, from a blank editor, starting from the rewritten question below.

**Rewritten question:** for every pair of different y levels, multiply their segment counts, and add all of those up.

## The problem

Given distinct points, count the sets of four points that form a horizontal trapezoid: a convex quadrilateral with at least one pair of horizontal sides. Return the count modulo 10^9 + 7. `4 <= points.length <= 10^5`, coordinates up to 10^8 in absolute value.

## Timeline

| Time  |     At | What                                                                                                                                                 |
| ----- | -----: | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| 21:53 |  0 min | Timer started.                                                                                                                                       |
| 22:04 | 11 min | Idea: count the points on each y in a map and add up each level's contribution, since only the horizontal lines matter.                              |
| 22:05 | 12 min | Asked whether the idea was correct; the one-word answer was yes. Started coding.                                                                     |
| 22:27 | 33 min | Pasted the WA (204 of 555) and said there was no next move. The exact submit time was not logged; it was before this.                                |
| 22:27 | 33 min | Past the cap. Step 1 given on the failing case; the user found that example unhelpful, was close to burnout, and asked to build it step by step.     |
| 22:30 | 36 min | Claude sent all five steps in one message instead of one; the user flagged it and the explanation restarted at step 3, one step per message.         |
| 22:33 | 40 min | Step 3 clicked on a three-level example with 3, 1 and 3 segments: 15 by pairs of levels against 9 by the product. Step 4, the running sum, followed. |
| 22:38 | 45 min | After step 5 (sizes and the mod), pasted the fixed loop. Checked locally; not submitted.                                                             |

The user had thought of adding something instead of multiplying, but could not make it concrete.

## The WA

**WA-cause [read-error] [untraced-submit]:** a trapezoid uses exactly two levels, but the code multiplied the segment counts of every level together, which counts one segment from all levels at once. Failing case `[[-73,-72],[-1,-56],[-92,30],[-57,-89],[-19,-89],[-35,30],[64,-72]]`: three levels with one segment each, got 1, expected 3.

Both examples have only two levels, and with two levels the product and the sum over pairs are the same number, so the WA code passes both (run below). The same as mock 4: the given examples could not catch the bug, and a Step 2 trace on a richer case, here three levels with different counts, was what was needed.

| Input                        | WA code | Correct |
| ---------------------------- | ------: | ------: |
| example 1                    |       3 |       3 |
| example 2                    |       1 |       1 |
| failing case                 |       1 |       3 |
| three levels, 3, 1, 3 points |       9 |      15 |

The three-level input is `[[0,0],[1,0],[2,0],[0,1],[1,1],[0,2],[1,2],[2,2]]`; 15 was also checked by testing every group of four points directly.

First attempt (WA):

```java
class Solution {
    public int countTrapezoids(int[][] points) {
        
        int MOD = 1000000007;
        int twoLines = 0;
        long ans = 1l;

        Map<Integer,Integer> map = new HashMap<>();

        for (int [] point : points){
            int y = point[1];
            map.put(y , map.getOrDefault(y , 0) + 1);
        }

        for (Map.Entry<Integer,Integer> entry : map.entrySet()){
            int value = entry.getValue();
            if (value > 1){
                twoLines++;
                long contribution = (( (long)value*(value - 1) )/2)%MOD;
                ans = (ans*contribution) % MOD;
            }
        }
        if (twoLines < 2) return 0;
        return (int)ans;

    }
}
```

## The approach, in the steps it was explained

1. Count the points on each y.
2. A level with v points has v·(v − 1)/2 segments.
3. A trapezoid is one segment from one level and one from a different level, so the answer is segments(A) × segments(B) summed over every pair of levels.
4. Looping over pairs of levels is up to about 10^9 pairs, so walk the levels once with `sum` holding the segments seen so far: each new level adds `seg × sum`, then adds its `seg` into `sum`.
5. One level can hold 4,999,950,000 segments, more than an int holds, so `seg`, `sum` and `ans` are long; the largest `seg × sum` is about 1.56 × 10^18, inside a long. Take the mod on the answer each time.

Step 4 on the three-level example:

| Level | seg | adds seg × sum | ans | sum after |
| ----- | --: | -------------- | --: | --------: |
| y = 2 |   3 | 3 × 0 = 0      |   0 |         3 |
| y = 1 |   1 | 1 × 3 = 3      |   3 |         4 |
| y = 0 |   3 | 3 × 4 = 12     |  15 |         7 |

O(n) time and space.

## Fixed code, not submitted

The user pasted only the new loop. This is the first attempt with that loop in place and `ans` starting at 0; starting it at 1, as in the first attempt, makes every answer 1 too high.

```java
class Solution {
    public int countTrapezoids(int[][] points) {
        
        int MOD = 1000000007;
        int twoLines = 0;
        long ans = 0l;

        Map<Integer,Integer> map = new HashMap<>();

        for (int [] point : points){
            int y = point[1];
            map.put(y , map.getOrDefault(y , 0) + 1);
        }

        long segments = 0;
        for (Map.Entry<Integer,Integer> entry : map.entrySet()){
            int value = entry.getValue();
            if (value > 1){
                twoLines++;
                long contribution = (( (long)value*(value - 1) )/2)%MOD;
                ans = (ans + (contribution*segments) % MOD) % MOD;
                segments = (segments + contribution)%MOD;
            }
        }
        if (twoLines < 2) return 0;
        return (int)ans;

    }
}
```

Run: 3, 1, 3 and 15 on the four inputs above, the same output as the editorial's method on 20,000 random inputs, and the same answer on 100,000 points split over two levels. With `ans` starting at 1 it gave 4, 2, 4 and 16 and disagreed on 18,632 of the 20,000.
