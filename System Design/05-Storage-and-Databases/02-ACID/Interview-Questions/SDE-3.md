# ACID — SDE-3 Interview Questions

> [!abstract] Open-ended architecture questions testing ACID guarantees at system boundaries — microservices, distributed transactions, concurrency at scale, and the limits of what ACID can actually protect. SDE-3 level — no single right answer, just structured thinking and clear justification.

---

> [!question] You're the lead architect at a fintech startup. Your monolith uses a single PostgreSQL database with full ACID guarantees. The CTO wants to split it into microservices — each with its own database. He says "we'll keep ACID within each service". What do you tell him about what's lost, and how do you handle it?

> [!success]- Answer
>
> **The CTO is right — but only half right.**
>
> ACID still works fine for operations that touch a single service's database:
> ```
> Order Service     → its own DB → ACID works ✓
> Payment Service   → its own DB → ACID works ✓
> Inventory Service → its own DB → ACID works ✓
> ```
>
> The problem is business operations that span multiple services:
> ```
> User places an order:
> → reserve inventory   (Inventory DB)
> → create order        (Order DB)
> → charge payment      (Payment DB)
> ```
>
> This is one logical transaction across three databases. ACID has no jurisdiction here — there is no single database that can roll all three back atomically if one step fails.
>
> **The real business flow matters:**
> The order of operations is driven by the business, not convenience:
> ```
> User adds to cart   → reserve inventory (reduce available count)
> User checks out     → create order
> User pays           → charge payment
> Order confirmed     → inventory deduction finalised
> ```
> This ordering determines which compensating transactions are needed if something fails.
>
> **The fix — Saga pattern:**
> ```
> Payment fails after order created:
> → publish "payment-failed" event
> → Inventory Service listens → restores inventory count
> → Order Service listens     → marks order as cancelled
> ```
>
> Instead of a global rollback, each service undoes its own work via compensating transactions.
>
> **The fundamental trade-off:**
> ```
> Monolith + single DB     → ACID covers everything, rollback is instant and automatic
>                            system is never in inconsistent state
>
> Microservices + Saga     → ACID within each service only
>                            cross-service operations use compensating transactions
>                            system is briefly inconsistent mid-saga
>                            eventual consistency, not atomicity
> ```
>
> > [!important] The monolith never has a state where order exists but payment failed. The microservice world does — even if only for milliseconds. You're trading atomicity for scalability.
>
> > [!tip] Interview framing
> > *"ACID within each service is correct — but it says nothing about cross-service operations. A user placing an order touches inventory, order, and payment DBs. If payment fails, we can't rollback the other two atomically. We use the Saga pattern — each service publishes failure events, and downstream services execute compensating transactions to undo their own work. The trade-off is brief inconsistency mid-saga instead of atomic rollback."*

---

> [!question] Two users try to book the last available hotel room at the exact same time. Walk me through every layer where this can go wrong and how you'd solve it at each layer.

> [!success]- Answer
>
> **The core problem — lost update via write-write conflict:**
>
> Both users read "room available" — this is not a stale read, it is the correct committed value. The problem is neither transaction knows the other is in progress. Both independently decide to write.
>
> ```
> T1: read → room available = true  ← correct, committed value
> T2: read → room available = true  ← correct, committed value
> T1: write → available = false
> T2: write → available = false     ← both succeed, double booking
> ```
>
> **Layer 1 — Application layer: pessimistic locking**
>
> ```sql
> SELECT * FROM rooms WHERE id = 101 FOR UPDATE;
> ```
>
> T1 acquires the lock. T2 blocks and waits. T1 books the room, commits, releases lock. T2 reads — room unavailable — returns error. No double booking.
>
> **Why not optimistic locking here:**
> ```
> 1000 users read room → available, version = 1
> All 1000 proceed to payment
> All 1000 complete payment
> All 1000 try to write → only 1 succeeds
> → 999 users already charged, bookings rejected
> → 999 refunds needed
> ```
> Optimistic locking is dangerous for high-contention scenarios — users pay before knowing if they won. Pessimistic locking ensures nobody reaches payment unless the room is theirs.
>
> **Pessimistic locking at scale:**
> Under high concurrency, pessimistic locking creates a bottleneck — all users queue for the lock, processed one by one. Acceptable for a single room but becomes a serialisation point at scale.
>
> **Layer 2 — Database layer: unique constraint**
>
> ```sql
> ALTER TABLE bookings
> ADD CONSTRAINT unique_room_date
> UNIQUE (room_id, check_in_date);
> ```
>
> Even if application locking fails — due to a bug, race condition, or direct DB write — the constraint rejects the second insert at the DB level. This is defence in depth: locking handles the flow, the constraint guarantees correctness.
>
> ```
> T1: INSERT booking (room_101, April 6) → succeeds ✓
> T2: INSERT booking (room_101, April 6) → UNIQUE constraint violation ✗
> ```
>
> > [!important] The constraint is not the primary mechanism — it's the last line of defence. If you're relying on constraint violations as your main concurrency control, you'll have lots of failed transactions. Locking handles the flow, constraints guarantee correctness even when locking fails.
>
> > [!tip] Interview framing
> > *"Lost update via write-write conflict — both transactions read the correct committed value, both decide to write, one stomps the other. Fix at app layer with pessimistic locking — nobody proceeds to payment unless the room is theirs. Fix at DB layer with a unique constraint on room_id + date — last line of defence if locking fails. Optimistic locking is wrong here — users would pay before knowing if they got the room."*

---

> [!question] 10,000 concert tickets go on sale at exactly 12pm. 500,000 users hit "Buy" simultaneously. Walk me through every ACID-related problem this creates and how you'd solve each one.

> [!success]- Answer
>
> **Problem 1 — Overselling (Lost Update)**
> 500,000 users simultaneously read "tickets available", all decide to buy. Write-write conflict → tickets sold beyond capacity.
> ```
> Fix: pessimistic locking + unique constraint on seat assignment
>      same pattern as hotel booking
> ```
>
> **Problem 2 — Duplicate charges (no idempotency)**
> User clicks "Buy", request times out, clicks again. Two charges fire for one ticket.
> ```
> Fix: idempotency key on every payment request
>
> POST /checkout
>   idempotency-key: user_123_concert_456_attempt_1
>
> Second identical request → DB sees key already exists
> → returns same response, no second charge
> ```
>
> **Problem 3 — Data loss on crash (fsync=off)**
> Confirmed ticket lost if server crashes before WAL flushes to disk. User told "confirmed", ticket gone on restart.
> ```
> Fix: fsync=on — never turn off for financial or ticketing data
> ```
>
> **Problem 4 — No atomicity (wrong database choice)**
> Some databases don't enforce ACID at all:
> ```
> MySQL with MyISAM engine  → no transactions, no atomicity
> MongoDB (older versions)  → no multi-document transactions by default
> Redis                     → no atomicity across multiple commands
> ```
> A crash mid-transaction leaves partial state — ticket deducted, payment not recorded, no rollback possible.
> ```
> Fix: use ACID-compliant database (PostgreSQL, MySQL InnoDB)
>      never MyISAM or non-transactional store for payments
> ```
>
> > [!important] Choosing the right database is itself an ACID decision. Using Redis or MyISAM for a payment flow violates atomicity by design.
>
> > [!tip] Interview framing
> > *"Four ACID problems: overselling via lost update — fix with pessimistic locking and unique seat constraint. Duplicate charges — fix with idempotency keys. Data loss — fsync=on. Partial transactions — use an ACID-compliant DB. Each is a separate layer of defence."*

---

> [!question] A bug in production caused 50,000 transactions to commit with incorrect data — wrong prices applied to orders. ACID guaranteed they committed successfully. How do you fix this, and what does this tell you about ACID's limits?

> [!success]- Answer
>
> **Why restoring a backup snapshot is wrong:**
> ```
> Restore last backup → wipe everything between backup and now
> → 50,000 bad transactions gone ✓
> → all legitimate transactions in that window also gone ✗
> → users who were correctly charged now have no record
> → refunds become impossible — no data to calculate from
> ```
>
> **The right fix — compensating transactions:**
> ```
> 1. Identify all affected transactions:
>    SELECT * FROM orders
>    WHERE created_at BETWEEN bug_introduced_at AND bug_fixed_at
>    AND price != correct_price;
>
> 2. For each affected order:
>    → calculate difference (what they paid vs correct price)
>    → issue refund or charge adjustment
>
> 3. Correct the data in place:
>    UPDATE orders SET price = correct_price
>    WHERE id IN (affected_ids);
> ```
>
> Surgical correction — no legitimate data touched.
>
> **What this tells you about ACID's limits:**
>
> ACID guaranteed these 50,000 transactions committed correctly and durably. The database did exactly what it was told. But the application had wrong business logic — wrong price calculation.
>
> ```
> ACID guarantees:  data is stored correctly, atomically, and durably
> ACID cannot:      validate that your business logic is correct
> ```
>
> ACID is a database guarantee, not a business correctness guarantee. It ensured the wrong price was committed atomically and durably — which actually made the problem harder to undo, because the data is now permanent and correct from the DB's perspective.
>
> The fix for this class of problem lives outside the DB:
> ```
> Application-level validation  → price range checks before commit
> Anomaly detection             → alert when average order value spikes/drops suddenly
> Audit logging                 → immutable log of every price calculation
> ```
>
> > [!important] ACID guarantees correctness of storage, not correctness of logic. A perfectly ACID-compliant database will commit wrong data with full durability if your application tells it to.
>
> > [!tip] Interview framing
> > *"Restoring a backup wipes all legitimate transactions in that window — too blunt. Instead, identify affected rows, issue compensating transactions (refunds/adjustments), and correct data in place. The deeper lesson: ACID guaranteed the wrong prices committed successfully — ACID validates storage, not business logic. Prevention requires application-level validation and anomaly detection, not DB guarantees."*

---

> [!question] A payments team proposes: write the transaction to the DB, then publish an event to Kafka for downstream services. They say "DB transactions guarantee the write, Kafka guarantees delivery, so the whole flow is safe." What's wrong with this and how do you fix it?

> [!success]- Answer
>
> **The claim is wrong — there's a gap between the two guarantees.**
>
> ```
> 1. Write payment to DB   → committed ✓
>    ← server crashes HERE →
> 2. Publish to Kafka      → never happens ✗
>
> DB has the payment. Kafka never got the event.
> Order service never fulfilled the order.
> Email never sent. Analytics never recorded it.
> User was charged but nothing else happened.
> ```
>
> Each guarantee is valid in isolation — but there's no atomic guarantee **spanning both**. This is the dual-write problem: two systems written in one logical operation with no atomicity between them.
>
> **The fix — Outbox Pattern:**
>
> The outbox pattern converts the dual-write into a single transaction by moving the event write inside the DB:
>
> ```
> Without outbox:
>   Write to DB       → committed ✓
>   CRASH
>   Publish to Kafka  → never happens ✗
>   → two separate operations, crash between them loses the event
>
> With outbox:
>   BEGIN transaction
>     Write payment to payments table  ✓
>     Write event to outbox table      ✓  ← same transaction, ACID covers both
>   COMMIT
>
>   Separate process:
>   reads outbox → publishes to Kafka → marks as sent
>   → Kafka publish fails? event still in outbox → retried
>   → server crashes? event still in outbox on restart → retried
>   → event is never lost
> ```
>
> **Why the outbox works:**
> It doesn't eliminate the dual-write problem — it moves the second write inside the DB transaction so ACID covers it. Kafka publishing becomes a separate, retryable operation. The event can never be lost because it's committed to the DB before the process even tries to publish it.
>
> ```
> ACID covers:    payment write + outbox write (same transaction)
> Kafka handles:  eventual delivery of the event (retryable, guaranteed)
> Gap eliminated: no window where payment exists but event doesn't
> ```
>
> > [!important] The outbox pattern trades immediate Kafka delivery for guaranteed eventual delivery. Downstream services get the event eventually — not instantly. This is the right trade-off for financial systems where losing an event is unacceptable.
>
> > [!tip] Interview framing
> > *"The gap is between the DB commit and the Kafka publish — a crash there loses the event permanently. Fix with the Outbox Pattern: write the event to an outbox table in the same DB transaction as the payment. A separate process reliably ships it to Kafka and retries on failure. ACID covers both writes atomically — the event can never be lost."*
