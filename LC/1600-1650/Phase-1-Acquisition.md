# Phase 1 — Acquisition (1600-1650)

**Principle:** acquisition installs a pattern's *mechanic* once. A topic already acquired at a lower band does **not** need re-acquisition here — the mechanic is learned. The harder band re-creates the need for **derivation + pattern-recognition**, not installation, so already-acquired topics carry their reps into **Phase 2 (disguised problems)**, not Phase 1.

So Phase 1 here = a real acquisition problem **only** for topics that are new this band or were never cleanly installed. Everything else is listed-and-tagged for completeness, with its work deferred to Phase 2.

> [!warning] Setup only — do NOT start solving until 1550-1600 ownership completes (rule 8). Currently 0-clean into 1550-1600 Phase 2.

**Build provenance (2026-05-28):** every bucket verified against LC official `topicTags` (`zerotrac-data/band_1600_1649_with_ar.tsv`); all 8 already-solved band problems excluded; acquisition picks are easiest available per bucket (highest AR, lowest Q-pos).

---

## Group A — Acquire in this band (new / never cleanly installed)

These get a real, easiest-per-bucket acquisition problem. Topic-visible, study-OK. Must be clean first-submission AC to count.

| # | Topic | Why acquire here | Problem | AR | QPos | Link |
|---|-------|------------------|---------|-----|------|------|
| 1 | **Union-Find / DSU** | scarce at 1500-1550 (~1, deferred); 7 in-band here — first real acquisition | Number of Operations to Make Network Connected | 66.6% | Q3 | https://leetcode.com/problems/number-of-operations-to-make-network-connected/ |

> [!warning] Shortest Path / Dijkstra REMOVED 2026-05-28 (≥3 rule audit)
> Previously listed as Group A #2 (Find a Safe Walk Through a Grid). Live LC tag re-fetch confirmed the band has **only 1 Shortest Path-tagged problem** — fails the ≥3-in-band-reps rule adopted 2026-05-28. Deferred to **1850-1899** where supply reaches 4 reps. See `LC/topic-install-ledger.md` (to be written).

> [!note] Demoted out of Group A by the 2026-05-28 re-base
> Three topics once listed as 1600-1650 acquisitions actually first appear lower, so they're now **Group B** (acquired at the floor) and their 1600-1650 problems are Phase 2 derivation reps:
> - **Binary search on answer** → acquired at **1500-1550 #8** (Minimum K to Reduce Array). Max Candies becomes a Phase 2 deriv rep here.
> - **Trie** → acquired at **1500-1550 #4** (Remove Sub-Folders). Short Encoding of Words becomes a Phase 2 deriv rep.
>
> **Design is removed entirely** (2026-05-28) — it is not a derivation/ownership target at any band. Design problems are simply ignored.

---

## Group B — Already acquired @ 1550-1600 → Phase 2 only (no re-acquisition)

Listed for completeness and tagged with the lower-band acquisition. **No acquisition problem to solve here** — the disguised/derivation reps come from **Phase 2**, which is mandatory for every one of these.

> [!important] These are OWNED, not shaky, by the time this band opens.
> Rule 8 forbids entering 1600-1650 until 1550-1600 has graduated — and graduation (rule 6A) requires **3 cold cleans per bucket** at 1550-1600. So even the topics whose *Phase 1 acquisition* was soft/hinted (math/NT, hashing, tree DP, plain BS) get cleanly owned via 1550-1600 **Phase 2** before we arrive. The Phase-1 outcome below is just historical provenance; it does not mean the install is weak when this band starts.

> [!note] Re-base 2026-05-28 — acquisition floor is 1500-1550
> The "#1550-1600" pointers below are *not* the true acquisition band for most of these. The ladder floor is **1500-1550**: monotonic stack, tree DP, backtracking, trie, plain BS, math/NT, greedy, sliding window, graph, bit, DP, hashing, and heap are all **acquired at 1500-1550**, then *re-derived* (Phase 2) at 1550-1600. The references below mark where each was re-derived, not first installed. Only game theory and interval DP are 1550-1600-native.

| Topic | Acquired @ 1550-1600 | Phase-1 outcome (historical) |
|-------|----------------------|------------------------------|
| Greedy / observation | #1 Pancake Sorting | clean |
| Sliding window | #3 Binary Subarrays With Sum | clean |
| Graph BFS/DFS / flood-fill | #4 Restore the Array From Adjacent Pairs | clean |
| Bit manipulation | #5 Count Max Bitwise-OR Subsets | clean |
| Linear / grid DP | #9 Ways to Make a Fair Array | clean |
| Monotonic stack | #11 Next Greater Node In Linked List | clean (thin in-band — cross-band reps too) |
| Math / number theory | #7 Happy Strings | soft fail → owned via 1550-1600 Phase 2 |
| Hashing / counting | #8 Groups of Special-Equivalent Strings | hinted → owned via 1550-1600 Phase 2 |
| Tree DP / DFS | #12 Construct BST from Preorder | hinted → owned via 1550-1600 Phase 2 |
| Plain binary search (lower_bound) | #14 Closest Nodes Queries in BST | soft fail → owned via 1550-1600 Phase 2 |
| Backtracking | 1500-1550 #3 Max Split Even Integers | present here (construct-smallest-number-from-di-string [1641]) → Phase 2 only |
| Trie | 1500-1550 #4 Remove Sub-Folders | present here (short-encoding, shortest-uncommon-substring) → Phase 2 only |
| Binary search on answer | 1500-1550 #8 Minimum K to Reduce Array | present here (max-candies, min-time-trips) → Phase 2 only |

---

## Tracker (Group A only — Group B has no acquisition step)

| # | Topic | Phase 1 | Status |
|---|-------|---------|--------|
| 1 | Union-Find / DSU | ☐ | — |
