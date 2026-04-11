# Sharding vs Quorum Queues

> [!info] In RabbitMQ, sharding and quorum queues solve different scaling problems. Sharding increases throughput by splitting a workload across many queues. Quorum queues increase durability and failover safety by replicating one queue across nodes.

---

## The hot-queue problem

Suppose billing traffic becomes too high for one queue:

```text
Exchange -> billing.queue -> billing workers
```

At `200k msgs/sec`, one queue can become the hotspot. Adding more consumers helps only up to a point because the queue is still owned by one node.

So the real throughput fix is to split one logical workload across multiple queues.

---

## Sharding for throughput

Instead of one billing queue, create multiple billing shards:

```text
Exchange
-> billing.0.queue
-> billing.1.queue
-> billing.2.queue
-> billing.3.queue
```

Now route by a stable key such as:

```text
campaign_id % 4
```

Example:

```text
campaign 10 -> billing.2.queue
campaign 11 -> billing.3.queue
campaign 12 -> billing.0.queue
```

Why this helps:

- each queue can live on a different node
- consumers can process shards independently
- one queue is no longer the single hotspot

Trade-offs:

- more routing complexity
- harder rebalancing later
- no strict global ordering across all shards

---

## Quorum queues for availability

Now take one queue and make it replicated:

```text
billing.queue
-> leader on Node A
-> follower on Node B
-> follower on Node C
```

Producer writes go to the leader, and the leader replicates to followers.

Why teams use this:

- queue can survive node failure
- failover is possible
- durability is stronger than a single local queue

But replication adds extra work:

- more network traffic
- more disk writes
- coordination before commit

So quorum queues are safer, but slower.

---

## The practical rule

These two tools solve different problems:

```text
Need more throughput?   -> shard across multiple queues
Need failover safety?   -> quorum queues
Need both?              -> multiple quorum-backed shards
```

That is the correct RabbitMQ scaling model.

Do not say this in an interview:

```text
I'll use quorum queues to scale throughput
```

That is wrong. Quorum queues improve safety, not raw speed.

---

## Putting it together

A real production design might look like this:

```text
billing.0.queue (quorum)
billing.1.queue (quorum)
billing.2.queue (quorum)
billing.3.queue (quorum)
```

This gives:

- throughput from sharding
- safety from replication

But it also increases:

- operational complexity
- routing logic
- observability difficulty
- ordering complexity

---

> [!important] What it guarantees
> Sharding increases parallelism and spreads load. Quorum queues increase durability and failover safety.

> [!danger] What it doesn't guarantee
> Neither feature alone solves every scaling problem. Sharding does not protect against node loss by itself, and quorum does not make one queue infinitely fast.

---

> [!tip] Interview framing
> "For RabbitMQ, I separate throughput scaling from availability scaling. I shard hot workloads across multiple queues for throughput, and I use quorum queues when I need replicated durability and failover."
