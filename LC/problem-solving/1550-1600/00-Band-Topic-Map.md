# 1550–1600 Band — Topic Map & Ownership Tracker

> Built 2026-05-29. SPOILER FILE — do not read pattern/set columns before a blind solve.
> Purpose: (1) the canonical topic list for this band, (2) every solved problem classified
> by the mechanic *actually used in our own solution* (not the editorial, not the LC tag),
> (3) per-bucket ownership counts against rule 6 (3 cold first-submission cleans on distinct problems).

---

## How the topic list was generated

No single source is complete, so the list is a synthesis of three:

1. **LearnYard subgroups** (`editorials-data/band_1550_1599_subgroups.tsv`) — clean curriculum buckets, but only classifies **59 of the 83** band problems. Critically, **all 23 solved problems fall in the unclassified 24** (they are recent contest problems LearnYard hasn't cataloged). So LearnYard is the spine for *unsolved* problems but is blind to everything we've actually done.
2. **AlgoMaster patterns** — [15 LeetCode patterns](https://blog.algomaster.io/p/15-leetcode-patterns) + [20 DP patterns](https://blog.algomaster.io/p/20-patterns-to-master-dynamic-programming). Used to *refine* LearnYard (esp. DP) and to name patterns LearnYard lumps together.
3. **Our own solutions** (`First-Attempt/`) — the authority for classifying solved problems. Priority rule: **classify by the mechanic in our code, not the editorial's approach or the original loose label.**

Editorials for all 83 are downloaded at `editorials-data/band_1550_1599/`.

---

## Band topic supply (LearnYard, across the 59 classified of 83)

| Main topic | Subgroup | # problems |
|---|---|---|
| Hashing | Implementary Problems | 16 |
| Greedy | Part I | 14 |
| Sorting | Implementary | 10 |
| DP Level 1 | Linear DP | 8 |
| 2 Pointers | Two Pointer on Arrays | 8 |
| 2 Pointers | Two Pointer on Strings | 5 |
| Matrix | Implementary | 5 |
| Sliding Window | Dynamic Size | 5 |
| Prefix Sum | Implementary | 5 |
| Stack | Implementary Stack | 4 |
| Stack | Stack with String | 3 |
| Binary Search | Upper/Lower Bound | 3 |
| Bit Manipulation | Basic Bit Concepts | 3 |
| DP Level 1 | DP on String | 2 |
| DP Level 1 | DP on Grid | 2 |
| Combinatorics & Geometry | Line | 2 |
| Graphs | Graph Representation | 2 |
| Graphs | Disjoint Set Union (DSU) | 2 |
| Recursion & Backtracking | Recursion | 1 |
| String Matching | Pattern Matching | 1 |
| Heap (PQ) | Implementary | 1 |
| Tries | Trie involving String | 1 |
| Advanced | Segment Tree / BIT | 1 |
| Stack | Monotonic Stack | 1 |

**Scarcity warning (matters for getting 2 clean self-derived ACs in-band):** Monotonic Stack (1), Trie (1), Segment Tree/BIT (1), DSU (2). Blind-spot patterns are thin here — some ownership reps will have to come cross-band.

### AlgoMaster patterns absent from this band
Fast & Slow Pointers, LinkedList In-place Reversal, Overlapping Intervals — not present at 1550–1600. The band's biggest buckets (Greedy, Hashing, Sorting) aren't in AlgoMaster's 15 at all, which is why LearnYard is the spine.

---

## Solved problems — classified by the mechanic in OUR code

24 logged in `First-Attempt/`. `Clean` = first-submission AC, no hint (counts toward ownership). `★` = blind-spot pattern.

| # | Problem | Mechanic in our code | Canonical bucket | Tags | Clean? |
|---|---|---|---|---|---|
| 01 | Max Bitwise XOR After Rearrangement | MSB-first greedy pairing on 0/1 counts | Greedy | `Greedy` `Counting` `Bit-framing` | ✅ |
| 02 | Min Cost to Equalize Arrays | frequency map + excess pairing | Greedy | `Greedy` `Hashing/Counting` | ✅ |
| 05 | Min Cost to Acquire Items | case analysis on costs | Greedy | `Greedy` `Case-analysis` | ✅ |
| 06 | Max Sum 3 Nums Div by 3 | greedy over mod-buckets | Greedy | `Greedy` `Modular-arith` | ❌ hinted |
| 20 | Pancake Sorting | place max→front→tail, repeat | Greedy (constructive) | `Greedy` `Constructive` | ✅ |
| 21 | Min Ops to Halve Array Sum | max-heap, halve largest | Heap | `Heap` `Greedy` | ❌ WA-then-AC |
| 08 | Zero Array Transformation I | 1D difference array | Prefix Sum / Diff-Array | `Prefix-Sum` `Difference-Array` | ✅ |
| 18 | Increment Submatrices by One | 2D diff-array + 2 sweeps | Prefix Sum / Diff-Array | `Prefix-Sum` `Diff-Array-2D` `Matrix` | ✅ |
| 17 | Ways to Make a Fair Array | suffix odd/even sums + prefix | Prefix Sum | `Prefix-Sum` `Suffix-Sum` `Parity` | ✅ |
| 10 | Power of K-Size Subarrays II | consecutive-run tracking | Sliding Window | `Sliding-Window` `Run-length` | ✅ |
| 14 | Binary Subarrays With Sum | atMost(K) − atMost(K−1) | Sliding Window | `Sliding-Window` `atMost-trick` | ✅ |
| 09 | Unit Conversion I | DFS on graph, running product | Graph traversal | `Graph` `DFS` | ✅ |
| 16 | Restore Array from Adjacent Pairs | adjacency map → BFS path | Graph traversal | `Graph` `BFS` `Path-graph` | ✅ |
| 24 | Closest Nodes in BST | inorder → sorted → BS floor/ceil | Binary Search | `Binary-Search` `BST-inorder` `floor/ceil` | ❌ WA-then-AC |
| 15 | Construct BST from Preorder | inorder=sort(pre) → D&C build | Tree construction (D&C) | `Tree` `BST` `Divide-Conquer` | ❌ hinted |
| 22 | Next Greater Node in Linked List | reverse + decreasing stack | Monotonic Stack ★ | `Monotonic-Stack` `Linked-List` | ✅ |
| 19 | Count Max Bitwise-OR Subsets | recursive include/exclude | Backtracking / Subset-Enum | `Backtracking` `Subset-Enum` `Bit-OR` | ✅ |
| 04 | Smallest All-Ones Multiple | BFS/recurrence on remainders | Math / Number Theory | `Number-Theory` `Modular` `Pigeonhole` | ✅ |
| 11 | Kth Happy String | constructive recursion via counting | Math (combinatorics) | `Math` `Combinatorics` `Constructive-recursion` | ❌ WA-then-AC |
| 23 | Alice & Bob Flower Game | count odd-sum pairs (clamped) | Math (combinatorics) | `Math` `Combinatorics` `GT-reduction` | ✅ |
| 03 | Final Element After Deletions | parity / one-move reduction | Game Theory (parity) | `Game-Theory` `Parity` `Brainteaser` | ✅ |
| 13 | Stone Game | memoized f(i,j) over interval | DP (Interval / Minimax) | `DP` `Interval-DP` `Minimax` | ✅ (over-cap, derivation clause) |
| 12 | Groups of Special-Equiv Strings | canonical key (sorted halves) in Set | Hashing (canonical-form) | `Hashing` `Sorting` `Canonical-key` | ❌ hinted |
| 07 | XOR After Range Mult Queries I | direct simulation | Simulation (substrate) | `Simulation` | ✅ |
| 30 | Count Collisions on a Road | count cars that stop (n − leadL − trailR) | Stack + **Invariant/Reframe** ✦ | `Stack` `Invariant/Reframe` `Brainteaser` | ❌ editorial (2 WA) |
| 31 | Count Paths With Given XOR Value | top-down memo `dp[i][j][x]`, XOR as bounded dim | DP » Grid (XOR-state) | `DP` `Grid-DP` `Bit` `Matrix` | ✅ (over-cap, derivation clause) |
| 34 | Longest Arith Subseq of Given Difference | value-keyed `dp[v]=dp[v−d]+1`, fixed-diff ⇒ unique predecessor | DP » LIS-variant | `DP` `LIS-variant` `Hashing-as-DP-table` | ✅ (over-cap, derivation clause) |
| 32 | Sentence Similarity III | prefix+suffix two-pointer (shorter = prefix∪suffix of longer) — but OUR code over-modeled w/ map+deque | Two Pointers (string) | `Two-Pointers` `String` | ❌→✓ soft fail (multi-WA, over-modeled) |
| 33 | Number of Ways Square = Product | frequency map of pairwise products, look up squares (count not positions) | Hashing (counting) | `Hashing` `Counting` `Invariant/Reframe` | ✅ clean first-AC (22m SUB-CAP) |
| 35 | Count Incremovable Subarrays I | prefix/suffix increasing decomp + two-pointer merge-count; middle descent forced into every removal | Two Pointers (array) + Invariant/Reframe ✦ | `Two-Pointers` `Prefix-Suffix` `Invariant/Reframe` | ◐ assisted acq. (skeleton+bug given) — installs, doesn't count. Consolidation win (120m→sleep→26m) |

---

## Ownership tracker (rule 6: owned = **2 clean self-derived first-submission ACs** on distinct problems — Set-A or Set-B both count, no acquisition phase in this band)

> **RE-AUDITED 2026-06-03 under the final 2-rule.** Owned = **2 clean self-derived first-AC** on distinct problems
> (clean = first-sub AC no WA; self-derived = no hint/editorial). **No acquisition phase here** — every clean
> self-derived solve counts, announced (Set-A) or disguised (Set-B). Excluded only: hinted / WA-then-AC / editorial.
> No spacing requirement (retention = the rule-5 revision lock). **Net: 5 buckets OWNED ●; 7 at 1-of-2; rest at 0.**

| Bucket | Clean self-derived ACs | Non-counting | Status |
|---|---|---|---|
| Greedy | **2+** (01,02,05,20,29) | 06 hinted | ● **OWNED** |
| Prefix Sum / Diff-Array | **3** (08,17,18) | — | ● **OWNED** |
| Sliding Window | **4** (10,14,25,26) | — | ● **OWNED** |
| Graph traversal (DFS/BFS) | **2** (09,16) | — | ● **OWNED** |
| Math / NT / Combinatorics | **2** (04,23) | 11 WA; 33-NT hard-fail | ● **OWNED** _(04: AC self-derived; a deeper bound was taught post-hoc — the solve itself was clean, so it counts)_ |
| **DP » LIS-variant** | 1 (34) | — | ◐ **1 of 2** — 34 longest-arith-subseq. Owe 1. |
| **DP » Grid** | 1 (31) | — | ◐ **1 of 2** — 31 count-paths-with-xor. Owe 1. |
| Hashing (canonical/counting) | 1 (33) | 12 hinted | ◐ **1 of 2** — 33 product frequency-map. Owe 1. |
| Backtracking / Subset-Enum | 1 (19) | — | ◐ **1 of 2** — 19 count-max-OR-subsets. Owe 1. |
| Game Theory (parity) | 1 (03) | — | ◐ **1 of 2** — 03 final-element. Owe 1 (parity scarce in band). |
| **DP » Interval/Minimax** | 1 (13) | — | ◐ **1 of 2** — 13 stone-game. Owe 1 (interval scarce → likely cross-band). |
| Monotonic Stack ★ | 1 (22) | 30 hard-fail | ◐ **1 of 2** — blind-spot, 22 next-greater-node. Owe 1, cross-band. |
| **DP » Linear / Count-ways** | 0 | 28 soft fail | ○ owe 2. ways-to-split already attempted (soft fail). |
| **DP » String** | 0 | — | ○ owe 2 (band-present but unqueued). |
| Two Pointers (string/array) | 0 | 32 soft fail; 35 soft-hinted | ○ owe 2. 35 installed prefix/suffix merge-count but soft-hinted (doesn't count). Next cold two-pointer = the test. |
| Heap | 0 | 21 soft fail | ○ owe 2. |
| Binary Search | 0 | 24 soft fail | ○ owe 2 + plain-BS carried from 1500-1550. |
| Tree | 0 | 15 hinted (D&C, not tree-DP) | ○ **blind-spot (tree-DP)** — owe 2. |
| Union-Find / DSU | 0 | — | ○ **blind-spot** — owe 2. Band supplies #19/#20 (earliest-moment-friends, properties-graph), neither attempted. |
| Simulation | (substrate — not an ownership target) | — | — |
| ✦ **Invariant / Reframe** (NON-STANDARD) | n/a — no clean-rep gate | deck: 8 solved | ✦ **Grow & review deck, not an ownership target — NEVER blocks graduation.** Cross-cutting axis. Solved members (83-editorial audit 2026-06-01): STRONG = 03, 23, 28, 30; LIGHTER = 02, 04, 17, 25. 6 more STRONG in the blind queue. See `patterns/master-taxonomy.md` → Invariant/Reframe. |

> **DP is tracked by sub-pattern, never as one bucket** (master taxonomy = 20 DP sub-patterns; see `patterns/master-taxonomy.md`).
> A Linear-DP rep does NOT cover Grid-DP, LIS, Interval, etc. — each owns separately, 2 cold disguised cleans each.
> At 1550–1600 only ~5 DP sub-patterns appear (Interval, Linear/Count-ways, LIS-variant, Grid, String).
> The deep ones — **Knapsack, LCS, Edit Distance, Bitmask, Digit, Tree-DP ★, Probability, State-Machine** — are
> absent at this level and roll to higher bands. So "owning DP here" only means owning those ~5 shallow sub-patterns.

### Blind-spot trio status (rule 6B, cross-band, each needs **2** clean self-derived ACs)
- **Monotonic Stack** — **1 clean (#22 next-greater-node).** 1 to go. (#30 was a hard-fail.)
- **Tree DP** — **0 clean.** #15 looked like a candidate but is divide-and-conquer *construction*, not tree-DP. Still completely open.
- **Union-Find / DSU** — **0 clean.** Band supplies 2 DSU problems (#19 earliest-moment-friends, #20 properties-graph), neither attempted yet.

---

## Corrections this audit made (trust-our-solution vs original loose labels)

1. **#17 Ways to Make Fair Array** — logged "DP", but our code builds suffix odd/even sum arrays. No state/choice → **Prefix Sum**, not DP. (A suffix-sum recurrence `arr[i]=f(arr[i+1])` looks like DP but is just accumulation.)
2. **#15 Construct BST from Preorder** — logged "tree DP", but our code does D&C construction from preorder+inorder. **Tree-DP blind spot stays at 0.**
3. **#23 Alice & Bob Flower Game** — logged "game theory", but our code is pure combinatorial counting of odd-sum pairs. Game theory only in the parity reduction; no game-tree → **Math**.
4. **#19 Count Max-OR Subsets** — logged "bit ops", but the mechanic is recursive subset enumeration → **Backtracking**. Bit-OR is just the domain.

**Net effect on ownership (post 2026-06-03 re-audit, final 2-clean rule):** **5 buckets OWNED ●** — Greedy, Prefix-Sum, Sliding Window, Graph, Math/NT. **7 at 1-of-2** — DP-LIS(34), DP-Grid(31), Hashing(33), Backtracking(19), Game-Theory(03), DP-Interval(13), Monotonic-Stack(22). **0-of-2** — DP-Linear, DP-String, Two-Pointers, Heap, Binary-Search, Tree, Union-Find. No acquisition phase in this band: every clean self-derived solve counts (Set-A or Set-B), so the old Phase-1 solves are full reps.
