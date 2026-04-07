# Pagination — Overview

> [!info] You never fetch all 50 million rows — you paginate. The question is how. Offset pagination is simple but breaks at scale and under concurrent writes. Cursor-based pagination is stable, index-efficient, and the correct choice for any feed or infinite scroll at scale.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Offset-Pagination.md | How OFFSET works, the full scan problem, pagination instability |
| 02-Cursor-Pagination.md | Cursor-based approach, how it uses indexes, the trade-off |
| 03-Interview-Cheatsheet.md | Quick reference for revision |

---

## The one-line model

```
Offset pagination   → LIMIT 100 OFFSET N  → simple, unstable, slow at large N
Cursor pagination   → WHERE id < cursor LIMIT 100  → stable, O(1) with index, next/prev only
```

---

## When to use which

```
Infinite scroll, feeds, timelines          → cursor-based
Page numbers, jump to page N              → offset (only for small datasets, infrequent writes)
Admin UIs, small datasets                 → offset is fine
```
