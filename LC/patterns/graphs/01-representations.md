# Graph Representations

---

## Adjacency List — `List<List<Integer>>`

```java
List<List<Integer>> graph = new ArrayList<>();
for (int i = 0; i < n; i++) graph.add(new ArrayList<>());

for (int[] edge : edges) {
    graph.get(edge[0]).add(edge[1]);   // directed
    graph.get(edge[1]).add(edge[0]);   // undirected — add this line
}

for (int neighbor : graph.get(i)) {
    // process neighbor
}
```

> [!tip] When to use
> - Default choice for most LC graph problems
> - Nodes are `0` to `n-1`
> - Need to iterate neighbors efficiently

> [!info] Complexity
> - Build: `O(E)`
> - Iterate neighbors of `i`: `O(degree of i)`
> - Check if edge `(i,j)` exists: `O(degree of i)` — not O(1)
> - Space: `O(V + E)`

---

## Adjacency List — `Map<Integer, List<Integer>>`

```java
Map<Integer, List<Integer>> graph = new HashMap<>();

for (int[] edge : edges) {
    graph.putIfAbsent(edge[0], new ArrayList<>());
    graph.putIfAbsent(edge[1], new ArrayList<>());
    graph.get(edge[0]).add(edge[1]);   // directed
    graph.get(edge[1]).add(edge[0]);   // undirected
}

for (int neighbor : graph.getOrDefault(i, new ArrayList<>())) {
    // process neighbor
}
```

> [!tip] When to use
> - Node IDs are arbitrary (not `0` to `n-1`)
> - Sparse graphs where not all nodes may appear in input

> [!danger] Gotcha
> Always use `getOrDefault()` — never `get()` directly, risks NullPointerException

---

## Adjacency List — `List<Integer>[]`

```java
List<Integer>[] graph = new List[n];
for (int i = 0; i < n; i++) graph[i] = new ArrayList<>();

for (int[] edge : edges) {
    graph[edge[0]].add(edge[1]);   // directed
    graph[edge[1]].add(edge[0]);   // undirected
}

for (int neighbor : graph[i]) {
    // process neighbor
}
```

> [!tip] When to use
> - Same as `List<List<>>` but with cleaner array-index access
> - Common in competitive programming style

> [!danger] Gotcha
> Must initialize each `graph[i] = new ArrayList<>()` before use — or NullPointerException

---

## Adjacency Matrix

```java
boolean[][] graph = new boolean[n][n];

for (int[] edge : edges) {
    graph[edge[0]][edge[1]] = true;   // directed
    graph[edge[1]][edge[0]] = true;   // undirected
}

// O(1) edge check
if (graph[i][j]) { /* edge exists */ }

// Iterate neighbors of node i
for (int j = 0; j < n; j++) {
    if (graph[i][j]) { /* j is a neighbor */ }
}
```

> [!tip] When to use
> - `N` is small (`N ≤ 1000`)
> - Need **O(1)** edge existence check: `graph[i][j]`

> [!danger] Never use when N is large
> `N = 10^5` → **MLE**: `N²` cells = `10^10` bytes in memory
> `N = 10^5` → **TLE**: iterating neighbors is `O(N)` per node = `O(N²)` total

---

## Edge List

```java
// Unweighted
int[][] edges = {{0,1}, {1,2}, {2,3}};

// Weighted — {from, to, weight}
int[][] edges = {{0,1,5}, {1,2,3}, {2,3,7}};
```

> [!tip] When to use
> - **Kruskal's MST** — sort edges by weight, process globally
> - **Bellman-Ford** — iterate all edges `N-1` times
> - Problems processing **all edges globally**, not neighbors of a specific node

> [!danger] When NOT to use
> Need to find neighbors of node `i` → `O(E)` scan every time. Use adjacency list instead.

---

## Comparison Table

| Representation | Check Edge `(i,j)` | Iterate Neighbors | Space | Best For |
|---|---|---|---|---|
| `List<List<>>` | `O(deg i)` | `O(deg i)` | `O(V+E)` | Default LC |
| `Map<List<>>` | `O(deg i)` | `O(deg i)` | `O(V+E)` | Arbitrary node IDs |
| `List<>[]` | `O(deg i)` | `O(deg i)` | `O(V+E)` | Competitive style |
| `boolean[][]` | **`O(1)`** | `O(V)` | `O(V²)` | Dense graphs, `N ≤ 1000` |
| Edge list `int[][]` | `O(E)` | `O(E)` | `O(E)` | Kruskal, Bellman-Ford |

---

> [!important] Golden Rules
> - **Large N?** → Adjacency list only. Matrix = instant MLE + TLE.
> - **Undirected graph?** → Always add edge both ways: `graph[i].add(j)` AND `graph[j].add(i)`
> - **Need O(1) edge check?** → Use matrix (only when N is small) or swap `List` for `HashSet` in adjacency list
> - **Map vs List?** → Use `List<List<>>` when nodes are `0` to `n-1` — Map has hash overhead
