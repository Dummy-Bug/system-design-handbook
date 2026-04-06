# MongoDB — Overview

> [!info] MongoDB is a document store — it stores JSON objects instead of rows. No fixed schema, no ALTER TABLE, no migrations when your data shape changes. Each document can have different fields, different nesting, different arrays. The database doesn't care.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-Document-Model.md | JSON documents, flexible schema, why SQL struggles with variable structure |
| 02-Indexes.md | Multikey indexes on arrays, nested field indexes, B-tree underneath |
| 03-Embedding-vs-Referencing.md | The core data modelling decision — bounded vs unbounded, trade-offs |
| 04-Replication-and-Sharding.md | Replica sets, write concern levels, mongos router |
| 05-Limitations.md | No cross-document joins, no constraints, intentional denormalization |
| 06-Interview-Cheatsheet.md | Quick reference for revision |

---

## The one-line model

```
MongoDB = JSON documents + indexes on any field + replica sets + sharding via mongos
```

---

## When to reach for MongoDB

```
✓  Variable schema — different entities have different fields (product catalog)
✓  Nested/hierarchical data that's always fetched together
✓  Rapid iteration — schema changes without migrations
✓  Read-heavy with document-centric access patterns

✗  Relational data with complex joins
✗  Financial data needing strict constraints and integrity
✗  Cross-document transactions at scale
✗  Write-heavy time-series at extreme scale (use Cassandra)
```
