# Minimum Cost Path With Alternating Directions II (cold re-solve) — Second Attempt (Cold Re-solve)

| Field | Value |
|-------|-------|
| Date | 2026-05-25 |
| Link | https://leetcode.com/problems/minimum-cost-path-with-alternating-directions-ii/description/ |
| Rating | TBD |
| Start | 14:33 |

### Thinking log (verbatim)

**Step 1 — Constraints:** constraints allow an O(m·n) solution.

**Step 2 — Reading / approach scoping:** cost doesn't depend on the actual cell value, only on indices → a closed-form math solution might exist instead of normal DP. But constraints are fine, so grid DP works. Read the full problem before concluding: must **wait on even-numbered seconds and move on odd-numbered seconds**; entering any cell costs you (pay on entry). The **wait cost is given as an array** — that rules out a pure-math solution; DP it is.

**Step 2 (cont.) — tracing sample cases to nail the mechanics:** start at entrance (0,0) at second = 1 (odd). So at second 1 we entered cell (0,0) → pay the entry price, and then no wait needed? First sample is too small to disambiguate — moving on to the second example case to read the mechanics off it.

**Step 2 (cont.) — mechanics understood from the trace:** start at (0,0) at second=1 (odd) → no wait, move down or right. At second=2 we reach (0,1) or (1,0) → pay the wait cost in that cell, and since it's even we can't move, so we wait 1 second. Next second=3 (odd) → move again, then even, then odd, and so on. Net: **we pay a waiting cost at every cell except (0,0)** (we start there on an odd second).

**Step 3 — Approach (BUP chosen deliberately):** solving bottom-up because it's the harder way to implement and teaches 10x more than top-down.
- State: `f(i,j)` = minimum cost to reach cell (i,j).
- Recurrence (as written by user): `f(i,j) = f(i-1,j) + f(i,j-1) + waitCost[i][j] + getEntryCost()`.
- Base: `dp[0][0] = 1` stored directly; rest computed with their wait + entry costs.

**Step 3 (cont.) — edge case found:** at the last cell `i==m-1 && j==n-1`, do we still pay a wait? Checked the examples — none added a wait there. So **no waiting cost for (0,0) nor (m-1,n-1)**.

**Step 3 (cont.) — verification:** approach traced and working for example 1 and example 2.

**Step 3 (cont.) — edge cases:**
- min grid `m*n >= 2` → start and end cell are never the same (nice). Checked anyway: if they were equal, answer is always 1 regardless of wait cost.
- max value 10^5, `m*n <= 10^5`; worst case every wait cost = 10^5 → sum can overflow int → use **long** for the accumulation. Return type is also long.

**Step 3 (cont.) — revising after "incorrect" verdict:**
- BUP direction: moving only right/down means starting from (m-1,n-1) to reach (0,0), checking right/down on the way — but that's the same as checking left/up, so BUP direction is not the problem.
- The real issue: the entry pattern — "cannot use both" — but the recurrence had **both** wait and entry cost. Reworked: **only the starting cell pays entry cost.** After that you're constrained to wait on even seconds, so you always add the **wait cost** and move only on odd seconds — entry cost is *not* added again because the wait cost was already incurred.
- Boundary at (m-1,n-1): same pattern, lands on an even second → only the wait cost is incurred.
- Dry-ran on example cases + own cases → working perfectly.

**Time note — approach phase:** ~40 min elapsed at end of thinking, minus ~5 min spent typing thoughts into chat → **~35 min to derive the approach** (before coding).

**Step 5 — Coding revealed approach was wrong:** code fails the example test case. Investigating what's wrong (the dry-run "working perfectly" claim didn't hold once actually coded).

**Step 6 — Re-reading example 3 (`m=2,n=3, waitCost=[[6,1,4],[3,2,5]]` → 16):** the breakdown shows entry cost `(row+1)*(col+1)` is paid on entering each new cell, and wait cost is paid at each cell except the start and the final move. Corrected mental model: if at cell (i,j), you pay the **entry cost of the neighbor** you move into; you can only move on odd seconds (paying entry cost on the move); on reaching (i+1,j) or (i,j+1) the second flips to even → wait 1 sec, incurring that cell's **wait cost**; then it's odd again → move, and you again pay the **entry cost** of the next neighbor. So **both** entry cost (index-dependent, `(i+1)*(j+1)`) and wait cost are involved — the earlier "only start pays entry" model was wrong.

**Step 6 (cont.) — recurrence:** state unchanged. Whether you arrive from left or top doesn't matter since entry cost is `(i+1)*(j+1)` (direction-independent). So:
`f(i,j) = min(f(i-1,j), f(i,j-1)) + entryCost[i][j] + waitCost[i][j]` — recurrence comes out the same shape as before, just with the corrected per-cell entry cost.

**Step 7 — Final submitted code:**

```java
public long minCost(int m, int n, int[][] waitCost) {
    long[][] dp = new long[m][n];
    dp[0][0] = 1;
    for (int i = 1; i < m; i++)
        dp[i][0] = i + 1L + dp[i-1][0] + waitCost[i][0];
    for (int j = 1; j < n; j++)
        dp[0][j] = j + 1L + dp[0][j-1] + waitCost[0][j];
    for (int i = 1; i < m; i++)
        for (int j = 1; j < n; j++) {
            long cost = waitCost[i][j];
            long entryCost = ((long)i + 1) * (j + 1);
            dp[i][j] = Math.min(dp[i-1][j], dp[i][j-1]) + cost + entryCost;
        }
    return dp[m-1][n-1] - waitCost[m-1][n-1];   // destination pays no wait
}
```

Traced on example 3 → returns 16. ✓ (first/dp-col use `i+1L`/`j+1L` to dodge int overflow; final `- waitCost[m-1][n-1]` removes the wait wrongly added to the destination.)

### Outcome (Min Cost Path Alt Directions II)

| Field | Value |
|-------|-------|
| Start | 14:33 |
| Time | **80 min** |
| AC | Y (no judge WA — all misfires were caught pre-submit on the example) |
| Verdict | **Hinted** — see below |

**Why hinted, not clean:** the user asked "is my approach correct?" three times and Claude gave correctness verdicts (one **"Incorrect"** that redirected them off a wrong recurrence + double-cost model). That "Incorrect" was an external nudge before the right approach was reached → under the tightened rule this counts as **hinted**, not a clean self-derived AC. Logged honestly to avoid optimistic counting (header-integrity rule).

**The real bottleneck (and it is NOT DP):** the 80 min went almost entirely into *problem comprehension*, not algorithm. The approach was reworked twice — first the wait-vs-entry cost model, then realising entry cost is `(i+1)*(j+1)` per cell — both were **misreads of the cost mechanics**, same family as #4's item-vs-arrival read-error. Once the cost model was correct, the DP itself was a textbook min-grid recurrence written cleanly and AC'd first judge-submit.

**WA-cause [read-error]:** (pre-submit, not a judge WA) cost mechanics misread twice — what is paid, where, and that entry cost is index-dependent.

**Band tally:** 5/10 done. Clean first-submission AC: **#3 only**. #1/#2/#4 soft fail (WA-then-AC), #5 hinted. **1/5 clean, 1/5 hinted** — both below bar. Dominant failure mode across the band is now unmistakable: **problem comprehension**, not algorithm/derivation. Three of five problems lost their time to reading the statement wrong.

---
