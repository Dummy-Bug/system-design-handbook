# Longest Common Prefix Between Adjacent Strings After Removals — First Attempt

## Problem

You are given an array of strings words. For each index i in the range [0, words.length - 1], perform the following steps:

	Remove the element at index i from the words array.

	Compute the length of the longest common prefix among all adjacent pairs in the modified array.

Return an array answer, where answer[i] is the length of the longest common prefix between the adjacent pairs after removing the element at index i. If no adjacent pairs remain or if none share a common prefix, then answer[i] should be 0.

 

Example 1:

Input: words = ["jump","run","run","jump","run"]

Output: [3,0,0,3,3]

Explanation:

	Removing index 0:
	
		words becomes ["run", "run", "jump", "run"]

		Longest adjacent pair is ["run", "run"] having a common prefix "run" (length 3)

	
	

	Removing index 1:
	
		words becomes ["jump", "run", "jump", "run"]

		No adjacent pairs share a common prefix (length 0)

	
	

	Removing index 2:
	
		words becomes ["jump", "run", "jump", "run"]

		No adjacent pairs share a common prefix (length 0)

	
	

	Removing index 3:
	
		words becomes ["jump", "run", "run", "run"]

		Longest adjacent pair is ["run", "run"] having a common prefix "run" (length 3)

	
	

	Removing index 4:
	
		words becomes ["jump", "run", "run", "jump"]

		Longest adjacent pair is ["run", "run"] having a common prefix "run" (length 3)

	
	

Example 2:

Input: words = ["dog","racer","car"]

Output: [0,0,0]

Explanation:

	Removing any index results in an answer of 0.

 

Constraints:

	1 <= words.length <= 10^5

	1 <= words[i].length <= 10^4

	words[i] consists of lowercase English letters.

	The sum of words[i].length is smaller than or equal 10^5.

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-15 |
| Link | https://leetcode.com/problems/longest-common-prefix-between-adjacent-strings-after-removals/description/ |
| Rating | TBD |
| AC | Y |
| Time | 47min (fully self-derived) |
| Pattern | Left-right prefix precomputation |
| Revision due | 2026-05-29 |

---

#### Thought process (what was actually going through the mind)

**Step 1 — Constraint reading (done first)**
- words.length ≤ 10^5
- words[i].length ≤ 10^4
- **Sum of words[i].length ≤ 10^5** ← key constraint

**Step 2 — Complexity analysis from the sum constraint**
Initial instinct was "n² won't pass." But the sum constraint changes the picture significantly.

Brute force complexity is O(n × m × l) where:
- n = number of words
- m = number of comparisons per removal (n-1 adjacent pairs)
- l = length of each word during comparison

The sum constraint means total characters across all words ≤ 10^5. So you cannot simultaneously have 10^5 words each of length 10^4 — those are competing limits. The worst cases are:
- 10^5 words of length 1 each
- 1 word of length 10^5

This means: even with a nested comparison loop, the total character work is capped. The "third loop" for string comparison doesn't independently scale — it's bounded by the sum. So the algorithm complexity collapses from O(n³) naive → O(n²) effective maximum, because l is not a free variable when the sum is fixed.

*Good: this is the correct read of sum-of-lengths constraints. Not every constraint that looks like n³ actually is.*

**Step 3 — Approach (23 min mark)**
Identified left-right prefix precomputation as the direction. Two arrays:
- `left[i]` = max prefix length among all adjacent pairs in words[0..i]
- `right[i]` = max prefix length among all adjacent pairs in words[i..n-1]

When removing index i, the answer is `max(left[i-1], right[i+1])`, plus a special case for the newly adjacent pair `(words[i-1], words[i+1])`.

**Step 4 — First submission (wrong)**
Initially used `word.equals(words[i+1])` (full equality) instead of computing prefix length. Caught the bug only after submission failed — the problem asks for longest common *prefix*, not equality. Fixed by extracting a proper `getPrefixLength(w1, w2)` helper.

*Note: the bug came from looking at sample examples where adjacent equal words (e.g. "run","run") made equality and prefix length identical. The prefix vs equality distinction only surfaces when adjacent words share a prefix but aren't equal.*

---

#### Closing notes

**Key insight:** Left-right precomputation is the standard tool whenever you need "best result if element i is removed" from a linear sequence. Build prefix-max from the left, suffix-max from the right, then combine with a bridge check for the newly adjacent pair that forms across the gap.

**Bug worth remembering:** Sample test cases only had equal adjacent words ("run","run") — prefix length equals full length there. The prefix vs equality distinction only shows up when words share a prefix but aren't equal (e.g. "runner","run"). Always test against non-equal prefix cases before submitting.

**Tracker:** 8/10 done in 1650-1700 band. 2 more to complete the set.

---
