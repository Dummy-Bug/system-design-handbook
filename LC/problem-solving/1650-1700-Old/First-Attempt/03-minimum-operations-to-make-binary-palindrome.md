# Minimum Operations to Make Binary Palindrome — First Attempt

## Problem

You are given an integer array nums.

For each element nums[i], you may perform the following operations any number of times (including zero):

	Increase nums[i] by 1, or

	Decrease nums[i] by 1.

A number is called a binary palindrome if its binary representation without leading zeros reads the same forward and backward.

Your task is to return an integer array ans, where ans[i] represents the minimum number of operations required to convert nums[i] into a binary palindrome.

 

Example 1:

Input: nums = [1,2,4]

Output: [0,1,1]

Explanation:

One optimal set of operations:

	
		
			nums[i]
			Binary(nums[i])
			Nearest
			Palindrome
			Binary
			(Palindrome)
			Operations Required
			ans[i]
		
	
	
		
			1
			1
			1
			1
			Already palindrome
			0
		
		
			2
			10
			3
			11
			Increase by 1
			1
		
		
			4
			100
			3
			11
			Decrease by 1
			1
		
	

Thus, ans = [0, 1, 1].

Example 2:

Input: nums = [6,7,12]

Output: [1,0,3]

Explanation:

One optimal set of operations:

	
		
			nums[i]
			Binary(nums[i])
			Nearest
			Palindrome
			Binary
			(Palindrome)
			Operations Required
			ans[i]
		
	
	
		
			6
			110
			5
			101
			Decrease by 1
			1
		
		
			7
			111
			7
			111
			Already palindrome
			0
		
		
			12
			1100
			15
			1111
			Increase by 3
			3
		
	

Thus, ans = [1, 0, 3].

 

Constraints:

	1 <= nums.length <= 5000

	^​​​​​​​1 <= nums[i] <=^ 5000

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-14 |
| Link | https://leetcode.com/problems/minimum-operations-to-make-binary-palindrome/description/ |
| Rating | 1657 |
| AC | Y |
| Time | ~1h (approach self-derived, `Integer.toBinaryString` and brute-force scan provided) |
| Pattern | Binary palindrome — brute force scan outward |
| Revision due | 2026-05-28 |

---

#### Thought process (what was actually going through the mind)

**Step 1 — Reading the problem**
Each nums[i] can be incremented or decremented by 1 per operation. A binary palindrome reads the same in binary forward and backward. Need minimum operations per element — so find the nearest binary palindrome to each nums[i] and return the absolute difference.

**Step 2 — Approach: mirror left half to right half**

Insight: the MSBs (left half) are higher-weight bits. Changing them costs more in absolute difference than changing the LSBs (right half). So keep the left half fixed and mirror it onto the right half — this gives a binary palindrome with minimum disturbance to the high-order bits.

Implementation: convert num to binary string, two-pointer from both ends, set `sb.charAt(j) = sb.charAt(i)` when they differ, then convert back to integer.

Traced on small cases (1, 2, 4, 6, 7, 12) — all matched expected output.

**Step 3 — Syntax bugs hit during coding**

Three bugs found before/after submitting:

1. `(int)bit` converts char to ASCII ('1' → 49, '0' → 48), not to digit value. Should be `bit - '0'`.
2. `return num` at the end of `findPalindrome` — the computed `palindromeNumber` was thrown away, returning the original number unchanged.
3. Incomplete `System.out.println` statement — syntax error.

**Step 4 — WA on nums = [3521]**

After fixing syntax bugs, output was 58, expected 38.

Traced: `3521 = 110111000001`. Mirror left to right → `110111111011 = 3579`. Distance = 58.

But `110110011011 = 3483` is also a binary palindrome. Distance = 38. Closer.

`3483` comes from decrementing the left half by 1 (`110111 → 110110`) and mirroring. The original approach never generated this candidate.

---

#### Root cause of the gap

The "fix left half, mirror to right" reasoning is correct in spirit — you don't want to change high-order bits because they're expensive. But it's incomplete.

Mirroring the current left half forces the right half to match it exactly. If the right half bits need to jump a lot upward to match, the resulting palindrome can be far above num. In that case, decrementing the left half by 1 (small MSB cost) and mirroring gives a palindrome below num that's closer overall.

The correct approach requires 3 candidates:
```
1. Mirror left half as-is        → P1
2. Mirror (left_half + 1)        → P2
3. Mirror (left_half - 1)        → P3
answer = min(|num - P1|, |num - P2|, |num - P3|)
```

The original approach only checked P1. P3 was the winner for 3521.

---

#### What should have been thought (gaps)

**Gap 1 — Single candidate is never enough for "nearest" problems**
Whenever the problem asks for the nearest X, the answer is rarely a single formula. It's always: generate a small set of candidates, compute distance to each, take the minimum. Should have asked "am I generating all plausible candidates?" before coding.

**Gap 2 — Test adversarial cases before submitting**
Tested only on the provided examples (all small, ≤ 12). Should have tested on a number where the right half is mostly 0s and the left half is mostly 1s — exactly the case where a large upward jump in the right half occurs and the decrement candidate wins.

**Gap 3 — `Integer.toBinaryString(n)` exists**
Manual bit extraction via `(n>>i)&1` and building a StringBuilder is 15 lines of code that can be replaced with one call. Java's standard library covers this. The syntax bugs (ASCII conversion, return value) were direct consequences of writing the manual version.

---

#### Complexity

O(n · D) time where D = distance to nearest binary palindrome (very small for nums[i] ≤ 5000). O(log n) space for the binary string.

**Note — why brute force over the 3-candidate mirroring fix:** given `nums[i] ≤ 5000`, the scan terminates in a handful of iterations. The 3-candidate approach is cleaner at scale but requires implementing left-half increment/decrement on binary strings, which introduces the same class of bit-manipulation bugs that caused the WA here. Brute force is correct, readable, and fast enough.

**Revision target:** implement the 3-candidate mirroring approach cleanly — extract left half as an integer, generate 3 palindromes by mirroring `left_half-1` / `left_half` / `left_half+1`, take min distance. O(log n) per number, no scan needed. Binary search approach if constraints were larger: precompute all binary palindromes up to the max, sort them, binary search for nearest to each num.

---
