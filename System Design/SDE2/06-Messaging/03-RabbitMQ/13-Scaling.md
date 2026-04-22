
> [!info] RabbitMQ scaling is a three-step problem. First you shard a hot queue across multiple servers to spread load. Then you protect each shard from server failure using replication. Then you solve the resharding pain using consistent hashing.

---

## The hot queue problem

You clustered RabbitMQ — one server per service:

```
Server 1: inventory.queue
Server 2: billing.queue
Server 3: notifications.queue
Server 4: analytics.queue
```

Black Friday hits. `inventory.queue` alone is receiving 200k messages/min. Server 1 is saturated — not because it's sharing with other queues, but because one queue has too much traffic for one server to handle.

Adding more consumers doesn't help. The bottleneck is Server 1 itself.

---

## Step 1 — Sharding for throughput

Instead of one `inventory.queue` on one server, split it into multiple shards — each living on a different server:

```
inventory.queue.0 → Server 1 → 50k messages/min
inventory.queue.1 → Server 2 → 50k messages/min
inventory.queue.2 → Server 3 → 50k messages/min
inventory.queue.3 → Server 4 → 50k messages/min
```

200k/min split evenly across 4 servers. No single server is hammered.

The producer decides which shard to send to using a consistent routing rule:

```java
int shard = orderId % 4;
String queueName = "inventory.queue." + shard;

channel.basicPublish("", queueName,
    MessageProperties.PERSISTENT_TEXT_PLAIN,
    messageBody);
```

The rule must be consistent — same order always goes to the same shard. If `order_1001.placed` goes to shard 1 and `order_1001.payment_confirmed` goes to shard 3, two different workers process the same order's events — ordering is broken.

---

## Step 2 — Consistent hashing for resharding

`order_id % 4` works until you need to add or remove a shard.

Add a 5th server:

```
Before: order_id % 4
  order_1005 → 1005 % 4 = 1 → inventory.queue.1

After: order_id % 5
  order_1005 → 1005 % 5 = 0 → inventory.queue.0  ← different shard
```

Almost every order remaps to a different shard. Messages already sitting in the old shard, new messages going to the new shard — same order's events split across two queues. Ordering broken, workers confused.

Consistent hashing fixes this. Instead of mapping to a shard number, you map to a point on a ring:

```
Ring (0 to 360°):

    Server 1 at 90°
    Server 2 at 180°
    Server 3 at 270°
    Server 4 at 0°

order_1001 hashes to 45° → nearest server clockwise → Server 1
order_1008 hashes to 150° → nearest server clockwise → Server 2
```

Now add Server 5 at 120°:

```
order_1001 at 45°  → Server 1 at 90°   ✓ unchanged
order_1008 at 150° → Server 2 at 180°  ✓ unchanged

Only orders between 90° and 120° → remapped to Server 5
```

Only the orders that fall in the new server's slice get remapped. Everything else stays exactly where it was.

```
% N hashing:        add one shard → almost everything remaps
Consistent hashing: add one shard → only ~1/N of traffic remaps
```

---

## Step 3 — Quorum queues for availability

Sharding spreads load across servers — but now each shard is a single point of failure.

```
Server 2 goes down → inventory.queue.1 is gone
Orders routed to shard 1 → nowhere to go
Messages already in queue.1 → lost
```

The fix is replication. Each shard keeps copies on multiple servers:

```
inventory.queue.1 → Server 2 (leader)
                  → Server 3 (follower)
                  → Server 4 (follower)
```

All writes go to the leader. The leader replicates to followers. If Server 2 goes down, followers hold an election — majority vote picks a new leader — and the queue keeps working.

```
Server 2 goes down
→ Server 3 and Server 4 detect failure
→ Server 3 elected new leader (2 of 3 servers agree = majority)
→ inventory.queue.1 still alive on Server 3
→ producers and consumers reconnect to Server 3
→ no messages lost
```

This is what **Quorum Queues** are in RabbitMQ — a queue replicated across an odd number of servers using majority vote.

```java
Map<String, Object> args = new HashMap<>();
args.put("x-queue-type", "quorum");

channel.queueDeclare("inventory.queue.1", true, false, false, args);
//                                          ↑ must be durable=true
```

> [!important] Quorum queues add replication overhead — every write must be confirmed by a majority of servers before the producer gets an ACK. They are safer but slower. Use them for queues where message loss is unacceptable — orders, payments. Not necessary for low-value events like analytics or logs.

---

## The full picture

```
Problem                    Solution
─────────────────────────────────────────────────────
One queue too hot        → shard across multiple servers
Resharding breaks routing → consistent hashing
Shard server goes down   → quorum queues (replication)
```

A production setup for a hot inventory queue:

```
inventory.queue.0 (quorum: Server 1, 2, 3)
inventory.queue.1 (quorum: Server 2, 3, 4)
inventory.queue.2 (quorum: Server 3, 4, 1)
inventory.queue.3 (quorum: Server 4, 1, 2)
```

Each shard handles a slice of traffic. Each shard survives a server failure independently.

---

> [!danger] Sharding and quorum queues together increase operational complexity significantly — more queues to monitor, more replication traffic, harder to reason about ordering. Only go here when a single queue genuinely cannot keep up. Start simple, shard when you have to.

> [!tip] **Interview framing:** "If a single RabbitMQ queue becomes a bottleneck, I shard it — split into multiple queues across different servers, route by a consistent key like order_id. For resharding without remapping everything, consistent hashing limits remapping to only the affected slice. For availability, I back each shard with a quorum queue — replicated across an odd number of servers, majority vote for leader election. Message loss on server failure is prevented."
