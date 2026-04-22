
> [!info] Redis INCR is the implementation — atomic, fast, and race-condition-safe
> The per-conversation counter needs to be atomic. Two WebSocket servers processing messages simultaneously must never get the same sequence number for the same conversation.

---

## Why atomicity matters

We have multiple WebSocket servers. Alice is on WS-Server-1. Bob is on WS-Server-2. Alice and Bob both send a message at the exact same millisecond.

```
WS-Server-1 processes Alice's message simultaneously with
WS-Server-2 processes Bob's message
```

Both servers need to increment the counter for `conv_abc123` and get a unique number. If the increment is not atomic, this happens:

```
WS-Server-1 reads counter → 5
WS-Server-2 reads counter → 5   (before Server-1 wrote back)
WS-Server-1 writes 6
WS-Server-2 writes 6

Result: Alice gets seq=6, Bob gets seq=6 → collision
```

Two messages with the same sequence number. The client cannot order them. The deli counter just gave the same ticket to two people.

---

## Redis INCR — atomic by design

Redis is single-threaded for command execution. Every command executes fully before the next one starts. `INCR` reads the current value, increments it, and writes the new value — all as one indivisible operation. No other command can interleave.

```
Redis key: seq:conv_abc123

WS-Server-1: INCR seq:conv_abc123 → returns 6  (atomic)
WS-Server-2: INCR seq:conv_abc123 → returns 7  (atomic, queued behind Server-1)
```

Even if both servers call `INCR` at the exact same microsecond, Redis queues the commands and executes them one at a time. Server-1 gets 6, Server-2 gets 7. No collision. No race condition.

---

## The full sequence assignment flow

```
1. Alice hits send on "hey"
2. WS-Server-1 receives the message
3. WS-Server-1 calls: INCR seq:conv_abc123 → gets seq=42
4. WS-Server-1 writes to DynamoDB:
     PK=conv_abc123, SK=42, content="hey", sender=alice, timestamp=4:20 (client's clock)
5. WS-Server-1 delivers "hey" to Bob's WebSocket with seq=42
6. Bob's client stores message at position 42 in the conversation
```

Simultaneously:

```
1. Bob hits send on "hi" (same millisecond)
2. WS-Server-2 receives the message
3. WS-Server-2 calls: INCR seq:conv_abc123 → gets seq=43 (queued after Alice's INCR)
4. WS-Server-2 writes to DynamoDB:
     PK=conv_abc123, SK=43, content="hi", sender=bob, timestamp=4:10 (Bob's drifted clock)
5. WS-Server-2 delivers "hi" to Alice's WebSocket with seq=43
6. Alice's client stores message at position 43 in the conversation
```

Both clients see:
```
seq=42  Alice: "hey"
seq=43  Bob:   "hi"
```

Correct order. Despite Bob's clock being 10 minutes behind. Despite two different servers processing simultaneously. Despite the messages arriving at nearly the same instant.

---

## Redis persistence for sequence counters

The sequence counter must survive a Redis restart. If Redis loses the counter, the next message would start from seq=0 again — colliding with messages already stored in DynamoDB.

Use AOF (Append-Only File) persistence on Redis, the same as the connection registry. Every INCR is written to disk before the response is returned. On restart, Redis replays the AOF log and restores the counter to its last value.

> [!tip] Interview framing
> "I'd store the per-conversation sequence counter in Redis using INCR. Redis is single-threaded so INCR is atomic — two WebSocket servers can't get the same seq for the same conversation. With AOF persistence, the counter survives restarts. No collisions, no race conditions."
