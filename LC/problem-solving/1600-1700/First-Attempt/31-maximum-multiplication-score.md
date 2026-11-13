# 31 — Maximum Multiplication Score

- **Link:** https://leetcode.com/problems/maximum-multiplication-score/ (LC 3290)
- **Dealt:** 2026-11-12 evening, solved 2026-11-13 morning, second problem after the restart
- **Rating / slot:** 1692 · Weekly Contest 415 Q2 · AR 41.4%
- **Result:** ❌ **Editorial, AC after 1 WA.** LC hint 1 (use DP) at 43 min, then the recurrence walked through with Claude after the cap. About 115 min wall clock including a 24-min walk, so about 91 min active.
- **Bucket (revealed post-solve):** **DP-Linear**, a take/skip over `b` with a pointer into `a`.
- **Cold re-solve:** ⏳ owed today, blank file.

## Timeline

| Time | Min | What happened |
|---|---|---|
| 06:13 | 0 | Started reading |
| ~06:16 | ~3 | Ruled out greedy (largest times largest fails). Thought of DP but rejected it as O(n²), which n ≤ 10⁵ will not allow |
| 06:43 | 30 | Cap. Brute force (fix one index, three inner loops) is O(n⁴). Idea: fix the index for a[0], then take the best value for each later index from a shifting window [x, y], needing range max in O(1) or O(log n) |
| 06:54 | 41 | Decided the approach was right and only a range-maximum structure was missing. Asked whether a simpler way exists → yes |
| 06:56 | 43 | **LC hint 1:** use Dynamic Programming |
| 07:08 | 55 | Could not form the recurrence. Stopped |
| 07:12 | 59 | Given only the state `dfs(i, j)` to think about on a walk |
| 07:12–07:36 | — | Walk |
| 07:36 | 83 | Walked through it on `a = [3, 2]`, `b = [1, 5, 4]`: filled in both transitions unaided, `skip = dfs(i, j+1)` and `take = a[i]*b[j] + dfs(i+1, j+1)`, then both base cases (`i == a.length → 0`, `j == b.length → MIN`) |
| ~07:40 | ~87 | Sentinel trap shown: `Integer.MIN_VALUE + (-6)` wraps to `2147483642`. Proposed long and converting back to int; corrected: `Long.MIN_VALUE` wraps the same way, and the answer can reach 4 × 10¹⁰, which does not fit an int |
| 07:45 | 92 | Started coding from memory |
| 08:05 | 112 | **WA** on 674 / 675 |
| 08:08 | 115 | Fixed the sentinel, **AC** |

## The recurrence

Walk along `b` left to right while `a[i]` waits for an index. At each `b[j]` there are two moves.

```
dfs(i, j) = best score still available, when a[i..] still need indices and only b[j..] may be used

dfs(i, j) = max( dfs(i, j+1),                   skip b[j]
                 a[i]*b[j] + dfs(i+1, j+1) )    take b[j] for a[i]

i == a.length  → 0          every a placed, nothing left to earn
j == b.length  → sentinel   b ran out with a[i] still waiting: illegal, must lose every max

answer = dfs(0, 0)
```

## Why it is O(n), not O(n²)

Without the memo the take/skip tree is exponential. With it, each distinct `(i, j)` is computed once, and the number of distinct pairs is the product of the ranges: `i` has `a.length = 4` values and `j` has `n` values, so 4 × 10⁵ states with O(1) work each. **O(4n) = O(n)** time, O(4n) space.

The minute-3 rejection was the real miss: DP was assumed to mean n², but the pairs are between the two arrays, not within `b`, and one side is fixed at size 4.

## WA-cause

- **WA-cause [impl-bug]:** the base case returned `Integer.MIN_VALUE` while the guard checked `take != Long.MIN_VALUE`, so the sentinel was never recognised. It survived as a real score of about −2.1 × 10⁹, beat the true answer −4 × 10¹⁰ in `Math.max`, and printed `-2147483648`. Overflow-and-sentinel family, checklist item 14.

## Debrief

- **The 06:54 idea had a gap that was not raised in session:** taking the best value for each later index from its own window does not keep `i1 < i2 < i3`, because the three choices are coupled. The fix for that coupling is exactly the DP: carry the best score of the previous `a` forward as a prefix maximum, one layer per element of `a`.
- **Overflow, both places:** `a[i] * b[j]` is int times int and overflows before it reaches a long, so write `(long) a[i] * b[j]` or `1L * a[i] * b[j]`. The sentinel either gets checked before adding, as here, or is `Long.MIN_VALUE / 2` so additions cannot wrap.
- **Code quality:** the `else { take = Long.MIN_VALUE; }` branch reassigns the value `take` already holds and can go.

**Reflex:** before rejecting DP, write the state and multiply the ranges of its parameters. A dimension bounded by a small constant (here `a.length == 4`) makes the DP linear.

## Final code (AC)

```java
class Solution {

    private Long [][]dp;

    public long maxScore(int[] a, int[] b) {
        this.dp = new Long[a.length][b.length];
        return dfs(0, 0, a, b);
    }

    private long dfs(int i, int j, int[] a, int[] b) {

        if (i == a.length)
            return 0;
        if (j == b.length)
            return Long.MIN_VALUE;

        if (this.dp[i][j] != null) return this.dp[i][j];

        long skip = dfs(i, j + 1, a, b);
        long take = dfs(i + 1, j + 1, a, b);
        if (take != Long.MIN_VALUE) {
            take += (long) a[i] * b[j];
        } else {
            take = Long.MIN_VALUE;
        }
        return this.dp[i][j] = Math.max(take, skip);
    }
}
```
