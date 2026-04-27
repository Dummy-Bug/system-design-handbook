# Zerotrac Log

Append-only. One row per problem. Update day+7 column when re-solve happens.

## How to use

- **Date:** when you first solved (or attempted)
- **Problem:** title or LC #
- **Rating:** zerotrac rating
- **AC <30min:** Y / N (no editorial used, solved within 30 min cap)
- **Day+7 re-solve:** Y / N / — (— means not yet 7 days)
- **Pattern:** 1-2 word tag (sliding window, monotonic stack, dp-knapsack, etc.)
- **Stuck on:** if N — what was the missing insight

## Graduation check

Look at **rolling last 10** in current range:
- AC <30min: ≥7/10 ✓
- Day+7 re-solve: ≥7/10 ✓
- **Both** clear → bump range +50

---

## Range 1450-1500 (started: 2026-04-27)

| # | Date | Problem | Rating | AC <30min | Day+7 re-solve | Pattern | Stuck on |
|---|------|---------|--------|-----------|----------------|---------|----------|
| 1 | 2026-04-27 | Minimum Operations to Reach Target Array | 1492 | Y | — (due 2026-05-04) | ad-hoc / set-dedupe | — |
| 2 | 2026-04-27 | Minimum Distance Between Three Equal Elements II | 1450-1500 | N (32 min) | — (due 2026-05-04) | math-reduction / greedy-on-indices | Java: new Deque<>() doesn't compile (interface), getOrDefault syntax rusty |
| 3 |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |
| 6 |  |  |  |  |  |  |  |
| 7 |  |  |  |  |  |  |  |
| 8 |  |  |  |  |  |  |  |
| 9 |  |  |  |  |  |  |  |
| 10 |  |  |  |  |  |  |  |

**Last-10 check:** AC __/10 · Day+7 __/10 · Decision: stay / bump

---

## Range 1500-1550 (started: ___)

| # | Date | Problem | Rating | AC <30min | Day+7 re-solve | Pattern | Stuck on |
|---|------|---------|--------|-----------|----------------|---------|----------|
| 1 |  |  |  |  |  |  |  |

---

## Pattern frequency tally

Update monthly. Which patterns keep beating you?

| Pattern | Times encountered | Times AC'd cold | Failure rate |
|---------|-------------------|-----------------|--------------|
|  |  |  |  |
