# 2PC vs Saga — When to Use Which

## Full comparison

| | 2PC | Saga |
|---|---|---|
| Atomicity | True atomicity — all or nothing | Eventual consistency — briefly inconsistent mid-saga |
| Locks | Holds locks across all services for the entire protocol | No locks — each service commits locally and moves on |
| Coordinator failure | Participants freeze indefinitely holding locks | No coordinator (choreography) or fault-tolerant orchestrator |
| Failure handling | Automatic rollback coordinated by the coordinator | Compensating transactions run in reverse |
| Consistency during failure | Never inconsistent — either all commit or none do | Briefly inconsistent while compensating transactions run |
| Latency | High — two network round trips + locks held throughout | Low — async, no waiting across services |
| Throughput | Low — locks create contention at high traffic | High — no cross-service locks |
| Complexity | Simpler protocol, but fragile under coordinator failure | Each service needs idempotency + compensating transactions |
| Observability | Easy — coordinator knows the state | Choreography: hard. Orchestration: easy. |
| When to use | Strong consistency required, low throughput | High availability, can tolerate brief inconsistency |
| Examples | Google Spanner, financial ledgers, stock trades | Swiggy orders, Uber rides, e-commerce checkouts |

---

## The decision rule

**Use 2PC when:**
- You need true atomicity — not eventual consistency
- The system has low throughput (not thousands of transactions per second)
- You're using a distributed SQL database that already supports it (Google Spanner, CockroachDB)
- Inconsistency even for a millisecond is unacceptable (bank transfer, financial ledger)

**Use Saga when:**
- You need high availability and can tolerate brief inconsistency
- The system is microservice-based with separate databases per service
- Throughput is high — locking across services would be a bottleneck
- The business can handle compensation (refund, cancel, restock) instead of true rollback
- Most e-commerce, ride-hailing, food delivery, booking systems

---

## Choreography vs Orchestration

| | Choreography | Orchestration |
|---|---|---|
| Control | Decentralised — services react to events | Centralised — orchestrator drives each step |
| Debugging | Hard — flow spread across services and Kafka topics | Easy — full saga state in one place |
| Coupling | Loose — services don't know about each other | Tighter — services coupled to orchestrator |
| Single point of failure | None | Orchestrator (mitigated by fault-tolerance + DB persistence) |
| Best for | Simple flows, small number of steps | Complex flows, many steps, where observability matters |

> [!tip] Interview decision rule
> "I'd use Saga over 2PC here — 2PC blocks all participants if the coordinator fails and doesn't scale under high concurrency. Saga gives us eventual consistency with compensating transactions. For the implementation, I'd use orchestration over choreography — the full saga state lives in one place, which makes debugging and monitoring straightforward. The trade-off is each service needs idempotency, but that's a well-understood pattern."
