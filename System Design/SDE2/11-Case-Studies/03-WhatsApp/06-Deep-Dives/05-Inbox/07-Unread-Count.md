
> [!info] Unread count — increment on offline delivery, reset on read receipt
> The app server already knows Alice's online state when a message arrives. That same check drives the unread count.

---

## Where unread count lives

The `unread_count` is an attribute on the conversations table row:

```
conversations table:
  (alice, conv_bob) → { last_ts, last_message, unread_count: 3 }
```

It lives here because it's per-user per-conversation — Alice's unread count for Bob's chat is independent of Bob's unread count for Alice's chat.

---

## When to increment

The naive approach — increment on every message — wastes write cycles. If Alice has Bob's chat open, she sees the message instantly. Her client sends a read receipt immediately. The counter goes to 1 and back to 0 in milliseconds — two unnecessary writes for a message that was never actually unread.

The right trigger is: increment only when Alice cannot see the message right now.

The app server already knows this. When a message arrives for Alice, it checks Redis to decide whether to deliver or queue:

```
Message arrives for Alice
→ check Redis: is ws:alice present?

YES (Alice is online)
→ deliver over WebSocket directly
→ skip increment — Alice will see it immediately

NO (Alice is offline)
→ queue in pending_deliveries table
→ UPDATE conversations[alice][conv_bob] SET unread_count = unread_count + 1
```

The Redis check was already happening for delivery routing. The unread count increment piggybacks on the same check — no extra work.

---

## When to reset

Alice opens Bob's chat. Her client sends a read receipt event with the last seq she read — the same event that drives the blue tick flow.

The app server receives this event and resets the counter:

```
Alice opens conv_bob
→ client sends: { type: read_receipt, conv_id: conv_bob, last_read_seq: 47 }
→ app server: UPDATE conversations[alice][conv_bob] SET unread_count = 0
→ app server: UPDATE message_status SET last_read_seq = 47 (blue tick flow)
```

One event, two writes — unread count reset and blue tick update both happen from the same read receipt.

---

## The full lifecycle

```
Bob sends message → Alice offline
→ Redis check: ws:alice absent
→ queue message + unread_count + 1 (now 1)

Bob sends another message → Alice still offline
→ Redis check: ws:alice absent
→ queue message + unread_count + 1 (now 2)

Bob sends another message → Alice still offline
→ unread_count + 1 (now 3)

Alice opens WhatsApp → inbox shows [3] badge on Bob's chat

Alice taps Bob's chat → read receipt sent
→ app server: unread_count = 0
→ badge disappears
```

No counting queries. No scanning pending_deliveries. Just a single atomic increment on each offline message and a reset on read.

> [!tip] Interview framing
> "Unread count is an attribute on the conversations row. It increments by 1 when a message is queued for an offline user — the app server already checks Redis for Alice's WebSocket status to route delivery, so the increment piggybacks on that same check at zero extra cost. It resets to 0 when Alice opens the chat and her client sends a read receipt event."
