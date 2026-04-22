# NFRs And Design Decisions

> [!info] Every NFR forces specific design decisions — and every design decision costs something. State both.

---

## Availability

> [!info] The system must stay up even when components fail.

```
Forces:
  Redundancy at every layer     → no single point of failure
  Multi-AZ deployment           → survive data center failure
  Active-Passive failover       → standby takes over automatically (CP systems)
  Active-Active                 → all nodes serve traffic (AP systems only)
  Load balancer with health checks → detects and routes around failures
  Auto failover                 → no manual intervention when a node dies
```

**Trade-off:**
```
More redundancy = more cost + more operational complexity
Active-Active = availability but conflicts with strong consistency
```

**What to say:**
> "To meet the high availability NFR I need to eliminate every SPOF — app servers, databases, even the load balancer itself. I'd deploy across at least two availability zones with automatic failover."

---

## Consistency

> [!info] Every read must return the latest write. No stale data.

```
Forces:
  Quorum reads/writes           → R + W > N, majority must agree
  Synchronous replication       → replica confirmed before returning success
  CP database                   → Postgres, Spanner — not Cassandra
  SERIALIZABLE isolation        → no phantom reads, no lost updates at DB level
```

**Trade-off:**
```
Strong consistency = higher latency on every write
Quorum = majority of nodes must respond — slower, less available during partitions
```

**What to say:**
> "This is financial data — wrong balance is catastrophic. I need strong consistency via quorum writes and synchronous replication. I'm accepting higher latency as the trade-off."

---

## Latency

> [!info] The system must respond fast — typically P99 < 200ms for user-facing systems.

```
Forces:
  Caching (Redis, Memcached)    → serve from memory, skip DB entirely
  CDN                           → serve static content from edge, close to user
  Read replicas                 → spread read load, read from nearest replica
  Async processing              → don't make user wait for non-critical work
                                   return response, process in background
  Denormalization               → precompute joins, avoid expensive queries at read time
```

**Trade-off:**
```
Cache = fast but potentially stale → eventual consistency
Read replicas = fast but replica lag → stale reads possible
Async = responsive but user doesn't get confirmation immediately
```

**What to say:**
> "The latency NFR forces me towards caching and read replicas. I'm accepting eventual consistency as the trade-off — for a social feed, slightly stale data is fine."

---

## Throughput / Scalability

> [!info] The system must handle massive load — millions of requests per second, hundreds of millions of users.

```
Forces:
  Horizontal scaling            → more app servers, stateless services
  Database sharding             → split data across multiple DB nodes by key
  Partitioning                  → user_id, region — each partition handles a subset
  Read replicas                 → offload reads from primary
  Message queues (Kafka)        → absorb write spikes, process at DB's own pace
  Batching                      → group small writes into larger ones
  Caching                       → reduce DB hits entirely
```

**Trade-off:**
```
Sharding = cross-shard queries are expensive, joins across partitions painful
Queues = writes are async, user doesn't get immediate confirmation
More replicas = more cost
```

**What to say:**
> "At 500M users the DB is the bottleneck. I'd shard by user_id and put Kafka in front of writes to absorb spikes. Cross-shard queries become expensive — I'd denormalize to avoid them."

---

## Durability

> [!info] Data must survive crashes, power loss, disk failure, and data center outages.

```
Forces:
  WAL (Write-Ahead Log)         → write to log before anything else
                                   crash mid-write? replay the log on recovery
  Replication factor 3+         → one copy isn't enough, three is minimum
  Synchronous replication       → RPO = 0, no data loss on failover
  Cross-region backup           → data center gone? another region has it
  Regular backups               → full + incremental, point-in-time recovery
```

**Trade-off:**
```
Synchronous replication = higher write latency
Cross-region replication = higher cost + network latency
More replicas = more storage cost
```

**What to say:**
> "Durability is non-negotiable here. I'd use WAL for crash safety, replication factor 3 across availability zones, and async cross-region backups for disaster recovery."

---

## Security

> [!info] Data must be protected from unauthorized access, interception, and abuse.

```
Forces:
  Authentication                → JWT / OAuth2 — verify identity on every request
  Authorization                 → RBAC — verify permissions after identity confirmed
  Encryption in transit         → TLS/HTTPS — data can't be read if intercepted
  Encryption at rest            → AES-256 — DB compromised? data is unreadable
  Rate limiting                 → prevent abuse, brute force at API gateway level
  Input validation              → SQL injection, XSS — validate at system boundaries
```

**Trade-off:**
```
Encryption = slight CPU overhead on every request
Rate limiting = legitimate users may get throttled under high load
```

**What to say:**
> "Since this handles sensitive data I'd enforce TLS in transit, encryption at rest, JWT-based auth, and rate limiting on all public endpoints."

---

## The NFR → Decision → Trade-off Pattern

> [!important] This three-step move is what separates strong hire answers from average ones.

```
Step 1: State the NFR
  "The NFR here is low latency — feed must load under 200ms"

Step 2: State what it forces
  "That forces me towards caching and read replicas"

Step 3: State the trade-off
  "I'm accepting eventual consistency — for a feed, slightly stale data is fine"
```

Never just say "I'll use Redis." Say why, and say what you're giving up.
