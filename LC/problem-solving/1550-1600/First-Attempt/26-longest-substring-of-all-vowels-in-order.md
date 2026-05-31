### #26 — Longest Substring Of All Vowels in Order
**Link:** https://leetcode.com/problems/longest-substring-of-all-vowels-in-order/
**Date attempted:** 2026-05-30
**AC at:** 2026-05-30 10:34 IST
**Rating:** 1550–1600 band (Phase 2 — sealed queue, deal-list #3)
**Time:** 22 min — first-submission AC ✓ (self-derived, under cap)
**Pattern (debrief):** Sliding Window · Two Pointers — Q3, AR 51.9%

---

**Insight:**
A "beautiful" substring is a maximal run that is **non-decreasing in alphabet
order** AND contains all 5 distinct vowels. The trick: vowel order a<e<i<o<u is
exactly alphabetical order, so "each char ≥ previous char" is the in-order check —
no special vowel-rank mapping needed. Walk j; when `word[j] < word[j-1]` the run
breaks, so reset the left anchor `i = j` and clear the distinct-vowel set.
Otherwise extend; whenever the set holds all 5, update `max(j − i + 1)`.

**Key gotcha:**
- Run-break detection via `word[j-1] > word[j]` (strict drop ends the run). On
  break, reset both `i` and the vowel `Set`, then re-seed the current char.
- `j <= 0` guard for the first index (no `j-1` to compare).
- All-5 check uses a `Set<Character>` size == 5, gated inside the non-decreasing
  branch so it only fires on a valid run.

**Complexity:**
O(n) time (each index visited once), O(1) space (set ≤ 5 vowels).

**Notes on own code:**
- `int ch = word.charAt(j) - 'a'` computed but the comparison is done on raw chars
  — harmless redundancy.
- Reset logic duplicates the "add current vowel to set" line in both branches;
  works but could be hoisted.

**Alternative approaches (not explored):**
1. **Two-pointer with explicit run length + vowel count** — track a `count` of
   distinct vowels seen in the current run instead of a Set; reset on break.
   Same O(n), avoids the HashSet overhead.

**Solution code (as submitted):**

```java
class Solution {

    private boolean isVowel(char ch) {
        if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u') {
            return true;
        }
        return false;
    }

    public int longestBeautifulSubstring(String word) {

        int maxLength = 0;
        int vowelCount = 0;
        Set<Character> vowelSet = new HashSet<>();

        int i = 0, j = 0, n = word.length();

        while (j < n) {

            int ch = word.charAt(j) - 'a';

            if (isVowel(word.charAt(j))) {
                vowelSet.add(word.charAt(j));
            }

            if (j <= 0 || word.charAt(j - 1) - 'a' > ch) {

                vowelSet.clear();
                i = j;

                if (isVowel(word.charAt(j))) {
                    vowelSet.add(word.charAt(j));
                }
            }
            else {

                if (word.charAt(j - 1) - 'a' <= ch) {
                    if (vowelSet.size() == 5) {
                        maxLength = Math.max(maxLength, j - i + 1);
                    }
                }
            }
            j++;
        }
        return maxLength;
    }
}
```

---

**Cleaned versions (post-AC refactor, 2026-05-30).** Kept the submitted code above as
the as-derived record; these are the de-duplicated rewrites.

Duplication/redundancy removed:
- `word` is constrained to vowels only → `isVowel(...)` is always true → helper +
  all `isVowel` guards are dead weight; the `Set` just tracks distinct chars.
- `vowelSet.add(...)` was written twice (top + reset branch) → once, after the reset.
- `else { if (word[j-1] <= word[j]) ... }` → the `else` already *means* that; inner
  check always true.
- `vowelCount` declared, never used.
- `'a' < 'e' < 'i' < 'o' < 'u'` is already alphabetical, so compare chars directly —
  no `- 'a'`.

**(1) Same approach, de-duplicated (Set):**

```java
class Solution {
    public int longestBeautifulSubstring(String word) {
        int n = word.length();
        int maxLength = 0;
        int start = 0;
        Set<Character> vowels = new HashSet<>();

        for (int j = 0; j < n; j++) {
            // run breaks when the current vowel is "smaller" than the previous
            if (j > 0 && word.charAt(j) < word.charAt(j - 1)) {
                vowels.clear();
                start = j;
            }
            vowels.add(word.charAt(j));
            if (vowels.size() == 5) {
                maxLength = Math.max(maxLength, j - start + 1);
            }
        }
        return maxLength;
    }
}
```

**(2) O(1) space — distinct-vowel counter instead of a Set:**

```java
class Solution {
    public int longestBeautifulSubstring(String word) {
        int n = word.length(), maxLength = 0, runLen = 1, distinct = 1;
        for (int j = 1; j < n; j++) {
            char prev = word.charAt(j - 1), cur = word.charAt(j);
            if (cur < prev) { runLen = 1; distinct = 1; }     // run breaks
            else { runLen++; if (cur > prev) distinct++; }     // grow; new vowel?
            if (distinct == 5) maxLength = Math.max(maxLength, runLen);
        }
        return maxLength;
    }
}
```

Both O(n) time; (2) is O(1) space. Distinct counter bumps only on a strict increase
`cur > prev` (a new vowel), so `distinct == 5` ⟺ all five appeared in the run.
