# State Machines — Interview Cheatsheet

## What To Say When Asked "Walk Me Through The States"

> [!tip] Draw states as circles, transitions as arrows, label the trigger event on each arrow.

```
Step 1: List all states the entity can be in
Step 2: Draw the happy path first (left to right)
Step 3: Add terminal states (COMPLETED, CANCELLED, FAILED)
Step 4: Add error/edge paths (what can be cancelled? from which states?)
Step 5: Identify any timeout-driven transitions
```

---

## Real-World State Examples

### Taxi Ride
```
REQUESTED ──(driver accepts)──→ MATCHED ──(ride starts)──→ IN_PROGRESS ──(ride ends)──→ COMPLETED
    │                               │                            │
    └──(user cancels)──→ CANCELLED  └──(driver cancels)──→ CANCELLED  └──(user cancels)──→ CANCELLED
```

### Hotel Reservation
```
HOLD ──(user pays)──→ CONFIRMED ──(check-in)──→ ACTIVE ──(check-out)──→ COMPLETED
  │                       │
  └──(10 min timeout)──→ EXPIRED   └──(user cancels)──→ CANCELLED
```

### Payment
```
INITIATED ──(sent to processor)──→ PROCESSING ──(processor confirms)──→ COMPLETED
                                        │                                     │
                                        └──(processor rejects)──→ FAILED      └──(refund requested)──→ REFUNDED
```

### Task / Job Queue
```
PENDING ──(worker picks up)──→ IN_PROGRESS ──(success)──→ COMPLETED
                                    │
                                    ├──(failure, retries left)──→ RETRYING ──→ IN_PROGRESS
                                    └──(failure, no retries)──→ FAILED
```

### Auction
```
OPEN ──(end time approaching)──→ ENDING_SOON ──(end time reached)──→ CLOSED ──(payment confirmed)──→ SETTLED
                                                                          │
                                                                          └──(no bids / payment failed)──→ CANCELLED
```

---

## Implementation Pattern — Say This Out Loud

```
"I'll store the current state in a status column on the entity table.
 Every transition uses a WHERE guard on the current status —
 if the guard fails (0 rows affected), the transition was illegal and I reject it.
 This gives me optimistic locking for free — the state IS the version number.
 I'll also maintain an events table for audit history, written atomically
 in the same transaction as the status update."
```

---

## The Three Questions Interviewers Ask

> [!warning] Be ready for these

**"What happens if two servers try to transition the same entity simultaneously?"**
```
The WHERE guard handles it. Only one UPDATE will match — the other gets 0 rows affected.
No explicit locks needed. The database serializes the writes.
```

**"How do you handle timeouts — like a reservation that expires?"**
```
Background job runs periodically, scans for entities past their deadline,
transitions them. This keeps DB status accurate and queries by status reliable.
```

**"Do you keep history of state transitions?"**
```
Yes — events table. Every transition writes a row with from_state, to_state,
triggered_by, and timestamp. Written atomically with the status update.
This gives full audit trail and debugging history.
```

---

## Full Checklist

- [ ] List all states before designing anything else
- [ ] Draw the state diagram — circles + arrows + trigger labels
- [ ] Identify terminal states (COMPLETED, CANCELLED, FAILED, EXPIRED)
- [ ] Identify timeout-driven transitions — what expires? after how long?
- [ ] Implement via status column + WHERE guard (optimistic locking)
- [ ] Check affected row count — 0 rows = illegal transition, throw error
- [ ] Write events table for audit trail, atomically with status update
- [ ] Wrap both writes in a transaction
- [ ] State which states allow cancellation — not everything is cancellable
- [ ] Connect to concurrency — WHERE guard = optimistic locking, state = version number

---

## Quick Reference — Label Each System

| System | Key States | Timeout transition |
|---|---|---|
| Taxi ride | REQUESTED → MATCHED → IN_PROGRESS → COMPLETED | none typical |
| Hotel reservation | HOLD → CONFIRMED → ACTIVE → COMPLETED | HOLD → EXPIRED (10 min) |
| Payment | INITIATED → PROCESSING → COMPLETED / FAILED / REFUNDED | PROCESSING → FAILED (timeout) |
| Task queue | PENDING → IN_PROGRESS → COMPLETED / FAILED / RETRYING | IN_PROGRESS → FAILED (worker timeout) |
| Auction | OPEN → ENDING_SOON → CLOSED → SETTLED / CANCELLED | OPEN → ENDING_SOON (schedule) |
