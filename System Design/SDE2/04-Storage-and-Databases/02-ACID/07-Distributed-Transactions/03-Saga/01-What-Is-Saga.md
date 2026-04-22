> [!info] The Saga pattern
>  breaks a distributed transaction into a sequence of local transactions — one per service. Each service commits locally and triggers the next step. If any step fails, **compensating transactions** run in reverse to undo the previous steps.


## The core insight

2PC tries to give you true atomicity by holding locks and coordinating across services. That's expensive and fragile.

Saga takes a different approach: **stop trying to make it atomic. Instead, make failures recoverable.**

Each service does its own local transaction — no cross-service locks, no coordinator holding everything up. If something fails midway, you don't rollback — you run **compensating transactions** to undo what already succeeded.

---

## What is a compensating transaction?

For every step in the saga that can succeed, you write a reverse operation that undoes it:

| Step | Compensating Transaction |
|---|---|
| Charge payment | Refund the payment |
| Deduct inventory | Add stock back |
| Create order | Cancel the order |

If the saga fails at step 3, you run the compensating transactions for steps 2 and 1 — in reverse order — to unwind the system back to a consistent state.

---

## Eventual consistency — not atomicity

The system is **briefly inconsistent** mid-saga. Between step 1 succeeding and the compensating transaction running, the user is charged but has no order. This window of inconsistency is acceptable as long as the saga always completes — either fully forward or fully reversed.

> [!important] Saga ≠ ACID atomicity
> Saga gives you **eventual consistency**, not atomicity. The system will reach a consistent state eventually — either all steps succeeded, or all compensating transactions ran. But during execution, it is briefly inconsistent.

---

## Idempotency — the critical requirement

Compensating transactions must be **idempotent** — running them twice produces the same result as running them once.

Why? Because the messaging system (Kafka) guarantees **at-least-once delivery**. If a consumer crashes after processing a message but before ACKing Kafka, the message gets redelivered. Your compensating transaction might run twice.

```
"refund payment" delivered
    ↓
refund executes ✓
    ↓
💀 consumer crashes before ACKing Kafka
    ↓
Kafka redelivers "refund payment"
    ↓
refund executes again → double refund 😬
```

Fix — check before acting:

```python
if payment.status != "refunded":
    process_refund()
    payment.status = "refunded"
    db.save(payment)
```

Second delivery sees `status = "refunded"` → skips safely.

> [!danger] Every compensating transaction must be idempotent
> This is not optional. Any service that handles saga events must check whether it already processed that event before acting. Missing this causes double charges, double refunds, and double inventory updates.

---

## Two ways to implement Saga

There are two implementations of the Saga pattern:

- **Choreography** — services talk to each other via events. No central brain. Each service listens to Kafka, reacts to events, and publishes its own events.
- **Orchestration** — a central saga orchestrator tells each service what to do next. One brain, one place to see the full flow.

Both are covered in the next two files.
