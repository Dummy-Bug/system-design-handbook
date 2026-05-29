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

**Scarcity warning (matters for getting 3 cold cleans in-band):** Monotonic Stack (1), Trie (1), Segment Tree/BIT (1), DSU (2). Blind-spot patterns are thin here — some ownership reps will have to come cross-band.

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

---

## Ownership tracker (rule 6: owned = 3 cold first-submission cleans, distinct problems, reps 2–3 disguised)

| Bucket | Clean reps | Reps logged | Status |
|---|---|---|---|
| Greedy | **4** (01,02,05,20) | 5 | ◐ near-owned — count met, verify reps 2–3 were disguised/cold, then ●. 06 was hinted (doesn't count). |
| Prefix Sum / Diff-Array | **3** (08,17,18) | 3 | ◐ count met — confirm spacing + disguise on rep 3 to call it ●. |
| Math / NT / Combinatorics | 2 (04,23) | 3 | ◐ 11 was WA. One more clean. |
| Sliding Window | 2 (10,14) | 2 | ◐ one more clean. |
| Graph traversal (DFS/BFS) | 2 (09,16) | 2 | ◐ one more clean. |
| DP (Interval) | 1 (13) | 1 | ○ only genuine DP rep in band. Need 2 more (disguised). |
| Monotonic Stack ★ | 1 (22) | 1 | ○ blind-spot first clean. Band supplies only 1 more — rest cross-band. |
| Backtracking / Subset-Enum | 1 (19) | 1 | ○ |
| Game Theory (parity) | 1 (03) | 1 | ○ |
| Heap | 0 | 1 | ○ 21 was WA-then-AC (soft fail). Owe a clean rep. |
| Binary Search | 0 | 1 | ○ 24 was WA-then-AC. Plain-BS rep still owed (also carried from 1500-1550). |
| Tree | 0 | 1 | ○ 15 hinted + it's D&C construction, **not tree-DP**. |
| Hashing (canonical) | 0 | 1 | ○ 12 was hinted. |
| Simulation | (substrate — not an ownership target) | 1 | — |

### Blind-spot trio status (rule 6B, cross-band, each needs 3 cold cleans)
- **Monotonic Stack** — 1 clean (#22). 2 to go.
- **Tree DP** — **0 clean.** #15 looked like a candidate but is divide-and-conquer *construction*, not tree-DP. Still completely open.
- **Union-Find / DSU** — **0 clean.** Band supplies 2 DSU problems, neither attempted yet.

---

## Corrections this audit made (trust-our-solution vs original loose labels)

1. **#17 Ways to Make Fair Array** — logged "DP", but our code builds suffix odd/even sum arrays. No state/choice → **Prefix Sum**, not DP. (A suffix-sum recurrence `arr[i]=f(arr[i+1])` looks like DP but is just accumulation.)
2. **#15 Construct BST from Preorder** — logged "tree DP", but our code does D&C construction from preorder+inorder. **Tree-DP blind spot stays at 0.**
3. **#23 Alice & Bob Flower Game** — logged "game theory", but our code is pure combinatorial counting of odd-sum pairs. Game theory only in the parity reduction; no game-tree → **Math**.
4. **#19 Count Max-OR Subsets** — logged "bit ops", but the mechanic is recursive subset enumeration → **Backtracking**. Bit-OR is just the domain.

**Net effect on ownership:** genuine DP reps = 1 (not 2), tree-DP = 0, and Greedy/Prefix-Sum are the only buckets with the count for ownership (pending disguise/cold verification on reps 2–3).
