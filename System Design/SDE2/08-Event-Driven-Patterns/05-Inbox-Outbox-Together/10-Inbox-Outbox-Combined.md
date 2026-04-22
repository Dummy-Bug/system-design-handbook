
## How They Work Together

Outbox and Inbox solve two different sides of the same problem:

| Pattern | Side | Problem it Solves |
|---|---|---|
| Outbox | Producer | Guarantee event is published to Kafka after DB write |
| Inbox | Consumer | Guarantee event is not processed twice |

Together they give you **exactly-once processing** end-to-end — even though Kafka itself only guarantees at-least-once.

---

## The Pattern

When a consumer needs to both process an event AND publish a new event downstream, it uses inbox + outbox together in one transaction:

```sql
BEGIN TRANSACTION
  -- Inbox: dedup check (consumer side)
  INSERT INTO inbox (event_id) VALUES ('evt-456')
  ON CONFLICT (event_id) DO NOTHING

  -- Business logic: actual DB work
  UPDATE orders SET status = 'shipped' WHERE order_id = 123

  -- Outbox: publish next event (producer side)
  INSERT INTO outbox (event_type, payload)
  VALUES ('SendShippingEmail', '{"order_id": 123, "email": "user@gmail.com"}')
COMMIT
```

Three things in one atomic transaction:
1. Mark incoming event as processed (inbox)
2. Do the business work
3. Queue the next event for publishing (outbox)

---

## Why This Works

If the service crashes at any point:
- Before commit → all three roll back → event retried → safe
- After commit → inbox has the event_id → duplicate delivery skipped

Debezium picks up the outbox row and publishes `SendShippingEmail` to Kafka. The email service then processes it with its own inbox check.

---

## Terminal Actions — The Exception

Not everything can go inside a transaction. **External calls** (sending emails, calling payment APIs, pushing push notifications) cannot be wrapped in a DB transaction.

These are called **terminal actions** — the last step in a chain, with no further DB consistency requirements.

### The Tradeoff: Lost vs Duplicate

**Option A: Do action first, then mark processed**
```
1. Send email (external call)
2. BEGIN TRANSACTION
     INSERT INTO inbox (event_id) ON CONFLICT DO NOTHING
   COMMIT
```
- Crash after email, before marking → **duplicate email on retry**
- Email sent twice — annoying but recoverable

**Option B: Mark processed first, then do action**
```
1. BEGIN TRANSACTION
     INSERT INTO inbox (event_id) ON CONFLICT DO NOTHING
   COMMIT
2. Send email (external call)
```
- Crash after marking, before email → **lost email**
- User never knows order shipped — silent failure

### Which to Choose?

**Always prefer duplicate over lost** for user-facing actions.

Duplicate email = user slightly annoyed.
Lost email = user has no idea what happened, support ticket, churn.

```
Rule: For terminal external calls — act first, mark processed after.
```

---

## When to Use Inbox + Outbox Together

Use this combined pattern when:
- **You are consuming from Kafka AND producing to Kafka**
- You need atomic consistency between the incoming event, your DB state, and the outgoing event
- Example: Order Service consuming `OrderShipped` and producing `SendShippingEmail`

Use only Inbox when:
- You are consuming from Kafka but NOT producing further events
- Example: Read Model Updater consuming `OrderCreated` and updating read model

Use only Outbox when:
- You are producing an event from a DB write (not consuming Kafka)
- Example: App Service writing a new order and publishing `OrderCreated`

---

## Key Insight

> Inbox + Outbox is the contract that makes event-driven systems reliable. Without it, you have races, duplicates, and silent data loss. With it, every step in the chain is atomic and recoverable. The only exception is terminal external calls — and there, you choose the failure mode deliberately: duplicate over lost.
