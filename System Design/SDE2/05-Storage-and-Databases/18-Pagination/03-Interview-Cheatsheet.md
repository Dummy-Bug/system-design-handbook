## The two approaches

```
Offset:  SELECT * FROM tweets ORDER BY id DESC LIMIT 100 OFFSET N

Cursor:  SELECT * FROM tweets WHERE id < cursor ORDER BY id DESC LIMIT 100
```

---

> [!question] Why is OFFSET pagination a problem at scale?

> [!success]-
> Two problems:
>
> **1. Full scan at large offsets** — OFFSET N means scan and discard N rows before returning results. At OFFSET 50,000, the DB scans 50,000 rows per request. Bypasses index efficiency entirely for the skipped rows. Gets worse the deeper users scroll.
>
> **2. Pagination instability** — OFFSET is a position in a moving list. If 10 new tweets arrive between page 1 and page 2, everything shifts by 10. OFFSET 100 now returns tweets 91-190 — tweets 91-100 appear on both pages (duplicates). Deletions cause tweets to be skipped entirely.
>
> > [!tip] Interview framing
> > "OFFSET pagination has two issues — it degrades to a full scan at depth, and it's unstable under concurrent writes. New inserts shift the result set, causing duplicates across pages."

---

> [!question] How does cursor-based pagination work and why is it better?

> [!success]-
> Instead of skipping N rows, you anchor to the last row you returned — its ID becomes the cursor. The next page query is WHERE id < cursor LIMIT 100.
>
> This uses the B+ tree index to jump directly to the cursor position — O(log n) at any depth, identical performance whether you're on page 1 or page 5000.
>
> It's stable because new inserts have higher IDs than your cursor — they don't shift anything below it. Deletions don't affect positions either.
>
> Trade-off: no random page access. You can only navigate next/previous — you need page N's cursor to fetch page N+1.
>
> > [!tip] Interview framing
> > "Cursor pagination anchors to a specific row ID. WHERE id < cursor LIMIT 100 — O(log n) via index at any depth, stable under concurrent writes. The trade-off is no random page access — only next/previous navigation."

---

## Decision map

```
Use case                              → Pagination type
──────────────────────────────────────────────────────
Twitter/Instagram feed, infinite scroll → Cursor-based
Chat message history                  → Cursor-based
Large dataset, frequent writes        → Cursor-based
Admin panel, small dataset            → Offset (acceptable)
Page number UI, infrequent writes     → Offset (acceptable)
Search results with jump-to-page      → Offset (acceptable, keep dataset small)
```

---

## SQL comparison

```sql
-- Offset (page 500, 50,000 rows scanned and discarded)
SELECT * FROM tweets ORDER BY id DESC LIMIT 100 OFFSET 50000

-- Cursor (jumps directly to id=9900, reads 100 rows)
SELECT * FROM tweets WHERE id < 9900 ORDER BY id DESC LIMIT 100
```

---

## Key facts

- Cursor = ID (or timestamp, or composite) of the last item on the current page
- Each page response includes the next cursor — client stores and sends it with the next request
- Cursor can be any unique ordered column — doesn't have to be the primary key
- Composite cursor `(created_at, id)` handles ties when multiple rows share the same timestamp
