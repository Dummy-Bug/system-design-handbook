# Sum of Digit Differences of All Pairs (cold re-solve, original #6 was 55 min) — Second Attempt (Cold Re-solve)

| Field | Value |
|-------|-------|
| Date | 2026-05-26 |
| Link | https://leetcode.com/problems/sum-of-digit-differences-of-all-pairs/ |
| Rating | ~1600 |
| AC | **Y — first submission, clean** |
| Time | **27 min end-to-end** (13 min approach + trace, rest coding) — First-Attempt was 55 min, **~2× faster** |
| Pattern | Per-digit-position contribution counting via freq map |
| Verdict | **Clean pass** (first-submission AC, self-derived, no hint) |

---

### Approach (insight)

`O(n²)` brute force is out (constraints). Key reframe: total = sum over **each digit position** of the number of pairs that *differ* at that position. Process one position at a time. Scanning left to right with a digit-frequency map, when you reach element `i`, `count` = earlier elements sharing this digit, so `(i+1) - (count+1) = i - count` = earlier elements that **differ** here. Accumulate across all `i` and all positions. `O(d·n)` time, `O(1)` space (≤10 digit buckets). Problem guarantees all numbers have equal digit length, so `digitCount` from `nums[0]` is safe.

### Step 2 / Step 3 (ritual)

Trace of `[13,23,12]→4` done on paper (not transcribed — logged as paper-only per the chat exchange). Edge cases named: all-identical (`[10,10,10,10]→0`), single number → 0 by definition.

### Review notes (no bug, but habit flags)

- **Float-cast trap [checklist #2], latent not live:** `(int)Math.pow(10, i)` for digit extraction. AC'd only because powers of 10 ≤10¹⁵ are exactly representable as doubles. Same shape as the `999`-instead-of-`1000` trap. Habit fix: integer-only digit peel (`n%10; n/=10`) or precomputed `int[] pow10`.
- **Intermediate-collection guideline:** `Map<Integer,Long>` over a fixed 0-9 digit range — an `int[10]`/`long[10]` is the natural fit (no boxing, `clear()` → `Arrays.fill`). Negligible at scale, noted for habit only.
- Clean otherwise: `getDigit` predicate extracted, no nested conditionals in main loop, orchestrator reads cleanly.

### Solution (submitted, AC)

```java
class Solution {

    private int getDigit(int n, int i) {
        n = n / (int) Math.pow(10, i);
        return n % 10;
    }

    public long sumDigitDifferences(int[] nums) {

        Map<Integer, Long> freq = new HashMap<>();
        int n = nums.length;

        int digitCount = Integer.toString(nums[0]).length();
        long ans = 0;

        while (digitCount != 0) {

            digitCount--;

            for (int i = 0; i < n; i++) {

                int digit = getDigit(nums[i], digitCount);

                long count = freq.getOrDefault(digit, 0L);
                long difference = (i + 1) - (count + 1);
                ans = ans + difference;
                freq.put(digit, count + 1);
            }
            freq.clear();
        }
        return ans;
    }
}
```

### Verdict

First clean self-derived first-submission AC of the band besides #3, and a genuine 2× speed drop (55→27) — this pattern **installed** on the first re-solve (contrast with the Outlier, whose subtle edge needed a card). No deck card: nothing cost real time.

**Band tally:** 7/10 done. Clean first-submission AC: **#3, #7**. #1/#2/#4 soft fail, #5/#6 hinted. **2/7 clean, 2/7 hinted** — still below the ≥7 clean / ≤1 hinted bar, but two cleans now and the dominant failure mode (comprehension) didn't bite here. 3 left: re-solve **Word Squares II** (orig 40 min) + 2 new on untouched patterns (monotonic stack / binary-search-on-answer / interval DP).
