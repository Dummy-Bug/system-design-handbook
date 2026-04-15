
> [!info] The sequence number changes the DynamoDB schema — the sort key needs to change
> The original schema used timestamp#message_id as the sort key. Now that seq_no is the ordering mechanism, the sort key should reflect that.

---

## Original schema (before ordering deep dive)

```
Table: messages

PK: conversation_id
SK: timestamp#message_id    ← composite, collision-safe, chronologically ordered

Attributes:
  message_id, sender_id, receiver_id, content, s3_ref
```

The composite sort key was designed to:
1. Keep messages in chronological order (timestamp first)
2. Prevent collisions when two messages arrive at the same millisecond (message_id as tiebreaker)

Both of these problems are now solved better by `seq_no`.

---

## Updated schema

```
Table: messages

PK: conversation_id
SK: seq_no                  ← globally ordered, collision-free, assigned by Redis INCR

Attributes:
  message_id      → unique ID (client-generated UUID or Snowflake)
  sender_id       → who sent the message
  receiver_id     → denormalized, avoids lookup to conversations table
  content         → message text
  timestamp       → client's local clock at send time, stored as attribute (display only)
  s3_ref          → nullable, pointer to S3 if message archived to cold storage
```

---

## Why seq_no is strictly better as the sort key

**Collision safety:**
`timestamp#message_id` needed the message_id suffix specifically because two messages could arrive at the same millisecond and collide on timestamp alone. `seq_no` is inherently unique — the Redis INCR guarantees no two messages in the same conversation ever get the same number.

**Ordering correctness:**
`timestamp#message_id` sorted by time, but time is unreliable across servers (NTP drift) and across clients (clock skew). `seq_no` sorts by logical sequence — the order in which the server processed the messages. Unaffected by any clock.

**Simplicity:**
A single integer is simpler than a composite string. Range queries on `SK BETWEEN 1 AND 100` are cleaner than parsing `timestamp#message_id` strings.

---

## What happens to timestamp

Timestamp is not dropped — it becomes a regular attribute. It serves one purpose only: display.

```
Before archival:
  SK:        42
  timestamp: "4:20:00"    ← stored as attribute, shown in UI as "4:20 PM"
  content:   "hey"
  s3_ref:    null

After archival (90+ days old):
  SK:        42
  timestamp: "4:20:00"    ← still there, display still works
  content:   null
  s3_ref:    "s3://whatsapp-archive/conv_abc123/msg_aaa.json"
```

The timestamp persists through archival. Even for messages from 5 years ago, the "4:20 PM" display still works correctly when the message is fetched from S3.

---

## Updated chat history query

```
PK = conv_abc123
SK < current_seq           (everything before the current cursor)
LIMIT 20
SCAN_INDEX_FORWARD = false (highest seq first = most recent first)
```

Cursor for pagination: the `seq_no` of the oldest message in the current batch. Pass it as `before_seq` in the next request.

```
First load:   PK=conv_abc123, SK < ∞,   LIMIT 20 → returns seq 480–500
Next page:    PK=conv_abc123, SK < 480, LIMIT 20 → returns seq 460–479
Next page:    PK=conv_abc123, SK < 460, LIMIT 20 → returns seq 440–459
```

Clean, stable, no pagination drift.

> [!tip] Interview framing
> "I'd change the sort key from timestamp#message_id to seq_no. The composite timestamp was a workaround for two problems — collision safety and ordering — that seq_no solves more cleanly. Timestamp stays as a display attribute so the UI can still show '4:20 PM' under each message."
