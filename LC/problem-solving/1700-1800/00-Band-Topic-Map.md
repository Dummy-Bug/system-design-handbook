# 1700–1800 — Band Topic Map (SPOILER)

> Built 2026-06-16. **Merged 100-pt band** (1700–1799), per user request — consolidates the old `1700-1750.md`
> (6 solved) + `1750-1800.md` (empty) stubs AND gives the thin relocated patterns enough supply to be owned.
> 186 problems; AR+tags + ALL 186 editorials assembled. **Status: BUILT, not yet OPEN** (rule 8 — 1600-1700
> must graduate first). This is the user's hardest band (above the current ~1530 contest ceiling).

## Why merged (the supply argument)
A 50-pt split would have re-deferred the relocation backlog. Merged band supply (editorial-verified):
- **Topological Sort = 4**, **Shortest Path/Dijkstra = 3** → clear the ≥3 advanced-rule **only because of the 100-pt width**.
- **Tree (14) + DFS (20)** → looked promising for tree-DP, but editorial phantom-check found only 1 *strict* tree-DP → **Tree-DP DEFERRED to next band** (see below). The merge still pays off via Topo/Dijkstra/Interval-DP/LIS.

## Buckets in this band (by editorial-verified mechanic)

| Bucket | In-band supply | Role this band |
|---|---|---|
| ~~Tree-DP ★~~ **DEFERRED** | 1 strict only | **FULLY DEFERRED to next band (2026-06-16, user decision)** — 1 strict rep (`longest-zigzag`) can't own a 2-rep bucket; both reps relocate to ~1800+ (House-Robber-on-tree / tree-knapsack). Removed from queue. |
| **Monotonic-Stack ★** | 2 | **blind-spot — own 1 more (1/2 → 2/2).** `max-chunks-ii` = the carried ref from 1600-1700 #9 |
| **BS-on-answer** (hard-feasibility flavor) | 2 disguised | **NOT plain-BS reps** (BS owned 2/2, one bucket) — solidify the non-trivial-`check()` flavor that hard-failed at 1600-1700 #12. Targeted, non-gating. |
| **Topological Sort** | 4 | **NEW bucket — own 2** (relocated from 1600-1699) |
| **Shortest Path / Dijkstra** | 3 | **NEW bucket — own 2** (relocated from 1600-1699) |
| **DP » Interval** | 2 (insertion-palindrome, valid-palindrome-iii) | **own 1 more (1/2 → 2/2)** — first genuine `dp[i][j]` supply ≥1550 |
| **DP » LIS** | 2 (longest-arith-subseq, sorting-three-groups) | **own 1 more (1/2 → 2/2)** |
| **Trie** | 3 | **acquire** (no clean-gate pressure per ledger) |
| DP » String | several | carried 1600-1700 debt (own 2) — insurance if it rolls |
| DP » Linear | many | carried 1600-1700 debt (own 2) — insurance |
| DP » Grid | several | carried 1600-1700 debt (own 1) — insurance |
| Two-Pointers (12) / Stack (6) | plenty | carried debts — **should close in 1600-1700 first** (rule 8); not farmed here |
| Greedy / Math / Graph / Prefix-Sum / Sliding-Window / Hashing / BS / Bit / Backtracking / Heap / Union-Find | abundant | **OWNED carry-in** — amortized ride-alongs only, never the target |

## Deferred / outlier (logged in `topic-install-ledger.md`)
- **Bitmask DP** — 2 in band (< ≥3 advanced-rule) → DEFER.
- **Monotonic Queue** — 3; advanced, install optional/ungated.
- **Segment Tree / BIT** — 2, outlier-class, skip.
- **Design** — 7, excluded at every band.

## ✅ TREE-DP — FULLY DEFERRED to next band (2026-06-16, user decision)
Phantom-check of all 13 tree-tagged editorials: **strict optimization tree-DP = 1** (`longest-zigzag-path` only;
`tree-diameter` = path-DP cousin; rest aggregation/construction). One strict rep can't own a 2-rep bucket, so
rather than bank a lone rep here, **both Tree-DP reps relocate to the next band** with House-Robber-on-tree /
tree-knapsack / tree-max-path supply (~1800+). `longest-zigzag` + `tree-diameter` **removed from this queue.**
Tree-DP stays a rule-6B blind-spot owed cross-band. Logged in `topic-install-ledger.md §1/§2`.

## Ownership tracker (rule 6A — owned = 2 clean self-derived first-submission ACs on distinct problems)

> Deal numbers per the reshuffled queue (`random.seed(1700)`, Tree-DP removed + BS-on-answer added 2026-06-16).

| Bucket | Clean reps | Need | Queue picks (deal #) |
|---|---|---|---|
| Monotonic-Stack ★ | 1/2 (carried) | 1 | #16 max-chunks-ii, #1 online-stock-span (backup) |
| Topological Sort | 0/2 | 2 | #15 parallel-courses, #7 loud-and-rich, #20 all-ancestors (3rd) |
| Shortest Path / Dijkstra | 0/2 | 2 | #9 reach-last-room, #14 disappearing-nodes, #4 cheapest-flights (backup) |
| DP » Interval | 1/2 (carried, Stone Game) | 1 | #11 insertion-palindrome, #6 valid-palindrome-iii |
| DP » LIS | 1/2 (carried, #34 1550-1600) | 1 | #18 longest-arith-subseq, #21 sorting-three-groups |
| Trie | 0 (acquire) | acq | #13 sum-of-prefix-scores, #8 extra-characters |
| BS-on-answer (hard-feasibility) | owned bucket; flavor shaky | non-gating | #17 maximize-score-of-numbers-in-ranges, #12 find-longest-special-substring-thrice-ii |
| DP » String | 0/2 (carried) | 2 | #10 count-substrings-differ-by-one, #19 min-deletions-balanced |
| DP » Linear | 0/2 (carried) | 2 | #5 max-subarray-one-deletion, #3 solving-questions-brainpower |
| DP » Grid | 0/2 (carried; was 1/2 at 1600) | 1+ | #2 minimum-xor-path-in-a-grid |
| ~~Tree-DP ★~~ | — | — | **DEFERRED to next band** (removed from queue) |

## Graduation (rule 6)
All core buckets above → ● (2 clean self-derived ACs). Blind-spots Tree-DP + Mono-Stack must reach 2 cross-band.
Quality bar ≥70% first-sub clean, ≤1 hinted/10. Realistic band total ≈ 18–24 solves. **Process focus carried from
1600-1700:** over-model ban on open buckets, mapping/impl time-split per solve, deck-harvest on fat-mapping solves
([[lc-index-bookkeeping-overmodel]], [[lc-derivation-budget-chunking]]).

## Data locations
- Tags+AR: `zerotrac-data/band_1700_1799_lctags.tsv` (186) · Editorials: `editorials-data/band_1700_1799/` (186, 0 miss)
- Statements: `zerotrac-data/content-tsv/all_1700_with_content.tsv` · Summary: `editorials-data/band_1700_1799_summary.tsv`
