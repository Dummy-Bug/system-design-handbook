# 41 — Longest Palindrome by Concatenating Two Letter Words

- **Link:** https://leetcode.com/problems/longest-palindrome-by-concatenating-two-letter-words/ (LC 2131, rating 1557, AR 53.5%)
- **Format:** single timed problem, the first under the 2026-11-22 format (15-minute target, 30-minute cap), unseen.
- **Bucket (revealed after the solve):** hash table / counting.
- **Dealt:** 2026-11-22, timer 19:57.
- **AC:** 20:36, 39 minutes.
- **Result:** clean first-submission AC, self-derived, over the 30-minute cap. The version with the bug was only run on the examples, never submitted. Counts toward coverage: hash table / counting 1 of 2.

## The problem

Each word has exactly two lowercase letters. Pick some words and concatenate them in any order to make the longest palindrome; each word used at most once. Return its length, or 0. `1 <= words.length <= 10^5`.

## Timeline

| Time  |     At | What                                                                                                                           |
| ----- | -----: | ------------------------------------------------------------------------------------------------------------------------------ |
| 19:57 |  0 min | Timer started.                                                                                                                 |
| 20:05 |  8 min | Plan: a frequency map; a second pass looks up each word's reverse, skips it if absent or already done, else takes the count.   |
| 20:10 | 13 min | Ran the approach on example 3 as the Step 2 trace; it surfaced one more case. Started coding.                                  |
| 20:35 | 38 min | Over the cap; the code gave 10 instead of 8 on example 2. Already debugging example 2 and found the one place it over-counted. |
| 20:36 | 39 min | Removed that line; AC on the first submission.                                                                                 |

The idea took 8 minutes. The other 26 went on one rule the trace never tested: only a word with two equal letters, like `gg`, can sit alone in the middle.

## The bug, found locally

The version at the stop set the middle flag whenever a word had no reverse in the map: `if (c2 == 0) isExtra = true;`. So an unpaired `ab` was treated as a middle word. Example 2, `[ab, ty, yt, lc, cl, ab]`, has an unpaired `ab` and gave 10 instead of 8. Example 3 has no unpaired word, so the Step 2 trace on it could not show the gap.

**Habit:** run Step 2 on the richest example, the one with the most kinds of case in it. Here that was example 2: a reverse pair, and an unpaired word.

## The approach

Count every word. A word with two different letters pairs with its reverse, and each pair adds 4 letters. A word with two equal letters pairs with itself, 4 letters per two copies. If any equal-letter word has an odd count, one copy goes in the middle for 2 more letters. O(n). This is the editorial's Solution 1 (greedy plus hash table).

## AC code, as submitted

The debug `println` was left in, as in Weekly 529 Q2.

```java
class Solution {
    public int longestPalindrome(String[] words) {
        
        Map<String,Integer> map = new HashMap<>();

        for (String word : words){
            map.put(word , 1 + map.getOrDefault(word , 0));
        }

        int ans = 0;
        boolean isExtra = false;
        Set<String> set = new HashSet<>();

        for (String word : words){

            if (set.contains(word)){
                continue;
            }

            int c1 = map.get(word);

            String palindrome = String.valueOf(word.charAt(1)) + String.valueOf(word.charAt(0) );
            
            if (word.charAt(1) == word.charAt(0)){
                if (c1 %2 != 0){
                    isExtra = true;
                }
                ans = ans + 4*(c1/2) ;
                set.add(word);
                continue;
            }

            
            int c2 = map.getOrDefault(palindrome , 0);
            ans = ans + 4*Math.min(c1,c2);
            System.out.println(word + " " + palindrome + " " + c1 + " " + c2);
            set.add(word);
            set.add(palindrome);
        }
        if (isExtra){
            ans += 2;
        }
        return ans;
    }
}
```

## A tidier version

Walking the map's keys instead of `words` brings each distinct word up once, so the done set goes away; counting a pair like `ab` and `ba` only from the side that sorts first keeps it from being added twice. Run: 6, 8 and 2 on the three examples, and the same output as the AC code on 200,000 random inputs.

```java
class Solution {
    public int longestPalindrome(String[] words) {
        Map<String, Integer> count = new HashMap<>();
        for (String word : words) {
            count.put(word, count.getOrDefault(word, 0) + 1);
        }

        int ans = 0;
        boolean hasMiddle = false;

        for (String word : count.keySet()) {
            int c = count.get(word);
            String reverse = "" + word.charAt(1) + word.charAt(0);

            if (word.equals(reverse)) {
                ans += 4 * (c / 2);
                if (c % 2 == 1) hasMiddle = true;
            } else if (word.compareTo(reverse) < 0) {
                ans += 4 * Math.min(c, count.getOrDefault(reverse, 0));
            }
        }
        return hasMiddle ? ans + 2 : ans;
    }
}
```
