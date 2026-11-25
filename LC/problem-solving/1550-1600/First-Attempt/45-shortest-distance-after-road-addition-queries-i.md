# 45 — Shortest Distance After Road Addition Queries I

- **Link:** https://leetcode.com/problems/shortest-distance-after-road-addition-queries-i/ (LC 3243, rating 1568, AR 61.9%)
- **Format:** single timed problem under the 2026-11-22 format (15-minute target, 30-minute cap), unseen. Dealt from `_Blind-Queue.md` #3.
- **Bucket (revealed after the solve):** BFS: rebuild nothing, add the new road and run one BFS from 0 per query.
- **Timer:** 2026-11-25, 07:52.
- **AC:** 08:15, 23 minutes: 6 to the idea, 17 coding.
- **Result:** clean first-submission AC, self-derived. The only exchange was a correctness check on the idea before coding, answered correct with BFS. Counts toward coverage: DFS / BFS 1 of 2.

**Rewritten question:** after each new one-way road, how many roads does the shortest path from city 0 to city n − 1 take?

## The problem

Cities 0 to n − 1 start with a one-way road from each city i to i + 1. Each query adds a one-way road from u to v, with u < v. After each query, return the length of the shortest path from 0 to n − 1. `3 <= n <= 500`, `1 <= queries.length <= 500`.

## Timeline

| Time  | What                                                                                                                                                                                                                    |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 07:52 | Timer started.                                                                                                                                                                                                          |
| 07:58 | Read the constraints: n up to 500, up to 500 queries, so a full traversal per query is affordable. Idea: build the graph, and for each query add the edge, run DFS or BFS for the shortest path, and append the result. |
| 07:58 | Asked for a correctness check before coding: correct with BFS.                                                                                                                                                          |
| 08:15 | AC on the first submission.                                                                                                                                                                                             |
| 08:20 | Follow-up, after the AC: thinking on a walk about a version that does not BFS from city 0 on every query. Claude posted one in chat; the user has not looked at it and is deriving it alone.                            |
| 08:52 | Follow-up idea: an all-pairs grid d[u][v] = v − u. For a new road u → v, set d[u][n−1] = min(d[u][n−1], d[v][n−1] + 1), then d[0][n−1] = min(d[0][n−1], d[0][u] + d[u][n−1]). Asked for a correctness check: incorrect. |
| 09:16 | The grid was shown wrong on n = 6 with roads 3 → 5 then 0 → 2: it gave [4, 4] against [4, 3]. The user asked for the real solution and took the forward sweep step by step (10 steps, skipped 8 and 9). Saved below.    |

## The accepted code

```java
class Solution {

    Map<Integer,List<Integer>> graph;

    public int[] shortestDistanceAfterQueries(int n, int[][] queries) {

        graph = new HashMap<>();

        for (int i = 0; i < n - 1; i++){
            graph.put(i, new ArrayList<>(Arrays.asList(i + 1)));
        }

        int [] ans = new int[queries.length];
        int i = 0;

        for (int [] query : queries){
            List<Integer> edges = graph.getOrDefault(query[0] , new ArrayList<>());
            edges.add(query[1]);
            graph.put(query[0] , edges);

            ans[i] = helper(0,n-1);
            i++;
        }
        return ans;
    }

    private int helper(int start , int target){

        int ans = 0;
        Set<Integer> visited = new HashSet<>();
        Deque<Integer> q = new ArrayDeque<>();
        q.offer(start);

        while(!q.isEmpty()){

            int length = q.size();
            for (int i = 0; i < length; i++){

               int node = q.poll();

               if (node == target) return ans;

               for (int neighbor : graph.getOrDefault(node , new ArrayList<>())){

                if (!visited.contains(neighbor)){
                    q.offer(neighbor);
                    visited.add(neighbor);
                }
               }
            }
            ans++;
        }
        return ans;
    }
}
```

## Debrief

- **Reading the constraints picked the approach.** n and the query count are both at most 500, so one BFS per query is about 500 × 1,000 steps, and no cleverer update is needed. The idea took 6 minutes.
- **The shorter version:** the cities are exactly 0 to n − 1, so an array of lists `List<Integer>[] graph` replaces the HashMap, and every `getOrDefault` goes away. An `int[]` or `boolean[]` of size n does the same for the visited set.

## Follow-up: the forward sweep

Not needed at 1568; the editorial gives only BFS per query. It skips the work a BFS from city 0 repeats on every query, though the worst case per query is the same.

**The user's first try, an all-pairs grid, was wrong.** It updated only d[u][n−1] and d[0][n−1] for a new road u → v. On n = 6 with roads 3 → 5 then 0 → 2 it gave [4, 4] against [4, 3]: the road 3 → 5 also brought city 5 closer to city 2, the grid never stored that, and the next road read the old value.

**The idea, as taught step by step:**

1. Keep one number per city, `dist[x]`: the fewest roads from city 0 to city x. Every query asks only about city 0.
2. With only the i → i + 1 roads, `dist[x] = x`.
3. A new road u → v offers city v the distance `dist[u] + 1`.
4. If that is not smaller than `dist[v]`, no city changes, so the query costs no work.
5. Cities before v never change: every road goes forward, so the road overshoots them and there is no way back.
6. Cities from v onward may get closer, but only through v.
7. Sweep w = v, v + 1, ..., n − 1, and for every road w → x set `dist[x] = min(dist[x], dist[w] + 1)`.
8. Left to right is safe because every road into w starts at a smaller city, which the sweep has already handled, so `dist[w]` is final before it is passed on.

```figure
 city                      0   1   2   3   4   5
 start                     0   1   2   3   4   5

 road 3 → 5   offer dist[3] + 1 = 4 < 5, so dist[5] = 4
                           0   1   2   3   4   4     answer 4

 road 0 → 2   offer dist[0] + 1 = 1 < 2, so dist[2] = 1
   w = 2      2 → 3        0   1   1   2   4   4
   w = 3      3 → 4, 3 → 5 0   1   1   2   3   3
   w = 4      4 → 5        offer 4, keeps 3
                           0   1   1   2   3   3     answer 3
```

```java
class Solution {
    public int[] shortestDistanceAfterQueries(int n, int[][] queries) {
        List<Integer>[] graph = new List[n];
        int[] dist = new int[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
            if (i + 1 < n) graph[i].add(i + 1);
            dist[i] = i;
        }

        int[] ans = new int[queries.length];
        for (int q = 0; q < queries.length; q++) {
            int u = queries[q][0], v = queries[q][1];
            graph[u].add(v);
            if (dist[u] + 1 < dist[v]) {
                dist[v] = dist[u] + 1;
                for (int w = v; w < n; w++) {
                    for (int x : graph[w]) dist[x] = Math.min(dist[x], dist[w] + 1);
                }
            }
            ans[q] = dist[n - 1];
        }
        return ans;
    }
}
```

Checked by running: [3, 2, 1] and [1, 1] on the two LeetCode examples, and no mismatch against one BFS per query on 20,000 random small cases. Not submitted to LeetCode.

The version where a faster method is required is shortest-distance-after-road-addition-queries-ii (LC 3244, 2270), with n and the query count up to 10^5 and roads that never cross.

