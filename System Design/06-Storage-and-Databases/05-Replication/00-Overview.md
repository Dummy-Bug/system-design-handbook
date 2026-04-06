# Database Replication — Overview

> [!abstract] Replication is the foundation of availability and read scalability in every production database system. One server is never enough — replication is how you survive failures and distribute load across multiple servers.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-What-is-Replication.md | Why one DB isn't enough, primary-replica architecture |
| 02-Sync-vs-Async.md | Sync vs async replication — the durability vs latency trade-off |
| 03-Replication-Lag.md | Replica lag, read-your-own-writes violations, and the fix |
| 04-Failover.md | What happens when the primary dies, data loss window |
| 05-Multi-Primary.md | Multiple write nodes, split-brain, quorum |
| 06-Interview-Cheatsheet.md | When and how to use replication in a design round |

---

## The one-line mental model

```
Replication → one primary accepts writes
            → copies every write to one or more replicas
            → replicas absorb reads + stand by to take over if primary dies
```
