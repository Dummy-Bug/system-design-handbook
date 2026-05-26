// Sum of Digit Differences of All Pairs
// https://leetcode.com/problems/sum-of-digit-differences-of-all-pairs/
// Band: 1600-1650 (~1600) | Second-Attempt #7 | 2026-05-26
// Verdict: clean first-submission AC, self-derived, 27 min (First-Attempt was 55 min)
//
// Approach: per-digit-position contribution. For each position, scan left->right with a
// digit-frequency map; at element i, (i+1)-(count+1) = i-count = #earlier elements that
// DIFFER at this position. Sum across all i and all positions. O(d*n) time, O(1) space.
//
// Review flags (no bug, habit only):
//  - [checklist #2] (int)Math.pow(10,i) is the float-cast-trap shape; AC'd only because
//    powers of 10 <= 1e15 are exact doubles. Prefer integer peel (n%10; n/=10) or int[] pow10.
//  - Map<Integer,Long> over fixed 0-9 range -> int[10]/long[10] is the natural fit (no boxing).

class Solution {

    private int getDigit(int n, int i) {
        n = n / (int) Math.pow(10, i);
        return n % 10;
    }

    public long sumDigitDifferences(int[] nums) {

        Map<Integer, Long> freq = new HashMap<>();
        int n = nums.length;

        int digitCount = Integer.toString(nums[0]).length();
        long ans = 0;

        while (digitCount != 0) {

            digitCount--;

            for (int i = 0; i < n; i++) {

                int digit = getDigit(nums[i], digitCount);

                long count = freq.getOrDefault(digit, 0L);
                long difference = (i + 1) - (count + 1);
                ans = ans + difference;
                freq.put(digit, count + 1);
            }
            freq.clear();
        }
        return ans;
    }
}
