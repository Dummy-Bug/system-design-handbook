### #19 — Count Number of Maximum Bitwise-OR Subsets
**Link:** https://leetcode.com/problems/count-number-of-maximum-bitwise-or-subsets/
**Date attempted:** 2026-05-27 ~19:20
**Rating:** 1550–1600 band (Phase 1 acquisition)
**Time:** 20 min — first-submission AC ✓
**Pattern:** Bit operations / XOR (subset enumeration)

---

**Verbatim thinking:**

- n ≤ 16, so 2^16 = ~65K — enumerate all subsets is fine
- OR only increases or stays the same, so max OR = OR of all elements
- precompute maxOr by OR-ing all elements
- generate all subsets via include/exclude recursion, count those whose OR equals maxOr
- subsets are unique by indices, not values — no dedup needed

**Insight:**
n ≤ 16 is the giveaway for subset enumeration (2^16 ≈ 65K). Max OR = OR of all elements (OR is monotonically non-decreasing). Generate all subsets, count matches.

**Key gotcha:**
None — straightforward once you see n ≤ 16 and that max OR is just OR of everything.

**Also solvable via (revisit when bitmask DP appears at higher bands):**
1. **Bitmask enumeration** — iterate all masks 0 to 2^n-1, compute OR per mask
2. **DP on bits** — track OR values and their counts as you add elements
3. **Bitmask DP** — full bitmask DP approach

These are noise at n ≤ 16 brute force, but bitmask DP will matter when n is larger. Come back here when that pattern lands.

**Complexity:**
O(2^n) time, O(n) space (recursion stack).

**Solution code:**

```java
class Solution {

    private int count = 0;
    private int maxOr = 0;

    private void helper(int i,int[] nums,int or){

        if (i == nums.length){
            if (or == maxOr){
                count++;
            }
            return;
        }

        helper(i + 1, nums, or | nums[i]);
        helper(i + 1, nums, or);
    }

    public int countMaxOrSubsets(int[] nums) {
        
        int n = nums.length;

        for (int i = 0; i < n; i++){
            maxOr |= nums[i];
        }

        helper(0,nums,0);
        return count;
    }
}
```
