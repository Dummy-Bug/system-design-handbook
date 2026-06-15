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
| **Monotonic Stack ★** | 1 | ◐ 1/2 | 1550-1600 #22 next-greater-node. 2nd: 1600-1699 `maximum-width-ramp` (queued) or carried 1550-1600 `max-chunks`. |
| **Union-Find / DSU ★** | 2 | ● **OWNED** | 1550-1600 #37 properties-graph + 1600-1699 #01 satisfiability-of-equality-equations (clean, 2026-06-10). **Blind-spot CLOSED.** |
| **Tree-DP ★** | 0 | ⊘ 0/2 **DEFERRED** | **DEFERRED 2026-06-12 (supply-justified) — see §2.** Re-audit of 1600-1699 tree tags: ~20 tree problems, **0 force a true optimization recurrence** (House-Robber-on-tree / tree-knapsack / tree-max-path shape). The 3 once-queued "tree-DP" picks were 1 sum-fold (`max-product-splitted`, solved 2026-06-12 → re-classed **Subtree-Aggregation**, NOT credited) + 2 tree-DP-*lite* (`kth-perfect-subtree`, `collect-apples` — composite-state/conditional-cost folds, plain post-order). Rule 6B requires owning blind-spots *cross-band*; relocation to a higher band with genuine supply satisfies it. |

> UF ✅ owned in-band. Mono-Stack ownable in-band (1 to go). **Tree-DP is NOT ownable here** — no in-band problem requires the optimization recurrence, so it relocates (the 100-pt width helped UF, not Tree-DP). Only true-optimization tree-DP on hand = House Robber V (seed inventory) but it's a re-solve → no new ownership rep.

---

## 2. Deferred patterns (tracked roll-forward — NOT skipped, must still be paid)

| Pattern | Deferred at | Reason | Target |
|---|---|---|---|
| **Tree-DP ★** | 1600-1699 | ~20 tree problems in band but **0 force a true optimization recurrence** (all traversal/aggregation/construction). A blind-spot can't be *owned* where nothing requires it. | band with House-Robber-on-tree / tree-knapsack / tree-max-path supply (likely 1700+). Still a rule-6B blind-spot — owe 2 clean self-derived ACs cross-band. |
| **Trie** | 1500-1550, 1550-1600, 1600-1699 | thin supply each band (≤4); all sort/prefix-solvable so far | acquire cross-band; no clean-gate pressure yet |
| **Topological Sort** | 1600-1699 | only ~2 in band — too thin to own (can't get 2 clean) | next band (1700-1799) |
| **Dijkstra / Shortest Path** | 1600-1699 | only ~1 in band | next band (1700-1799) |
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
| **DP » LIS-variant** | 1 (1550-1600 #34) | ◐ 1/2 — DEFERRED | **LIS = 0** in both 1550-1600 and 1600-1699 bands. **Confirmed 2026-06-15 by tag+EDITORIAL audit** (the only "increasing subsequence" hits, 1121/2943, are greedy-count + sort-scan, not LIS-DP). Roll to first band that supplies a genuine LIS. Topic-map "in-band" note corrected to match. |
| **DP » Interval / Minimax** | 1 (1550-1600 #13 Stone Game) | ◐ 1/2 — DEFERRED | No genuine interval-DP at ≤1699 ("cutting cake I" is greedy). **Confirmed 2026-06-15 by tag+EDITORIAL audit** (0 `dp[i][j]`/`dp[l][r]` in any band editorial, no Game-Theory tag). `defer.md` holds the Stone-Game family as reserve. Topic-map "now in-band" note was an unverified tag-read, now corrected. |

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
| **1700-1750** | paused/backfill | see `1700-1750.md` | need ≥3 more |
| **1750-1800** | backfill | see `1750-1800.md` | full pass owed |
| **1800-1850** | paused (5 logged) | see `1800-1850.md` | — |
| **1900-1950** | acquisition notes | see `1900-1950/Phase-1-Acquisition.md` | — |

---

## 7. Owned-bucket master list (don't farm these for ownership reps — amortized ride-alongs only)
**Greedy · Prefix-Sum/Diff-Array · Sliding-Window · Graph-traversal (DFS/BFS) · Math/NT/Combinatorics** (all owned at 1550-1600, carried).
