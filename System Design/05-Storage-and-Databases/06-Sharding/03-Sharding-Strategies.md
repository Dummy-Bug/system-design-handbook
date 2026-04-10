> [!question] You have a shard key. Now how do you decide which row goes to which shard?

There are three strategies. Each solves a different problem and creates a different one.

---

## Range-Based Sharding

Divide the key space into contiguous ranges:

```
Shard 1 → user_id 1 - 25M
Shard 2 → user_id 25M - 50M
Shard 3 → user_id 50M - 75M
Shard 4 → user_id 75M - 100M
```

Simple to understand and implement. Range queries are fast — all users in a given range sit on the same shard, no scatter-gather needed.

**The problem:** users sign up sequentially. user_id 99,000,001 goes to Shard 4. user_id 99,000,002 also goes to Shard 4. Every new signup goes to the same shard — the others sit idle while one shard absorbs all writes.

```
Range-based with time-ordered IDs:
  Shard 1 (old users) → occasional reads, almost no writes
  Shard 2 (old users) → occasional reads, almost no writes
  Shard 3 (old users) → occasional reads, almost no writes
  Shard 4 (new users) → ALL new writes ✗
```

Range-based sharding is useful when you *want* data locality — archiving old logs and only querying recent ones, for example. But for general user data with sequential IDs, **it creates a permanent write hotspot on the latest shard**.

---

## Hash-Based Sharding

Hash the shard key to pick the shard:

```
shard = hash(user_id) % N
```

Even distribution — no hotspots, no sequential clustering. user_id 1 might hash to Shard 3, user_id 2 to Shard 1, user_id 3 to Shard 3 again. The distribution looks random and is statistically even. This is the standard approach.

**The problem:** no control over where related data lands. **user_id 1 and their best friend might end up on completely different shards**. Range queries across shards require hitting every shard and aggregating results — scatter-gather.

```
Hash-based:
  user_id 1   → hash % 4 = 2 → Shard 2
  user_id 2   → hash % 4 = 0 → Shard 1  (friend of user 1, different shard)
  user_id 3   → hash % 4 = 2 → Shard 2

  "Find all of user 1's friends" → must query all shards ✗
```

Also: naive hash-based sharding (`% N`) is catastrophic when you add a shard — see `04-Consistent-Hashing.md` for the fix.

---

## Directory-Based Sharding

Instead of a formula, maintain an explicit lookup table — a directory that maps every key to a shard:

```
Directory (lookup table):
  user_id 1    → Shard 2
  user_id 2    → Shard 1
  user_id 500M → Shard 2   ← deliberately co-located with user 1
```

Full control over placement. If user 1 and their friends need to live on the same shard for JOIN performance, you can explicitly place them there. Moving a user to a different shard still requires migrating their actual data — copy rows to the new shard, update the directory entry, delete from the old shard. What directory-based sharding avoids is bulk rehashing — you choose exactly which users to move, rather than triggering a mass redistribution every time a new shard is added.

**The problem:** every single read and write must first consult this directory — an extra network hop on every query. And the directory itself becomes a **SPOF** — if it goes down, nothing in the system can route anywhere. The directory must be highly available and extremely fast, which means it needs its own replication and caching, adding complexity.

---

## Comparison

```
Range-based      → split key space into ranges
                   ✓ range queries fast, data locality
                   ✗ sequential inserts hotspot the latest shard

Hash-based       → hash the key to pick a shard
                   ✓ even distribution, simple, no hotspots
                   ✗ no control over placement, range queries scatter

Directory-based  → explicit lookup table: key → shard
                   ✓ full placement control, easy to move rows
                   ✗ directory is a SPOF + extra network hop on every query
```

> [!tip] In practice
> Most systems use **hash-based sharding** (or consistent hashing, which improves on it). Directory-based is reserved for cases where co-location is critical and you can afford the operational complexity of maintaining and protecting the directory.
