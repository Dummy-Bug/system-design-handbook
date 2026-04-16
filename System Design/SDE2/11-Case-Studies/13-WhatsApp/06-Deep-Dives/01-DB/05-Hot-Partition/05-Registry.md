
> [!info] The hot partition registry — a routing table, not a cache
> The registry maps conversation_id to max_N. Every write and every read consults it. Losing it doesn't mean a cache miss — it means wrong routing, which means missing messages. This distinction changes everything about how you store it.

---

## Cache vs routing table

There is a critical distinction between a cache and a routing table:

```
Cache:
  → Stores a copy of data that also exists elsewhere
  → Losing it = cache miss = slower, but correct
  → TTL is fine — expired entry just means a DB fetch

Routing table:
  → Stores the ONLY record of where data lives
  → Losing it = wrong routing = incorrect results, missing data
  → TTL is NOT fine — expired entry means you query the wrong partitions
```

The hot partition registry is a routing table. If `conv_abc123 → max_N=4` expires from Redis, the app server treats the conversation as N=1, queries only `conv_abc123`, and misses all messages in `#1`, `#2`, `#3`. From the user's perspective, recent messages disappear. This is silent data loss — no error, just wrong results.

---

## Requirements for the registry

```
1. Fast reads     → checked on every write and read (~1ms budget)
2. No TTL         → entries must never expire
3. Durable        → survives Redis restart, server crash, power loss
4. N only goes up → writes are always max(current_N, new_N)
```

---

## Redis with AOF persistence

Redis with **AOF (Append Only File)** persistence satisfies all four requirements:

```
Fast reads:    O(1) hash lookup → ~1ms ✓
No TTL:        SET without EXPIRE → entries never expire ✓
Durable:       AOF logs every write to disk → survives restart ✓
N only up:     SET only if new_N > current_N (Lua script for atomicity) ✓
```

How AOF works:

```
Every Redis write → appended to /var/redis/appendonly.aof on disk
Redis restart     → replays AOF file → full recovery of all keys
```

With AOF set to `fsync everysec` (the default), at most 1 second of writes are lost on a crash — acceptable for a routing table that updates infrequently.

For stricter durability, `fsync always` syncs every write to disk before acknowledging — zero data loss but ~10× slower writes. For this registry (updated only when a conversation becomes hot, not on every message), `fsync everysec` is more than adequate.

---

## The atomic N update

The registry must only ever increase N. A race condition where two hot partition service instances both try to update N simultaneously could result in N being set to a lower value:

```
Current max_N = 4
Instance A reads max_N=4, computes new_N=3 (traffic dropped), writes 3  ← wrong
Instance B reads max_N=4, computes new_N=5, writes 5  ← correct
```

Fix: use a Lua script in Redis to make the read-compare-write atomic:

```lua
local current = redis.call('HGET', KEYS[1], 'max_N')
local new_n = tonumber(ARGV[1])
if current == false or tonumber(current) < new_n then
  redis.call('HSET', KEYS[1], 'max_N', new_n)
end
```

This runs atomically — no other Redis command can execute between the read and the write.

---

## Why not the database alone

Storing the registry in DynamoDB instead of Redis seems safe — durable by default, no TTL risk. But:

```
DynamoDB read latency → ~5-10ms
Redis read latency    → ~1ms

Registry is checked on EVERY message write and read.
At 10k WPS:
  DynamoDB registry: 10k × 10ms = 100 seconds of latency per second → impossible
  Redis registry:    10k × 1ms  = 10 seconds of latency per second  → still too much
```

Wait — even Redis at 1ms × 10k WPS = 10,000ms of cumulative latency? That's fine — these are parallel reads, not sequential. 10k concurrent registry lookups each taking 1ms means each message write adds 1ms of latency, not 10 seconds. The math is per-request, not cumulative.

```
Per-request cost:
  Redis registry lookup → 1ms added to each message write
  DynamoDB registry     → 5-10ms added to each message write
```

1ms is acceptable. 5-10ms on every write eats into the 200ms latency SLO meaningfully. Redis wins.

---

> [!tip] Interview framing
> "The registry is a routing table, not a cache — losing it causes silent data loss, not just a cache miss. So no TTL. Redis with AOF persistence gives us fast reads (~1ms), durability across restarts, and no expiry. The Lua script ensures N only ever increases. DynamoDB alone would add 5-10ms per write — too expensive at this scale."
