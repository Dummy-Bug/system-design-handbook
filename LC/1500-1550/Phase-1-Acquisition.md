# Phase 1 — Acquisition (1500-1550 — BASE band)

**This is the floor of the acquisition ladder.** No lower band feeds it, so almost every core pattern first appears here and is acquired here.

**RE-AUDITED 2026-05-28 at LearnYard subtopic granularity.** Earlier versions classified at broad LC-tag granularity (e.g. "Tree DP", "math/bit"). This version uses three stacked signals — doocs editorial algorithmic tags + doocs approach names + LC official tags — joined to LearnYard's 119-subgroup taxonomy. Supply data: `editorials-data/band_1500_1549_subgroup_supply.tsv`. Per-problem classification: `editorials-data/band_1500_1549_subgroups.tsv`.

> [!warning] Setup retrofit. This band was worked under the old zerotrac protocol (9 problems logged, 1 failure). This file retrofits the Phase-1 structure + subtopic taxonomy onto it. Acquisition picks = easiest single-pattern problem per subgroup (highest AR, lowest Q-pos), excluding the 9 already-logged.

---

## What the subtopic re-audit changed

| Change | Old (broad tag) | New (LearnYard subgroup) | Why |
|--------|-----------------|--------------------------|-----|
| #2 relabel | "Tree DP / DFS" | **Binary Tree / Implementary** | The pick (Smallest Subtree with Deepest Nodes) is tree *traversal*, not DP-on-Trees. doocs confirms: no DP in the editorial. **Real DP-on-Trees has 0 reps at 1500-1549** → defers to a band that has it. |
| #7 relabel | "Graph BFS/DFS / flood-fill" | **Graphs / Flood Fill** | Find All Groups of Farmland is grid-DFS = Flood Fill subgroup. |
| #10 ADD | (folded into math/bit) | **Bit Manipulation / Bitwise XOR** | 10 in-band reps of genuine XOR problems (Min Ops XOR=K, Count Triplets Equal XOR, etc.). Distinct from Math/NT — LearnYard treats Bit Manipulation as its own top-level topic. |
| Dropped | — | ~~String Matching~~, ~~Sorting~~, ~~Matrix~~ | String Matching's 3 "reps" are all actually Trie/two-pointer (incidental tag). Sorting (24) & Matrix (9) are scaffolding, not derivation-muscle targets — excluded like Design. |

---

## Group A — Acquire here (subtopic-labeled)

Topic-visible, study-OK. Must be clean first-submission AC to count. Deal blind (one bare link on "next").

| # | LearnYard subgroup | In-band supply | Problem | AR | QPos | Link |
|---|--------------------|---------------:|---------|-----|------|------|
| 1 | **Stack / Monotonic Stack** (blind-spot, foundational) | 2 | Sum of Subarray Ranges | 61.2% | Q2 | https://leetcode.com/problems/sum-of-subarray-ranges/ |
| 2 | **Binary Tree / Implementary** (foundational) | 4 | Smallest Subtree with all the Deepest Nodes | 77.6% | Q2 | https://leetcode.com/problems/smallest-subtree-with-all-the-deepest-nodes/ |
| 3 | **Tries / Trie involving String** | 3 | Remove Sub-Folders from the Filesystem | 78.6% | Q2 | https://leetcode.com/problems/remove-sub-folders-from-the-filesystem/ |
| 4 | **Greedy / Part I** | 25 | Construct K Palindrome Strings | 68.5% | Q2 | https://leetcode.com/problems/construct-k-palindrome-strings/ |
| 5 | **Dynamic Programming Level 1 / Linear DP** | 8 | Count Sorted Vowel Strings | 79.3% | Q2 | https://leetcode.com/problems/count-sorted-vowel-strings/ |
| 6 | **Graphs / Flood Fill** (foundational) | 2 | Find All Groups of Farmland | 75.5% | Q2 | https://leetcode.com/problems/find-all-groups-of-farmland/ |
| 7 | **2 Pointers / Two Pointer on Arrays** | 13 | Boats to Save People | 61.8% | Q2 | https://leetcode.com/problems/boats-to-save-people/ |
| 8 | **Binary Search / Upper Bound and Lower Bound** | 10 | Maximum Distance Between a Pair of Values | 61.4% | Q2 | https://leetcode.com/problems/maximum-distance-between-a-pair-of-values/ |
| 9 | **Bit Manipulation / Bitwise XOR** (NEW — surfaced by re-audit) | 10 | Minimum Number of Operations to Make Array XOR Equal to K | 85.5% | Q2 | https://leetcode.com/problems/minimum-number-of-operations-to-make-array-xor-equal-to-k/ |

> [!danger] Backtracking REMOVED 2026-05-28 (verification caught a phantom)
> Backtracking was Group A #3 (Maximum Split of Positive Even Integers). The editorial-correctness check found **zero genuine backtracking problems at 1500-1549** — both backtracking-tagged problems (Max Split, Max Strength of a Group) have **Greedy / Binary-Enumeration** editorial solutions, confirmed across doocs tags, LC tags, and editorial body. A solver finds greedy and never practices backtracking, so it fails as an acquisition. Backtracking is **foundational** → defers to the first band whose editorial solution is genuinely backtracking (generate permutations/combinations/subsets with pruning). Same phantom class as DP-on-Trees.

> [!note] Foundational picks with <3 supply still install (CLAUDE.md Step 4 rule)
> #1 Monotonic Stack (2) and #6 Flood Fill (2) are below the ≥3 advanced-topic threshold, but they are **foundational** patterns with genuine editorial solutions — install at first appearance regardless of supply. The 2nd/3rd ownership cleans come cross-band.

---

## Already acquired in-band via the 9 logged zerotrac solves → Group B (Phase 2 only)

No acquisition problem needed; disguised reps come from this band's Phase 2.

| LearnYard subgroup | In-band supply | Acquired via | Outcome |
|--------------------|---------------:|--------------|---------|
| Hashing / Implementary Problems | 40 | #2 Count Special Triplets, #3 Rearrange K Substrings | clean |
| Sliding Window / Dynamic Size | 10 | #1 Min Subarray Length Distinct Sum ≥ K | clean |
| Heap (Priority Queue) / Implementary | 3 | #5 Max Product of Three After Replacement | clean |
| Prefix Sum / Implementary | 7 | #2, #6 (prefix exposure) | shaky — reinforce in Phase 2 |
| Binary Search / Binary Search On Answer | 2 | #8 Minimum K to Reduce Array Within Limit | clean — **true first install of BS-on-answer** |
| (Math / Number Theory — no LearnYard subgroup) | 20 | #7 Find Good Integers, #9 Largest Prime Consecutive Sum | clean (vanilla) |

---

## Excluded as target buckets (not derivation-muscle)

| Subgroup | In-band supply | Why excluded |
|----------|---------------:|--------------|
| Sorting / Implementary | 24 | scaffolding — sorting is a sub-step, not a standalone derivation pattern |
| Matrix / Implementary | 9 | scaffolding — 2D iteration, folds into DP-on-Grid / Flood Fill |
| String Matching Algos / Pattern Matching | 3 | all 3 are actually Trie/two-pointer (incidental LC tag); no genuine KMP/Z-algo here |
| Stack / Implementary (non-monotonic) | 4 | 2 are monotonic (covered by #1); other 2 are trivial adjacent-dedup simulation |
| Design | — | CLAUDE.md rule — never a target |

---

## Deferred FROM this band (insufficient/zero supply here)

| LearnYard subgroup | In-band supply | Defer to |
|--------------------|---------------:|----------|
| **DP on Trees** (DP L2) | 0 | first band with ≥3 — the real "tree DP" blind-spot install (NOT the #2 traversal pick) |
| **Recursion & Backtracking** | 0 genuine (2 tagged, both greedy-solved) | first band whose editorial solution is genuinely backtracking |
| Union-Find / DSU | ~1 | 1600-1649 (7 reps there) |
| Game Theory | 0 | 1550-1599 |
| Matrix Chain Multiplication / Interval DP | 0 | 1550-1599 (Stone Game) |

---

## Tracker (Group A)

| # | LearnYard subgroup | Phase 1 | Status |
|---|--------------------|---------|--------|
| 1 | Stack / Monotonic Stack | ☐ | — |
| 2 | Binary Tree / Implementary | ☐ | — |
| 3 | Tries / Trie involving String | ☐ | — |
| 4 | Greedy / Part I | ☐ | — |
| 5 | DP Level 1 / Linear DP | ☐ | — |
| 6 | Graphs / Flood Fill | ☐ | — |
| 7 | 2 Pointers / Two Pointer on Arrays | ☐ | — |
| 8 | Binary Search / Upper & Lower Bound | ☐ | — |
| 9 | Bit Manipulation / Bitwise XOR | ☐ | — |

---

## Data provenance

- Supply + easiest-pick: `editorials-data/band_1500_1549_subgroup_supply.tsv`
- Per-problem subgroup assignment: `editorials-data/band_1500_1549_subgroups.tsv`
- doocs editorials (algorithm names): `editorials-data/band_1500_1549/*.md` (112/112)
- LC tags + AR: `zerotrac-data/band_1500_1549_lctags.tsv`
- Taxonomy: `learnyard-data/subgroups.tsv` (119 subgroups)
- Classifier: `scripts/classify_band_to_learnyard.py`
