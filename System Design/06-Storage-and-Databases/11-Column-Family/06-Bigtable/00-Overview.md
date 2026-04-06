# Bigtable — Overview

> [!abstract] Bigtable is Google's wide-column store, published as a research paper in 2006. It directly inspired Cassandra (data model) and HBase (open-source equivalent). For SDE-2 interviews, the key is understanding how it differs from Cassandra and when you'd pick one over the other.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Architecture.md | Tablets, tablet servers, master, and GFS — how Bigtable is structured |
| 02-Cassandra-vs-Bigtable.md | Side-by-side comparison — architecture, storage, consistency, failure recovery |

---

## The one-line model

```
Cassandra  → masterless, local disk, tunable consistency, open source
Bigtable   → master + tablet servers, GFS storage, strong consistency, Google-managed
```
