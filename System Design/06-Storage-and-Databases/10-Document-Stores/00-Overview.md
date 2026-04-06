# Document Stores — Overview

> [!abstract] A document store trades SQL's rigid schema and join capabilities for flexible, nested, queryable JSON documents. The right tool when your data has variable structure and your access patterns are document-centric — fetch everything about this entity in one read.

---

## Files in this folder

| File | Topic |
|---|---|
| 01-MongoDB/ | Deep dive — data model, indexes, embedding vs referencing, replication, sharding |
| 02-Positioning.md | When document stores win vs SQL, KV, column-family |
| 03-Interview-Cheatsheet.md | Quick reference for revision |

---

## Document stores at a glance

| Store | What it is |
|---|---|
| **MongoDB** | Most popular, general purpose, rich query API, indexes on nested fields |
| **Firestore** | Google's managed document store, real-time sync built-in, great for mobile |
| **CouchDB** | Strong offline sync, conflict resolution built-in, good for mobile apps |
| **DynamoDB** | Primarily KV but supports JSON values — no querying inside the JSON though |
| **Elasticsearch** | Primarily a search engine but stores documents underneath |

> For SDE-2 interviews, MongoDB is all you need to know deeply. Know the others exist and roughly when they're used.

---

## The one-line model

```
Document store = flexible JSON documents + queryable nested structures + no schema enforcement
```
