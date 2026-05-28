# 1600-1650 Band — Full Topic Map (all 90 problems)

> [!danger] SPOILER — this file labels every problem with its solution pattern and set (A/B). Do **not** read it before solving the blind queue (`_Sealed-Queue.md`). Use it only for planning and post-solve debrief.

Built 2026-05-26 by reading every problem statement (rating ≤ 1650) from `zerotrac-data/content-tsv/all_1600_with_content.tsv`. Pattern = the *primary* technique the intended solution uses, judged from the actual statement (not the title, not the math-topic tag in the tsv).

**Legend:** ✅ done · ⏭️ skipped · ⭐ recommended next (gap-filling, high transfer)

---

## Coverage summary

| Pattern | # problems | Done? | Priority to train |
|---------|-----------|-------|-------------------|
| Hashing / counting | 14 | ✅✅✅ (3 done) | low — already strong |
| Linear / grid DP | 9 | ✅✅ (2 done) | low-med |
| Greedy / observation | 13 | — | med |
| Sliding window / prefix-count | 7 | ✅ (1 done) | med |
| Math / bit / parity (tsv-tagged) | 16 | — | **CORE — needs ownership** (math-reflex = recall only) |
| **Binary search on answer** | **4** | ❌ none | **HIGH — gap** |
| **Monotonic stack** | **2** | ❌ none | **HIGH — gap** |
| **Tree DP / DFS** | **6** | ❌ none | **HIGH — gap** |
| **Union-Find (DSU)** | **4** | ❌ none | **HIGH — gap (newly found)** |
| **Graph BFS/DFS / flood-fill** | **7** | ❌ none | **MED-HIGH — gap** |
| Trie | 1 | ❌ none | low |
| Interval DP | **0** | — | n/a — absent at this band (1700+ topic) |

The four ❌ HIGH rows are where contest Q3 lives. You've done 7 problems and **zero** of them touch a stack, a binary-search-on-answer, a tree recursion, or a DSU.

---

## Problem sets

- **Phase 1 — GENERATED 2026-05-28, RE-BASED to the 1500-1550 floor:** `Phase-1-Acquisition.md`. **Group A (acquire here) = 2:** **Union-Find** (scarce at 1500-1550, real supply here) and **Shortest path / Dijkstra** (absent below). Binary-search-on-answer (→1500-1550 #8) and Trie (→1500-1550 #4) demoted to Group B — acquired at the floor, so their 1600-1650 problems are Phase 2 derivation reps. **Design is removed entirely (not a target at any band).** Every bucket verified against LC official `topicTags`; all 8 already-solved excluded. AR + tags for all 90 at `zerotrac-data/band_1600_1649_with_ar.tsv`.
- **Phase 2 — not yet generated** (derivation, disguised/combined, blind shuffled). The old `_Sealed-Queue.md` (two-set A/B system) is superseded but left in place.

> [!note] Binary search taxonomy fix (from 1550-1600 audit, 2026-05-28)
> The coverage summary below lists "Binary search on answer ×4" — that's correct for this band's *new* mechanic. **Plain binary search** (floor/ceil/lower_bound on sorted data) is a *separate* pattern, acquired at 1550-1600 (Closest Nodes, Time Based KV), so it is NOT a Phase 1 topic here. Do not conflate the two — that conflation is what caused the Closest Nodes mislabel.

**Graduation (rule 6, ownership-based):** every core bucket must reach `●` (3 cold first-submission cleans, reps 2-3 disguised). Interval DP is absent at this band — shortfall completes at 1550-1600 (Stone Game).

---

## Ownership tracker

Owned = **3 cold first-submission cleans**, reps 2-3 disguised/combined (rule 6). Marks: `◯` 0/3 · `◐` 1-2/3 · `●` owned. Only clean first-submission counts; soft-fail (#1,#2,#4) and hinted (#5,#6) = 0.

| Core bucket | Cold cleans | Status | Need |
|-------------|-------------|--------|------|
| Greedy / prefix-suffix scan | 1 (#3) | ◐ | 2 disguised |
| Hashing / counting | 1 (#7) | ◐ | 2 disguised (#2,#6 didn't count) |
| Linear / grid DP | 0 (#1 soft, #5 hinted) | ◯ | 3 |
| Sliding window | 0 (#4 soft) | ◯ | 3 |
| Graph BFS/DFS | 0 | ◯ | 3 |
| Math / number theory / bit | 0 | ◯ | 3 — math-reflex ≠ solving |
| **Monotonic stack** (blind) | 0 | ◯ | acquisition + 3 |
| **Binary search on answer** | 0 in band | ◯ | 3 (cross-band rep exists @1500-1550) |
| **Tree DP** (blind) | 0 | ◯ | acquisition + 3 |
| **Union-Find** (blind) | 0 | ◯ | acquisition + 3 |

---

## What's already trained (the 7 solved, on both axes)

Depth scored from how the solve actually went (verdicts + WA-causes are the evidence).

| # | Problem | Breadth (pattern) | D×C | Note |
|---|---------|-------------------|-----|------|
| 1 | House Robber V | linear DP (constrained) | 6 | 4 WAs on recurrence (`logic-recurrence`) |
| 2 | Count Caesar Cipher Pairs | hashing + pair-count | 4 | delta-vs-cumulative bug |
| 3 | Split Array Min Difference | greedy prefix/suffix scan | 6 | shared-element reframe (deck Card 01); clean |
| 4 | Min Discards Balance Inventory | fixed sliding window | 6 | item-vs-arrival misread (`read-error`) |
| 5 | Min Cost Path Alt Dir II | grid DP | 6 | cost mechanics misread ×2 (`read-error`), hinted |
| 6 | Identify Largest Outlier | hashing + algebra reframe | 9 | index-aliasing recognition, hinted both attempts |
| 7 | Sum of Digit Differences | digit-position freq count | 2 | clean, fast |
