
> [!info] Cache invalidation is the hard part — getting data into cache is easy, keeping it correct is where things break.

---

## Two invalidation cases

There are exactly two ways a cached paste can become invalid:

1. **Expiry** — the paste reaches its `expires_at` time and should no longer be accessible
2. **Manual delete** — the creator deletes the paste before expiry

Each case has a different solution.

---

## Case 1: Expiry — TTL does the work

When you write a paste into Redis, set the TTL to:

```
TTL = expires_at - now
```

For example, if a paste expires in 7 days, the Redis entry TTL is set to 7 days. When the TTL fires, Redis automatically removes the entry. The cache and the database expire in sync, with no background job and no manual coordination.

```
Paste created with 7-day expiry:
  expires_at = now + 7 days
  Redis TTL  = 7 days

After 7 days:
  Redis:    entry auto-deleted by TTL
  Postgres: cleanup job removes the row (or marks deleted_at)
  Result:   cache miss → Postgres returns 404 → client gets 404
```

This is the cleanest possible invalidation — the cache self-manages for the expiry case.

---

## Case 2: Manual delete — explicit invalidation required

When the creator deletes a paste before expiry, the TTL is not enough. If a paste has 29 days left on its TTL and the user deletes it, the Redis entry sits live for 29 more days. Any read during that window hits the cache, gets the content, and returns it — even though the paste was deleted.

**29 days of stale reads is not acceptable.**

The fix is explicit cache invalidation on every manual delete:

```
Delete flow:
  1. Delete row from Postgres  (source of truth)
  2. Delete key from Redis      (synchronous, best effort)
  3. Return 204 to client
```

Step 2 happens synchronously — in the same request, before the response is sent. The paste is removed from both stores before the client receives confirmation.

---

## What if the Redis delete fails?

This is where the SDE-2 and SDE-3 answers diverge.

**SDE-2 answer — retry with exponential backoff:**

If the Redis delete in step 2 fails (network blip, Redis briefly unavailable), retry with exponential backoff — try again after 100ms, then 200ms, then 400ms. This handles transient failures cleanly.

The gap: if the app server crashes mid-retry, the retry is lost. The paste stays in Redis until the TTL fires. Worst case: 30 days of stale reads on a manually deleted paste.

For SDE-2, retry is an acceptable answer because it shows you know invalidation needs to happen and you handle the common failure case (transient Redis error). The crash window is a known limitation.

**SDE-3 answer — outbox pattern:**

The crash window is closed with the outbox pattern:

```
Delete flow:
  1. Begin transaction
  2. Delete row from Postgres
  3. Insert "invalidate cache for shortCode X" into outbox table
  4. Commit transaction  ← both deletes are now durable in one ACID commit
  5. Return 204 to client

Async:
  6. Outbox worker reads event, publishes to Kafka
  7. Cache invalidation service consumes event, deletes from Redis
  8. If step 7 fails, Kafka retries — event is never lost
```

The key insight: the cache invalidation event is committed to the database in the same transaction as the delete. If the app server crashes after step 4, the outbox row survives. The worker picks it up and the cache gets invalidated eventually — no event is lost, no 30-day stale window.

> [!important] The outbox pattern is the correct answer when you need guaranteed cache invalidation — especially for long-TTL entries where stale reads would be a serious correctness issue.

---

## Summary

```
Expiry:        TTL = expires_at - now → Redis auto-expires, no coordination needed
Manual delete: Explicit Redis delete in same request as DB delete
  On failure:
    SDE-2: retry with exponential backoff (crash window exists)
    SDE-3: outbox + Kafka (durable event, crash-safe, eventual invalidation)
```

---

> [!tip] Interview framing
> "Two invalidation cases. Expiry: set Redis TTL to expires_at - now — cache auto-expires in sync with the paste, no extra work needed. Manual delete: synchronous Redis delete in the same request as the DB delete. If Redis delete fails, retry with backoff. SDE-3 answer: outbox pattern — write the invalidation event to an outbox table in the same ACID transaction as the delete, Kafka consumer handles the Redis delete asynchronously with guaranteed delivery."
