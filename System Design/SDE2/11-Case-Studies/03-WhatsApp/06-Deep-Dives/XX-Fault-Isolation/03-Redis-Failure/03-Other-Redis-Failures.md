
> [!info] Other Redis failures — registry, rate limiting, sequence counter
> Three other Redis instances in the system. Each has a different criticality and a different fallback.

---

## Connection Registry Redis

**What it does:** maps user IDs to their current connection server for message routing.

**What breaks when it goes down:** the app server can't look up which server a user is connected to. All users appear offline to the routing layer.

**Fallback:** the offline delivery system handles it cleanly. A registry miss already means "treat as offline" — the message goes to pending_deliveries. When the registry Redis recovers, the delivery worker resumes routing.

```
Registry Redis down
→ All registry lookups miss
→ All messages go to pending_deliveries
→ Registry Redis recovers
→ Clients reconnect (connections were unaffected — only lookup is broken)
→ Registry repopulated via Kafka consumers
→ Delivery workers drain pending_deliveries
→ All messages delivered
```

Users experience a delay — messages queue up during the outage and arrive in a burst once the registry recovers. No messages are lost.

**Why this is survivable:** the registry is not the source of truth for messages. It's only needed for routing. The pending_deliveries table holds the messages safely until routing is restored.

---

## Rate Limiting Redis

**What it does:** stores per-user message counters (INCR with 1-second TTL) to enforce the 10 messages/second limit.

**What breaks when it goes down:** the app server can't check rate limit counters. Every INCR call fails.

**Fallback — fail open:** allow all messages through without rate limiting.

```
Rate limit Redis down
→ INCR call fails
→ App server: treat as rate limit not exceeded
→ Message allowed through
```

This is the correct choice. The alternative — fail closed (reject all messages) — would mean no user can send any message during the outage. That's far worse UX than temporarily losing rate limit enforcement.

The risk of failing open is a brief window where a malicious user can send unlimited messages. At WhatsApp scale, this is an acceptable trade-off for a short outage. Rate limiting Redis is a small, low-load instance — it rarely goes down, and if it does, it recovers quickly.

---

## Sequence Counter Redis

**What it does:** generates monotonically increasing message IDs per conversation for ordering.

**What breaks when it goes down:** new messages can't get a sequence number. Message ordering within a conversation may be lost.

**Fallback:** use timestamp-based ordering as a fallback ID.

```
Sequence Redis down
→ Can't get seq_id for message
→ Fall back to: message_id = current_timestamp_ms + random_suffix
→ Messages ordered by timestamp
```

Timestamp ordering is slightly weaker than sequence numbers — two messages sent within the same millisecond have non-deterministic order. In practice this is extremely rare and users won't notice.

The system eventually becomes consistent — when sequence Redis recovers, new messages get proper sequence IDs again. Existing messages with timestamp IDs are already delivered and don't need re-ordering.

> [!important] Fail open vs fail closed
> Rate limiting Redis fails open — temporary loss of rate limiting is better than blocking all messages.
> Sequence counter Redis fails to timestamps — slightly weaker ordering is better than message delivery failure.
> Both choices prioritise availability over strict correctness for short outage windows.

> [!tip] Interview framing
> "Registry Redis failure degrades to offline delivery — no messages lost, just delayed. Rate limiting Redis fails open — we lose rate limiting temporarily but keep message delivery working. Sequence Redis falls back to timestamp ordering — slightly weaker but delivery is unaffected."
