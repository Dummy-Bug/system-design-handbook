## When to mention sharding

```
Estimation says storage > few TB?          → shard
Write QPS > 100K sustained?                → shard
Single DB primary can't keep up?           → shard
Interviewer asks "how do you scale this?"  → shard
```

---

## The move — replication first, sharding second

> [!tip] Always say replication before sharding
> "I'd first scale reads with read replicas. If the write bottleneck or storage limit becomes the constraint, I'd introduce sharding."

Sharding is operationally complex. Interviewers want to see that you reach for it only when necessary, not as a first instinct.

---

## Decisions to state explicitly

**1. Shard key choice — always justify it**

> "I'd shard by user_id — it's high cardinality, immutable, evenly distributed, and present in every query."

Never just say "I'd shard by user_id." Say *why* it's a good shard key using the four rules.

**2. Strategy**

> "I'd use consistent hashing so adding shards only remaps ~1/N of keys instead of causing a full remapping."

**3. Cross-shard joins**

> "I'd co-locate a user's profile, posts, and follows under the same shard key so most queries stay on a single shard. Cross-shard access only happens for specific operations like viewing another user's profile, which I'd handle at the application layer."

**4. Resharding plan**

> "I'd over-shard upfront — start with 256 virtual shards mapped to physical servers. Adding capacity means moving whole virtual shards, not migrating individual rows."

---

## One-line definitions

> [!info] Sharding
> Horizontally splitting rows across multiple servers so each holds a fraction of the data. Solves write bottleneck and storage limits that replication cannot.

> [!info] Shard key
> The column used to route every row to its shard. Must be high cardinality, immutable, evenly distributed, and present in every query.

> [!info] Consistent hashing
> Placing shards on a ring so adding/removing a shard only remaps ~1/N of keys. Avoids the ~80% remapping problem of naive modulo hashing.

> [!info] Co-location
> Designing the data model so related data (user + their posts + their follows) all share the same shard key and land on the same shard. Eliminates cross-shard joins.

> [!info] Virtual nodes (vnodes)
> Each physical shard owns multiple positions on the consistent hashing ring. Ensures even key distribution and spreads load when a shard is added or removed.

---

## The hotspot trap

> [!danger] A good shard key distributes rows evenly — not request volume
> user_id is a perfect shard key. But if one user (a celebrity) gets 10 million reads per second, their shard is still a hotspot. Fix: cache the hot row in Redis. The shard only handles cache misses.

---

## Quick comparison

| Strategy | Good for | Problem |
|---|---|---|
| Range-based | Data locality, archive queries | Sequential inserts hotspot latest shard |
| Hash-based | Even distribution, general use | No co-location control, naive % breaks on topology change |
| Directory-based | Full placement control | SPOF + extra network hop on every query |
| Consistent hashing | Any distributed system with changing topology | Slightly more complex than modulo |
