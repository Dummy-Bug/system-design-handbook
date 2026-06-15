# Path Existence Queries in a Graph I — First Attempt

## Problem

You are given an integer n representing the number of nodes in a graph, labeled from 0 to n - 1.

You are also given an integer array nums of length n sorted in non-decreasing order, and an integer maxDiff.

An undirected edge exists between nodes i and j if the absolute difference between nums[i] and nums[j] is at most maxDiff (i.e., |nums[i] - nums[j]| <= maxDiff).

You are also given a 2D integer array queries. For each queries[i] = [ui, vi], determine whether there exists a path between nodes ui and vi.

Return a boolean array answer, where answer[i] is true if there exists a path between ui and vi in the i^th query and false otherwise.

 

Example 1:

Input: n = 2, nums = [1,3], maxDiff = 1, queries = [[0,0],[0,1]]

Output: [true,false]

Explanation:

	Query [0,0]: Node 0 has a trivial path to itself.

	Query [0,1]: There is no edge between Node 0 and Node 1 because |nums[0] - nums[1]| = |1 - 3| = 2, which is greater than maxDiff.

	Thus, the final answer after processing all the queries is [true, false].

Example 2:

Input: n = 4, nums = [2,5,6,8], maxDiff = 2, queries = [[0,1],[0,2],[1,3],[2,3]]

Output: [false,false,true,true]

Explanation:

The resulting graph is:

	Query [0,1]: There is no edge between Node 0 and Node 1 because |nums[0] - nums[1]| = |2 - 5| = 3, which is greater than maxDiff.

	Query [0,2]: There is no edge between Node 0 and Node 2 because |nums[0] - nums[2]| = |2 - 6| = 4, which is greater than maxDiff.

	Query [1,3]: There is a path between Node 1 and Node 3 through Node 2 since |nums[1] - nums[2]| = |5 - 6| = 1 and |nums[2] - nums[3]| = |6 - 8| = 2, both of which are within maxDiff.

	Query [2,3]: There is an edge between Node 2 and Node 3 because |nums[2] - nums[3]| = |6 - 8| = 2, which is equal to maxDiff.

	Thus, the final answer after processing all the queries is [false, false, true, true].

 

Constraints:

	1 <= n == nums.length <= 10^5

	0 <= nums[i] <= 10^5

	nums is sorted in non-decreasing order.

	0 <= maxDiff <= 10^5

	1 <= queries.length <= 10^5

	queries[i] == [ui, vi]

	0 <= ui, vi < n

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-15 |
| Link | https://leetcode.com/problems/path-existence-queries-in-a-graph-i/ |
| Rating | ~1650-1700 |
| AC | Y |
| Time | 40min (self-derived, 1 WA) |
| Pattern | Connected components via adjacent edge scan |
| Revision due | 2026-05-29 |

---

#### Thought process (what was actually going through the mind)

**Step 1 — Brute force identification**
First thought: for each query check if direct edge exists (O(1)), else BFS/DFS to find path. Brute force for Q queries with N nodes → O(Q × N) in the worst case — too slow at N, Q ≤ 10^5.

**Step 2 — Non-graph approach (dead end)**
Tried to build a map from each node to all reachable nodes incrementally from right to left. But merging sets naively is O(n) per node → O(n²) total. Dead end.

**Step 3 — Key insight: connected components**
If two nodes are reachable from each other, they're in the same connected component. Precompute all components once, then answer each query in O(1) by comparing component IDs.

**Step 4 — Why only adjacent edges matter**
Because nums is sorted, if an edge exists between i and j (non-adjacent, i < j), then `nums[i+1] - nums[i] ≤ nums[j] - nums[i] ≤ maxDiff` → the adjacent edge (i, i+1) also exists. Transitivity chains all intermediate nodes. So connected components are fully determined by adjacent-pair edges alone.

Only check `|nums[i+1] - nums[i]| ≤ maxDiff` for each i — skip all non-adjacent pair checks.

**Step 5 — Component assignment (linear scan)**
Iterate left to right. If adjacent pair has an edge, propagate current component ID rightward. If no edge, current node starts a new component (its own ID).

**Step 6 — WA on first submission**
Bug: `components[n-1]` initialized to -1 and never updated when the last pair has no edge. Any query involving the last node compared against another -1 node returned true incorrectly.

Fix: initialize `components[n-1] = n-1` upfront (isolated last node gets its own component). Add fallback `if (components[i] == -1) components[i] = i` after the main conditional to cover all isolated nodes not reached by any left neighbor.

---

#### Closing notes

**Key insight:** Sorted array + maxDiff edge condition means connected components are contiguous segments. Only adjacent edges need to be checked — non-adjacent edges are redundant because all intermediate edges already exist.

**Bug worth remembering:** Always handle the last node (and any isolated node) explicitly. When a linear scan propagates state rightward, the rightmost node and any node with no left neighbor that connects may never receive an update. The `-1` sentinel then creates false matches on queries.

**Alternative:** Union-Find is the canonical tool for connectivity queries with offline edge construction. The linear scan works here because components are contiguous (sorted array property), but Union-Find generalizes to non-sorted inputs. Worth revisiting once Union-Find syntax is fresh.

**Tracker:** 9/10 done in 1650-1700 band. 1 more to complete the set.

---
