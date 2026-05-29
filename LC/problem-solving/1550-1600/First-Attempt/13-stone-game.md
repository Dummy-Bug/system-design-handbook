### #13 — Stone Game
**Link:** https://leetcode.com/problems/stone-game/
**Date attempted:** 2026-05-26
**Rating:** 1550–1600 band (Phase 1 acquisition — interval DP blind spot)
**Time:** 70 min total (8 min read + greedy invalidation, state definition struggle + break, code + AC)
**Pattern:** Interval DP

---

**Verbatim thinking:**

- tried greedy but failing for [2,3,5,100,10] — both play optimally so greedy is out
- thinking of recursion with pick and non-pick
- state: f(N) = max sum for alice for array of size n. f(N) = f(n-1) + pickedNumber. number removed from either first or last, size reduced either way
- realized n is redundant — i, j are the only two changing metrics. also need turns. so (turn, start, end) = 3D
- but wait — if start+end is odd then it's alice's turn → turn is derivable from i,j, not a third variable
- but the return value is confusing: on alice's turn maximize alice sum, on bob's turn maximize bob sum, what does f return?
- "f(i,j) = max sum scored by either alice or bob" — too ambiguous
- tried "alice's turn returns bob's score, bob's turn returns alice's score" — broke the recurrence
- **took a break**
- came back fresh: f(i,j) = max sum the CURRENT player can score from piles[i..j]
- when opponent plays f(i+1,j), current player's remaining from that range = sum(i+1,j) - f(i+1,j)
- so f(i,j) = max(piles[i] + sum(i+1,j) - f(i+1,j), piles[j] + sum(i,j-1) - f(i,j-1))
- base case: f(i,i) = piles[i]
- alice wins if f(0,n-1) > totalSum/2

**Insight:**
Interval DP where f(i,j) = max sum the current player can score from piles[i..j]. The trick is that when f returns the opponent's best score from a subrange, YOUR remaining score is totalRangeSum - opponentBest. This lets a single function handle both players without tracking turns.

**Key gotcha:**
Defining what f(i,j) returns is the entire problem. "Max sum for Alice" or "max sum for Bob" breaks because turns alternate. "Max sum for the CURRENT player" is the clean definition — it's turn-agnostic because both players use the same optimal strategy.

**Complexity:**
O(n²) time, O(n²) space (memo table + prefix sum).

**Solution code:**

```java
class Solution {
    
    int[] pre;
    int[][] dp;

    private int getSum(int i, int j) {
        if (i == 0) return pre[j];
        return pre[j] - pre[i - 1];
    }

    public boolean stoneGame(int[] piles) {
        int n = piles.length;
        pre = new int[n];
        pre[0] = piles[0];

        for (int i = 1; i < n; i++) {
            pre[i] = pre[i - 1] + piles[i];
        }

        dp = new int[n][n];
        for (int i = 0; i < n; i++) {
            Arrays.fill(dp[i], -1);
        }

        int aliceScore = helper(piles, 0, n - 1);

        if (pre[n - 1] - aliceScore > aliceScore) {
            return false;
        }
        return true;
    }

    private int helper(int[] piles, int i, int j) {
        if (i == j) return piles[i];

        if (dp[i][j] != -1) return dp[i][j];

        int s1 = helper(piles, i + 1, j);
        int s2 = helper(piles, i, j - 1);

        int tS1 = getSum(i + 1, j);
        int ts2 = getSum(i, j - 1);

        int firstPick = piles[i] + tS1 - s1;
        int lastPick = piles[j] + ts2 - s2;

        return dp[i][j] = Math.max(firstPick, lastPick);
    }
}
```
