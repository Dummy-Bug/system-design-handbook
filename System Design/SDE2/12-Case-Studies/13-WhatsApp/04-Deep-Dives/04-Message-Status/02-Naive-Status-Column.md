
> [!info] The first instinct — a status column on the message row
> Seems natural. Falls apart at scale the moment you think about bulk updates.

---

## The naive approach

The first instinct is to add a `status` column directly to the messages table:

```
messages table
──────────────────────────────────────────────────
PK             SK      content    sender   status
conv_abc123    42      "hey"      alice    SENT
conv_abc123    43      "where?"   alice    SENT
conv_abc123    44      "hello??"  alice    SENT
```

When Bob receives seq=42, update the row: `status = DELIVERED`.
When Bob reads the chat, update all visible rows: `status = READ`.

Clean, simple. Each message carries its own state.

---

## Where it breaks — bulk updates on read

Bob goes on a 2-week vacation. Alice sends 50 messages. Bob comes back, opens the chat.

The moment Bob opens the chat, every one of those 50 messages transitions from DELIVERED to READ. With a status column on the message row, that's **50 individual DynamoDB writes** — one per message row.

```
Bob opens chat
→ update seq=42 status=READ
→ update seq=43 status=READ
→ update seq=44 status=READ
... (50 times)
```

At WhatsApp scale, millions of users are opening chats every second. Each open triggers a batch of writes proportional to the number of unread messages. This is expensive, unpredictable in cost, and completely unnecessary.

---

## The deeper problem — what are you actually storing?

Look at what those 50 rows encode:

```
seq=42  READ
seq=43  READ
seq=44  READ
...
seq=91  READ
```

Every single row says the same thing. The only information you actually need is:

**"Bob has read up to seq=91 in this conversation."**

One integer. That's it. Fifty rows of `READ` can be replaced with a single number.

---

## The right model — seq numbers as state boundaries

Instead of storing status per message, store the boundary:

```
message_status table
───────────────────────────────────────────────────────────
user_id    conversation_id    last_delivered_seq    last_read_seq
bob        conv_abc123        91                    91
```

Now the tick state of any message is derived, not stored:

```
seq <= last_read_seq       → blue tick
seq <= last_delivered_seq  → double tick
seq > last_delivered_seq   → single tick
```

Bob opens the chat and reads 50 messages? One write: update `last_read_seq = 91`. Not 50 writes. One.

> [!important] Key insight
> Status is a range property, not a per-message property. Every message up to a point is read. Every message up to another point is delivered. Store the boundaries, derive the states.

---

## Why the status column pattern is still tempting

In a small system with a few hundred users, the status column works fine. The bulk update cost is invisible. This is exactly why it's a trap in a system design interview — it looks reasonable at small scale and only reveals its cost when you reason about WhatsApp's actual load.

The interviewer is watching for whether you catch this yourself or need to be pushed on it.
