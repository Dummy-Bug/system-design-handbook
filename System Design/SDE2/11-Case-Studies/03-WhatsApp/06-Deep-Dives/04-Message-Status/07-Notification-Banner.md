
> [!info] Reading from the notification banner does not trigger a blue tick
> The app must be open and the chat must be visible. Lock screen reads are invisible to the system.

---

## The scenario

Bob's phone gets a notification: "Alice: hello??"

Bob is at a meeting. He glances at his phone, reads the message from the lock screen notification banner, and puts the phone back down. He does not tap the notification. WhatsApp never opens.

Does Alice get a blue tick?

**No.**

---

## Why not — the app never ran

Blue tick is fired by Bob's WhatsApp client. Specifically, by the event sent when Bob opens a chat screen:

```
Bob's client → WS server: { type: "read", conversation_id: ..., seq: ... }
```

For this event to fire:
1. WhatsApp must be running (foreground or recently opened)
2. Bob must have navigated to that specific conversation
3. The chat screen must have rendered

When Bob reads from the notification banner, none of these happen. The OS shows him the notification text. WhatsApp is never launched. No read event is ever sent. The server has no signal that Bob saw anything.

---

## What the server knows at this point

```
Alice sent seq=44 "hello??"
Bob's phone received the notification via APNs
Bob read it from the lock screen

Server's view:
  last_delivered_seq = 44   (Bob received messages via WebSocket earlier — or still single tick if offline)
  last_read_seq = 41        (last time Bob actually opened the chat)
```

From Alice's perspective: double tick, maybe single tick. No blue.

---

## This is intentional product design

WhatsApp's definition of "read" is deliberately conservative: **the chat was open, the messages were on screen.** Not "the notification was seen." Not "the message preview was read from the banner."

This matters to users. If Alice gets a blue tick every time Bob glanced at a notification, Bob would feel surveilled — Alice would know he saw the message even when he had no time to respond. The product respects the distinction between "notification delivered" and "message read in full context."

---

## The notification reply edge case

Bob reads the notification and replies inline — without opening the app. Does Alice get a blue tick now?

Not for the incoming messages — Bob replied from the background process, which doesn't render the chat screen and doesn't fire a read event. Alice gets:

```
Bob's reply sent: Alice sees Bob replied (her message feed updates)
last_read_seq: not updated   ← Bob never opened the chat
```

When Bob eventually opens WhatsApp and opens the chat, the read event fires and Alice gets the blue tick for her previous messages at that point.

> [!important] Summary
> Blue tick requires the chat screen to be open inside the app. Notification delivery, notification preview on lock screen, and notification inline replies do not count as read. The read event is application-level — it requires WhatsApp to be running and the conversation to be visible.
