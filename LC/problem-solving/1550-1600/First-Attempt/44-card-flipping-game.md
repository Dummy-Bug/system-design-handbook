# 44 — Card Flipping Game

- **Link:** https://leetcode.com/problems/card-flipping-game/ (LC 822, rating 1594, AR 50.4%)
- **Format:** single timed problem under the 2026-11-22 format (15-minute target, 30-minute cap), unseen. Dealt from `_Blind-Queue.md` #1.
- **Bucket (revealed after the solve):** hash table: a value is ruled out only when some card shows it on both sides.
- **Timer:** 2026-11-25, 06:50.
- **AC:** 07:38, 48 minutes: 35 to the idea, 12 coding.
- **Result:** clean first-submission AC, self-derived, over the 30-minute cap. The working idea came at 35 minutes, so the cap did not stop the solve. Does not count toward coverage: hash table / counting stays at 0 of 2.

**Rewritten question:** a number can be the answer unless some card has it on both sides; return the smallest number on any card that no card has on both sides.

## The problem

Each card has a number on the front and the back, and any cards can be flipped. A number is good when it is on the back of some card and on the front of no card after flipping. Return the smallest good number, or 0. `1 <= n <= 1000`, values up to 2000.

## Timeline

| Time  | What                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 06:50 | Timer started.                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 07:15 | First approach: swap each pair so the back array holds the smaller number, put the front numbers in a HashSet, and scan the back array for numbers not in the set; the smallest of those is the answer. Fails on fronts [1,2,1], backs [1,2,3]: after the greedy swap it becomes [1,2,3] and [1,2,2], so 3 is missed unless the back array gets a HashSet too. Feels ugly; looking for something simpler.                                                     |
| 07:15 | Asked for 5 more minutes to think of a non-greedy way.                                                                                                                                                                                                                                                                                                                                                                                                        |
| 07:25 | Insight: a front value can fail only if some card has that same value on its back too; otherwise it can always be flipped to the back. This holds for every occurrence of the value. Approach: a map from value to true or false; for each card, if its two sides differ the value stays true unless already false, if they are the same it becomes false. Check the mirror value in the same pass so it is one pass. Asked for a correctness check: correct. |
| 07:26 | Starting to code, with a working idea in hand after the 30-minute cap. The user says doing Step 3 (edge cases) this time is what showed the first approach was wrong, since it passed the example test cases.                                                                                                                                                                                                                                                 |
| 07:38 | AC on the first submission.                                                                                                                                                                                                                                                                                                                                                                                                                                   |

## The accepted code

```java
class Solution {
    public int flipgame(int[] fronts, int[] backs) {

        Map<Integer, Boolean> map = new HashMap<>();
        int n = fronts.length;

        for (int i = 0; i < n; i++) {

            if (fronts[i] == backs[i]){
                map.put(fronts[i] , false);
                continue;
            }

            if (!map.containsKey(fronts[i])){
                map.put(fronts[i] , true);
            }
            if (!map.containsKey(backs[i])){
                map.put(backs[i] , true);
            }

        }

        int ans = Integer.MAX_VALUE;

        for (Map.Entry<Integer,Boolean> entry : map.entrySet()){

            int key = entry.getKey();
            boolean value = entry.getValue();

            if (value){
                ans = Math.min(ans , key);
            }
        }
        if (ans == Integer.MAX_VALUE) return 0;
        return ans;
    }
}
```

## Debrief

- **Step 3 caught the wrong first approach.** The greedy swap passed the examples and failed on fronts [1,2,1], backs [1,2,3], found by trying edge cases before submitting.
- **The time went to the idea, not the code:** 35 minutes to the idea, 12 coding. This is the opposite of the earlier logs, where coding took as long as the idea or longer in 7 of 8.
- **The shorter version:** the editorial puts only the both-sides values in a HashSet, then takes the smallest front or back value not in that set. With a set of bad values, no true or false map and no containsKey checks are needed, because a value counts as good just by not being in the set.
- **What blocked the set version:** the user tried a bad set too, but in one pass, and could not keep the minimum right. In one pass a value can turn bad after it was already taken as the minimum, because its both-sides card can come later. Two passes fix that: first learn every bad value, then pick the minimum. When a decision depends on facts the rest of the array can still change, collect first and decide in a second pass.

