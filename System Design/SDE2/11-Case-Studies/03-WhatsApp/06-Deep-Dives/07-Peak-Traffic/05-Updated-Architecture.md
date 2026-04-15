
> [!info] Architecture after Peak Traffic deep dive
> Four changes from the caching architecture: inbox Redis is sharded across 10 primaries with read replicas, registry writes go through Kafka, rate limiting uses a centralised Redis counter, and app servers have internal queues with auto-scaling.

---

## What changed

**1. Inbox Redis — sharded across 10 primaries**

Previously a single Redis node. Under New Year's midnight load, a single primary cannot handle ~1M writes/second.

```
Sharding:   user_id % 10 → routes to correct primary
Each shard: 1 primary + N read replicas
Reads:      served from replicas (stale by milliseconds — acceptable)
Writes:     go to primary only
TTL:        extended to 26 hours ahead of known high-traffic events
```

**2. Registry writes — async via Kafka**

Previously synchronous write on connect. Under connection storm, 500M simultaneous registry writes overwhelm Redis.

```
On connect:    connection server publishes event to Kafka
Consumer pool: registry workers drain Kafka → write to Redis at controlled rate
Fallback:      registry miss → treat as offline → pending_deliveries
```

**3. Rate limiting — centralised Redis counter**

```
Key:    rate:<user_id>
Op:     INCR on every message (atomic)
TTL:    1 second
Limit:  10 messages/second
Reject: app server returns 429 → connection server sends WS error to client
```

**4. App server — internal queue + auto-scaling**

```
Queue:        in-memory, in front of thread pool
Capacity:     set via load testing (e.g. 50K requests)
Queue full:   returns 429 to connection server
Auto-scaling: triggers on CPU/queue depth, new servers ready in 2-3 min
```

---

## Updated architecture diagram

```mermaid
flowchart TD
    A[Client A] -- WebSocket --> APIGW[API Gateway]
    B[Client B] -- WebSocket --> APIGW
    APIGW --> LB[Load Balancer]
    LB --> WS1[Connection Server 1]
    LB --> WS2[Connection Server 2]
    LB --> WSN[Connection Server N\n500 servers]

    WS1 -- HTTP POST --> ASLB[App Server LB]
    WS2 -- HTTP POST --> ASLB
    WSN -- HTTP POST --> ASLB

    ASLB --> AS1[App Server\ninternal queue + thread pool]
    ASLB --> AS2[App Server\nautoscaling group]

    WS1 -- publishes connect event --> KAFKA[Kafka\nregistry-updates topic]
    KAFKA --> REGWORKER[Registry Workers]
    REGWORKER --> REGISTRY[(Redis\nConnection Registry\n+ last_seen)]

    AS1 --> RATELIMIT[(Redis\nRate Limit Counters\nrate:user_id → INCR TTL 1s)]
    AS1 --> SEQ[Sequence Service]
    SEQ --> SEQREDIS[(Redis\nSeq Counters)]
    AS1 --> DDB[(DynamoDB\nmessages)]
    AS1 --> PENDING[(DynamoDB\npending_deliveries)]
    AS1 --> STATUS[(DynamoDB\nmessage_status)]
    AS1 --> CONVOS[(DynamoDB\nconversations)]
    AS1 --> USERS[(DynamoDB\nusers)]

    AS1 --> INBOX[(Redis Inbox\n10 sharded primaries\n+ read replicas each)]
    AS1 --> PROFILES[(Redis\nProfile Cache)]
    AS1 --> PUSH[Push Notification Service]
    PUSH --> APNS[APNs / FCM]

    DDB -- cold after 30d --> S3[(S3 Cold Tier)]

    REGISTRY -- lookup --> AS1
    INBOX -- ZREVRANGE top K --> AS1
    PROFILES -- cache-aside --> AS1
    AS1 -- route to online user --> WS2
    WS2 -- delivered ack / read receipt --> AS1
    AS1 -- tick push --> WS1
```

---

## Peak traffic capacity summary

| Component | Normal | Peak (New Year) | Mechanism |
|---|---|---|---|
| Inbox Redis | 1 primary | 10 primaries + replicas | shard by user_id % 10 |
| Registry writes | sync | async via Kafka | consumer pool drains at 100K/s per shard |
| Rate limiting | — | 10 msg/s per user | centralised Redis INCR |
| App servers | N | N + auto-scaled | in-memory queue absorbs 2-3 min gap |
