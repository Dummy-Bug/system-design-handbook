# Phase 1 — Acquisition (1550-1600)

**RE-AUDITED 2026-05-28 at LearnYard subtopic granularity** (same pipeline as 1500-1549: doocs editorials + LearnYard subgroups + editorial-correctness check). Supersedes the earlier broad-tag re-base.

**Install floor is 1500-1549.** Nearly every foundational pattern is acquired there. At 1550-1599 a topic is a Group A acquisition only if it is a **genuinely new subtopic** (per the rule: a new *subtopic* is Phase-1 even if its parent main-topic was already installed) AND its **doocs editorial solution actually uses that pattern** (tags alone are insufficient — this caught two phantoms at 1500-1549).

Provenance:
- 83 band problems, **28 excluded as already-solved** (`1550-1600/First-Attempt/` + 3 filename↔slug aliases), 59 unsolved classified.
- Supply: `editorials-data/band_1550_1599_subgroup_supply.tsv` · per-problem: `..._subgroups.tsv` · editorials: `editorials-data/band_1550_1599/` (83/83 fetched).

---

## Already installed-via-solve at this band (the old Group A — DONE)

The earlier broad-tag plan listed Game Theory + Interval DP as Group A. Both were **cleanly solved** and are now installed — no re-acquisition.

| Subtopic | Installed via | Outcome |
|----------|---------------|---------|
| Game Theory / Level I | Alice and Bob Playing Flower Game (#23) | ✅ clean (47 min) |
| Matrix Chain / Interval DP | Stone Game (#13) | ✅ clean (self-derived) |
| Stack / Monotonic Stack (cross-band rep) | Next Greater Node in Linked List (#22) | ✅ clean (1st blind-spot clean) |

---

## Group A — Acquire here (genuinely-new subtopics, editorial-verified)

Deal blind. Must be clean first-submission AC to count.

| # | LearnYard subgroup | Why new here | Genuine supply | Problem | AR | QPos | Link |
|---|--------------------|--------------|---------------:|---------|-----|------|------|
| 1 | **DP Level 1 / DP On Grid** | Linear DP installed @1500; grid-DP is a distinct mechanic, first real supply here | 2 | Minimum Falling Path Sum | 60.8% | Q2 | https://leetcode.com/problems/minimum-falling-path-sum/ |
| 2 | **DP Level 1 / DP on String** | distinct DP mechanic (chain/edit-style); uninstalled at 1500 | 1 genuine | Longest String Chain | 63.0% | Q2 | https://leetcode.com/problems/longest-string-chain/ |

> [!note] Editorial-verified
> - Minimum Falling Path Sum: doocs tags Array/**DP**/Matrix, textbook grid DP. ✅
> - Longest String Chain: doocs tags include **DP** + Sorting; canonical solution is sort-by-length + dp. ✅ (the Two-Pointers tag is just the word-compare helper)

---

## Candidates checked and REJECTED (editorial-correctness)

| Subgroup | Candidate | Why rejected |
|----------|-----------|--------------|
| Stack / Implementary (plain stack) | Score of Parentheses | doocs editorial leads with **Counting** (depth), not stack → phantom risk; plain stack is near-trivial/foundational and surfaces in Phase 2 anyway |
| Recursion & Backtracking | Iterator for Combination | **Design-tagged** → excluded by rule. The only other (k-th Happy Strings) is already solved (soft-fail). **No clean unsolved genuine-backtracking acquisition at 1550** → defer clean install. |
| DP on Trees (deferred phantom) | — | **0 reps at 1550-1599** (confirmed absent again). Still homeless; defer to first band with genuine DP-on-tree editorials. |
| Graphs / Disjoint Set Union | Earliest Moment Friends (1 genuine) | only 1 here → defer to **1600-1649** (7 reps). |
| Two Pointer on Strings (5) | — | trivial variant of installed Two-Pointer-Arrays — same mechanic; Phase 2, not a fresh acquisition. |
| Advance algorithm / Segment Tree (1), String Matching (1) | — | outliers / mirage (incidental tags). |

---

## Group B — installed at 1500-1549 → Phase 2 derivation reps here

All these have their mechanic from the floor; their 1550-1599 problems are disguised reps for ownership:
Hashing (16) · Greedy/Part I (14) · Linear DP (8) · Two-Pointer Arrays (8) · Sliding Window (5) · Prefix Sum (5) · Binary Search Upper/Lower (3) · Bit/XOR (3) · Monotonic Stack (Phase-2 reps incl. Max Chunks) · Trie (1) · Heap (1) · Math/NT.

Excluded as scaffolding (not targets): Sorting (10), Matrix (5), Stack/Implementary, Stack-with-String, Two-Pointer-Strings, Design.

---

## Tracker (Group A)

| # | LearnYard subgroup | Phase 1 | Status |
|---|--------------------|---------|--------|
| 1 | DP Level 1 / DP On Grid | ☐ | — |
| 2 | DP Level 1 / DP on String | ☐ | — |

---

## Deferred FROM this band

| Subtopic | In-band genuine supply | Defer to |
|----------|-----------------------:|----------|
| DP on Trees | 0 | first band with genuine DP-on-tree editorials |
| Recursion & Backtracking (clean install) | 0 unsolved genuine (Design-excluded / solved) | first band with a genuine unsolved backtracking editorial |
| Union-Find / DSU | 1 genuine | 1600-1649 (7 reps) |

---

## Data provenance

- Supply: `editorials-data/band_1550_1599_subgroup_supply.tsv`
- Per-problem: `editorials-data/band_1550_1599_subgroups.tsv`
- Editorials: `editorials-data/band_1550_1599/*.md` (83/83)
- LC tags + AR: `zerotrac-data/band_1550_1599_lctags.tsv`
- Classifier: `scripts/classify_band_to_learnyard.py` (with already-solved exclusion + filename↔slug aliases)
