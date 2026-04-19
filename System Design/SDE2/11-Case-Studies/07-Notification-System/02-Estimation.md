
## Users and Activity

Start with the real world: roughly 10 billion people on Earth, about 1 billion of them are on a platform like Instagram or WhatsApp. Of those 1 billion registered users, assume **50% are Daily Active Users (DAU)** — 500 million people using the product on any given day.

Each active user performs about **50 actions per day** — likes, comments, DMs, story views. Each action typically generates **1 notification for the receiver** (not the sender). So:

```
500M DAU × 50 actions = 25 billion notifications per day
```

---

## QPS

There are approximately 86,400 seconds in a day — round to 100,000 for easy math:

```
25B / 100,000 = 250,000 notifications/sec  (sustained)
```

Traffic is never uniform. Peak hours (evening, major events) can spike to 10× sustained:

```
250K × 10 = 2.5M notification events/sec  (peak)
```

---

## Multi-Channel Multiplier

Here's what candidates often miss: one notification **event** can trigger sends on multiple channels. A user might have push + email both enabled. The system supports 3 channels — push, SMS, email. On average, assume **2 channel sends per event**:

```
2.5M events/sec × 2 channels = 5M actual sends/sec at peak
```

This is the harder number. The fan-out infrastructure (Kafka, channel workers) must handle 5M dispatches per second at peak, not 2.5M.

---

## Storage

Each notification record contains:
- ID: 8 bytes
- User ID, sender ID: 16 bytes  
- Title + body: ~200 bytes
- Deep link + metadata: ~100 bytes
- Status, timestamps: ~50 bytes

**Total: ~300–400 bytes per notification record. Call it 400 bytes.**

```
2.5M notifications/sec × 400 bytes = 1GB/sec
1GB/sec × 86,400 = ~86TB/day
```

Wait — that seems large. The key insight is **notifications are not permanent**. Nobody queries "did I get that Instagram like in January?" After 30–90 days, notifications are useless. Cap retention at **90 days**:

```
86TB/day × 90 days = ~7.7PB
```

That's still large. But most of this is cold storage — only recent notifications (last 7 days) are hot. And you can compress heavily since notification payloads are repetitive text. With 10× compression, cold storage drops to ~770TB for 90 days. Manageable.

> [!important] What to store vs what to drop
> You don't need to store the full notification payload forever. Store: ID, user ID, channel, delivery status, timestamp. Drop: full body/title after 30 days. This brings storage down dramatically.

---

## Bandwidth

At peak, 5M sends/sec, each notification payload ~300 bytes:

```
5M × 300 bytes = 1.5GB/sec outbound
1.5GB/sec × 8 = 12Gbps
```

A standard NIC handles 10Gbps. At peak you need slightly more than one NIC's worth of capacity — so you need either:
- Multiple dispatch nodes (each handling a shard of the traffic), or
- 25Gbps NICs on dispatcher machines

This is not a problem in practice since you'll have many dispatcher nodes anyway, but it's worth flagging that a single-machine dispatcher falls over at peak.

> [!tip] Interview framing for bandwidth
> "At 5M sends/sec with ~300 bytes per payload, we're looking at ~12Gbps outbound at peak. A single machine can't handle this, which is one reason we need a horizontally scalable dispatcher pool behind Kafka — each worker node handles a partition and the total throughput is distributed."

---

## Summary Table

| Metric | Value |
|---|---|
| Registered users | 1B |
| DAU | 500M |
| Notifications/day | 25B |
| Sustained QPS (events) | 250K/sec |
| Peak QPS (events) | 2.5M/sec |
| Peak QPS (actual sends) | 5M/sec (×2 channel multiplier) |
| Payload size | ~300 bytes |
| Peak bandwidth | ~12Gbps |
| Storage per day | ~86TB (raw), compress to ~8TB |
| Retention | 90 days |
| Working storage | ~720TB compressed |
