# Phase 1 — Acquisition (1700-1750)

**Group A is EMPTY at this band.** Every pattern that appears at 1700-1749 is either (a) already installed at a lower band's Phase 1, or (b) too thinly supplied to install cleanly here. The whole band collapses to Phase 2 derivation reps.

Generated 2026-05-28. Same-day revisions applied the **thin-supply-defer rule** (a topic needs ≥3 in-band problems to support 1 acquisition + 2 derivation reps; below that, defer to the next band with healthier supply), then the **niche-topic-skip rule** for Geometry.

**Sources used:**
- LC tags + AR + difficulty: live-fetched from LC GraphQL → `zerotrac-data/band_1700_1749_lctags.tsv` (92 problems, all 1700-1749).
- Statements: read from `zerotrac-data/content-tsv/all_1700_with_content.tsv` for the Group A candidates (verified that LC-tag classifications weren't misleading). Full-band statement reading deferred until the topic map / Phase 2 queue is generated.
- Solved-here exclusions: `LC/1700-1750.md` lists 7 prior solves; 6 fall inside 1700-1749 (the 7th, Max Points Tasks With Two Techniques, is outside this slice).

---

## Why Group A is empty — the four candidate topics and their verdicts

A topic earns Group A only if (i) it's genuinely new at this band AND (ii) the band has ≥3 in-band problems for it (1 acquisition + 2 disguised derivation reps). Below that threshold, install at the next band where supply justifies — same precedent as Union-Find (deferred 1500-1550 → 1600-1650).

| Topic | In-band count | Viable (non-Design) | Verdict |
|-------|---------------|---------------------|---------|
| **Segment Tree / BIT** | 2 | 1 (Range Frequency Queries is Design-tagged → excluded) | **DEFER** → install at 1750-1800+ |
| **Bitmask DP** | 1 (Max Compatibility Score Sum) | 1, but m,n ≤ 8 lets backtracking brute-force pass — the intended bitmask DP isn't forced | **DEFER** → install at 1800+ |
| **Dijkstra / Shortest Path (weighted)** | 1 (Find Min Time to Reach Last Room I) | 1 | **DEFER** → install at 1750-1800+ |
| **Geometry** | 3 (Place People I · Circle & Rectangle Overlapping · Max Area Rectangle I) | 3 | **SKIP entirely** — niche LC topic, not a fundamental derivation-muscle pattern; supply doesn't densify at any higher band (1700-2049 all stay ~2-3 problems). Treat like Design: excluded as a target bucket. |

> [!info] Why defer instead of force on the first three
> Acquiring on a single in-band rep means the 3 cold cleans for ownership are 100% cross-band — which makes the same-band acquisition arbitrary. Installing where supply is real means the acquisition rep and the first two ownership reps all live in the same band, giving the pattern a real workout before the cross-band tail. The blind-spot trio at 1500-1700 formed exactly because acquisition was attempted on thin supply earlier.

> [!info] Why skip Geometry entirely instead of installing here
> Cross-band supply check showed Geometry stays ~2-3 problems per band from 1700 all the way to 2049 — it never densifies. So "defer to a richer band" is a fiction here; either you install at 1700-1749 or you never install. For contest rating 1700 + FANGM design rounds, Geometry isn't a recurring Q3/Q4 lock — when it does appear, it's solvable from first principles + math-reflex without a dedicated pattern install. Excluding it from target buckets is symmetric with the existing Design exclusion (CLAUDE.md: "Design is EXCLUDED at every band").

---

## Group A — empty

No acquisitions at this band.

---

## Group B — Already acquired in a lower band → Phase 2 only at 1700-1749

Every pattern below was installed at a lower band's Phase 1 (or in-band via the original zerotrac protocol). At 1700-1749 every 1700-1749 problem in these buckets is a **disguised/combined derivation rep** — they feed Phase 2 ownership counts here, not acquisition.

| Topic | Acquired at | Acquisition problem |
|-------|-------------|---------------------|
| Greedy / observation | 1500-1550 Phase 1 | Construct K Palindrome Strings |
| Linear / grid / counting DP | 1500-1550 Phase 1 | Count Sorted Vowel Strings |
| Graph BFS/DFS (unweighted) | 1500-1550 Phase 1 | Find All Groups of Farmland |
| Two-pointer / interval merge | 1500-1550 Phase 1 | Boats to Save People |
| Plain binary search (lower_bound) | 1500-1550 Phase 1 | Maximum Distance Between a Pair of Values |
| Monotonic stack (blind-spot) | 1500-1550 Phase 1 | Sum of Subarray Ranges |
| Tree DP / DFS (blind-spot) | 1500-1550 Phase 1 | Smallest Subtree with all the Deepest Nodes |
| Backtracking | 1500-1550 Phase 1 | Maximum Split of Positive Even Integers |
| Trie | 1500-1550 Phase 1 | Remove Sub-Folders from the Filesystem |
| Sliding window | 1500-1550 in-band | Min Subarray Length Distinct Sum ≥ K (#1) |
| Hashing / counting | 1500-1550 in-band | Count Special Triplets (#2), Rearrange K Substrings (#3) |
| Heap / top-k / heap-greedy | 1500-1550 in-band | Max Product of Three After Replacement (#5) |
| Math / number theory / bit | 1500-1550 in-band | Find Good Integers (#7), Largest Prime Consecutive Sum (#9) |
| Binary search on answer | 1500-1550 in-band | Minimum K to Reduce Array Within Limit (#8) |
| Prefix / sort-scan | 1500-1550 in-band | Count Special Triplets (#2) prefix; Special Array II (#6) |
| Game theory | 1550-1600 Phase 1 | Alice and Bob Playing Flower Game |
| Interval DP | 1550-1600 Phase 1 | Stone Game |
| Difference array / prefix-range | 1550-1600 derivation | Zero Array Transformation I (band #8), Increment Submatrices (2D, #18) |
| Union-Find / DSU (blind-spot) | 1600-1650 Phase 1 | Number of Operations to Make Network Connected |

> [!warning] 2026-05-28 audit — these were previously listed here but no longer install
> - **Topological sort** → moved to 1750-1799 Phase 1 (1650-1700 only had 2 reps, failed ≥3 rule)
> - **Monotonic deque / queue** → outlier (1 rep at 1650-1700, never ≥3 in any band 1500-1899)
> - **Quickselect** → outlier (2 reps at 1650-1700, never ≥3)
> - **Rolling hash** → outlier (1 rep at 1650-1700, never ≥3)
> - **Shortest path / Dijkstra** → deferred from 1600-1650 to 1850-1899

> [!important] What this means for ownership at 1700-1749
> Group B topics earn their 3 cold cleans here entirely through Phase 2 — each disguised 1700-1749 problem in a Group B bucket counts toward that bucket's ownership tally. The blind-spot trio (monotonic stack, tree DP, union-find) lives across multiple bands; reps here add to the cross-band ownership count, they don't restart it.

---

## Already solved in this band (excluded from Phase 2 selection later)

Logged in `LC/1700-1750.md` under the old (pre-Phase-system) zerotrac protocol — 6 of the 7 fall inside 1700-1749:

| # | Problem | Rating | LC tags | Outcome |
|---|---------|--------|---------|---------|
| 1 | Minimum Removals to Achieve Target XOR | 1745 | Array, DP, Bit Manipulation | clean (55min) |
| 2 | Pythagorean Distance Nodes in a Tree | 1725 | Tree, BFS | clean |
| 3 | Minimum Moves to Balance Circular Array | 1740 | Array, Greedy, Sorting | clean |
| 5 | Count the Number of Computer Unlocking Permutations | 1750 | Array, Math, Brainteaser, Combinatorics | clean |
| 6 | Distinct Points Reachable After Substring Removal | 1739 | Hash Table, String, Sliding Window, Prefix Sum | clean |
| 7 | Number of Perfect Pairs (logged as "Count Distinct Perfect Pairs") | 1716 | Array, Math, Two Pointers, Sorting | clean |

(Problem #4 "Maximum Points Tasks With Two Techniques" is outside the 1700-1749 slice — different rating bucket.)

These contribute to Phase 2 ownership counts for math, sliding window, prefix sum, tree BFS, and greedy when the rebuilt Phase 2 queue is generated.

---

## Deferred / skipped acquisitions — where each lands

| Topic | Status | Reason |
|-------|--------|--------|
| Segment Tree / BIT | DEFER → 1750-1800+ | only 1 non-Design rep in 1700-1749 |
| Dijkstra / Shortest Path (weighted) | DEFER → 1750-1800+ | only 1 rep in 1700-1749 |
| Bitmask DP | DEFER → 1800+ | only 1 rep + it's also brute-forceable at this rating |
| Geometry | SKIP entirely | thin everywhere (1700-2049); not a derivation-muscle target |

When generating the next band's Phase 1, check supply for the three DEFERRED topics first — if a band has ≥3 reps for any of them, install there.

---

## What comes next

There's no Group A to work through. The next step at this band is generating `1700-1750/_Sealed-Queue-Phase2.md` from the ~85 unsolved problems — two derivation-hard, disguised reps per Group B bucket, shuffled blind. Shortfalls (buckets with <3 in-band reps) stay uncapped and complete via cross-band reps at 1750-1800+.
