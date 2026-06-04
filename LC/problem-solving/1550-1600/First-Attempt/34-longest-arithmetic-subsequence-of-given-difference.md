# 34 — Longest Arithmetic Subsequence of Given Difference

- **Link:** https://leetcode.com/problems/longest-arithmetic-subsequence-of-given-difference/
- **Band:** 1550–1600 · Phase 2 sealed queue deal #7 · Q2 · AR ~54%
- **Bucket (revealed post-solve):** **DP » LIS-variant** (the map is the DP table keyed by value, not a hashing mechanic — [[lc-classify-by-own-solution]]).
- **AC:** 2026-06-02 17:01:20 IST
- **Result:** ✅ **CLEAN first-submission AC, ~34 min — OVER-CAP → derivation clause applied** (self-derived, first sub AC, no WA, no hint → counts as a clean ownership rep; clause exempts time only). **First clean DP » LIS-variant rep** (bucket was 0).

## Approach (our code)
DP keyed by **value**, not index. For each `num`, the only possible predecessor in an arithmetic
subsequence with fixed difference `d` is `num − d`. So `dp[num] = dp[num − d] + 1`, where `dp[v]` =
length of the longest valid subsequence ending at value `v`. Track the running max. O(n) time, O(n) space.

```java
class Solution {
    public int longestSubsequence(int[] arr, int difference) {
        Map<Integer,Integer> map = new HashMap<>();
        int maxCount = 0;
        for (int num : arr) {
            int length = map.getOrDefault(num - difference, 0) + 1;
            map.put(num, length);
            maxCount = Math.max(maxCount, length);
        }
        return maxCount;
    }
}
```

## The scare → the insight
First read pattern-matched to **LIS** and braced for the O(n log n) patience-sorting / binary-search machinery.
It is **not** classic LIS. Because the common difference `d` is **fixed**, every value has *exactly one* legal
predecessor (`num − d`) — there is no "search among all smaller elements for the best chain." That single fact
collapses the problem from O(n log n) with a search structure to a **one-pass O(n) value-keyed DP**.
- **Load-bearing distinction:** classic LIS = predecessor is *any* smaller element (must search) → DP+binary search.
  This variant = predecessor is *one specific value* (lookup) → plain hash-DP.

## Key decisions (logged live, pre-code)
- DP state keyed by **value** (`num`), processed left→right in array order — so `dp[num−d]` is already the best
  chain ending at the latest occurrence of `num−d` *before* this index. Order of iteration is what makes the
  one-pass correct (no need to revisit).
- Map default 0 handles "predecessor never seen" → current element starts a length-1 chain.

## Perturbation probes
_(settled Socratically in chat before writing — [[lc-perturbation-before-write]])_

**Load-bearing assumption = the number of valid predecessors is exactly ONE.**
With a fixed exact difference, each value's only legal predecessor is `num − d` → a single map lookup → O(n).
The fixed difference isn't just a detail; it is the *only* thing removing the search. The instant the
predecessor stops being a unique value and becomes a *set you must look through*, the LIS search cost returns.
This is why it's "kinda LIS but not": same extend-the-best-chain skeleton, but the search dimension is gone.

| # candidate predecessors | Condition | Cost |
|---|---|---|
| exactly 1 (this problem) | predecessor = exact value `num − d` | **O(n)** single lookup |
| many | predecessor satisfies a range/inequality (e.g. "any smaller", "gap ≥ d") | search returns |

**Two perturbations that bring the cost back:**
1. **Difference free to vary (you choose it) → Longest Arithmetic Subsequence (LC 1027):** predecessor depends on
   a diff not known in advance → `dp[i][d]` over all pairwise diffs → **O(n²)**.
2. **Strictly increasing, any gap → classic LIS:** predecessor = any smaller element → **O(n log n)** with binary search.

Both confirm: relax "unique exact predecessor" → a candidate *set* appears → search returns → cost returns.

## Lesson
Recognising "this *looks* like LIS but the predecessor is fixed" is the whole derivation. The fear was correct
(LIS is genuinely hard) and the resolution was correct (fixed-diff ⇒ not LIS). Counts toward **DP » LIS-variant**
first clean rep. Over-cap (34m) is fine under the derivation clause — the time went into *recognising it wasn't
classic LIS*, which is exactly the derivation muscle being trained.

## Array-vs-Map variant — the offset-normalization boundary lesson
_(reusable: many value-keyed DP problems do this; only the magnitudes change, the logic is identical)_

An `int[]` DP table is faster than a `HashMap` (no hashing/boxing, no GC), but it can't take a negative index
and can't "miss" a key. So when the index is computed from an **expression** (`num − difference`), the offset
must absorb the worst case of the **whole expression**, not just `num`.

**Derive the two constants — never hardcode them:**
```java
// Constraints: |num| ≤ 10^4   and   |difference| ≤ 10^4
final int NUM_ABS  = 10000;                 // how far num alone can reach (offset for nums)
final int DIFF_ABS = 10000;                 // extra reach added by subtracting difference (offset for difference)
final int OFFSET   = NUM_ABS + DIFF_ABS;    // = 20000 — BOTH swings, so the read index never goes negative
final int SIZE     = 2 * OFFSET + 1;        // = 40001 — covers indices 0 .. 40000
```
- Offset for **nums** (`NUM_ABS`) shifts `num`'s own range `[−10⁴,10⁴]` up to non-negative.
- Offset for **difference** (`DIFF_ABS`) covers the extra downward push from `− difference` (difference up to `+10⁴`).
- They **add**: total `OFFSET = 20000`. The two are not independent knobs — accounting for difference *is* just
  making the single value-offset bigger.

```java
class Solution {
    public int longestSubsequence(int[] arr, int difference) {
        final int maxVal  = 10000;
        final int maxDiff = 10000;
        final int offset  = maxVal + maxDiff;
        final int size    = 2 * offset + 1;

        int[] dp = new int[size];

        int best = 0;
        for (int num : arr) {
            int normalizedNum     = num + offset;
            int prevNormalizedNum = normalizedNum - difference;
            dp[normalizedNum] = dp[prevNormalizedNum] + 1;
            best = Math.max(best, dp[normalizedNum]);
        }
        return best;
    }
}
```
**AC** with this array version (`maxVal`/`maxDiff` → `offset` → `size`, all derived from constraints).
Bounds check (why `OFFSET=20000`, `SIZE=40001` are exactly right):
- lowest read: `num=−10⁴, difference=+10⁴` → `(−10⁴+20000) − 10⁴ = 0` ✓
- highest read: `num=+10⁴, difference=−10⁴` → `(10⁴+20000) − (−10⁴) = 40000` ✓

**Three styles, ranked:**
| Style | Array size | Notes |
|---|---|---|
| Map (`getOrDefault(_,0)`) | — | most forgiving; missing/out-of-range key auto-returns 0. What our first AC used. |
| Array + big offset | `2·(NUM_ABS+DIFF_ABS)+1` = 40001 | simplest correct array; fixed ~160 KB alloc/call. |
| Array + bounds guard | `2·NUM_ABS+1` = 20001 | smallest; read 0 when `prev<0 \|\| prev≥SIZE` (a predecessor value outside `[−10⁴,10⁴]` can't be in `arr`). |

**The takeaway (carries to other problems):** when normalizing a signed value into an array index, size the
offset to the worst-case index *after all arithmetic on the index expression*, not to the raw value's range.
Here `+10⁴` covered only `num`; the `− difference` demanded another `+10⁴`. A `HashMap` hides this boundary;
an `int[]` exposes it — which is exactly why the array is faster *and* more bug-prone.

## REVISION TARGET (Day+14)
Re-derive directly: why a **fixed** difference gives a unique predecessor and collapses LIS → O(n) hash-DP.
Re-answer the "any-difference" perturbation (what state explodes to, and why).
