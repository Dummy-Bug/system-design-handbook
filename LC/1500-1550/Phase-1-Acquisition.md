# Phase 1 — Acquisition (1500-1550 — BASE band)

**This is the floor of the acquisition ladder.** There is no lower band feeding it (1450-1500 was pre-system warm-up), so almost every core pattern *first appears here* and is acquired here. That means most patterns previously scheduled for acquisition at 1550-1600 are actually 1500-1550 topics — see the re-base note at the bottom.

> [!warning] Setup only. This band was worked under the old zerotrac protocol (9 problems logged, 1 failure); this file retrofits the Phase-1 structure onto it. Acquisition picks are easiest-per-bucket (highest AR, lowest Q-pos), verified against LC official `topicTags` (`zerotrac-data/band_1500_1549_lctags.tsv`), excluding the 9 already-logged.

---

## Group A — Acquire here (buckets not yet cleanly solved in-band)

Topic-visible, study-OK. Must be clean first-submission AC to count.

| # | Topic | Problem | AR | QPos | LC tags (verified) | Link |
|---|-------|---------|-----|------|--------------------|------|
| 1 | **Monotonic stack** (blind spot — FIRST appearance) | Sum of Subarray Ranges | 61.2% | Q2 | Stack, **Monotonic Stack** | https://leetcode.com/problems/sum-of-subarray-ranges/ |
| 2 | **Tree DP / DFS** (blind spot — FIRST appearance) | Smallest Subtree with all the Deepest Nodes | 77.6% | Q2 | **Tree, DFS**, BFS, Binary Tree | https://leetcode.com/problems/smallest-subtree-with-all-the-deepest-nodes/ |
| 3 | **Backtracking** (FIRST appearance) | Maximum Split of Positive Even Integers | 59.7% | Q3 | Math, **Backtracking**, Greedy | https://leetcode.com/problems/maximum-split-of-positive-even-integers/ |
| 4 | **Trie** (FIRST appearance) | Remove Sub-Folders from the Filesystem | 78.6% | Q2 | DFS, **Trie** | https://leetcode.com/problems/remove-sub-folders-from-the-filesystem/ |
| 5 | Greedy / observation | Construct K Palindrome Strings | 68.5% | Q2 | Hash Table, String, **Greedy**, Counting | https://leetcode.com/problems/construct-k-palindrome-strings/ |
| 6 | Linear / grid / counting DP | Count Sorted Vowel Strings | 79.3% | Q2 | Math, **DP**, Combinatorics | https://leetcode.com/problems/count-sorted-vowel-strings/ |
| 7 | Graph BFS/DFS / flood-fill | Find All Groups of Farmland | 75.5% | Q2 | **DFS, BFS**, Matrix | https://leetcode.com/problems/find-all-groups-of-farmland/ |
| 8 | Two-pointer / interval merge | Boats to Save People | 61.8% | Q2 | **Two Pointers**, Greedy, Sorting | https://leetcode.com/problems/boats-to-save-people/ |
| 9 | Plain binary search (lower_bound) | Maximum Distance Between a Pair of Values | 61.4% | Q2 | Array, Two Pointers, **Binary Search** | https://leetcode.com/problems/maximum-distance-between-a-pair-of-values/ |

---

## Already acquired in-band (via the 9 logged zerotrac solves)

No acquisition problem needed — exposed by prior solves; their disguised reps come from this band's Phase 2.

| Topic | Acquired via | Outcome |
|-------|--------------|---------|
| Sliding window | #1 Min Subarray Length Distinct Sum ≥ K | clean |
| Hashing / counting | #2 Count Special Triplets, #3 Rearrange K Substrings | clean |
| Heap / top-k | #5 Max Product of Three After Replacement | clean |
| Math / number theory / bit | #7 Find Good Integers, #9 Largest Prime Consecutive Sum | clean (vanilla) |
| **Binary search on answer** | #8 Minimum K to Reduce Array Within Limit | clean — **NOTE: this is the true first install of BS-on-answer** (not 1600-1650) |
| Prefix / sort-scan | #2, #9 (prefix exposure) | shaky — #4 Count Covered Buildings *failed*, #6 was not a clean rep; reinforce in Phase 2 |

---

## Tracker (Group A)

| # | Topic | Phase 1 | Status |
|---|-------|---------|--------|
| 1 | Monotonic stack | ☐ | — |
| 2 | Tree DP / DFS | ☐ | — |
| 3 | Backtracking | ☐ | — |
| 4 | Trie | ☐ | — |
| 5 | Greedy | ☐ | — |
| 6 | Linear / grid DP | ☐ | — |
| 7 | Graph BFS/DFS | ☐ | — |
| 8 | Two-pointer / interval merge | ☐ | — |
| 9 | Plain binary search | ☐ | — |

---
