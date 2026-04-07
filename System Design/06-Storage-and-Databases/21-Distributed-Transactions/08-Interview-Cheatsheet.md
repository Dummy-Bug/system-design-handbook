# Interview Cheatsheet — Distributed Transactions

> [!question] What is the distributed transaction problem?
>> [!success]-
>> ACID gives you atomicity within one database. But when a transaction spans multiple services — each with their own database — there is no single database to wrap a transaction around. If Payment succeeds but Order Service fails, the user is charged with no order. You need a way to make all steps either all succeed or all fail together across service boundaries.

---

> [!question] What is 2PC and what are its problems?
>> [!success]-
>> Two-Phase Commit uses a central coordinator to achieve true atomicity across multiple databases.
>>
>> Phase 1 (Prepare): coordinator asks all participants "are you ready?" — each locks its resources and votes YES or NO.
>> Phase 2 (Commit/Abort): if all voted YES → coordinator sends COMMIT. If any voted NO → coordinator sends ABORT.
>>
>> Problems:
>> - **Blocking protocol** — if the coordinator crashes after Phase 1, participants hold locks indefinitely waiting for a decision they never get
>> - **Partial commits** — coordinator might commit some participants before crashing — participants can't safely rollback on their own
>> - **High latency** — two network round trips plus locks held across both phases
>> - **Coordinator is SPOF** — single point of failure
>>
>> > [!tip] Interview framing
>> > "2PC gives true atomicity but at the cost of availability — a coordinator crash leaves all participants blocked holding locks. For high-throughput systems, this is unacceptable. I'd use Saga instead."

---

> [!question] What is the Saga pattern?
>> [!success]-
>> Saga breaks a distributed transaction into a sequence of local transactions — one per service. Each service commits locally and triggers the next step. If any step fails, **compensating transactions** run in reverse to undo what already succeeded.
>>
>> Saga gives eventual consistency, not atomicity. The system is briefly inconsistent mid-saga, but will always reach a consistent state — either all forward or all compensated.
>>
>> Two implementations: Choreography (decentralised, event-driven) and Orchestration (central brain).

---

> [!question] What is a compensating transaction and why must it be idempotent?
>> [!success]-
>> A compensating transaction is the reverse operation for a saga step — charge payment → refund payment, deduct inventory → add stock back.
>>
>> It must be idempotent because Kafka guarantees at-least-once delivery. If a consumer crashes after processing but before ACKing Kafka, the message is redelivered. The compensating transaction must detect it already ran and skip safely — otherwise you get double refunds, double restocks, etc.
>>
>> Fix: check state before acting — `if payment.status != "refunded": process_refund()`

---

> [!question] Choreography vs Orchestration — what's the difference?
>> [!success]-
>> **Choreography** — no central brain. Services listen to Kafka events, react, publish their own events. Decentralised. Hard to debug — the flow is spread across multiple services and Kafka topics. No single place to see what happened to a specific order.
>>
>> **Orchestration** — a central saga orchestrator tells each service what to do next. The full saga state lives in one place. Easy to debug — you open the orchestrator's log for order 123 and see every step, success, and failure in order.
>>
>> Orchestrator must persist state to its own DB before sending each command — so it can resume correctly after a crash.
>>
>> > [!tip] Interview framing
>> > "I'd use orchestration — it gives centralised observability, which matters operationally. The orchestrator persists state to a DB before each command, so it can recover after a crash. Services still need idempotency for duplicate commands, but they only deal with one caller instead of coordinating with each other."

---

> [!question] When do you use 2PC vs Saga?
>> [!success]-
>> **2PC**: true atomicity required, low throughput, using a distributed SQL DB that supports it (Spanner, CockroachDB). Financial ledgers, stock trades, bank transfers — where even milliseconds of inconsistency is unacceptable.
>>
>> **Saga**: high availability needed, microservice architecture with separate DBs, high throughput, business can handle compensation. E-commerce, food delivery, ride-hailing, booking systems.

---

## Quick reference

```
2PC:
Coordinator → PREPARE → all participants lock + vote
All YES → Coordinator → COMMIT → all commit + unlock
Any NO  → Coordinator → ABORT  → all rollback + unlock
Problem: coordinator crash = participants blocked forever

Saga (Choreography):
Service A commits → publishes event → Kafka → Service B commits → ...
On failure: publish failure event → previous services run compensating transactions
Problem: hard to debug, idempotency scattered across all services

Saga (Orchestration):
Orchestrator → tells Service A → ACK → tells Service B → ACK → ...
On failure: orchestrator triggers compensating transactions in reverse
Orchestrator persists state to DB before each command
Both orchestrator + services need idempotency
Advantage: full saga state in one place, easy to debug
```
