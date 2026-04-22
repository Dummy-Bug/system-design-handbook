# Redis Data Structures

> [!info] Redis is an in-memory data store. Everything lives in RAM. That's why it's fast — no disk, no file system, just memory.

```mermaid
flowchart LR
    A["DB query<br/>~10ms<br/>disk I/O + query planning + network"] -->|"100x faster"| B["Redis GET<br/>~0.1ms<br/>RAM lookup + network hop"]
    style A fill:#f8d7da,stroke:#dc3545,color:#000
    style B fill:#d4edda,stroke:#28a745,color:#000
```

A natural question: isn't a file sitting on the same server's disk faster than a network hop to Redis?

```mermaid
flowchart LR
    A["Same server disk<br/>1–10ms<br/>seek time + OS page cache + storage controller"]
    B["Redis over network<br/>~0.1ms<br/>network + RAM lookup"]
    A -->|"Redis still wins"| B
    style A fill:#f8d7da,stroke:#dc3545,color:#000
    style B fill:#d4edda,stroke:#28a745,color:#000
```

Disk I/O has to physically move through layers — storage controller, kernel buffers, OS scheduling. A network hop to a RAM store skips all of that.

The only thing faster than Redis is local in-process cache — that's why two-level caching exists:

```mermaid
flowchart LR
    A["Local RAM<br/>nanoseconds<br/>no network at all"] -->|slower| B["Redis<br/>~0.1ms<br/>shared across all servers"] -->|slower| C["Same server disk<br/>1–10ms"] -->|slower| D["DB<br/>10–100ms<br/>disk + query planning"]
    style A fill:#d4edda,stroke:#28a745,color:#000
    style B fill:#c3e6cb,stroke:#28a745,color:#000
    style C fill:#fff3cd,stroke:#ffc107,color:#000
    style D fill:#f8d7da,stroke:#dc3545,color:#000
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

HGET user:123 name      → "John"
HGETALL user:123        → { name: John, age: 28, city: NYC }
HSET user:123 city "LA" ← update one field, nothing else touched
```

**Why not just serialize the whole object to JSON and store as a String?**

At 10 million users, 1 million city updates per day:

```mermaid
flowchart LR
    subgraph String["String approach — wasteful"]
        S1["GET user:123<br/>fetch entire 1KB JSON"] --> S2["Deserialize + update city<br/>in app memory"]
        S2 --> S3["SET user:123<br/>write entire 1KB back"]
        S3 --> S4["1M updates × 2KB = 2GB<br/>wasted network traffic/day"]
        style S4 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph Hash["Hash approach — efficient"]
        H1["HSET user:123 city 'LA'<br/>~10 bytes on the wire"]
        H1 --> H2["1M updates × 10 bytes = 10MB/day<br/>200x less data ✓"]
        style H2 fill:#d4edda,stroke:#28a745,color:#000
    end
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

```mermaid
flowchart LR
    subgraph DB["DB approach"]
        D1["SELECT * FROM notifications<br/>WHERE user_id = 123<br/>ORDER BY created_at DESC LIMIT 10"]
        D1 --> D2["index lookup + disk read + sort<br/>~10ms per request"]
        D2 --> D3["at 1M reads/sec → DB hammered ✗"]
        style D3 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph List["List approach"]
        L1["LRANGE notifications:user:123 0 9"]
        L1 --> L2["already ordered, already in RAM<br/>~0.1ms"]
        L2 --> L3["100x faster, DB never touched ✓"]
        style L3 fill:#d4edda,stroke:#28a745,color:#000
    end
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

```mermaid
flowchart LR
    subgraph L["List"]
        L1["fetch entire list"] --> L2["find alice"] --> L3["update score"] --> L4["re-sort entire list<br/>O(n log n) ✗"]
        style L4 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph SS["Sorted Set"]
        S1["ZADD leaderboard 10000 'alice'<br/>position updated automatically<br/>O(log n) ✓"]
        style S1 fill:#d4edda,stroke:#28a745,color:#000
    end
```

**Why not a DB?**

50 million players, scores updating every few seconds:

```mermaid
flowchart LR
    subgraph DB["DB"]
        D1["UPDATE scores SET score = 10000 WHERE user = 'alice'"]
        D1 --> D2["SELECT ORDER BY score DESC LIMIT 10"]
        D2 --> D3["disk write + sort on every update<br/>collapses at scale ✗"]
        style D3 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph SortedSet["Sorted Set"]
        S1["ZADD leaderboard 10000 'alice'"] --> S2["ZRANGE leaderboard 0 9"]
        S2 --> S3["all in RAM, always sorted<br/>milliseconds ✓"]
        style S3 fill:#d4edda,stroke:#28a745,color:#000
    end
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

```mermaid
flowchart LR
    subgraph L["List"]
        L1["Scan 1 million entries<br/>to check if alice already exists<br/>O(n) ✗"]
        style L1 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph S["Set"]
        S1["SADD handles uniqueness automatically<br/>O(1) ✓"]
        style S1 fill:#d4edda,stroke:#28a745,color:#000
    end
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

**Why not just store every viewer in a Set?**

```mermaid
flowchart LR
    A["1 video, 5M viewers<br/>5M × 50 bytes = 250MB"] --> B["YouTube has 800M videos<br/>1M popular videos × 100K viewers × 50 bytes"]
    B --> C["= 5 petabytes<br/>just for view counts ✗"]
    style C fill:#f8d7da,stroke:#dc3545,color:#000
```

**How HyperLogLog works — the leading zeros trick:**

Every user ID gets hashed into a binary number. Hash functions produce random-looking output, so leading zeros follow a probability pattern:

```
hash("user:1")      → 00110101...   (2 leading zeros)
hash("user:2")      → 00001101...   (4 leading zeros)
hash("user:3")      → 10110010...   (0 leading zeros)
hash("user:99999")  → 00000001...   (7 leading zeros)
```

Leading zeros get rarer the longer they are:

```mermaid
flowchart LR
    A["1 leading zero<br/>1 in 2 hashes<br/>common"] --> B["5 leading zeros<br/>1 in 32 hashes<br/>rare"] --> C["10 leading zeros<br/>1 in 1,024 hashes<br/>very rare"] --> D["20 leading zeros<br/>1 in 1M hashes<br/>extremely rare"]
    style A fill:#d4edda,stroke:#28a745,color:#000
    style B fill:#c3e6cb,stroke:#28a745,color:#000
    style C fill:#fff3cd,stroke:#ffc107,color:#000
    style D fill:#f8d7da,stroke:#dc3545,color:#000
```

HyperLogLog only remembers **one number** — the maximum leading zeros seen so far:

```
Processed 1,000,000 user IDs
→ rarest hash seen had 20 leading zeros
→ 20 leading zeros happens ~1 in 1,000,000 times
→ estimate: ~1,000,000 unique users ✓

Memory used: just the number "20" — a few bytes
```

**Why 12KB and not just a few bytes?**

Tracking one global max is too noisy:

```mermaid
flowchart LR
    A["Only 100 people watched<br/>but one hash had 20 leading zeros by luck"] --> B["Estimate: 1,000,000 viewers<br/>Actual: 100 viewers ✗"]
    style B fill:#f8d7da,stroke:#dc3545,color:#000
```

The fix: split users into **16,384 buckets**, track max per bucket, then average:

```
Bucket 1      → max = 18
Bucket 2      → max = 19
Bucket 3      → max = 3   ← lucky outlier, averaged out
Bucket 4      → max = 20
...
Bucket 16,384 → max = 17

Average across all buckets → stable, accurate estimate
One lucky outlier barely moves the average
```

```
16,384 buckets × 6 bits per bucket (leading zeros on 64-bit hash fits in 6 bits)
= 98,304 bits = 12KB — fixed forever, whether 1 user or 1 billion
```

**Why Redis and not just write to a DB?**

```mermaid
flowchart LR
    subgraph DB["DB"]
        D1["Every page load fires INSERT"] --> D2["Millions of writes/sec"] --> D3["DB collapses ✗"]
        style D3 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph Redis["Redis"]
        R1["Every page load fires PFADD"] --> R2["RAM write, millions/sec easy"] --> R3["Read count once at end of day ✓"]
        style R3 fill:#d4edda,stroke:#28a745,color:#000
    end
```

```
PFADD visitors:2026-04-04 "user:1" ... "user:5000000"
PFCOUNT visitors:2026-04-04 → ~5,000,000

Memory: always 12KB — whether 1 user or 1 billion
Error:  ~0.81% — 5,000,000 might come back as 5,040,500. Acceptable for view counts.
```

> [!important] HyperLogLog tells you HOW MANY unique items — not WHICH ones. You get the count, never the list.

> [!tip] More buckets = more accuracy = more memory. Redis chose 16,384 as the sweet spot — 0.81% error at just 12KB.

**Use for:** unique visitors, distinct search queries, video view counts — anything where approximate is fine and memory matters.

---

## Bitmap

**The problem:** track which users logged in today. Three possible solutions.

**Solution 1 — Redis Set**

```
SADD active:2026-04-04 "user:123"
SADD active:2026-04-04 "user:456"

Memory: 5M users × 50 bytes = 250MB/day
```

**Solution 2 — User ID as key, 1/0 as value**

```
SET active:2026-04-04:123  1
SET active:2026-04-04:456  1
SET active:2026-04-04:789  0

Memory: 5M users × ~60 bytes = 300MB/day  ← worse than Set
```

Each key carries Redis overhead — key string + value + metadata per entry.

**Solution 3 — Bitmap**

One key, one array. The array is indexed by user ID — just like a boolean array in DSA:

```java
boolean[] active = new boolean[100_000_000];

active[123] = true;   // user 123 logged in
active[456] = true;   // user 456 logged in
active[789] = false;  // user 789 didn't log in
```

Redis Bitmap is exactly this — but instead of `boolean` (1 byte each in Java), it uses actual bits (8x smaller):

```mermaid
flowchart LR
    K["active:2026-04-04"] --> A["pos 0<br/>0"]
    K --> B["pos 1<br/>0"]
    K --> C["pos 2<br/>0"]
    K --> D["..."]
    K --> E["pos 123<br/>1 ✓"]
    K --> F["..."]
    K --> G["pos 456<br/>1 ✓"]
    K --> H["..."]
    K --> I["pos N<br/>0"]
    style E fill:#d4edda,stroke:#28a745,color:#000
    style G fill:#d4edda,stroke:#28a745,color:#000
    style A fill:#f8f9fa,stroke:#adb5bd,color:#000
    style B fill:#f8f9fa,stroke:#adb5bd,color:#000
    style C fill:#f8f9fa,stroke:#adb5bd,color:#000
    style I fill:#f8f9fa,stroke:#adb5bd,color:#000
```

```
SETBIT active:2026-04-04 123 1    ← user 123 logged in
SETBIT active:2026-04-04 456 1    ← user 456 logged in

GETBIT active:2026-04-04 123  → 1    ← did user 123 log in? yes
GETBIT active:2026-04-04 789  → 0    ← did user 789 log in? no
BITCOUNT active:2026-04-04    → 2    ← total active users today
```

**How big is the array?**

The array size is determined by the **highest user ID**, not the number of logged-in users:

```
Highest user ID = 100,000,000
→ array needs 100M positions
→ 100M bits ÷ 8 = 12.5MB — fixed forever
```

Once sized, adding 1 active user or 80M active users costs zero extra memory:

```
Day 1: 1M users log in    → 12.5MB
Day 2: 80M users log in   → 12.5MB
Day 3: 1 user logs in     → 12.5MB
```

**All three compared:**

```mermaid
flowchart LR
    subgraph Comparison["Memory — 5M users, highest ID = 100M"]
        A["Set<br/>250MB<br/>scales with active users today"]
        B["Key/Value<br/>300MB<br/>scales with active users today"]
        C["Bitmap<br/>12.5MB fixed<br/>scales only with highest user ID ✓"]
    end
    style A fill:#f8d7da,stroke:#dc3545,color:#000
    style B fill:#f8d7da,stroke:#dc3545,color:#000
    style C fill:#d4edda,stroke:#28a745,color:#000
```

> [!important] The position IS the user ID. You never store the ID itself — user 123's answer simply lives at position 123 in the array. That's where all the savings come from.

> [!tip] Whenever you see a DSA problem using a boolean array indexed by ID — that's a bitmap in disguise.

**The one constraint:** user IDs must be integers. You can't do `SETBIT active "alice"` — you need `SETBIT active 123`. UUID-based systems need a mapping layer first.

**Use for:** daily active users, feature flags per user (is user 123 in the beta?), any yes/no fact per user.

---

## HyperLogLog vs Bitmap

> [!important] Two different questions — don't mix them up.

```mermaid
flowchart LR
    subgraph HLL["HyperLogLog"]
        H1["How many unique users visited today?<br/>→ gives you a count<br/>cannot ask 'did user 123 visit?'"]
    end
    subgraph BM["Bitmap"]
        B1["Did user 123 visit today?<br/>→ yes/no per specific user<br/>+ total count via BITCOUNT"]
    end
    style HLL fill:#fff3cd,stroke:#ffc107,color:#000
    style BM fill:#d4edda,stroke:#28a745,color:#000
```

---

## Summary

| Data Structure | Best for | Key commands |
|---|---|---|
| String | Single value, atomic counters | `SET` / `GET` / `INCR` |
| Hash | Object fields, update one at a time | `HSET` / `HGET` / `HGETALL` |
| List | Ordered, push/pop, feeds, queues | `LPUSH` / `LRANGE` |
| Sorted Set | Scored + auto-sorted, leaderboards | `ZADD` / `ZRANGE` |
| Set | Unique members, set operations | `SADD` / `SCARD` / `SINTER` |
| HyperLogLog | Approximate unique count, fixed 12KB | `PFADD` / `PFCOUNT` |
| Bitmap | Yes/no per user, minimal memory | `SETBIT` / `GETBIT` / `BITCOUNT` |
