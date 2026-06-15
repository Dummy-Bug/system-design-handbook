# Closest Equal Element Queries — First Attempt

## Problem

You are given a circular array nums and an array queries.

For each query i, you have to find the following:

	The minimum distance between the element at index queries[i] and any other index j in the circular array, where nums[j] == nums[queries[i]]. If no such index exists, the answer for that query should be -1.

Return an array answer of the same size as queries, where answer[i] represents the result for query i.

 

Example 1:

Input: nums = [1,3,1,4,1,3,2], queries = [0,3,5]

Output: [2,-1,3]

Explanation:

	Query 0: The element at queries[0] = 0 is nums[0] = 1. The nearest index with the same value is 2, and the distance between them is 2.

	Query 1: The element at queries[1] = 3 is nums[3] = 4. No other index contains 4, so the result is -1.

	Query 2: The element at queries[2] = 5 is nums[5] = 3. The nearest index with the same value is 1, and the distance between them is 3 (following the circular path: 5 -> 6 -> 0 -> 1).

Example 2:

Input: nums = [1,2,3,4], queries = [0,1,2,3]

Output: [-1,-1,-1,-1]

Explanation:

Each value in nums is unique, so no index shares the same value as the queried element. This results in -1 for all queries.

 

Constraints:

	1 <= queries.length <= nums.length <= 10^5

	1 <= nums[i] <= 10^6

	0 <= queries[i] < nums.length

---

## First-attempt record

| Field | Value |
|-------|-------|
| Date | 2026-05-15 |
| Link | https://leetcode.com/problems/closest-equal-element-queries/description/ |
| Rating | ~1650-1700 |
| AC | Y |
| Time | approach derived 2026-05-15, coded + submitted 2026-05-16 (self-derived, no editorial/hint) |
| Pattern | Array doubling — linear left/right pass with mod |
| Revision due | 2026-05-30 |

---

#### Thought process (what was actually going through the mind)

**Step 1 — Brute force identified and rejected**
For each query, scan all other indices with the same value, compute circular distance, take minimum. O(n × q) in the worst case — too slow at n, q ≤ 10^5.

**Step 2 — Dead ends**
- Map from node to all reachable nodes: merging sets is O(n) per node → O(n²). Rejected.
- Storing `int[]{firstOcc, latestOcc}` per value: couldn't cleanly handle circular wrap.
- Left pass only up to n and a separate right pass: edge handling for the circular wrap was getting complex.

**Step 3 — Key insight: array doubling**
Treat the circular array as a linear array of length 2n by running indices 0 → 2n-1 with `nums[i % n]`. This converts the circular distance problem to a standard linear nearest-same-value problem.

- **Left pass** (0 → 2n-1): for each index i, check if `nums[i % n]` was seen before in the map. If yes, distance from left = `i - map.get(nums[i % n])`. Update map with current index.
- **Right pass** (2n-1 → 0): same logic in reverse, gives nearest same-value to the right.
- For each original index, answer = min(left distance, right distance).

Circular wrapping is handled automatically — the doubling ensures that a value at index n-1 can "see" a value at index 1 through the extended range without any special-case logic.

**Step 4 — Alternative noted**
Binary search on per-value index lists: store all indices for each value, binary search for nearest (with circular wrap handled separately). Same O(n log n) complexity but more implementation complexity. Doubling approach is simpler — stick with it.

---

#### Closing notes

**Key insight:** Array doubling (extend the array 0→2n-1 with mod indexing) converts any circular nearest-same-value problem into a standard linear left/right pass. No special circular wrap logic needed — the doubling handles it structurally.

**Guard for unique elements:** The `index%n == i%n` check catches when the only other "occurrence" the map sees is the same original position in the second half of the doubled array. Without this guard, unique elements would record a spurious distance of n. With it, they stay at MAX_VALUE → -1 in the final answer.

**Why the guard never fires incorrectly for multi-occurrence elements:** For any value with 2+ original indices k and m (k < m), the doubled array always has an occurrence of that value between positions n+k and k in the right sweep (specifically at position m). This intermediate occurrence updates the map before the sweep reaches k, so the map at i=k never points to n+k. The guard only fires in the unique-element case.

**Minor code quality note:** `int index = map.get(num)` is declared but then `map.get(num)` is called again in the distance calculation (`i - map.get(num)`, `map.get(num) - i`). Should use `index` in both branches — redundant lookup. Not a bug, just noise.

**Complexity:** O(n + q) time — two linear passes over the doubled array (4n iterations total), then q query lookups. O(n) space for left[], right[], and the map.

**Tracker:** 10/10 done in 1650-1700 band. Graduation audit next.
