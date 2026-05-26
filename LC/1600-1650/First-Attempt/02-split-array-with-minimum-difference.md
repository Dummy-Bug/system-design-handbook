# Split Array with Minimum Difference — First Attempt

## Problem

You are given an integer array nums.

Split the array into exactly two subarrays, left and right, such that left is strictly increasing  and right is strictly decreasing.

Return the minimum possible absolute difference between the sums of left and right. If no valid split exists, return -1.

 

Example 1:

Input: nums = [1,3,2]

Output: 2

Explanation:

	
		
			i
			left
			right
			Validity
			left sum
			right sum
			Absolute difference
		
	
	
		
			0
			[1]
			[3, 2]
			Yes
			1
			5
			|1 - 5| = 4
		
		
			1
			[1, 3]
			[2]
			Yes
			4
			2
			|4 - 2| = 2
		
	

Thus, the minimum absolute difference is 2.

Example 2:

Input: nums = [1,2,4,3]

Output: 4

Explanation:

	
		
			i
			left
			right
			Validity
			left sum
			right sum
			Absolute difference
		
	
	
		
			0
			[1]
			[2, 4, 3]
			No
			1
			9
			-
		
		
			1
			[1, 2]
			[4, 3]
			Yes
			3
			7
			|3 - 7| = 4
		
		
			2
			[1, 2, 4]
			[3]
			Yes
			7
			3
			|7 - 3| = 4
		
	

Thus, the minimum absolute difference is 4.

Example 3:

Input: nums = [3,1,2]

Output: -1

Explanation:

No valid split exists, so the answer is -1.

 

Constraints:

	2 <= nums.length <= 10^5

	1 <= nums[i] <= 10^5

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-08 |
| Link | https://leetcode.com/problems/split-array-with-minimum-difference/ |
| Rating | 1649 |
| AC | Y |
| Time | 120min |
| Pattern | two-pointer / greedy validation |
| Revision due | 2026-05-22 |
| Remark | Self-derived with WA edge case debugs. Insight: for each split position i, check if nums[0..i] strictly increasing AND nums[i+1..n-1] strictly decreasing via on-the-fly validation (no extra boolean arrays). Key gotcha — boundary conditions at split point and when entire array is increasing/decreasing. Complexity: O(n^2) time (n positions × O(n) validation per position), O(1) space. |

---

> [!note] Verbatim thinking and full solution code were **not captured** on the first attempt (it predates the per-attempt archive). Only the logged insight/remark above survives. Full verbatim + inlined code begin from the second attempt onward.
