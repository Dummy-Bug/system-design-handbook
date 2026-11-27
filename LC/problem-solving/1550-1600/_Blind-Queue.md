**Spoiler file. Do not open.** Claude deals from it, one bare link per next, top to bottom.

Built 2026-11-25 at the user's request, so a deal takes no lookup. Every rating was checked in `zerotrac-data/ratings.tsv` (all 1550-1599), and every unseen slug was checked absent from `problem-solving/`, `contest/`, `DP/`, `concepts/` and `reflexes/`. The order alternates unseen and old and never repeats a mechanic back to back. Unseen problems come least-covered mechanic first, from the coverage table in `contest/Mock/mock-contest.md`. Old ones come weakest first, as in `LC/CLAUDE.md`. Mark a row dealt with the date when it is handed out.

| #  | Kind   | Slug                                                             | ID   | Rating | Mechanic (from the editorial)       | Dealt      |
| -- | ------ | ---------------------------------------------------------------- | ---- | -----: | ----------------------------------- | ---------- |
| 1  | unseen | card-flipping-game                                               | 822  |   1594 | hash table: set of same-both-sides  | 2026-11-25 |
| 2  | old 06 | maximum-sum-of-three-numbers-divisible-by-three                  | 3780 |   1585 | math: remainder buckets + greedy    |            |
| 3  | unseen | shortest-distance-after-road-addition-queries-i                  | 3243 |   1568 | BFS per query                       | 2026-11-25 |
| 4  | old 12 | groups-of-special-equivalent-strings                             | 893  |   1590 | hash table + sorting: canonical key |            |
| 5  | unseen | decrease-elements-to-make-array-zigzag                           | 1144 |   1559 | enumeration: try even, try odd      | 2026-11-26 |
| 6  | old 15 | construct-binary-search-tree-from-preorder-traversal             | 1008 |   1563 | stack / tree                        |            |
| 7  | unseen | hand-of-straights                                                | 846  |   1565 | hash table counting + sorting       |            |
| 8  | old 11 | the-k-th-lexicographical-string-of-all-happy-strings-of-length-n | 1415 |   1576 | backtracking                        |            |
| 9  | unseen | coloring-a-border                                                | 1034 |   1579 | DFS / BFS on a grid                 |            |
| 10 | old 40 | maximize-number-of-subsequences-in-a-string                      | 2207 |   1550 | greedy + combinatorics              |            |

> [!warning] Old 06 has had its idea given away
> greatest-sum-divisible-by-three (1762) was dealt by mistake on 2026-11-24 and explained step by step, and it uses the same remainder idea; `concepts/Maths/01-modular-arithmetic.md` teaches it too. Its re-solve measures speed of recall, not derivation.
