# Word Squares II — First Attempt

## Problem

You are given a string array words, consisting of distinct 4-letter strings, each containing lowercase English letters.

A word square consists of 4 distinct words: top, left, right and bottom, arranged as follows:

	top forms the top row.

	bottom forms the bottom row.

	left forms the left column (top to bottom).

	right forms the right column (top to bottom).

It must satisfy:

	top[0] == left[0], top[3] == right[0]

	bottom[0] == left[3], bottom[3] == right[3]

Return all valid distinct word squares, sorted in ascending lexicographic order by the 4-tuple (top, left, right, bottom)​​​​​​​.

 

Example 1:

Input: words = ["able","area","echo","also"]

Output: [["able","area","echo","also"],["area","able","also","echo"]]

Explanation:

There are exactly two valid 4-word squares that satisfy all corner constraints:

	"able" (top), "area" (left), "echo" (right), "also" (bottom)

	
		top[0] == left[0] == 'a'

		top[3] == right[0] == 'e'

		bottom[0] == left[3] == 'a'

		bottom[3] == right[3] == 'o'

	
	

	"area" (top), "able" (left), "also" (right), "echo" (bottom)
	
		All corner constraints are satisfied.

	
	

Thus, the answer is [["able","area","echo","also"],["area","able","also","echo"]].

Example 2:

Input: words = ["code","cafe","eden","edge"]

Output: []

Explanation:

No combination of four words satisfies all four corner constraints. Thus, the answer is empty array [].

 

Constraints:

	4 <= words.length <= 15

	words[i].length == 4

	words[i] consists of only lowercase English letters.

	All words[i] are distinct.

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-08 |
| Link | https://leetcode.com/problems/word-squares-ii/description/ |
| Rating | 1606 |
| AC | Y |
| Time | 40min |
| Pattern | brute force / combinatorial search |
| Revision due | 2026-05-22 |
| Remark | Self-derived with WA debugs on sorting. Approach: 4 nested loops over all word combos, check word-square condition (word[i][j] == word[j][i] across all chosen words). Key sorting insight — `String.join("", list).compareTo(...)` cleaner than `toString()`. Complexity: O(n^k) where n is word count, k is grid size. |

---

> [!note] Verbatim thinking and full solution code were **not captured** on the first attempt (it predates the per-attempt archive). Only the logged insight/remark above survives. Full verbatim + inlined code begin from the second attempt onward.
