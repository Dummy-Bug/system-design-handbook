# 1600–1699 Band — Topic Map & Ownership Tracker

> Built 2026-06-09. **SPOILER FILE** — do not read pattern/set columns before a blind solve.
> **This is a 100-point band** (deliberate width change from the prior 50-pt slices). Rationale below.
> Purpose: (1) the canonical topic list for this band, (2) per-bucket ownership against rule 6,
> (3) the carried debts rolled in from 1550-1600, (4) seed inventory of prior 1600-1700 work pending re-audit.

---

## Why this band is 100 points wide (1600–1699, not 1600–1650)

Decided 2026-06-09. A 50-point gap is difficulty-noise (a 1625 problem ≈ a 1675 problem; the 1600-1650 log already shows its misses are comprehension/careless, not algorithm). Going 100-wide:

1. **Consolidates fragmented work** — 7 logged at `1600-1650/` + 10 at `1650-1700/` were two half-finished stubs. Merged into one band → less fragmentation (itself a source of the "endless" feeling).
2. **Doubles per-bucket supply** — the literal pain at 1550-1600 was scarcity (mono-stack 1, trie 1, DSU 2). 182 band problems means 2 clean reps are gettable in-band instead of scrounging cross-band.
3. **Pulls owed blind-spots in-band** — Union-Find (~11) and Tree (~20) are well-supplied here, so two of the three blind-spots can finally be **owned in-band**. Interval-DP (absent ≤1650) also becomes in-band.

Cost acknowledged: wider ≠ faster to graduate (more total problems). The win is *enough supply to own each bucket*, not speed.

**This is tracked roll-forward, NOT the skip-3 sin** (rule 8). The historical failure was *untracked* skip; here every carried debt is pre-filled below and must still be paid.

---

## Band stats & data provenance

- **182 problems**, Q-spread: **Q1 ×3 · Q2 ×92 · Q3 ×81 · Q4 ×6** — solidly mid-contest.
- **Topic supply** below is synthesized from: LearnYard subgroups (`editorials-data/band_1600_1649_subgroups.tsv`, classifies only the 1600-1649 half) + official LC tags across the full band (`zerotrac-data/band_1600_1649_lctags.tsv` + `band_1650_1699_lctags.tsv`). LC-tag counts are multi-label estimates, not exact.
- Editorials: `editorials-data/band_1600_1649/` (1600-1649 only at time of writing).

---

## Band topic supply (coarse ownership buckets; DP by sub-pattern)

| Bucket | ~Supply | Status for us |
|---|---|---|
| Hashing / Counting | ~52 | ◐ carried 1/2 — abundant |
| Sorting | ~40 | substrate (rarely the credited mechanic) |
| Greedy | ~32 | ● OWNED (carryover) |
| Math / NT / Combinatorics | ~32 | ● OWNED (carryover) — folds in Game-Theory/parity & most Invariant/Reframe |
| Graph (BFS/DFS/traversal) | ~35 | ● OWNED (carryover) |
| Matrix | ~22 | grid-traversal substrate |
| Binary Search | ~18 | ◐ carried 0/2 — abundant (+ plain-BS owed from 1500-1550) |
| Prefix Sum | ~17 | ● OWNED (carryover) |
| Heap | ~16 | ◐ carried 0/2 — abundant |
| Bit Manipulation | ~13 | ◐ informal reps, formalize 0/2 (core) |
| **Tree / Binary Tree** | ~20 | ★ **blind-spot (tree-DP) — now ownable in-band** |
| **Union-Find** | ~11 | ★ ✅ **OWNED 2/2** (#01, 2026-06-10) — blind-spot closed |
| Two Pointers | ~11 | ◐ carried 0/2 |
| DP » Linear | ~10 | ◐ carried 0/2 |
| Sliding Window | ~8 | ● OWNED (carryover) |
| Backtracking | ~5 | ◐ carried 1/2 |
| Stack (plain) | ~5 | ◐ carried 0/2 |
| DP » String | ~4 | ◐ carried 0/2 |
| DP » Grid | ~2 | ◐ carried 1/2 |
| DP » Interval | enters @1650+ | ◐ carried 1/2 — **now in-band** (was cross-band) |
| **Monotonic Stack** | ~2 | ★ blind-spot, carried 1/2 — scarce (1 more: carried #9 max-chunks or in-band) |
| Trie | ~4 | ⊘ deferred — acquire cross-band |
| Topological Sort | ~2 | ⊘ **DEFERRED to next band** (too thin to own) |
| Dijkstra / Shortest Path | ~1 | ⊘ **DEFERRED to next band** (too thin to own) |
| Segment Tree / BIT | ~2 | ⊘ outlier-class (skip) |
| Design / Simulation / Enumeration | ~26 | ⊘ defer / substrate (not ownership targets) — [[lc-defer-design-problems-reflex-track]] |

---

## Ownership tracker (rule 6: owned = **2 clean self-derived first-submission ACs** on distinct problems)

> Carried-in from 1550-1600: owned buckets stay owned (a 1575-difficulty rep is a valid rep — 50pts is noise);
> open buckets carry their partial count. As we solve in-band, increment here. `★` = blind-spot trio (rule 6B).

### ● OWNED (carryover — no further reps needed)
| Bucket | Source |
|---|---|
| Greedy | 1550-1600 (01,02,05,20,29) |
| Prefix Sum / Diff-Array | 1550-1600 (08,17,18,39) |
| Sliding Window | 1550-1600 (10,14,25,26) |
| Graph traversal (DFS/BFS) | 1550-1600 (09,16) |
| Math / NT / Combinatorics | 1550-1600 (04,23) — incl. parity/game-theory & Invariant/Reframe flavor |
| **Union-Find / DSU ★** | 1550-1600 #37 + **1600-1699 #01 satisfiability-of-equality-equations (2026-06-10, clean)** — blind-spot CLOSED |
| **Backtracking / Subset-Enum** | 1550-1600 #19 + **1600-1699 #05 find-the-punishment-number (2026-06-11, clean self-derived)** |

### ◐ / ○ TO OWN (carried debt + blind-spots) — **13 buckets** _(Union-Find closed 2026-06-10; Backtracking closed 2026-06-11)_
| Bucket | Carried count | Owe | Notes |
|---|---|---|---|
| Hashing (canonical/counting) | 1/2 (33) | **1** | abundant supply |
| Two Pointers | 0/2 | **2** | 32 soft-fail, 35 soft-hinted, 38 hard-fail at 1550-1600 (none counted) |
| Binary Search | 0/2 | **2** | + plain-BS owed from 1500-1550 |
| Heap | 0/2 | **2** | 21 soft-fail at 1550-1600 |
| Bit Manipulation | 0/2 | **2** | informal reps only (01,19 folded elsewhere) — formalize |
| Stack (plain) | 0/2 | **2** | 30 hard-fail at 1550-1600 |
| ~~Backtracking / Subset-Enum~~ | **2/2** ✅ | 0 | **OWNED 2026-06-11** (#05) — moved to owned table above |
| DP » Linear | 0/2 | **2** | 28,36 soft-fail at 1550-1600 |
| DP » Grid | 1/2 (31) | **1** | |
| DP » LIS-variant | 1/2 (34) | **1** | |
| DP » String | 0/2 | **2** | band-present, untouched |
| DP » Interval/Minimax | 1/2 (13) | **1** | now in-band (was cross-band) |
| **Monotonic Stack ★** | 1/2 (22) | **1** | reachable via carried #9 max-chunks or in-band |
| ~~Union-Find / DSU ★~~ | **2/2** ✅ | 0 | **OWNED 2026-06-10** (#01) — moved to owned table above |
| **Tree-DP ★** | 0/2 | **2** | well-supplied here (~20); completely open |

### ⊘ DEFERRED (tracked, NON-gating for this band → roll to next band / outlier)
- **Topological Sort** — too thin (~2). Train next band. _(mirror this in `topic-install-ledger.md`)_
- **Dijkstra / Shortest Path** — too thin (~1). Train next band. _(ledger)_
- **Trie ★-adjacent** — acquire cross-band.
- **Segment Tree / BIT** — outlier-class, skip.
- **Design** — deferred ([[lc-defer-design-problems-reflex-track]]).

> **DP tracked by sub-pattern, never as one bucket** ([[lc-dp-by-subpattern]]). Deep sub-patterns (Knapsack, LCS,
> Edit-Distance, Bitmask, Digit, Probability, State-Machine) remain absent/scarce here and roll to higher bands.

---

## The band's two jobs (the whole finish line)

With the deferrals out, **1600-1699 has zero new ownership targets.** It is exactly:
1. **Close carried debts** (all well-supplied here): Hashing, Two-Pointers, Binary-Search, Heap, Bit, Stack, Backtracking, DP-Linear/Grid/LIS/String/Interval.
2. **Own the blind-spot trio** — ✅ **Union-Find OWNED 2/2** (#01, 2026-06-10); Tree-DP (2 to go), Mono-Stack (1 to go).

**Headline process metric (carried in place of the prove-the-streak gate we skipped):** Step-2 (recompute worked example) + Step-3 (named edge cases) on *every* solve, and track **first-submission-clean rate** (rule 6C bar = ≥70%, ≤1 hinted/10). The 1550-1600 leak was ~65% clean / ~1.25 hinted-per-10 — carelessness, not algorithm. This band's real job is to close that.

---

## Seed inventory — prior 1600-1700 work (PENDING our-code re-audit)

> 17 problems already logged across the two old folders. Results below are from prior headers; **buckets are
> NOT yet credited** — each must be re-read and classified by the mechanic in OUR code ([[lc-classify-by-own-solution]])
> before it counts toward any bucket above. Re-audit is a follow-up pass.

**`1600-1650/` (7 logged — per CLAUDE.md: 2 clean, 3 soft-fail, 2 hinted):**
| # | Problem | Prior result | Bucket |
|---|---|---|---|
| 01 | House Robber V | soft fail | ⏳ re-audit |
| 02 | Count Caesar Cipher Pairs | soft fail | ⏳ re-audit |
| 03 | Split Array with Minimum Difference | **clean** | ⏳ re-audit |
| 04 | Minimum Discards to Balance Inventory | soft fail | ⏳ re-audit |
| 05 | Minimum Cost Path w/ Alternating Directions II | hinted | ⏳ re-audit |
| 06 | Identify the Largest Outlier | hinted | ⏳ re-audit |
| 07 | Sum of Digit Differences of All Pairs | **clean** | ⏳ re-audit |

_(Word Squares II was dropped.)_ Second-Attempt versions exist for all 7 in `1600-1650/Second-Attempt/`.

**`1650-1700/` (10 logged — results pending, revision was due 2026-05-30):**
| # | Problem | Bucket |
|---|---|---|
| 01 | Minimum Operations to Make Array Non-Decreasing | ⏳ re-audit |
| 02 | Minimum Absolute Distance Between Mirror Pairs | ⏳ re-audit |
| 03 | Minimum Operations to Make Binary Palindrome | ⏳ re-audit |
| 04 | Find the Smallest Balanced Index | ⏳ re-audit |
| 05 | Multi-Source Flood Fill | ⏳ re-audit |
| 06 | Find Maximum Balanced XOR Subarray Length | ⏳ re-audit |
| 07 | Number of Unique XOR Triplets I | ⏳ re-audit |
| 08 | Longest Common Prefix Between Adjacent Strings After Removals | ⏳ re-audit |
| 09 | Path Existence Queries in a Graph I | ⏳ re-audit |
| 10 | Closest Equal Element Queries | ⏳ re-audit |

> Physical files stay in the old folders for now; new in-band problems go in `1600-1699/First-Attempt/`.
> Migration/renumber into this folder is optional and can follow the re-audit.

---

## Selection system (to build next)
- `_Sealed-Queue.md` — blind deal-list + spoiler answer key + trickiness tiers (not yet built).
- Reflex deck stays **walled off** ([[feedback-primitive-reflex-file-format]]): it grows freely and **never** adds to the gating list above.
