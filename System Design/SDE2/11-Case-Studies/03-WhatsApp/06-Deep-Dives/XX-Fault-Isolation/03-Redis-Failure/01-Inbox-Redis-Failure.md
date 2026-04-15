
> [!info] Inbox Redis shard failure — fallback to DynamoDB
> The inbox sorted sets are sharded across 10 Redis primaries. If one shard goes down, the users mapped to that shard can no longer load their inbox from cache. The fallback is a direct read from the conversations table in DynamoDB.

---

## What breaks

Each inbox sorted set stores the top K conversations for a user — conversation IDs ranked by last message timestamp. When a user opens WhatsApp, the app server reads their sorted set to render the inbox.

If the Redis shard for a user goes down:

```
Alice opens inbox
→ App server: ZREVRANGE inbox:alice 0 19 → connection error (shard down)
→ No inbox data returned
→ Alice sees a blank inbox or an error
```

With 10 shards, one shard going down affects 10% of users — 50M users at WhatsApp scale. This is the most impactful Redis failure.

---

## The fallback — read from DynamoDB conversations table

The conversations table in DynamoDB stores the same data — conversation IDs with last_message_at timestamps. The inbox sorted set is a cache of this data, not the source of truth.

```
Alice opens inbox
→ Redis shard down → cache miss/error
→ App server falls back to DynamoDB:
  SELECT * FROM conversations
  WHERE participant = alice
  ORDER BY last_message_at DESC
  LIMIT 20
→ Returns top 20 conversations
→ Alice sees her inbox (slower, but correct)
```

DynamoDB has a GSI on `(participant, last_message_at)` — the query is efficient.

---

## Performance impact

Redis inbox read: ~1ms
DynamoDB fallback: ~5-10ms

The inbox load is slower during the outage. Users may notice a slight delay on app open. This is acceptable — the inbox loads, just not as fast.

---

## Read replicas as a buffer

Each Redis primary has read replicas. If the primary goes down, reads can still be served from replicas (stale by milliseconds — acceptable for inbox ordering). Only if all replicas of a shard go down does the DynamoDB fallback kick in.

```
Primary down, replicas alive → reads from replicas, no fallback needed
All replicas down            → fallback to DynamoDB
```

This makes a full inbox Redis failure rare in practice.

> [!tip] Interview framing
> "The inbox sorted set is a cache — conversations table in DynamoDB is the source of truth. If the Redis shard goes down, we fall back to a DynamoDB GSI query on (participant, last_message_at). Slightly slower inbox load, but correct. Read replicas per shard mean the primary going down alone doesn't trigger the fallback."
