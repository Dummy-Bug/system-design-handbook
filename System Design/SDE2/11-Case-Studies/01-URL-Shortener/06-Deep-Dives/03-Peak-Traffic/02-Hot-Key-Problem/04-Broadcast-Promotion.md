
> [!info] The coordination problem
> App server 1 detects a hot key and starts writing salted copies. But app servers 2, 3, and 4 don't know yet — they still read the unsalted key from the overloaded node. You need to broadcast the promotion to all app servers simultaneously.

---

## The race condition

```
T=0ms   → App server 1 detects x7k2p9 as hot
T=1ms   → App server 1 writes x7k2p9:0, :1, :2 to Redis
T=1ms   → App server 1 reads x7k2p9:{random} → distributed ✓
T=50ms  → App server 2 still reads x7k2p9 (unsalted) → Node 2 still overloaded
T=100ms → App server 3 still reads x7k2p9 (unsalted) → Node 2 still overloaded
```

Until all app servers switch to salted reads, Node 2 keeps getting hammered. The fix only works when every server participates.

---

## Option 1 — SNS + SQS

App server 1 publishes a "hot key" message to an SNS topic. Each app server has an SQS queue subscribed to that topic. App servers poll their queues and switch to salted reads when they receive the message.

```
App server 1 → SNS publish: { key: "x7k2p9", replicas: 3 }
SNS → fans out to SQS queues for each app server
App servers poll SQS → receive message → switch to salted reads
```

**Why this is not the best choice:**
- AWS-specific — vendor lock-in
- SQS polling adds latency — messages may sit in queue for seconds before being consumed
- Extra infrastructure to manage (SNS topic, SQS queues per server)
- Overkill for a message that needs to be delivered in milliseconds

---

## Option 2 — Kafka / RabbitMQ

A dedicated message broker handles the broadcast. App servers are consumers on a shared topic.

```
App server 1 → publish to Kafka topic "hot-keys"
All app servers consume from "hot-keys" → switch to salted reads
```

**Why this is overkill:**
- Kafka is designed for high-throughput durable event streaming — millions of events/sec, replay, partitioning
- RabbitMQ is designed for complex routing, acknowledgments, dead letter queues
- You're sending at most a few hot key promotions per minute
- Running a Kafka cluster for a handful of messages per minute is massive operational overhead for zero benefit

---

## Option 3 — Redis pub/sub (the right approach)

Redis has a built-in publish/subscribe mechanism. App servers subscribe to a channel. When a hot key is detected, the detecting server publishes to that channel — all subscribers receive the message in milliseconds.

```
// App server 1 detects hot key
PUBLISH hot-keys '{"key": "x7k2p9", "replicas": 3}'

// All other app servers (subscribed to hot-keys channel)
// receive the message immediately
→ write salted copies: x7k2p9:0, x7k2p9:1, x7k2p9:2
→ switch to random salt reads for x7k2p9
```

**Why Redis pub/sub wins:**
- Already in the stack — zero extra infrastructure
- Millisecond delivery — Redis pub/sub is near-instant
- Simple — one PUBLISH command, one SUBSCRIBE per server
- No polling, no queues, no brokers

---

## The remaining race window — and why it's safe

Even with Redis pub/sub, there's a brief window between when app server 1 detects the hot key and when all other servers consume the message:

```
T=0ms   → App server 1 detects hot key, publishes to Redis channel
T=2ms   → App servers 2,3,4 receive message → switch to salted reads
T=0-2ms → App servers 2,3,4 still read unsalted x7k2p9
```

During this 2ms window, some servers still use the unsalted key. But the **original unsalted key still exists in Redis** — it was there before promotion. Those reads still hit the cache, just on Node 2.

No correctness problem. No cache misses. No DB hits. Just a 2ms window where load isn't fully distributed yet. This is acceptable.

---

## The full promotion flow

```
1. App server 1 local counter: x7k2p9 → 80k reads/sec → exceeds threshold
2. App server 1 writes salted copies:
   SET x7k2p9:0 https://long-url.com EX 3600
   SET x7k2p9:1 https://long-url.com EX 3600
   SET x7k2p9:2 https://long-url.com EX 3600
3. App server 1 publishes: PUBLISH hot-keys '{"key":"x7k2p9","replicas":3}'
4. All app servers receive → switch to GET x7k2p9:{random(0,2)}
5. Load distributed across Node 2, Node 5, Node 7 ✓
```

---

> [!tip] Interview framing
> "Redis pub/sub for broadcasting hot key promotions — already in the stack, millisecond delivery, zero extra infrastructure. SNS+SQS works but is AWS-specific with polling latency. Kafka/RabbitMQ is massively overkill for a handful of promotions per minute. The race window between detection and all servers switching is ~2ms — safe because the original unsalted key still serves reads during that window."
