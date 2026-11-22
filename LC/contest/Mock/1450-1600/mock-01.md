# Mock Contest 1

**Date:** 2026-11-19 (Thu), 06:25–07:55 IST, 90 minutes, no AI, four unseen problems rated in rising order from 1479 to 1588.
**Why:** the band moved to 1500-1599 on 2026-11-18, after the profile check showed rating 1512 and Q2 solved in 4 of the last 8 contests. A mock contest copies contest conditions: one clock across four problems.

| Q | Problem | Started | Finished | Minutes | Result |
|---|---|---|---|---|---|
| Q1 | minimum-sum-of-mountain-triplets-ii | 06:25 | 06:43 | 18 | AC first submission |
| Q2 | minimum-deletions-to-make-array-beautiful | 06:44 | 07:04 | 20 | AC first submission |
| Q3 | climbing-stairs-ii | 07:05 | 07:25 | 20 | AC first submission |
| Q4 | minimum-operations-to-make-a-special-number | 07:25 | 07:49 | 24 | Not solved, contest ended at minute 84 |

**Three solved, no WA, each in 18-20 minutes.** All three count as wins under the 25-minute rule.

**Difficulty: MEDIUM.** By rating, the four average 1534 against a range midpoint of 1525; the hardest possible set would have been four problems near 1599 with acceptance rates in the 30s. By feel, it was split: Q1-Q3 were classics already known (prefix and suffix min, a greedy pair scan, climbing stairs with a twist), so they were quick recall; Q4 was a blank from the first read.

**Performance estimate, about 1728, weak evidence.** Elo gives a solve chance for each problem at a given player rating, and the chances add up to the expected number solved. 1728 is the rating at which 3 of these 4 is the expected result. It's one session, and it assumes each problem was as hard as its rating, which the three classics were not.

| Player rating | Q1 1479 | Q2 1510 | Q3 1560 | Q4 1588 | Expected solves |
|---|---|---|---|---|---|
| 1512 (current) | 55% | 50% | 43% | 39% | 1.87 |
| 1728 | 81% | 78% | 72% | 69% | 3.00 |

**Q4 at the stop:** tried counting the multiples of 25 for each digit length, but a count gives nothing to act on. Stuck on how to test divisibility by 25 when the number has up to 100 digits, too many for a long. Linked it to remove-k-digits, read months ago, since both delete digits from a string, but it felt like staring at an abyss. Upsolved on 2026-11-20 from step 1 of the explanation, logged under Upsolve below.

**Next mock:** pick from 1550-1650 and skip anything shaped like a well-known classic, so more of the four need a new idea.

---

## Q1 — Minimum Sum of Mountain Triplets II

**Link:** https://leetcode.com/problems/minimum-sum-of-mountain-triplets-ii/ (LC 2909, rating 1479)

AC on the first submission at contest minute 18. For each middle index, the best left partner is the smallest value before it and the best right partner is the smallest value after it: a running min from the left and a suffix min array from the right.

```java
class Solution {
    public int minimumSum(int[] nums) {
        
        int n = nums.length;

        if (n < 3) return -1;
        
        int [] rightMin = new int[nums.length];
        rightMin[n-1] = nums[n - 1];

        for (int i = n - 2; i >= 0; i--){
            rightMin[i] = Math.min(rightMin[i + 1] , nums[i]);
        }

        int minSum = Integer.MAX_VALUE;

        int minLeft = nums[0];

        for (int i = 1; i < n - 1; i++){

            if (minLeft < nums[i] && nums[i] > rightMin[i + 1]){
                minSum = Math.min(minSum , minLeft + nums[i] + rightMin[i + 1]);
            }
            minLeft = Math.min(minLeft , nums[i]);
        }
        if (minSum == Integer.MAX_VALUE) return -1;
        return minSum;
    }
}
```

## Q2 — Minimum Deletions to Make Array Beautiful

**Link:** https://leetcode.com/problems/minimum-deletions-to-make-array-beautiful/ (LC 2216, rating 1510)

AC on the first submission, 20 minutes, contest minute 39. Walk the array in pairs. When a pair starts with two equal values, delete the run of copies until a different value arrives to close the pair, then jump past it. If the length left over is odd, delete one more.

```java
class Solution {
    public int minDeletion(int[] nums) {
        
        int deletion = 0;
        int n = nums.length;
        int i = 0;

        while(i < n - 1){

            if (nums[i] == nums[i + 1]){
                int j = i + 1;
                while(j < n && nums[i] == nums[j]){
                    j++;
                    deletion++;
                }
                i = j + 1;
            }
            else i = i + 2;
        }

        if ((n - deletion)%2 != 0) return deletion + 1;
        return deletion;
    }
}
```

## Q3 — Climbing Stairs II

**Link:** https://leetcode.com/problems/climbing-stairs-ii/ (LC 3693, rating 1560)

AC on the first submission, 20 minutes, contest minute 60. Memoised recursion from the ground: from position i, jump 1, 2 or 3 steps to j and pay costs[j − 1] + (j − i)², which is 1, 4 or 9; take the cheapest of the three plus the best cost from j.

```java
class Solution {
    
    private static Long[] dp;

    public int climbStairs(int n, int[] costs) {
        
        dp = new Long[n + 1];

        return (int)helper(0 , n , costs);
    }

    private long helper(int i , int n , int [] costs){

        if (i == n) return 0;

        if (dp[i] != null) return dp[i];

        long minCost = costs[i] + 1 + helper(i + 1 , n , costs);

        if (i + 2 <= n){
            minCost = Math.min(minCost , costs[i + 1] + 4 + helper(i + 2, n , costs));
        }
        if (i + 3 <= n){
            minCost = Math.min(minCost , costs[i + 2] + 9 + helper(i + 3, n , costs));
        }
        return dp[i] = minCost;

    }
}
```

---

## Upsolve

### Q4 — Minimum Operations to Make a Special Number

**Link:** https://leetcode.com/problems/minimum-operations-to-make-a-special-number/ (LC 2844, rating 1588)

**Result: AC, hinted.** 2026-11-20 (Fri), 14:49–15:06 and 16:04–16:46, about 59 minutes. Started from step 1 of the explanation and finished alone. Cold re-solve due 2026-11-21.

**Step 1, the rewritten question:** a number is divisible by 25 exactly when its last two digits are 00, 25, 50 or 75, or when the whole number is 0. So find the fewest deletions that leave the digits ending in one of those four pairs, or reduce the number to 0.

**How the solution works:** a stack of indices per digit, filled left to right. Scan from the right with `count` holding the digits already passed. At a 0, look for the nearest 5 or 0 to its left; at a 5, the nearest 2 or 7. The cost of a pair is the digits between the two plus `count`. Two sentinels cover the edge cases: a missing partner returns -2, which prices the pair at n (delete everything), and a -1 at the bottom of the 0 stack prices keeping a lone 0 at n − 1. The scan stops once it reaches the leftmost partner found so far, since any pair ending further left deletes more digits.

**Checked:** examples give 2, 3 and 1; 0 mismatches against brute force over 20,000 random cases; n = 100 runs in 54 µs.

```java
class Solution {

    private int getPosition(Character ch , int index , Map<Character,Stack<Integer>> map){

        Stack<Integer> stack = map.getOrDefault(ch , new Stack<>());

        while(!stack.isEmpty()){

            int top = stack.peek();
            if (top >= index) {
                stack.pop();
                continue;
            }
            return top;
        }

        return -2;
    }

    public int minimumOperations(String num) {
    
    Map<Character,Stack<Integer>> map = new HashMap<>();
    Stack<Integer> st = new Stack<>();
    st.push(-1);
    map.put('0' , st);

    for (int i = 0; i < num.length(); i++){

        Character ch = num.charAt(i);

        Stack<Integer> stack = map.getOrDefault(ch  , new Stack<>());
        stack.push(i);
        map.put(ch , stack);
    }


    int minDeletion = Integer.MAX_VALUE;
    int maxIndex = -1;

    int count = 0;
    
    for (int i = num.length() - 1; i >= 0; i--){

        if (i == maxIndex) return minDeletion;

        Character ch = num.charAt(i);
        int digit = ch - '0' - 0;

        if (digit == 0){

            int pos1 = getPosition('5' , i , map);
            minDeletion = Math.min(minDeletion , (i - pos1 - 1) + count);

            int pos2 = getPosition('0' , i , map);
            minDeletion = Math.min(minDeletion , (i - pos2 - 1) + count);

            maxIndex = Math.max(maxIndex ,Math.max(pos1 , pos2));
            
        }
        else if (digit == 5){

            int pos1 = getPosition('2' , i , map);
            minDeletion = Math.min(minDeletion , (i - pos1 - 1) + count);

            int pos2 = getPosition('7' , i , map);
            minDeletion = Math.min(minDeletion , (i - pos2 - 1) + count);

            maxIndex = Math.max(maxIndex ,Math.max(pos1 , pos2));
        }
        count++;
    }

    if (minDeletion == Integer.MAX_VALUE) return count;
    return minDeletion;

    }
}
```

**Other ways to solve it:**

- **Two scans per pair:** for each of 00, 25, 50 and 75, scan from the right for the second digit, then keep going left for the first; the cost is the digits after the second plus the digits between. Take the smallest, against n − 1 when a 0 exists and n otherwise. Same O(n), no map or stack; checked against brute force with 0 mismatches. To walk through after the cold re-solve.
- **DP on the remainder** (the doocs editorial in `editorials-data/`): `dfs(i, k)` with k the kept number mod 25, delete or keep each digit, O(25n). The state is the remainder, not the value, which is the same fix mock 2 Q3 needed: there the memo held the running sum, n × 1,000,001 cells, when the sum mod 2 was enough.
