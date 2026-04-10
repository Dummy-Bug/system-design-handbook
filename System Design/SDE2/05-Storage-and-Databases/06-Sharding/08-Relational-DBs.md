> [!question] MySQL and Postgres are not distributed. So how do companies actually scale them — and when do they give up and switch?

## The starting point — relational DBs run on one machine

Postgres and MySQL are not distributed by default. They run on a single server. There are no built-in concepts of nodes, rings, or routing — you query one machine and that machine has all your data.

This surprises people who assume every large system must be using some sophisticated distributed database. Most don't. Most start with Postgres or MySQL and stay there longer than you'd expect.

---

## How companies scale before switching

**Vertical scaling first** — bigger machine, more RAM, faster disk, faster CPU. This gets you surprisingly far. Instagram ran on Postgres for years serving hundreds of millions of users. The database doesn't need to be distributed if the single machine is powerful enough and reads are offloaded to replicas.

When vertical scaling hits its ceiling, companies have two paths.

---

## Path 1 — stay on Postgres/MySQL, shard manually at the application layer

The application code decides which database instance to talk to. The databases themselves know nothing about each other — they're just separate Postgres or MySQL instances sitting on separate servers. Your app does all the routing.

```
App → "user_id 423 → shard 2" → Postgres instance 2
App → "user_id 891 → shard 1" → Postgres instance 1
```

This works, but it's painful. Cross-shard JOINs break — the two rows you want to JOIN live on different machines with no connection between them. Transactions that touch multiple shards break ACID guarantees. Schema migrations have to be run on every shard separately.

You're bolting distributed behaviour onto something not designed for it.

Companies like Shopify and GitHub do this — hundreds of MySQL shards with application-level routing. It works at scale, but it requires significant engineering effort to manage.

---

## Path 2 — migrate to a natively distributed database

At a certain scale, the sharding pain becomes worse than the cost of migrating. So companies move to databases designed for distribution from day one.

```
Facebook  → MySQL sharded + Cassandra for certain workloads
Netflix   → Cassandra
Uber      → MySQL sharded → moved parts to Cassandra over time
Google    → Spanner (their own globally distributed database)
```

The trade-off: most of these databases (Cassandra, DynamoDB) are not fully ACID compliant. They give up strict consistency for horizontal scalability.

---

## But what if you need ACID at scale?

This used to mean your only option was application-level sharding — painful, but ACID-preserving.

That changed with **NewSQL** — a category of databases that are natively distributed AND fully ACID compliant.

```
CockroachDB   → distributed, ACID, Postgres-compatible SQL
Google Spanner → distributed, ACID, used inside Google for financial systems
YugabyteDB    → distributed, ACID, Postgres-compatible
```

These give you horizontal scaling like Cassandra with full ACID like Postgres. The catch: they're complex to operate, expensive, and still carry trade-offs. Google Spanner achieves distributed ACID by using **atomic clocks in every datacenter** to synchronise time globally — that's not something most companies can replicate independently.

---

## The decision tree in practice

```
Need ACID + small/medium scale?
→ Postgres or MySQL (single node + read replicas)

Need ACID + massive scale + can afford the complexity?
→ CockroachDB or Google Spanner

Don't need strict ACID + massive scale?
→ Cassandra, DynamoDB

Already on MySQL, can't afford migration?
→ application-level sharding (painful but proven)
```

> [!important] Most companies never outgrow a well-tuned Postgres
> The companies that do are operating at a scale where they have entire teams dedicated solely to database infrastructure. If you're designing a system in an interview, Postgres with read replicas is a completely valid answer for most problem sizes — you only reach for distributed databases when you can justify the scale that requires it.
