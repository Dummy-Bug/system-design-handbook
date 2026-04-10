# Views, Materialized Views & Stored Procedures

---

## The Problem — Query Duplication

You're building a reporting dashboard for Twitter. The analytics team runs this query every day to find the most active users:

```sql
SELECT users.username, COUNT(tweets.tweet_id) as tweet_count
FROM users
JOIN tweets ON users.user_id = tweets.user_id
GROUP BY users.username
ORDER BY tweet_count DESC
```

Five different API endpoints need this same join. Three analysts copy-paste it daily, each slightly differently. One forgets the GROUP BY. Another joins the wrong table. Now you have five versions of "the same query" returning different numbers.

This is query duplication — the same problem as data duplication, but in SQL. The fix is the same idea: define it once, reuse it everywhere.

---

## Views — Save the Query, Not the Data

A **View** is a saved query that looks and behaves like a table. You define it once in the database, and anyone can query it by name.

```sql
CREATE VIEW active_users AS
SELECT users.username, COUNT(tweets.tweet_id) as tweet_count
FROM users
JOIN tweets ON users.user_id = tweets.user_id
GROUP BY users.username
ORDER BY tweet_count DESC;
```

Now anyone who needs this just does:

```sql
SELECT * FROM active_users;
```

No joins, no GROUP BY, no room for mistakes. They query `active_users` like it's a table — they don't need to know or care what's underneath.

**How it's stored inside the database:**

The database stores only the query definition in its internal catalog — no rows, no data, nothing computed:

```
View name:   active_users
Definition:  SELECT users.username, COUNT(tweets.tweet_id)...
             FROM users JOIN tweets...
```

When someone queries the view:

```
SELECT * FROM active_users
→ DB looks up the definition
→ runs the full JOIN + GROUP BY on live data at that moment
→ returns the result
→ result is discarded — nothing stored
```

Next query — same thing again from scratch.

```
✓ query reuse     — write once, use everywhere
✓ simplicity      — hide complex joins behind a simple name
✓ always fresh    — runs against live data every time
✗ no performance gain — full query re-runs on every request
✗ no caching      — result thrown away after each query
```

> [!info] **View** — a saved query stored in the database. Looks like a table. The underlying query runs fresh every time it's queried. No data is stored — just the definition.

---

## Materialized Views — Store the Result

A regular view re-runs the full query every time. If 100 people query `active_users` simultaneously, the complex join runs 100 times in parallel — expensive.

The fix: run the query once, store the result on disk, serve everyone from the stored result.

That's a **Materialized View**.

```
Regular View:
  Query → run JOIN + GROUP BY → return result → discard
  Query → run JOIN + GROUP BY → return result → discard  (every time, from scratch)

Materialized View:
  First query → run JOIN + GROUP BY → store result on disk
  Next query  → read from stored result → return instantly ✓
  Next query  → read from stored result → return instantly ✓
```

Reading from stored data is just a simple table scan — no joins, no aggregations, just fetch rows. Much faster.

**The freshness problem:**

Tweet counts change every second. The moment you store the result, it starts going stale. New tweets come in — the materialized view still shows old counts.

The fix is a **scheduled refresh** — re-run the full query on a schedule and overwrite the stored result:

```
Every 1 hour → re-run query → overwrite stored result
→ data is at most 1 hour stale
```

How often you refresh depends on how stale you can tolerate:

```
Analytics dashboard   → 1 hour stale is fine   → refresh every hour
Leaderboard           → 1 min stale is fine     → refresh every minute
Live tweet counts     → any stale = wrong       → don't use materialized view
```

Some databases also support **incremental refresh** — instead of recomputing everything, only update the rows that changed since the last refresh. Faster but more complex to implement.

```
✓ fast reads      — stored on disk, no joins at query time
✓ less DB load    — complex query runs once, not on every request
✗ stale data      — result is always slightly behind live tables
✗ storage cost    — result set stored on disk
```

> [!info] **Materialized View** — a view whose result is precomputed and stored on disk. Reads are instant. Refreshed on a schedule — data is stale between refreshes.

> [!important] A materialized view trades freshness for speed. If your use case needs real-time accuracy — use a regular view or query the table directly. If your use case tolerates some staleness — materialized view is a big performance win.

---

## Views vs Materialized Views

```
Regular View         → query saved, result computed fresh every time
                       ✓ always fresh   ✗ slow, full query runs each time

Materialized View    → result stored on disk, refreshed on schedule
                       ✓ fast reads     ✗ stale between refreshes
```

Use regular views for: simplifying complex queries, hiding joins from application code.
Use materialized views for: expensive aggregations queried frequently, dashboards, reports where slight staleness is acceptable.

---

## Stored Procedures — Logic Inside the Database

A stored procedure is different from a view. A view is purely for reading data. A stored procedure is more like a function inside the database — it can take parameters, run business logic, and modify data.

```sql
CREATE PROCEDURE transfer_money(from_id INT, to_id INT, amount DECIMAL)
BEGIN
  UPDATE accounts SET balance = balance - amount WHERE id = from_id;
  UPDATE accounts SET balance = balance + amount WHERE id = to_id;
END;
```

Call it like:

```sql
CALL transfer_money(1, 2, 100);
```

```
View              → saved SELECT query, returns data, read only
Stored Procedure  → saved block of code, can INSERT/UPDATE/DELETE, has logic
```

> [!tip] Stored procedures are rarely used in modern system design. Most companies keep business logic in application code — easier to test, version control, and deploy. Stored procedures are harder to debug and tie your logic to a specific database. Worth knowing the difference, but don't deep dive them in interviews.
