## The mental model

```
MongoDB = flexible JSON documents + indexes on any field (including arrays/nested)
        + replica sets + write concern + mongos sharding
```


## Embedding vs Referencing

| | Embed | Reference |
|---|---|---|
| When | Bounded, always fetched together | Unbounded, fetched independently |
| Example | Product specs, images, sizes | Comments, likes, orders |
| Reads | One fetch, fast | Multiple round trips |
| Updates | Rewrite entire document | Update target document only |
| Limit | 16MB document cap | No limit |

```
Rule: bounded + co-fetched → embed
      unbounded + independent → reference
```

---

## Write Concern

| Level | Guarantee | Cost | Use for |
|---|---|---|---|
| w:0 | None — fire and forget | Fastest | Metrics, logs |
| w:1 | Primary confirmed | Fast | Non-critical writes |
| w:majority | Quorum confirmed | Slower | Orders, payments, critical data |

---

## Indexes

```
Regular index    →  flat field, same as SQL B-tree
Multikey index   →  array field, one index entry per array element
Nested index     →  dot notation "experience.years", reaches inside objects
```

---

## Replication and Sharding

```
Replica set  →  1 primary + N secondaries, async replication, auto failover
mongos       →  transparent query router, app sees one endpoint
Shard key    →  consistent hashing, each shard is a replica set
```

---

## Limitations

```
No cross-document joins     →  denormalize or multiple round trips
No schema constraints       →  application enforces integrity
16MB document limit         →  unbounded arrays must be referenced
Denormalization cost        →  update propagation is your problem
```

---

## Use cases

```
✓  Product catalogs (variable specs per category)
✓  User profiles (variable fields per user type)
✓  CMS / blog content (flexible content blocks)
✓  Event data with variable payload structure

✗  Financial transactions (needs strict constraints)
✗  Relational data with complex joins
✗  Write-heavy time-series at extreme scale (use Cassandra)
```

---

## Interview framing

> "I'd use MongoDB when the data has variable structure and access patterns are document-centric — product catalogs, user profiles, CMS content. I'd embed bounded co-fetched data like specs and images, and reference unbounded data like comments. Write concern set to w:majority for critical writes, w:1 for high-throughput non-critical events. The key limitation is no cross-document joins — you design around that with intentional denormalization upfront."
