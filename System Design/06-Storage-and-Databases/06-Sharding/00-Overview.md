# Database Sharding — Overview

> [!abstract] Sharding is what you reach for when replication isn't enough — when a single server can no longer hold all your data or handle all your writes. It splits the data itself across multiple servers so each holds only a fraction. Every major system design interview at scale requires knowing this well.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-What-is-Sharding.md | Why replication doesn't solve everything, what sharding is, vertical partitioning |
| 02-Shard-Key.md | The most important decision — what makes a good vs bad shard key |
| 03-Sharding-Strategies.md | Range-based, hash-based, directory-based — trade-offs of each |
| 04-Consistent-Hashing.md | Why naive hashing breaks when topology changes, how consistent hashing fixes it |
| 05-Cross-Shard-Joins.md | Why JOINs break across shards, co-location, app-level join |
| 06-Resharding.md | Live data migration, the pain, and how to plan around it |
| 07-Interview-Cheatsheet.md | When and how to mention sharding in a design round |

---

## The one-line mental model

```
Replication → copies the same data to multiple servers (solves reads)
Sharding    → splits the data across multiple servers  (solves writes + storage)
```
