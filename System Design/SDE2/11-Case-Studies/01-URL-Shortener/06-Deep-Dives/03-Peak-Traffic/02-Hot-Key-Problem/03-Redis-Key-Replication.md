
> [!info] Fix 2 — spread the hot key across multiple Redis nodes
> Local app server cache works perfectly for immutable data. But for systems where data can change — and local cache invalidation is a real problem — you need a different approach: replicate the hot key across multiple Redis nodes using key salting.

---

## The problem with consistent hashing for hot keys

In a Redis Cluster, consistent hashing maps each key to exactly one node:

```
hash("x7k2p9") → always Node 2
```

800k reads/sec for x7k2p9 → all go to Node 2 → Node 2 overwhelmed.

You can't change where the key lives without changing the key itself. Consistent hashing is deterministic — same key always same node.

---

## Key salting — bypass consistent hashing deliberately

Instead of one key `x7k2p9`, create N salted copies of the same key, each landing on a different node:

```
x7k2p9:0  → hash → Node 2
x7k2p9:1  → hash → Node 5
x7k2p9:2  → hash → Node 7
```

Write the same value to all N copies:

```
SET x7k2p9:0 https://long-url.com
SET x7k2p9:1 https://long-url.com
SET x7k2p9:2 https://long-url.com
```

On read, pick a random salt:

```
suffix = random(0, N-1)
GET x7k2p9:{suffix}  → hits a random node each time
```

800k reads/sec → randomly distributed across 3 nodes → ~267k each → manageable.

The consistent hashing ring is not bypassed — you're using 3 different keys that happen to contain the same value. The ring routes each salted key to a different node naturally.

---

## The write amplification trade-off

Every write to a hot key now requires N writes instead of 1:

```
Normal key: SET x7k2p9 value          → 1 write
Salted key: SET x7k2p9:0, :1, :2      → 3 writes
```

For a URL shortener, writes are 1k/sec. Even if every URL became a hot key (unrealistic), 3x writes = 3k writes/sec. Negligible.

For write-heavy systems, this trade-off needs more careful evaluation.

---

## When to use salting vs local cache

```
Local app server cache:
→ right for: immutable data, no invalidation needed
→ wrong for: mutable data (stale reads across servers)

Key salting:
→ right for: mutable data where invalidation is needed
             (update all N salted copies on write)
→ wrong for: high write volume (N writes per update)
```

For URL shorteners — immutable data — local cache is better. Key salting is the tool to reach for in systems where data changes and local caching is unsafe.

---

> [!tip] Interview framing
> "Key salting bypasses consistent hashing by creating N copies of the hot key with different suffixes — each lands on a different Redis node via normal consistent hashing. Reads pick a random suffix, distributing load across N nodes. Write amplification is the cost — N writes per update. Right for mutable data where local caching is unsafe. For URL shorteners, local app server cache is simpler and works better."

---

**Next:** Once you decide to replicate a hot key via salting, all app servers need to know about it simultaneously — otherwise some servers still use the unsalted key and the load isn't distributed. How do you broadcast the promotion?
