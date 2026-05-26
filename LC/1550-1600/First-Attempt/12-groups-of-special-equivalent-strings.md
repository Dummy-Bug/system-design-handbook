### #12 — Groups of Special-Equivalent Strings
**Link:** https://leetcode.com/problems/groups-of-special-equivalent-strings/
**Date attempted:** 2026-05-26
**Rating:** 1550–1600 band (Phase 1 acquisition)
**Time:** 50min — AC (hinted — Claude pointed out 2 bugs)
**Pattern:** Hashing / counting

---

**Verbatim thinking:**

- take a string and divide it into two smaller strings s1 and s2 — s1 from even index chars, s2 from odd index chars
- sort s1 and s2 individually, then merge them alternating even/odd to get the smallest possible string achievable by swapping
- use a map to check if this normalized form already exists → count groups
- realized concat (sorted-even + sorted-odd) works just as well as interleaving, but kept the merge anyway

**Insight:**
Two strings are special-equivalent iff they have the same sorted even-index characters AND the same sorted odd-index characters. Split → sort each half → use as canonical key → count distinct keys.

**Bugs hit:**
1. **[read-error]** Returned max group size (`maxCount`) instead of number of groups (`freq.size()` / `count`). Misread what the problem asks.
2. **[impl-bug]** Merge loop bound `while (length <= Math.max(m,n))` — should be `while (length < m + n)`. For even-length words, max(m,n) = m = n, so loop runs max+1 times instead of m+n. Off-by-one.

Both bugs found by Claude after 20 min of failed self-debugging → **hinted**.

**Key gotcha:**
The merge function is unnecessary complexity. Just concatenate `new String(sortedEven) + new String(sortedOdd)` — produces the same canonical key with zero bug surface.

**Complexity:**
O(n × k log k) time (n words, k = word length), O(n × k) space.

**Solution code:**

```java
class Solution {

    private String merge(char[] even, char[] odd) {
        StringBuilder sb = new StringBuilder();
        int m = even.length;
        int n = odd.length;
        int i = 0, j = 0, length = 0;

        while (length < m + n) {
            if ((length & 1) == 1) {
                sb.append(odd[j]);
                j++;
            } else {
                sb.append(even[i]);
                i++;
            }
            length++;
        }
        return sb.toString();
    }

    public int numSpecialEquivGroups(String[] words) {
        int n = words.length;
        Set<String> set = new HashSet<>();
        int count = 0;

        for (String word : words) {
            StringBuilder even = new StringBuilder();
            StringBuilder odd = new StringBuilder();

            for (int i = 0; i < word.length(); i++) {
                if ((i & 1) == 1) {
                    odd.append(word.charAt(i));
                } else {
                    even.append(word.charAt(i));
                }
            }

            char[] oddChars = odd.toString().toCharArray();
            Arrays.sort(oddChars);
            char[] evenChars = even.toString().toCharArray();
            Arrays.sort(evenChars);

            String normalizedWord = merge(evenChars, oddChars);
            if (set.add(normalizedWord)) {
                count++;
            }
        }
        return count;
    }
}
```
