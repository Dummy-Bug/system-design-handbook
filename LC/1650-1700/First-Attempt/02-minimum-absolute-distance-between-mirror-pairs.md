# Minimum Absolute Distance Between Mirror Pairs — First Attempt

## Problem

You are given an integer array nums.

A mirror pair is a pair of indices (i, j) such that:

	0 <= i < j < nums.length, and

	reverse(nums[i]) == nums[j], where reverse(x) denotes the integer formed by reversing the digits of x. Leading zeros are omitted after reversing, for example reverse(120) = 21.

Return the minimum absolute distance between the indices of any mirror pair. The absolute distance between indices i and j is abs(i - j).

If no mirror pair exists, return -1.

 

Example 1:

Input: nums = [12,21,45,33,54]

Output: 1

Explanation:

The mirror pairs are:

	(0, 1) since reverse(nums[0]) = reverse(12) = 21 = nums[1], giving an absolute distance abs(0 - 1) = 1.

	(2, 4) since reverse(nums[2]) = reverse(45) = 54 = nums[4], giving an absolute distance abs(2 - 4) = 2.

The minimum absolute distance among all pairs is 1.

Example 2:

Input: nums = [120,21]

Output: 1

Explanation:

There is only one mirror pair (0, 1) since reverse(nums[0]) = reverse(120) = 21 = nums[1].

The minimum absolute distance is 1.

Example 3:

Input: nums = [21,120]

Output: -1

Explanation:

There are no mirror pairs in the array.

 

Constraints:

	1 <= nums.length <= 10^5

	1 <= nums[i] <= 10^9​​​​​​​

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-13 |
| Link | https://leetcode.com/problems/minimum-absolute-distance-between-mirror-pairs/description/ |
| Rating | 1669 |
| AC | Y |
| Time | ~40min |
| Pattern | HashMap lookup — right-to-left traversal with closest-index override |
| Revision due | 2026-05-27 |

---

#### Thought process (what was actually going through the mind)

**Step 1 — Constraint reading**
- nums[i] all positive → no negative number handling needed
- nums[i] ≤ 10^9 → large but no arithmetic overflow risk since we're not summing

**Step 2 — Approach**
Treated reversing digits as a blackbox initially. Core idea: for each num, compute its reverse and check if that reverse already exists in a HashMap. If yes, compute index distance and track minimum. Store num → index in map as you go.

Override rule: if the same number appears again, override with the latest index — minimizes distance for future lookups.

Palindrome numbers (reverse == itself, e.g. 33) handled automatically — treated as any other mirror pair.

Traced all three sample test cases before coding. All matched.

**Step 3 — Reverse function**
Only open question was handling leading zeros after reversing (e.g. reverse(120) = 021 = 21). Derived that integer arithmetic handles this naturally — building `rev = rev * 10 + n % 10` in a loop until n == 0 drops leading zeros automatically since integers don't store them.

**Step 4 — Right-to-left traversal insight**
Iterated right to left. By overriding map entries with smaller indices as traversal progresses left, the map always holds the **closest** occurrence of any number to the right of the current position. Every lookup gives minimum possible distance to the right automatically.

---

#### What should have been thought (gaps)

No significant gaps. Approach was clean and self-derived. The one thing worth noting: the right-to-left traversal with override was implicit in the solution — making the reasoning explicit ("map always holds closest right occurrence") would have made the correctness argument clearer upfront.

---

#### Complexity

O(n · log C) time where C = max value (log C = number of digits to reverse). O(n) space.

---
