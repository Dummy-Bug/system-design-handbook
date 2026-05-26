# Identify the Largest Outlier in an Array — First Attempt

## Problem

You are given an integer array nums. This array contains n elements, where exactly n - 2 elements are special numbers. One of the remaining two elements is the sum of these special numbers, and the other is an outlier.

An outlier is defined as a number that is neither one of the original special numbers nor the element representing the sum of those numbers.

Note that special numbers, the sum element, and the outlier must have distinct indices, but may share the same value.

Return the largest potential outlier in nums.

 

Example 1:

Input: nums = [2,3,5,10]

Output: 10

Explanation:

The special numbers could be 2 and 3, thus making their sum 5 and the outlier 10.

Example 2:

Input: nums = [-2,-1,-3,-6,4]

Output: 4

Explanation:

The special numbers could be -2, -1, and -3, thus making their sum -6 and the outlier 4.

Example 3:

Input: nums = [1,1,1,1,1,5,5]

Output: 5

Explanation:

The special numbers could be 1, 1, 1, 1, and 1, thus making their sum 5 and the other 5 as the outlier.

 

Constraints:

	3 <= nums.length <= 10^5

	-1000 <= nums[i] <= 1000

	The input is generated such that at least one potential outlier exists in nums.

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-13 |
| Link | https://leetcode.com/problems/identify-the-largest-outlier-in-an-array/ |
| Rating | 1644 |
| AC | Y (hinted) |
| Time | 135min (2h 15m) |
| Pattern | HashMap lookup / algebraic rearrangement |
| Revision due | 2026-05-27 |
| Remark | **First hinted pass in this band.** Spent 60+ min stuck on wrong approach (tracking max/second-max with absolute values). Hint received — "convert O(n²) brute force to O(n) lookup via algebra." Self-derived the math: tSum = 2·sum_element + outlier → sum_element = (tSum - outlier)/2. So for each outlier candidate, target value is determined; just check existence. **Real gap was recognition, NOT data-structure knowledge.** I know set vs freq map cold — but a value-based check (`is target present?`) under an index-based constraint (`distinct indices, may share values`) means the matched value can alias the *same physical element* I'm standing on. I never asked "could the only copy of target be the candidate itself?", so the freq map looked pointless — nothing to defend against. The miss is failing to *see* the collision, not failing to *fix* it. Collision happens exactly when `target == outlier_value` ⇔ `tSum = 3·z`. Failing test: `[1,2,4,5]` returns 4 (fake) instead of 2 (real) because 4 = tSum/3 appears once; set false-positives, freq map with `count ≥ 2` self-guard rejects it. Complexity: O(n) time, O(n) space. |

---

> [!note] Verbatim thinking and full solution code were **not captured** on the first attempt (it predates the per-attempt archive). Only the logged insight/remark above survives. Full verbatim + inlined code begin from the second attempt onward.
