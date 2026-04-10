> [!info] You never fetch all 50 million rows — you paginate. The question is how. Offset pagination is simple but breaks at scale and under concurrent writes. Cursor-based pagination is stable, index-efficient, and the correct choice for any feed or infinite scroll at scale.

## The naive approach

You're building Twitter. A user opens their feed — 50 million tweets in the database. You don't send all 50 million. You send 100 at a time. That's pagination.

The simplest SQL way to do this:

```sql
-- Page 1
SELECT * FROM tweets ORDER BY created_at DESC LIMIT 100 OFFSET 0

-- Page 2
SELECT * FROM tweets ORDER BY created_at DESC LIMIT 100 OFFSET 100

-- Page 3
SELECT * FROM tweets ORDER BY created_at DESC LIMIT 100 OFFSET 200
```

`LIMIT` says how many rows to return. `OFFSET` says how many rows to skip first. Simple, readable, works immediately.

---

## Problem 1 — Full scan at large offsets

OFFSET doesn't mean "start from row N." It means "scan from the beginning, count N rows, throw them away, then return the next batch."

```
OFFSET 50,000:
→ DB scans rows 1 through 50,000
→ Discards all 50,000
→ Returns rows 50,001 to 50,100
→ 50,000 rows of wasted work, every single request
```

You might think the B+ tree index on `created_at` saves you here — the index has tweets sorted by timestamp, so surely the DB can just jump directly to position 50,001?

No. The index stores values in sorted order, but it does not store position numbers. There is no entry in the index that says "this is row number 50,001." The DB has to start at the top of the index and count through 50,000 entries one by one before it knows where to begin returning results.

```
Index (sorted by created_at DESC):
  entry 1     → tweet at T=1000  → row pointer
  entry 2     → tweet at T=999   → row pointer
  entry 3     → tweet at T=998   → row pointer
  ...
  entry 50,001 → tweet at T=500  → row pointer ← this is what you want

OFFSET 50,000:
→ start at entry 1
→ count... 1, 2, 3 ... 49,999, 50,000  (all thrown away)
→ now return entry 50,001 onwards
```

Think of it like a book with no page numbers. To get to chapter 50 you have to flip through chapters 1 to 49 first. You cannot skip.

At page 1 — fine. At page 500 with OFFSET 50,000 — the DB is doing this massive count on every single request. Under load, this hammers the database.

Most users won't scroll to page 500 — true. But at scale, even a small percentage of users doing deep pagination creates serious DB load.

---

## Problem 2 — Pagination instability

This one affects even page 1 and page 2, and it's the more insidious problem.

Imagine you fetch page 1 of Twitter's feed — tweets ranked 1 to 100 by recency. While you're reading, 10 new tweets get posted. You scroll down, page 2 is fetched with OFFSET 100.

```
Page 1 fetched:     tweets at positions 1-100  (you read these)
10 new tweets arrive → everything shifts down by 10 positions
Page 2 fetched:     OFFSET 100 → now returns tweets at positions 91-190

Result: tweets at positions 91-100 appear on BOTH page 1 and page 2
→ User sees duplicates
```

The reverse also happens — if tweets are deleted between page fetches, some tweets shift up and get skipped entirely. They never appear on any page.

```
Page 1 fetched:  tweets 1-100
5 tweets deleted → everything shifts up by 5
Page 2 fetched:  OFFSET 100 → starts at what was position 105
→ tweets 101-104 are never shown to the user
```

This is **pagination instability** — the result set shifts under you as data changes concurrently. OFFSET is a position in a moving list, not an anchor to a specific row.

---

## When offset is acceptable

Despite its problems, offset pagination is fine when:

- The dataset is small (a few thousand rows at most)
- Writes are infrequent — the list doesn't shift much between page fetches
- **You need page number navigation** ("jump to page 50")

Admin panels, internal tools, search results with small result sets — offset is perfectly reasonable here. The instability and scan cost only matter at scale.

> [!danger] Never use offset pagination for feeds or timelines at scale
> The combination of full scans at depth and instability under concurrent writes makes it the wrong tool for any user-facing feed with frequent writes and deep scrolling.
