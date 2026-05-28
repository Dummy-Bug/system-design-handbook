# Phase 1 — Acquisition (1600-1650)

**RE-AUDITED 2026-05-28 at LearnYard subtopic granularity** (doocs editorials + LearnYard subgroups + editorial-correctness check). Supersedes the earlier broad-tag version.

**Install floor: 1500-1549 + 1550-1599.** A topic is Group A here only if it's a genuinely-new subtopic (new-subtopic rule) AND its doocs editorial solution actually uses the pattern.

Provenance: 87 band problems, **8 excluded as solved** (`First-Attempt/` + `Second-Attempt/`), 79 unsolved classified. Editorials: `editorials-data/band_1600_1649/` (87/87). Supply: `editorials-data/band_1600_1649_subgroup_supply.tsv`.

---

## Group A — Acquire here (editorial-verified)

Deal blind. Must be clean first-submission AC to count.

| # | LearnYard subgroup | Why new here | Genuine supply | Problem | AR | QPos | Link |
|---|--------------------|--------------|---------------:|---------|-----|------|------|
| 1 | **Graphs / Disjoint Set Union** (blind-spot, deferred from 1500/1550) | scarce below (~1-2); **7 reps here** — the real Union-Find install | 7 (≥4 genuine: Network Connected, Satisfiability, Minimize Max Component, Is Graph Bipartite) | Number of Operations to Make Network Connected | 66.6% | Q3 | https://leetcode.com/problems/number-of-operations-to-make-network-connected/ |
| 2 | **Graphs / Multi Source BFS** (new foundational graph subtopic) | distinct from Flood Fill (installed @1500); first appearance | 1 (foundational → install regardless) | Push Dominoes | 63.0% | Q2 | https://leetcode.com/problems/push-dominoes/ |
| 3 | **Recursion & Backtracking** (3-band phantom — install from LearnYard) | **contest pool lacks pure backtracking** (3 bands: every tagged problem solves greedy/DP). Source from LearnYard curated list. | n/a (out-of-band) | Subsets | 79.6% | — | https://leetcode.com/problems/subsets/ |

> [!important] Why Backtracking is sourced from LearnYard, not the band
> Backtracking has been a **phantom across 1500, 1550, AND 1600** — zero editorials in any band use backtracking as the actual solution. Rated weekly/biweekly contest problems systematically favor greedy/DP optimizations over brute-force backtracking, so the zerotrac pool simply doesn't contain pure-backtracking problems. LearnYard's curated **Recursion & Backtracking** list is all classics (Subsets, Permutations, Combination Sum, N-Queens, Letter Combinations, Sudoku) — mostly *unrated*. **Subsets (LC 78)** is the canonical mechanic-installer; follow-up reps from the same list: Combination Sum, Permutations, Letter Combinations of a Phone Number. This resolves the longest-standing blind spot.

> [!note] Editorial verification
> - Union-Find: Number of Operations to Make Network Connected → editorial **Union-Find** ✅ (plus Satisfiability of Equality Equations, Minimize Maximum Component Cost as genuine reps 2-3 in-band)
> - Multi Source BFS: Push Dominoes → editorial **Multi-Source BFS** ✅
> - Backtracking: Subsets → THE canonical subset-generation backtracking template ✅

---

## Candidates checked and REJECTED / DEFERRED

| Subgroup | Status | Reason |
|----------|--------|--------|
| **DP on Trees** (blind-spot) | DEFER (3rd band) | **absent at 1600-1649** — still zero reps across 1500/1550/1600. Homeless. |
| Graphs / Dijkstra | DEFER → 1850-1899 | only 1 rep (Find a Safe Walk), and its editorial is **BFS** not Dijkstra. Real install at 1850 (4 reps). |
| Advance algorithm / Segment Tree | outlier | 1 rep — confirmed outlier across all bands. |
| Stack / Implementary, Two-Pointer-Strings, Sorting, Matrix | scaffolding | not derivation targets. |

---

## Group B — installed at 1500-1549 / 1550-1599 → Phase 2 derivation reps here

Hashing (22) · Greedy/Part I (16) · Binary Search Upper/Lower (10) · Linear DP (10) · Prefix Sum (8) · Bit/XOR (7) · Two-Pointer Arrays (6) · Heap (5) · **DP-on-String (4, installed @1550)** · Binary Tree (4) · Sliding Window (4) · **DP-on-Grid (2, installed @1550)** · Trie (2) · Monotonic Stack (1) · Math/NT. Their 3 cold cleans come from Phase 2.

---

## Tracker (Group A)

| # | LearnYard subgroup | Phase 1 | Status |
|---|--------------------|---------|--------|
| 1 | Graphs / Disjoint Set Union (Union-Find) | ☐ | — |
| 2 | Graphs / Multi Source BFS | ☐ | — |
| 3 | Recursion & Backtracking (LearnYard-sourced) | ☐ | — |

---

## Deferred FROM this band

| Subtopic | Status | Defer to |
|----------|--------|----------|
| DP on Trees | absent 3rd band | first band with genuine DP-on-tree editorials |
| Dijkstra / Shortest Path | 1 rep, editorial is BFS | 1850-1899 (4 reps) |

---

## Data provenance

- Supply: `editorials-data/band_1600_1649_subgroup_supply.tsv`
- Per-problem: `editorials-data/band_1600_1649_subgroups.tsv`
- Editorials: `editorials-data/band_1600_1649/*.md` (87/87)
- LC tags + AR: `zerotrac-data/band_1600_1649_lctags.tsv`
- LearnYard backtracking source: `learnyard-data/recursion-backtracking.tsv`
- Classifier: `scripts/classify_band_to_learnyard.py`
