>[!info] NewSQL is the answer to a specific problem:
> you need the full guarantees of SQL (ACID, strong consistency, complex transactions) but your system has outgrown what a single database node can handle. NewSQL gives you both — SQL semantics with horizontal scale.


## Starting point — Postgres works great, until it doesn't

For most systems, Postgres is the right answer. A well-tuned Postgres node handles tens of thousands of TPS. Add read replicas to offload reads. Add connection pooling. You can go very far with a single primary node.

But imagine you're building Google Pay — a global payments system. Transactions happen across the US, Europe, and Asia simultaneously. You need two things at once:

1. **Strong consistency** — money must never be double-spent. Two users cannot spend the same balance simultaneously. A transfer must either fully complete or fully fail — never half-execute.
2. **Scale** — millions of transactions per second across multiple continents.

A single Postgres node hits its ceiling at roughly 10k-50k TPS. At millions of TPS globally, you have to scale out.

---

## The sharding trap

The natural move is to shard Postgres — split your data across multiple nodes. NA users on shard 1, EU users on shard 2, Asia users on shard 3.

Internal transactions — Alice in NA sends money to Bob also in NA — stay within shard 1. ACID holds perfectly.

But cross-region transactions — Alice in NA sends money to Bob in EU — now span two separate database nodes. And here's the uncomfortable truth: **ACID guarantees are per-node**. The moment a transaction touches two separate shards, you've lost the atomic guarantee that makes it safe.

```
Alice → Bob (cross-region transfer)
→ Debit Alice on shard 1 (NA)  ✓
→ Credit Bob on shard 2 (EU)   ✗  (network failure)
→ Alice lost $100, Bob got nothing
```

Making this atomic requires coordination between shards — which is complex, slow, and fragile. You end up with painful distributed transaction protocols, and your system's correctness now depends on whether those protocols handle every failure case correctly.

---

## The gap NewSQL fills

```
Postgres (single node)  → full ACID ✓  |  global scale ✗

Sharded Postgres        → global scale ✓  |  cross-shard ACID is your problem ✗

Cassandra               → massive scale ✓  |  eventual consistency only ✗ (wrong for money)

NewSQL (Spanner)        → full ACID ✓  |  global scale ✓
```

NewSQL databases are built from the ground up to give you both. They handle the distributed coordination internally — you get a clean SQL interface with full ACID guarantees, and the database scales horizontally behind the scenes.

---

## The upgrade path

You don't reach for NewSQL on day one. The progression looks like:

```
Start      → Postgres (single node)
Growing    → Postgres + read replicas
Scaling    → Sharded Postgres
Hitting walls → NewSQL (when sharding complexity becomes unmanageable)
```

Most companies never reach NewSQL. The 1% that do are operating at Google/Amazon/global financial system scale.

> [!important] The core insight
> The problem isn't write volume alone — Cassandra handles that. The problem is **write volume + strong consistency together**. Cassandra gives you scale by relaxing consistency. NewSQL gives you scale without relaxing consistency. Whenever money is involved, consistency wins. Always.
