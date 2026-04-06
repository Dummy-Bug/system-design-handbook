# Event-Driven Invalidation

> [!info] Invalidate the cache key the moment the DB is updated. Zero stale window — the cache is always fresh.

---

## How it works

```
User updates profile picture
→ write to DB ✓
→ DELETE cache key "user:123:profile" immediately
→ next read → cache miss → fetches fresh from DB → repopulates ✓
```

The moment the DB is written, the corresponding cache key is deleted (or updated). Any subsequent read gets fresh data.

---

## What's good

```
Zero stale window       → cache invalidated the instant DB changes
No time-based drift     → doesn't rely on guessing a good TTL
Reacts to real changes  → not just the passage of time
```

---

## What's bad

```
One slow request after every write  → delete → miss → repopulate
                                       that first read after invalidation hits DB
Needs infrastructure                → who triggers the invalidation?
Miss on targeted invalidation       → if you forget to invalidate a key on one code path,
                                       that key stays stale indefinitely
```

---

## How to trigger the invalidation

Three approaches, in order of increasing sophistication:

**1. App code (simplest):**
```
// After every DB write, delete the cache key
db.update(user);
cache.delete("user:" + userId + ":profile");
```
Simple but brittle — you must remember to delete the right key on every code path that writes to the DB. Miss one path and you have a permanently stale key.

**2. Message queue:**
```
Write service publishes event → "user:123 updated"
Cache invalidation service subscribes → deletes "user:123:profile"
```
Decoupled — the write service doesn't need to know about the cache. But the event must be reliably delivered.

**3. CDC (most reliable):**
```
Debezium reads Postgres WAL → detects row update → publishes event to Kafka
Cache invalidation consumer → receives event → deletes Redis key
```
The most robust approach — CDC catches every DB change regardless of which code path made it. You can't forget to publish the event because CDC reads directly from the WAL. Covered in depth in the CDC section.

---

## Delete vs Update

On invalidation, you have two choices:

**Delete the key** — next read is a miss, fetches fresh from DB:
```
Safer — you can never serve stale data after the delete
Miss on first read after write — slight latency spike
```

**Update the key with new value** — this is Write-Through (covered in the next file):
```
No miss after write — faster for read-heavy data
Risk of race condition if cache update fails after DB write
```

For most systems, **delete on invalidation** is safer. The one cold miss after a write is acceptable.
