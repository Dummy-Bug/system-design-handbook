# Redis Streams

> [!info] Redis Stream is an append-only log with consumer groups and acknowledgements. It solves the core problem that makes a Redis List unsafe as a message queue — messages disappearing permanently when a worker crashes.

---

## The problem with List as a queue

A Redis List seems like a natural queue — push to one end, pop from the other. But `LPOP` is permanent:

```
Worker picks up message → LPOP removes it from List forever
Worker crashes mid-processing → message is gone, no retry possible ✗
```

There is no concept of "I'm currently processing this — hold it for me, but don't delete it yet." Pop means delete. If anything goes wrong after the pop, the message is lost.

---

## What Streams add — the acknowledgement model

A Stream never deletes a message when a worker reads it. The message stays until the worker explicitly acknowledges it:

```
Worker reads message  → message STAYS in the stream (not deleted)
Worker finishes       → sends XACK → message marked as done ✓
Worker crashes        → no XACK sent → message stays as "pending"
                      → another worker picks it up and retries ✓
```

Think of it like a receipt — you sign the receipt only after you've actually processed the item. Until you sign, the stream assumes you might still fail.

---

## Consumer Groups — work distribution

Consumer groups let multiple workers share the work of consuming a stream, with each message going to exactly one worker automatically.

```
Stream: [msg1, msg2, msg3, msg4, msg5, msg6]

Consumer Group "workers":
  Worker A → receives msg1, msg4
  Worker B → receives msg2, msg5
  Worker C → receives msg3, msg6

Each message delivered to exactly one worker ✓
No app-level coordination needed ✓
```

Without consumer groups, you'd have to write your own locking logic to prevent two workers processing the same message. Consumer groups handle this at the Redis level.

---

## List vs Stream — side by side

```
Redis List:
  LPOP → message removed permanently
  Worker crashes → message gone forever
  Multiple workers → must coordinate manually to avoid duplicate processing
  Use for: simple task queues where losing a task is acceptable

Redis Stream:
  XREAD → message stays in stream until XACK
  Worker crashes → message stays pending, retried automatically
  Consumer groups → each message to exactly one worker, no coordination needed
  Use for: reliable event processing where every message must be handled
```

---

## Key commands

```
XADD stream * field value     → append message to stream (* = auto-generate ID)
XREAD COUNT 10 STREAMS stream → read up to 10 messages
XACK stream group message-id  → acknowledge a message as processed
XPENDING stream group         → list messages that were read but not yet ACKed
```

---

## Where Redis Streams fit in system design

Redis Stream is a lightweight alternative to Kafka for simpler use cases:

```
Redis Stream  → simple, low-volume event processing, already using Redis
               no separate infrastructure, millisecond latency
               limited retention, no replay of old messages by default

Kafka         → high-volume, long retention, replay from any offset
               more operationally complex, separate cluster needed
```

> [!tip] Interview framing
> "For lightweight async processing where we're already using Redis, I'd use a Redis Stream with consumer groups — each message is acknowledged after processing so worker crashes don't lose events. For higher volume or long-term retention needs, I'd reach for Kafka instead."
