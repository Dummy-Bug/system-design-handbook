# Query-First Data Modeling in Cassandra

In SQL, you design your schema around your data. You create a `users` table, an `orders` table, a `messages` table — and then you write whatever query you need. Joins, filters, any column — SQL figures it out at query time.

Cassandra cannot do this. The partition key is the only fast access path. If you don't know the partition key at query time, Cassandra scans the entire cluster. So the approach is flipped entirely: **you design the table around the query, not the data**.

---

## The messaging app problem

You're building a messaging app. You have two queries:

```
Query 1: "give me all messages in conversation_123"
Query 2: "give me all messages sent by user_456"
```

The natural instinct is to create one `messages` table and serve both queries from it. In SQL, that works fine. In Cassandra, it breaks immediately.

If you design the table with `conversation_id` as the partition key:

```
Partition key:  conversation_id
Clustering:     timestamp

conversation_123 | 9:00am → { user: user_456, text: "hey" }
conversation_123 | 9:01am → { user: user_789, text: "what's up" }
conversation_123 | 9:02am → { user: user_456, text: "not much" }
```

Query 1 is a fast sequential scan — you know `conversation_123`, Cassandra goes straight to that partition and scans by timestamp. Done.

But Query 2 — "give me all messages by user_456" — `user_id` is not the partition key. It's just a regular column sitting inside each partition. To find all messages by user_456, Cassandra has to scan every partition, on every node, across the entire cluster. At billions of messages, this is catastrophically slow.

> [!danger] No partition key = full cluster scan
> In Cassandra, filtering on any column that isn't the partition key means visiting every node and every partition. There is no global secondary index that makes this efficient. The partition key is the only fast access path.

---

## The solution — one query, one table

The Cassandra answer is to store the same data twice, in two different shapes, each optimised for one query:

```
Table 1: messages_by_conversation
Partition key:  conversation_id
Clustering:     timestamp

conversation_123 | 9:00am → { user: user_456, text: "hey" }
conversation_123 | 9:01am → { user: user_789, text: "what's up" }


Table 2: messages_by_user
Partition key:  user_id
Clustering:     timestamp

user_456 | 9:00am → { conversation: conversation_123, text: "hey" }
user_456 | 9:05am → { conversation: conversation_789, text: "hello" }
```

The same message exists in both tables. Each table is built for exactly one query. Query 1 hits Table 1 — fast. Query 2 hits Table 2 — fast.

> [!info] Query-first data modeling
> In Cassandra, you start by listing your queries, then design one table per query. The table's partition key and clustering columns are chosen specifically to make that query a sequential scan. This is the opposite of SQL normalisation — duplication is intentional and expected.

---

## The cost — duplication and consistency risk

Storing the same data twice means every write must go to both tables. And since Cassandra has **no multi-partition transactions**, those two writes are not atomic.

In SQL, you wrap both updates in a transaction:

```sql
BEGIN;
  UPDATE messages_by_conversation SET text = 'edited' WHERE conversation_id = 'conv_123';
  UPDATE messages_by_user         SET text = 'edited' WHERE user_id = 'user_456';
COMMIT;
-- either both happen or neither does
```

In Cassandra, each write goes to its own partition on its own node independently. There is no coordinator that can roll both back if one fails:

```
Write 1 → messages_by_conversation (Node A) ✅ success
Write 2 → messages_by_user         (Node B) ❌ network blip, failed

→ Tables are now out of sync. No automatic recovery.
```

This is the real cost of query-first modeling. You trade consistency risk for query performance.

> [!important] No multi-partition transactions
> Each partition write in Cassandra is an independent operation. There is no atomicity across partitions or tables. If you write to two tables and one fails, the other has already committed — there is no rollback.

---

## How real systems handle the consistency risk

**Option 1 — Accept eventual consistency**

For most event-driven data, a brief window where one table is ahead of the other is acceptable. The app writes to both tables, and a retry mechanism catches up on failure. For chat messages, a few milliseconds of inconsistency between two views is invisible to users.

**Option 2 — Use CDC to sync**

Write to one table only. CDC reads the CommitLog and asynchronously propagates the write to the second table. One source of truth, the second table catches up eventually:

```
App writes → Table 1 (conversation_id partition)
                  │
                  CDC reads CommitLog
                  │
                  ↓
             Table 2 (user_id partition)  ← eventually in sync
```

**Option 3 — Make data immutable**

For messages, events, and analytics — most systems don't allow edits at all, or model an edit as a new row with a newer timestamp rather than modifying the old one. If the data never changes, the duplication problem disappears entirely. This is the most common pattern in Cassandra-backed systems.

> [!tip] Query-first duplication is only painful when data mutates frequently
> For append-heavy, rarely-updated data — messages, sensor readings, analytics events, audit logs — the data is written once and never changed. Duplication across tables costs disk space but creates zero consistency risk. This is exactly the data profile Cassandra is designed for.

---

## The mental shift from SQL

```
SQL mindset:      design around data → normalise → query anything
Cassandra mindset: list your queries → design one table per query → accept duplication
```

In SQL, duplication is a smell — it means your schema isn't normalised. In Cassandra, duplication is the solution. Disk is cheap. Full cluster scans at billions of rows are not.

> [!important] Start every Cassandra schema design with the question list
> Before writing a single CREATE TABLE, write down every query the system needs to serve. Each query becomes a table. The partition key is whatever the query filters on first. The clustering column is whatever the query sorts or ranges on. If you can't answer "which query is this table for?" — the table is wrong.
