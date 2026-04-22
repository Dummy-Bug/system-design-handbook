## What problem does NewSQL solve?

SQL gives you ACID but hits a scale ceiling (~50k TPS on a single node). Sharding SQL breaks cross-shard ACID. Cassandra scales but is eventually consistent. NewSQL gives you ACID + horizontal scale together.

---

## Key names

| Database | Cloud | Key feature |
|---|---|---|
| Google Spanner | Google Cloud | TrueTime — atomic clocks + GPS for global ordering |
| Amazon Aurora | AWS | Distributed SQL, storage-compute separation, multi-region reads |
| Azure Cosmos DB | Azure | Multi-model, tunable consistency levels, global distribution |

---

> [!question] How does Spanner achieve globally ordered transactions without a central coordinator?

> [!success]-
> TrueTime. Every Spanner data center has atomic clocks and GPS receivers. Instead of a single timestamp, TrueTime returns a bounded uncertainty window — e.g., "true time is somewhere in this 4ms range."
>
> Before committing, Spanner waits out the entire uncertainty window (commit-wait). After the wait, the commit timestamp is guaranteed to be unique and globally ordered — no other transaction anywhere in the world has an overlapping timestamp.
>
> This gives **external consistency** — the database's ordering matches real-world causality — without any central coordinator bottleneck.
>
> > [!tip] Interview framing
> > "Spanner uses atomic clocks and GPS to get a bounded uncertainty window on the current time. Before committing, it waits out that window — typically 1-7ms. After the wait, the timestamp is guaranteed to be globally unique and ordered. This is called external consistency."

---

> [!question] How does Spanner handle two transactions touching the same row simultaneously?

> [!success]-
> Row-level locking + optimistic concurrency control. Spanner locks at the row level — two transactions on different rows proceed in parallel. Two transactions on the same row: one waits. At commit time, the later transaction checks if anything it read has changed. If yes — conflict detected, rollback. TrueTime's ordering determines which transaction wins.
>
> > [!tip] Interview framing
> > "Spanner uses row-level locking. The TrueTime ordering determines which transaction commits first. The second transaction detects the conflict at commit time and rolls back — same as optimistic locking, but with guaranteed global ordering."

---

> [!question] Would you use Spanner for a social media feed? Why or why not?

> [!success]-
> No. A social feed can tolerate eventual consistency — if a post appears 200ms late for some users, nobody loses money. Spanner's global ACID and commit-wait latency are unnecessary overhead for this use case. Use Cassandra or DynamoDB — built for write-heavy, eventually consistent workloads at massive scale.
>
> Spanner is for: payments, banking, stock trading, inventory that cannot oversell — anywhere money or real-world scarcity is involved and consistency cannot be compromised.

---

## Decision map

```
Regional + strong consistency + < 50k TPS          → Postgres / MySQL
Global + strong consistency + millions of TPS      → NewSQL (Spanner / Aurora)
Write-heavy + eventual consistency + massive scale → Cassandra / DynamoDB
Read-heavy + cache layer                           → Redis
```

---

## The rule

```
Money involved → consistency wins → Postgres or NewSQL
No money → evaluate consistency vs scale trade-off → maybe Cassandra
```

Never use eventual consistency for financial data. Ever.
