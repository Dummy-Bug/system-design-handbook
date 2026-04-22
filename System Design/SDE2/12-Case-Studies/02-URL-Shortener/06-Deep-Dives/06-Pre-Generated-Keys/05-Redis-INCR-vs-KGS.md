
> [!info] Two approaches that eliminate collisions entirely
> Both Redis INCR and the pre-generated key pool solve the collision problem completely. Neither needs a collision check. Neither needs retries. But they have very different trade-offs — and only one is right for a public URL shortener.

---

## Option 1 — Redis INCR counter

Instead of generating random codes and checking for collisions, use Redis as a distributed counter. Every creation request increments the counter and base62-encodes the result.

```
Creation request arrives
→ Redis: INCR url_counter → returns 1000000 (unique, atomic, guaranteed)
→ Base62 encode 1000000:

  1000000 in base62:
  1000000 ÷ 62 = 16129 remainder 22  → 'M'
  16129   ÷ 62 = 260   remainder 9   → '9'
  260     ÷ 62 = 4     remainder 12  → 'C'
  4       ÷ 62 = 0     remainder 4   → '4'

  Result: "4C9M" → pad to 6 chars → "004C9M"

→ INSERT into DB with short_code = "004C9M"
→ Done. Zero collision check. Zero retry.
```

**Why it works:**

Redis is single-threaded. `INCR` is atomic — it increments and returns the new value in a single operation. Two simultaneous calls always get different values. One gets 1000000, the other gets 1000001. No race condition possible.

```
App server 1: INCR → 1000000
App server 2: INCR → 1000001   ← different value, guaranteed
App server 3: INCR → 1000002   ← different value, guaranteed
```

Every counter value is unique by definition. Encoding a unique number always produces a unique code.

**Why it looks attractive:**

No KGS. No pre-generated pool. No background worker to operate. No pool size monitoring. One Redis command and you have a unique short code. It is significantly simpler than the KGS approach.

---

## Why Option 1 gets rejected

**Problem 1 — Codes are predictable and enumerable.**

Counter values are sequential. If a user receives `bit.ly/004C9M`, they know the previous URL was `bit.ly/004C9L` and the next will be `bit.ly/004C9N`. They can walk through the entire sequence and enumerate every URL in the system.

```
User gets:  bit.ly/004C9M
They try:   bit.ly/004C9L → someone else's URL ← exposed
            bit.ly/004C9K → someone else's URL ← exposed
            bit.ly/004C9J → someone else's URL ← exposed
```

For a public URL shortener, users expect privacy. A user who shortens a document link, an internal dashboard, or a pre-announcement page does not expect anyone to discover it by incrementing a counter. Sequential codes make every URL in the system discoverable by any user.

Random codes (KGS approach) have no this problem — knowing one code tells you nothing about any other code.

**Problem 2 — Redis is now a hard SPOF for creation.**

With the INCR approach, every single creation request needs Redis to be alive. If Redis goes down:

```
Redis down
→ INCR fails
→ No counter value available
→ Creation fails immediately
→ Zero fallback
```

With the KGS + pool approach, app servers hold a local batch of 100 pre-fetched keys. Redis going down does not immediately stop creation — app servers drain their local batch first, buying time:

```
Redis down
→ App servers use local batch (100 keys each, 20 servers = 2000 keys)
→ At 1k creations/sec → ~2 seconds of local runway
→ Plus Redis circuit breaker kicks in
→ Graceful degradation instead of hard failure
```

The pool approach treats Redis as a supply chain, not a live dependency. The INCR approach makes Redis a hard blocker on every single creation request.

---

## Option 2 — Pre-generated key pool + KGS (the right approach)

The KGS generates keys sequentially (same uniqueness guarantee as INCR, same base62 math), stores them in a Redis pool in advance, and app servers LPOP keys on demand.

```
Creation request arrives
→ App server pops key from local batch (pre-fetched from Redis pool)
→ INSERT into DB
→ Done. Zero Redis call on hot path. Zero collision check. Zero retry.
```

**What it fixes:**

```
Predictability:  KGS generates sequential codes internally but shuffles
                 the pool — or generates in random order — before pushing
                 to Redis. Codes handed to users are not sequential.

Redis SPOF:      App servers pre-fetch 100 keys locally. Redis down
                 → local batch still works → graceful degradation.

Simplicity cost: KGS is a 50-line background worker. Monitoring pool
                 size is one metric. The operational overhead is minimal.
```

---

## Side by side

| | Redis INCR | KGS + Pool |
|---|---|---|
| Collision checks | None | None |
| Code predictability | Sequential — enumerable | Random — private |
| Redis failure impact | Creation fails instantly | Local batch buys time |
| Operational complexity | Very simple | Small background worker |
| Right for | Internal tools, no privacy concern | Public URL shortener |

---

> [!tip] Interview framing
> "Redis INCR is a clean approach — atomic, no collisions, no KGS needed. But two problems: codes are sequential and enumerable (privacy violation for a public shortener), and Redis is a hard SPOF on every creation. KGS + pool solves both — random code order from the pool, and app servers pre-fetch locally so Redis failure doesn't immediately break creation. For a public URL shortener, KGS wins."
