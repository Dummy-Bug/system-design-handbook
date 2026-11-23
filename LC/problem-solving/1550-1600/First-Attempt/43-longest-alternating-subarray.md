# 43 — Longest Alternating Subarray

- **Link:** https://leetcode.com/problems/longest-alternating-subarray/ (LC 2765, rating 1581, AR 35.3%)
- **Format:** single timed problem under the 2026-11-22 format (15-minute target, 30-minute cap), unseen. LeetCode marks it Easy; the user found it was not.
- **Bucket (revealed after the solve):** enumeration by LeetCode tag; solved here with a two-pointer run scan.
- **Timer:** 2026-11-23, 06:37.
- **AC:** 07:20, 43 minutes.
- **Result:** editorial. One WA (2435 of 2880), then the step-by-step explanation after the cap, and the user asked for the full fix after step 2. Does not count toward coverage: enumeration stays at 0 of 2.
- **Cold re-solve owed:** 2026-11-24 or later, from a blank editor, starting from the rewritten question below.

**Rewritten question:** find the longest run whose steps go +1, −1, +1, ...; when a run breaks, the next run can only start at the element just before the break.

## The problem

A subarray `s` of length `m > 1` is alternating when `s1 = s0 + 1` and the differences then alternate −1, +1, −1, and so on, so `s` looks like `[s0, s0 + 1, s0, s0 + 1, ...]`. Return the longest alternating subarray's length, or −1. `2 <= nums.length <= 100`.

## Timeline

| Time  |     At | What                                                                                                                                                                                    |
| ----- | -----: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 06:37 |  0 min | Timer started.                                                                                                                                                                          |
| 06:54 | 17 min | Idea from the equation: at an odd offset from the start the difference must be 1, at an even offset 0, so two pointers or a sliding window. The one-word check was yes. Started coding. |
| 07:04 | 27 min | Pasted the WA (2435 of 2880) and started debugging. The exact submit time was not logged; it was before this.                                                                           |
| 07:09 | 32 min | Past the cap, asked what was wrong (time approximate). Step 1: the trace below. The user had found the same issue but could not see the fix.                                            |
| 07:14 | 37 min | Step 2, on a break jump `left` to `right − 1`, did not land at first; it landed on a smaller example, and the user restated it correctly.                                               |
| 07:16 | 39 min | Asked for the full solution; given as their own code with the two `else` branches changed.                                                                                              |
| 07:20 | 43 min | AC.                                                                                                                                                                                     |

## The WA

**WA-cause [incomplete-validation] [untraced-submit]:** on a break the code moved `left` up by one and only ever compared the new `nums[right]` with `nums[left]`, so the elements already inside the window were never checked against the new start. Moving the start by one flips every offset, so the window was broken from its second element and still grew. Failing case `[64,65,64,65,64,65,66,65,66,65]`: got 9, expected 6.

The trace of the WA code on the failing case, run:

| Step          | left | right | Window                             | Length |
| ------------- | ---: | ----: | ---------------------------------- | -----: |
| valid run     |    0 |     5 | 64, 65, 64, 65, 64, 65             |      6 |
| break at 66   |    1 |     6 | `left` moves 0 to 1                |        |
| keeps growing |    1 |     9 | 65, 64, 65, 64, 65, 66, 65, 66, 65 |      9 |

From index 1 the pattern should be 65, 66, 65, ...; index 2 is 64, so the window is broken from its second element.

Both examples pass with the bug (run: 4 and 2), as in #42 and mock 4. The smaller case `[3,4,3,4,5,4]`, a run broken by a step of +1, gives 5 instead of 4 and would have caught it as a Step 3 edge case.

## Why `right − 1`

When a run breaks at `right`, every start inside it is useless: a start at an even offset gives a piece of the same run, which ends at the same break and is shorter, and a start at an odd offset is shifted, the broken pattern above. The only new start is the element just before the break, since (`nums[right − 1]`, `nums[right]`) may be a fresh +1. If `left` is already `right − 1`, that pair failed too, so `left` goes to `right`.

On `[3,4,3,4,5,4]`, the run 3, 4, 3, 4 breaks at index 4:

| Start at | Window from there   | Useful? |
| -------: | ------------------- | :-----: |
|        1 | 4, 3 ... goes down  |    ✗    |
|        2 | 3, 4, then 5 breaks |    ✗    |
|        3 | 4, 5, 4             |    ✓    |

## First attempt (WA)

```java
class Solution {
    public int alternatingSubarray(int[] nums) {
        
        int right = 1;
        int left = 0;
        int maxLength = -1;

        while (right < nums.length){

            if (left == right) {
                right = right + 1;
                continue;
            }
            
            if (((right - left)&1) == 0){

                if (nums[right] - nums[left] == 0){
                    maxLength = Math.max(right - left + 1 , maxLength);
                    right++;
                }
                else {
                    left++;
                }
            }
            else{
                if (nums[right] - nums[left] == 1){
                    maxLength = Math.max(right - left + 1, maxLength);
                    right++;
                }
                else {
                    left++;
                }
            }
        }
        return maxLength;
    }
}
```

## AC code, the owned solution

The user chose this over both versions below.

```java
class Solution {
    public int alternatingSubarray(int[] nums) {
        
        int right = 1;
        int left = 0;
        int maxLength = -1;

        while (right < nums.length){

            if (left == right) {
                right = right + 1;
                continue;
            }
            
            if (((right - left)&1) == 0){

                if (nums[right] - nums[left] == 0){
                    maxLength = Math.max(right - left + 1 , maxLength);
                    right++;
                }
                else {
                    left = (left == right - 1) ? right : right - 1;
                }
            }
            else{
                if (nums[right] - nums[left] == 1){
                    maxLength = Math.max(right - left + 1, maxLength);
                    right++;
                }
                else {
                    left = (left == right - 1) ? right : right - 1;
                }
            }
        }
        return maxLength;
    }
}
```

Run: 4 and 2 on the examples, 6 on the failing case, and the same output as a brute force on 200,000 random arrays.

## Asides

Both compare neighbours instead of `nums[left]`: the steps must go +1, −1, +1, ..., so no offset parity is needed. Both were run: 4, 2 and 6 on the examples and the failing case, and the same output as a brute force on 200,000 random arrays.

**The editorial, try every start.** With `n <= 100`, O(n²) is nothing, and with every start tried there is no question of where `left` goes after a break; the constraint was the signal that brute force was enough.

```java
class Solution {
    public int alternatingSubarray(int[] nums) {
        int ans = -1, n = nums.length;
        for (int i = 0; i < n; ++i) {
            int k = 1;
            int j = i;
            for (; j + 1 < n && nums[j + 1] - nums[j] == k; ++j) {
                k *= -1;
            }
            if (j - i + 1 > 1) {
                ans = Math.max(ans, j - i + 1);
            }
        }
        return ans;
    }
}
```

**One pass.** `expectedDiff` is the step the run needs next; a break with a +1 starts a new run of length 2 at `i − 1`, the same move as `left = right − 1`.

```java
class Solution {
    public int alternatingSubarray(int[] nums) {
        int longest = -1;
        int runLength = 0;
        int expectedDiff = 1;

        for (int i = 1; i < nums.length; i++) {
            int diff = nums[i] - nums[i - 1];

            boolean continuesRun = runLength > 0 && diff == expectedDiff;
            boolean startsNewRun = diff == 1;

            if (continuesRun) {
                runLength++;
                expectedDiff = -expectedDiff;
            } else if (startsNewRun) {
                runLength = 2;
                expectedDiff = -1;
            } else {
                runLength = 0;
            }

            if (runLength > 0) {
                longest = Math.max(longest, runLength);
            }
        }
        return longest;
    }
}
```
