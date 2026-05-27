### #17 — Ways to Make a Fair Array
**Link:** https://leetcode.com/problems/ways-to-make-a-fair-array/
**Date attempted:** 2026-05-27 ~17:30
**Rating:** 1550–1600 band (Phase 1 acquisition)
**Time:** 30 min (15 min approach + 15 min coding) — first-submission AC ✓
**Pattern:** Linear / grid / counting DP

---

**Verbatim thinking:**

- previously solved this on Sep 11, 2025
- prefix sum of odds and evens — removing element i shifts all elements after i, flipping their odd/even positions
- suffix prefix sums: build suffix odd[] and even[] arrays from right to left
- when removing index i, elements before i keep their positions, elements after i swap odd↔even
- so: new odd sum = left odd sum + right even sum, new even sum = left even sum + right odd sum
- fair if new odd sum == new even sum, equivalently 2 * totalOddSum == (totalSum - nums[i])

**Insight:**
Removing element at index i shifts all elements after i by one position, flipping their odd/even parity. Build suffix odd/even sums. For each removal candidate, the new odd sum = prefix odd (before i) + suffix even (after i), and similarly for even. Fair when both sums equal.

**Key gotcha:**
The parity flip only affects elements AFTER the removed index. Elements before keep their original positions. Need to track running prefix sums for the left side and use suffix arrays for the right side.

**Complexity:**
O(n) time, O(n) space.

**Solution code:**

```java
class Solution {
    public int waysToMakeFair(int[] nums) {
        
        int n = nums.length;
        long totalSum = 0;

        long[] odd = new long  [n];
        long[] even = new long [n];

        if (((n-1)&1  )== 1){
            even[n-1] = 0L;
            odd[n-1] = nums[n-1];
        }
        else {
            even[n-1] = nums[n-1];
            odd[n-1] = 0L;
        }
        
        totalSum = nums[n-1];

        for (int i = n-2; i >= 0; i--){
            
            if ((i&1) == 1){
                even[i] = even[i+1];
                odd[i] = nums[i] + odd[i+1];
            }
            else{
                even[i] = nums[i] + even[i+1];
                odd[i] = odd[i+1];
            }
            totalSum += nums[i];
        }


        long evenSum = 0;
        long oddSum = 0;
        int count = 0;

        for (int i = 0; i < n ; i++){

            if ((i&1) == 1){
                
                long totalOddSum = oddSum + even[i];
                
                if (2*totalOddSum == (totalSum - nums[i])){
                    count++;
                }
                oddSum += nums[i];
            }
            else {

                long totalEvenSum = evenSum + odd[i];

                if (2*totalEvenSum == (totalSum - nums[i])){
                    count++;
                }
                evenSum += nums[i];
            }
        }
        return count;
    }
}
```
