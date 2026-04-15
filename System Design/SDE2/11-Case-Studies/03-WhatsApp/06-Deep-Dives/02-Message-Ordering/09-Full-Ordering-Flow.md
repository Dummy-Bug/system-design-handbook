
> [!info] End to end — how message ordering works in the final design
> Putting all the pieces together: client sends, server assigns seq, DynamoDB stores, client displays in seq order.

---

## The complete flow

```
Alice sends "hey":
  1. Alice's client sends message over WebSocket
     payload: { content: "hey", client_timestamp: "4:20:00", message_id: "msg_aaa" }

  2. WS-Server-1 receives the message
     → calls INCR seq:conv_abc123 on Redis
     → gets seq=42

  3. WS-Server-1 writes to DynamoDB:
     PK=conv_abc123, SK=42
     content="hey", sender=alice, receiver=bob
     message_id=msg_aaa, timestamp=4:20:00, s3_ref=null

  4. WS-Server-1 delivers to Bob:
     → looks up Bob's ws_server_id in Redis registry
     → forwards to Bob's WS server
     → Bob's WS server pushes to Bob's WebSocket:
       { seq: 42, content: "hey", sender: alice, timestamp: "4:20:00" }

  5. Bob's client:
     → stores message at seq=42
     → renders in conversation sorted by seq
```

---

## What the client holds and how it renders

Bob's client maintains a local sorted list of messages by `seq`:

```
seq=40  Alice: "how was your day"   4:19:55
seq=41  Bob:   "pretty good"        4:19:58
seq=42  Alice: "hey"                4:20:00
```

When a new message arrives, the client inserts it at the correct `seq` position. If messages arrive out of order over the network (seq=44 before seq=43), the client holds seq=44 in a buffer and waits briefly for seq=43 before rendering.

---

## Network reordering with seq numbers

The original problem was network reordering — packets arriving out of order. With seq numbers, the client handles this cleanly:

```
Arrives first:  seq=44 "hello??"    → buffer it, waiting for seq=43
Arrives second: seq=43 "you there"  → now have 43 and 44, render both in order
Arrives third:  seq=42 "hey"        → have 42, 43, 44, render all three in order
```

The seq number is the anchor. Regardless of network arrival order, the client always renders in seq order.

---

## Summary — what each component does

```
Client timestamp  → display only ("4:20 PM" shown under the message)
                    client fills this, server stores it as-is

seq_no            → ordering only (what position this message occupies in conversation)
                    server assigns via Redis INCR, stored as DynamoDB sort key

DynamoDB SK       → seq_no (sorted within partition, enables range reads for history)

Client rendering  → sort by seq_no, display client_timestamp
```

These three concerns — display time, ordering, storage — are fully decoupled. Each is solved by the right tool for the job.
