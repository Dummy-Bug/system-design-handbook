
> [!info] The WebSocket delivery ack — how the server knows Bob received the message
> Bob's client doesn't ack every message individually. It sends one cumulative ack: "delivered up to seq N."

---

## The question the design leaves open

We said: Bob's client receives messages over WebSocket and sends a delivery ack back. But what exactly does that ack look like?

Two options:
1. Per-message ack — one ack per message received
2. Cumulative ack — one ack covering all messages up to a seq number

---

## Why per-message ack is wasteful

Bob comes back online after 3 days. Alice sent 50 messages. The WS server pushes all 50 over WebSocket.

With per-message acks:

```
Bob's client → server: "delivered seq=42"
Bob's client → server: "delivered seq=43"
Bob's client → server: "delivered seq=44"
... (50 times)
```

50 ack messages. 50 server-side `message_status` writes. For a batch delivery of 50 messages this is completely wasteful — every ack says the same thing except for the sequence number.

---

## Cumulative ack — one message, full coverage

Bob's client receives the full batch of 50 messages. Once rendered, it sends one ack:

```
Bob's client → server: {
  type: "delivered",
  conversation_id: "conv_abc123",
  seq: 91         ← the highest seq received
}
```

Server processes this as: "Bob has received everything up to seq=91 in conv_abc123."

```
UPDATE message_status
  SET last_delivered_seq = 91
  WHERE user_id=bob AND conversation_id=conv_abc123
```

One ack. One write. Full coverage.

---

## Why this works — the seq number is monotonically increasing

Sequence numbers only go up. If Bob has received seq=91, he has necessarily received seq=42 through seq=90 as well (they were all delivered in the same batch, in order). The highest seq in the batch is sufficient to represent delivery of the entire batch.

```
Messages pushed to Bob: seq 42, 43, 44, ... 91
Bob's client renders all of them
Bob's client acks: seq=91
Server knows: Bob has seq 42 through 91 ✓
```

---

## What if messages arrive out of order over WebSocket

In rare cases — network hiccups, reconnects — messages might arrive slightly out of order on the client. Bob's client buffers messages and only sends the cumulative ack once it has a contiguous sequence up to N. It does not ack seq=91 if seq=89 is missing.

```
Bob's client receives: 42, 43, 45  (44 missing)
→ holds 45, does not ack past 43 yet
→ 44 arrives (retransmit or reorder resolves)
→ now has 42, 43, 44, 45 contiguous
→ acks seq=45
```

This mirrors TCP's cumulative acknowledgement model — the receiver only acks up to the last contiguous byte received.

---

## The ack triggers the double tick on Alice's side

Once the server updates `last_delivered_seq`, it checks if Alice is online:

```
Server receives Bob's ack: last_delivered_seq=91 for conv_abc123
→ UPDATE message_status SET last_delivered_seq=91 WHERE user_id=bob, conversation_id=conv_abc123
→ GET ws:alice from Redis registry
→ Alice is online on ws_server_2
→ Push event to Alice's client:
   { type: "status_update", conversation_id: conv_abc123, last_delivered_seq: 91 }
→ Alice's client: show double tick ✓✓ for all messages up to seq=91
```

If Alice is offline, this event is held and sent when she reconnects — covered in the offline status sync file.

> [!tip] Interview framing
> "Bob's client sends a cumulative delivery ack — one message with the highest seq received. Not one ack per message. The server updates last_delivered_seq in a single write and pushes the double tick event to Alice if she's online."
