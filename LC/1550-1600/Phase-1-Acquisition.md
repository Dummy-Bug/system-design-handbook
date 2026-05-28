# Phase 1 — Acquisition (14 problems, topic-visible)

**Protocol:** topic is labeled — study-OK for blind spots. Must be clean first-submission AC to count as 1/3. Work through these before entering Phase 2.

| # | Topic | Problem | AR | QPos | Link |
|---|-------|---------|-----|------|------|
| 1 | Greedy / observation | Pancake Sorting | 71.8% | Q2 | https://leetcode.com/problems/pancake-sorting/ |
| 2 | Game theory | Alice and Bob Playing Flower Game | 60.0% | Q3 | https://leetcode.com/problems/alice-and-bob-playing-flower-game/ |
| 3 | Sliding window | Binary Subarrays With Sum | 68.8% | Q2 | https://leetcode.com/problems/binary-subarrays-with-sum/ |
| 4 | Graph / tree traversal | Restore the Array From Adjacent Pairs | 75.0% | Q2 | https://leetcode.com/problems/restore-the-array-from-adjacent-pairs/ |
| 5 | Bit operations / XOR | Count Number of Maximum Bitwise-OR Subsets | 89.5% | Q3 | https://leetcode.com/problems/count-number-of-maximum-bitwise-or-subsets/ |
| 6 | Difference array / prefix-range | Increment Submatrices by One | 73.8% | Q2 | https://leetcode.com/problems/increment-submatrices-by-one/ |
| 7 | Math / number theory | The k-th Lexicographical String of All Happy Strings of Length n | 87.1% | Q3 | https://leetcode.com/problems/the-k-th-lexicographical-string-of-all-happy-strings-of-length-n/ |
| 8 | Hashing / counting | Groups of Special-Equivalent Strings | 73.6% | Q2 | https://leetcode.com/problems/groups-of-special-equivalent-strings/ |
| 9 | Linear / grid / counting DP | Ways to Make a Fair Array | 66.9% | Q3 | https://leetcode.com/problems/ways-to-make-a-fair-array/ |
| 10 | Heap-greedy | Minimum Operations to Halve Array Sum | 50.2% | Q3 | https://leetcode.com/problems/minimum-operations-to-halve-array-sum/ |
| 11 | Monotonic stack (blind) | Next Greater Node In Linked List | 64.3% | Q3 | https://leetcode.com/problems/next-greater-node-in-linked-list/ |
| 12 | Tree DP (blind) | Construct Binary Search Tree from Preorder Traversal | 84.3% | Q4 | https://leetcode.com/problems/construct-binary-search-tree-from-preorder-traversal/ |
| 13 | Interval DP (blind) | Stone Game | 73.3% | Q2 | https://leetcode.com/problems/stone-game/ |
| 14 | Binary search (added 2026-05-28) | Closest Nodes Queries in a Binary Search Tree | 44.5% | Q2 | https://leetcode.com/problems/closest-nodes-queries-in-a-binary-search-tree/ |

> [!note] Why #14 was added (2026-05-28)
> The original taxonomy only bucketed "binary-search-on-answer" (marked absent in-band) and never created a slot for **plain binary search** (floor/ceil / lower_bound on a sorted array). That hole meant Closest Nodes was dealt blind in Phase 2 under a wrong "Tree DP" tag with no prior acquisition rep — so it hit cold and soft-failed on the `mid ± 1` mechanic. Closest Nodes is now the BS acquisition problem here (LC tags: Binary Search, BST). Its Phase-2 derivation rep is Time Based Key-Value Store [981].

---

## Tracker

| # | Topic | Phase 1 | Status |
|---|-------|---------|--------|
| 1 | Greedy | ☑ | pass — 58 min, first-submission AC, fix largest→smallest via double flip |
| 2 | Game theory | ☑ | pass — 47 min, first-submission AC, parity reduction + clamped odd-sum count |
| 3 | Sliding window | ☑ | pass — 26 min, first-submission AC, atMost(K)-atMost(K-1) trick |
| 4 | Graph / tree traversal | ☑ | pass — 38 min, first-submission AC, path graph + BFS from endpoint |
| 5 | Bit / XOR | ☑ | pass — 20 min, first-submission AC, subset enum (n≤16) + precompute maxOR |
| 6 | Difference array | ☑ | pass — 40 min, first-submission AC, 2D difference array (4 corners + two prefix sweeps) |
| 7 | Math / number theory | ☑ | soft fail (WA-then-AC) — impl bug in char selection |
| 8 | Hashing / counting | ☑ | hinted — read-error (wrong return value) + off-by-one in merge |
| 9 | DP | ☑ | pass — 30 min, first-submission AC, suffix odd/even prefix sums + parity flip |
| 10 | Heap-greedy | ☑ | soft fail (WA-then-AC) — used Float instead of Double, precision loss on large values |
| 11 | Monotonic stack | ☑ | pass — 37 min, first-submission AC, reverse LL + decreasing mono stack |
| 12 | Tree DP | ☑ | hinted — mixed preorder/inorder index in right subtree call |
| 13 | Interval DP | ☑ | pass — self-derived, correct logic, intentional TLE→AC (memo trivial) |
| 14 | Binary search | ☑ | soft fail — 40 min, TLE→AC; degraded BS to linear scan (`bound±1` instead of `mid±1`), 10¹⁰ ops. Approach derivation was instant; pure mechanic rust (first BS in ~1yr). See First-Attempt/24. |
