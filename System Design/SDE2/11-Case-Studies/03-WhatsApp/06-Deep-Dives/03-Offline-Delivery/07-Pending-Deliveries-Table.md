
> [!info] A DynamoDB table that tracks exactly which conversations have undelivered messages for each offline user
> Durable by default, queryable by receiver_id, stores only what's needed — one row per pending conversation.

---

## The table design

```
Table: pending_deliveries

PK: receiver_id          → bob
SK: conversation_id      → conv_abc123
Attribute: first_undelivered_seq → 42
```

One row per (user, conversation) pair that has undelivered messages. That's it.

---

## Why this design works

**Durable:** DynamoDB replicates across 3 availability zones. No AOF sync windows, no restart concerns. A write to pending_deliveries is safe the moment it returns success.

**Queryable by receiver:** `PK=bob` returns all conversations with pending messages for Bob in a single range scan. No scanning other users' data.

**Lightweight:** One row per conversation, not one row per message. Bob could have 50 undelivered messages from Alice and it's still just one row:

```
{ receiver_id: bob, conversation_id: conv_abc123, first_undelivered_seq: 42 }
```

On reconnect, `SK > 41` on the messages table returns all 50. The pending_deliveries table never grows with message volume — only with conversation count.

---

## Write flow — when a message arrives for an offline user

```
Alice sends seq=42, Bob is offline:
  → Check pending_deliveries: GET {bob, conv_abc123}
  → No entry exists
  → Write: { receiver_id: bob, conversation_id: conv_abc123, first_undelivered_seq: 42 }

Alice sends seq=43, Bob still offline:
  → Check pending_deliveries: GET {bob, conv_abc123}
  → Entry already exists with first_undelivered_seq=42
  → Do nothing — seq=43 will be fetched automatically when server queries SK > 41
```

The entry is written only once per conversation per offline session. Subsequent messages to the same conversation don't update it — the DynamoDB range query `SK > first_undelivered_seq` naturally catches everything.

---

## Why first_undelivered_seq and not last_undelivered_seq

The server stores the **first** message Bob missed, not the last. On reconnect:

```
Query: PK=conv_abc123, SK >= first_undelivered_seq
```

This returns everything from that point forward — including messages that arrived after the entry was written. No need to update the entry every time a new message arrives. The DynamoDB query dynamically catches up to the current state of the conversation.

---

## Cleanup after delivery

Once Bob reconnects and all pending messages are delivered:

```
→ Delete entry from pending_deliveries: {bob, conv_abc123}
→ Update last_delivered_seq tracker to the latest seq delivered
```

The table stays lean — entries only exist for users who are currently offline with pending messages.
