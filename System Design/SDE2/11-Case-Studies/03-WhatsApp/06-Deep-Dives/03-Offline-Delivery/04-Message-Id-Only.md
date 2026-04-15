
> [!info] Store only message_ids instead of full messages — lighter, but durability concern remains
> If storing full messages in Redis is wasteful, store just enough to find them later.

---

## The improvement

Instead of storing full message content in the mailbox, store only the identifiers:

```
RPUSH mailbox:bob → { conversation_id: conv_abc123, message_id: msg_xyz }
RPUSH mailbox:bob → { conversation_id: conv_abc123, message_id: msg_abc }
```

When Bob reconnects:

```
LRANGE mailbox:bob → [ {conv_abc123, msg_xyz}, {conv_abc123, msg_abc} ]
→ fetch full messages from DynamoDB by message_id
→ push to Bob over WebSocket
→ delete mailbox:bob
```

Memory footprint drops dramatically. A message_id is ~16 bytes vs ~250 bytes for the full message. 15× less Redis memory.

---

## Why durability is still a concern

The mailbox is still in Redis. Bob goes offline for 3 days. Redis restarts twice during that time. Even with AOF, there is a small window where a write to Redis completes but the AOF sync hasn't flushed yet.

More importantly: the mailbox has become the **source of truth** for what Bob hasn't received. If any entry is lost, Bob permanently misses that message — because the server has no other record of "this message needs to be delivered to Bob."

The message itself is safe in DynamoDB. But the pointer saying "Bob hasn't seen this" only exists in Redis. Losing the pointer is as bad as losing the message.

---

## The deeper insight

Storing message_ids is better than storing full messages, but the fundamental problem remains: Redis is not the right store for data this critical.

What you actually need is:
- **Durable** — survives restarts without any loss window
- **Queryable by receiver** — on reconnect, get all pending conversations for Bob instantly
- **Lightweight** — don't store what you already have in DynamoDB

