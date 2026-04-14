
> [!info] The cleanup job processes expired pastes in batches — not one at a time. Each batch handles the full deletion chain: ref_count, S3, content table, pastes table, and Redis.

---

## Why batches, not row-by-row

Processing one paste at a time means:
- One Postgres query per paste
- One S3 delete call per paste
- One Redis delete call per paste

At 1M expirations per day, that's 1M individual S3 API calls. S3 charges per API call. More importantly, at ~10ms per S3 call, processing 1M pastes sequentially takes ~3 hours just on S3 round trips alone.

Batch processing collapses this:
- One Postgres query fetches 1000 expired rows
- One S3 batch delete removes up to 1000 objects in a single API call (S3 native batch delete API)
- One Redis pipeline deletes 1000 keys in a single round trip

The same work happens in a fraction of the time at a fraction of the cost.

---

## The full cleanup flow per batch

```
1. SELECT short_code, content_hash FROM pastes
   WHERE expires_at < now()
   AND status = 'NOT_EXPIRED'
   LIMIT 1000

2. For each row:
   → UPDATE content SET ref_count = ref_count - 1
     WHERE content_hash = ?

3. Collect content_hashes where ref_count = 0 after decrement

4. If any ref_count = 0:
   → S3 batch delete (up to 1000 objects in one API call)
   → DELETE FROM content WHERE content_hash IN (...)

5. DELETE FROM pastes WHERE short_code IN (...)

6. Redis pipeline: DEL shortCode1 shortCode2 ... shortCode1000
```

---

## Why ref_count matters

Multiple paste rows can point to the same S3 object — the dedup mechanism ensures identical content is stored once. ref_count tracks how many paste rows reference that content.

You only delete from S3 and the content table when ref_count hits 0. If two pastes share the same content and one expires, the S3 object stays — the other paste still needs it.

```
Paste A (expires today) → content_hash: abc123, ref_count: 2
Paste B (expires next month) → content_hash: abc123

Cleanup runs:
  Decrement ref_count for abc123 → ref_count = 1
  ref_count != 0 → do NOT delete S3 object
  Delete pastes row for Paste A only
```

Only when Paste B also expires and ref_count drops to 0 does the S3 object get deleted.

---

## Redis invalidation

The cleanup job deletes Redis keys for all expired shortCodes in the batch, regardless of whether the content was actually in Redis. Redis DEL on a non-existent key is a no-op — safe to call unconditionally.

This ensures no stale cached content survives past expiry.
