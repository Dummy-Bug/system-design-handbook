# Cassandra Internals — Overview

> [!abstract] Cassandra is a distributed column-family store built for massive write throughput and predictable low-latency reads — as long as you know your partition key. Every internal design decision flows from that constraint.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Ring-Architecture.md | How Cassandra distributes data across nodes using consistent hashing |
| 02-Write-Path.md | What happens inside a node when a write arrives — CommitLog, MemTable, SSTable, compaction |
| 03-Read-Path.md | How Cassandra reads efficiently — Bloom Filters, SSTable merge, coordinator routing |
| 04-Replication-Consistency.md | Replication factor, consistency levels, and the R+W>N formula |
| 05-Interview-Cheatsheet.md | Quick-reference for revision and interviews |

---

## The mental model

```
Client Write
     │
     ├──→ Coordinator Node (routes to correct node via ring)
     │         │
     │         ├──→ CommitLog (disk, append-only, durability)
     │         └──→ MemTable (memory, sorted, fast)
     │                   │ (when full)
     │                   ↓
     │               SSTable (disk, sorted, immutable)
     │                   │ (over time)
     │                   ↓
     │               Compaction (merge SSTables, keep latest version)
     │
     └──→ Replicated to N nodes (RF=3 means 3 copies)

Client Read
     │
     ├──→ Coordinator routes to replica nodes
     ├──→ Bloom Filter per SSTable → skip files that don't have the key
     └──→ Read MemTable + remaining SSTables → merge → return latest
```
