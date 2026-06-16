# 1700–1800 — Sealed Queue (merged 100-pt band)

> Built 2026-06-16 from full assembled data: 186 problems, AR+LC-tags (`zerotrac-data/band_1700_1799_lctags.tsv`),
> editorials ALL 186 fetched (`editorials-data/band_1700_1799/`, 0 misses), statements cached
> (`zerotrac-data/content-tsv/all_1700_with_content.tsv`). Single disguised pool (no Phase-1/Phase-2 split —
> acquisition is floor-band-only per the 2026-06-03 model change). 6 already-solved excluded (see overview).
> **Revised 2026-06-16:** Tree-DP fully DEFERRED to next band (removed its 2 problems); BS-on-answer hard-feasibility
> flavor added (2 problems). Reshuffled `random.seed(1700)`.
>
> **Targets:** Topological Sort + Shortest-Path/Dijkstra + Trie (new buckets, ≥3-rule cleared only by the 100-pt
> width), Monotonic-Stack ★ (blind-spot 1→2), DP-Interval + DP-LIS (relocated debts, 1→2), BS-on-answer
> hard-feasibility flavor (the #12-mountain gap), + carried 1600-1700 DP debts (Linear/Grid/String). Owned buckets
> appear only as amortized ride-alongs.
>
> **BLIND-DEAL RULE** ([[lc-blind-deal-protocol]]): on "next", hand the next un-ticked link — NO bucket, NO AR.
> Do NOT open the ANSWER KEY before solving (SPOILER). Tick after the cold re-solve.
> **⚠ RULE-8 GATE:** BUILT but **must NOT open until 1600-1700 graduates.** **⚠ PREREQ:** install the missing
> primitives first (Dijkstra, Topo/Kahn, Trie, Interval-DP, DSU kernel) Socratically on CANONICAL problems — NOT on
> these band problems — or you hit the #01 template-rust trap (38/46 min lost). See overview.
> Protocol: 30-min cap (derivation clause — self-derived over-cap AC still counts; first sub must be AC), then cold re-solve.
> **Process metrics (carried in):** over-model BAN on open buckets; mapping/impl TIME-SPLIT per solve; deck-harvest on fat-mapping solves.

---

## DEAL LIST (blind — links only). Shuffle = `random.seed(1700)`. Position is NOT a tell.

1. [ ] https://leetcode.com/problems/online-stock-span/
2. [ ] https://leetcode.com/problems/minimum-xor-path-in-a-grid/
3. [ ] https://leetcode.com/problems/solving-questions-with-brainpower/
4. [ ] https://leetcode.com/problems/cheapest-flights-within-k-stops/
5. [ ] https://leetcode.com/problems/maximum-subarray-sum-with-one-deletion/
6. [ ] https://leetcode.com/problems/valid-palindrome-iii/
7. [ ] https://leetcode.com/problems/loud-and-rich/
8. [ ] https://leetcode.com/problems/extra-characters-in-a-string/
9. [ ] https://leetcode.com/problems/find-minimum-time-to-reach-last-room-i/
10. [ ] https://leetcode.com/problems/count-substrings-that-differ-by-one-character/
11. [ ] https://leetcode.com/problems/minimum-insertion-steps-to-make-a-string-palindrome/
12. [ ] https://leetcode.com/problems/find-longest-special-substring-that-occurs-thrice-ii/
13. [ ] https://leetcode.com/problems/sum-of-prefix-scores-of-strings/
14. [ ] https://leetcode.com/problems/minimum-time-to-visit-disappearing-nodes/
15. [ ] https://leetcode.com/problems/parallel-courses/
16. [ ] https://leetcode.com/problems/max-chunks-to-make-sorted-ii/
17. [ ] https://leetcode.com/problems/maximize-score-of-numbers-in-ranges/
18. [ ] https://leetcode.com/problems/longest-arithmetic-subsequence/
19. [ ] https://leetcode.com/problems/minimum-deletions-to-make-string-balanced/
20. [ ] https://leetcode.com/problems/all-ancestors-of-a-node-in-a-directed-acyclic-graph/
21. [ ] https://leetcode.com/problems/sorting-three-groups/

---

<details>
<summary>⚠️ SPOILER — ANSWER KEY (do not open before solving)</summary>

### Per-problem buckets (editorial-verified, by deal #)

| # | Bucket (credit by OUR code) | Slug | Role / note |
|---|---|---|---|
| 1 | Monotonic-Stack ★ | online-stock-span | mono-stack backup (Design-tagged; mechanic = mono-stack-as-you-go) |
| 2 | DP » Grid | minimum-xor-path-in-a-grid | carried 1600-1700 DP-Grid debt |
| 3 | DP » Linear | solving-questions-with-brainpower | carried DP-Linear (skip/take) |
| 4 | Shortest Path | cheapest-flights-within-k-stops | Dijkstra/SP backup — Bellman-Ford / DP-on-edges |
| 5 | DP » Linear | maximum-subarray-sum-with-one-deletion | carried DP-Linear (Kadane-with-state) |
| 6 | **DP » Interval** | valid-palindrome-iii | own #2 — interval/LPS |
| 7 | **Topological Sort** | loud-and-rich | own #2 |
| 8 | **Trie** | extra-characters-in-a-string | acquire #2 — trie + DP |
| 9 | **Shortest Path** | find-minimum-time-to-reach-last-room-i | own #1 — Dijkstra on grid |
| 10 | DP » String | count-substrings-that-differ-by-one-character | carried DP-String |
| 11 | **DP » Interval** | minimum-insertion-steps-to-make-a-string-palindrome | own #1→2 — classic `dp[i][j]` LPS |
| 12 | **BS-on-answer** (hard-feasibility) | find-longest-special-substring-that-occurs-thrice-ii | #12-mountain gap rep #2 — feasibility is the work |
| 13 | **Trie** | sum-of-prefix-scores-of-strings | acquire #1 — classic prefix trie |
| 14 | **Shortest Path** | minimum-time-to-visit-disappearing-nodes | own #2 — Dijkstra |
| 15 | **Topological Sort** | parallel-courses | own #1 — Kahn's / cycle-detect |
| 16 | **Monotonic-Stack ★** | max-chunks-to-make-sorted-ii | blind-spot own #2 — **the carried ref owed from 1600-1700 #9** |
| 17 | **BS-on-answer** (hard-feasibility) | maximize-score-of-numbers-in-ranges | #12-mountain gap rep #1 — non-trivial check() |
| 18 | **DP » LIS** | longest-arithmetic-subsequence | own #1→2 — LIS-variant (map-keyed) |
| 19 | DP » String | minimum-deletions-to-make-string-balanced | carried DP-String |
| 20 | **Topological Sort** | all-ancestors-of-a-node-in-a-directed-acyclic-graph | Topo 3rd/backup |
| 21 | **DP » LIS** | sorting-three-groups | own #2 — min changes = n − LIS |

### Bucket coverage (21 problems)
- **New buckets:** Topo (3: parallel-courses, loud-and-rich, all-ancestors) · Dijkstra/SP (3: reach-last-room, disappearing-nodes, cheapest-flights) · Trie (2)
- **Blind-spot:** Monotonic-Stack ★ (2: max-chunks-ii, online-stock-span) → close 1→2/2
- **Relocated DP:** Interval (2), LIS (2) → close 1→2/2 each
- **BS-on-answer hard-feasibility flavor** (2) — NOT plain-BS reps (BS owned 2/2, one bucket); these solidify the
  non-trivial-`check()` flavor that hard-failed at 1600-1700 #12 (mountain inverse-triangular). Non-gating but targeted.
- **Carried 1600-1700 DP debts:** String (2), Linear (2), Grid (1)

### DEFERRED / outlier (logged in ledger)
- **Tree-DP ★ — FULLY DEFERRED to next band (2026-06-16, user decision).** Strict bar: only `longest-zigzag-path`
  qualified (1 rep), not enough to own; relocate BOTH reps to a band with House-Robber-on-tree / tree-knapsack
  supply (~1800+). `longest-zigzag` + `tree-diameter` removed from this queue.
- **Bitmask DP** (2 in band) — below ≥3 advanced-rule → DEFER.
- **Monotonic Queue** (3) — advanced, install optional/ungated.
- **Segment Tree / BIT** (2) — outlier, skip. **Design** (7) — excluded every band.

### Trickiness
Lean on editorial difficulty, not AR ([[lc-difficulty-by-editorial]]). Dijkstra/Topo = standard application (clean
reps once template installed); DP-Interval/LIS + BS-hard-feasibility = derivation (the recurrence / the `check()` is the work).

</details>
