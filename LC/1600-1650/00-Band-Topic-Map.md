# 1600-1650 Band — Full Topic Map (all 90 problems)

> [!danger] SPOILER — this file labels every problem with its solution pattern and set (A/B). Do **not** read it before solving the blind queue (`_Sealed-Queue.md`). Use it only for planning and post-solve debrief.

Built 2026-05-26 by reading every problem statement (rating ≤ 1650) from `zerotrac-data/content-tsv/all_1600_with_content.tsv`. Pattern = the *primary* technique the intended solution uses, judged from the actual statement (not the title, not the math-topic tag in the tsv).

**Legend:** ✅ done · ⏭️ skipped · ⭐ recommended next (gap-filling, high transfer)

---

## Coverage summary

| Pattern | # problems | Done? | Priority to train |
|---------|-----------|-------|-------------------|
| Hashing / counting | 14 | ✅✅✅ (3 done) | low — already strong |
| Linear / grid DP | 9 | ✅✅ (2 done) | low-med |
| Greedy / observation | 13 | — | med |
| Sliding window / prefix-count | 7 | ✅ (1 done) | med |
| Math / bit / parity (tsv-tagged) | 16 | — | low (covered by math-reflex) |
| **Binary search on answer** | **4** | ❌ none | **HIGH — gap** |
| **Monotonic stack** | **2** | ❌ none | **HIGH — gap** |
| **Tree DP / DFS** | **6** | ❌ none | **HIGH — gap** |
| **Union-Find (DSU)** | **4** | ❌ none | **HIGH — gap (newly found)** |
| **Graph BFS/DFS / flood-fill** | **7** | ❌ none | **MED-HIGH — gap** |
| Design (data structure) | 4 | ❌ none | med |
| Trie | 1 | ❌ none | low |
| Interval DP | **0** | — | n/a — absent at this band (1700+ topic) |

The four ❌ HIGH rows are where contest Q3 lives. You've done 7 problems and **zero** of them touch a stack, a binary-search-on-answer, a tree recursion, or a DSU.

---

## GAP PATTERNS (train these)

### Binary search on answer (4)
| Rating | Problem | Why / twist |
|--------|---------|-------------|
| 1606 | Sum of Mutated Array Closest to Target | BS on cap value; objective is *closest to target* (tie→min), answer not in array. Harder objective. |
| 1640 | ⭐ Minimum Time to Complete Trips | `feasible(t)=Σ(t/time[i])≥trips`. Cleanest predicate. Answer ~10¹⁴ → **forces `long`** (trains overflow too). |
| 1646 | Maximum Candies Allocated to K Children | `feasible(x)=Σ(candy/x)≥k`. Clean. Edge: answer can be 0. |
| 1641 | Minimize Maximum Component Cost | BS on max edge weight **+ union-find** to count components. Two patterns at once — advanced. |

### Monotonic stack (2)
| Rating | Problem | Why / twist |
|--------|---------|-------------|
| 1607 | ⭐ Maximum Width Ramp | The canonical one. Decreasing stack of left candidates + reverse scan. High transfer (next-greater family). |
| 1641 | Construct Smallest Number From DI String | Stack push-1..9 / pop-on-'I' is the clean solution (also greedy-able). Secondary stack rep. |

### Tree DP / DFS (6)
| Rating | Problem | Why / twist |
|--------|---------|-------------|
| 1607 | ⭐ Lowest Common Ancestor of Deepest Leaves | Post-order returns `(depth, lca)`; non-trivial combine at parent. Best "return info up the tree" teacher. |
| 1603 | K-th Largest Perfect Subtree Size | Post-order returns `(isPerfect, size, height)`; collect & sort. Gentler tuple-return. |
| 1649 | Linked List in Binary Tree | Nested DFS (match path) — *not* DP, different muscle. |
| 1635 | Min Operations to Sort Binary Tree by Level | BFS per level + min-swaps-to-sort (cycle decomposition). |
| 1643 | Create Binary Tree From Descriptions | Hashmap construction; comprehension/impl, not DP. |
| 1633 | Reorder Routes to Make All Paths Lead to City Zero | DFS on a tree, count edges pointing wrong way. |

### Union-Find / DSU (4) — newly surfaced gap
| Rating | Problem | Why / twist |
|--------|---------|-------------|
| 1638 | ⭐ Satisfiability of Equality Equations | The textbook DSU intro: union `==`, then check `!=` contradictions. |
| 1604 | Count Unreachable Pairs of Nodes | DSU component sizes → pair counting across components. |
| 1633 | Number of Operations to Make Network Connected | DSU components; answer = `components−1` if enough cables. |
| 1641 | Minimize Maximum Component Cost | DSU under a binary search (see above). |

### Graph BFS/DFS / flood-fill (7)
| Rating | Problem | Why / twist |
|--------|---------|-------------|
| 1624 | Is Graph Bipartite? | 2-coloring via BFS/DFS. Core graph rep. |
| 1615 | Number of Enclaves | Flood-fill from borders. |
| 1638 | Nearest Exit from Entrance in Maze | BFS shortest path on grid. |
| 1607 | Find a Safe Walk Through a Grid | BFS/Dijkstra with health budget. |
| 1633 | Reorder Routes (also tree) | DFS/BFS edge orientation. |
| (1604 Count Unreachable also graph) | — | — |
| 1632 | Short Encoding of Words | Trie (suffix) — adjacent skill. |

---

## ALREADY-STRONG PATTERNS (don't over-train)

### Hashing / counting (14) — 3 done
Done: Count Caesar Cipher Pairs [1624], Identify the Largest Outlier [1643], Sum of Digit Differences [1645].
Others: Alert Using Key-Card [1606], Relocate Marbles [1613], Count Number of Bad Pairs [1622], Task Scheduler II [1622], Word Subsets [1624], Can Convert String in K Moves [1631], Reward Top K Students [1636], Remove Letter To Equalize Frequency [1648], Rank Teams by Votes [1626], Cinema Seat Allocation [1636].

### Linear / grid DP (9) — 2 done
Done: House Robber V [1618] (linear), Min Cost Path Alt Directions II [1639] (grid).
Others worth a rep (distinct trick): Flip String to Monotone Increasing [1601] (two-state), Count Ways to Place Houses [1607] (Fibonacci), **Count Square Submatrices with All Ones [1613]** (`dp=min(3 neighbors)+1` — genuinely new trick), Maximum Number of Moves in a Grid [1625], Shortest Distance to Target Color [1626] (L/R pass), Partition String ≤K [1604].

### Sliding window / prefix-count (7) — 1 done
Done: Min Discards to Balance Inventory [1638].
Others: Count Number of Nice Subarrays [1623] (atMost trick), Maximize the Confusion of an Exam [1643], Number of Substrings Containing All Three Chars [1646], Maximum Beauty of an Array [1638] (sort+window — *not* BS), Number of Subarrays With GCD=K [1602], Number of Sub-arrays With Odd Sum [1610].

### Greedy / observation (13)
Adjacent Increasing Subarrays II [1600], Min Ops Median=K [1604], Construct Longest New String [1607], Min Score by Changing Two [1608], Escape The Ghosts [1611], Last Moment Ants Fall [1618], Min Ops Array Equal II [1619], Min Buckets Rainwater/hamsters [1622], Merge Triplets [1635], Largest Palindromic Number [1636], Min Function Calls [1637], Advantage Shuffle [1648] (two-pointer), Maximum Matrix Sum [1648], Previous Permutation With One Swap [1633], Min Deletions Divisible [1640], Happy Students [1625], Remove Palindromic Subsequences [1628] (answer∈{0,1,2}).

### Math / bit / parity (16) — covered by math-reflex
The tsv-tagged set (PARITY, BIT_OPS, GEOM, MOD_ARITH, GCD, XOR, PRIME, etc.). Train via math-reflex drills, not full solves.

### Design (4)
Longest Uploaded Prefix [1604], Design Front Middle Back Queue [1610], Design an ATM Machine [1616], Design Exam Scores Tracker [1647].

---

## Recommended next 3 (close the 3 hardest gaps, one each)

1. ⭐ **Maximum Width Ramp [1607]** — monotonic stack (only canonical one in band).
2. ⭐ **Minimum Time to Complete Trips [1640]** — binary search on answer + overflow lesson.
3. ⭐ **Lowest Common Ancestor of Deepest Leaves [1607]** — tree DP (return-info-up idiom).

**Then, before graduating the band, also touch union-find** (Satisfiability of Equality Equations [1638]) and one graph BFS/DFS (Is Graph Bipartite? [1624]) — both are entirely-untouched core 1600+ patterns that the per-problem read revealed. These two matter as much as the original three; they were missing from the first gap list because that list was built from the 7 solved problems, not from the band's actual contents.

**Interval DP:** confirmed absent at ≤1650 across all 90 — do not force it here; it's a 1700+ topic.

---

## Ownership tracker

Owned = **3 cold first-submission cleans**, reps 2-3 disguised/combined (rule 6). Marks: `◯` 0/3 · `◐` 1-2/3 · `●` owned. Only clean first-submission counts; soft-fail (#1,#2,#4) and hinted (#5,#6) = 0.

| Core bucket | Cold cleans | Status | Need |
|-------------|-------------|--------|------|
| Greedy / prefix-suffix scan | 1 (#3) | ◐ | 2 disguised |
| Hashing / counting | 1 (#7) | ◐ | 2 disguised (#2,#6 didn't count) |
| Linear / grid DP | 0 (#1 soft, #5 hinted) | ◯ | 3 |
| Sliding window | 0 (#4 soft) | ◯ | 3 |
| Graph BFS/DFS | 0 | ◯ | 3 |
| Design | 0 | ◯ | 3 |
| **Monotonic stack** (blind) | 0 | ◯ | acquisition + 3 |
| **Binary search on answer** | 0 in band | ◯ | 3 (cross-band rep exists @1500-1550) |
| **Tree DP** (blind) | 0 | ◯ | acquisition + 3 |
| **Union-Find** (blind) | 0 | ◯ | acquisition + 3 |

---

## What's already trained (the 7 solved, on both axes)

Depth scored from how the solve actually went (verdicts + WA-causes are the evidence).

| # | Problem | Breadth (pattern) | D×C | Note |
|---|---------|-------------------|-----|------|
| 1 | House Robber V | linear DP (constrained) | 6 | 4 WAs on recurrence (`logic-recurrence`) |
| 2 | Count Caesar Cipher Pairs | hashing + pair-count | 4 | delta-vs-cumulative bug |
| 3 | Split Array Min Difference | greedy prefix/suffix scan | 6 | shared-element reframe (deck Card 01); clean |
| 4 | Min Discards Balance Inventory | fixed sliding window | 6 | item-vs-arrival misread (`read-error`) |
| 5 | Min Cost Path Alt Dir II | grid DP | 6 | cost mechanics misread ×2 (`read-error`), hinted |
| 6 | Identify Largest Outlier | hashing + algebra reframe | 9 | index-aliasing recognition, hinted both attempts |
| 7 | Sum of Digit Differences | digit-position freq count | 2 | clean, fast |

**Breadth covered (4 buckets only):** linear+grid DP, hashing (×3, over-represented), sliding window, greedy/scan. **Zero** in the 5 gap patterns.
**Depth:** already well-exercised — avg D×C ≈ 5, five of seven ≥ 6. Not depth-starved; depth was just confined to those 4 buckets.
**Implication:** more depth-reps on the covered buckets = diminishing returns. **Breadth (Set A) is the deficient axis.** Set B's highest value is on the *comprehension* sub-axis (the `read-error` losses), so weight Set B toward misreadable statements.

---

## The training plan — two sets, two jobs

Both sets matter; they train different things and use different protocols. Breadth is not competing with depth — **breadth is the floor that makes depth-training possible at the next band.** You can't derive a 1700 DSU cold if the DSU primitive isn't installed; at 1700 the *pattern* must be free so the whole derivation budget goes to the *twist*.

### Set A — Breadth / Prerequisite Ladder
**Job:** install the missing primitive at 1600 so it's not the blocker at 1700+.
**Protocol:** studying the pattern is *allowed* — this is vocabulary acquisition, not a cold test. One clean rep per untouched pattern. The 3 problems needed to reach the 10-logged graduation count come from here.

| Pattern | Problem | rating |
|---------|---------|--------|
| Monotonic stack | Maximum Width Ramp | 1607 |
| Binary search on answer | Minimum Time to Complete Trips | 1640 |
| Tree DP | Lowest Common Ancestor of Deepest Leaves | 1607 |
| Union-Find | Satisfiability of Equality Equations | 1638 |
| Graph BFS/DFS | Is Graph Bipartite? | 1624 |

### Set B — Derivation × Comprehension
**Job:** train the diagnosed muscle (cold derivation) + the dominant band failure mode (read-error / comprehension — 3 of 5 misses in the second-attempt log). Pattern may be *familiar*; what qualifies a problem is a non-obvious reframe and a misreadable statement.
**Protocol:** cold, no study, no hints, full 5-step ritual. This is the set that counts as real derivation reps and is the better *test* for the clean-AC metric.
**Score = Derivation(1-3) × Comprehension(1-3).** (Weighting can be revisited — comprehension may deserve a heavier weight since it's the #1 failure mode.)

| Problem | rating | D×C | The trap |
|---------|--------|-----|----------|
| Find the Integer Added to Array II | 1620 | 3×3=**9** | two elements removed + offset; try-each-removal + matching, dense statement |
| Count Number of Bad Pairs | 1622 | 3×2=6 | reframe to `j−nums[j]` grouping; condition easy to misread |
| Count Number of Nice Subarrays | 1623 | 3×2=6 | `atMost(k)−atMost(k−1)` reframe |
| Maximum Beauty of an Array | 1638 | 2×3=6 | statement says "subsequence" → misdirects; real move is sort + window |
| Maximum Matrix Sum | 1648 | 3×2=6 | sign-flip parity invariant (count negatives, track min abs) |
| Last Moment Before All Ants Fall | 1618 | 3×2=6 | the "ants pass through = ignore each other" aha |

### Sequencing
1. Install 1-2 **Set A** primitives you've genuinely never *derived* (study OK).
2. Then alternate, leaning into **Set B** (the real derivation engine, solved cold).
3. Graduation count (3 more to reach 10) is satisfied by Set A; Set B continues as depth training beyond graduation.
