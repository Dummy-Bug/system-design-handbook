# Key-Value Stores — Overview

> [!abstract] A Key-Value store is the simplest possible database model — a key maps to a value, that's it. No joins, no schema, no WHERE clauses. That simplicity enables extreme speed. Understanding when to reach for a KV store, and which one, is a core system design skill.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Redis.md | Reference to Redis deep-dive in Caching section |
| 02-Memcached.md | Simple, multi-threaded, pure caching — when it beats Redis |
| 03-DynamoDB/ | AWS managed KV store — data model, consistency, query API, GSI |
| 04-KV-Positioning.md | When to use KV vs SQL vs document vs column-family |
| 05-Interview-Cheatsheet.md | Quick reference for revision |

---

## The one-line model

```
SQL         → complex queries, joins, strong consistency
Document    → flexible schema, nested objects
Column-family → write-heavy, time-ordered, massive scale
Key-Value   → ultra-fast simple lookups, O(1), everything in RAM
```
