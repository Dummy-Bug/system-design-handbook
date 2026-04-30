# Zerotrac Log

## Graduation check

Rolling last 10 in current range — both must clear independently:
- AC <30min: ≥7/10
- Day+7 re-solve: ≥7/10

---

## Range 1450-1500 (started: 2026-04-26)

**Last-10 check:** AC 3/6 · Day+7 —/6 · Decision: stay

---

### #1 — Merge Close Characters

| Field | Value |
|-------|-------|
| Date | 2026-04-26 |
| Link | https://leetcode.com/problems/merge-close-characters/ |
| Rating | 1472 |
| AC | N |
| Time | hinted |
| Pattern | build-forward / result-index-hash |
| Next rep | 2026-05-03 |
| Remark | hinted on build-forward DS; derived result-index insight solo; Java: chars.toString() returns object hash — use new String(chars) |

---

### #2 — Minimum Operations to Reach Target Array

| Field | Value |
|-------|-------|
| Date | 2026-04-27 |
| Link | https://leetcode.com/problems/minimum-operations-to-make-array-values-equal-to-k/ |
| Rating | 1492 |
| AC | Y |
| Time | <30min |
| Pattern | ad-hoc / set-dedupe |
| Next rep | 2026-05-04 |
| Remark | clean solve |

---

### #3 — Minimum Distance Between Three Equal Elements II

| Field | Value |
|-------|-------|
| Date | 2026-04-27 |
| Link | https://leetcode.com/problems/minimum-distance-to-the-target-element/ |
| Rating | 1450 |
| AC | N |
| Time | 32min |
| Pattern | math-reduction / greedy-on-indices |
| Next rep | 2026-05-04 |
| Remark | Java syntax gaps: new Deque<>() doesn't compile (interface), getOrDefault syntax rusty |

---

### #4 — Maximum Alternating Sum of Squares

| Field | Value |
|-------|-------|
| Date | 2026-04-28 |
| Link | https://leetcode.com/problems/maximum-alternating-sum-of-a-subarray/ |
| Rating | 1455 |
| AC | Y |
| Time | <30min |
| Pattern | greedy-abs-sort |
| Next rep | 2026-05-05 |
| Remark | AC but missed O(n): counting-sort (bounded K=4×10⁴) and quickselect (unbounded K) both viable |

---

### #5 — Longest Balanced Substring

| Field | Value |
|-------|-------|
| Date | 2026-04-28 |
| Link | https://leetcode.com/problems/longest-balanced-substring/ |
| Rating | 1490 |
| AC | N |
| Time | 2×30min upsolve |
| Pattern | O(n²) brute-force / min==max-freq |
| Next rep | 2026-05-06 |
| Remark | used minValue*distinct as the answer instead of as the condition; fix: if (min==max) → balanced, length = j-i+1; maxValue declared outside j-loop (scope bug) |

---

### #6 — Longest Balanced Subarray I

| Field | Value |
|-------|-------|
| Date | 2026-04-30 |
| Link | https://leetcode.com/problems/longest-balanced-subarray-i/description/ |
| Rating | 1467 |
| AC | Y |
| Time | 18min |
| Pattern | O(n²) brute-force / even-odd distinct sets |
| Next rep | 2026-05-07 |
| Remark | clean derive; !set.contains() before add() is redundant — HashSet ignores duplicates automatically |

---

### #7 — Longest Subsequence With Non-Zero Bitwise XOR

| Field | Value |
|-------|-------|
| Date | 2026-04-30 |
| Link | https://leetcode.com/problems/longest-subsequence-with-non-zero-bitwise-xor/description/ |
| Rating | 1489 |
| AC | N |
| Time | 40min+ |
| Pattern | XOR property / whole-array XOR check |
| Next rep | 2026-05-07 |
| Remark | started with set+XOR tracking approach (wrong — broke on repeated elements); insight clicked while writing stuck note (rubber duck): if total XOR==0 → remove one non-zero element → n-1; if total XOR!=0 → n; edge case: all zeros → return 0 |

---

### #8

*(empty)*

---

### #9

*(empty)*

---

### #10

*(empty)*

---

## Range 1500-1550 (started: ___)

*(not started)*

---

## Pattern frequency tally

Update monthly.

| Pattern | Times encountered | Times AC'd cold | Failure rate |
|---------|-------------------|-----------------|--------------|
| brute-force / two-set | 2 | 1 | 50% |
| math-reduction / greedy | 1 | 0 | 100% |
| build-forward | 1 | 0 | 100% |
