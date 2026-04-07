# Offset Pagination

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

This bypasses the B+ tree index entirely for the skipped rows. The index can find where to start, but the DB still has to traverse 50,000 index entries just to count them before it can begin returning results.

At page 1 — fine. At page 500 with OFFSET 50,000 — the DB is doing a massive scan on every request. Under load, this hammers the database.

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
- You need page number navigation ("jump to page 50")

Admin panels, internal tools, search results with small result sets — offset is perfectly reasonable here. The instability and scan cost only matter at scale.

> [!danger] Never use offset pagination for feeds or timelines at scale
> The combination of full scans at depth and instability under concurrent writes makes it the wrong tool for any user-facing feed with frequent writes and deep scrolling.
