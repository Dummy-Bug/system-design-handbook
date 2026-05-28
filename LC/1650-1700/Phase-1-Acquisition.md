# Phase 1 — Acquisition (1650-1700)

**Principle (per `LC/CLAUDE.md` Step 4):** acquisition installs a pattern's *mechanic* once, at the lowest band where it appears. By the time this band opens, rule 8 guarantees **both** 1550-1600 and 1600-1650 have graduated — so nearly every pattern is already acquired and owned. Phase 1 here gets a real acquisition problem **only** for patterns genuinely new to this band; everything else is Group B (tagged, Phase 2 only).

> [!warning] Setup only — do NOT start solving until 1550-1600 AND 1600-1650 ownership complete (rule 8). Currently 0-clean into 1550-1600 Phase 2; 1600-1650 is paused.

**Build provenance (2026-05-28):** every bucket verified against LC official `topicTags` (`zerotrac-data/band_1650_1699_with_ar.tsv`); all 10 already-solved band problems excluded; acquisition picks are easiest available per bucket (highest AR / lowest Q-pos).

---

## Group A — EMPTY (all 4 prior picks failed the ≥3 audit on 2026-05-28)

Live LC tag re-fetch + ≥3-in-band-reps rule applied retroactively (rule adopted 2026-05-28). All 4 prior Group A picks have been removed:

| Prior pick | In-band reps | Fate |
|-----------|-------------:|------|
| Topological Sort (Find All Possible Recipes) | 2 | → defer; install band is **1750-1799** (3 reps) |
| Monotonic Queue (Longest Continuous Subarray) | 1 | → **outlier / skip-class** (never ≥3 across 1500-1899) |
| Quickselect (Query Kth Smallest Trimmed Number) | 2 | → **outlier / skip-class** (2 reps in 6 bands) |
| Rolling Hash (Minimum Time to Revert Word) | 1 | → **outlier / skip-class** (never ≥3 across 1500-1899) |

All four problems remain valid Phase 2 derivation reps under Group B (their owned-from-lower-band buckets — quickselect's heap subst, rolling-hash's trie subst, monotonic queue's heap-greedy subst, topo sort's graph BFS subst).

> [!note] Backtracking removed from Group A (2026-05-28 buried-topic audit)
> Backtracking was originally Group A #2 here (Path with Maximum Gold). The audit found backtracking first appears at **1500-1550** — so it's now acquired there and is **Group B** below.

---

## Group B — Already acquired @ 1550-1600 / 1600-1650 → Phase 2 only

Listed for completeness, tagged with the acquisition band. **No acquisition problem here** — disguised/derivation reps and this band's 3-cold-clean ownership come from **Phase 2**, mandatory for each.

> [!important] These are OWNED, not shaky, on arrival. Rule 8 forbids entering 1650-1700 until all lower bands graduated (3 cold cleans per bucket each). Acquisition-outcome notes below are historical provenance only.

> [!note] Re-base 2026-05-28 — acquisition floor is 1500-1550
> Acquisition pointers below are re-based: monotonic stack, tree DP, backtracking, trie, plain BS, math/NT, greedy, sliding window, graph, bit, DP, hashing, heap → **first acquired at 1500-1550** (the ladder floor), not at 1550-1600/1600-1650. Game theory & interval DP are 1550-1600-native; union-find & shortest-path are 1600-1650-native; BS-on-answer is 1500-1550-native. The band labels below mark provenance under the re-based ladder. (Design is excluded everywhere — not a target.)

| Topic | Acquired | Provenance |
|-------|----------|------------|
| Greedy / observation | 1550-1600 #1 | clean |
| Sliding window | 1550-1600 #3 | clean |
| Graph BFS/DFS / flood-fill | 1550-1600 #4 | clean |
| Bit manipulation | 1550-1600 #5 | clean |
| Math / number theory | 1550-1600 #7 | soft → owned via Phase 2 |
| Hashing / counting / prefix-state | 1550-1600 #8 | hinted → owned via Phase 2 |
| Linear / grid / counting DP | 1550-1600 #9 | clean |
| Heap / PQ greedy | 1550-1600 #10 (soft) | owned via 1600-1650 Phase 2 |
| Monotonic stack | 1550-1600 #11 | clean (thin everywhere — reps span bands) |
| Tree DP / DFS | 1550-1600 #12 | hinted → owned via Phase 2 |
| Plain binary search | 1550-1600 #14 | soft → owned via Phase 2 |
| Prefix / suffix precompute | 1550-1600 (diff-array / sliding) | clean |
| Backtracking | 1550-1600 #15 Iterator for Combination (added 2026-05-28 audit) | acquired |
| Trie | 1550-1600 #16 Search Suggestions System (corrected 2026-05-28 — audit found it's a 1550 topic, not 1600) | acquired |
| Union-Find / DSU | 1600-1650 Group A #1 | acquired |
| ~~Shortest path / Dijkstra~~ | DEFERRED → 1850-1899 (≥3 rule audit 2026-05-28) | — |
| Binary search on answer | 1500-1550 #8 (re-based) | acquired |

---

## Tracker (Group A only)

Group A is empty — no tracker rows. Phase 1 at this band is a no-op; jump straight to Phase 2 generation when this band activates.
