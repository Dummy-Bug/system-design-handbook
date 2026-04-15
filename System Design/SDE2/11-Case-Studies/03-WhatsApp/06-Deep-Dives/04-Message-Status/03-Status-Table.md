
> [!info] The message_status table — tracking tick boundaries per user per conversation
> Two integers per conversation per user. Everything else is derived.

---

## Schema

```
message_status table (DynamoDB)
───────────────────────────────────────────────────────────
PK: user_id          (who we're tracking status for)
SK: conversation_id  (which conversation)
last_delivered_seq   (double tick boundary)
last_read_seq        (blue tick boundary)
```

Example rows for Bob across multiple conversations:

```
user_id    conversation_id    last_delivered_seq    last_read_seq
bob        conv_abc123        44                    42
bob        conv_def456        17                    17
bob        conv_ghi789        8                     8
```

Reading this:
- In conv_abc123, Bob has received messages up to seq=44, but only read up to seq=42. Messages 43 and 44 are delivered but unread (double tick, not blue).
- In conv_def456 and conv_ghi789, Bob has both received and read everything up to the latest seq.

---

## Separation of concerns — two tables, two responsibilities

This table is separate from `pending_deliveries`. They solve different problems:

```
pending_deliveries    → "what messages does Bob still need to receive?"
                        used when Bob reconnects after being offline
                        PK=receiver_id, SK=conversation_id, first_undelivered_seq

message_status        → "what is the tick state of Alice's sent messages?"
                        used to show ticks on Alice's side
                        PK=user_id, SK=conversation_id, last_delivered_seq, last_read_seq
```

`pending_deliveries` is Bob's inbox state — what he hasn't received yet.
`message_status` is Alice's display state — what tick to show on her messages.

Mixing these two would couple delivery tracking with UI rendering. Keep them separate.

---

## Deriving tick state from the boundaries

Given these two numbers, the tick state of any message Alice sent is:

```python
def tick_state(seq, last_delivered_seq, last_read_seq):
    if seq <= last_read_seq:
        return BLUE_TICK
    elif seq <= last_delivered_seq:
        return DOUBLE_TICK
    else:
        return SINGLE_TICK
```

Alice's client receives the two numbers once and applies this logic locally. No per-message queries. No per-message status columns.

---

## Writes to this table

Three events trigger writes:

**1. Message delivered to Bob's device (double tick)**
```
Bob's client acks seq=44 over WebSocket
→ server: UPDATE message_status
    SET last_delivered_seq = 44
    WHERE user_id=bob AND conversation_id=conv_abc123
```

**2. Bob opens the chat (blue tick)**
```
Bob opens conv_abc123
→ Bob's client sends: "read up to seq=44"
→ server: UPDATE message_status
    SET last_read_seq = 44
    WHERE user_id=bob AND conversation_id=conv_abc123
```

**3. Bob replies (implicit read)**
```
Bob sends a message in conv_abc123
→ all of Alice's previous messages are implicitly read
→ server: UPDATE message_status
    SET last_read_seq = latest_seq_before_bob_reply
    WHERE user_id=bob AND conversation_id=conv_abc123
```

All three are single-row updates. One write per event, regardless of how many messages are in the conversation.

---

## Initial row creation

When Alice sends the first message in a conversation and Bob is offline, there is no row in message_status yet. The row is created on first delivery ack or first read event — whichever comes first.

> [!tip] Interview framing
> "Instead of a status column per message, we track two sequence number boundaries per user per conversation — last_delivered_seq and last_read_seq. Tick state for any message is derived from these two numbers at render time. Every status event is a single row update, not a bulk operation."
