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

---

| Field | Value |
|-------|-------|
| Date | 2026-05-20 |
| Link | https://leetcode.com/problems/minimum-cost-to-make-two-binary-strings-equal/description/ |
| Rating | 1840 |
| AC | Y |
| Time | 80min |
| Pattern | Greedy / Counting — pair mismatches by type, minimize cost per pair |
| Revision due | 2026-06-03 |
| Remark | Key: classify (0,1) vs (1,0) mismatches; needed 3 candidates — flip-all, swap+cross+swap, swap+flip — hybrid case was the missing piece |

---

| Field | Value |
|-------|-------|
| Date | 2026-05-20 |
| Link | https://leetcode.com/problems/find-maximum-value-in-a-constrained-sequence/ |
| Rating | 1832 |
| AC | N (derived ~80%, final approach understood via Socratic walkthrough — not self-derived) |
| Time | ~80min |
| Pattern | Slope constraint between neighbors → two-pass min propagation (Candy / Trapping Rain Water family) |
| Revision due | 2026-06-03 |
| Remark | Derived forward bound + suffix-right reachability, but assumed only immediate-right restriction matters — wrong when later cap is tighter than earlier. Fix: min over ALL future restrictions, or equivalently two-pass (forward + backward) min propagation. Trigger: `|a[i]-a[i+1]|≤d` → two passes, take min |

---

| Field | Value |
|-------|-------|
| Date | 2026-05-20 |
| Link | https://leetcode.com/problems/maximum-score-after-binary-swaps/description/ |
| Rating | 1823 |
| AC | Y |
| Time | 25min |
| Pattern | Regret-based greedy — max-heap, push all, pop max at each '1' |
| Revision due | 2026-06-03 |
| Remark | Swap moves '1' LEFT → i-th '1' must end at q_i ≤ p_i. Max-heap holds "still available" values; popping at each '1' picks best remaining. Pops don't form literal assignment but sum is realizable by exchange. Family: IPO, Course Schedule III, Max Performance of a Team |
