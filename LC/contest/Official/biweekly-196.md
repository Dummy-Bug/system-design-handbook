# Biweekly Contest 196

**Date:** 2026-11-21 (Sat), 20:00–21:30 IST, logged 19:59–21:25.
**Rank:** about 5k, the user's figure; the full result line was not captured.
**Ratings:** no zerotrac rating yet for any of the four; titles and slugs were not captured, so the problems are named by their function.

| Q   | Function       | Result          | Note                                                               |
| --- | -------------- | --------------- | ------------------------------------------------------------------ |
| Q1  | assignUmbrella | WA then AC (+5) | AC at 20:10; the tie-break comparison was flipped                  |
| Q2  | minRange       | AC              | AC at 20:32, first submission                                      |
| Q3  | minOperations  | WA, not solved  | WA at 20:45, 79/1000 passed; stopped at 21:25 with 10 minutes left |
| Q4  | not opened     | not attempted   |                                                                    |

**Two solved.** Stopped with 10 minutes left; not burned out, just out of time. Went for a walk after.

---

## Q1 — assignUmbrella (WA then AC)

**WA-cause [impl-bug]:** the tie-break `alice >= bob` gave the umbrella to Alice when the counts were equal; it had to be `alice <= bob`. Failing case `[1,1,1]`: got Alice, Alice, Bob, expected Alice, Bob, Bob. 173/999 passed. In the user's words: a silly mistake.

First attempt (WA):

```java
class Solution {
    public String[] assignUmbrella(int[] rain) {

        int alice = 0;
        int bob = 0;

        int n = rain.length;

        String [] ans = new String[n];

        for (int i = 0; i < n - 1; i++){

            if (rain[i] == 1){

                if (rain[i + 1] == 1){

                    if (alice >= bob){
                        alice++;
                        ans[i] = "Alice";
                    }
                    else{
                        bob++;
                        ans[i] = "Bob";
                    }
                    
                }
                else {
                    ans[i] = "Bob";
                    bob++;
                }
            }
            else{
                ans[i] = "None";
            }
        }

        if (rain[n - 1] == 1){
            ans[n - 1] = "Bob";
        }
        else ans[n - 1] = "None";

        return ans;
    }
}
```

Second attempt (AC): the same code with `alice >= bob` changed to `alice <= bob`.

---

## Q2 — minRange (AC first submission)

The idea: keep the three values in a min-heap; while the two smallest add up to less than the largest, replace the largest with their sum; the answer is max minus min at the stop.

```java
class Solution {
    public int minRange(int a, int b, int c) {

        PriorityQueue<Integer> pq = new PriorityQueue<>();

        pq.offer(a);
        pq.offer(b);
        pq.offer(c);

        int ans = Math.max(a , Math.max(b , c)) - Math.min(a , Math.min(b , c));

        while(true){

            int min = pq.poll();
            int mid = pq.poll();
            int max = pq.poll();

            if (min + mid >= max) return ans;
            max = min + mid;
            ans = max - min;

            pq.offer(min);
            pq.offer(mid);
            pq.offer(max);
        }
    }
}
```

---

## Q3 — minOperations (WA, not solved)

The full statement was not captured, so the cause of the WA is only partly known.

**WA-cause [unknown]:** the submission returned 0 on `[2,13,1,12]` where 12 was expected; 79/1000 passed. It returns 0 as soon as some middle element beats the max on both sides, which is not enough for that case.

Submitted (WA):

```java
class Solution {
    public int minOperations(int[] nums) {

        int n = nums.length;
        if (n < 3) return -1;

        int [] suffix = new int [n];
        suffix[n - 1] = nums[n - 1];
        
        for (int i = n - 2; i >= 0; i--){
           suffix[i] = Math.max(nums[i] , suffix[i + 1]); 
        }

        int prefix = nums[0];

        int ans = Integer.MAX_VALUE;

        for (int i = 1; i < n - 1; i++){

            int max = Math.max(prefix , suffix[i + 1]);

            if (max < nums[i]) return 0;
            else ans = Math.min(ans , max - nums[i] + 1);
            prefix = Math.max(nums[i] , prefix);
        }

        return ans;
    }
}
```

**Thinking at the stop (21:25):** for each `nums[i]`, count the operations on the left and on the right. The values on the left must fit in `[1, nums[i] - 1]`, so skip `i` if there are too many values on the left to fit a strictly increasing order. Walk left tracking the largest allowed value at each position, adding `nums[left] - nums[left - 1] + 1` operations when a number goes over it; mirror on the right with the smallest allowed. Total = left ops + right ops, answer = min over `i`. O(n²) in the worst case, felt fine. Too many cases; felt some maths was needed.

**Upsolve:** waits for its zerotrac rating; skip if 1600 or above.
