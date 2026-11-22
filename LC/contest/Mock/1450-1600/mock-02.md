# Mock Contest 2

**Date:** 2026-11-20 (Fri), 06:30–08:00 IST, 90 minutes, no AI, four unseen problems from 1550-1650 with well-known classics left out, rated in rising order from 1560 to 1636.

| Q   | Problem                                 | Rating | Time                | Result          |
| --- | --------------------------------------- | -----: | ------------------- | --------------- |
| Q1  | number-of-subarrays-with-lcm-equal-to-k |   1560 | 1 min read          | Skipped         |
| Q2  | maximum-points-after-enemy-battles      |   1591 | 06:31–07:14, 43 min | WA then AC (+5) |
| Q3  | number-of-sub-arrays-with-odd-sum       |   1611 | 07:14–08:00, 46 min | Not solved      |
| Q4  | largest-palindromic-number              |   1636 | not reached         | Not opened      |

**One solved, one WA, 49 minutes with the penalty.** No problem counts as a win under the 25-minute rule.

**Difficulty: MEDIUM by rating, HARD by feel.** The four average 1600, exactly the midpoint of 1550-1650; the hardest possible set would have been four problems near 1650 with acceptance rates in the 30s. Only Q2 (33.4%) was like that. With the classics left out on purpose, none of the four was quick recall, which is what made it hard.

**Performance estimate, about 1408, weak evidence.** 1 of these 4 is the expected result for a player rated about 1408. At 1512 the expected count is 1.5, so one solve is inside normal variation for a single session.

|                   | Mock 1        | Mock 2    |
| ----------------- | ------------- | --------- |
| Band              | 1479-1588     | 1560-1636 |
| Classics          | three of four | none      |
| Solved            | 3             | 1         |
| WA                | 0             | 1         |
| Minutes per solve | 18, 20, 20    | 43        |

## What went wrong

1. **Q2 WA on a constraint bound.** The constraints allow currentEnergy = 0, and the failing case was [1, 2, 3] with energy 0. Steps 2 and 3 were not posted before the submit; pushing that bound to its extreme is exactly the Step 3 case that would have caught it. The rule itself (no point, no absorbing) was already in the notebook and got dropped while coding.
2. **Q1 skipped on the topic word.** One minute of reading, then dropped because of LCM. It was the lowest-rated problem in the set, and Math/NT is a bucket owned since June. A problem gets ranked after about five minutes on its constraints and examples, not on the first word that sounds uncomfortable.
3. **Q3: 46 minutes on an approach that could not run.** The memo table was n × 1,000,001 Integers. At n = 10⁵ that is 10¹¹ cells, far past any memory limit. A one-minute check of states × cost before coding would have dropped it and freed the time to look for another idea.

## Q2 — Maximum Points After Enemy Battles

**Link:** https://leetcode.com/problems/maximum-points-after-enemy-battles/ (LC 3207, rating 1591, AR 33.4%)

**WA-cause [untraced-submit]:** submitted without Step 3. On [1, 2, 3] with currentEnergy 0, no enemy can be beaten, so the answer is 0; the first submission absorbed the largest enemy anyway, gaining energy without having a point, and returned 5. The fix returns 0 when there are no points yet and the smallest enemy is out of reach.

First submission (WA):

```java
class Solution {

    private long getEnergyBooster(PriorityQueue<int[]> maxPq ,Set<Integer> marked){

        while(!maxPq.isEmpty()){

            int [] entry = maxPq.poll();
            marked.add(entry[1]);

            return (long)entry[0];
        }
        return -1l;
    }

    public long maximumPoints(int[] enemyEnergies, int initialEnergy) {
        
        PriorityQueue<int[]> maxPq = new PriorityQueue<>((a,b) -> {
            if (a[0] == b[0]){
                return a[1] - b[1];
            }
            return b[0] - a[0];
        });

        PriorityQueue<int[]> minPq = new PriorityQueue<>((a,b) -> {
            if (a[0] == b[0]){
                return a[1] - b[1];
            }
            return a[0] - b[0];
        });

        int n = enemyEnergies.length;
        long currentEnergy = (long)initialEnergy;

        for(int i = 0; i < n; i++){
            
            int [] entry = new int[]{enemyEnergies[i] , i};
            
            minPq.offer(entry);
            maxPq.offer(entry);
        }

        long points = 0l;
        Set<Integer> marked = new HashSet<>();

        while(!minPq.isEmpty()){
                
            int [] entry = minPq.peek();
            
            if (marked.contains(entry[1])) minPq.poll();

            else if (entry[0] > currentEnergy){
                
                long boost = getEnergyBooster(maxPq , marked);
                
                if ( boost == -1) return points;

                currentEnergy += boost;
            }
            else {
                long factor = currentEnergy / entry[0];
                currentEnergy = currentEnergy % entry[0];
                points += factor;
            }
        }
        return points;
    }
}
```

Final (AC), the one added line is `if (points == 0) return 0;`:

```java
class Solution {

    private long getEnergyBooster(PriorityQueue<int[]> maxPq ,Set<Integer> marked){

        while(!maxPq.isEmpty()){

            int [] entry = maxPq.poll();
            marked.add(entry[1]);

            return (long)entry[0];
        }
        return -1l;
    }

    public long maximumPoints(int[] enemyEnergies, int initialEnergy) {
        
        PriorityQueue<int[]> maxPq = new PriorityQueue<>((a,b) -> {
            if (a[0] == b[0]){
                return a[1] - b[1];
            }
            return b[0] - a[0];
        });

        PriorityQueue<int[]> minPq = new PriorityQueue<>((a,b) -> {
            if (a[0] == b[0]){
                return a[1] - b[1];
            }
            return a[0] - b[0];
        });

        int n = enemyEnergies.length;
        long currentEnergy = (long)initialEnergy;

        for(int i = 0; i < n; i++){
            
            int [] entry = new int[]{enemyEnergies[i] , i};
            
            minPq.offer(entry);
            maxPq.offer(entry);
        }

        long points = 0l;
        Set<Integer> marked = new HashSet<>();

        while(!minPq.isEmpty()){
                
            int [] entry = minPq.peek();
            
            if (marked.contains(entry[1])) minPq.poll();

            else if (entry[0] > currentEnergy){
                
                if (points == 0) return 0;
                long boost = getEnergyBooster(maxPq , marked);
                
                if ( boost == -1) return points;

                currentEnergy += boost;
            }
            else {
                long factor = currentEnergy / entry[0];
                currentEnergy = currentEnergy % entry[0];
                points += factor;
            }
        }
        return points;
    }
}
```

## Q3 — Number of Sub-arrays With Odd Sum (not solved)

**Link:** https://leetcode.com/problems/number-of-sub-arrays-with-odd-sum/ (LC 1524, rating 1611)

**Stuck note:**
1. **Understood:** count the subarrays whose sum is odd, mod 10⁹ + 7.
2. **Tried:** recursion with memo over (index, running sum), either starting a new chain or continuing the current one.
3. **Stuck at:** could not make it count correctly.

Last attempt at the stop:

```java
class Solution {

    private Integer[][] dp;
    private int MOD = 1000000007;

    public int numOfSubarrays(int[] arr) {

        int n = arr.length;

        dp = new Integer[n][1000001];

        return (int) helper(0, 0, arr);
    }

    private long helper(int i, long sum, int[] arr) {

        if (i == arr.length)
            return 0;

        if (this.dp[i][(int)sum] != null)
            return this.dp[i][(int)sum];


        long startChain = helper(i + 1, arr[i] , arr);
        if ((arr[i]%2) != 0)
            startChain++;

        long afterSummation = (sum + arr[i])%MOD;
        long continueChain = helper(i + 1, afterSummation, arr);
        if ((afterSummation%2) != 0)
            continueChain ++;

        return dp[i][(int)sum] = (int)(startChain + continueChain)%MOD;
    }
}
```

Step-by-step explanation pending: step 1 (the rewritten question) given at 08:03, the rest on hold.

## Still open from this mock

- **Q3:** finish from step 1.
- **Q1:** read for one minute only, so it is close to unseen; can be dealt again later.
- **Q4:** never opened, still unseen.
