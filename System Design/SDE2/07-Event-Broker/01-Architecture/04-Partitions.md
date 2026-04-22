
> [!info] A partition is Kafka's unit of sharding. One topic is split into multiple partitions, each stored independently. Messages within a partition are strictly ordered. Messages across partitions are not.

---

## The problem — one log can't scale

You have a topic `ad_clicks` receiving 100,000 events/sec. If that entire topic lives as a single log on one machine:
- One disk fills up — 30 days of 100k events/sec is petabytes of data
- One machine handles all writes — it hits its network and CPU ceiling
- One machine going down = entire topic unavailable

This is the same problem databases hit at scale. And the fix is the same: **sharding**. Split the data across multiple machines.

---

## What a partition is

A partition is an independent, ordered log. One topic is split into N partitions, each stored on a different machine. Every partition is its own append-only log with its own offsets starting from 0.

```
Topic: ad_clicks

Partition 0: [offset 0][offset 1][offset 2]...  → Machine A
Partition 1: [offset 0][offset 1][offset 2]...  → Machine B
Partition 2: [offset 0][offset 1][offset 2]...  → Machine C
```

100,000 events/sec across 3 partitions = ~33,000 events/sec per machine. Both storage and write load are distributed.

---

## How producers decide which partition to write to

The producer uses a **partition key** — a field from the message that gets hashed to determine the partition.

```
click event: { advertiser_id: "nike", user_id: "abc", timestamp: ... }

hash("nike")   % 3 = 1  → all Nike clicks go to Partition 1
hash("adidas") % 3 = 0  → all Adidas clicks go to Partition 0
hash("puma")   % 3 = 2  → all Puma clicks go to Partition 2
```

Same key always maps to the same partition. This gives you **ordering per key** — all Nike clicks arrive at Partition 1 in the exact order they happened. No Nike click can overtake another Nike click.

If no key is specified, the producer round-robins across partitions — even load distribution but no ordering guarantee.

---

## Ordering guarantee — within partition only

Messages within a partition are strictly ordered. Messages across partitions are not.

```
Partition 0: Nike click 1 → Nike click 2 → Nike click 3  ← strict order guaranteed

Partition 1: Adidas click 1 → Adidas click 2             ← strict order guaranteed

But:
Nike click 2 vs Adidas click 1 — no ordering guarantee across partitions
```

This is why partition key choice matters. If your billing service needs to count Nike clicks in order, all Nike clicks must land in the same partition. Using `advertiser_id` as the partition key guarantees that.

---

## How partitions are distributed across machines

Each partition has one **leader** — the machine that handles all reads and writes for that partition — and multiple **replicas** on other machines for fault tolerance. That's covered in depth in the Replication file.

The important thing for now: partitions are the unit of distribution. Adding more partitions means more machines share the load.

> [!important] Partition count is set at topic creation and is painful to change later. Too few partitions = bottleneck. Too many = metadata overhead. A common starting point is partitions = number of consumers you plan to run, with room to grow.

> [!tip] **Interview framing:** "I'd partition the `ad_clicks` topic by `advertiser_id`. This ensures all clicks for a given advertiser land in the same partition in order — which matters for billing to count clicks correctly. It also distributes load evenly assuming advertisers have roughly similar click volumes. With 3 partitions and 100k events/sec, each machine handles ~33k events/sec — well within commodity hardware limits."
