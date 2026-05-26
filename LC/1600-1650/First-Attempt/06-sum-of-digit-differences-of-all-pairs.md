# Sum of Digit Differences of All Pairs — First Attempt

## Problem

You are given an array nums consisting of positive integers where all integers have the same number of digits.

The digit difference between two integers is the count of different digits that are in the same position in the two integers.

Return the sum of the digit differences between all pairs of integers in nums.

 

Example 1:

Input: nums = [13,23,12]

Output: 4

Explanation:
We have the following:
- The digit difference between 13 and 23 is 1.
- The digit difference between 13 and 12 is 1.
- The digit difference between 23 and 12 is 2.
So the total sum of digit differences between all pairs of integers is 1 + 1 + 2 = 4.

Example 2:

Input: nums = [10,10,10,10]

Output: 0

Explanation:
All the integers in the array are the same. So the total sum of digit differences between all pairs of integers will be 0.

 

Constraints:

	2 <= nums.length <= 10^5

	1 <= nums[i] < 10^9

	All integers in nums have the same number of digits.

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-12 |
| Link | https://leetcode.com/problems/sum-of-digit-differences-of-all-pairs/description/ |
| Rating | 1645 |
| AC | Y |
| Time | 55min |
| Pattern | Digit position iteration / frequency counting |
| Revision due | 2026-05-26 |
| Remark | Self-derived, no gotchas during 15-min coding. 40 min spent deriving O(n·d) approach from first principles. Key insight: iterate each digit position separately. For each number at position j, count how many *previous* numbers (0 to j-1) have same digit — contribution = (j+1) - count. Incremental accumulation avoids formula approach's division-by-2 trap. Complexity: O(n·d) time (n numbers, d digit positions), O(1) space (at most 10 digits per position). |

---

> [!note] Verbatim thinking and full solution code were **not captured** on the first attempt (it predates the per-attempt archive). Only the logged insight/remark above survives. Full verbatim + inlined code begin from the second attempt onward.
