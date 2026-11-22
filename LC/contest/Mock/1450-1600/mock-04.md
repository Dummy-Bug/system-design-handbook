# Mock Contest 4

**Date:** 2026-11-22 (Sun), 15:08–16:38 IST, the full 90 minutes, no AI, four problems from 1450-1599, rated in rising order from 1523 to 1571. The same day as Weekly 529 in the morning.

| Q   | Problem                                             | Rating |    AR | Time                | Result                            |
| --- | --------------------------------------------------- | -----: | ----: | ------------------- | --------------------------------- |
| Q1  | maximum-xor-for-each-query                          |   1523 | 84.7% | 15:08–15:29, 21 min | WA then AC (+5)                   |
| Q2  | length-of-longest-subarray-with-at-most-k-frequency |   1535 | 56.6% | 15:29–15:40, 11 min | AC first submission               |
| Q3  | time-needed-to-inform-all-employees                 |   1561 | 60.5% | 15:40–16:22, 42 min | WA then AC (+5)                   |
| Q4  | k-th-symbol-in-grammar                              |   1571 | 48.3% | 16:22–17:02, 40 min | Not solved in time, AC after time |

**Three solved in time, two WAs, 26, 11 and 47 minutes with the penalty.** Q2 counts as a win under the 25-minute rule; Q1 and Q3 do not. Q4 was not solved at 16:38; the user kept going and got AC on the first submission at 17:02, 24 minutes after time. The times are when each solution was pasted.

**Q4 had been solved before, but it was not easy now.** The LeetCode history shows 7 submissions from Sep 2021 to Jan 2025, the last an AC in Java on 2025-01-22. It was still uncomfortable: at the 90-minute mark the pattern was visible but would not reduce to a recursion, and the overtime AC took real effort and was derived, not recalled. The solved check covers the vault files only, not LeetCode submission history.

**Difficulty: MEDIUM by the user, MIXED as built.** Built as MIXED because mock 2 went badly and mock 3 ended burned out, with an official contest already done that morning: a bit-manipulation start, a sliding-window classic, a tree weak spot, and the lowest acceptance last. The user's labels: overall MEDIUM, not MIXED, because Q1 was not straightforward at all. Q1 and Q2 felt swapped: Q2 easier thanks to reps on the sliding-window classics, Q1 harder than its 1523. Q3: a long time since a graph problem, and it needed a twist inside BFS, so both the thinking and the implementation took time; no single word given. Q4 MEDIUM because seen before; unseen it would have been on the HARD side.

**Calibration:** rating and acceptance undersell a weak-spot mechanic. Q1's 84.7% reflects a well-known problem, not one that is easy for this user; bit manipulation plays above its rating, drilled classics below theirs.

|                   | Mock 1        | Mock 2    | Mock 3            | Mock 4                    |
| ----------------- | ------------- | --------- | ----------------- | ------------------------- |
| Band              | 1479-1588     | 1560-1636 | 1477-1574         | 1523-1571                 |
| Classics          | three of four | none      | one               | one, plus Q4 seen before  |
| Solved            | 3             | 1         | 2                 | 3, plus Q4 after time     |
| WA                | 0             | 1         | 3                 | 2                         |
| Minutes per solve | 18, 20, 20    | 43        | 34, 24 (with +5s) | 26, 11, 47 (with +5s)     |
| Ended             | burned out    | at time   | burned out, 07:28 | at time, then overtime Q4 |

## What went wrong

1. **Neither WA could be caught by the examples.** Running the WA code on the given examples gives the expected output every time (run below). Q1 needed the smallest input from a Step 3 list; the user tried edge cases but may have skipped that one. Q3 needed a Step 2 trace on a lopsided tree. No Steps 2 or 3 were posted during the mock.
2. **Q3 took 42 minutes on rust.** No graph or tree problem since June; both the idea and the code were slow.

## Q1 — Maximum XOR for Each Query

**Link:** https://leetcode.com/problems/maximum-xor-for-each-query/ (LC 1829, rating 1523, AR 84.7%)

**WA-cause [read-error]:** `max = nums[n - 1]`. Since k < 2^maximumBit, the best k turns on all maximumBit bits of the XOR, so the value to XOR with is always `2^maximumBit − 1`, whatever nums holds. Failing case `nums = [0], maximumBit = 1`: got [0], expected [1]. 32/86 passed.

Run on the three examples and the failing case. The last element happens to equal the mask in every example (3, 7, 7), so the bug passes all three:

| Input               | WA code            | AC code            |
| ------------------- | ------------------ | ------------------ |
| [0,1,1,3], mb=2     | [0, 3, 2, 3]       | [0, 3, 2, 3]       |
| [2,3,4,7], mb=3     | [5, 2, 6, 5]       | [5, 2, 6, 5]       |
| [0,1,2,2,5,7], mb=3 | [4, 3, 6, 4, 6, 7] | [4, 3, 6, 4, 6, 7] |
| [0], mb=1           | [0]                | [1]                |

First attempt (WA):

```java
class Solution {
    public int[] getMaximumXor(int[] nums, int maximumBit) {

        int n = nums.length;

        int xor = 0;

        for (int i = 0; i < n; i++) {
            xor ^= nums[i];
        }

        int [] ans = new int[n];
        int max = nums[n - 1];

        for (int i = n - 1; i >= 0; i--) {
            ans[n - i - 1] = xor ^ max;
            xor ^= nums[i];
        }
        return ans;
    }
}
```

Second attempt (AC):

```java
class Solution {
    public int[] getMaximumXor(int[] nums, int maximumBit) {

        int n = nums.length;

        int xor = 0;

        for (int i = 0; i < n; i++) {
            xor ^= nums[i];
        }

        int [] ans = new int[n];
        int max = (int)Math.pow(2,maximumBit) - 1;

        for (int i = n - 1; i >= 0; i--) {
            ans[n - i - 1] = xor ^ max;
            xor ^= nums[i];
        }
        return ans;
    }
}
```

## Q2 — Length of Longest Subarray With at Most K Frequency

**Link:** https://leetcode.com/problems/length-of-longest-subarray-with-at-most-k-frequency/ (LC 2958, rating 1535, AR 56.6%)

Clean, 11 minutes. Only `nums[right]` can go over k when it enters, so moving left until one copy of it leaves the window restores the rule.

```java
class Solution {
    public int maxSubarrayLength(int[] nums, int k) {
        
        int ans = 1;
        int n = nums.length;
        int left = 0;

        Map<Integer,Integer> map = new HashMap<>();

        for (int right = 0; right < n; right++){

            int freq = 1 + map.getOrDefault(nums[right] , 0);
            map.put(nums[right] , freq);

            if (freq <= k){
                ans = Math.max(ans , right - left + 1);
                continue;
            }
            while(nums[left] != nums[right]){
                map.put(nums[left] , map.get(nums[left]) - 1);
                left++;
            }
            map.put(nums[left] , map.get(nums[left]) - 1);
            left++;
        }
        return ans;
    }
}
```

## Q3 — Time Needed to Inform All Employees

**Link:** https://leetcode.com/problems/time-needed-to-inform-all-employees/ (LC 1376, rating 1561, AR 60.5%)

**WA-cause [logic-accounting]:** the first attempt added the largest informTime on each BFS level. Those maxima can come from different branches; the time to reach an employee is the sum along their own chain of managers. Failing case `n = 11, headID = 4, manager = [5,9,6,10,-1,8,9,1,9,3,4], informTime = [0,213,0,253,686,170,975,0,261,309,337]`: got 2730, expected 2560. 8/39 passed. Both examples pass with the bug (run: 0 and 1).

```text
4(686) → 10(337) → 3(253) → 9(309) → 6(975)            = 2560  ← answer
                                   → 8(261) → 5(170)   = 2016
level sums: 686 + 337 + 253 + 309 + 975 + 170           = 2730  ← WA
```

The 975 is on 6's branch and the 170 is under 8, yet the level sum adds both.

First attempt (WA):

```java
class Solution {

    Map<Integer, List<Integer>> tree;

    public int numOfMinutes(int n, int headID, int[] manager, int[] informTime) {
        
        tree = new HashMap<>();

        for (int i = 0; i < n; i++){
            if (manager[i] == -1) continue;

            List<Integer> subordinates = tree.getOrDefault(manager[i] , new ArrayList<>());
            subordinates.add(i);
            tree.put(manager[i] , subordinates);
        }

        return helper(headID,informTime);
    }

    private int helper(int head, int [] informTime){

        Deque<Integer> q = new ArrayDeque<>();
        q.offer(head);
        int ans = 0;

        while(!q.isEmpty()){

            int size = q.size();
            int levelTime = 0;

            for (int i = 0; i < size; i++){

                int manager = q.poll();
                levelTime = Math.max(levelTime , informTime[manager]);

                for (int employee : tree.getOrDefault(manager , new ArrayList<>())){
                   if (informTime[employee] != 0){
                    q.offer(employee);
                   }
                }
            }
            ans += levelTime;
        }
        return ans;
    }
}
```

Second attempt (AC): each queue entry carries the time so far along its own path, and the answer is the max over all entries.

```java
class Solution {

    Map<Integer, List<Integer>> tree;

    public int numOfMinutes(int n, int headID, int[] manager, int[] informTime) {

        tree = new HashMap<>();

        for (int i = 0; i < n; i++) {
            if (manager[i] == -1)
                continue;

            List<Integer> subordinates = tree.getOrDefault(manager[i], new ArrayList<>());
            subordinates.add(i);
            tree.put(manager[i], subordinates);
        }

        return helper(headID, informTime);
    }

    private int helper(int head, int[] informTime) {

        Deque<int[]> q = new ArrayDeque<>();
        q.offer(new int[] { head, informTime[head]});

        int ans = 0;

        while (!q.isEmpty()) {

            int [] entry = q.poll();
            head = entry[0];
            int time = entry[1];

            for (int employee : tree.getOrDefault(head, new ArrayList<>())) {
                if (informTime[employee] != 0) {
                    q.offer(new int[ ]{employee, time + informTime[employee]});
                }
            }
            ans = Math.max(ans , time);
        }
        return ans;
    }
}
```

The `getOrDefault` result is written back with `put`, so the Weekly 528 lesson held. With labels 0 to n-1, a list of lists needs no map at all.

## Q4 — K-th Symbol in Grammar (seen before, AC after time)

**Link:** https://leetcode.com/problems/k-th-symbol-in-grammar/ (LC 779, rating 1571, AR 48.3%)

Not solved at 16:38: the pattern was visible but would not reduce. AC on the first submission at 17:02. The recursion: row n is row n − 1 followed by its flip, so a k in the second half is the flipped symbol at `k − half` in row n − 1, and a k in the first half is the same symbol in row n − 1.

```java
class Solution {
    public int kthGrammar(int n, int k) {
        
        if (n == 1 || k == 1) return 0;

        int totalColumns = (int)Math.pow(2,n - 1);

        if (k >  totalColumns/2 ){
            return kthGrammar(n - 1, k - totalColumns/2) ^ 1;
        }
        return kthGrammar(n - 1, k);
    }
}
```

## Mechanic coverage

Each problem counts once, under the idea that solves it. Q4 does not count because it was solved after time.

| Mechanic         | Solve from |
| ---------------- | ---------- |
| Bit manipulation | Q1         |
| Sliding window   | Q2         |
| DFS / BFS / tree | Q3         |

Standing after mocks 1-4: 9 of 31.
