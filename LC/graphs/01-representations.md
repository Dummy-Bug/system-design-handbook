# 01 — Graph Representations

## Adjacency List — List<List<Integer>>

```java
List<List<Integer>> graph = new ArrayList<>();
for (int i = 0; i < n; i++) graph.add(new ArrayList<>());

// Building from edges
for (int[] edge : edges) {
    graph.get(edge[0]).add(edge[1]);        // directed
    graph.get(edge[1]).add(edge[0]);        // undirected (add this line)
}

// Access neighbors of node i
for (int neighbor : graph.get(i)) {
    // process neighbor
}
```

**When to use:**
- Most LC graph problems (default choice)
- Nodes are 0 to n-1
- Need to iterate neighbors of a node efficiently

**Time complexity:**
- Build: O(E) where E = number of edges
- Iterate neighbors of node i: O(degree of i)
- Check if edge (i, j) exists: O(degree of i) — not O(1)

---

## Adjacency List — Map<Integer, List<Integer>>

```java
Map<Integer, List<Integer>> graph = new HashMap<>();

// Building from edges
for (int[] edge : edges) {
    graph.putIfAbsent(edge[0], new ArrayList<>());
    graph.putIfAbsent(edge[1], new ArrayList<>());
    
    graph.get(edge[0]).add(edge[1]);        // directed
    graph.get(edge[1]).add(edge[0]);        // undirected
}

// Access neighbors of node i (safe for missing keys)
for (int neighbor : graph.getOrDefault(i, new ArrayList<>())) {
    // process neighbor
}
```

**When to use:**
- Node IDs are arbitrary (not 0 to n-1)
- Sparse graphs where not all nodes may appear
- Graph is built incrementally

**Gotcha:**
- Always use `getOrDefault()` to avoid NullPointerException

---

## Adjacency List — Array of Lists

```java
List<Integer>[] graph = new List[n];
for (int i = 0; i < n; i++) graph[i] = new ArrayList<>();

// Building from edges
for (int[] edge : edges) {
    graph[edge[0]].add(edge[1]);        // directed
    graph[edge[1]].add(edge[0]);        // undirected
}

// Access neighbors
for (int neighbor : graph[i]) {
    // process neighbor
}
```

**When to use:**
- Competitive programming style (slightly cleaner than `List<List<>>`)
- Direct array indexing preferred

**Gotcha:**
- Must initialize each `graph[i]` to new ArrayList before using

---

## Adjacency Matrix

```java
boolean[][] graph = new boolean[n][n];

// Building from edges
for (int[] edge : edges) {
    graph[edge[0]][edge[1]] = true;        // directed
    graph[edge[1]][edge[0]] = true;        // undirected
}

// Check if edge (i, j) exists
if (graph[i][j]) { /* edge exists */ }

// Iterate neighbors of node i
for (int j = 0; j < n; j++) {
    if (graph[i][j]) {
        // j is a neighbor of i
    }
}
```

**When to use:**
- N is small (N ≤ 1000)
- Need O(1) edge existence check: `graph[i][j]`

**When NOT to use:**
- N is large (N = 10^5):
  - **MLE:** N² memory = 10^10 cells exceeds memory limit
  - **TLE:** Iterating neighbors is O(N) per node → O(N²) total traversal = 10^10 operations

---

## Edge List

```java
// Unweighted
int[][] edges = {{0,1}, {1,2}, {2,3}};

// Weighted
int[][] edges = {{0,1,5}, {1,2,3}, {2,3,7}};
// edges[i] = {from, to, weight}
```

**When to use:**
- Kruskal's MST: sort edges, process in order
- Bellman-Ford: iterate all edges multiple times
- Need to process **all edges globally**, not neighbors of a specific node

**When NOT to use:**
- Need to find neighbors of node i → O(E) scan each time
- Frequent neighbor lookups → use adjacency list instead

---

## Comparison Table

| Representation | Build | Check Edge (i,j) | Iterate Neighbors | Space | Best For |
|---|---|---|---|---|---|
| `List<List<>>` | O(E) | O(deg i) | O(deg i) | O(V+E) | Default LC |
| `Map<Integer, List<>>` | O(E) | O(deg i) | O(deg i) | O(V+E) | Arbitrary IDs |
| `List<Integer>[]` | O(E) | O(deg i) | O(deg i) | O(V+E) | Competitive style |
| `boolean[][]` | O(E) | **O(1)** | O(V) | O(V²) | Dense graphs, N ≤ 1000 |
| `int[][] edges` | O(1) | O(E) | O(E) | O(E) | Kruskal, Bellman-Ford |

---

## Gotchas

- **Never use matrix for large N** — instant MLE + TLE
- **Adjacency list**: check edge (i,j) is O(degree), not O(1) — if you need O(1) checks, use matrix or HashSet
- **For undirected graphs**, always add edges both ways: `graph[i].add(j)` AND `graph[j].add(i)`
- **Map vs List**: Map is slower (hash lookup) — use List if nodes are 0 to n-1
- **Edge list input**: Problem gives you edges as `int[][]` — decide whether to convert to adjacency list or use directly
