# Cache Penetration

> [!info] Requests for keys that don't exist in the DB. Every request is a cache miss. Every request hits the DB. DB returns null. Nothing gets cached. The cycle repeats forever.

---

## Why it's different from a normal cache miss

A normal cache miss eventually resolves itself:

```
Normal miss:
  → cache miss → DB returns data → store in cache
  → next request → cache hit ✓
  → self-healing
```

Cache penetration never resolves:

```
Penetration:
  GET /user/99999999  (user doesn't exist)
  → cache miss
  → DB returns null
  → nothing to cache  ← this is the key difference
  → next request → cache miss again
  → DB again → null again → nothing cached
  → infinite loop
```

At 1,000 requests/second for non-existent keys, that's 1,000 DB queries/second all returning null. The DB does real work (table scan, index lookup) for zero useful result.

---

## Common causes

```
Malicious attack    → attacker deliberately queries non-existent IDs
                      to exhaust DB connections
Bugs in code        → generating invalid IDs, wrong join keys
Deleted records     → data existed once but was deleted;
                      cache wasn't invalidated and now DB has nothing
```

---

## Fix 1 — Cache the Null

```
DB returns null for user:99999999
→ cache.set("user:99999999", NULL, TTL=60s)   ← cache the absence

Next 1,000 requests for user:99999999:
→ cache hit → return null immediately ✓
→ DB sees zero queries ✓
```

Keep the TTL short on null entries. If the record gets created later, the null expires and real data gets cached on the next request.

**The risk:** memory consumption from null entries. If an attacker queries millions of different non-existent IDs, you fill your cache with null entries. Set a very short TTL (30-60 seconds) and monitor cache memory usage.

---

## Fix 2 — Bloom Filter (better for attacks)

A Bloom filter answers: "has this key ever been inserted into the DB?"

```
Request arrives for user:99999999
→ check Bloom filter: "has user:99999999 ever been inserted?"
→ NO (definitely not) → return 404 immediately ✓
   → cache never touched, DB never touched

→ YES (or maybe) → proceed normally to cache → DB
```

**Why Bloom filters work here:**
- **No false negatives** — if the filter says NO, the key definitely doesn't exist. Safe to reject immediately.
- **Possible false positives** — the filter might say YES for a key that doesn't exist, but the rate is very low and controllable (< 1%).
- **Space-efficient** — a Bloom filter for 100 million keys fits in ~120MB. Storing those same keys in a hash set would take gigabytes.

Put the Bloom filter in front of the cache layer. Non-existent keys never reach cache or DB at all.

> [!tip] Bloom filters in production
> Cassandra, HBase, and PostgreSQL all use Bloom filters internally to avoid disk lookups for non-existent keys. The pattern is well-established.

---

## Which fix to use

```
Cache null values   → simple, works for small datasets, short-lived fix
                      vulnerable to memory exhaustion under attack
Bloom filter        → better under attack, scales to billions of keys
                      more infrastructure, requires periodic rebuilding
                      as new records are inserted
```

For a system under active attack or with adversarial input, Bloom filter is the correct answer.
