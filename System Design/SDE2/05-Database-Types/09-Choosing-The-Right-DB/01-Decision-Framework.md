
> [!info] The golden rule
> Start with SQL. Move away only when you have a specific reason — a scale problem, an access pattern SQL can't handle efficiently, or a data model that doesn't fit tables. Never pick a exotic database because it sounds impressive.

---

## How to think about this in an interview

Don't memorise a lookup table. Instead, ask three questions in order:

1. **What is the data shape?** — structured and relational, or flexible and nested, or just key→value?
2. **What are the access patterns?** — exact lookups, range scans, full-text search, graph traversal, analytical aggregations?
3. **What are the scale and consistency requirements?** — write-heavy, read-heavy, global, strong consistency, eventual consistency?

The answers eliminate options. What's left is your answer — and you can justify it.

---

## The 8 scenarios

---

### Scenario 1 — Instagram user accounts

**Requirements:** store username, email, bio, profile picture URL. Enforce unique email. Look up by user ID. Link to posts, comments, followers later.

**Answer: SQL (PostgreSQL)**

Structured data with a fixed schema. Unique constraint on email is a first-class SQL feature. Relationships to other entities (posts, followers) are naturally expressed with foreign keys. SQL is the safe default when data is structured and access patterns are straightforward.

> Start with SQL. Move away only when SQL can't handle your specific access pattern or scale.

**Why not others:**
- Document store — no benefit here, schema is fixed and relationships matter
- Key-value — too simple, can't query by email or enforce uniqueness
- Cassandra — overkill, no write-heavy requirement yet

---

### Scenario 2 — Instagram session tokens

**Requirements:** store token → user_id mapping. Auto-expire after 30 days. Look up on every single API request. Millions of lookups per day.

**Answer: Redis**

In-memory key-value store. O(1) lookup in microseconds — every API request is blocked waiting for this, so speed is everything. TTL is a built-in Redis primitive — `SET token abc123 EX 2592000` auto-deletes after 30 days, no cleanup job needed.

Persistence isn't needed — losing sessions just means users get logged out. The source of truth (user account) lives safely in MySQL.

**Why not DynamoDB:**
- DynamoDB also supports TTL but **expired items can linger for up to 48 hours** — a security risk for session tokens
- DynamoDB charges per read/write unit — millions of session lookups per day makes the bill painful
- DynamoDB adds a network hop to AWS infrastructure; Redis on a local instance is microseconds faster
- DynamoDB's strengths (global distribution, managed scale) don't apply to a session store

> Redis for sessions, tokens, rate limiting, caching — in-memory speed, TTL built-in, O(1) lookup. Use DynamoDB when you need globally distributed managed key-value at massive scale with complex access patterns.

---

### Scenario 3 — Amazon product catalog

**Requirements:** thousands of product types with completely different attributes. Laptops have RAM, processor, battery. T-shirts have size, color, material. Books have ISBN, author, pages. New categories added every month. Filter by any combination of attributes.

**Answer: Document Store (MongoDB)**

Flexible schema handles wildly different product shapes — a laptop document has RAM and processor fields, a t-shirt document has size and color. No ALTER TABLE, no null columns for attributes that don't apply. New product category next month? Just start writing documents with new fields.

Nested objects fit naturally — images, variants, and attributes are all embedded in one document. One read fetches everything needed to render the product page.

**Why not DynamoDB:**
- DynamoDB is optimised for known, predictable access patterns
- "Filter by any combination of 20 different attributes" is unpredictable — MongoDB's rich query engine handles this; **DynamoDB requires secondary indexes for each access pattern**, which gets painful fast

**Why not SQL:**
- Every new product category would require ALTER TABLE to add new columns
- Products with 50 different attribute types would leave most rows with mostly NULL columns — wasted storage and confusing schema

---

### Scenario 4 — WhatsApp messages

**Requirements:** 100 billion messages written per day. Each message belongs to a conversation. Only one query ever needed: "give me the last 50 messages in conversation X."

**Answer: Cassandra**

Write-heavy at massive scale — Cassandra's LSM tree write path (MemTable → SSTable) handles this without the random I/O bottleneck of B+ Tree databases.

Data model:
- **Partition key → conversation_id** — all messages for a conversation land on the same node, making reads a fast local operation
- **Clustering key → timestamp DESC** — messages sorted by time within a partition, so "last 50 messages" is a simple range scan with no sorting needed

```
Partition key  → conversation_id  (which node holds this data)
Clustering key → timestamp DESC   (sort order within that node)

Query: SELECT * FROM messages
       WHERE conversation_id = 'abc'
       ORDER BY timestamp DESC
       LIMIT 50;
→ pure index scan, no sorting, blazing fast
```

**Elimination reasoning:**
- SQL — write throughput at 100B messages/day would require massive sharding; joins not needed anyway
- Document store — schema flexibility not needed, fixed message structure
- Key-value — **can't do range scans** (last 50 messages)
- Graph DB — no relationship traversal needed
- No relationships involved, no flexible schema needed, writes dominate → Cassandra

---

### Scenario 5 — LinkedIn connections

**Requirements:** find all people within 3 degrees of connection. Check if two users share mutual connections. 900 million users, billions of connection rows.

**Answer: Graph DB (Neo4j)**

Multi-hop relationship traversal is the primary operation. SQL joins become exponentially expensive:

```sql
-- 1st degree: who do I follow?
JOIN followers WHERE user_id = me                          -- billions of rows

-- 2nd degree: who do they follow?
JOIN followers WHERE user_id IN (1st degree results)      -- billions of rows again

-- 3rd degree: who do THEY follow?
JOIN followers WHERE user_id IN (2nd degree results)      -- billions of rows again
```

Three chained joins on a billions-row table. Each join is a full scan. The query takes minutes — completely unusable for real-time "people you may know."

A Graph DB stores relationships as **first-class citizens** — edges between nodes. Traversing 3 degrees is just following pointers:

```
me → [edge] → friend → [edge] → friend's friend → [edge] → 3rd degree
```

No joins. No full table scans. Just pointer hops. O(degrees) not O(n³).

> Graph DB when relationship traversal is the primary operation and you need multi-hop queries. SQL joins become exponentially expensive beyond 2 hops at scale.

---

### Scenario 6 — YouTube videos

**Requirements:** users upload videos up to 50GB. Billions of videos total. Need to store the file and its metadata (title, description, uploader, view count, duration).

**Answer: S3 (Blob Storage) + SQL**

Never store large binary files inside a database. S3 is built for exactly this — flat namespace, buckets, keys, scales to exabytes, cheap storage, CDN integration for fast global delivery.

SQL for metadata — video title, description, uploader_id, view_count, uploaded_at, duration are all structured with clear relationships (video belongs to user, has many comments, belongs to many categories). Foreign keys, joins, and constraints apply naturally.

```
S3:   stores the actual video bytes (flat file, addressed by key)
SQL:  stores everything you need to find, display, and manage those bytes
```

These two always go together. S3 stores the bytes, PostgreSQL stores the metadata.

---

### Scenario 7 — Google Docs global editing

**Requirements:** users globally (India, US, Europe) edit documents simultaneously. Strong consistency — everyone sees the same version. SQL-level queries. Horizontal scale across regions.

**Answer: NewSQL (Google Spanner)**

Single-region PostgreSQL can't serve global users with low latency — too far from users in other regions. Cassandra gives global scale but eventual consistency — two users could see different document versions simultaneously, which is unacceptable for collaborative editing.

Spanner uses **TrueTime** — GPS and atomic clocks in every Google datacenter — to bound clock uncertainty to milliseconds. This gives globally ordered timestamps on every transaction — external consistency across regions with SQL semantics.

> NewSQL = SQL semantics + horizontal global scale + strong consistency. Use when a single-region SQL DB can't serve your global user base but you can't give up consistency.

**Interview tip by company:**
- Google interview → Spanner + TrueTime
- Amazon interview → Aurora
- Microsoft interview → Cosmos DB

---

### Scenario 8 — Swiggy search

**Requirements:** user types "biry" and needs "Biryani", "Chicken Biryani", "Biryani House" back — ranked by relevance, typo-tolerant, partial matching.

**Answer: Elasticsearch**

SQL LIKE query fails on three counts:
- `LIKE '%biry%'` — no ranking, results come back in random order
- No typo tolerance — `LIKE '%briy%'` returns nothing
- Full table scan — leading wildcard searches can't use any index

Elasticsearch uses an **inverted index** — maps terms to document IDs. "biryani" → [doc1, doc3, doc7]. Fuzzy matching handles typos. BM25 ranking returns results sorted by relevance.

> Elasticsearch whenever you need full-text search, ranked results, or typo tolerance. Never use SQL LIKE for search at scale.

---

## Complete decision reference

| Use case | Database | Core reason |
|---|---|---|
| User accounts, structured data | SQL (PostgreSQL) | Constraints, relationships, fixed schema |
| Sessions, tokens, rate limiting, caching | Redis | In-memory speed, TTL built-in, O(1) |
| Product catalog, flexible attributes | Document (MongoDB) | Dynamic schema, nested objects, rich queries |
| Write-heavy, time-ordered, massive scale | Cassandra | LSM writes, partition+cluster key |
| Multi-hop relationship traversal | Graph (Neo4j) | Edges as first-class citizens, no joins |
| Large files, media, backups | S3 + SQL | Blob for bytes, SQL for metadata |
| Global strong consistency + SQL | NewSQL (Spanner) | TrueTime, external consistency, horizontal scale |
| Full-text search, ranking, typos | Elasticsearch | Inverted index, BM25, fuzzy match |

---

## One-line decision rules

- **SQL** — default choice. Structured data, relationships, constraints. Move away only with a specific reason.
- **Redis** — anything needing sub-millisecond speed, TTL, or simple key→value. Sessions, cache, rate limiting.
- **MongoDB** — flexible or nested data where schema changes frequently. Product catalogs, user profiles, CMS.
- **Cassandra** — write-heavy, time-ordered data at massive scale. Messages, IoT, event logs.
- **Neo4j** — when relationship traversal is the primary operation. Social graphs, fraud detection, recommendations.
- **S3** — large binary files. Never store files in a DB.
- **Spanner/Aurora/Cosmos** — global SQL with strong consistency. Payments, banking, collaborative tools.
- **Elasticsearch** — full-text search with ranking. Never use SQL LIKE at scale.
