# Mock Contest 3

**Date:** 2026-11-21 (Sat), 06:05–07:28 IST, stopped at minute 83 of 90, no AI, four unseen problems from 1450-1599, rated in rising order from 1477 to 1574.

| Q  | Problem                                              | Rating |    AR | Time                | Result          |
| -- | ---------------------------------------------------- | -----: | ----: | ------------------- | --------------- |
| Q1 | successful-pairs-of-spells-and-potions               |   1477 |       | 06:05–06:34, 29 min | WA then AC (+5) |
| Q2 | minimum-length-of-string-after-deleting-similar-ends |   1502 | 56.1% | 06:34–06:53, 19 min | WA then AC (+5) |
| Q3 | array-of-doubled-pairs                               |   1548 | 39.8% | 06:53–07:28, 35 min | Not solved      |
| Q4 | minimum-time-to-make-rope-colorful                   |   1574 | 65.2% | not reached         | Not opened      |

**Two solved, three WAs, 34 and 24 minutes with the penalty.** Q2 counts as a win under the 25-minute rule; Q1 does not. The contest was stopped at 07:28: fully burned out, not able to think anything.

**Difficulty: MEDIUM.** Ratings spread across the band, one classic (Q1, sort plus binary search), one weak spot (Q2, two pointers), acceptance from 39.8% to 65.2%. The user left the one-word labels to Claude; read from the evidence, not from feel: Q1 MEDIUM (a classic, but 29 minutes and a WA), Q2 MEDIUM (19 minutes plus a WA), Q3 HARD (not solved, the lowest acceptance in the set). Q4 has no label because it was never opened.

**Performance estimate, about 1525, weak evidence.** 2 of these 4 is the expected result for a player rated about 1525, close to the current 1517.

|                   | Mock 1        | Mock 2    | Mock 3            |
| ----------------- | ------------- | --------- | ----------------- |
| Band              | 1479-1588     | 1560-1636 | 1477-1574         |
| Classics          | three of four | none      | one               |
| Solved            | 3             | 1         | 2                 |
| WA                | 0             | 1         | 3                 |
| Minutes per solve | 18, 20, 20    | 43        | 34, 24 (with +5s) |
| Ended             | burned out    | at time   | burned out, 07:28 |

## What went wrong

1. **Every WA was an edge case.** Q1: the case where every potion is strong enough was in the Step 3 list, but the guard returned -1 on the belief that it gave the answer, and n − position was never worked out for position −1; careless. Q2: the single-middle-character case was missing from the list. Q3: zeros.
2. **Stopped burned out, for the second time in three mocks.** Mock 1 also ended burned out.

## Q1 — Successful Pairs of Spells and Potions

**Link:** https://leetcode.com/problems/successful-pairs-of-spells-and-potions/ (LC 2300, rating 1477)

Sort the potions. For each spell, the weakest potion that works is the ceiling of success / spell, so binary search for the first potion at least that large; every potion from there to the end is a successful pair.

**WA-cause [impl-bug] [untraced-submit]:** the guard for a target below the smallest potion returned `low - 1`, which is -1, so the count came out as n + 1. On spells [15, 8, 19], potions [38, 36, 23], success 328 it returned [4, 0, 4] instead of [3, 0, 3]. The fix returns `low`, index 0, so the count is n.

AC code:

```java
class Solution {

    private int findPosition(long num  , int [] nums){
        
        int low = 0;
        int high = nums.length - 1;

        if (num < nums[low]) return low;
        if (num > nums[high]) return high + 1;

        int candidate = -1;

        while(low <= high){

            int mid = (low + high)/2 ;

            if (nums[mid] >= num){
                candidate = mid;
                high = mid - 1;
            }
            else low = mid + 1;
        }
        return candidate;
    }


    public int[] successfulPairs(int[] spells, int[] potions, long success) {
        
        Arrays.sort(potions);
        int m = spells.length;
        int [] ans = new int[m];

        for (int i = 0; i < m; i++){
            long element = (spells[i] + success - 1)/spells[i] ;

            int position = findPosition(element , potions);
            ans[i] = potions.length - position;
        }
        return ans;
    }
}
```

## Q2 — Minimum Length of String After Deleting Similar Ends

**Link:** https://leetcode.com/problems/minimum-length-of-string-after-deleting-similar-ends/ (LC 1750, rating 1502, AR 56.1%)

Two pointers from both ends. While the two ends hold the same character, move each pointer past its whole run of that character. Stop when the ends differ, or when only one character is left, since a prefix and a suffix cannot share it.

**WA-cause [untraced-submit]:** on `aabaaa`, the runs of a are removed and only `b` is left at left == right. The loop treated it as a matching pair of ends and deleted it, returning 0 instead of 1. The fix adds `|| left == right` to the first check, so a single middle character is kept.

AC code:

```java
class Solution {
    public int minimumLength(String s) {
        
        int n = s.length();
        int left = 0;
        int right = n - 1;

        while (right >= left){

            if (s.charAt(left) != s.charAt(right) || left == right) return right - left + 1;

            while((left + 1 < n) && (s.charAt(left) == s.charAt(left + 1))){
                left++;
            }

            while((right - 1 > 0 ) && (s.charAt(right) == s.charAt(right - 1))){
                right--;
            }
            left++;
            right--;
            
        }
        if (left > right) return 0;
        return right - left + 1;
    }
}
```

## Q3 — Array of Doubled Pairs (not solved)

**Link:** https://leetcode.com/problems/array-of-doubled-pairs/ (LC 954, rating 1548, AR 39.8%)

**Stuck note:**
1. **Understood:** pair every element with one equal to its double, using each element once.
2. **Tried:** count the values in a map, then for each element take one copy of its double from the map, counting the elements that find no double.
3. **Stuck at:** a WA on zeros, then a second attempt; burned out and not able to think anything.

**WA-cause [untraced-submit]:** on [2, 4, 0, 0, 8, 1] the first submission returned false instead of true.

First submission (WA, 65 of 102):

```java
class Solution {
    public boolean canReorderDoubled(int[] arr) {

        Map<Integer, Integer> map = new HashMap<>();

        for (int num : arr) {
            int count = map.getOrDefault(num, 0);
            map.put(num, count + 1);
        }

        int falseAlarm = 0;
        for (int num : arr) {

            int count = map.getOrDefault(num * 2, 0);

            if (count == 0) {
                falseAlarm++;
                continue;
            }
            map.put(num * 2, count - 1);
        }
        if (falseAlarm == arr.length/2) return true;
        return false;
    }
}
```

Second attempt at the stop, adding a check for an odd count of zeros:

```java
class Solution {
    public boolean canReorderDoubled(int[] arr) {

        Map<Integer, Integer> map = new HashMap<>();

        for (int num : arr) {
            int count = map.getOrDefault(num, 0);
            map.put(num, count + 1);
        }

        if (map.getOrDefault(0 , 0)%2 != 0 ) return false;

        int falseAlarm = 0;
        for (int num : arr) {

            int count = map.getOrDefault(num * 2, 0);

            if (count == 0) {
                falseAlarm++;
                continue;
            }
            map.put(num * 2, count - 1);
        }
        if (falseAlarm <= arr.length/2) return true;
        return false;
    }
}
```

## Q3 upsolve

**2026-11-21, 09:59–10:48, hinted: step 1 only, one WA then AC.** Step 1, the rewritten question: the element with the smallest absolute value still left cannot be anyone's double, because its half would be smaller still, so it must take an unused copy of its double; remove both and repeat from the smallest absolute value upward. Carried on alone from there.

**WA-cause [impl-bug]:** the pair counter started at the number of zero pairs, and the only `count == n/2` check sat after a non-zero pair was made. On [0, 0] the loop skipped both zeros, never reached the check and fell through to `return false`; 99 of 102 passed. The fix drops the counter and returns true once the loop finishes.

AC code:

```java
class Solution {
    public boolean canReorderDoubled(int[] nums) {


        int n = nums.length;
        Integer [] arr = new Integer[n];

        for (int i = 0; i < n; i++){
            arr[i] = nums[i];
        }

        Map<Integer, Deque<Integer>> map = new HashMap<>();

        Arrays.sort(arr , (a,b) -> Math.abs(a) - Math.abs(b));

        for (int i = 0; i < n; i++) {
            int num = arr[i];
            Deque<Integer> stack = map.getOrDefault(num, new ArrayDeque<>());
            stack.push(i);
            map.put(num , stack);
        }

        Deque<Integer> st = map.getOrDefault(0, new ArrayDeque<>());

        if ( (!st.isEmpty()) && (st.size() %2 != 0) ) return false;
        
        Set<Integer> paired = new HashSet<>();
        
        for (int i = 0; i < n; i++) {

            if (arr[i] == 0) paired.add(i);

            if (paired.contains(i)) continue;

            Deque<Integer> stack = map.getOrDefault(2 * arr[i], new ArrayDeque<>());
            if (stack.isEmpty()) return false;

            paired.add(stack.pop());
            map.put(2 * arr[i] , stack);
        }
        return true;
    }
}
```

**The expected solution is the same greedy, kept per distinct value instead of per index.** Count each value, walk the distinct values in order of absolute value, and for each x check that count[2x] is at least count[x], then take count[x] off count[2x]. Zeros pass on their own once their count is even. The index stacks and the paired set do the work a count already does. The mock's first submission had the count map; it lacked the order by absolute value, and an element used up as a double was never skipped later.

```java
class Solution {
    public boolean canReorderDoubled(int[] arr) {
        Map<Integer, Integer> freq = new HashMap<>();
        for (int v : arr) {
            freq.put(v, freq.getOrDefault(v, 0) + 1);
        }
        if ((freq.getOrDefault(0, 0) & 1) != 0) {
            return false;
        }
        List<Integer> keys = new ArrayList<>(freq.keySet());
        keys.sort(Comparator.comparingInt(Math::abs));
        for (int k : keys) {
            if (freq.getOrDefault(k << 1, 0) < freq.get(k)) {
                return false;
            }
            freq.put(k << 1, freq.getOrDefault(k << 1, 0) - freq.get(k));
        }
        return true;
    }
}
```

### The same habit across earlier problems

**This problem was solved before in another form.** LC 2007, find-original-array-from-doubled-array (rating 1557, `problem-solving/1550-1600/First-Attempt/29`), on 2026-06-01: the smallest-first greedy self-derived, first submission AC in 49 minutes, with nearly the same code (`Map<Integer, Deque<Integer>>`, `push(i)`, a `Set` of used indices). Its log ended with a revision target to reproduce the count-map form, which was never done because DSA stopped on 2026-06-26. Five months later the structure came back but the insight did not.

**Storing positions in a map (`Map<key, Deque or Stack of indices>`) has now happened six times.** Five times a count, a running variable or a sorted index array was enough; in find-mirror-score and mock 1 Q4 the positions were needed and only the map itself was extra.

| When       | Problem                                                 | Rating | Result               | What was enough                                 | Where the WAs were                         |
| ---------- | ------------------------------------------------------- | -----: | -------------------- | ----------------------------------------------- | ------------------------------------------ |
| 2026-05-30 | find-mirror-score-of-a-string                           |   1578 | WA then AC, 44 min   | positions needed; 26 stacks in an array, no map | map bookkeeping, a new stack overwrote one |
| 2026-06-01 | find-original-array-from-doubled-array                  |   1557 | clean, 49 min        | a count per value                               | none                                       |
| 2026-06-02 | sentence-similarity-iii                                 |   1589 | 3 WAs, about 2 hours | prefix plus suffix two pointers, no map         | all three inside the matching machinery    |
| 2026-06-15 | maximum-width-ramp                                      |   1608 | clean                | indices sorted by value, or a monotonic stack   | none                                       |
| 2026-11-20 | minimum-operations-to-make-a-special-number (mock 1 Q4) |   1588 | hinted, about 59 min | two scans per ending pair, no map               | none                                       |
| 2026-11-21 | array-of-doubled-pairs (mock 3 Q3)                      |   1548 | 1 WA, 49 min         | a count per value                               | the extra pair counter                     |

The related form, a stack or heap that collapses to one variable: push-dominoes, 1638 (a running index), minimize-maximum-component-cost, 1642 (a heap over already sorted edges), car-fleet, 1678 (a running max), construct-smallest-number-from-di-string, 1642 (reversing a block).

1. **Every WA in the table sat in the added bookkeeping, not in the idea.**
2. **It costs time even without a WA:** 44 minutes to about 2 hours each, against a bar of 20.
3. **The counter-example worked.** On 2026-06-02, number-of-ways-where-square-of-number-is-equal-to-product-of-two-numbers (rating 1594): the question of counts or positions was asked, a `Map<Long,Integer>` count chosen, clean in 22 minutes.
4. **The check already exists** as the minimal-tool check at `extendedClaude.md:138`: before reaching for a map of positions, ask whether counts or positions are needed. It was not asked during today's derivation.

**Cold re-solve:** 2026-11-22, in the count form, from a blank editor, starting with the rewritten question in one line. Q4 stays unseen and is a fresh attempt, not an upsolve.
