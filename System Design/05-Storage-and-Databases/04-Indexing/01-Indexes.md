## The Problem — Full Table Scan

You have a users table with 100 million rows. Someone runs:

```sql
SELECT * FROM users WHERE email = 'alice@gmail.com';
```

How does the database find Alice? It goes through every single row, checks the email column, and moves on if it doesn't match. That's a **full table scan** — O(n).

```
100 million rows → up to 100 million comparisons in the worst case
Alice might be the very last row
```

At Instagram scale — millions of logins per second — that's millions of full table scans running simultaneously. The database collapses.

Think of a phone book with 100 million names. You don't read from page 1 to find "Alice" — you open the middle, decide left or right, keep halving. Binary search. You find Alice in ~27 steps instead of 100 million.

```
Full table scan  → O(n)      → up to 100,000,000 comparisons
Binary search    → O(log n)  → up to 27 comparisons  (log₂ of 100M ≈ 27)
```

That's the idea behind a database **index**.

---

## What an Index Is

An index is a separate data structure stored alongside your table. It keeps column values sorted and maps each value to the actual row location — so the database can binary search instead of scanning.

```sql
CREATE INDEX idx_users_email ON users(email);
```

The database builds a sorted structure of all email values:

```
Index on email (sorted alphabetically):
  aaron@gmail.com  → row 12,445,231
  alice@gmail.com  → row 4,521,847   ← target
  bob@gmail.com    → row 892,341
  charlie@...      → row 67,234,901
```

Binary search works on strings too — strings have alphabetical ordering, just like numbers have numeric ordering. The database compares alphabetically: does `alice` come before or after the middle entry? Go left or right. Repeat. Found in ~27 steps.

```
WHERE email = 'alice@gmail.com'
→ binary search index → found at row 4,521,847 → fetch that row
→ 27 comparisons instead of 100 million ✓
```

The underlying data structure databases use is called a **B+ Tree** — a sorted tree that makes both exact lookups and range queries fast.

---

## The Cost of Indexes

Indexes aren't free. Two costs:

**1. Storage** — the index is a separate data structure stored on disk alongside the table. More indexes = more disk usage.

**2. Write overhead** — every INSERT, UPDATE, DELETE must also update every index to keep it in sync:

```
No index:
  INSERT → write one row to table → done ✓

With 5 indexes:
  INSERT → write row + update 5 indexes → 6 write operations ✗
```

The more indexes, the slower your writes.

---

## When NOT to Index

**Write-heavy tables** — if a table is constantly being written to, every write updates all indexes. The write overhead outweighs the read benefit.

**Low cardinality columns** — cardinality means number of distinct values relative to total rows.

```
High cardinality → index helps
  email     → 100M users, 100M unique values → index finds 1 row ✓
  user_id   → 100M users, 100M unique values → index finds 1 row ✓

Low cardinality → index useless
  gender    → 100M users, 3 distinct values  → index finds ~33M rows ✗
  is_active → 100M users, 2 distinct values  → index finds ~50M rows ✗
```

The index finds the value instantly — but then still has to fetch 33 million rows. You've done a binary search to save nothing.

---

## Composite Index

What if your query filters on two columns together?

```sql
SELECT * FROM users WHERE country = 'UK' AND age = 25;
```

You have two separate indexes — one on `country`, one on `age`. The database **picks one** — whichever narrows down rows more — and then manually checks the other condition on the remaining rows:

```
country index → finds 10M UK users
→ fetch each of those 10M rows from the table
→ check age = 25 on each one manually
→ still scanning 10M rows ✗
```

The second index is ignored. The database query planner picks one and scans the rest.

The fix is a **Composite Index** — one index built on both columns together:

```sql
CREATE INDEX idx_country_age ON users(country, age);
```

Now the index is sorted by country first, then by age within each country. Each entry still stores a row pointer — exactly like a single-column index, just with a wider key:

```
Index (country, age):
  UK, 20  → row 892,341
  UK, 24  → row 12,445,231
  UK, 25  → row 4,521,847   ← jump straight here
  UK, 25  → row 7,234,123   ← second UK-25 user, second pointer
  UK, 26  → row 67,234,901
  US, 19  → row 3,112,008
  US, 25  → row 5,892,004
```

The B+ Tree sorts on the combined key `(country, age)` instead of a single value. When the matching entries are found, the row pointers are right there — same direct fetch. One lookup finds exactly country = 'UK' AND age = 25. No scanning.

---

## The Leftmost Prefix Rule

Column order in a composite index matters — critically.

Composite index on `(country, age)` is like a phone book sorted by last name, then first name. If you want everyone named "John" — you can't use it. The book is sorted by last name first.

```
Index (country, age) can be used for:
  ✓ WHERE country = 'UK'                → country is leftmost, groups together
  ✓ WHERE country = 'UK' AND age = 25  → full composite match
  ✗ WHERE age = 25                      → skips leftmost column, index ignored
                                           age 25 users scattered across index
```

Any query that starts from the leftmost column works. Any query that skips it forces a full scan.

> [!important] Always put the most commonly filtered column first in a composite index. Design indexes around your most frequent query patterns.

---

## Covering Index

Even with an index, the database still has to fetch the actual row after finding it in the index:

```sql
SELECT email FROM users WHERE country = 'UK';
```

```
country index → finds 10M UK row pointers
→ fetch row 1 from table → read email, discard everything else
→ fetch row 2 from table → read email, discard everything else
...10 million table fetches just to read one column...
```

What if the index itself already contained the `email` column?

```sql
CREATE INDEX idx_country_email ON users(country, email);
```

```
Index (country, email):
  UK, alice@gmail.com
  UK, bob@gmail.com
  ...
```

The database finds UK users in the index — email is already right there. Zero table fetches.

This is a **Covering Index** — a composite index that includes all columns the query needs, so the actual table is never touched.

> [!info] **Covering Index** — not a separate index type. It's a composite index where you've deliberately included both the WHERE columns (for filtering) and the SELECT columns (for reading), so the query is satisfied entirely from the index. The database recognises this automatically and skips the table fetch.

```sql
-- Composite for filtering only:
CREATE INDEX idx_country_age ON users(country, age);
-- goal: fast WHERE country AND age filtering

-- Same syntax, covering intent:
CREATE INDEX idx_country_email ON users(country, email);
-- goal: SELECT email WHERE country — never touch the table
```

Most valuable when: high row count, few columns selected. Fetching millions of rows from the table just to read 1-2 columns is the worst case — covering index eliminates all those fetches.

---

```
Full table scan     → O(n), checks every row — collapses at scale

Index               → O(log n), binary search on sorted B+ Tree

Composite index     → filter on multiple columns, database picks only one without it

Leftmost prefix     → composite index only works if query starts from leftmost column

Covering index      → composite index that includes SELECT columns — zero table fetches

Low cardinality     → don't index (gender, is_active) — finds too many rows to help

Write-heavy table   → think twice — every write updates all indexes
```
