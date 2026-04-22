
> [!info] Status updates while Alice is offline — catching up when she reconnects
> Bob reads Alice's messages while Alice is offline. How does Alice's client catch up the moment she comes back?

---

## The problem

Alice sent messages to Bob. Then Alice went offline — closed WhatsApp, phone in her bag.

While Alice is offline, Bob:
1. Receives the messages (double tick event ready to send)
2. Opens the chat (blue tick event ready to send)

Both status events are ready. But Alice is offline. There's no WebSocket to push them to.

What happens to those events? How does Alice see the correct tick state when she comes back?

---

## What the server stores

The server doesn't queue individual status events for Alice. It doesn't maintain a list of "pending tick updates to push when Alice reconnects."

Instead, it just updates `message_status` with the latest seq numbers:

```
Bob receives seq=44 → UPDATE last_delivered_seq=44 WHERE user_id=bob, conv=conv_abc123
Bob reads seq=44   → UPDATE last_read_seq=44 WHERE user_id=bob, conv=conv_abc123
```

The table always reflects the current truth. No event queue. No backlog. Just two integers that represent the current state.

---

## When Alice reconnects

Alice opens WhatsApp. WebSocket established. WS server registers her in Redis.

Now the WS server needs to tell Alice's client what tick state to display for her sent messages. It queries `message_status` for all conversations Alice is active in:

```
SELECT * FROM message_status
WHERE user_id=bob AND conversation_id IN (alice's active conversations)
```

Returns:
```
{ conversation_id: conv_abc123, last_delivered_seq: 44, last_read_seq: 44 }
```

Server pushes one event to Alice's client per conversation:

```
{
  type: "status_update",
  conversation_id: "conv_abc123",
  last_delivered_seq: 44,
  last_read_seq: 44
}
```

---

## Alice's client renders the three ranges

Alice's client receives the two numbers and applies the tick logic:

```
last_read_seq = 44
last_delivered_seq = 44

For each message Alice sent:
  seq <= 44 (last_read_seq)      → blue tick ✓✓
  seq <= 44 (last_delivered_seq) → (same in this case, all blue)
  seq > 44                        → single tick ✓ (not yet delivered)
```

If Bob had received but not read:

```
last_delivered_seq = 44
last_read_seq = 41

seq <= 41  → blue tick ✓✓ (blue)
42 to 44   → double tick ✓✓ (grey)
seq > 44   → single tick ✓
```

Alice's client receives two numbers. From those two numbers, it determines the correct tick for every single message in the conversation, without any per-message queries.

---

## Why one event is enough

The key insight is that status is always cumulative. If Bob has read up to seq=44, he has necessarily read seq=42 and seq=43 as well. There's no case where seq=43 is unread but seq=44 is read — messages are read in order.

This means the entire tick state of a conversation can always be described by two integers. The server never needs to send more than two numbers to fully describe the current state.

```
Instead of:                         You send:
  "seq=42 is blue tick"             last_read_seq: 44
  "seq=43 is blue tick"             last_delivered_seq: 44
  "seq=44 is blue tick"
  "seq=45 is double tick"
  "seq=46 is single tick"
```

Five events compressed to one. At WhatsApp scale — millions of users reconnecting every hour — this matters enormously.

---

## What if multiple conversations have pending status updates

Alice was in 5 active conversations while offline. In each one, the other person may have received or read messages.

When Alice reconnects, the server queries `message_status` for all 5 conversations and pushes 5 status update events — one per conversation. Each carries two seq numbers. Alice's client updates tick display for all 5 conversations simultaneously.

```
Server pushes on Alice's reconnect:
  [conv_abc123] last_delivered=44, last_read=44
  [conv_def456] last_delivered=12, last_read=9
  [conv_ghi789] last_delivered=31, last_read=31
  [conv_jkl012] last_delivered=7,  last_read=7
  [conv_mno345] last_delivered=19, last_read=15
```

Five events. Complete tick state for all conversations. Alice's inbox shows correct tick indicators everywhere — instantly, on reconnect.

> [!tip] Interview framing
> "When Alice reconnects, we don't replay a queue of status events. We query message_status for her active conversations, get the latest last_delivered_seq and last_read_seq per conversation, and push one event per conversation. Her client derives the tick state for all messages from those two numbers. Two integers fully describe the tick state of an entire conversation — because status is always cumulative."
