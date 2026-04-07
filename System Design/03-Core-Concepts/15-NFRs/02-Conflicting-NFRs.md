# Conflicting NFRs

## The Reality

> [!info] In real systems — and in interviews — clients want everything. High availability AND strong consistency. Low latency AND durability. You cannot always have both.

The wrong answer: "We'll achieve both."
The right answer: "These are in tension. Here's the trade-off, and here's what I recommend given the use case."

---

## The Three-Step Move For Every Conflict

```
Step 1: Name the conflict explicitly
  "Availability and strong consistency are in tension here —
   CAP theorem tells us we can't guarantee both during a partition"

Step 2: Pick a winner and justify it
  "Given this is a social feed, availability wins —
   a slightly stale feed is acceptable"

Step 3: State what you're giving up
  "I'm accepting eventual consistency as the trade-off"
```

---

## The Four Common Conflicts

### 1. Availability vs Strong Consistency

> [!important] The most common conflict. CAP and PACELC in action.

```
Client wants:   "Always up AND always fresh data"
The reality:    During a partition, you can't have both

Availability wins when:
  Social feed, shopping cart, activity log
  Slight staleness is acceptable
  Downtime costs more than stale data
  → AP system: Cassandra, DynamoDB
  → Accept eventual consistency

Consistency wins when:
  Payments, bookings, inventory, distributed locks
  Wrong data causes financial loss or data corruption
  Unavailability is recoverable, wrong data is not
  → CP system: Postgres, Spanner, Zookeeper
  → Accept potential unavailability during partition
```

> [!tip] Middle ground: tunable consistency (Cassandra) or causal consistency — provide ordering guarantees without full strong consistency cost.

---

### 2. Low Latency vs Durability

```
Client wants:   "Respond in under 10ms AND never lose data"
The reality:    Durable writes are slower

Low latency wins when:
  Cache layer, session data, ephemeral state
  Losing some data on crash is acceptable
  → Async replication: respond immediately, replicate in background
  → RPO > 0: some data loss possible on failure

Durability wins when:
  Financial transactions, user-generated content, orders
  Data loss is unacceptable
  → Sync replication: wait for replica confirmation before responding
  → RPO = 0: no data loss, but higher write latency
```

---

### 3. Low Latency vs Strong Consistency

```
Client wants:   "Under 200ms response AND always fresh data"
The reality:    Quorum reads are slower than cached reads

Low latency wins when:
  Read-heavy systems where slight staleness is fine
  → Cache aggressively, accept stale reads
  → Read from nearest replica, accept replica lag

Consistency wins when:
  Balance checks, inventory counts, booking availability
  Stale read causes double booking or incorrect charge
  → Read from primary only, skip cache for critical reads
  → Accept higher latency on those specific reads
```

> [!tip] Hybrid approach: cache non-critical reads (user profile, feed), enforce consistency only on critical reads (balance, inventory). Per-operation decision.

---

### 4. High Throughput vs Cost

```
Client wants:   "Handle 10M writes/sec AND keep infrastructure cost low"
The reality:    Scale costs money

What to say:
  "More shards, more replicas, more Kafka partitions = more cost.
   I'd start with a smaller cluster and scale horizontally as load grows.
   Auto-scaling helps — pay for what you use, not peak capacity always."
```

---

## Handling Conflicts In Interviews — Full Pattern

> [!example] Interviewer: "This system needs to be highly available AND strongly consistent."

```
You: "These two NFRs are in tension — CAP theorem tells us that during
      a network partition we can only guarantee one.

      The question is: which is worse for this system —
      returning stale data or refusing requests?

      If this is a payment system — wrong data is catastrophic,
      I'd choose CP. A failed transaction is recoverable.
      A wrong transaction destroys trust.

      If this is a social feed — availability wins.
      A slightly stale feed is far better than an error page.

      For mixed systems I'd apply consistency selectively —
      enforce it on critical paths like payments,
      accept eventual consistency on non-critical paths like feeds."
```

---

## Quick Reference

| Conflict | Winner depends on | Key question |
|---|---|---|
| Availability vs Consistency | Data type | Wrong data or no response — which is worse? |
| Latency vs Durability | Data criticality | Can you afford to lose this data on crash? |
| Latency vs Consistency | Read criticality | Is stale data acceptable for this read? |
| Throughput vs Cost | Business constraints | What's the budget? Start small, scale on demand. |
