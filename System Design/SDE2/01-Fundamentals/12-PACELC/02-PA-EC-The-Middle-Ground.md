# PA/EC — The Middle Ground

## The Confusion

> [!question] How can a system enforce strong consistency during normal operation but accept inconsistency during a partition? Isn't that contradictory?

It feels backwards. If consistency is important enough to pay the latency cost every day, why abandon it the moment a partition happens?

The answer: **they are two separate modes with different constraints.**

```
Normal operation  → quorum is reachable → enforce consistency (EC)
                    all replicas can talk to each other
                    cost: slightly higher latency, acceptable

Partition happens → quorum is unreachable → consistency is impossible (PA)
                    nodes CANNOT reach each other by definition
                    choice: go down (PC) or serve stale (PA)
                    PA says: better to serve than to refuse
```

The system isn't being inconsistent by choice during normal operation — it's being forced into a trade-off during a failure it cannot control.

---

## The Pilot Analogy

> [!tip] Think of it like a pilot's emergency protocol.

```
Normal flight  → follows every checklist strictly
               → verifies every instrument before proceeding
               → consistent, careful, no shortcuts         (EC)

Emergency      → plane is going down, checklists out the window
               → skips non-critical checks to land the plane
               → availability over process                 (PA)
```

The pilot doesn't abandon safety because they're lazy. They abandon the full protocol because the alternative — crashing — is worse than landing imperfectly.

PA/EC works the same way:
- Normally: be strict, pay the latency cost, enforce correctness
- Partition: crashing (going down) is worse than serving slightly stale data

---

## Why MongoDB Does This

MongoDB's pitch is being a **general-purpose database** — one cluster that can serve different types of data with different consistency needs.

```
Normal operation (no partition):
  Read from primary   → strongly consistent     (EC for critical data)
  Read from secondary → eventually consistent   (EL for non-critical data)
  Your choice per query.

Partition happens:
  Primary unreachable → secondaries take over
  Secondaries serve reads → may be slightly behind  (PA)
  Better than refusing all traffic
```

One MongoDB cluster can serve:
```
Payment service   → reads from primary     → strong consistency
Activity feed     → reads from secondary   → eventual consistency
```

---

## Why Most Engineers Don't Bother

> [!warning] PA/EC is a design smell. In practice, most engineers just pick the right tool.

MongoDB's flexibility is also its weakness. "Configurable" means you can misconfigure it.

```
Need consistency always?      → use PostgreSQL / Google Spanner (PC/EC)
Need speed and availability?  → use Cassandra / DynamoDB        (PA/EL)
Need both in one DB?          → use MongoDB, configure carefully, hope for the best
```

Jack of all trades, master of none. That's why you'll often hear engineers say:

> "Don't use MongoDB for financial data. Use Postgres."
> "Don't use Postgres for a 10M user feed. Use Cassandra."

The right tool has a clear identity. PA/EC systems try to be everything — and that complexity is a cost.

---

## The Key Insight

> [!important] PA/EC is not contradictory — it's a pragmatic trade-off.
>
> "Be strict when I can be. When I physically cannot enforce consistency (partition), stay up rather than go down."
>
> The problem is that most use cases don't need this flexibility. They need a clear, strong guarantee — either consistency always (PC/EC) or availability always (PA/EL).
