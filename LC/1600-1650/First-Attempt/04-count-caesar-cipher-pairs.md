# Count Caesar Cipher Pairs — First Attempt

## Problem

You are given an array words of n strings. Each string has length m and contains only lowercase English letters.

Two strings s and t are similar if we can apply the following operation any number of times (possibly zero times) so that s and t become equal.

	Choose either s or t.

	Replace every letter in the chosen string with the next letter in the alphabet cyclically. The next letter after 'z' is 'a'.

Count the number of pairs of indices (i, j) such that:

	i < j

	words[i] and words[j] are similar.

Return an integer denoting the number of such pairs.

 

Example 1:

Input: words = ["fusion","layout"]

Output: 1

Explanation:

words[0] = "fusion" and words[1] = "layout" are similar because we can apply the operation to "fusion" 6 times. The string "fusion" changes as follows.

	"fusion"

	"gvtjpo"

	"hwukqp"

	"ixvlrq"

	"jywmsr"

	"kzxnts"

	"layout"

Example 2:

Input: words = ["ab","aa","za","aa"]

Output: 2

Explanation:

words[0] = "ab" and words[2] = "za" are similar. words[1] = "aa" and words[3] = "aa" are similar.

 

Constraints:

	1 <= n == words.length <= 10^5

	1 <= m == words[i].length <= 10^5

	1 <= n * m <= 10^5

	words[i] consists only of lowercase English letters.

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-11 |
| Link | https://leetcode.com/problems/count-caesar-cipher-pairs/ |
| Rating | 1624 |
| AC | Y |
| Time | 55min |
| Pattern | Caesar cipher / MOD normalization |
| Revision due | 2026-05-25 |
| Remark | Insight — normalize each word relative to first char using `(offset - ref + MOD) % MOD` to detect identical shift patterns. HashMap counts matching normalized forms, pairs increment by prior count. Key gotcha — MOD formula handles wraparound for backward shifts. Complexity: O(n·m) time (n words, m avg length), O(n·m) space (normalized strings in HashMap). |

---

> [!note] Verbatim thinking and full solution code were **not captured** on the first attempt (it predates the per-attempt archive). Only the logged insight/remark above survives. Full verbatim + inlined code begin from the second attempt onward.
