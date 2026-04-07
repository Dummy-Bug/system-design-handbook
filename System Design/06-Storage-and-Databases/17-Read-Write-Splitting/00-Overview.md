# Read/Write Splitting — Overview

> [!info] In most systems, reads vastly outnumber writes — often 100:1. Forcing both through a single database node means reads and writes compete for the same connections, locks, and CPU. Read/Write Splitting routes writes to a primary node and reads to replica nodes, scaling each independently.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-The-Problem.md | Why a single node handling both reads and writes is a bottleneck |
| 02-How-It-Works.md | Primary/replica setup, WAL streaming, routing at the application layer |
| 03-Replication-Lag.md | The lag problem, read-your-own-writes violation, and the fix |
| 04-Interview-Cheatsheet.md | Quick reference for revision |

---

## The one-line model

```
All writes → Primary node
All reads  → Replica nodes (one or many)
```

---

## When to mention in interviews

Any read-heavy system — social feeds, news feeds, product catalogs, dashboards. If reads vastly outnumber writes and the DB is the bottleneck, read/write splitting is part of the answer alongside caching and connection pooling.
