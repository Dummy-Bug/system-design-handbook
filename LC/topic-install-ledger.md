# Topic Install Ledger — Single Source of Truth

> **(Re)established 2026-06-10.** This file was referenced across the repo (CLAUDE.md, extendedClaude.md,
> band topic maps) as the SSoT for *which pattern is installed at which band, deferred, or outlier-class* —
> but it had never actually been created. This is it.
>
> Detailed per-problem classification lives in each band's `00-Band-Topic-Map.md`. This ledger holds the
> **cross-band** view: the blind-spot trio, deferrals, outlier-class, and cross-band debt rolls.
> Legend: ● owned (2 clean self-derived first-AC) · ◐ partial · ○ open · ★ blind-spot · ⊘ deferred · ▲ outlier-class.

---

## 1. Blind-spot trio (rule 6B — must each reach 2 clean self-derived ACs, cross-band)

| Pattern | Clean ACs | Status | Source / next |
|---|---|---|---|
| **Monotonic Stack ★** | 1 | ◐ 1/2 | 1550-1600 #22 next-greater-node. (1600-1699 `maximum-width-ramp` was solved via sort = over-model dodge, NOT credited.) 2nd rep queued at **1700-1799 #15 `max-chunks-to-make-sorted-ii`** (the carried ref) + #12 online-stock-span backup. |
| **Union-Find / DSU ★** | 2 | ● **OWNED** | 1550-1600 #37 properties-graph + 1600-1699 #01 satisfiability-of-equality-equations (clean, 2026-06-10). **Blind-spot CLOSED.** |
| **Tree-DP ★** | 0 | ⊘ 0/2 **DEFERRED to next band** | **FULLY DEFERRED 2026-06-16 (user decision).** 1700-1799 phantom-check of 13 tree editorials = only `longest-zigzag-path` strict (1) — can't own a 2-rep bucket with 1, so **both reps relocate to next band** (~1800+, House-Robber-on-tree / tree-knapsack supply). Removed from 1700-1799 queue. (1600-1699 had 0 strict — see §2.) Rule-6B blind-spot still owed cross-band. |

> UF ✅ owned in-band. Mono-Stack ownable in-band (1 to go). **Tree-DP is NOT ownable here** — no in-band problem requires the optimization recurrence, so it relocates (the 100-pt width helped UF, not Tree-DP). Only true-optimization tree-DP on hand = House Robber V (seed inventory) but it's a re-solve → no new ownership rep.

---

## 2. Deferred patterns (tracked roll-forward — NOT skipped, must still be paid)

| Pattern | Deferred at | Reason | Target |
|---|---|---|---|
| **Tree-DP ★** | 1600-1699, **1700-1799** | 1600-99: 0 strict. 1700-99: only 1 strict (`longest-zigzag`), can't own a 2-rep bucket. | **FULLY DEFERRED to next band (2026-06-16, user decision)** — both reps relocate to ~1800+ (House-Robber-on-tree / tree-knapsack / tree-max-path). Removed from 1700-1799 queue. Still rule-6B blind-spot owed cross-band. |
| **Trie** | 1500-1550, 1550-1600, 1600-1699 | thin supply each band (≤4); all sort/prefix-solvable so far | **1700-1799 BUILT — 3 in band (sum-of-prefix-scores, extra-characters, k-divisible); 2 queued as acquire. No clean-gate pressure.** |
| **Topological Sort** | 1600-1699 | only ~2 in band — too thin to own (can't get 2 clean) | ✅ **1700-1799 BUILT 2026-06-16 — 4 in band (parallel-courses, loud-and-rich, all-ancestors-DAG, tree-diameter); editorial-verified; ≥3-rule cleared by the 100-pt merge. Own 2 here.** |
| **Dijkstra / Shortest Path** | 1600-1699 | only ~1 in band | ✅ **1700-1799 BUILT 2026-06-16 — 3 in band (reach-last-room-i, disappearing-nodes [Dijkstra], cheapest-flights [Bellman-Ford]); editorial-verified; ≥3-rule cleared by merge. Own 2 here.** |
| **Design / implement-interface** | ongoing | interview-only, low contest value ([[lc-defer-design-problems-reflex-track]]) | install core once, then defer indefinitely |

---

## 3. Outlier-class (skip unless a problem genuinely forces it)

| Pattern | Note |
|---|---|
| **Segment Tree / BIT** | ▲ outlier-class. ~1 at 1550-1600, ~2 at 1600-1699. Most "range update/query" here is diff-array/prefix-sum solvable. Don't grind; pick up only when truly forced (likely 1900+). |

---

## 4. Cross-band DP-sub-pattern rolls (owe 1 each, no clean in-band candidate found)

| Sub-pattern | Clean | Status | Why rolling |
|---|---|---|---|
| **DP » LIS-variant** | 1 (1550-1600 #34) | ◐ 1/2 → **in-band 1700-1799** | LIS = 0 at ≤1699. ✅ **GENUINE supply FOUND 1700-1799 (2026-06-16): longest-arithmetic-subsequence (LIS-variant) + sorting-three-groups (min-changes = n−LIS). Both queued — own the 2nd rep here.** |
| **DP » Interval / Minimax** | 1 (1550-1600 #13 Stone Game) | ◐ 1/2 → **in-band 1700-1799** | No genuine interval-DP at ≤1699. ✅ **GENUINE `dp[i][j]` supply FOUND 1700-1799 (2026-06-16): minimum-insertion-steps-to-make-string-palindrome + valid-palindrome-iii (both LPS interval-DP, editorial-verified). Queued — own the 2nd rep here.** |

---

## 5. Carried single-rep debts

| Debt | Origin | Now owed in |
|---|---|---|
| ~~Plain **Binary Search / upper-lower-bound**~~ | 1500-1550 (its pick was solved via two-pointer, so BS was never installed) | ✅ **CLOSED 2026-06-15** — Binary-Search is **one bucket regardless of flavor** (on-answer / upper-lower-bound / semi-sorted all share one template); owned 2/2 via #13 + #14 (both on-answer). Plain-BS subsumed, not separately owed. **Policy: never split BS into sub-buckets** (unlike DP) — else 2 reps × N flavors = overkill. |

---

## 6. Per-band install state (summary — detail in each band's topic map)

| Band | State | Owned ● / installed | Open / notes |
|---|---|---|---|
| **1450-1500** | done (early) | see `1450-1500.md` | pre-protocol |
| **1500-1550** | WRAPPED 2026-05-29 (floor, acquisition-only) | Greedy, Flood-Fill, Binary-Tree, Two-Ptr, Bitwise-XOR; +Mono-Stack (cross), +Linear-DP (syntax-assisted) | plain-BS OPEN, Trie DEFERRED |
| **1550-1600** | CALLED 2026-06-10 (not fully graduated; debts rolled fwd) | ● Greedy, Prefix-Sum, Sliding-Window, Graph, Math/NT | all other debts → 1600-1699 |
| **1600-1699** | **ACTIVE** (made active 2026-06-10; 100-pt merged band) | carries 1550-1600's 5 owned | targets: blind-spot trio + carried debts (see `1600-1700/00-Band-Topic-Map.md`) |
| **1700-1799** | **BUILT (sealed, NOT open) 2026-06-16** — merged 100-pt band; supersedes the old 1700-1750/1750-1800 stubs | targets: Tree-DP ★, Mono-Stack ★ (1→2), Topo-Sort + Dijkstra (new), DP-Interval/LIS (1→2), Trie (acq) + carried DP debts | 21-problem sealed queue at `1700-1800/_Sealed-Queue.md`; **rule-8 gated on 1600-1699 graduating first.** 6 old solves excluded. |
| **1800-1850** | paused (5 logged) | see `1800-1850.md` | — |
| **1900-1950** | acquisition notes | see `1900-1950/Phase-1-Acquisition.md` | — |

---

## 7. Owned-bucket master list (don't farm these for ownership reps — amortized ride-alongs only)
**Greedy · Prefix-Sum/Diff-Array · Sliding-Window · Graph-traversal (DFS/BFS) · Math/NT/Combinatorics** (all owned at 1550-1600, carried).
