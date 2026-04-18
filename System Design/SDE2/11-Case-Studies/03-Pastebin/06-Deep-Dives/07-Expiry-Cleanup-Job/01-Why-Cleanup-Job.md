
> [!info] Expired pastes do not delete themselves. The expires_at timestamp marks when a paste should be gone — but nothing in Postgres acts on that automatically. A background cleanup job is required.

---

## The problem

Every paste has an expires_at timestamp. When that timestamp passes, the paste is logically expired — but the row still sits in the pastes table, the content still lives in S3, and if it was recently read, the content is still in Redis.

Nothing removes it automatically. Postgres does not have a built-in TTL mechanism for rows. If you never clean up, you accumulate:

```
3.65B pastes over 10 years
Average expiry: 30 days
Pastes expiring per day: ~100M at peak
```

Without cleanup, the pastes table grows unbounded. Storage costs climb. Query performance degrades as the table fills with dead rows. S3 costs grow as orphaned content accumulates.

The cleanup job exists to reclaim this storage systematically.

---

## What needs to be cleaned up per expired paste

A single expired paste has footprint in three places:

```
1. Postgres pastes table     → row with expires_at < now()
2. Postgres content table    → row with the content hash and s3_url (if ref_count hits 0)
3. S3                        → the actual content blob (if ref_count hits 0)
4. Redis                     → cached content (if the paste was recently read)
```

The cleanup job must handle all four. Missing any one leaves orphaned data that wastes storage or serves stale content.

---

## Scale of the problem

At 1M writes/day peak with a 30-day average expiry:

```
Pastes created per day:    1M
Average TTL:               30 days
Pastes expiring per day:   ~1M (steady state — what comes in must go out)
```

On days where a cohort of 30-day pastes all expire together, you could have several million rows to process. The cleanup job cannot be a simple sequential loop — it must be designed for scale from the start.
