# #11 — Find All Groups of Farmland

**Link:** https://leetcode.com/problems/find-all-groups-of-farmland/
**Date:** 2026-05-29 (Fri)
**Rating:** ~1500-1550 band (Group A #6 — Flood Fill acquisition)
**Time:** 25 min — **AC clean, first attempt**
**Pattern:** Graphs / Flood Fill (BFS connected-component, track bounding corners)

---

## Problem

Binary grid `land` where `1` = farmland. Farmland groups are rectangular and do not touch (no two groups are 4-directionally adjacent). For each group return `[r1, c1, r2, c2]` = top-left and bottom-right corners.

## Approach (verbatim)

Start from `(r,c)`; if it's a `1` and unvisited, then this is a group's starting vertex. Apply BFS to collect all farmland cells in this group, keeping a running max row and max col. Once done, append `[startRow, startCol, maxRow, maxCol]` to the answer. Repeat the scan until all groups are found.

Because the scan goes top-to-bottom, left-to-right, the first `1` hit in any group is its top-left corner, and the BFS max-row/max-col is its bottom-right corner.

## Solution

```java
class Solution {
    private Set<String> visited = new HashSet<>();
    private Deque<int[]> q = new ArrayDeque<>();
    private int[][] direction = new int[][] {{0,-1},{0,1},{-1,0},{1,0}};

    private int[] helper(int r, int c, int[][] grid){
        int m = grid.length, n = grid[0].length;
        q.offer(new int[]{r,c});
        visited.add(r+"-"+c);
        int maxRow = 0, maxCol = 0;
        while(!q.isEmpty()){
            int[] land = q.poll();
            int x = land[0], y = land[1];
            maxRow = Math.max(maxRow, x);
            maxCol = Math.max(maxCol, y);
            for (int[] nb : direction){
                int i = nb[0] + x, j = nb[1] + y;
                if (i < m && j < n && i >= 0 && j >= 0){
                    if (!visited.contains(i+"-"+j) && grid[i][j] == 1){
                        q.offer(new int[]{i,j});
                        visited.add(i+"-"+j);
                    }
                }
            }
        }
        return new int[]{r,c,maxRow,maxCol};
    }

    public int[][] findFarmland(int[][] land) {
        int m = land.length, n = land[0].length;
        List<int[]> ans = new ArrayList<>();
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++)
                if (!visited.contains(i+"-"+j) && land[i][j] == 1)
                    ans.add(helper(i, j, land));
        return ans.toArray(new int[0][]);
    }
}
```

**Complexity:** O(m·n) time (each cell enqueued once), O(m·n) space (visited set + queue).

## Debrief notes

- **Correct and clean.** Visited-on-enqueue (not on-dequeue) avoids the classic double-enqueue bug — good instinct.
- **Efficiency nit — `Set<String>` "r-c" encoding.** On a 300×300 grid that's ~90k string allocations + hashing, all garbage. A `boolean[][] visited` (or marking `land[i][j] = 0` in place) is O(1) per cell with zero allocation. This is the grid-analog of pre-submit item 5 (`Set<int[]>` reference-equality) — for grids, prefer `boolean[][]` over string-encoded coordinates.
- **Manual copy loop at the end is unnecessary** — `ans.toArray(new int[0][])` does it directly (shown above; original used the explicit double loop).
- The problem *guarantees* rectangular groups, so flood fill isn't strictly required (a right+down scan from each top-left also works) — but BFS flood fill is exactly the mechanic this acquisition installs, so it's the right tool to practice here.
