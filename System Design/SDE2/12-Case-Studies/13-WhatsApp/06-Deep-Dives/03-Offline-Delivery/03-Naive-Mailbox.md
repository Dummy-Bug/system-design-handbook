
> [!info] The first instinct — store undelivered messages in a Redis mailbox
> If Bob is offline, hold his messages somewhere until he reconnects. Redis is already in the system. Why not use it?

---

## The naive approach

When the server detects Bob is offline, instead of dropping the message, it queues it in Redis:

```
RPUSH mailbox:bob → { conversation_id: conv_abc123, content: "hey", seq: 42, ... }
RPUSH mailbox:bob → { conversation_id: conv_abc123, content: "where are you?", seq: 43, ... }
```

When Bob reconnects, drain the mailbox:

```
LRANGE mailbox:bob → get all queued messages
→ push them to Bob over WebSocket
→ delete mailbox:bob
```

Simple. No new components. Reuses existing Redis.

---

## Why it fails — problem 1: memory

Redis is an in-memory store. Every byte in a Redis mailbox costs RAM. At WhatsApp scale:

```
100M DAU
Each offline user accumulates messages while away
Average offline duration: several hours
Messages per hour per active conversation: ~10-20

If even 10% of DAU goes offline with pending messages:
  10M users × 10 messages × 250 bytes = 25 GB just for one hour of offline messages
```

Redis is not designed to be a durable message store for millions of users. This blows up memory fast.

---

## Why it fails — problem 2: durability

Bob goes offline Friday evening. Redis restarts Saturday morning — a routine deploy, or a crash. AOF helps recover most data, but this mailbox is the **only record** of messages Bob hasn't received yet.

```
Bob's mailbox before restart:
  seq=42 "hey"
  seq=43 "where are you?"

Redis restarts → AOF replays → mailbox restored

BUT: what if AOF sync was slightly behind? 
     seq=43 is lost. Bob never receives it.
```

For a messaging app, losing a message silently is a critical failure. The mailbox is too important to trust to an in-memory store.

---

## The root cause

The naive mailbox stores **full message content** in Redis. But the full messages are already safely stored in DynamoDB. Duplicating them into Redis adds memory cost and durability risk with no real benefit.

The right question isn't "where do I store the messages" — it's "what's the minimum information I need to find them later?"
