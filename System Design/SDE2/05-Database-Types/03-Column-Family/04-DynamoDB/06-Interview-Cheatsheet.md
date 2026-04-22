## The mental model in one block

```
Partition key  →  consistent hashing → which server (O(1) routing)

Sort key       →  LSM tree → order within that server (range queries)

GSI            →  second copy of data with different partition key

Global Tables  →  async multi-region replication, eventual consistency

Consistency    →  tunable per read (eventual = cheap, strong = 2x cost)
```


---

## Three read modes

| Operation | What it does | When to use |
|---|---|---|
| GetItem | Exact lookup by full primary key | Single row fetch |
| Query | Range scan within one partition | All rows by user, time range |
| Scan | Reads entire table | Never in production |

---

## Consistency cheatsheet

| Mode | Guarantee | Cost | Use when |
|---|---|---|---|
| Eventually consistent | Might be milliseconds stale | 0.5x | Feeds, counts, recommendations |
| Strongly consistent | Latest write guaranteed | 2x | Profile updates, payments, messages |
| GSI reads | Always eventually consistent | — | No choice — GSI is always eventual |

---

## GSI trade-offs

```
GSI adds:   new access pattern (different partition key)
GSI costs:  double write cost + double storage + eventual consistency
GSI rule:   if you're about to Scan, you need a GSI instead
```

---

## Redis vs DynamoDB in one line

```
Redis      →  sub-millisecond, in-memory, rich structures, cache layer
DynamoDB   →  millisecond, disk-backed, managed sharding, persistent store
Together   →  Redis in front (hot cache), DynamoDB behind (source of truth)
```

---

## Interview framing

> "DynamoDB is my default for write-heavy workloads at massive scale — activity logs, likes, events. Partition key routes via consistent hashing, sort key enables range queries within a partition. For cross-partition queries I'd add a GSI. For multi-region I'd use Global Tables — async replication, eventual consistency cross-region. I'd pair it with Redis as a cache layer for sub-millisecond reads on hot data."
