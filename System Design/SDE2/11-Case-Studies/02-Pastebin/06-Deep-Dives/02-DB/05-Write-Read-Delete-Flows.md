
> [!info] Flows are where schema decisions get tested — every column and index must serve at least one flow.
> If a flow is slow or broken, trace it back to the schema.

---

## Write Flow — Creating a Paste

```
1. Client sends POST /api/v1/pastes with content + expiryDays + optional customAlias
   JWT in header identifies the user → extract user_id

2. App server hashes the content:
   content_hash = SHA-256(paste_text)

3. Check if content already exists:
   SELECT 1 FROM content WHERE content_hash = ?

   → EXISTS:
     UPDATE content SET ref_count = ref_count + 1 WHERE content_hash = ?
     (content already in S3, skip upload)

   → NOT EXISTS:
     INSERT INTO content (content_hash, s3_url, ref_count) 
     VALUES (?, 'PENDING', 1)
     Upload paste_text to S3 async → on completion: UPDATE content SET s3_url = ? 
     ⚠ Risk: s3_url is null/PENDING during upload window (covered below)

4. Generate short_code:
   → customAlias provided: check it's not taken in pastes table, use it
   → no alias: generate random 8-char Base62 code

5. INSERT INTO pastes (short_code, user_id, content_hash, expires_at, created_at)
   expires_at = NOW() + INTERVAL '? days'  (1, 7, or 30)

6. Return short_code to client → 200 OK
```

> [!danger] The async S3 upload window
> Between step 3 (content row inserted with s3_url = 'PENDING') and S3 upload completing, a read for that paste will find the content row but get a null/PENDING s3_url. The app server must handle this case — either return a 503 "content not ready yet", or make the S3 upload synchronous before returning the short_code. Synchronous upload adds latency to writes (~100-200ms for a 10KB file) but eliminates the inconsistency window. Given our write SLO is p99 < 100ms, this is worth flagging as a deep dive decision.

---

## Read Flow — Viewing a Paste

```
1. Client sends GET /api/v1/pastes/:shortCode (no auth required)

2. App server queries pastes table:
   SELECT p.short_code, p.content_hash, p.expires_at, p.deleted_at, c.s3_url
   FROM pastes p
   JOIN content c ON p.content_hash = c.content_hash
   WHERE p.short_code = ?

3. Check validity:
   → Row not found       → 404
   → deleted_at IS SET   → 404 (treat deleted same as not found)
   → expires_at < NOW()  → 404 (expired — treat same as not found)

4. Fetch paste text from S3 using c.s3_url

5. Return to client:
   { data: { content: text, expiresAt: expires_at }, error: null }
```

**Why merge 404 cases?**
Returning different error codes for "not found", "deleted", and "expired" leaks information — an attacker could enumerate which short codes ever existed and infer when pastes were created or deleted. A single 404 for all three cases reveals nothing.

**Read-your-own-writes:**
The creator may read their paste immediately after creation — before read replicas have synced. To guarantee they see their paste, route their first read (within a short window after creation, identified by JWT) to the primary DB. By the time they share the link externally, replicas have caught up.

---

## Delete Flow — Removing a Paste

```
1. Client sends DELETE /api/v1/pastes/:shortCode (auth required)
   JWT identifies the caller → extract caller_user_id

2. Look up the paste:
   SELECT user_id, content_hash FROM pastes 
   WHERE short_code = ? AND deleted_at IS NULL

   → Row not found or already deleted → return 204 immediately (idempotent)

3. Authorisation check:
   IF paste.user_id != caller_user_id → return 403 Forbidden

4. Execute in a single transaction:
   BEGIN;
     UPDATE pastes SET deleted_at = NOW() WHERE short_code = ?;
     UPDATE content SET ref_count = ref_count - 1 WHERE content_hash = ?;
     -- check if ref_count hit zero
     SELECT ref_count FROM content WHERE content_hash = ?;
   COMMIT;

5. If ref_count = 0:
   DELETE FROM content WHERE content_hash = ?
   Schedule S3 blob deletion (async, background job)

6. Return 204 No Content
```

**Why soft delete instead of hard delete?**
Soft delete (setting `deleted_at`) is instant — a single column update. Hard delete involves cascading checks, potential FK constraint violations, and makes the operation non-reversible. Soft delete also preserves audit history. A background cleanup job handles physical row removal later.

**Why the transaction wraps UPDATE pastes + UPDATE content?**
If the ref_count decrement succeeds but the pastes soft-delete fails (or vice versa), the DB is in an inconsistent state — ref_count doesn't match the actual number of active pastes rows. The transaction guarantees both happen or neither does.

---

## Expiry Cleanup — Background Job

A nightly job scans for pastes that have expired or been soft-deleted:

```sql
SELECT short_code, content_hash 
FROM pastes 
WHERE expires_at < NOW() OR deleted_at IS NOT NULL;
```

For each result:
1. Decrement `ref_count` on the content row
2. If `ref_count = 0`: delete content row + schedule S3 blob deletion
3. Hard-delete the paste row (or archive to cold storage)

This job runs on the `expires_at` index — fast range scan, not a full table scan.

---

> [!tip] Interview framing
> "Write: hash content → check if exists → increment ref_count or insert new → generate short_code → insert paste row → return short_code. Read: lookup by short_code → check not deleted/expired → fetch from S3 → return. Delete: verify ownership → soft delete paste row + decrement ref_count in one transaction → if ref_count=0 schedule S3 cleanup. All 404 cases (not found / deleted / expired) return the same error to avoid leaking existence information."
