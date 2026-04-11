> [!info] Most people use DynamoDB like a hashmap — put a value in, get it back by key. But DynamoDB has a full query API that lets you do range queries within a partition, and Global Secondary Indexes that let you query by a completely different key. Understanding this is what separates "I've used DynamoDB" from "I know how to model data in DynamoDB."


## Three ways to read data

**GetItem** — exact lookup by primary key

```
GetItem(TableName: "likes", Key: { user_id: 42, created_at: "2024-01-07" })
→ returns exactly one row
→ pure hashmap mode — partition key + sort key → one record
```

**Query** — range scan within a partition

```
Query(
  TableName: "likes",
  KeyConditionExpression: "user_id = 42 AND created_at BETWEEN '2024-01-01' AND '2024-01-31'"
)
→ hashes user_id=42 → goes to Server 3
→ range scan on created_at within that partition
→ returns all matching rows in order
```

**Scan** — reads every row in the entire table

```
Scan(TableName: "likes")
→ hits every partition, every server
→ reads everything
→ extremely expensive, slow, almost never appropriate in production
```

> [!danger] Never use Scan in production. It reads the entire table regardless of size. If you find yourself needing a Scan, your data model is wrong — you need a GSI instead.

---

## The range query is always anchored to one partition

This is the key constraint to internalise. The `BETWEEN` range in a Query only works within a single partition. You must always specify an exact partition key first.

```
✓  "Give me all likes by user 42 in January"
   → partition key fixed (user_id=42), range on sort key (created_at)

✗  "Give me all users who liked posts in January"
   → no fixed partition key — would need to scan every partition
```

For the second query, you need a different access pattern — which is what GSI solves.

---

## Global Secondary Index (GSI)

A GSI is a second copy of your data, stored with a different partition key and sort key. It lets you query by dimensions that aren't your primary key.

**Example:** Your primary table is `likes` with `user_id` as partition key. That's great for "all likes by user 42." But now you need "all likes on post 123."

Without a GSI, you'd have to scan the entire table.
```
Primary table:
  Partition key: user_id
  Sort key: created_at
  → fast for: all likes by a user
```

With a GSI:

```
GSI:
  Partition key: post_id
  Sort key: created_at
  → fast for: all likes on a post
```

DynamoDB maintains the GSI automatically. Every write to the primary table propagates to the GSI asynchronously.

---

## What GSI actually costs you

**Storage** — DynamoDB stores a second copy of the projected attributes. Double the storage for a full projection.

**Write cost** — every write to the primary table triggers a write to the GSI. Two writes billed, not one.

**Consistency** — GSI reads are always eventually consistent. Even if you request a strongly consistent read on the primary table, the GSI can be slightly behind.

```
Primary table write → GSI updated async → GSI might lag by milliseconds
→ GSI reads are eventually consistent, no exception
```

**This is the trade-off:** you can add a GSI to answer any access pattern, but every GSI adds write cost and eventual consistency.

---

## When to add a GSI vs rethink your data model

GSI is the right call when you genuinely have two different access patterns on the same data:

```
"give me all likes by user"   → primary table, partition key = user_id
"give me all likes on post"   → GSI, partition key = post_id
```

But sometimes the right answer is to store the data twice in two separate tables, each modelled for one access pattern. Cheaper than a GSI if the two access patterns have very different traffic.

> [!tip] Interview framing
> "DynamoDB's primary key only supports range queries within a partition. For cross-partition queries I'd add a GSI with the new dimension as the partition key — accepts the trade-off of eventual consistency on the index and double the write cost."

---

## Summary

```
GetItem   →  exact lookup, one row, O(1)
Query     →  range within a partition, partition key must be exact
Scan      →  entire table, never in prod

GSI       →  second copy of data with different partition key
           →  enables cross-partition queries
           →  always eventually consistent
           →  doubles write cost + storage
```
