Before databases existed, people stored data in flat files — CSVs, text files. It works fine for a handful of records. But imagine you're building Instagram and you store 100 million users in a CSV:

```
1, Alice, alice@gmail.com, 28
2, Bob, bob@gmail.com, 34
...
100,000,000 rows
```

Someone tries to log in with `alice@gmail.com`. How do you find her?

You write code that scans every row top to bottom — **linear search**. At 100 million rows, that's slow. You might think "split it into multiple files and search in parallel" — but then you don't know which file Alice is in, so you still have to search all of them every time.

This is exactly the problem databases were invented to solve. Two things they give you that raw files don't:

```
1. Indexes  → a separate lookup structure so you can find data without scanning everything
             "Alice is in file 3, row 47" → go straight there

2. Schema   → enforced rules on every write
             id must be integer, email must be unique, age cannot be null
             → bad data rejected before it gets stored
```

> [!info] A database is a smarter, more organised way to store and retrieve data — with built-in mechanisms for finding records fast and keeping data clean.

---

## Structured vs Semi-Structured vs Unstructured Data

Not all data looks the same. Before you pick a database, you need to know what kind of data you're storing.

### Structured Data

Fits neatly into rows and columns. Every record has the same fields, same types, same shape.

```
Users table:
| id  | name    | email             | age |
|-----|---------|-------------------|-----|
| 1   | Alice   | alice@gmail.com   | 28  |
| 2   | Bob     | bob@gmail.com     | 34  |
```

Every row is identical in structure. You know exactly what fields exist and what type each field is. SQL databases (PostgreSQL, MySQL) are built for this.

### Semi-Structured Data

Has some structure, but it's flexible — not every record needs the same fields.

```json
{ "id": 1, "name": "Alice", "age": 28 }
{ "id": 2, "name": "Bob", "address": { "city": "London", "zip": "E1 6RF" } }
{ "id": 3, "name": "Charlie", "tags": ["premium", "verified"] }
```

Alice has no address. Bob has a nested object. Charlie has an array. In a SQL table this would require nullable columns for everything, or a messy set of separate tables. Document databases (MongoDB) are built for this shape.

### Unstructured Data

No fixed schema at all. Can't fit in a table.

```
A video file       → just bytes, no fields
A PDF document     → free-form text + images
An audio recording → raw audio signal
An image           → pixels
```

You store this in **blob/object storage** (S3, Google Cloud Storage) — not in a traditional database. The database just stores a *pointer* (a URL) to where the file lives.

> [!important] The moment you decide what data you're storing, you're already narrowing your database choice.
> ```
> Structured, relational data    → SQL (PostgreSQL, MySQL)
> Flexible/nested documents      → Document store (MongoDB)
> Raw files (videos, images)     → Blob storage (S3)
> ```

---

## Schema-on-Write vs Schema-on-Read

### Schema-on-Write (SQL)

You define the structure **before** writing any data. Every row must conform. The database enforces it.

```sql
CREATE TABLE users (
  id    INTEGER NOT NULL,
  name  VARCHAR(255),
  email VARCHAR(255) UNIQUE NOT NULL,
  age   INTEGER
);
```

Now try inserting `age = "twenty two"` — the database rejects it immediately.

**The problem with fast-moving products:**

What if product wants to add a new field every week?

```
Week 1 → add "address" column     → 100M rows get null
Week 2 → add "phone" column       → 100M rows get null
Week 3 → remove "age" column      → migration needed
Week 4 → split "address" into     → complex migration
          city, zip, country
```

Every change touches every row. At 100 million users, migrations take time, can lock the table, and carry risk.

### Schema-on-Read (MongoDB)

You just store the data in, whatever shape it is. The structure is only interpreted when you read it.

Real example — Instagram Stories. Every story type is different:

```json
{ "type": "photo", "image_url": "img.jpg", "duration": 5 }
{ "type": "video", "video_url": "vid.mp4", "thumbnail": "thumb.jpg" }
{ "type": "poll",  "question": "Best?", "options": ["cats", "dogs"] }
```

No nulls. Each document only has the fields it needs. New story type tomorrow? Just start writing it — no table migration required.

Compare this to forcing it into a SQL table:

```
| id | image_url | video_url | thumbnail | question | option_a | option_b |
|----|-----------|-----------|-----------|----------|----------|----------|
| 1  | img.jpg   | null      | null      | null     | null     | null     |
| 2  | null      | vid.mp4   | thumb.jpg | null     | null     | null     |
| 3  | null      | null      | null      | "Best?"  | "cats"   | "dogs"   |
```

Mostly nulls. Messy. And every new story type means altering the table.

> [!info] The simple way to remember it:
> ```
> Schema-on-write → structure enforced BEFORE data goes in  → SQL
> Schema-on-read  → structure interpreted WHEN data comes out → MongoDB
> ```

> [!important] Schema-on-write is safer — bad data is rejected at write time. Schema-on-read is flexible — but bad data can sneak in and only blow up when you try to read it. You trade safety for flexibility.

---

## Row-Oriented vs Column-Oriented Storage

When a database writes your data to disk, how does it physically lay it out? This decision has a massive impact on performance depending on what you're doing.

### Row-Oriented Storage

Stores data **row by row** on disk:

```
[1, Alice, alice@gmail.com, 28, London]
[2, Bob, bob@gmail.com, 34, New York]
[3, Charlie, charlie@..., 22, London]
```

When Instagram loads Alice's full profile — name, email, age, city all at once — one disk read gets you everything. Fast and it will also fetch other rows that are present inside that disk block.

**Use for:** individual record reads and writes — user profiles, orders, transactions.

**Examples:** PostgreSQL, MySQL, SQLite.

### Column-Oriented Storage

Stores data **column by column** on disk:

```
ids:    [1, 2, 3, ...]
names:  [Alice, Bob, Charlie, ...]
emails: [alice@..., bob@..., charlie@..., ...]
ages:   [28, 34, 22, ...]
cities: [London, New York, London, ...]
```

Now the data team wants: **"What is the average age of all 100 million users?"**

With row-oriented storage, you'd read every single row — loading name, email, city, all data you don't need — just to get to the age column. Massive wasted I/O.

With column-oriented storage, you read just the ages column. Nothing else is touched.

**Use for:** aggregations across many rows — analytics, reports, dashboards.

**Examples:** Amazon Redshift, Google BigQuery, Snowflake.

> [!info] The trade-off:
> ```
> Row-oriented    → fast for reading/writing individual records
>                 → your production database (PostgreSQL, MySQL)
>
> Column-oriented → fast for aggregations across millions of rows
>                 → your analytics database (Redshift, BigQuery)
> ```

> [!danger] Never run heavy analytics queries (GROUP BY, COUNT, SUM across millions of rows) against your production row-oriented database. Full table scans compete with live traffic → latency spikes → real users get slow responses. Analytics data belongs in a separate column-oriented store.

---

## Never Store Money as a Float

This comes up in every financial system design — payment platforms, auctions, stock brokers, banking ledgers.

You might think storing a price like `$9.99` as a `float` or `double` is fine. It's not.

```
0.1 + 0.2 = 0.30000000000000004   ← actual result in IEEE 754 floating point
```

Floats can't represent decimal fractions like `0.1` exactly in binary. They store an approximation. For most use cases that's fine — but for money, tiny rounding errors compound across millions of transactions and you end up with ledgers that don't balance.

**The fix — two options:**

```
Option 1 — Store as integer (cents)
  $9.99  → store as 999
  $0.10  → store as 10
  No decimals, no floating point, no rounding errors ✓

Option 2 — Use DECIMAL/NUMERIC type
  DECIMAL(10, 2) → stores exactly 2 decimal places
  Slower than integer but readable as a real price ✓
```

> [!danger] Never use `float` or `double` for money, prices, or any financial value. The rounding error is invisible in testing and catastrophic in production at scale.

> [!important] Applies directly to: Payment System, Banking Ledger, Online Auction, Stock Broker case studies. Any time you're designing a schema for a financial system, this is the first thing to get right.

For the full explanation of why binary floating point fails and how IEEE 754 works under the hood, see: `[[Fundamentals/Binary Number Rounding.md]]`

---

## Summary

```
Problem with files       → no fast lookup, no data validation
Databases give you       → indexes (fast lookup) + schema (data rules)

Structured data          → SQL (rows and columns, fixed schema)
Semi-structured data     → Document store (MongoDB, flexible shape)
Unstructured data        → Blob storage (S3, just store the file)

Schema-on-write          → rules enforced on write, safe, SQL
Schema-on-read           → rules interpreted on read, flexible, MongoDB

Row-oriented             → fast per-record reads, production DBs
Column-oriented          → fast aggregations, analytics DBs

Money storage            → never float/double → use integer (cents) or DECIMAL
```
