### #11 — The k-th Lexicographical String of All Happy Strings of Length n
**Link:** https://leetcode.com/problems/the-k-th-lexicographical-string-of-all-happy-strings-of-length-n/
**Date attempted:** 2026-05-26
**Rating:** 1550–1600 band (Phase 1 acquisition)
**Time:** ~1h20m — AC (WA-then-AC → soft fail)
**Pattern:** Math / number theory (set-based kth element selection)

---

**Verbatim thinking:**

- constraints are n <= 10 so we can have some brute forcing or backtracking shit
- took some time but finally understood the problem — we only care about the string of length = n and inside that we only want kth string
- enumerated n=1, n=2, n=3 and found formula: s*(s-1)*(s-2).. number of happy strings possible. for n=1: numString = 3, n=2: 6, n=3: 12. can use this to return empty if k > possible strings
- how to generate the kth string if exists? simple way: backtracking, generate all and return kth sorted. but before that — think if some trick/formula/derivation exists
- using n=3 k=9 to visualize: each starting char (a/b/c) has 4 strings = total/3. k/setSize → 9/4 = 3rd set → starts with 'c'. inside set C, first two have 'a' as 2nd char, last two have 'b'. k=9 is 8+1 = first string of set C → 2nd char = 'a' → only option left for last = 'b'
- pattern is present but can't make concrete formula yet. increase to n=4: total = 3×2^(n-1) = 24, sets for 1st char = 3, set size = 8. for k=21: 21/8 → 3rd set, starting range 17, ending 24. 21-17 = 4th from starting. problem reduces to finding 4th happy string when 1st char is 'c'
- after fixing first char, same char can't be next, so from 12 possibilities now 8 remain. first 4 start with 'a', first 2 of those have 'b' as 3rd char, next 2 have 'c', etc.
- break into two parts: (1) get the first char — 3 choices, (2) recursively handle remaining — only 2 choices each level since previous != current
- first step is separate, not part of recursion. f(n,k): find total possible, set size = total/2, find which set k falls in → that gives the char. append char, n=n-1, k = k - starting_range, recurse. base case: n=1 → return
- inside recursion total = 2^n (not 2^(n-1)) because excluding prev char already happened before entering

**Trace (n=4, k=21):**

```
Step 1 (3 choices):
  total = 3 × 2^(n-1) = 24
  setSize = 24/3 = 8
  k=21 → set 3 → 'c'
  newK = 21 - 16 = 5, n=3

Recursion (2 choices each level):
  n=3, k=5, prev='c' → total=2^3=8, setSize=4 → set 2 → 'b', newK=1, n=2
  n=2, k=1, prev='b' → total=2^2=4, setSize=2 → set 1 → 'a', newK=1, n=1
  n=1, k=1, prev='a' → total=2^1=2, setSize=1 → set 1 → 'b'

Result: "cbab"
```

---

**WA-cause [impl-bug]:** `addToAns` hardcoded char selection with if/else chains that missed the `prev='a', targetSet=2` case — appended 'b' instead of 'c'. Fix: build sorted available-chars list excluding prev, index with `targetSet-1`.

**Insight:**
Total happy strings = 3 × 2^(n-1). First char splits into 3 equal sets; each subsequent position splits into 2 sets (exclude prev char). Recursively narrow: find which set k falls in → pick that char → reduce k to local index → recurse with n-1.

**Key gotcha:**
When selecting the char for a position, don't hardcode if/else per char — build the available chars list dynamically (exclude prev, sort) and index into it. Hardcoding misses cases.

**Complexity:**
O(n) time, O(n) space (recursion stack + StringBuilder).

**Solution code:**

```java
class Solution {

    private void addToAns(StringBuilder sb, int targetSet) {
        char[] all = {'a', 'b', 'c'};
        int n = sb.length();

        if (n == 0) {
            sb.append(all[targetSet - 1]);
            return;
        }

        char prev = sb.charAt(n - 1);
        List<Character> available = new ArrayList<>();
        for (char c : all) {
            if (c != prev) available.add(c);
        }
        sb.append(available.get(targetSet - 1));
    }

    private void helper(StringBuilder sb, int n, int k) {
        int totalStrings = (int) Math.pow(2, n);

        if (totalStrings == 1) {
            return;
        }
        int setSize = totalStrings / 2;
        int targetSet = (int) Math.ceil((double) k / setSize);
        addToAns(sb, targetSet);

        int startingRange = setSize * (targetSet - 1) + 1;
        int newK = k - startingRange + 1;
        helper(sb, n - 1, newK);
    }

    public String getHappyString(int n, int k) {
        int totalStrings = (int) Math.pow(2, n - 1) * 3;
        if (k > totalStrings) {
            return "";
        }

        int setSize = totalStrings / 3;
        int targetSet = (int) Math.ceil((double) k / setSize);

        StringBuilder sb = new StringBuilder();
        addToAns(sb, targetSet);

        int startingRange = setSize * (targetSet - 1) + 1;
        int newK = k - startingRange + 1;

        helper(sb, n - 1, newK);
        return sb.toString();
    }
}
```
