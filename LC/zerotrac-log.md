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

---

| Field | Value |
|-------|-------|
| Date | 2026-05-21 |
| Link | — (Lex smallest array, |·| = permutation, sum = target) |
| Rating | ~1830 |
| AC | N (hinted — could not derive greedy-from-top reframe) |
| Time | stuck → hints from LC |
| Pattern | Greedy flip on `{1..n}` — pick largest values that fit `D = S − target` |
| Revision due | 2026-06-04 |
| Remark | Reframe: pick subset of `{1..n}` summing to `D/2` to flip. Greedy from `n` down always works because `{1..n}` subset sums have no gaps in `[0, S]`. Lex smallest = flip largest values (most-negative first elements dominate). Trigger: "permutation magnitudes + sign choices + target sum" |

---

| Field | Value |
|-------|-------|
| Date | 2026-05-21 |
| Link | — (Count distinct strip-zero values, n ≤ 10^15) |
| Rating | ~1800 |
| AC | N (reframe came from discussion; walk self-driven once reframe was clear) |
| Time | stuck → reframed via walkthrough |
| Pattern | Image reframing + digit counting (digit-walk template, no memo) |
| Revision due | 2026-06-04 |
| Remark | Image of strip0 = {no-zero positive integers ≤ n}. Count via digit walk: Part A = Σ 9^d for d<L, Part B = walk n's digits, at each pos contribute (d_i−1)×9^(L−1−i); walk dies on 0-digit; +1 for n if no-zero. Trigger: "count over [1,n] with n ≥ 10^9 and digit-dependent property" → digit walk |
