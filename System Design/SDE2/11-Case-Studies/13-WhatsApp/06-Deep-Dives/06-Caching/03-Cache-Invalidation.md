
> [!info] Cache invalidation — keeping the profile cache consistent
> When Bob updates his profile, the cache must be updated. The question is how — and the answer is simpler than it first appears.

---

## The problem

Bob opens settings and changes his profile picture. DynamoDB gets the new avatar URL. But Redis still has the old one. For the next hour (until TTL expires), anyone who opens a chat with Bob sees his old picture.

This is the classic cache consistency problem. You have two stores — DB and Redis — and they're now out of sync.

---

## The tempting over-engineered solution

One instinct is to use the outbox pattern with Kafka:

```
Bob updates profile
→ DB write + outbox event written atomically
→ Kafka producer publishes profile_updated event
→ Cache invalidation consumer reads event
→ Consumer DEL user:bob from Redis
```

This is correct for complex distributed systems where multiple downstream consumers need to react to the same event. But here you have exactly one consumer: Redis. You're firing up a distributed message bus to delete a single cache key.

> [!danger] Don't over-engineer cache invalidation
> Outbox + Kafka is the right pattern when you have multiple consumers or when the DB write and downstream action must be decoupled across service boundaries. For a single cache key, it adds latency, operational complexity, and failure modes with zero benefit.

---

## The right solution — synchronous DEL

Bob's profile update is already being handled by the app server. The app server writes to DynamoDB. Then, in the same request handler, it deletes the Redis key.

```
Bob hits save on new profile picture
→ App server writes new profile to DynamoDB
→ App server DEL user:bob from Redis    (~1ms)
→ Response returned to Bob
```

That's it. A Redis DEL takes roughly 1 millisecond. Bob is already waiting for the DynamoDB write to complete — adding 1ms is invisible.

The next time Alice opens her inbox and needs Bob's profile:
```
GET user:bob → miss (key was deleted)
→ fetch from DynamoDB → gets new avatar URL
→ re-cache in Redis
→ return to Alice
```

Alice sees the new profile picture on her very next inbox load. No lag, no Kafka consumer, no outbox table.

---

## What about concurrent reads during invalidation?

Between the moment the DB is written and the Redis key is deleted, there's a tiny window where a read could cache the old value. This is acceptable — the window is microseconds, and a 1-hour TTL already means you're tolerating some staleness by design.

> [!tip] Interview framing
> "Profile updates are rare — maybe once a month per user. I'd do a synchronous DEL on the Redis key in the same request that writes to the DB. The DEL takes 1ms and keeps the implementation simple. The TTL acts as a backstop — even if the DEL somehow failed, the entry expires within the hour."
