> [!question] Your app needs to save data to the database AND publish an event to Kafka. How do you guarantee both happen, or neither happens?

---

## The problem — publishing to Kafka after a DB write

You're building a hotel booking system. When a booking is confirmed, two things must happen:

```
1. Save the booking to your database
2. Publish a "booking_confirmed" event to Kafka
   → email notification service subscribes
   → inventory update service subscribes
   → analytics service subscribes
```

Your app code does this:

```java
db.save(booking);           // step 1
kafka.publish(event);       // step 2
```

What if step 1 succeeds but step 2 fails? The booking is saved in the DB but no confirmation email goes out, no inventory is updated, no analytics recorded. A silent failure that the user never knows about.

What if you flip the order — publish to Kafka first, then save?

```java
kafka.publish(event);       // step 1
db.save(booking);           // step 2
```

Kafka succeeds, DB crashes. You sent a confirmation email for a booking that doesn't exist in your database.

> [!danger] There is no safe order when writing to two separate systems
> This is the same dual write problem, just with Kafka instead of Elasticsearch. No ordering saves you — the problem is that two separate systems are involved.

---

## The fix — write the event into the same database transaction

The Outbox Pattern eliminates the second external system entirely. Instead of publishing to Kafka directly from your app, you write the event into a special table in the **same database** — the **outbox table** — in the same transaction as your actual data.

```sql
BEGIN TRANSACTION;
    INSERT INTO bookings (id, hotel, status) VALUES (1, 'Marriott', 'confirmed');
    INSERT INTO outbox (event_type, payload) VALUES ('booking_confirmed', '{"booking_id": 1, ...}');
COMMIT;
```

Either both rows are inserted or neither is. That is the guarantee of a single database transaction — atomicity. You never touch two systems.

```
bookings table:  { id: 1, hotel: "Marriott", status: "confirmed" }
outbox table:    { id: 1, event: "booking_confirmed", payload: {...}, status: "pending" }
```

Now CDC is watching the outbox table. The moment that new row appears in the WAL, Debezium picks it up and publishes it to Kafka.

```
Outbox table row inserted
    → CDC reads WAL
    → Debezium publishes to Kafka
    → email service receives event
    → inventory service receives event
    → analytics service receives event
```

---

## What happens after CDC picks up the event?

The outbox table is a staging area, not permanent storage. Once CDC successfully reads and publishes an event, the row is either marked as processed or deleted. The table stays small.

```
outbox table:
    id=1  status=processed  ← CDC picked this up, safe to delete
    id=2  status=pending     ← CDC hasn't picked this up yet
```

If CDC goes down temporarily, it picks up from where it left off when it recovers — the pending rows are still sitting in the outbox table waiting. Nothing is lost.

---

## The full picture

```
App code:
    BEGIN TRANSACTION
        → INSERT into bookings        ← actual data
        → INSERT into outbox table    ← event to be sent
    COMMIT

CDC (async, milliseconds later):
    → reads outbox row from WAL
    → publishes to Kafka
    → marks outbox row as processed

Kafka consumers:
    → email service sends confirmation
    → inventory service decrements room count
    → analytics service records the booking
```

Your application only ever writes to one system — your own database. Kafka gets the event guaranteed, in order, with no dual write risk.

> [!important] The Outbox Pattern is CDC's best friend
> CDC alone tells you how to stream changes out of a database. The Outbox Pattern tells you how to safely get events into that stream in the first place. Together they solve the dual write problem end to end.

---

## Why this is better than alternatives

| Approach | Risk |
|---|---|
| App writes to DB then publishes to Kafka | Kafka publish can fail silently |
| App publishes to Kafka then writes to DB | DB write can fail, event already sent |
| Two-phase commit across DB + Kafka | Complex, slow, Kafka doesn't support XA transactions |
| **Outbox Pattern** | **Single DB transaction — atomic by definition** |
