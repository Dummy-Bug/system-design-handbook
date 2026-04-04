# Redis Data Structures

> [!info] Redis is an in-memory data store. Everything lives in RAM. That's why it's fast — no disk, no file system, just memory.

```
DB query  → ~10ms   (disk I/O, query planning, network)
Redis get → ~0.1ms  (RAM lookup, network hop)

100x faster than the DB
```

A natural question: isn't a file sitting on the same server's disk faster than a network hop to Redis?

```
Same server disk  → 1–10ms   (seek time, OS page cache, storage controller)
Redis over network → ~0.1ms  (network + RAM lookup)

Redis wins. Network is faster than disk.
```

Disk I/O has to physically move through layers — storage controller, kernel buffers, OS scheduling. A network hop to a RAM store skips all of that. The RAM lookup itself is so fast that even with network overhead it still wins.

The only thing faster than Redis is local in-process cache — that's why two-level caching exists:

```
Local RAM (same process) → nanoseconds   ← fastest, no network at all
Redis (network hop)      → ~0.1ms        ← fast, shared across all servers
Same server disk         → 1–10ms
DB (disk + query)        → 10–100ms      ← slowest
```

Redis is essentially **shared RAM over the network**. All your servers read and write to one place, so they all see consistent data. Local cache can't do that — if Server 1 updates a value, Server 2 still has the old one.

---

> [!info] Redis isn't just a key-value store that holds strings. It has built-in data structures — each one solves a specific problem at scale that a plain string or a DB query can't handle efficiently.

---

## String

The simplest structure. Key maps to a single value.

```
SET user:123:name "John"
GET user:123:name → "John"
```

Strings can also act as atomic counters:

```
INCR page:views → 1
INCR page:views → 2
INCR page:views → 3
```

One command, atomic. No race conditions. This is how Redis handles like counts, view counts, and rate limiting counters.

**Use for:** cached values, session tokens, counters.

---

## Hash

Key maps to a mini key-value map. Perfect for objects with multiple fields.

```
HSET user:123 name "John" age 28 city "NYC"

HGET user:123 name     → "John"
HGETALL user:123       → { name: John, age: 28, city: NYC }
HSET user:123 city "LA"  ← update one field, nothing else touched
```

**Why not just serialize the whole object to JSON and store as a String?**

At 10 million users, 1 million city updates per day:

```
String approach:
  GET user:123          → fetch entire 1KB JSON over network
  deserialize + update  → in app memory
  SET user:123          → write entire 1KB back

  1M updates × 1KB GET + 1KB SET = 2GB of wasted network traffic per day
  just to change one field

Hash approach:
  HSET user:123 city "LA"
  1M updates × ~10 bytes = 10MB
  200x less data on the wire, same result
```

**Use for:** user profiles, product details, shopping carts.

---

## List

An ordered list of strings. Push to front or back, read a range.

```
LPUSH notifications:user:123 "someone liked your post"
LPUSH notifications:user:123 "someone followed you"

LRANGE notifications:user:123 0 9  → last 10 notifications, newest first
```

Already ordered because you push newest items to the front. No sorting needed at read time.

**Why not a DB table?**

50 million users × 100 notification events/day = 5 billion rows.

```
DB approach:
  SELECT * FROM notifications WHERE user_id = 123
  ORDER BY created_at DESC LIMIT 10
  → index lookup + disk read + sort → ~10ms per request
  → at 1M reads/sec → DB hammered

List approach:
  LRANGE notifications:user:123 0 9
  → already ordered, already in RAM → ~0.1ms
  → 100x faster, DB never touched
```

**Use for:** notification feeds, activity logs, recent history, task queues.

---

## Sorted Set

Like a Set but every member has a **score**. Redis keeps members sorted by score automatically.

```
ZADD leaderboard 9500 "alice"
ZADD leaderboard 8200 "bob"
ZADD leaderboard 9800 "charlie"

ZRANGE leaderboard 0 2 WITHSCORES → charlie(9800), alice(9500), bob(8200)
```

**Why not a List?**

Alice scores 500 more points:

```
List:        fetch → find alice → update → re-sort entire list → write back → O(n log n)
Sorted Set:  ZADD leaderboard 10000 "alice" → position updated automatically → O(log n)
```

**Why not a DB?**

50 million players, scores updating every few seconds:

```
DB:          UPDATE + SELECT ORDER BY on every update
             → disk write + sort every time → collapses at scale

Sorted Set:  ZADD + ZRANGE → all in RAM, always sorted → milliseconds
```

> [!tip] The Z prefix has no deep meaning — "S" was already taken by Sets. The original author needed a letter. Historical accident, don't look for logic.

**Use for:** leaderboards, trending posts, rate limiting (score = timestamp).

---

## Set

An unordered collection of unique strings. Duplicates ignored automatically.

```
SADD post:123:likes "alice"
SADD post:123:likes "bob"
SADD post:123:likes "alice"   ← duplicate, silently ignored

SCARD post:123:likes → 2
```

**Why not a List?**

Post has 1 million likes. Alice tries to like it again:

```
List:  scan 1 million entries to check if alice already exists → O(n)
Set:   SADD handles uniqueness automatically                   → O(1)
```

**The killer feature — set operations:**

```
SINTER followers:alice followers:bob  → mutual followers
SUNION followers:alice followers:bob  → everyone either follows
SDIFF  followers:alice followers:bob  → alice follows but bob doesn't
```

Finding mutual friends via a DB join is expensive at scale. `SINTER` in Redis is a RAM operation — milliseconds.

**Use for:** likes, tags, mutual friends, unique visitors.

---

## HyperLogLog

Counts unique items **approximately** using fixed memory regardless of input size.

The naive approach — store every visitor in a Set:

```
SADD visitors:2026-04-04 "user:1" ... "user:5000000"
SCARD visitors:2026-04-04 → 5,000,000

Memory: 5M users × 10 bytes = 50MB/day × 365 = 18GB/year
Just to store one count per day
```

HyperLogLog:

```
PFADD visitors:2026-04-04 "user:1" ... "user:5000000"
PFCOUNT visitors:2026-04-04 → ~5,000,000

Memory: always 12KB — whether 1 user or 1 billion
```

The catch: ~0.81% error rate. 5,000,000 might come back as 5,040,500. For unique visitor counts, perfectly acceptable.

**Why Redis and not just write to a DB?**

Every page load fires an event — millions per second across thousands of servers:

```
DB:     INSERT into visits ... → millions of writes/sec → DB collapses
Redis:  PFADD → RAM write → handles millions/sec easily
```

Redis absorbs the write spike. Read the count once at end of day, persist it somewhere permanent if needed.

> [!important] HyperLogLog tells you HOW MANY unique items — not WHICH ones. You get the count, not the list.

**Use for:** unique visitors, distinct search queries — anything where approximate is fine and memory matters.

---

## Bitmap

Tracks a yes/no fact per user using one **bit** per user ID position.

Classic use case — did this user log in today?

```
SETBIT active:2026-04-04 123 1   ← user 123 logged in today
SETBIT active:2026-04-04 456 1   ← user 456 logged in today

GETBIT active:2026-04-04 123     → 1 (active)
GETBIT active:2026-04-04 789     → 0 (not active)
BITCOUNT active:2026-04-04       → total active users today
```

Memory at 5 million users:

```
Hash approach  → ~50MB
Bitmap         → 5,000,000 bits = 625KB   (80x less)
```

**Use for:** daily active users, feature flags per user (is user 123 in the beta?), any yes/no fact per user.

---

## HyperLogLog vs Bitmap

> [!important] Two different questions — don't mix them up.
> ```
> HyperLogLog → "how many unique users did X?"  → count only, not who
> Bitmap      → "did user 123 do X?"            → yes/no per specific user
> ```

---

## Summary

```
String       → single value, atomic counters              SET / GET / INCR
Hash         → object fields, update one at a time        HSET / HGET / HGETALL
List         → ordered, push/pop, feeds, queues           LPUSH / LRANGE
Sorted Set   → scored + auto-sorted, leaderboards         ZADD / ZRANGE
Set          → unique members, set operations             SADD / SCARD / SINTER
HyperLogLog  → approximate unique count, fixed 12KB       PFADD / PFCOUNT
Bitmap       → yes/no per user, minimal memory            SETBIT / GETBIT / BITCOUNT
```
