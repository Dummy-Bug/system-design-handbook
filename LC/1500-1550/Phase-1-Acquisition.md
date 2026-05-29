# Phase 1 — Acquisition (1500-1550 — BASE band)

**This is the floor of the acquisition ladder.** No lower band feeds it, so almost every core pattern first appears here and is acquired here.

**RE-AUDITED 2026-05-28 at LearnYard subtopic granularity.** Earlier versions classified at broad LC-tag granularity (e.g. "Tree DP", "math/bit"). This version uses three stacked signals — doocs editorial algorithmic tags + doocs approach names + LC official tags — joined to LearnYard's 119-subgroup taxonomy. Supply data: `editorials-data/band_1500_1549_subgroup_supply.tsv`. Per-problem classification: `editorials-data/band_1500_1549_subgroups.tsv`.

> [!warning] Setup retrofit. This band was worked under the old zerotrac protocol (9 problems logged, 1 failure). This file retrofits the Phase-1 structure + subtopic taxonomy onto it. Acquisition picks = easiest single-pattern problem per subgroup (highest AR, lowest Q-pos), excluding the 9 already-logged.

> [!important] 1500-1550 is ACQUISITION-ONLY (decided 2026-05-29)
> This is the **floor band** — its sole job is to *install* each mechanic, i.e. get **one clean first-submission AC** per Group A bucket. There is **no Phase 2 / ownership grind in this band.** The 3-cold-clean **ownership** reps (rule 6 gate) begin at **1550-1600** and run **cross-band**. So here: a single clean AC = bucket acquired. A soft-fail bucket is acquired as soon as *any* later clean AC lands (it does not need 3 cleans here). Graduation of 1500-1550 = every Group A bucket acquired (one clean AC), phantoms deferred. Owning them comes later.

> [!success] BAND WRAPPED — 2026-05-29 (acquisition-only graduation)
> Every Group A bucket is acquired, deferred, or explicitly carried forward. **Session clean first-submission ACs (5):** Greedy (Construct K Palindrome, 57m) · Flood Fill (Find All Groups of Farmland, 25m) · Binary Tree (Smallest Subtree Deepest, 56m) · Two-Pointer (Maximum Distance, 14m) · Bitwise XOR (Min Ops XOR=K, 4m). **+ Monotonic Stack** acquired cross-band (1550-1600 #22). **+ Linear DP** acquired syntax-assisted (Count Sorted Vowel Strings — logic self-derived, Gemini syntax help; ☑*, would not count as ownership rep).
> **Carry-forwards (2):**
> - **Binary Search / Upper & Lower Bound — OPEN.** Its pick was solved via two-pointer (credited to #7), so the BS mechanic was never installed. Carries to **1550-1600**, where plain BS (floor/ceil/lower-bound) is a CORE bucket and gets genuine reps.
> - **Trie — DEFERRED.** No genuine trie-requiring problem in-band (all 3 are sort/prefix-solvable). Defers to the first higher band with a problem that *requires* a trie.
> Next active band: **1550-1600** (resume from its Phase-2 sealed queue to convert ◐ buckets → ●).

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

> [!danger] Trie pick is a phantom — bucket NOT covered despite clean AC (2026-05-29)
> #3 (Remove Sub-Folders) was solved first-attempt clean in 31min, but via **sort + prefix-set**, not a trie. The trie mechanic was never built, so the **Tries / Trie involving String bucket is NOT acquired** — the ☑* in the tracker means "problem AC'd, mechanic absent." Do **not** count Trie toward coverage. A problem that *genuinely requires* a trie (insert paths node-by-node, prune at a folder/word boundary, or prefix-search where sorting doesn't substitute) must be the rep that installs and later owns this bucket. Same phantom class as the removed Backtracking pick (greedy-solvable) and DP-on-Trees (traversal-solvable).

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
| **Tries / Trie involving String** | 3 tagged, 0 genuine | first band with a problem that *requires* a trie. All 3 in-band are sort/prefix-set-solvable (pick #3 Remove Sub-Folders AC'd 2026-05-29 without a trie). Phantom — defers like Backtracking. |
| **DP on Trees** (DP L2) | 0 | first band with ≥3 — the real "tree DP" blind-spot install (NOT the #2 traversal pick) |
| **Recursion & Backtracking** | 0 genuine (2 tagged, both greedy-solved) | first band whose editorial solution is genuinely backtracking |
| Union-Find / DSU | ~1 | 1600-1649 (7 reps there) |
| Game Theory | 0 | 1550-1599 |
| Matrix Chain Multiplication / Interval DP | 0 | 1550-1599 (Stone Game) |

---

## Tracker (Group A)

| # | LearnYard subgroup | Phase 1 | Status |
|---|--------------------|---------|--------|
| 1 | Stack / Monotonic Stack (blind-spot) | ☑ | **ACQUIRED cross-band.** First clean first-submission AC was 1550-1600 #22 Next Greater Node In Linked List (37min, 2026-05-28) — genuine monotonic stack (reverse list, strictly-decreasing stack, pop `<=`). Acquisition closed. The band's pick (Sum of Subarray Ranges) is now **optional** here — useful only as a cross-band **ownership** rep (rep 2/3 toward owning the blind-spot), not required for acquisition. |
| 2 | Binary Tree / Implementary | ☑ | **CLEAN** (first-attempt AC, 56min, 2026-05-29). Mechanic installed (LCA of deepest leaves = deepest path node where leftDepth==rightDepth). Solve was over-built (path store + reverse deque + shared maxDepth counter, O(n²)); clean idiom is one post-order pass returning (node, depth) tuple, O(n). Logged in `First-Attempt/12-smallest-subtree-with-all-the-deepest-nodes.md`. |
| 3 | ~~Tries / Trie involving String~~ → **DEFERRED** | ☑* AC only | Pick #3 (Remove Sub-Folders) AC'd clean first-attempt 31min 2026-05-29, but via sort + prefix-set — **trie never exercised**. All 3 Trie-tagged problems in-band are sort/prefix-solvable → **no genuine trie rep exists in this band**. Bucket **deferred to first higher band with a problem that requires a trie** (see Deferred table). Not counted toward 1500-1550 coverage. Logged in `First-Attempt/13-remove-subfolders-from-the-filesystem.md`. |
| 4 | Greedy / Part I | ☑ | **CLEAN** (first-attempt AC, 57min, 2026-05-29). Mechanic installed (odd-freq parity → `oddCount <= k <= n`). 27min was comprehension, not algorithm. Logged in `1450-1500.md` #12. |
| 5 | DP Level 1 / Linear DP | ☑* | **ACQUIRED (syntax-assisted, NOT clean cold).** Count Sorted Vowel Strings, 2026-05-29, over cap. State `(prev, length)` + `Σ_{i>=prev}` recurrence **self-derived** (the muscle this band trains) — but Java syntax help taken from Gemini, so it would NOT count as an ownership rep. Mechanic installed for acquisition. Reps to drill: BUP suffix-sum form + stars-and-bars closed form C(n+4,4). Logged in `First-Attempt/16-count-sorted-vowel-strings.md`. |
| 6 | Graphs / Flood Fill | ☑ | **CLEAN** (first-attempt AC, 25min, 2026-05-29). Mechanic installed (BFS connected-component + bounding corners). Nit: used `Set<String>` "r-c" instead of `boolean[][]`. Logged in `First-Attempt/11-find-all-groups-of-farmland.md`. |
| 7 | 2 Pointers / Two Pointer on Arrays | ☑ | **ACQUIRED** (clean). Original solve (Boats to Save People, 2026-05-28) soft-failed (2 WA → AC), but acquisition is satisfied by the clean AC on **Maximum Distance Between a Pair of Values** — cold first-submission, 14min, 2026-05-29 (dealt blind, monotonic two-pointer). Per acquisition-only band rule, that closes the bucket here. Ownership (3 cold cleans) is tracked from 1550-1600 cross-band. Logged in `First-Attempt/14-maximum-distance-between-a-pair-of-values.md`. |
| 8 | Binary Search / Upper & Lower Bound | ☐ | **NOT acquired.** The pick (Maximum Distance) was AC'd clean but via **monotonic two-pointer** — that solve is credited to bucket #7 (Two-Pointer), NOT here. The upper/lower-bound BS mechanic was never exercised, so this bucket stays open. BS *is* genuinely applicable to this problem (per-`i` binary-search the furthest `j`, O(m log n)) — a genuine BS rep is still needed: either re-solve this via `lowerBound`/`upperBound`, or a Phase-2 problem that forces it. BS-on-answer is already installed separately (Group B). |
| 9 | Bit Manipulation / Bitwise XOR | ☑ | **CLEAN** (first-attempt AC, 4min, 2026-05-29). Mechanic installed: `Integer.bitCount(arrayXor ^ k)` = Hamming distance = answer. Logged in `First-Attempt/15-minimum-operations-to-make-array-xor-equal-to-k.md`. |

---

## Data provenance

- Supply + easiest-pick: `editorials-data/band_1500_1549_subgroup_supply.tsv`
- Per-problem subgroup assignment: `editorials-data/band_1500_1549_subgroups.tsv`
- doocs editorials (algorithm names): `editorials-data/band_1500_1549/*.md` (112/112)
- LC tags + AR: `zerotrac-data/band_1500_1549_lctags.tsv`
- Taxonomy: `learnyard-data/subgroups.tsv` (119 subgroups)
- Classifier: `scripts/classify_band_to_learnyard.py`
