# SEALED — 1550-1600 Phase 2 Blind Queue + Answer Key

> [!danger] DO NOT OPEN before solving. This file reveals the topic of every queued problem.
> Ask Claude to **deal the next problem**; Claude serves a bare link only and reveals the topic *after* you finish.

> [!info] Queue rebuilt 2026-05-28 (18 problems). Removed: old Q01 Closest Nodes (→ moved to Phase 1 as the binary-search acquisition rep) and 4 duplicates of already-solved band problems (old Q02=band#1 · Q10=band#10 · Q16=band#8 · Q19=band#3). Added 3 LC-tag-verified backfills (Q16–Q18). All 18 are genuine, unsolved derivation problems.

| Q   | status | link                                                                                         | TOPIC (SPOILER)                 |
| --- | ------ | -------------------------------------------------------------------------------------------- | ------------------------------- |
| Q01 | ☐      | https://leetcode.com/problems/coloring-a-border/                                             | Graph / tree traversal          |
| Q02 | ☐      | https://leetcode.com/problems/count-paths-with-the-given-xor-value/                          | Linear / grid / counting DP (+ bit) |
| Q03 | ☐      | https://leetcode.com/problems/find-original-array-from-doubled-array/                        | Hashing / counting (+ greedy)   |
| Q04 | ☐      | https://leetcode.com/problems/count-of-substrings-containing-every-vowel-and-k-consonants-i/ | Sliding window                  |
| Q05 | ☐      | https://leetcode.com/problems/ways-to-split-array-into-good-subarrays/                       | Math / counting (DP) [LC tags: Math, DP] |
| Q06 | ☐      | https://leetcode.com/problems/count-the-number-of-good-nodes/                                | Tree DP [LC tags: Tree, DFS] — the real tree-DP rep |
| Q07 | ☐      | https://leetcode.com/problems/longest-arithmetic-subsequence-of-given-difference/            | Linear / hashing DP             |
| Q08 | ☐      | https://leetcode.com/problems/maximum-points-after-enemy-battles/                            | Greedy / observation            |
| Q09 | ☐      | https://leetcode.com/problems/find-mirror-score-of-a-string/                                 | Stack (per-letter, mirror pairs) [LC tags: Stack, Hash Table] |
| Q10 | ☐      | https://leetcode.com/problems/shortest-distance-after-road-addition-queries-i/               | Graph BFS                       |
| Q11 | ☐      | https://leetcode.com/problems/corporate-flight-bookings/                                     | Difference array / prefix-range |
| Q12 | ☐      | https://leetcode.com/problems/sum-of-numbers-with-units-digit-k/                             | Math / number theory            |
| Q13 | ☐      | https://leetcode.com/problems/maximize-number-of-subsequences-in-a-string/                   | Greedy / prefix                 |
| Q14 | ☐      | https://leetcode.com/problems/score-of-parentheses/                                          | Stack (depth-based — NOT monotonic) [LC tags: Stack] |
| Q15 | ☐      | https://leetcode.com/problems/best-time-to-buy-and-sell-stock-using-strategy/                | Sliding window + prefix sum [LC tags: Sliding Window, Prefix Sum] |
| Q16 | ☐      | https://leetcode.com/problems/k-th-symbol-in-grammar/                                         | Bit operations / XOR — backfill for removed dup [LC tags: Math, Bit Manipulation, Recursion] |
| Q17 | ☐      | https://leetcode.com/problems/maximum-points-you-can-obtain-from-cards/                       | Sliding window — backfill for removed dup [LC tags: Sliding Window, Prefix Sum] |
| Q18 | ☐      | https://leetcode.com/problems/time-based-key-value-store/                                     | Binary search — derivation rep for new BS bucket [LC tags: Binary Search, Design] |

## Tag-verification audit (2026-05-28)

Triggered by Q01 being dealt as "Tree DP" when it's a binary-search problem — and binary search was never a Phase 1 acquisition topic, so it hit cold. Re-checked all 20 against LC's official `topicTags` (public GraphQL, the canonical classification). Re-tags applied above:

| Q | Old label | LC tags | New label |
|---|-----------|---------|-----------|
| Q01 | Tree DP | Array, **Binary Search**, Tree, DFS, BST | Binary search |
| Q20 | Heap-greedy | Array, **Sliding Window, Prefix Sum** | Sliding window + prefix sum |
| Q18 | Monotonic stack | String, **Stack** | Stack (not monotonic) |
| Q12 | Hashing/counting | Hash Table, String, **Stack** | Stack (per-letter) |
| Q07 | Math/number theory | Array, **Math, DP** | Math/counting (DP) — refined, not a mislabel |

All four real mislabels are rated Medium (Q01 1596 · Q20 1556 · Q18 1562 · Q12 1578) — none secretly hard.

### Resolution (2026-05-28)

1. **Phase 1 taxonomy hole — plain binary search → FIXED.** Binary search added as Phase 1 topic #14, with Closest Nodes [1596] as the acquisition rep (the soft-fail solve). Phase 2 BS derivation rep added: Time Based Key-Value Store [981] (now Q18).
2. **4 duplicates → REMOVED from queue.** Old Q02/Q10/Q16/Q19 dropped (already solved). Backfilled the two buckets with in-band supply: Bit/XOR → K-th Symbol in Grammar [779] (Q16); Sliding window → Maximum Points From Cards [1423] (Q17). Diff-array (old Q16) and Game theory (old Q19) have **no clean in-band backfill** — diff-array bucket is already covered by Q11 Corporate Flight + prior band #8; game-theory in-band supply is exhausted (all 3 used: Flower Game P1, Stone Game P1, Final Element band#3).
3. **Heap-greedy → cross-band shortfall (no in-band supply).** Verified via LC tags: the only candidate (Hand of Straights [846]) is Greedy/Sorting, not heap. The Phase-1 heap rep (Min Ops to Halve) soft-failed on Float precision. **Plan:** re-solve Min Ops to Halve cleanly to install the pattern; the 3 derivation cleans complete cross-band (1600-1650+ have real heap problems). Not forced in here.

## Dropped from this band

- **Union-Find** — only ~2 in-band (not enough to own here). It's a mandatory blind-spot pattern (CLAUDE.md rule 6B), so it's installed cross-band in **1600-1650** (4+ problems there), not forced in.
- **Design** — pulled from the derivation queue; not a derivation-muscle target.

## Shortfalls (topics exhausted in-band — cross-band later)

| Topic | In-band deriv reps | Need | Deficit |
|-------|-------------------|------|---------|
| Game theory | 1 (Final Element, band#3) | 2 | 1 — in-band supply exhausted |
| Heap-greedy | 0 (Min Ops to Halve soft-failed; no other in-band heap problem) | 2 | 2 — no in-band supply |
| Monotonic stack | 1 | 2 | 1 |
| Interval DP | 0 | 2 | 2 |

These missing reps come from adjacent bands after this band's in-band supply is exhausted. Do NOT pull from other bands until Phase 2 here is complete.
