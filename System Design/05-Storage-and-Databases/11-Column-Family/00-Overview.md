# Column-Family Stores — Overview

> [!abstract] Column-family stores are built for one thing SQL cannot do: absorb billions of writes per day while keeping range queries over time-series data fast. They do this by flipping how data is stored on disk — columns instead of rows — and by sorting everything by a structured row key.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Why-Column-Family.md | The problem — why SQL and KV stores both fall short |
| 02-Column-Oriented-Storage.md | Row vs column disk layout, and why it matters for writes |
| 03-Column-Families-And-Row-Keys.md | What a column family is, and how row key sorting enables fast range queries |
| 04-When-To-Use.md | The golden rule — known entity + time range, and when to avoid Cassandra |
| Cassandra/ | Cassandra internals — architecture, write path, read path, replication |
| Bigtable/ | Google's wide-column store — architecture and comparison with Cassandra |

---

## The one-line model

```
SQL             → any query, strong consistency, poor write throughput at scale
Key-Value       → O(1) point lookups, no range queries across related keys
Document        → flexible nested schema, poor fit for sparse time-series data
Column-Family   → write-heavy, time-ordered, massive scale — but only if you know your row key
```
