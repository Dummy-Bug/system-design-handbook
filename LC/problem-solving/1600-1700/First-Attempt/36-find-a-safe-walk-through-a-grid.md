# 36 — Find a Safe Walk Through a Grid

- **Link:** https://leetcode.com/problems/find-a-safe-walk-through-a-grid/ (LC 3286)
- **Dealt:** 2026-11-17 morning, seventh problem after the restart
- **Rating / slot:** 1608 · Biweekly Contest 139 Q2 · AR 33.3%
- **Result:** 🟡 **Hinted, first-submission AC, about 76 min.** The approach was self-derived and checked one word at a time. One partial hint at minute 16-18, when Claude explained a Partly verdict: BFS is the right family and a plain visited array is not enough. All Java syntax came from Gemini, which breaks the no-AI rule.
- **Bucket (revealed post-solve):** **Graph BFS, shortest path (0-1 BFS).** Ours: BFS over (cell, health) states.
- **Cold re-solve:** ⏳ owed, with the answer-key 0-1 BFS, from a blank editor and with no AI for syntax.

## Timeline

| Time | Min | What happened |
|---|---|---|
| 06:39 | 0 | Started reading |
| 06:51 | 12 | Read it as grid DP: dp[i][j] from the four neighbours, never stepping back into the parent, so at most three moves per cell. Check → incorrect |
| 06:55 | 16 | Saw why: the DP can loop forever since only the direct parent is blocked. Noted m, n ≤ 50 and that nothing seems maximised or minimised. Proposed DFS or BFS. Check → partly |
| ~06:57 | 18 | Asked what partly means. Claude split it: the infinite-loop reasoning is correct; nothing being minimised is incorrect; BFS is the right family but plain DFS or BFS with a visited array is not enough. **This is the hint** |
| ~06:59 | 20 | Clarified: the output is only yes or no, arriving with health 1 is enough. Check → correct |
| 07:02 | 23 | BFS from (0,0); a plain visited set can skip a cell later reached from another direction, so the visited state also carries the incoming direction and the health on arrival. Check → correct |
| 07:05 | 26 | Dry-ran example 1 in their head; asked whether DP with stored results would also work. Check → correct, as a search over the same states |
| 07:09 | 30 | Cap. Step 3 posted (below). Step 2 by hand pushed back on as too slow for a contest grid; agreed instead: hand-trace the smallest case and press Run on every given example before Submit |
| 07:09–07:54 | 30–75 | Coded it, with all Java syntax (record, HashSet of records, ArrayDeque, the directions array) taken from Gemini. Dropped the direction from the state, keeping cell and health |
| 07:54 | 75 | Code posted, checked by running → correct |
| ~07:55 | 76 | **AC** on the first submission |

## The approach (ours)

1. Start health is `health − grid[0][0]`; if it is 0 or less, return false.
2. BFS over states (row, col, health on arrival). From each state, try the four neighbours; the new health is the old minus the neighbour's cell value. Keep it only if it is above 0 and the state is unseen.
3. Return true when the bottom-right cell is dequeued with health above 0, false when the queue empties.

Why it works: two arrivals at the same cell with different health are different situations, so the visited set is keyed on (cell, health), not on cell alone. That is what fixes the skipped-cell problem from minute 23. The direction in the minute-23 plan turned out not to be needed and was dropped in the code.

Complexity: health ≤ m + n ≤ 100, so at most 50 × 50 × 100 = 250,000 states with 4 moves each. A random 50 × 50 grid with health 100 ran in 73 ms.

## Edge cases (Step 3)

| Name | Input | Expected | What it tests |
|---|---|---|---|
| Start cell unsafe | [[1,0]], health = 1 | false | the start cell costs health too |
| End cell unsafe | [[0,1]], health = 1 | false | the last cell costs health too |
| All safe | [[0,0]], health = 1 | true | health 1 is enough |

`2 <= m * n` was read as a minimum of three cells; it is two (a 1 × 2 or 2 × 1 grid), which the three cases above already are.

Run before submitting: true, false, true on the three examples, false, false, true on the edge cases, 0 mismatches against a reference shortest-path solution over 5,000 random grids.

## Debrief — the answer-key approach (0-1 BFS)

The hidden minimisation: reaching the end with health at least 1 is possible exactly when the path through the **fewest unsafe cells** is safe. So store one number per cell, `dist[r][c]` = the fewest unsafe cells on any path from the start to (r, c), counting both ends, and answer `dist[m−1][n−1] < health`.

Every move costs 0 (safe cell) or 1 (unsafe cell). With only 0 and 1 costs, a deque replaces Dijkstra's heap: a 0-cost neighbour goes to the front, a 1-cost neighbour to the back, and a cell is re-added only when its `dist` improves. **O(m · n)**, one number per cell instead of up to 100 health values per cell.

Our state BFS is the same search spread over every health value; it passes because health ≤ m + n keeps it small. Checked against each other on 20,000 random grids: 0 mismatches.

```java
import java.util.*;

class Solution {
    public boolean findSafeWalk(List<List<Integer>> grid, int health) {

        int m = grid.size();
        int n = grid.get(0).size();

        int[][] dist = new int[m][n];
        for (int[] row : dist) {
            Arrays.fill(row, Integer.MAX_VALUE);
        }
        dist[0][0] = grid.get(0).get(0);

        Deque<int[]> dq = new ArrayDeque<>();
        dq.offerFirst(new int[]{0, 0});

        int[][] directions = {{-1, 0}, {0, 1}, {1, 0}, {0, -1}};

        while (!dq.isEmpty()) {
            int[] cell = dq.pollFirst();
            int row = cell[0];
            int col = cell[1];

            for (int[] d : directions) {
                int x = row + d[0];
                int y = col + d[1];
                if (x < 0 || y < 0 || x >= m || y >= n) continue;

                int cost = grid.get(x).get(y);
                if (dist[row][col] + cost < dist[x][y]) {
                    dist[x][y] = dist[row][col] + cost;
                    if (cost == 0) {
                        dq.offerFirst(new int[]{x, y});
                    } else {
                        dq.offerLast(new int[]{x, y});
                    }
                }
            }
        }
        return dist[m - 1][n - 1] < health;
    }
}
```

**What was missing at minute 16:** the question of what a yes or no answer depends on. Reaching with health at least 1 is the same as the cheapest path being cheap enough, so a feasibility question hides a minimisation. Once that is seen, the state shrinks from (cell, health) to one number per cell.

**Reflex:** can you reach the end with a budget, where each cell costs 0 or 1 → shortest path on cost, then compare with the budget; costs only 0 and 1 → 0-1 BFS with a deque.

**Syntax gap:** the record, the HashSet of records, the ArrayDeque and the directions array all came from Gemini. Same lesson as Weekly 528: the logic is there, the Java is not yet automatic.

## Final code (AC)

```java
class Solution {

    record Entry(int row, int col, int health) {}

    private boolean isValid(int i, int j, int m, int n) {
        return i >= 0 && j >= 0 && i < m && j < n;
    }

    public boolean findSafeWalk(List<List<Integer>> grid, int health) {

        int m = grid.size();
        int n = grid.get(0).size();

        int startHealth = health - grid.get(0).get(0);
        if (startHealth <= 0) return false;

        Set<Entry> visited = new HashSet<>();
        Queue<Entry> q = new ArrayDeque<>();

        Entry start = new Entry(0, 0, startHealth);
        q.offer(start);
        visited.add(start); 

        int[][] directions = {
            {-1, 0},
            {0, 1},
            {1, 0},
            {0, -1}
        };

        while (!q.isEmpty()) {
            Entry entry = q.poll();
            int row = entry.row();
            int col = entry.col();
            int incomingHealth = entry.health();

           
            if (row == m - 1 && col == n - 1 && incomingHealth > 0) {
                return true;
            }

            for (int[] direction : directions) {
                
                int x = row + direction[0];
                int y = col + direction[1];

                if (isValid(x, y, m, n)) {
                   
                    int updatedHealth = incomingHealth - grid.get(x).get(y);
                    Entry next = new Entry(x, y, updatedHealth);

                    if (updatedHealth > 0 && !visited.contains(next)) {
                        visited.add(next); 
                        q.offer(next);
                    }
                }
            }
        }
        return false;
    }
}
```
