### #14 — Binary Subarrays With Sum
**Link:** https://leetcode.com/problems/binary-subarrays-with-sum/
**Date attempted:** 2026-05-26
**Rating:** 1550–1600 band (Phase 1 acquisition)
**Time:** 26 min (13 min derivation + 13 min coding) — first-submission AC ✓
**Pattern:** Sliding window

---

**Verbatim thinking:**

- can't directly find subarrays with sum exactly = goal using sliding window (shrinking the window is ambiguous — multiple valid lefts)
- but CAN find subarrays with sum ≤ goal using standard sliding window
- so: atMost(goal) - atMost(goal - 1) = exactly(goal)
- s1 = s2 + s3 → s1 - s2 = s3 where s1 = atMost(goal), s2 = atMost(goal-1), s3 = exactly(goal)
- traced through an example to confirm

**Insight:**
"Exactly K" sliding window problems can't be solved directly because the window has multiple valid left boundaries. Convert to atMost(K) - atMost(K-1) = exactly(K). Each atMost is a standard shrinking window.

**Key gotcha:**
Handle goal = 0 — atMost(-1) should return 0 (no valid subarrays with negative sum).

**Complexity:**
O(n) time, O(1) space.

**Alternative approaches (not explored — revisit if needed at higher bands):**
1. **Prefix sum + hashmap** — count prefix sums in a map, for each j check if `prefixSum[j] - goal` exists. O(n) time, O(n) space.
2. **Single-pass sliding window** — track two left pointers (one for sum ≤ goal, one for sum ≤ goal-1) in a single pass instead of two separate passes. O(n) time, O(1) space, single pass.

**Solution code:**

```java
class Solution {

    private int getSumLessThanGoal(int[] nums, int goal){
        int n = nums.length;
        int i = 0;
        int j = 0;
        int ans = 0;
        int sum = 0;

        while( j < n){
            sum += nums[j];

            if (sum < goal){
                ans += j - i + 1;
            }
            else if (sum == goal){
                while( i <= j && sum == goal){
                    sum -= nums[i];
                    i++;
                }
                if (i <= j){
                     ans += j - i + 1;
                }
            }
            j++;
        }
        return ans;
    }

    private int getSumLessThanEqualToGoal(int[] nums, int goal){
        int n = nums.length;
        int i = 0;
        int j = 0;
        int ans = 0;
        int sum = 0;

        while ( j < n ){
            sum += nums[j];

            if ( sum <= goal){
                ans += j - i + 1;
            }
            else if (sum > goal){
                while ( i <= j && sum > goal){
                    sum -= nums[i];
                    i++;
                }
                if (i <= j){
                    ans += j - i + 1;
                }
            }
            j++;
        }
        return ans;
    }

    public int numSubarraysWithSum(int[] nums, int goal) {
        return getSumLessThanEqualToGoal(nums, goal) - getSumLessThanGoal(nums, goal);
    }
}
```
