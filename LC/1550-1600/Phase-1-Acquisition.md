# Phase 1 — Acquisition (1550-1600) — RE-BASED 2026-05-28

**The acquisition floor is 1500-1550, not this band.** After generating the 1500-1550 base Phase 1, almost every pattern turned out to first appear one band down — so 1550-1600 acquires only the patterns genuinely *new* at 1550. Everything else was installed at 1500-1550, which makes the 1550-1600 problems for those topics **derivation reps (Phase 2 material), not acquisitions.**

> [!warning] Setup/structure file. This band's 10 original solves happened before the Phase system; this file reclassifies them under the re-based ladder.

---

## Group A — Acquire here (genuinely new at 1550-1600)

Only two patterns have no 1500-1550 predecessor. Both were already solved clean in-band.

| # | Topic | Why new here | Problem | AR | QPos | Outcome | Link |
|---|-------|--------------|---------|-----|------|---------|------|
| 1 | **Game theory** | absent at 1500-1550 | Alice and Bob Playing Flower Game | 60.0% | Q3 | clean ✓ (47 min, parity reduction) | https://leetcode.com/problems/alice-and-bob-playing-flower-game/ |
| 2 | **Interval DP** | absent at 1500-1550 (first interval/minimax DP ≤1700) | Stone Game | 73.3% | Q2 | clean ✓ (self-derived) | https://leetcode.com/problems/stone-game/ |

---

## Group B — Acquired @ 1500-1550 → 1550-1600 problems are Phase 2 DERIVATION reps

These patterns were installed at the 1500-1550 floor. The problems below were originally mislabeled here as "Phase 1 acquisition," but at this harder band they are **derivation reps** — so the (already-completed) solves count toward **1550-1600 Phase 2 ownership**, not acquisition.

| Topic | Acquired @ 1500-1550 | 1550-1600 derivation rep (former "Phase 1") | Solve outcome |
|-------|----------------------|---------------------------------------------|---------------|
| Greedy / observation | #5 Construct K Palindrome Strings | Pancake Sorting | clean |
| Sliding window | in-band #1 Min Subarray Distinct Sum | Binary Subarrays With Sum | clean |
| Graph BFS/DFS / traversal | #7 Find All Groups of Farmland | Restore the Array From Adjacent Pairs | clean |
| Bit / XOR | in-band (bit solves) | Count Number of Maximum Bitwise-OR Subsets | clean |
| Difference array / prefix-range | in-band #2/#9 (prefix) | Increment Submatrices by One | clean |
| Backtracking | #3 Maximum Split of Positive Even Integers | The k-th Lexicographical Happy Strings (was mislabeled "Math") | soft fail |
| Hashing / counting | in-band #2/#3 | Groups of Special-Equivalent Strings | hinted |
| Linear / grid / counting DP | #6 Count Sorted Vowel Strings | Ways to Make a Fair Array | clean |
| Heap-greedy | in-band #5 Max Product of Three | Minimum Operations to Halve Array Sum | soft fail |
| Monotonic stack | #1 Sum of Subarray Ranges | Next Greater Node In Linked List | clean |
| Tree DP / DFS | #2 Smallest Subtree with Deepest Nodes | Construct BST from Preorder | hinted |
| Plain binary search (lower_bound) | #10 Maximum Distance Between a Pair of Values | Closest Nodes Queries in a BST | soft fail (the `mid±1` rust) |
| Trie | #4 Remove Sub-Folders from Filesystem | Search Suggestions System (unsolved — available as a Phase 2 deriv rep) | — |
| Math / number theory | in-band #7/#9 (sieve, enumeration) | Number of Subarrays With LCM Equal to K (unsolved — Phase 2 deriv rep) | — |

> [!important] What this means for ownership
> Group B topics need their **3 cold cleans at 1550-1600 via Phase 2**, exactly as before — but their *first* 1550-1600 problem (the "clean"/"soft"/"hinted" solves above) is now counted as a **derivation rep**, not an acquisition warm-up. The soft/hinted ones (backtracking, hashing, tree DP, plain BS, heap) did NOT clean — those reps reset and need redoing in Phase 2.

---

## Tracker (Group A only — Group B work lives in Phase 2)

| # | Topic | Phase 1 | Status |
|---|-------|---------|--------|
| 1 | Game theory | ☑ | clean — 47 min, parity reduction + clamped odd-sum count |
| 2 | Interval DP | ☑ | clean — self-derived, intentional TLE→AC (memo trivial) |
