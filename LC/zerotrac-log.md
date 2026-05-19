# Zerotrac Log

---

| Field | Value |
|-------|-------|
| Date | 2026-05-19 |
| Link | https://leetcode.com/problems/minimum-generations-to-target-point |
| Rating | 1883 |
| AC | Y |
| Time | 45min |
| Pattern | BFS generation expansion — newcomer-only pair pruning |
| Revision due | 2026-06-02 |
| Remark | State space tiny (N≤20, coords 0..6 → ≤343 pts); brute force intended; off-by-one on generation counter |

---

| Field | Value |
|-------|-------|
| Date | 2026-05-19 |
| Link | — (Even Sum Subgraphs, n ≤ 13) |
| Rating | 1859 |
| AC | Y |
| Time | 46min |
| Pattern | Subset enumeration + induced subgraph connectivity (bitmask) |
| Revision due | 2026-06-02 |
| Remark | n≤13 → 2^n subsets; algo clean in 10min, bugs all in impl (ref vs copy, index vs value, wrong dimension) |

---

| Field | Value |
|-------|-------|
| Date | 2026-05-19 |
| Link | — |
| Rating | 1860 |
| AC | N (hinted) |
| Time | hinted |
| Pattern | Greedy / String — unsorted window + first/last occurrence of min/max |
| Revision due | 2026-06-02 |
| Remark | 3-op cond = lastIndexOf(max)==0 AND indexOf(min)==n-1; naive max==s[0] breaks on duplicates like "bba" |
