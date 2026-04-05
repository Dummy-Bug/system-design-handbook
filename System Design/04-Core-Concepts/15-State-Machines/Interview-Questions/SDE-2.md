# State Machines — SDE-2 Interview Questions

> [!abstract] Scenario-based questions testing trade-off reasoning around concurrent state transitions, payment state design, timeout handling at scale, and idempotent operations. Expected at SDE-2 level.

---

## Q1 — Payment State Machine Design

> [!question] Design the state machine for a payment in an e-commerce system. Include both success and failure paths, and explain how you handle the transition from PROCESSING to FAILED when the payment processor times out.

> [!success]- Answer
>
> **States:**
> ```
> INITIATED   → payment record created, not yet sent to processor
> PROCESSING  → sent to payment processor, awaiting response
> COMPLETED   → processor confirmed successful charge
> FAILED      → processor rejected or no response received
> REFUNDED    → charge reversed (from COMPLETED only)
> ```
>
> **State diagram:**
> ```
> INITIATED ──(sent to processor)──→ PROCESSING ──(processor confirms)──→ COMPLETED
>                                         │                                    │
>                                         ├──(processor rejects)──→ FAILED    └──(refund)──→ REFUNDED
>                                         └──(timeout after 30s)──→ FAILED
> ```
>
> **The hard case — timeout:**
> ```
> Request sent to processor at T=0
> No response after 30 seconds → transition to FAILED
>
> Problem: did the processor receive the request?
>   Unknown: processor may have charged the user but response was lost in transit
>
>   If we mark FAILED and user retries → potential double charge
> ```
>
> **Safe timeout handling:**
>
> ```
> 1. Idempotency key sent with every payment request
>    idempotency_key = "order-123-payment-attempt-1"
>
> 2. On timeout:
>    → Transition to FAILED (or UNKNOWN state)
>    → Do NOT let user retry with a new payment immediately
>
> 3. Background reconciliation job (runs every 5 minutes):
>    For each FAILED payment with unclear status:
>      → Query processor: "Did charge with idempotency_key X go through?"
>      → Yes: mark COMPLETED, fulfill order
>      → No:  confirm FAILED, allow retry
>
> 4. User-facing: "Your payment is being processed — we'll confirm shortly"
>    Never: "Payment failed, try again" before reconciliation
> ```
>
> **The WHERE guard on transition:**
> ```sql
> UPDATE payments
> SET status = 'FAILED', failed_at = NOW(), failure_reason = 'timeout'
> WHERE payment_id = 'pay_123'
>   AND status = 'PROCESSING'   ← WHERE guard
>
> -- If processor response arrives simultaneously:
> --   The first update wins, the second gets 0 rows → ignored ✓
> ```
>
> > [!tip] Interview framing
> > *"Timeout from processor is the hardest case — you don't know if the charge went through. Use idempotency keys + background reconciliation. Don't mark FAILED and immediately allow retry — that risks double charge. Query the processor out-of-band to confirm before marking final state."*

---

## Q2 — Concurrent State Transitions

> [!question] Two webhook callbacks from Stripe arrive simultaneously: one says payment SUCCEEDED, one says payment FAILED (race condition). How does your state machine handle this without data corruption?

> [!success]- Answer
>
> **The scenario:**
> ```
> Payment is in PROCESSING state
>
> Stripe sends two webhooks (possibly a bug or network retry):
>   Webhook 1: payment_intent.succeeded
>   Webhook 2: payment_intent.payment_failed
>
> Both arrive at your servers within 100ms of each other
> Both try to transition the payment simultaneously
> ```
>
> **Without WHERE guard — the corruption:**
> ```
> Server A: reads status = PROCESSING → transitions to COMPLETED
> Server B: reads status = PROCESSING → transitions to FAILED
>
> Last write wins → payment could end up COMPLETED or FAILED arbitrarily
> If COMPLETED → order fulfilled for a payment that failed ✗
> If FAILED → order not fulfilled for a payment that succeeded ✗
> ```
>
> **With WHERE guard — safe handling:**
> ```sql
> Server A (SUCCEEDED callback):
> UPDATE payments SET status = 'COMPLETED'
> WHERE payment_id = 'pay_123'
>   AND status = 'PROCESSING'   ← WHERE guard
>
> IF rows_affected = 1 → transition succeeded, process order ✓
>
> Server B (FAILED callback) — same millisecond:
> UPDATE payments SET status = 'FAILED'
> WHERE payment_id = 'pay_123'
>   AND status = 'PROCESSING'   ← WHERE guard
>
> IF rows_affected = 0 → already transitioned by Server A → log and ignore ✓
> ```
>
> **The database serializes the concurrent writes:**
> ```
> Only one of the two UPDATEs can find status = 'PROCESSING'
> The first one wins → 1 row affected → transition executed
> The second one arrives → finds status already changed → 0 rows → rejected
>
> State machine integrity preserved ✓
> ```
>
> **Webhook deduplication (defense in depth):**
> ```
> Stripe sends webhooks with a unique event ID
> Store processed event IDs in a table
>
> On receipt: has event_id been processed?
>   Yes → ignore (duplicate delivery) ✓
>   No  → process + store event_id
>
> Prevents any duplicate processing even if WHERE guard somehow fails
> ```
>
> > [!tip] Interview framing
> > *"WHERE guard makes concurrent transitions safe — database serializes the two updates, only the first finds the row in PROCESSING state. The second gets 0 rows and is discarded. Add webhook deduplication on top (store Stripe event IDs) as a defense-in-depth layer."*

---

## Q3 — Handling Expired Holds at Scale

> [!question] Your hotel booking system has 10 million HOLD reservations that need to expire after 10 minutes if unpaid. How do you implement the background expiration job efficiently?

> [!success]- Answer
>
> **Naive approach — full table scan:**
> ```sql
> -- Runs every minute
> UPDATE reservations SET status = 'EXPIRED'
> WHERE status = 'HOLD'
>   AND created_at < NOW() - INTERVAL '10 minutes'
>
> Problem: full table scan on 10M rows every minute
>           → DB under constant heavy load
>           → Holds up other queries
> ```
>
> **Fix 1 — Proper index:**
> ```sql
> CREATE INDEX idx_reservations_hold_expiry
> ON reservations (status, created_at)
> WHERE status = 'HOLD'  ← partial index — only HOLD rows
>
> Now: index-only scan on HOLD rows
>      Only touch HOLDs past their expiry → no full table scan ✓
>
> At 10M total reservations but maybe 50k active HOLDs:
>   Scan 50k rows not 10M → 200x faster
> ```
>
> **Fix 2 — Process in batches:**
> ```sql
> -- Don't update all expired HOLDs in one giant UPDATE
> -- That locks too many rows at once
>
> LOOP:
>   UPDATE reservations SET status = 'EXPIRED'
>   WHERE reservation_id IN (
>     SELECT reservation_id FROM reservations
>     WHERE status = 'HOLD' AND created_at < NOW() - INTERVAL '10 minutes'
>     LIMIT 100   ← process 100 at a time
>   )
>   AND status = 'HOLD'  ← WHERE guard for concurrency
>
>   BREAK when rows_affected = 0
> ```
>
> **Fix 3 — Dedicated expiry queue (for very high scale):**
> ```
> When reservation is created:
>   Push to delayed queue: (reservation_id, expire_at = created_at + 10min)
>
> Consumer runs continuously:
>   Poll queue for items where expire_at < NOW()
>   For each: attempt HOLD → EXPIRED transition (with WHERE guard)
>
> Benefits:
>   No DB scanning at all
>   Each expiration is O(1) — just process the queue
>   Decoupled from booking writes
>
> Implementation: Redis sorted set (score = expire_at timestamp)
>   ZADD expiry_queue <timestamp> reservation_id
>   ZRANGEBYSCORE expiry_queue 0 <now> → returns all expired
> ```
>
> > [!tip] Interview framing
> > *"Naive full table scan on 10M rows every minute is expensive. Fix: partial index on (status, created_at) WHERE status='HOLD' — only scan HOLD rows (50k not 10M). Process in batches of 100 to limit lock contention. For high scale: Redis sorted set as an expiry queue — push on creation, consume continuously."*

---

## Q4 — Ride-Hailing State Machine

> [!question] Design the state machine for a taxi ride. A user can only cancel before the driver has arrived. A driver can cancel after accepting but before pickup. What state transitions are allowed for each actor?

> [!success]- Answer
>
> **States:**
> ```
> REQUESTED    → rider placed request, no driver yet
> MATCHED      → driver accepted, en route to pickup
> ARRIVED      → driver at pickup location
> IN_PROGRESS  → ride started
> COMPLETED    → ride finished, payment processed
> CANCELLED    → ride cancelled (terminal)
> ```
>
> **Transition matrix by actor:**
>
> ```
> Rider can cancel:
>   REQUESTED → CANCELLED  ✓  (before any driver: no penalty)
>   MATCHED   → CANCELLED  ✓  (driver en route: possible cancellation fee)
>   ARRIVED   → CANCELLED  ✓  (driver waiting: cancellation fee applies)
>   IN_PROGRESS → CANCELLED  ✗  (ride started: cannot cancel, must complete)
>
> Driver can cancel:
>   MATCHED     → CANCELLED  ✓  (before pickup: allowed with penalty for driver)
>   ARRIVED     → CANCELLED  ✓  (passenger not appearing: allowed with note)
>   IN_PROGRESS → CANCELLED  ✗  (cannot abandon a ride in progress)
>
> System transitions:
>   MATCHED → ARRIVED      (driver marks arrival)
>   ARRIVED → IN_PROGRESS  (driver starts ride)
>   IN_PROGRESS → COMPLETED (driver ends ride + payment)
> ```
>
> **DB implementation:**
> ```sql
> -- Rider cancels from MATCHED state
> UPDATE rides
> SET status = 'CANCELLED',
>     cancelled_by = 'rider',
>     cancelled_at = NOW(),
>     cancellation_reason = 'rider_request'
> WHERE ride_id = 'ride_abc'
>   AND status IN ('REQUESTED', 'MATCHED', 'ARRIVED')  ← only these states
>   AND rider_id = current_user_id  ← only the rider of THIS ride
>
> IF rows_affected = 0:
>   status was IN_PROGRESS or COMPLETED → transition not allowed
>   OR someone else's ride → not authorized
> ```
>
> **Cancellation fee logic:**
> ```
> ON CANCELLED transition:
>   Read previous status from events table
>   REQUESTED:    no fee
>   MATCHED:      small fee (driver lost opportunity)
>   ARRIVED > 2min: larger fee (driver waited)
>
>   Trigger payment for fee asynchronously
> ```
>
> > [!tip] Interview framing
> > *"State matrix by actor: riders can cancel from REQUESTED/MATCHED/ARRIVED but not IN_PROGRESS. Drivers can cancel from MATCHED/ARRIVED but not IN_PROGRESS. WHERE clause in the UPDATE restricts both state and actor — only the ride's rider can cancel it, and only from permitted states. Cancellation fee is post-hoc logic triggered by the event record."*

---

## Q5 — State Machine for Long-Running Async Jobs

> [!question] You're building a video transcoding pipeline. Jobs can take 10 minutes and may fail midway. Design the state machine including retry logic with exponential backoff.

> [!success]- Answer
>
> **States:**
> ```
> PENDING      → job queued, not yet picked up
> IN_PROGRESS  → worker processing it
> COMPLETED    → transcoding done, output available
> FAILED       → all retries exhausted
> RETRYING     → will be retried after backoff delay
> ```
>
> **State diagram:**
> ```
> PENDING ──(worker picks up)──→ IN_PROGRESS ──(success)──→ COMPLETED
>                                     │
>                                     ├──(failure, attempts < max)──→ RETRYING ──(backoff elapsed)──→ PENDING
>                                     └──(failure, attempts = max)──→ FAILED
> ```
>
> **Schema:**
> ```sql
> jobs (
>   id              BIGINT PRIMARY KEY,
>   status          VARCHAR(20),
>   attempt_count   INT DEFAULT 0,
>   max_attempts    INT DEFAULT 3,
>   next_retry_at   TIMESTAMP,  -- when to allow next attempt
>   worker_id       VARCHAR(50), -- which worker owns it
>   locked_until    TIMESTAMP,  -- heartbeat-based lock expiry
>   created_at      TIMESTAMP,
>   completed_at    TIMESTAMP,
>   error_message   TEXT
> )
> ```
>
> **Worker claiming a job (with race-safe SELECT FOR UPDATE):**
> ```sql
> BEGIN;
> SELECT id FROM jobs
> WHERE status = 'PENDING'
>   AND (next_retry_at IS NULL OR next_retry_at < NOW())
> LIMIT 1
> FOR UPDATE SKIP LOCKED;  ← skip rows already locked by other workers
>
> UPDATE jobs SET
>   status = 'IN_PROGRESS',
>   worker_id = :worker_id,
>   locked_until = NOW() + INTERVAL '15 minutes',  ← heartbeat window
>   attempt_count = attempt_count + 1
> WHERE id = :claimed_id;
> COMMIT;
> ```
>
> **On failure — transition to RETRYING with backoff:**
> ```sql
> -- Exponential backoff: 1min, 2min, 4min for attempts 1, 2, 3
> backoff_seconds = 60 * (2 ^ (attempt_count - 1))
>
> UPDATE jobs SET
>   status = CASE
>     WHEN attempt_count >= max_attempts THEN 'FAILED'
>     ELSE 'RETRYING'
>   END,
>   next_retry_at = CASE
>     WHEN attempt_count < max_attempts THEN NOW() + INTERVAL ':backoff_seconds seconds'
>     ELSE NULL
>   END,
>   worker_id = NULL,
>   error_message = :error
> WHERE id = :job_id
>   AND status = 'IN_PROGRESS'  ← WHERE guard
>   AND worker_id = :worker_id   ← only this worker can fail its own job
> ```
>
> **Orphan detection (worker crashes mid-job):**
> ```
> Background job scans every 5 minutes:
>   SELECT * FROM jobs WHERE status = 'IN_PROGRESS' AND locked_until < NOW()
>   → Worker crashed without updating status
>   → Transition back to PENDING (or RETRYING with incremented attempt_count)
> ```
>
> > [!tip] Interview framing
> > *"FOR UPDATE SKIP LOCKED lets multiple workers claim jobs safely without collisions. locked_until + heartbeat handles crashed workers — orphaned jobs return to PENDING after the lock expires. Exponential backoff: 60s, 120s, 240s. WHERE guard on failure ensures only the owning worker can transition the job."*
