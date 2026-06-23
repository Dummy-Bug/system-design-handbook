# 22 — Maximum Number of Moves in a Grid

- **Link:** https://leetcode.com/problems/maximum-number-of-moves-in-a-grid/
- **Dealt:** 2026-06-22 (last sealed-queue item)
- **Result:** ✅ **CLEAN first-submission AC, self-derived, 15m SUB-CAP**
- **Bucket (credit by our code):** **DP » Grid** → **1/2 → 2/2 → OWNED ●**
- **AR / slot:** 58.8% / Q3

## Contamination note (overturned)
Queue had this flagged "implementation rep only" (bucket DP-Grid leaked in chat 2026-06-15).
**Overturned at debrief:** the leak was immaterial — recognition is **inherent to the problem statement**
("maximum number of moves in a **grid**" + explicitly-listed moves ⇒ self-evidently grid DP), so the leaked
label conveyed zero information. The actual derivation (recurrence + memo + column-0 starts) was fully
self-driven, first-sub, clean. Credited as a genuine ownership rep. Not optimistic counting: a leak that
duplicates the statement steals no derivation.

## Approach
Top-down memoized DFS. `dp[i][j]` = longest strictly-increasing path **starting** at `(i,j)`.
Three forward moves (column always `+1`): `(i-1,j+1)`, `(i,j+1)`, `(i+1,j+1)`, each taken only if the target
value is strictly greater. Answer = max over all column-0 start cells. Sentinel `-1` = uncomputed; terminal
cells legitimately store `0` (no collision with sentinel).

```java
private int helper(int[][] grid, int i, int j) {
    if (dp[i][j] != -1) return dp[i][j];
    int c1 = 0, c2 = 0, c3 = 0;
    int m = grid.length, n = grid[0].length;
    if (isValid(i-1, j+1, m, n) && grid[i-1][j+1] > grid[i][j]) c1 = 1 + helper(grid, i-1, j+1);
    if (isValid(i,   j+1, m, n) && grid[i][j+1]   > grid[i][j]) c2 = 1 + helper(grid, i,   j+1);
    if (isValid(i+1, j+1, m, n) && grid[i+1][j+1] > grid[i][j]) c3 = 1 + helper(grid, i+1, j+1);
    return dp[i][j] = Math.max(c1, Math.max(c2, c3));
}
```

## Step 2 / Step 3 (retroactive — solve was clean)
- **Worked example:** any cell with no strictly-greater forward neighbor → returns 0 (base). Chains add 1 per hop.
- **Edges:** single column (n=1) → every start returns 0; all-equal grid → 0 (strict `>` blocks every move);
  single row → only the `(i,j+1)` branch ever fires; bounds via `isValid`.

## Perturbation (debrief, [[lc-perturbation-debrief]])
Every move forces `j+1` ⇒ the search graph is a **DAG layered by column** (strictly left→right, acyclic).
Consequence: recursion/memo was **not required** — iterate columns right→left,
`dp[i][j] = 1 + max(valid greater neighbors in column j+1)`, bottom-up, no stack. The memoized DFS discovers
this column order implicitly. (BUP rewrite deferred per 1800+ policy — top-down memo is the contest-speed default.)

## Credit
DP » Grid **OWNED 2/2**. Clean-rate this band: 15/20 (#22 counts; contamination overturned).
Owed buckets remaining (all need fresh non-queue picks): Two-Pointers (2), Stack (2), DP-Linear (2),
DP-String (2), Mono-Stack (1).
