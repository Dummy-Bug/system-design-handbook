# DynamoDB — Overview

> [!info] DynamoDB is AWS's fully managed key-value store. No servers to provision, no indexes to tune manually, no replication to configure. You define a partition key, optionally a sort key, and DynamoDB handles everything else — sharding, replication across 3 availability zones, scaling up and down automatically.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Data-Model.md | Partition key, sort key, how consistent hashing routes to the right server |
| 02-Consistency.md | Eventual vs strong reads, tunable per query, Global Tables for multi-region |
| 03-Query-API-and-Indexes.md | GetItem vs Query vs Scan, KeyConditionExpression, GSI for cross-partition queries |
| 04-Redis-vs-DynamoDB.md | Redis vs DynamoDB — when to pick which |
| 05-Interview-Cheatsheet.md | Quick reference for revision |

---

## The one-line model

```
DynamoDB = managed KV store + range queries within a partition + tunable consistency + auto-scaling
```

---

## When to reach for DynamoDB

```
✓  Write-heavy workloads at massive scale (billions of events/day)
✓  Simple access patterns — lookup by user, lookup by user + time range
✓  Don't want to manage infrastructure (fully managed)
✓  Already on AWS

✗  Complex joins or ad-hoc queries across dimensions
✗  Need full SQL flexibility
✗  Sub-millisecond in-memory performance (use Redis instead)
```
