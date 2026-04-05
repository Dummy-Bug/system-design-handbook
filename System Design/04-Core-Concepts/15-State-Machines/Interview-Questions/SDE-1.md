# State Machines — SDE-1 Interview Questions

> [!abstract] Foundational questions testing basic understanding of states, transitions, terminal states, and the WHERE guard pattern. Every SDE candidate is expected to answer these confidently.

---

## Q1 — What Is a State Machine?

> [!question] What is a state machine and when would you use one in system design?

> [!success]- Answer
>
> **State machine:**
> A model where an entity can be in exactly one state at any time, and can move between states only via defined transitions triggered by specific events.
>
> ```
> States:     the valid situations an entity can be in
> Transitions: the allowed moves between states
> Triggers:   the events that cause transitions
>
> Example — Taxi ride:
>   States: REQUESTED, MATCHED, IN_PROGRESS, COMPLETED, CANCELLED
>   Transition: REQUESTED → MATCHED (trigger: driver accepts)
>   Transition: IN_PROGRESS → COMPLETED (trigger: ride ends)
>   Invalid: COMPLETED → IN_PROGRESS (not allowed — terminal state)
> ```
>
> **When to use one:**
> ```
> Any entity with lifecycle stages:
>   Orders     → PENDING → PROCESSING → SHIPPED → DELIVERED
>   Payments   → INITIATED → PROCESSING → COMPLETED / FAILED
>   Bookings   → HOLD → CONFIRMED → ACTIVE → COMPLETED
>   Tickets    → OPEN → IN_PROGRESS → RESOLVED / CLOSED
>   Auctions   → OPEN → ENDING_SOON → CLOSED → SETTLED
> ```
>
> **Why it matters in interviews:**
> State machines make illegal transitions impossible to execute — they're a built-in correctness guarantee. Without one, any code path could set any status, leading to corrupted lifecycle state.
>
> > [!tip] Interview framing
> > *"A state machine models an entity's lifecycle — valid states and the allowed transitions between them. I'd use one for any entity with stages: orders, payments, bookings, rides. It makes illegal transitions impossible and gives a clear model for how the system works."*

---

## Q2 — Drawing a State Machine

> [!question] Draw the state machine for a hotel reservation — from initial hold to checkout.

> [!success]- Answer
>
> **States:**
> ```
> HOLD        → reservation created, not yet paid, slot temporarily reserved
> CONFIRMED   → payment completed, reservation secured
> ACTIVE      → guest has checked in
> COMPLETED   → guest has checked out
> EXPIRED     → HOLD was not paid within timeout window
> CANCELLED   → reservation cancelled (from HOLD or CONFIRMED)
> ```
>
> **State diagram:**
> ```
> HOLD ──(payment confirmed)──→ CONFIRMED ──(check-in)──→ ACTIVE ──(check-out)──→ COMPLETED
>   │                               │
>   └──(10 min timeout)──→ EXPIRED  └──(user cancels)──→ CANCELLED
> ```
>
> **Key design decisions:**
> ```
> Terminal states: COMPLETED, EXPIRED, CANCELLED
>   → No transitions out of these
>   → Once completed or cancelled, no further changes
>
> Timeout transition: HOLD → EXPIRED
>   → If user doesn't pay in 10 minutes, release the room
>   → Implemented by a background job scanning for expired HOLDs
>
> Cancellation policy: only from HOLD or CONFIRMED
>   → Cannot cancel ACTIVE (already checked in)
>   → Cannot cancel COMPLETED (already checked out)
> ```
>
> **What CANNOT happen:**
> ```
> COMPLETED → ACTIVE     (can't un-checkout)
> EXPIRED   → HOLD       (can't revive an expired hold)
> CANCELLED → CONFIRMED  (can't reinstate a cancellation)
> ```
>
> > [!tip] Interview framing
> > *"Draw states as circles, transitions as arrows, event labels on arrows. Start with the happy path (HOLD → CONFIRMED → ACTIVE → COMPLETED), then add terminal states and error/timeout paths. Explicitly call out which states allow cancellation and what the timeout behavior is."*

---

## Q3 — The WHERE Guard Pattern

> [!question] How do you implement a state transition in the database safely, so two concurrent servers can't transition the same entity simultaneously?

> [!success]- Answer
>
> **The pattern — status column + WHERE guard:**
>
> ```sql
> -- Transitioning order from PENDING to PROCESSING
> UPDATE orders
> SET status = 'PROCESSING'
> WHERE id = 123
>   AND status = 'PENDING'   ← the WHERE guard
>
> -- Check rows affected
> IF rows_affected = 0:
>     THROW IllegalTransitionException
> ```
>
> **Why this is safe with concurrent servers:**
> ```
> Server A and Server B both try to process order 123 simultaneously
>
> Server A: UPDATE ... WHERE id=123 AND status='PENDING'
> Server B: UPDATE ... WHERE id=123 AND status='PENDING'
>
> Database serializes these two writes (one at a time):
>   Server A's UPDATE executes → status = 'PROCESSING' → 1 row affected
>   Server B's UPDATE executes → status is now 'PROCESSING', not 'PENDING'
>                                → WHERE guard fails → 0 rows affected
>
> Server A: sees 1 row → transition succeeded → continues processing
> Server B: sees 0 rows → transition failed → throws error / backs off
> ```
>
> **This gives you optimistic locking for free:**
> ```
> No explicit SELECT FOR UPDATE needed
> No locks held across network calls
> The status column IS the version number
> Database atomically performs check-and-update
> ```
>
> > [!important] Always check the number of rows affected after a state transition UPDATE. Zero rows means the entity was already in a different state — someone else transitioned it first. Throw an error, don't silently continue.
>
> > [!tip] Interview framing
> > *"WHERE guard: UPDATE orders SET status='PROCESSING' WHERE id=X AND status='PENDING'. If 0 rows affected, someone else already transitioned it — throw an error. This is optimistic locking built into the state machine — no explicit locks needed."*

---

## Q4 — Audit Trail

> [!question] Your system needs to track the full history of state transitions for an order (for customer support and debugging). How do you design this?

> [!success]- Answer
>
> **Two tables — entity table + events table:**
>
> ```sql
> -- Entity table: current state only
> orders (
>   id          BIGINT PRIMARY KEY,
>   status      VARCHAR(20),   -- current state
>   updated_at  TIMESTAMP
> )
>
> -- Events table: full history
> order_events (
>   id           BIGINT PRIMARY KEY,
>   order_id     BIGINT,
>   from_status  VARCHAR(20),  -- where we came from
>   to_status    VARCHAR(20),  -- where we went
>   triggered_by VARCHAR(100), -- who/what triggered it (user_id, system, webhook)
>   occurred_at  TIMESTAMP,    -- when it happened
>   metadata     JSONB         -- optional: context (reason for cancellation, etc.)
> )
> ```
>
> **Write both in one transaction:**
> ```sql
> BEGIN TRANSACTION
>
> -- 1. Update current state (with WHERE guard)
> UPDATE orders SET status = 'CONFIRMED' WHERE id = 123 AND status = 'HOLD'
>
> -- 2. Write history record
> INSERT INTO order_events (order_id, from_status, to_status, triggered_by, occurred_at)
> VALUES (123, 'HOLD', 'CONFIRMED', 'payment_service', NOW())
>
> COMMIT
>
> -- If WHERE guard returns 0 rows → ROLLBACK → no history record written
> ```
>
> **Why atomic write matters:**
> ```
> Status updated but no event written → history is incomplete → can't reconstruct timeline
> Event written but status not updated → ghost event → inconsistent history
> Transaction ensures both happen or neither happens
> ```
>
> > [!tip] Interview framing
> > *"Two tables: entity table for current state, events table for full history. Write both atomically in one transaction. Events capture from_state, to_state, triggered_by, and timestamp. This gives customer support a full audit trail and gives engineers a debugging timeline."*

---

## Q5 — Timeout-Driven Transitions

> [!question] A hotel reservation expires if not paid within 10 minutes. How do you implement the HOLD → EXPIRED transition?

> [!success]- Answer
>
> **The problem:**
> The HOLD → EXPIRED transition isn't triggered by a user action — it's triggered by time passing. How do you fire it automatically?
>
> **The solution — background job:**
> ```
> Scheduled job runs every minute (or every 30 seconds)
>
> SELECT id FROM reservations
> WHERE status = 'HOLD'
>   AND created_at < NOW() - INTERVAL '10 minutes'
>
> For each result:
>   UPDATE reservations SET status = 'EXPIRED'
>   WHERE id = X AND status = 'HOLD'   ← WHERE guard still needed
>
>   INSERT INTO reservation_events (...)
>
>   Release the room slot back to available
> ```
>
> **Why the WHERE guard is still required in the background job:**
> ```
> Job runs at T=10min → finds reservation R → starts transition
> User pays at T=10min+1sec → HOLD → CONFIRMED transition fires
>
> Without WHERE guard:
>   Both transitions succeed → reservation is EXPIRED after being CONFIRMED ✗
>
> With WHERE guard:
>   Job UPDATE: WHERE status='HOLD' → user already set it to CONFIRMED → 0 rows → skip ✓
>   User's transition won the race → correct outcome
> ```
>
> **Scale consideration:**
> ```
> At high volume: millions of reservations
> Background job scanning millions of rows every minute → expensive
>
> Better: index on (status, created_at)
>         → fast scan of only HOLD rows past deadline
> ```
>
> > [!tip] Interview framing
> > *"Timeout transitions are handled by a background job scanning for entities past their deadline. Still use the WHERE guard — a user might pay right as the job fires. Without it, a confirmed reservation could get marked EXPIRED. Index on (status, created_at) to keep the scan fast."*
