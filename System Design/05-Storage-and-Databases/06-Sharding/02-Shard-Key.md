> [!question] You've decided to shard. Now what column do you shard on? This is the most important decision in sharding — get it wrong and you've built an uneven system that breaks under load.

---

## What the shard key does

The shard key is the column you use to decide which shard a given row belongs to. Every read and write uses this key to route to the correct shard. Once chosen, it is extremely painful to change — rows would have to physically migrate across servers.

---

## What a bad shard key looks like

**Bad shard key — country_id:**

```
Shard 1 (India)   → 1.4 billion users → overwhelmed ✗
Shard 2 (USA)     → 340 million users → very busy ✗
Shard 3 (Vatican) → 800 users         → basically idle ✗
```

**Low cardinality** — only ~200 distinct values. Data distribution is wildly uneven. India's shard is a permanent hotspot.

**Bad shard key — created_at (time-based):**

```
Shard Jan → old data, no new writes, just occasional reads
Shard Feb → old data, no new writes, just occasional reads
Shard Mar → ALL new writes hammering this one shard ✗
```

Sequential inserts always hit the most recent shard. The latest shard is a write hotspot while all older shards sit mostly idle.

**Bad shard key — user_status (low cardinality):**

```
Shard 1 (active)   → 900 million users ✗
Shard 2 (inactive) → 100 million users
```

Only 2-3 distinct values. Can never distribute evenly no matter how many shards you add.

---

## What a good shard key looks like

**Good shard key — user_id:**

```
High cardinality   → billions of unique values → distributes evenly ✓

Immutable          → user_id never changes → row never needs to move shards ✓

Always queryable   → every query includes user_id → always know which shard ✓

Even distribution  → no single user_id has disproportionate data ✓
```

Every query says "give me data for user_id X" — you hash X, route to the correct shard, done. No scatter-gather, no fan-out.

---

## The four rules for a good shard key

```
1. High cardinality   → many distinct values → rows distribute evenly across shards
   
2. Immutable          → never changes → a row never needs to migrate to a different shard
   
3. Evenly distributed → no single value dominates → no hotspot shards
   
4. Always present     → appears in every query → you always know which shard to hit
```

> [!danger] Immutability is the most overlooked rule
> If you shard by email and a user changes their email, their row must physically move to a different shard. At millions of rows, this is a live data migration nightmare. user_id never changes — that's why it's the canonical shard key for user data.

---

## The hotspot problem

Even with a good shard key, hotspots can emerge. On Twitter, user_id is a good shard key — unless one of your users is Elon Musk. A single row (a celebrity's profile) receives millions of reads per second, hammering whichever shard holds that user_id.

The shard key distributes rows evenly. It cannot distribute *request volume* evenly when some rows are orders of magnitude more popular than others.

**Fix for read hotspots:** cache the hot row in Redis. The DB shard only handles cache misses.

**Fix for write hotspots:** add a random suffix to the shard key for high-volume rows, spreading writes across multiple shards. **Reads must then query all suffixes and aggregate** — a trade-off.
