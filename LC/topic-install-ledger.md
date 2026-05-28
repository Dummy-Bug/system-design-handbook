# Topic Install Ledger

Single source of truth for **which pattern is installed at which band** across the 1500-1899+ acquisition ladder. Updated whenever a new band's Phase 1 is generated.

Last updated: 2026-05-28 (after retroactive ≥3 audit + foundational-vs-advanced split + 1900-1949 generation).

**Two pattern classes (rule formalized 2026-05-28):**
- **Foundational** — install at the FIRST band where the pattern appears, regardless of supply. The ≥3 rule does NOT apply. Examples: monotonic stack, tree DP, backtracking, plain binary search. Rationale: these are core CS patterns the user must own for 1700-rating contests; deferring them indefinitely on thin supply would leave permanent blind spots.
- **Advanced** — install ONLY at the first band with ≥3 viable (non-Design) in-band reps. If no band 1500-1899 has ≥3, the pattern is classified **outlier** and treated like Design (excluded as a target bucket). Examples: Segment Tree, Dijkstra, Bitmask DP.

See `LC/CLAUDE.md` Step 4 for the canonical rule.

---

## Foundational installs (regardless of supply)

| Pattern | Install band | Acquisition problem | Status |
|---------|--------------|---------------------|--------|
| Monotonic stack (blind-spot) | 1500-1549 | Sum of Subarray Ranges | ☐ planned · 1 cross-band clean at 1550-1600 #22 (Next Greater Node) |
| Tree DP / DFS (blind-spot) | 1500-1549 | Smallest Subtree with all the Deepest Nodes | ☐ planned |
| Backtracking | 1500-1549 | Maximum Split of Positive Even Integers | ☐ planned |
| Trie | 1500-1549 | Remove Sub-Folders from the Filesystem | ☐ planned |
| Greedy / observation | 1500-1549 | Construct K Palindrome Strings | ☐ planned |
| Linear / grid / counting DP | 1500-1549 | Count Sorted Vowel Strings | ☐ planned |
| Graph BFS/DFS (unweighted) | 1500-1549 | Find All Groups of Farmland | ☐ planned |
| Two-pointer / interval merge | 1500-1549 | Boats to Save People | ☐ planned |
| Plain binary search (lower_bound) | 1500-1549 | Maximum Distance Between a Pair of Values | ☐ planned |
| Sliding window | 1500-1549 in-band | Min Subarray Length Distinct Sum ≥ K (#1) | ✓ clean |
| Hashing / counting | 1500-1549 in-band | Count Special Triplets (#2), Rearrange K Substrings (#3) | ✓ clean |
| Heap / top-k / heap-greedy | 1500-1549 in-band | Max Product of Three After Replacement (#5) | ✓ clean |
| Math / number theory / bit | 1500-1549 in-band | Find Good Integers (#7), Largest Prime Consecutive Sum (#9) | ✓ clean (vanilla) |
| Binary search on answer | 1500-1549 in-band | Minimum K to Reduce Array Within Limit (#8) | ✓ clean |
| Prefix / sort-scan | 1500-1549 in-band | Count Special Triplets (#2), Special Array II (#6) | ✓ clean |
| Game theory | 1550-1599 | Alice and Bob Playing Flower Game | ✓ clean (47 min) |
| Interval DP | 1550-1599 | Stone Game | ✓ clean (self-derived) |
| Difference array / prefix-range | 1550-1599 derivation | Zero Array Transformation I (#8), Increment Submatrices 2D (#18) | ✓ via Phase 2 |
| Union-Find / DSU (blind-spot) | 1600-1649 | Number of Operations to Make Network Connected | ☐ planned |

## Advanced installs (only when ≥3 supply hits)

| Pattern | Install band | Acquisition problem | Cumulative supply by install band | Status |
|---------|--------------|---------------------|----------------------------------:|--------|
| Topological Sort | 1750-1799 | Loud and Rich | 1650-99: 2, 1700-49: 1, 1750-99: **3 (install)** | ☐ planned |
| Dijkstra / Shortest Path (weighted) | 1850-1899 | Find the City With the Smallest Number of Neighbors at a Threshold Distance | 1600-49: 1, 1700-49: 1, 1750-99: 2, 1800-49: 2 viable, 1850-99: **4 (install)** | ☐ planned |
| Bitmask DP | 1850-1899 | Fair Distribution of Cookies | 1700-49: 1, 1750-99: 1, 1800-49: 0, 1850-99: **4 (install)** | ☐ planned |

## Outliers / skip-class (never installed — treated like Design)

| Pattern | Reason | Total reps across 1500-1899 |
|---------|--------|----------------------------:|
| Design | CLAUDE.md rule (always) | n/a |
| Geometry | thin everywhere (2-3/band across 1700-2049) | ~8 across 6 bands, never densifies |
| Segment Tree / BIT | 0 viable Segment Tree across 9 bands; 1 BIT at 1900-49, 1 at 1950-99 — never ≥3 either | 2 viable in 9 bands |
| Monotonic deque / queue | never ≥3 in any single band | 1+1+2+0+0+2+1 = 7 split across 5 bands |
| Quickselect | 2 reps in 1650-99, 0 elsewhere | 2 across 8 bands |
| Rolling Hash | never ≥3 in any single band | 1+1+0+1+2+1+0 = 6 split across 5 bands |
| Minimum Spanning Tree | 2 reps in 7 bands, adjacent to Union-Find anyway | 2 across 7 bands |

When a problem with an outlier-class tag appears in Phase 2, it flows under its **substitute installed bucket** (e.g., Quickselect → Heap/top-k; Rolling Hash → Trie or Hashing+String; Mono Queue → Heap-greedy; MST → Union-Find).

---

## Per-band Phase 1 summary

| Band | Group A count | Topics |
|------|--------------:|--------|
| 1500-1549 | 9 + 6 in-band | mono stack, tree DP, backtracking, trie, greedy, linear/grid DP, graph BFS/DFS, two-pointer, plain BS + sliding window, hashing, heap, math/bit, BS-on-answer, prefix/sort-scan |
| 1550-1599 | 2 | game theory ✓, interval DP ✓ |
| 1600-1649 | 1 | Union-Find |
| 1650-1699 | 0 | (4 prior picks dropped by 2026-05-28 audit: Topo Sort moved to 1750-99; Mono Queue / Quickselect / Rolling Hash → outliers) |
| 1700-1749 | 0 | (Segment Tree / Dijkstra / Bitmask DP / MST all thin; Geometry skipped) |
| 1750-1799 | 1 | Topological Sort |
| 1800-1849 | 0 | (Dijkstra 2 viable still <3; deferred to 1850-99) |
| 1850-1899 | 2 | Dijkstra, Bitmask DP |
| 1900-1949 | 0 | (no new patterns; all advanced still <3) |
| 1950-1999 | 0 | (no new patterns; advanced topics still <3; Segment Tree still 0 viable through 9 bands) |

---

## Audit history

- **2026-05-28** — Built initial ledger after generating Phase 1 for 1700-1949.
- **2026-05-28** — Adopted ≥3-in-band-reps rule after noticing the 1700-1749 over-acquisition (4 picks on thin supply).
- **2026-05-28** — Retroactive ≥3 audit: dropped Dijkstra from 1600-1649 (1 rep), and Topo Sort / Mono Queue / Quickselect / Rolling Hash from 1650-1699 (all <3).
- **2026-05-28** — Foundational-vs-advanced split formalized: 1500-1549 and 1550-1599 picks confirmed all foundational (no audit changes); ≥3 rule applies only to advanced topics.
- **2026-05-28** — 1900-1949 generated: no new installs; advanced topics confirmed still thin.
- **2026-05-28** — 1950-1999 generated: same shape; no new installs; outlier classifications hold. Segment Tree confirmed 0 viable across 9 bands.

---

## When to update

Update this ledger every time a new band's Phase 1 is generated, or when a re-audit changes an install/outlier classification. The "Per-band Phase 1 summary" table at the bottom is the quick-reference; the install/outlier tables above are the source-of-truth.
