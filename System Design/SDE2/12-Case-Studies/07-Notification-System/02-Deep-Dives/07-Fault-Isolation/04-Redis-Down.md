# Redis Down — Fault Isolation

## How It Propagates

Redis serves three distinct purposes in this system — each with its own failure mode when Redis goes down:

1. **Preferences cache** — workers check Redis for user opt-out settings before sending
2. **Bloom filter** — deduplication check before sending to prevent duplicate notifications
3. **Token buckets** — per-account rate limiting for Twilio and SendGrid

Each breaks differently and needs its own containment strategy.

---

## Preferences Cache Down — Fallback to PostgreSQL

When the preferences cache is unavailable, workers fall back to reading directly from PostgreSQL for every notification. At 5M notifications/sec, that's 5M preference reads/sec hitting PostgreSQL directly.

PostgreSQL caps at ~50K reads/sec even when well-tuned. 5M/sec would kill it instantly — connection pool saturation, query latency spikes, full DB failure.

---

## Why Not Cassandra for Preferences

The instinct is to move preferences to Cassandra — it handles 5M reads/sec comfortably. But preferences were put in PostgreSQL for a specific reason: **strong consistency**.

If a user opts out of SMS at 9:00:00, the very next notification at 9:00:01 must not send SMS. Cassandra is eventually consistent — a preference update might not be visible across all nodes for hundreds of milliseconds. That window is enough to send an SMS to a user who just opted out. That's a correctness bug, not a performance trade-off.

Moving preferences to Cassandra trades correctness for throughput. The right answer is to keep PostgreSQL and handle the Redis-down scenario differently.

---

## Fallback Default — Assume Opted-In When Redis Is Down

When both the Redis cache and PostgreSQL are overwhelmed, workers apply a **fallback default**: assume the user has not opted out of any channel and send the notification.

This is slightly wrong — a small number of users who opted out may receive a notification they didn't want. But this is:
- **Temporary** — Redis recovers, cache is repopulated, correct behaviour resumes
- **Rare** — Redis going fully down is an uncommon event
- **Recoverable** — users can report unwanted notifications, no permanent harm

The alternative — blocking all notifications until Redis recovers — violates the core availability guarantee. A brief correctness degradation is far better than a full notification outage.

> [!important] Temporary incorrectness beats full outage
> The fallback default means some opted-out users get a notification they shouldn't. That's a minor UX issue. Blocking all notifications while Redis is down means millions of users miss time-sensitive alerts (OTPs, fraud alerts). Always choose the option that keeps critical notifications flowing.

---

## Bloom Filter Down — Skip Deduplication, Accept Duplicates

The bloom filter for deduplication lives entirely in Redis. When Redis is down, the bloom filter is unavailable — workers have no way to check if a notification has already been processed.

Two options:
1. **Skip deduplication** — send the notification, risk duplicates
2. **Block until Redis recovers** — hold notifications, risk missing SLOs

Option 2 violates the at-least-once delivery guarantee from the NFR. Misses are worse than duplicates — a user missing a fraud alert is far more serious than receiving a duplicate push notification.

**Skip deduplication and accept duplicates.** When Redis recovers, the bloom filter is repopulated and deduplication resumes. The window of duplicates is short and bounded by the Redis outage duration.

> [!danger] Never block delivery waiting for deduplication infrastructure
> The bloom filter is a best-effort mechanism — it reduces duplicates, it does not eliminate them. At-least-once delivery is the core contract. Blocking notifications because the dedup filter is unavailable inverts the priority. Skip it, send the notification, accept the rare duplicate.

---

## Token Buckets Down — Circuit Breaker Handles Rate Limiting

Token buckets for Twilio and SendGrid rate limiting also live in Redis. When Redis is down, workers can't check if an account has capacity before sending.

Without token bucket enforcement, workers might exceed Twilio's 1K/sec limit and start receiving 429s. The circuit breaker handles this — 429s trigger the same flow as normal rate limiting: mark the account blocked, route to the next account, shed load if all accounts are at capacity.

The circuit breaker does not need Redis — it tracks failure rates in local worker memory. So rate limiting degrades gracefully: token bucket precision is lost, but the circuit breaker prevents a full cascade failure.

---

## Redis Cluster — Sharding for Availability

Redis deployed in **cluster mode** with sharding means one shard going down only affects a portion of keys — not the entire cache. With 6 shards:

- Preferences cache: keys distributed across shards by `user_id`
- Token buckets: keys distributed across shards by `account_id`
- Bloom filter: cannot be sharded — all notification IDs must be in the same filter to detect duplicates. The bloom filter lives on a single Redis instance with a replica for failover.

Redis Cluster with automatic failover (Redis Sentinel) promotes a replica to primary within seconds of a primary failure. Most Redis failures are resolved before workers even notice.

---

## Detection and Recovery

**Detection:**
- Redis error rate spikes
- Worker preference read latency increases (falling back to PostgreSQL)
- PostgreSQL connection pool saturation alert
- Alert fires to on-call

**Recovery:**
- Redis recovers → preferences cache repopulated on next read (lazy population)
- Bloom filter repopulated — note: the window of duplicates during the outage cannot be retroactively deduplicated. Accept them.
- Token buckets reset to full on recovery — workers resume normal rate-limited sends
- No manual intervention needed for single shard failure (Redis Cluster handles it)

> [!info] Three failure modes, three containment strategies
> Preferences cache down → fallback default (assume opted-in)
> Bloom filter down → skip deduplication, accept duplicates
> Token buckets down → circuit breaker absorbs the degradation
> All three allow delivery to continue — just with reduced accuracy.
