# Column-Oriented Storage

> [!info] Column-oriented storage — used by Redshift, BigQuery, Snowflake — packs one column's values together into each page instead of one row's values. This single layout decision is what makes aggregations across millions of rows fast and full record lookups expensive.

---

## How data is packed into pages

Instead of packing full rows together, the DB packs all values for a single column into each page:

```mermaid
flowchart LR
    subgraph ages["Block 204 — ages only"]
        A["28"] --- B["34"] --- C["22"] --- D["31"]
    end
    subgraph names["Block 205 — names only"]
        E["Alice"] --- F["Bob"] --- G["Charlie"] --- H["Dave"]
    end
    subgraph emails["Block 206 — emails only"]
        I["alice@gmail.com"] --- J["bob@gmail.com"] --- K["charlie@gmail.com"] --- L["dave@gmail.com"]
    end
    subgraph cities["Block 207 — cities only"]
        M["London"] --- N["New York"] --- O["London"] --- P["Berlin"]
    end
```

Each block contains values from only one column, for many rows. The OS still sees 8KB of bytes — it has no idea a column boundary exists. The DB engine is the one that decided what to pack where.

---

## What happens when you run an aggregation

```sql
SELECT AVG(age) FROM users;
```

```mermaid
flowchart TD
    A[Query: average age of 100M users] --> B[DB knows ages are in blocks 204 to 312]
    B --> C[DB asks OS for block 204]
    C --> D[OS loads 8KB - ages only - no names, emails, cities]
    D --> E[DB extracts all age values from block 204]
    E --> F[DB asks OS for block 205 - next age block]
    F --> G[... repeated only for age blocks]
    G --> H[DB computes average - done]
```

The DB only requests the age blocks. Names are on block 205. Emails on block 206. Cities on block 207. None of those blocks are ever touched. At 100 million users, this is the difference between reading 1GB of age data versus reading 10GB of mixed row data.

> [!important] The OS fetches exactly what the DB asks for. Because the DB only asks for age blocks, the OS only loads age blocks. The layout decision made at write time determines how much I/O you pay at read time.

---

## What happens when you fetch a full profile

```sql
SELECT * FROM users WHERE id = 1;
```

```mermaid
flowchart TD
    A[Query: fetch Alice's full profile] --> B[DB needs all columns for id=1]
    B --> C[Fetch block 204 for age]
    B --> D[Fetch block 205 for name]
    B --> E[Fetch block 206 for email]
    B --> F[Fetch block 207 for city]
    C & D & E & F --> G[DB stitches values together]
    G --> H[Returns: Alice, alice@gmail.com, 28, London]
```

Alice's data is now spread across four different blocks. Four separate OS reads to reconstruct one record. In row-oriented storage this was one read. This is the cost of column-oriented layout for OLTP-style queries.

> [!danger] Column-oriented storage is not a production database replacement. Running transactional workloads — individual inserts, updates, single-record reads — against a columnar store is slow. It is built for analytics, not transactions.

---

## The OS perspective

The OS behaves identically in both cases. It fetches blocks on demand, hands raw bytes to the DB, and steps back:

```mermaid
flowchart TD
    A[DB requests block 204] --> B[OS looks up inode for analytics.db]
    B --> C[Finds block 204 on disk]
    C --> D[Loads 8KB into memory - all age values]
    D --> E[Hands raw bytes to DB engine]
    E --> F[DB interprets bytes as a column of age values]
```

The OS does not know it is fetching a column instead of rows. It just fetches bytes. All the intelligence — what went into block 204, why only block 204 was requested — lives entirely in the DB engine.

---

## Row vs Column — side by side

```mermaid
flowchart LR
    subgraph Row["Row-Oriented"]
        R1["Block 204: full rows packed together"]
        R2["AVG age → load all blocks, extract age from each row"]
        R3["Fetch Alice → 1 block read"]
    end
    subgraph Col["Column-Oriented"]
        C1["Block 204: age values only"]
        C2["AVG age → load age blocks only"]
        C3["Fetch Alice → 4 block reads"]
    end
```

```
Workload                        Row-Oriented        Column-Oriented
─────────────────────────────────────────────────────────────────────
Fetch one full record           1 block read        N block reads (one per column)
AVG/SUM across all rows         All blocks loaded   Only target column blocks loaded
INSERT one row                  Append to one page  Must update N column pages
Best for                        OLTP, transactions  OLAP, analytics, dashboards
Examples                        PostgreSQL, MySQL    Redshift, BigQuery, Snowflake
```

> [!important] The layout is a write-time decision with read-time consequences. Pack rows together if your queries are about individual records. Pack columns together if your queries aggregate across millions of rows.
