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
| Hashing / Counting | ~52 | ● **OWNED 2/2** (seed re-audit 2026-06-15: Mirror-Pairs + Sum-Digit-Diff) |
| Sorting | ~40 | substrate (rarely the credited mechanic) |
| Greedy | ~32 | ● OWNED (carryover) |
| Math / NT / Combinatorics | ~32 | ● OWNED (carryover) — folds in Game-Theory/parity & most Invariant/Reframe |
| Graph (BFS/DFS/traversal) | ~35 | ● OWNED (carryover) |
| Matrix | ~22 | grid-traversal substrate |
| Binary Search | ~18 | ● **OWNED 2/2** (#13, #14, 2026-06-15) — plain-BS debt from 1500-1550 **closed** |
| Prefix Sum | ~17 | ● OWNED (carryover) |
| Heap | ~16 | ● **OWNED 2/2** (#06 reward-top-k 2026-06-11 soft + #20 max-product-after-k-increments 2026-06-16 clean, heap load-bearing) |
| Bit Manipulation | ~13 | ● **OWNED 2/2** (2026-06-15: Unique-XOR-Triplets-I + #16 beautiful-subarrays XOR reframe) |
| **Tree / Binary Tree** | ~20 | ⊘ **tree-DP DEFERRED 2026-06-12** — the ~20 are traversal/BFS-level/construction; **0 force a true optimization recurrence** (audited from band tags). Roll to a band with House-Robber-on-tree / tree-knapsack supply. See ledger §2. |
| **Union-Find** | ~11 | ★ ✅ **OWNED 2/2** (#01, 2026-06-10) — blind-spot closed |
| Two Pointers | ~11 | ◐ carried 0/2 |
| DP » Linear | ~10 | ◐ carried 0/2 |
| Sliding Window | ~8 | ● OWNED (carryover) |
| Backtracking | ~5 | ◐ carried 1/2 |
| Stack (plain) | ~5 | ◐ carried 0/2 |
| DP » String | ~4 | ◐ carried 0/2 |
| DP » Grid | ~2 | ● **OWNED 2/2** (#22 max-moves-in-grid, 2026-06-22 — contamination overturned, immaterial leak) |
| DP » Interval | ~0 genuine | ⊘ **DEFERRED 2026-06-15** — tag+editorial audit: 0 interval-DP in-band (Cutting-Cake-I is greedy). Carried 1/2 (#13 Stone Game) rolls cross-band. |
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
| **Union-Find / DSU ★** | 1550-1600 #37 + **1600-1699 #01 satisfiability-of-equality-equations (2026-06-10, clean)** — blind-spot CLOSED · _reinforced #08 minimize-maximum-component-cost (2026-06-12, Kruskal MST, clean)_ |
| **Backtracking / Subset-Enum** | 1550-1600 #19 + **1600-1699 #05 find-the-punishment-number (2026-06-11, clean self-derived)** |
| **Binary Search** | 1600-1699 #13 minimum-time-to-complete-trips + #14 minimum-time-to-repair-cars (both 2026-06-15, clean self-derived) — one bucket all flavors [[lc-binary-search-one-bucket]]; closes plain-BS debt from 1500-1550 |
| **Hashing / Counting** | 1550-1600 #33 + seed re-audit 2026-06-15: Mirror-Pairs (1650-1700 #02) + Sum-Digit-Diff (1600-1650) — both clean self-derived first-AC (Closest-Equal #10 a 3rd, surplus) |
| **Bit Manipulation** | seed re-audit Unique-XOR-Triplets-I (1650-1700 #07, bit-width cap) + **1600-1699 #16 beautiful-subarrays (2026-06-15, clean self-derived, XOR-cancellation reframe)** |

### ◐ / ○ TO OWN (carried debt + blind-spots) — **7 gating buckets** (+3 deferred cross-band: Tree-DP, DP-LIS, DP-Interval) _(Union-Find 06-10; Backtracking 06-11; Binary-Search + Hashing + Bit 06-15; DP-LIS + DP-Interval deferred 06-15 by editorial audit)_
| Bucket | Carried count | Owe | Notes |
|---|---|---|---|
| ~~Hashing (canonical/counting)~~ | **2/2** ✅ | 0 | **OWNED 2026-06-15 (seed re-audit).** #33 (1550-1600) + Mirror-Pairs (1650-1700 #02, clean) + Sum-Digit-Diff (1600-1650, clean); Closest-Equal (#10) a surplus 3rd. Moved to owned table. |
| Two Pointers | 0/2 | **2** | 32 soft-fail, 35 soft-hinted, 38 hard-fail at 1550-1600 (none counted). **Both queue picks spent with NO credit:** #03 push-dominoes (over-modeled) + #17 advantage-shuffle (2026-06-15, solved via TreeMap-greedy = Greedy ride-along, not two-pointer). → **needs 2 FRESH sort+two-pointer picks.** |
| ~~Binary Search~~ | **2/2** ✅ | 0 | **OWNED 2026-06-15.** #13 minimum-time-to-complete-trips (CLEAN first-sub self-derived, 18m — feasibility `Σ⌊T/t⌋`) + #14 minimum-time-to-repair-cars (CLEAN first-sub self-derived — feasibility `Σ⌊√(T/r)⌋`, isqrt). **Closes the plain-BS debt carried from 1500-1550.** (#12 mountain-height BS route 2026-06-15 was HARD FAIL/editorial — NOT counted.) |
| ~~Heap~~ | **2/2** ✅ | 0 | **OWNED 2026-06-16.** #06 reward-top-k-students (2026-06-11, clean, soft rep — heap not load-bearing) + #20 max-product-after-k-increments (2026-06-16, CLEAN first-sub self-derived 15m, **heap load-bearing** — k× grab-min loop). #12 mountain-height (soft fail 2×WA — NOT counted). |
| ~~Bit Manipulation~~ | **2/2** ✅ | 0 | **OWNED 2026-06-15.** Unique-XOR-Triplets-I (seed #07, bit-width cap §4.3) + #16 beautiful-subarrays (clean self-derived, XOR-cancellation → subarray-XOR-0 reframe). Moved to owned table. |
| Stack (plain) | 0/2 | **2** | 30 hard-fail at 1550-1600. **Both queue Stack deals are spent with NO rep:** #11 min-swaps-balanced (editorial hard-fail) + #16 minimum-remove (2026-06-15 RE-SOLVE — LC 1249 pre-solved 2026-06-03 in stack-reflex track). → **needs 2 FRESH non-queue Stack picks.** |
| ~~Backtracking / Subset-Enum~~ | **2/2** ✅ | 0 | **OWNED 2026-06-11** (#05) — moved to owned table above |
| DP » Linear | 1/2 | **1** | #23 knight-dialer (2026-06-23) clean rep 1; 28,36 soft-fail at 1550-1600 |
| ~~DP » Grid~~ | **2/2** ✅ | 0 | **OWNED 2026-06-22** (#22 max-moves-in-grid) — contamination overturned (immaterial leak) |
| ~~DP » LIS-variant~~ | 1/2 (34) | **DEFERRED** | **DEFERRED 2026-06-15 (supply-justified).** Tag+editorial audit of both halves: **genuine LIS = 0 in-band** (phrase-hits 1121 = greedy-count, 2943 = sort-scan, neither LIS-DP). Carried 1/2 (#34) rolls cross-band. |
| DP » String | 0/2 | **2** | #04 partition-≤k (Greedy ride-along, no rep) + #22 flip-string-to-monotone (2026-06-16, AC but **editorial-level help — NO REP**). Both queue picks spent without credit → needs 2 FRESH non-queue picks. |
| ~~DP » Interval/Minimax~~ | 1/2 (13) | **DEFERRED** | **DEFERRED 2026-06-15 (supply-justified).** Tag+editorial audit: **0 interval-DP in-band** (no `dp[i][j]`/Game-Theory tag; Cutting-Cake-I is greedy). Carried 1/2 (#13 Stone Game) rolls cross-band. Corrects the prior "now in-band" mislabel. |
| **Monotonic Stack ★** | 1/2 (22) | **1** | #19 max-width-ramp (2026-06-15) was the queue's mono-stack pick but **solved via sort, not stack → NOT credited**, stays 1/2. **Reflex-gap fixed:** installed mono atom covered only NEAREST; new **Stack Atom 09** (farthest/widest) created (Socratically led = acquisition, no rep). **Rep 2 owed cold on carried #9 max-chunks** where Atom 09 must fire unaided. |
| ~~Union-Find / DSU ★~~ | **2/2** ✅ | 0 | **OWNED 2026-06-10** (#01) — moved to owned table above |
| ~~**Tree-DP ★**~~ | 0/2 | **DEFERRED** | **DEFERRED 2026-06-12 (supply-justified).** Re-audited band tree tags: ~20 tree problems are traversal/aggregation/construction; **0 force an optimization recurrence**. The 3 queued "tree-DP" were 1 sum-fold (max-product-splitted, done → re-classed Subtree-Aggregation) + 2 tree-DP-*lite*. True tree-DP supply ≈ 0 below ~1700 → own it in a higher band (rule 6B "cross-band" satisfied by relocation, not skip). |

### ⊘ DEFERRED (tracked, NON-gating for this band → roll to next band / outlier)
- **Tree-DP ★** — **DEFERRED 2026-06-12 (supply-justified).** Despite ~20 tree problems, **0 force a true optimization recurrence** — all traversal/aggregation/construction. A blind-spot can't be *owned* where no problem requires it. Relocate to a band with House-Robber-on-tree / tree-knapsack / tree-max-path supply. Rule 6B (blind-spots owned *cross-band*) is satisfied by relocation, not skip. _(mirror in `topic-install-ledger.md` §2)_
- **DP-LIS-variant** — **DEFERRED 2026-06-15 (supply-justified, tag+EDITORIAL audit).** Genuine LIS-DP = 0 in-band: the only "increasing subsequence" editorial hits (1121, 2943) resolve to greedy-counting and sort+linear-scan respectively, not the `dp[i]=max(dp[j]+1)` / patience mechanic. Carried 1/2 (#34) rolls to a band that supplies a real LIS. _(ledger §5 / line 49)_
- **DP-Interval/Minimax** — **DEFERRED 2026-06-15 (supply-justified, tag+EDITORIAL audit).** 0 interval-DP in-band — no `dp[i][j]`/`dp[l][r]` in any editorial, no Game-Theory tag, and Minimum-Cost-for-Cutting-Cake-I is greedy (not the range-DP cut problem). Carried 1/2 (#13 Stone Game) rolls cross-band; `defer.md` holds the Stone-Game family as reserve. Supersedes the earlier "now in-band" note. _(ledger §5 / line 50)_
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
1. **Close carried debts.** ✅ Closed: Hashing, Binary-Search, Backtracking, Union-Find, Bit, **Heap (#20, 2026-06-16)**, **DP-Grid (#22, 2026-06-22)**. **Still owed (5 gating buckets, 9 reps):** Two-Pointers (2), Stack (2), DP-Linear (2), DP-String (2), Mono-Stack (1). **↻ Queue REPLENISHED 2026-06-23 with 7 mechanic-matched picks (deals #24–30)** covering 7 of these 9: Two-Ptr×2, DP-Linear×2, DP-String×1, Stack×1, Mono-Stack×1. **2 reps have no clean in-band supply → roll cross-band (rule 6B):** Stack 2nd, DP-String 2nd. **Deferred cross-band (supply <2, non-gating):** DP-LIS, DP-Interval, Tree-DP — editorial-confirmed 2026-06-15.
2. **Own the blind-spot trio** — ✅ **Union-Find OWNED 2/2** (#01, 2026-06-10); **Tree-DP DEFERRED 2026-06-12** (no in-band problem forces a true optimization recurrence — own it cross-band where supply exists); **Mono-Stack (1 to go)** is the only blind-spot left to own in-band.

**Headline process metric (carried in place of the prove-the-streak gate we skipped):** Step-2 (recompute worked example) + Step-3 (named edge cases) on *every* solve, and track **first-submission-clean rate** (rule 6C bar = ≥70%, ≤1 hinted/10). The 1550-1600 leak was ~65% clean / ~1.25 hinted-per-10 — carelessness, not algorithm. This band's real job is to close that.

> **⚠ QUALITY-GATE STATUS 2026-06-16:** clean-rate **14/20 = 70%** (exactly on the floor — #22 flip-string editorial, no longer above) but **hinted-rate FAILING: 3 hinted (#02, #15, #18) in 18 ≈ 1.7/10 > the ≤1/10 bar** (rule 6C → blocks graduation until pulled under 1/10). **+ OVER-MODEL recurring (4×):** push-dominoes / advantage-shuffle / max-width-ramp each dodged their target mechanic (two-ptr / two-ptr / mono-stack) via a comfort hashmap [[lc-index-bookkeeping-overmodel]] → those buckets aren't getting trained even on clean ACs. Both fixes are behavioral, not coverage. Track going forward.

---

## Seed inventory — prior 1600-1700 work (✅ RE-AUDITED 2026-06-15)

> 17 First-Attempt problems across the two old folders, re-classified by mechanic-in-insight
> ([[lc-classify-by-own-solution]] — **First-Attempt code predates the per-attempt archive**, so classified from the
> logged insight/remark, which the hierarchy allows when code is absent). **Only clean self-derived first-submission
> ACs count** (rule 6A); WA-then-AC / hinted give no rep. **Credits already applied to the trackers above.**

**`1600-1650/` First-Attempt (7 files):**
| Problem | Verdict | Bucket | Credit |
|---|---|---|---|
| Word Squares II | soft fail (WA on sorting) | brute-force enum | — |
| Split Array with Minimum Difference | **soft fail** (WA edge-case debugs) — _seed table wrongly said "clean"; corrected_ | prefix-sum + validation | — |
| House Robber V | soft fail (overflow bug) | DP-Linear | — |
| Count Caesar Cipher Pairs | soft fail (ambiguous; no clean assertion → conservative) | Hashing | — |
| Minimum Discards to Balance Inventory | soft fail (WA edge-case debugs) | Sliding Window | — |
| **Sum of Digit Differences of All Pairs** | ✅ **CLEAN** ("no gotchas, self-derived") | **Hashing/Counting** | ✅ **Hashing rep** |
| Identify the Largest Outlier | hinted | Hashing/algebra | — |

> _(Min Cost Path w/ Alt Directions II exists only in `1600-1650/Second-Attempt/`, no First-Attempt file → cannot supply a clean first-AC rep.)_

**`1650-1700/` First-Attempt (10 files):**
| # | Problem | Verdict | Bucket | Credit |
|---|---|---|---|---|
| 01 | Min Operations to Make Array Non-Decreasing | hinted ("when shown 8 achievable") | Greedy *(owned)* | — |
| 02 | **Min Absolute Distance Between Mirror Pairs** | ✅ **CLEAN** ("clean and self-derived") | **Hashing** (reverse→index map) | ✅ **Hashing rep** |
| 03 | Min Operations to Make Binary Palindrome | soft fail (WA on 3521 + syntax help) | Bit/brute | — |
| 04 | Find the Smallest Balanced Index | assisted (syntax help); Prefix-Sum *(owned)* | Prefix-Sum | — |
| 05 | Multi-Source Flood Fill | ✅ clean — but Graph *(owned)* → reinforces only | Graph BFS | — |
| 06 | Find Maximum Balanced XOR Subarray Length | hinted (hint taken @1h43) | Prefix-XOR + 2D-state hash | — |
| 07 | **Number of Unique XOR Triplets I** | ✅ **CLEAN** ("fully self-derived, no hint", 3h — derivation-clause pass) | **Bit Manipulation** (XOR bit-width cap §4.3) | ✅ **Bit rep (0/2→1/2)** |
| 08 | Longest Common Prefix After Removals | soft fail (first submission wrong) | prefix/suffix precompute | — |
| 09 | Path Existence Queries in a Graph I | soft fail (1 WA) | components / UF-adjacent *(UF owned)* | — |
| 10 | Closest Equal Element Queries | ✅ clean — Hashing (surplus, already owned) | Hashing (array-doubling+map) | (surplus) |

**Re-audit yield:** Hashing **1/2 → OWNED 2/2** · Bit **0/2 → 1/2.** Net owed reps **16 → 14**; gating buckets to own **11 → 10**.
**Side-finding:** the old bands' First-Attempt clean-rate was low (≈4 clean / 17 = ~24%, lots of WA-then-AC) — corroborates the "carelessness, not coverage" thesis this band targets.

> Physical files stay in the old folders; new in-band problems go in `1600-1700/First-Attempt/`. Migration/renumber optional.

---

## Selection system (to build next)
- `_Sealed-Queue.md` — blind deal-list + spoiler answer key + trickiness tiers (not yet built).
- Reflex deck stays **walled off** ([[feedback-primitive-reflex-file-format]]): it grows freely and **never** adds to the gating list above.
