# Multi-Source Flood Fill — First Attempt

## Problem

You are given two integers n and m representing the number of rows and columns of a grid, respectively.

You are also given a 2D integer array sources, where sources[i] = [ri, ci, color​​​​​​​i] indicates that the cell (ri, ci) is initially colored with colori. All other cells are initially uncolored and represented as 0.

At each time step, every currently colored cell spreads its color to all adjacent uncolored cells in the four directions: up, down, left, and right. All spreads happen simultaneously.

If multiple colors reach the same uncolored cell at the same time step, the cell takes the color with the maximum value.

The process continues until no more cells can be colored.

Return a 2D integer array representing the final state of the grid, where each cell contains its final color.

 

Example 1:

Input: n = 3, m = 3, sources = [[0,0,1],[2,2,2]]

Output: [[1,1,2],[1,2,2],[2,2,2]]

Explanation:

The grid at each time step is as follows:

​​​​​​​

At time step 2, cells (0, 2), (1, 1), and (2, 0) are reached by both colors, so they are assigned color 2 as it has the maximum value among them.

Example 2:

Input: n = 3, m = 3, sources = [[0,1,3],[1,1,5]]

Output: [[3,3,3],[5,5,5],[5,5,5]]

Explanation:

The grid at each time step is as follows:

Example 3:

Input: n = 2, m = 2, sources = [[1,1,5]]

Output: [[5,5],[5,5]]

Explanation:

The grid at each time step is as follows:

​​​​​​​

Since there is only one source, all cells are assigned the same color.

 

Constraints:

	1 <= n, m <= 10^5

	1 <= n * m <= 10^5

	1 <= sources.length <= n * m

	sources[i] = [ri, ci, colori]

	0 <= ri <= n - 1

	0 <= ci <= m - 1

	1 <= colori <= 10^6​​​​​​​

	All (ri, ci​​​​​​​) in sources are distinct.

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-14 |
| Link | https://leetcode.com/problems/multi-source-flood-fill/description/ |
| Rating | 1671 |
| AC | Y |
| Time | 25min (fully self-derived) |
| Pattern | Multi-source BFS — sort sources by color descending |
| Revision due | 2026-05-28 |

---

#### Thought process (what was actually going through the mind)

**Step 1 — Constraint reading**
- n * m <= 10^5 → O(n * m) accepted
- Multiple sources, color spreads to uncolored neighbors each time step
- Contention: if two colors reach the same cell at the same time step, higher color wins

**Step 2 — Approach derivation**
Spreading to adjacent cells at each time step → BFS. All sources start simultaneously → multi-source BFS (seed queue with all sources at once).

Contention resolution: higher color must take priority. First instinct — sort at each BFS level. Then sharper insight: sort sources by color descending at the start. Higher-color sources process first at level 0, color their neighbors first, and add them to the queue first. Level 1 queue therefore also has higher-color cells ahead. By induction, at every level, higher-color cells are processed before lower-color cells. Lower-color cells find contested cells already colored → skip automatically.

One sort at the start. Standard BFS after that.

**Step 3 — Correctness check**
Color 0 used as "uncolored" sentinel. Constraints say `1 <= colori <= 10^6` — no source has color 0, so sentinel is safe.

No missed edge cases during derivation.

---

#### What should have been thought (gaps)

No significant gaps. The sort-at-start insight was derived cleanly during planning, not discovered via WA. Approach was coded correctly on first attempt.

---

#### Complexity

O(n * m * log(sources.length)) time — sort is O(s log s), BFS visits each cell once. O(n * m) space for the grid and queue.

---
