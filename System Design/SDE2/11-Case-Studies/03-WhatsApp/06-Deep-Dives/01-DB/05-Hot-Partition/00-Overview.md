
> [!info] The hot partition problem
> DynamoDB distributes data by partition key using consistent hashing. The assumption is that traffic is spread across many partition keys. But what if 20% of all writes go to a small number of conversations? Those partitions get overwhelmed — not because of storage limits, but because of throughput limits.

---

## DynamoDB partition limits

DynamoDB has two limits per partition:

```
Storage limit    → 10 GB per partition key
Throughput limit → 1,000 WPS per partition (in provisioned mode)
                   (effectively unlimited in on-demand, but throttling can still occur)
```

The storage limit is not a problem for 1-on-1 chat:

```
DynamoDB partition limit  → 10 GB = 10,000,000,000 bytes
Average message size      → 250 bytes
Max messages per partition → 10,000,000,000 / 250 = 40 million messages

Busy couple texting       → 200 messages/day
Time to fill partition    → 40,000,000 / 200 = 200,000 days = 547 years
```

A single 1-on-1 conversation will never fill a 10 GB partition in any realistic scenario.

The **throughput limit** is the real problem.

---

## The math

```
Peak write QPS        → 20k WPS across the whole system
Hot conversations (80/20 rule):
  20% of conversations generate 80% of traffic
  → 80% × 20k = 16k WPS concentrated on ~20% of conversations

Worst case — very hot conversations:
  A small number of extremely active conversations could concentrate
  even more traffic on single partitions
```

Let's say the top 1% of conversations get 20% of all writes:

```
20% × 20k WPS = 4k WPS on ~1% of conversations
DynamoDB limit = 1,000 WPS per partition

4k WPS / 1,000 WPS per partition = 4× over the limit
```

DynamoDB starts throttling — requests get rejected with `ProvisionedThroughputExceededException`. Messages fail to write. Users see errors.

---

## Why this happens — consistent hashing concentrates traffic

DynamoDB uses consistent hashing on the partition key to assign partitions to nodes. If 10 conversations are all hashed to the same underlying partition (which can happen when the number of partitions is small relative to the number of hot keys), all their traffic hits the same physical node.

The problem is not random distribution — it's that a small number of conversations are genuinely much hotter than others. The hashing is even, but the traffic is not.

```
1M conversations total
Top 100 conversations get 20% of all writes
Those 100 conversations likely map to ~10 DynamoDB partitions
Each partition handles 2,000 WPS → 2× over the limit
```

---

## What throttling looks like

When a partition is throttled, DynamoDB rejects writes to that partition:

```
Alice sends "hey" → DynamoDB write → ProvisionedThroughputExceededException
App Server retries with exponential backoff
→ 1st retry after 50ms
→ 2nd retry after 100ms
→ 3rd retry after 200ms
...
```

In the best case, the message is delayed. In the worst case, after all retries are exhausted, the message is dropped or an error is returned to Alice. Her message disappears. This directly violates the durability NFR.

---

## The scale of the problem

With 100M DAU sending 10 messages/day:

```
Total conversations active per day:
  Assuming average 5 messages per conversation per day
  → 1B messages / 5 = 200M active conversations per day

Top 0.1% hottest conversations:
  → 200k conversations
  → Each receiving ~4x average traffic = ~40 messages/day per conversation
  
In peak hour (assuming 10% of daily traffic in 1 hour):
  200k conversations × 40 messages / (24 hours × 3600 sec) × 10% peak factor
  → some partitions could see 500-2000 WPS
```

This is right at or above the DynamoDB partition limit during peak hours.

---

> [!important] Storage hot partition vs throughput hot partition
> These are two different problems. Storage hot partition: one conversation accumulates so much data it fills a 10 GB partition. This doesn't happen in 1-on-1 chat (takes 547 years). Throughput hot partition: too many writes per second hit the same partition. This can happen with popular conversations during peak traffic. The fix is different for each — tiered storage fixes the storage problem, partition key design fixes the throughput problem.

The fix for the throughput hot partition problem is covered in the next file.
