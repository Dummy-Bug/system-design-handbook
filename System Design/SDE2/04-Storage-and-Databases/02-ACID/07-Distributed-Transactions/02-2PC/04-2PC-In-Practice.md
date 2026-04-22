> [!info] 2PC is not magic. The coordinator is just a service making HTTP calls. Each participant exposes /prepare and /commit endpoints. The lock is just a normal database transaction kept open between two API calls.

---

## The coordinator is just making REST calls

There is no special protocol, no shared memory, no direct DB access from the coordinator. The coordinator sends ordinary HTTP (or gRPC) requests to each participant service. Each participant service exposes two endpoints:

```
POST /prepare   ← coordinator calls this in Phase 1
POST /commit    ← coordinator calls this in Phase 2
POST /rollback  ← coordinator calls this if anything fails
```

That's the entire interface.

---

## What a real /prepare request looks like

```json
POST /payment/prepare
{
  "transaction_id": "txn_abc123",
  "payment_id":     "pay_789",
  "amount":         299.00,
  "currency":       "INR",
  "debitor_id":     "user_42",
  "creditor_id":    "merchant_99"
}
```

`transaction_id` is the coordinator's global ID for this distributed transaction. Every participant receives the same `transaction_id` — it's how the coordinator correlates responses across services.

Payment Service receives this and:

```
1. Opens a DB transaction
2. Validates user_42 has balance ≥ 299
3. Runs: SELECT * FROM users WHERE id=42 FOR UPDATE  ← acquires lock
4. Does NOT commit — transaction stays open
5. Writes "PREPARED txn_abc123" to its WAL
6. Stores the open transaction handle keyed by txn_abc123
7. Returns:
```

```json
200 OK
{
  "transaction_id": "txn_abc123",
  "status": "prepared",
  "service": "payment"
}
```

The lock is now held inside Payment's Postgres. The transaction is open, paused, waiting.

---

## What a real /commit request looks like

```json
POST /payment/commit
{
  "transaction_id": "txn_abc123"
}
```

Just the ID. The service already knows everything — it stored the open transaction handle when it prepared. It looks up `txn_abc123`, finds the open transaction, and commits it:

```
1. Look up txn_abc123 → open transaction found
2. Commit the transaction
3. Lock released
4. Write "COMMITTED txn_abc123" to WAL
5. Return:
```

```json
200 OK
{
  "transaction_id": "txn_abc123",
  "status": "committed"
}
```

---

## The full flow with all three services

```
Phase 1 — Coordinator sends PREPARE to all three in parallel:

POST /payment/prepare   { transaction_id: txn_abc123, amount: 299, debitor_id: user_42 ... }
POST /inventory/prepare { transaction_id: txn_abc123, item_id: 99, quantity: 1 ... }
POST /order/prepare     { transaction_id: txn_abc123, user_id: 42, items: [...] ... }

All three respond YES:
  Payment   → lock held on user_42's row in Payment DB
  Inventory → lock held on item_99's row in Inventory DB
  Order     → lock held in Order DB

Phase 2 — Coordinator sends COMMIT to all three in parallel:

POST /payment/commit   { transaction_id: txn_abc123 }
POST /inventory/commit { transaction_id: txn_abc123 }
POST /order/commit     { transaction_id: txn_abc123 }

All three commit and release their locks.
```

---

## The transaction_id is everything

The `transaction_id` is what makes the whole thing work. It correlates:

- The coordinator's global state for this transaction
- Each service's locally stored open transaction handle
- The WAL entries on each participant for crash recovery

Without it, a service receiving `/commit` would have no idea which open transaction to commit.

On idempotency — if the coordinator retries `/commit` due to a network hiccup:

```
Service receives POST /commit { transaction_id: txn_abc123 }
→ checks: is txn_abc123 already committed?
→ yes → return 200 OK, do nothing
→ no  → commit and return 200 OK
```

The coordinator can safely retry without double-committing.

---

## What the lock duration actually is

```
10:00:000  POST /prepare sent to Payment
10:00:005  Payment responds YES, lock acquired     ← lock starts here
           ...
10:00:010  POST /commit sent to Payment
10:00:015  Payment commits, lock released          ← lock ends here

Lock held for: ~10ms (one network round trip)
```

At 1,000 transactions/second, each taking 10ms of lock time — that's 10 rows locked simultaneously at any point. At 10,000 transactions/second it's 100 rows. Other transactions trying to touch those rows queue behind them. This is why 2PC doesn't scale at high throughput — the lock duration is tied to network latency, not just DB speed.

---

## XA transactions — the DB-level protocol

The standard way databases expose this "pause a transaction mid-way" capability is called **XA transactions**. It's a protocol supported by Postgres, MySQL, Oracle, and others.

```
xa_start(txn_abc123)    ← begin the transaction, associate it with this ID
xa_prepare(txn_abc123)  ← lock resources, write to WAL, pause before committing
xa_commit(txn_abc123)   ← actually commit
xa_rollback(txn_abc123) ← rollback
```

Your service's `/prepare` endpoint calls `xa_prepare()` under the hood. Your `/commit` endpoint calls `xa_commit()`. The coordinator never touches the DB directly — it just drives these calls through the service's API.

> [!important] The coordinator never touches participant databases directly
> The coordinator only makes HTTP calls to participant services. Each service owns its own database and decides how to prepare and commit. The coordinator just coordinates the sequence.
