### #20 — Pancake Sorting
**Link:** https://leetcode.com/problems/pancake-sorting/
**Date attempted:** 2026-05-27 ~21:05
**Rating:** 1550–1600 band (Phase 1 acquisition)
**Time:** 58 min (25 min approach + 33 min coding) — first-submission AC ✓
**Pattern:** Greedy / observation

---

**Verbatim thinking:**

- first 21 min: considered reverse-or-not at each index (2 choices per element) — too expensive
- knew topic was greedy but couldn't see how
- key realization: fix elements from largest to smallest. Once fixed at the end, they stay out of future flips
- for each element (largest first): find its current position, flip it to index 0, then flip it to its required position
- if already in correct position, skip

**Insight:**
Fix elements from largest to smallest. For each element: (1) flip prefix up to its current position → moves it to index 0, (2) flip prefix up to its target position → places it correctly. Once placed, it's at the end and never touched again.

**Key gotcha:**
The flip operation is `reverse(0..k-1)` but the answer records `k` (1-indexed length). So `position + 1` and `requiredPosition + 1` go into the answer list. Also skip if element is already in the right spot.

**Complexity:**
O(n²) time, O(n) space (answer list).

**Solution code:**

```java
class Solution {

    private int findPosition(int[] nums, int num){
        
        int n = nums.length;

        for (int i = 0; i < n; i++){
            if (nums[i] == num){
                return i;
            }
        }
        return -1;
    }

    private void reverse(int [] nums, int k){

        int i = 0;
        int j = k;

        while( i < j){
            int temp = nums[i];
            nums[i] = nums[j];
            nums[j] = temp;
            i++;
            j--;
        }

    }
    public List<Integer> pancakeSort(int[] nums) {
        
        int n = nums.length;
        List<Integer> ans = new ArrayList<>();

        while( n!= 0){
            
            int position = findPosition(nums,n);
            int requiredPosition = n - 1;
            
            if (position != requiredPosition){
                ans.add(position + 1);
                reverse(nums,position);

                ans.add(requiredPosition + 1);
                reverse(nums,requiredPosition);
            }
            n = n - 1; 
        }
        return ans;

    }
}
```
