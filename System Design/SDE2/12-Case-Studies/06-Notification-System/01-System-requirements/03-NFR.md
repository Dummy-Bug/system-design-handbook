# Non-Functional Requirements

## Availability — The Most Critical NFR

Availability is the top priority for this system. The calling services (Instagram's like service, Uber's trip service, the bank's fraud detection) must always be able to register a notification request. If the notification system is down, those services either have to retry indefinitely or drop the event — both are bad.

The key insight here is that "available" doesn't mean "delivers instantly." It means **the system always accepts the request**. Delivery can be async and delayed — but registration must never fail. This is why the intake layer must be highly available and backed by a durable queue. The caller fires and forgets; the system guarantees eventual delivery.

> [!info] Availability SLO
> The notification intake API should target **99.99% availability** — roughly 52 minutes of downtime per year. The delivery pipeline can be slightly lower (99.9%) since delayed delivery is tolerable, but dropped requests are not.

---

## Latency — Low But Not Extreme

This is not a user-facing system in the traditional sense — the caller doesn't wait for the notification to land on the device before continuing. The like service fires the event and moves on. So end-to-end latency is not a blocking concern for the caller.

That said, users do expect notifications to arrive reasonably quickly. A fraud alert that arrives 10 minutes late is a bad experience. The targets by channel:

```
Push notification  → 95th percentile delivered within 5 seconds
SMS                → 95th percentile delivered within 30 seconds
Email              → 95th percentile delivered within 2 minutes
```

200ms end-to-end would be over-engineering — that's trading platform territory. 5 seconds for push is the right bar.

---

## Eventual Consistency — Delivery Status

The system tracks the status of every notification — pending, sent, delivered, failed, clicked. This status data is spread across multiple nodes. When a notification is delivered and Node A updates its status, Node B might not have synced yet. If someone queries Node B immediately, they'll see a stale "pending" status.

This is fine. Delivery status is not a correctness-critical field — it's an analytics/observability signal. A short inconsistency window (seconds to minutes) is completely acceptable. The status will converge eventually across all nodes.

> [!important] Where consistency IS a hard requirement
> The one place you cannot afford inconsistency is **user preference data** — which channels a user has opted into or out of. If a user opts out of SMS and Node B hasn't synced that preference yet, the system might send an unwanted SMS. This is a user trust violation. User preference reads should be strongly consistent or served from a single source of truth.

---

## At-Least-Once Delivery

The system guarantees **at-least-once delivery** — a notification will never be silently dropped. If push fails (phone offline, APNs timeout), the system retries with exponential backoff. If SMS fails, it retries. If all retries are exhausted, it goes to a Dead Letter Queue for manual inspection.

The trade-off: a notification might be delivered twice. This is acceptable. A duplicate "John liked your photo" is annoying but harmless. A missed fraud alert is a real problem. We optimize for no misses over no duplicates.

> [!danger] At-least-once vs exactly-once
> Exactly-once delivery would require distributed transactions across your system and the external provider (APNs, FCM, Twilio). That's prohibitively expensive and complex. At-least-once with idempotent handling on the client side is the right engineering trade-off here.

---

## Durability — Never Lose a Request

Once the notification system acknowledges a request from the calling service, that notification must never be lost — even if nodes crash, disks fail, or the network partitions. The system persists every accepted notification to a durable queue (Kafka) before acknowledging the caller.

This is distinct from at-least-once delivery:
- **Durability** = the request is never lost after acceptance
- **At-least-once** = the send is retried until it succeeds

```
Caller fires request
  → System persists to Kafka (durable)
  → System acknowledges caller  ← durability guarantee ends here
  → Worker picks up and sends
  → If send fails → retry       ← at-least-once guarantee kicks in here
```

---

## Fault Tolerance

The failure of individual nodes must not bring down the system. This is achieved through:
- **Horizontal scaling** — many stateless intake nodes behind a load balancer; any node can die and the others absorb the traffic
- **Kafka as the backbone** — the queue is replicated across brokers; no single broker failure drops messages
- **No single point of failure** in the delivery path — channel workers (push, SMS, email) are independent; a failure in the SMS worker doesn't affect push delivery

---

## Data Integrity — Right Notification, Right User

Whatever notification was registered must be delivered exactly as intended — to the correct user, on the correct channel, with the correct content. No misdirected notifications. This is a correctness requirement, not a performance one.

> [!danger] Misdirected notifications are a trust-destroying bug
> Sending user A's fraud alert to user B, or sending a private DM notification to the wrong recipient, is not an availability issue — it's a data integrity violation. The system must validate user ID and channel ownership at intake, before any fan-out happens.

---

## NFR Summary

| Property | Requirement |
|---|---|
| Availability (intake) | 99.99% — always accept requests |
| Latency (push) | p95 < 5 seconds end-to-end |
| Latency (SMS) | p95 < 30 seconds |
| Latency (email) | p95 < 2 minutes |
| Consistency (status) | Eventual — stale reads acceptable |
| Consistency (preferences) | Strong — opt-out must be respected immediately |
| Delivery guarantee | At-least-once — duplicates tolerable, drops are not |
| Durability | Persist before ack — no silent loss after acceptance |
| Fault tolerance | Node failures isolated — no cascading failures |
| Data integrity | Right notification to right user, always |
