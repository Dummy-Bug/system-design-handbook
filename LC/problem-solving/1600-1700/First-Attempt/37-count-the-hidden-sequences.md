# 37 — Count the Hidden Sequences

- **Link:** https://leetcode.com/problems/count-the-hidden-sequences/ (LC 2145)
- **Dealt:** 2026-11-18 morning, eighth problem after the restart
- **Rating / slot:** 1614 · Biweekly Contest 70 Q2 · AR 56.8%
- **Result:** 🔴 **Hints, then taught; WA then AC, about 116 min.** Gave up at minute 31 with the key observation already found. Read all four LeetCode hints at minutes 35-39, which state the formula, and could not follow them. Derived both ends on example 1 and generalised them from Claude's questions. The overflow edge case came out of Step 3 after a prompt to push n to its extreme. One WA, min and max not seeded with the starting 0, explained by Claude.
- **Bucket (revealed post-solve):** **Prefix Sum.**
- **Cold re-solve:** ⏳ owed, from a blank editor.

## Timeline

| Time | Min | What happened |
|---|---|---|
| 06:10 | 0 | Started reading |
| 06:19 | 9 | Felt tough. Started by turning the input into ranges, like the earlier problems |
| 06:25 | 15 | Dropped the ranges: the element to choose depends on the one chosen before it |
| 06:27 | 17 | Pick and skip would work, but the worst case is worse than n² |
| 06:30 | 20 | On example 1, chained the equations x2 − x1 = 1, x3 − x2 = −3, x4 − x3 = 4 into x4 − x1 = 2 |
| 06:37 | 27 | Dropped the chained equation as telling nothing |
| 06:40 | 30 | Cap. Observation: once the number at index 0 is chosen, every other number is fixed by the equations, no choice left |
| 06:41 | 31 | Gave up |
| 06:45 | 35 | Opened LeetCode's hints |
| 06:47 | 37 | Hint 1 (fix the first element to any x, the differences give the rest) matched the minute-30 observation. Had dropped it because up to 10⁵ starting values each need a full check, about n² |
| 06:49 | 39 | Read hints 2-4 (the spread max − min does not depend on x; answer is (upper − lower + 1) − spread), could not follow them |
| ~06:50 | 40 | Claude: build the sequence from start 0 on example 1, then from start 1 and 5, and compare |
| 06:59 | 49 | Worked it on example 1: the min must be lifted up to lower, so the smallest start is 3; starting at 6 the max is 8, 2 too many, so the largest start is 6 − 2 = 4; 4 − 3 + 1 = 2. Check → correct |
| 07:08 | 58 | Generalised: start from lower and from upper, ends [lower + (lower − minValue), upper + (maxValue − upper)]. Check → partly, the right end has the wrong sign. Fixed to upper − (maxValue − upper) → correct |
| 07:09 | 59 | Count = right − left + 1, and 0 when left > right → correct |
| 07:10 | 60 | Asked why starting from lower only breaks the min. Claude: it can break the max too, each run is used for one bound only, and a broken max shows up as left > right |
| ~07:12 | 62 | Asked about the start-from-0 version; saw that raising the start by k lifts every value by k |
| 07:17 | 67 | Step 2 on example 2 from start 0: both min and max already in range, confused. Claude: start 0 is one of the valid starts, the formulas need nothing out of range |
| 07:21 | 71 | Got left = −3 and right = 0 whatever start was tried, could not see why. Claude rebuilt it on differences [2] with a table of starts 0, 1, 2, 10, all giving left = 0 |
| ~07:30 | 80 | Own framing: the true start is s, the guess is start, so the guess is lower, higher or equal, and every number moves with it. Check → correct. Then: the hidden sequence has its min at lower, so lower − min is how far off the guess is; same for upper − max; that gives the range for s. Check → correct |
| ~07:35 | 85 | Step 3: three cases with n = 1 (below). Claude: n not pushed to its extreme yet |
| ~07:40 | 90 | Fourth case, all differences 10⁵ with n = 10⁵, answer 0; asked what a running sum is and why it is needed. Saw that the sequence reaches 10⁵ × 10⁵ = 10¹⁰, past the int limit |
| ~07:45 | 95 | Asked whether this is a fit at all |
| ~08:00 | 110 | Coded it with long. **WA** on 73 / 86: differences [−40], lower −46, upper 53, output 100, expected 60 |
| ~08:02 | 112 | Claude explained the bug: min and max never saw the starting 0. Fixed by seeding both with 0 |
| ~08:06 | 116 | **AC** |

## Stuck note

1. **Understood:** each difference ties a number to the one before it, and every number has to stay inside [lower, upper].
2. **Tried:** a range per element; pick and skip (worse than n²); chaining the equations into x4 − x1 = 2.
3. **Stuck at:** had the observation that the first number fixes all the others, but saw it as 10⁵ starts each checked in full, not as one sequence that just shifts.

## Approach 1 (ours) — two runs, from lower and from upper

1. Build the sequence starting at lower and take its smallest value, minValue. Lifting the start by lower − minValue brings the min up to lower, so the smallest valid start is **left = lower + (lower − minValue)**.
2. Build the sequence starting at upper and take its largest value, maxValue. Lowering the start by maxValue − upper brings the max down to upper, so the largest valid start is **right = upper − (maxValue − upper)**.
3. Answer: **right − left + 1**, or **0 when left > right**.

Why each run looks at only one bound: the run from lower may break the max too, and the run from upper may break the min too. Each run answers one question only, and a valid start must pass both, so the valid starts are the overlap [left, right]. A broken max in the run from lower shows up as left > right, which the 0 case covers. The start is itself in the sequence, so minValue ≤ lower and the left end never drops below lower.

Example 1, differences [1, −3, 4], lower = 1, upper = 6: from 1 the sequence is [1, 2, −1, 3], minValue = −1, left = 1 + 2 = 3. From 6 it is [6, 7, 4, 8], maxValue = 8, right = 6 − 2 = 4. Answer 4 − 3 + 1 = 2.

Small check where the max also breaks in the run from lower: differences [10], lower = 0, upper = 5. From 0: [0, 10], left = 0. From 5: [5, 15], right = 5 − 10 = −5. left > right, answer 0.

## Approach 2 — one run from 0

Raising the start by k lifts every value of the sequence by k, so the shape never changes, only its position.

1. Build the sequence from start 0 with a running sum; keep its smallest value mn and largest value mx (0 itself counts).
2. A start s gives min s + mn and max s + mx. So s + mn ≥ lower gives **s ≥ lower − mn**, and s + mx ≤ upper gives **s ≤ upper − mx**.
3. Answer: (upper − mx) − (lower − mn) + 1 = **(upper − lower + 1) − (mx − mn)**, or 0 if that is negative.

This is hint 4. mx − mn is the spread of the sequence, the same for every start (hint 2). It is the same formula as approach 1, since the run from lower has minValue = lower + mn, so lower + (lower − minValue) = lower − mn. The gain is one pass and no stored sequence: a running sum, a running min and a running max.

Example 1: from 0 the sequence is [0, 1, −2, 2], mn = −2, mx = 2. left = 1 + 2 = 3, right = 6 − 2 = 4. Answer (6 − 1 + 1) − 4 = 2.

Both approaches checked against a brute force over every start in [lower, upper]: 2, 4, 0 on the three examples, 0 on the [10] case, 0 mismatches over 20,000 random small inputs.

**What was missing at minute 30:** the observation was there, but the next step was to ask what changing the start does to the whole sequence. It shifts it without changing its shape, so one sequence and two bounds decide everything.

**Reflex:** an array built from its differences plus bounds on every value → build it once from 0, keep the min and max, and the valid starts are one interval [lower − min, upper − max].

## Why any start gives the same answer

The sticking point at minutes 67-80. The true smallest valid start is s and the guess is start. If the guess is off by d, every number of the sequence is off by d, the min included. The true sequence has its min exactly at lower, so lower − min is exactly how far off the guess is, and start + (lower − min) always lands on s.

| start | sequence for differences [2] | min | lower − min (lower = 0) | start + (lower − min) |
|---|---|---|---|---|
| 0 | [0, 2] | 0 | 0 | 0 |
| 1 | [1, 3] | 1 | −1 | 0 |
| 2 | [2, 4] | 2 | −2 | 0 |
| 10 | [10, 12] | 10 | −10 | 0 |

## Step 2

Example 2, differences [3, −4, 5, 1, −2], lower −4, upper 5, from start 0: [0, 3, −1, 4, 5, 3], min −1, max 5. left = −4 − (−1) = −3, right = 5 − 5 = 0, count 0 − (−3) + 1 = 4. Expected 4.

## Edge cases (Step 3)

| Name | Input | Expected | What it tests |
|---|---|---|---|
| No room | [1], lower = upper = 0 | 0 | the spread does not fit in the bounds |
| Exact fit | [1], lower 0, upper 1 | 1 | spread equals the width, one start |
| Largest single difference | [10⁵], lower 0, upper 10⁵ | 1 | spread 10⁵ in a width of 10⁵ + 1 |
| Overflow | 10⁵ differences all 10⁵, lower 1, upper 10⁵ | 0 | the sequence reaches 10⁵ × 10⁵ = 10¹⁰, past the int limit of 2,147,483,647 |

Measured in Java, adding 10⁵ a total of 10⁵ times: int ends at 1410065408, wrapped around; long ends at 10000000000.

## First submission (WA)

**WA-cause [impl-bug]:** min and max started at `Long.MAX_VALUE` and `Long.MIN_VALUE` and were updated only after each difference was added, so the starting 0, the first element of the sequence, was never counted. On [−40] the sequence is [0, −40], but the loop saw only −40, so max came out −40 instead of 0, right = 53 + 40 = 93 instead of 53, and the answer 100 instead of 60. The three examples passed because their sequences go both above and below 0, so 0 was never the min or the max.

**Rule:** an accumulator starts at the first element. Same lesson as Weekly 528 Q1. Here the first element is the 0 the sequence is built from.

```java
class Solution {
    public int numberOfArrays(int[] differences, int lower, int upper) {
        
        long min = Long.MAX_VALUE;
        long max = Long.MIN_VALUE;

        long prev = 0l;

        for (int d : differences){
            prev = d + prev;
            min = Math.min(min , prev);
            max = Math.max(max , prev);
        }

        long allowableMin = (long)lower - min;
        long allowableMax = (long)upper - max;

        if (allowableMax < allowableMin) return 0;

        return (int)(allowableMax - allowableMin + 1);
    }
}
```

## Final code (AC)

```java
class Solution {
    public int numberOfArrays(int[] differences, int lower, int upper) {
        
        long min = 0;
        long max = 0;

        long prev = 0l;

        for (int d : differences){
            prev = d + prev;
            min = Math.min(min , prev);
            max = Math.max(max , prev);
        }

        long allowableMin = (long)lower - min;
        long allowableMax = (long)upper - max;

        if (allowableMax < allowableMin) return 0;

        return (int)(allowableMax - allowableMin + 1);
    }
}
```

Checked by running: 60 on the failing case, 2, 4, 0 on the examples, 0, 1, 1 on the first three edge cases, 0 on the overflow case in 3 ms, 0 mismatches against a brute force over 20,000 random small inputs.
