# Why Single Node Doesn't Scale

> [!question] Your Redis instance is running fine. 10 million users later, what breaks?

---

## Two fundamental problems

**Problem 1 — Memory limit:**

```
10 million users × 10KB per user profile = 100GB of cache data

A single Redis node typically has 32-64GB of RAM
→ you physically cannot fit 100GB on one server
→ cache hit rate drops as keys get evicted to make space
→ more cache misses → more DB queries → DB becomes the bottleneck again
```

**Problem 2 — SPOF (Single Point of Failure):**

```
Redis node goes down (hardware failure, OOM kill, deployment)
→ entire cache gone instantly
→ every request → cache miss
→ all traffic hits DB simultaneously
→ DB collapses under the load ✗
```

A cache that improves performance 95% of the time but causes outages when it fails is worse than no cache at all — it trains your system to depend on it, then fails catastrophically.

---

## The solution — distribute the cache

Split the cache across multiple nodes. Each node holds a fraction of the total keyspace.

```
Single node (fails at 64GB):
  Node A → all 100GB of keys → memory exhausted ✗

Distributed (scales horizontally):
  Node A → keys 1-25M   → 25GB ✓
  Node B → keys 25M-50M → 25GB ✓
  Node C → keys 50M-75M → 25GB ✓
  Node D → keys 75M-100M→ 25GB ✓
```

New problem: a request comes in for `user:123:profile`. Which node do you go to?

This is the key routing problem — solved by **consistent hashing** (next file).
