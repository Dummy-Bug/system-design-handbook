### #29 — Find Original Array From Doubled Array
**Link:** https://leetcode.com/problems/find-original-array-from-doubled-array/
**Date attempted:** 2026-06-01
**Rating:** 1550–1600 band (Phase 2 — sealed queue, deal-list #2)
**AC at:** 2026-06-01 _(self-derived, no hint)_
**Time:** 49 min — **first submission AC** (over 30-min cap)
**Status:** ✅ **CLEAN first-submission AC.** Over cap → **derivation-over-speed clause applied** (self-derived, first sub AC, no WA, no hint → counts as a clean ownership rep; clause exempts time only).
**Pattern (debrief):** Greedy (pair-with-double, smallest-first) · Hashing (multiset counting) · Sorting — Q2, AR 40.8%.

---

**Approach (own derivation):**
- If `n` is odd → impossible, return `{}`.
- Sort `nums`. Handle zeros separately: zeros pair with zeros, so `countZero` must be even, and `countZero/2` zeros go into the answer.
- Build a multiset of value → indices (Map of Deque).
- Walk ascending from the smallest non-zero. For each unused `x`, its partner must be `2x` — because `x` is the smallest remaining, nothing can be `x`'s half, so `x` must be the *original* and `2x` the doubled copy.
- If `2x` not available → return `{}`. Else consume one `2x`, push `x` to the answer.

**Greedy correctness (the insight):** processing in ascending order guarantees the
current smallest element can never be someone else's double, so it is forced to be an
original whose double is `2x`. Match-and-consume; any leftover/missing double ⇒ no valid
original array.

**Solution code (attempt 1, AC):**

```java
class Solution {
    public int[] findOriginalArray(int[] nums) {

        int n = nums.length;

        if ((n&1) == 1){
            return new int[]{};
        }

        int countZero = 0;
        Map<Integer,Deque<Integer>> map = new HashMap<>();

        Arrays.sort(nums);

        for (int i = 0; i < n; i++){

            int num = nums[i];

            if (num == 0){
                countZero++;
                continue;
            }
            Deque<Integer> stack;

            if (!map.containsKey(num)){
                stack = new ArrayDeque<>();
            }
            else{
                stack = map.get(num);
            }
            stack.push(i);
            map.put(num,stack);
        }

        if ((countZero%2) != 0){
            return new int[]{};
        }

        int[] ans = new int[n/2];
        int j = 0;
        for (int i = 0; i < countZero/2; i++){
            ans[j] = 0;
            j++;
        }

        Set<Integer> set = new HashSet<>();

        for (int i = countZero; i < n; i++){

            int num = nums[i];

            if (set.contains(i)){
                continue;
            }

            if (!map.containsKey(2*nums[i])){
                return new int[]{};
            }

            Deque<Integer> stack = map.get(2*nums[i]);
            int index = stack.pop();

            if (stack.isEmpty()){
                map.remove(2*num);
            }
            else {
                map.put(2*num,stack);
            }

            set.add(index);
            ans[j] = num;
            j++;
        }
        return ans;
    }
}
```

**Edge cases handled:** odd `n`; odd zero-count; `2x` missing; `x` already consumed as
someone's double (the `set.contains(i)` guard).

---

**Shorter / canonical version (count map of values, no index bookkeeping):**

The index `Deque` + `Set<Integer>` of consumed indices is heavier than needed. Key by
**value count**, not index — sort, then for each `x` (skipping already-used counts):
decrement `count[x]`, require and decrement `count[2x]`. Zeros: must be even, emit half.

```java
class Solution {
    public int[] findOriginalArray(int[] nums) {
        int n = nums.length;
        if ((n & 1) == 1) return new int[]{};

        Arrays.sort(nums);
        Map<Integer,Integer> cnt = new HashMap<>();
        for (int x : nums) cnt.merge(x, 1, Integer::sum);

        int[] ans = new int[n / 2];
        int j = 0;
        for (int x : nums) {
            if (cnt.get(x) == 0) continue;          // already used as a double
            if (x == 0) {                            // zero pairs with zero
                if (cnt.get(0) < 2) return new int[]{};
                cnt.merge(0, -2, Integer::sum);
                ans[j++] = 0;
                continue;
            }
            cnt.merge(x, -1, Integer::sum);          // use x as an original
            Integer dbl = cnt.get(2 * x);
            if (dbl == null || dbl == 0) return new int[]{};
            cnt.merge(2 * x, -1, Integer::sum);
            ans[j++] = x;
        }
        return ans;
    }
}
```

What collapsed:
- `Map<Integer,Deque<Integer>>` + `Set<Integer>` of indices → a single `Map<Integer,Integer>`
  count. No per-index tracking; "used" = count hit 0.
- Zero handling folded into the main ascending loop (still O(n log n) from the sort).
- Same greedy, same correctness — just less bookkeeping surface to bug.

> **⏳ REVISION TARGET:** re-derive the ascending-greedy argument ("smallest remaining
> must be an original") cold, and reproduce the count-map form, not the index-Deque one.
