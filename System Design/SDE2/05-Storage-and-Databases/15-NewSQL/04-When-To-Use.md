## The decision comes down to two axes

```
                        Strong Consistency
                               ↑
                               |
               Postgres        |        NewSQL (Spanner)
               MySQL           |        Aurora
                               |
  ─────────────────────────────┼──────────────────────── Scale
                               |
               Redis           |        Cassandra
               Memcached       |        DynamoDB
                               |
                        Eventual Consistency
```

Pick your quadrant based on what the system actually requires — not what sounds impressive.

---

## The three database archetypes for scale

**Postgres / MySQL — single region, strong consistency**

The right default for most systems. Handles tens of thousands of TPS on a single well-tuned node. Add read replicas for read-heavy workloads. Can be sharded if needed, but cross-shard transactions become your problem.

Reach for this when: the system is regional, consistency matters, and you haven't hit the scale ceiling yet.

```
Examples: most web apps, regional e-commerce, internal tools, anything < 50k TPS
```

**Cassandra / DynamoDB — global scale, eventual consistency**

Built for write-heavy, massive-scale workloads where you can tolerate a brief window of inconsistency. Not suitable for money. Excellent for timelines, activity logs, IoT events, social feeds.

Reach for this when: write volume is extreme, consistency can be relaxed, data is naturally time-ordered or partitioned cleanly.

```
Examples: WhatsApp message history, Instagram feed, IoT sensor data, Netflix viewing history
```

**NewSQL (Spanner, Aurora) — global scale, strong consistency**

The hardest quadrant to be in. You need both — scale and consistency — and you can't compromise on either. This is rare. Most systems can live in one of the first two quadrants.

Reach for this when: the system is explicitly global, TPS is in the millions, and strong consistency is non-negotiable.

```
Examples: Google Pay, global stock exchange, international banking ledger, multi-region inventory (can't oversell)
```

---

## The stock trading example

A stock trading platform in India:

- Volume: high, but regional — one country, one timezone, peak trading hours
- Consistency: non-negotiable — two users cannot buy the same last share

**Answer: Postgres (or MySQL)**. Regional scale, strong consistency. No need for NewSQL complexity.

The same platform going global — US, EU, Asia trading simultaneously, millions of TPS:

**Answer: NewSQL (Spanner)**. Now you need global ordering and global ACID.

---

## The rule for money

Whenever money is involved — payments, transfers, balances, inventory that maps to real-world scarcity — consistency wins. Always. You cannot use eventual consistency for financial data.

```
Social feed slightly stale?        → Fine. Use Cassandra.
User balance slightly stale?       → Not fine. Use Postgres or Spanner.
Last seat on a flight oversold?    → Not fine. Use Postgres or Spanner.
```

---

## The upgrade path

Don't architect for Spanner on day one. The progression:

```
Day 1:    Postgres single node
Scaling:  Postgres + read replicas
Growing:  Sharded Postgres
Painful:  Cross-shard ACID problems → consider NewSQL
```

Most companies never reach step 4. Design for where you are, with a clear upgrade path in mind.

> [!tip] Interview framing
> "I'd start with Postgres — it handles strong consistency and scales well with read replicas. If the system is explicitly global with millions of TPS and I can't compromise on consistency — like a payments platform — I'd reach for Spanner. I wouldn't use Cassandra here because it's eventually consistent and money can't be eventually consistent."
