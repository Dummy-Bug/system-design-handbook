# 1700–1800 Band — Overview

**Built:** 2026-06-16 · **Status:** BUILT, NOT YET OPEN (rule-8 gate — 1600-1700 must graduate first).
**Width:** merged 100-pt (1700–1799), per user request.
**Header integrity (rule 7):** 0 solved in-band so far · 0/0 first-sub clean · 0 hinted · 0 WA-then-AC.

## What this band is for
The **relocation backlog** finally becomes ownable here: Tree-DP ★, Monotonic-Stack ★ (close to 2/2),
Topological Sort + Shortest-Path/Dijkstra (new buckets), DP-Interval + DP-LIS (close to 2/2), Trie (acquire).
Plus carried 1600-1700 DP debts (Linear/Grid/String) as insurance. This is the user's **hardest band** — above the
current ~1530 contest ceiling — so the derivation clause is essential and problems will routinely overshoot 30 min.

## Already-solved — EXCLUDED from the queue (Step 3b, 6 problems)
From the old `1700-1750.md` stub (verified in-band by slug):
1. minimum-removals-to-achieve-target-xor (Q3)
2. pythagorean-distance-nodes-in-a-tree (Q3)
3. minimum-moves-to-balance-circular-array (Q3)
4. count-the-number-of-computer-unlocking-permutations (Q2)
5. distinct-points-reachable-after-substring-removal (Q3)
6. minimum-area-rectangle (Q3 — was a reflex-track solve, but genuinely in-band → excluded)

(`1750-1800.md` had 0 solved. Other slugs in the stubs — split-array-same-average, closest-subsequence-sum,
number-of-islands-ii, etc. — are reflex-track/other-band, not in the 1700-1799 rated list.)

## Process rules carried in from 1600-1700 (the carelessness + mapping fixes)
1. **Over-model BAN on open buckets** — a clean AC that dodged the target mechanic via a comfort hashmap/stack is
   **NOT a rep**; redo with the intended tool. (Killed 4 reps at 1600-1700.) [[lc-index-bookkeeping-overmodel]]
2. **Mapping/impl time-split** logged per solve ("mapped at T1, AC at T2") — makes the Q2-speed bottleneck visible
   and auto-nominates deck cards on fat-mapping solves. [[lc-contest-bottleneck-q2-speed]]
3. **Fire the reframe before reaching for help** — the deck's felt-signal cards (positions-vs-structure, "is it
   positionless?", "cancel matched pairs") used at the 20-min mark, not the hint.
4. Step-2 (worked example) + Step-3 (named edges) on EVERY solve before code.

## Resolved decisions (2026-06-16)
- **Tree-DP FULLY DEFERRED to next band** — only 1 strict tree-DP in band (`longest-zigzag`), can't own a 2-rep
  bucket; both reps relocate to ~1800+ (House-Robber-on-tree / tree-knapsack). Removed from queue.
- **BS-on-answer hard-feasibility flavor ADDED** (2 problems) — not plain-BS reps (BS owned), but solidify the
  non-trivial-`check()` flavor that hard-failed at 1600-1700 #12.
- **Mono-stack supply checked** — exactly 2 in band (max-chunks-ii, online-stock-span), both already queued.

## PREREQ before this band opens (install-first, or you hit the dark)
Install the missing primitives Socratically on CANONICAL problems (NOT band problems): **Dijkstra, Topo/Kahn's,
Trie, Interval-DP** (+ owed **DSU kernel**). DP-Linear/Grid/LIS already have notes (`DP/`). Each install = canonical
trigger + confusion-matrix + skeleton + blank-page drill. Then the band trains disguised mapping on top.

## Files
- `_Sealed-Queue.md` — blind deal list (21) + spoiler answer key
- `00-Band-Topic-Map.md` — classification + ownership tracker
- `First-Attempt/NN-<slug>.md` — one per solved problem (created on solve)
