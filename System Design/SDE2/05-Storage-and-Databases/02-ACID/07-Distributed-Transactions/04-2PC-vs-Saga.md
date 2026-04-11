# 2PC vs Saga — When to Use Which

## The core difference in one line

```
2PC   →  all services lock and wait together — true atomicity, but blocks under failure
Saga  →  each service commits independently — eventual consistency, never blocks
```

---

## What "locks" means in 2PC — clearing the misconception

2PC does not require a shared codebase or shared database. The services are completely independent — separate code, separate deployments, separate databases.

The locks are **local to each service's own database**:

```
Payment Service (its own DB)   → locks user row locally
Inventory Service (its own DB) → locks item row locally
Order Service (its own DB)     → locks order row locally
```

The problem is not that the locks are shared — it's that they are **held simultaneously across all services for the entire duration of both phases**. While those locks are held, no other transaction in any of those databases can touch those rows.

At low throughput this is fine. At thousands of orders per second, every service's database is blocked waiting for the coordinator. Latency spikes, queues build up, the system slows to a crawl.

---

## Why 2PC breaks across organisations

2PC requires you to control all participants at the infrastructure level — your services must be able to hold locks inside their databases on your instruction.

```
Your services (same company):
✓  you own the databases
✓  you can tell them to hold locks and wait
✓  they support XA/2PC protocol

External bank (HDFC, SBI):
✗  you don't own their databases
✗  they will never let you hold locks inside their systems
✗  no external 2PC protocol is exposed
```

This is why GPay and PhonePay use Saga — not because the code is in separate repos, but because HDFC and SBI are independent organisations whose databases you cannot control.

---

## Real example — UPI payment

A UPI payment flows through:

```
GPay → NPCI → Bank A (debit) → NPCI → Bank B (credit)
```

For 2PC, NPCI would need to hold a lock on your HDFC account AND the recipient's SBI account simultaneously. HDFC and SBI will never allow this. They're independent banks with their own systems.

So NPCI uses Saga instead. If Bank B's credit fails:

```
Step 1: Debit Bank A        →  committed locally ✓
Step 2: Credit Bank B       →  fails ✗
Step 3: Compensate          →  reverse the debit on Bank A (refund)
```

The user sees "payment pending" for a few seconds. That brief inconsistency is acceptable. What's not acceptable is permanent money loss — and Saga prevents that via compensation.

The one place 2PC lives in payments is **inside a single bank's own database** — debiting and crediting two internal accounts is a local ACID transaction, no distributed coordination needed.

---

## Full comparison

| | 2PC | Saga |
|---|---|---|
| Atomicity | True atomicity — all or nothing | Eventual consistency — briefly inconsistent mid-saga |
| Locks | Local locks in each DB, held across all phases | No locks — each service commits locally and moves on |
| Services | Independent codebases, but you must control all DBs | Independent codebases, no DB control required |
| Works across organisations | No — you can't hold locks in external systems | Yes — compensating transactions work across any API |
| Coordinator failure | Participants freeze holding locks — blocking protocol | No coordinator (choreography) or fault-tolerant orchestrator |
| Failure handling | Automatic rollback coordinated by coordinator | Compensating transactions run in reverse |
| Consistency during failure | Never inconsistent — all or nothing | Briefly inconsistent while compensating transactions run |
| Latency | High — two network round trips + locks held throughout | Low — async, each service moves on immediately |
| Throughput | Low — local locks create contention at high traffic | High — no locks, no waiting across services |
| Complexity | Simpler protocol, fragile under coordinator failure | Each service needs idempotency + compensating transactions |
| Observability | Coordinator knows the full state | Choreography: hard. Orchestration: easy. |

---

## The decision rule

**Use 2PC when:**
- You need true atomicity — not eventual consistency
- You own and control all participating services and their databases
- The system has low throughput (not thousands of transactions per second)
- You're using a distributed SQL database that already supports it (Google Spanner, CockroachDB)
- Inconsistency even for a millisecond is unacceptable (financial ledger, stock trade)

**Use Saga when:**
- Any participant is an external organisation or third-party API
- You need high availability and can tolerate brief inconsistency
- The system is microservice-based with separate databases per service
- Throughput is high — local locks across services would be a bottleneck
- The business can handle compensation (refund, cancel, restock) instead of true rollback
- Most e-commerce, ride-hailing, food delivery, booking, payment systems

---

## Choreography vs Orchestration

| | Choreography | Orchestration |
|---|---|---|
| Control | Decentralised — services react to events | Centralised — orchestrator drives each step |
| Debugging | Hard — flow spread across services and Kafka topics | Easy — full saga state in one place |
| Coupling | Loose — services don't know about each other | Tighter — services coupled to orchestrator |
| Single point of failure | None | Orchestrator (mitigated by fault-tolerance + DB persistence) |
| Best for | Simple flows, small number of steps | Complex flows, many steps, where observability matters |

> [!tip] Interview framing
> "I'd use Saga over 2PC here — 2PC holds local locks in each service's database across two network round trips, which kills throughput at scale. More importantly, if any participant is an external system like a bank or third-party API, 2PC simply can't work — you can't hold locks inside systems you don't control. Saga gives us eventual consistency with compensating transactions, works across any service boundary, and never blocks. For the implementation I'd use orchestration — the full saga state in one place makes debugging and monitoring straightforward."
