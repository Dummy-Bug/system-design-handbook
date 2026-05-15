# DFS — Depth First Search

---

## Recursive DFS — Basic Traversal

```java
boolean[] visited = new boolean[n];

void dfs(int node, List<List<Integer>> graph) {
    visited[node] = true;

    for (int neighbor : graph.get(node)) {
        if (!visited[neighbor]) {
            dfs(neighbor, graph);
        }
    }
}
```

> [!tip] When to use
> - Explore all nodes reachable from a starting node
> - Connected components, flood fill, path existence

---

## Recursive DFS — With Return Value

```java
boolean[] visited = new boolean[n];

boolean dfs(int node, int target, List<List<Integer>> graph) {
    if (node == target) return true;
    visited[node] = true;

    for (int neighbor : graph.get(node)) {
        if (!visited[neighbor]) {
            if (dfs(neighbor, target, graph)) return true;
        }
    }
    return false;
}
```

> [!tip] When to use
> - Path finding: does a path exist from A to B?
> - Cycle detection (return true when you revisit a node)

---

## Recursive DFS — Grid (4-directional)

```java
int[][] dirs = {{0,1},{0,-1},{1,0},{-1,0}};

void dfs(int r, int c, boolean[][] visited, int[][] grid) {
    visited[r][c] = true;

    for (int[] d : dirs) {
        int nr = r + d[0], nc = c + d[1];
        if (nr >= 0 && nr < grid.length
                && nc >= 0 && nc < grid[0].length
                && !visited[nr][nc]) {
            dfs(nr, nc, visited, grid);
        }
    }
}
```

> [!tip] When to use
> - Grid problems: number of islands, flood fill, surrounded regions
> - 4-directional movement (up/down/left/right)

> [!danger] Gotcha
> Bounds check order matters — always check `nr >= 0 && nr < rows` before accessing `grid[nr][nc]` or you'll get ArrayIndexOutOfBoundsException

---

## Iterative DFS — Explicit Stack

```java
// added after Socratic session
```

---

## Connected Components Pattern

```java
// Call DFS for every unvisited node — each call = one component
int components = 0;
boolean[] visited = new boolean[n];

for (int i = 0; i < n; i++) {
    if (!visited[i]) {
        dfs(i, graph);
        components++;
    }
}
```

> [!tip] When to use
> - Count number of connected components
> - Number of islands, friend circles, province counting

---

> [!danger] Gotchas
> - **Always mark visited BEFORE recursing** — not after. Marking after causes infinite loops on cycles.
> - **Stack overflow risk** — if N ≥ 10^5 and graph could be a straight chain (linear path), use iterative DFS instead
> - **Grid problems** — use `visited[][]` OR modify the grid in-place (`grid[r][c] = 0`) to mark visited. In-place is O(1) space but destructive.

---

> [!important] When to use Iterative DFS instead
> - N ≥ 10^5 AND graph could be a linear chain → recursion depth = N → stack overflow
> - Problem explicitly asks for iterative solution
> - Skewed tree input (BST degenerated to linked list)
