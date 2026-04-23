
> [!info] Replying from the notification banner — without opening the app
> iOS and Android both support inline replies directly from the notification. WhatsApp doesn't need to fully launch for this to work.

---

## What inline reply looks like

Bob sees the notification banner: "Alice: hello??"

On iOS and Android, he can long-press the notification and type a reply directly — without opening WhatsApp. The reply sends. WhatsApp never fully launches.

---

## How it works under the hood

When Bob taps reply in the notification, the OS wakes WhatsApp as a **background process** — not a full app launch. The UI doesn't appear. Only a lightweight background task runs.

```
Bob types "on my way" in notification reply field
  → hits send

OS wakes WhatsApp background process
  → WhatsApp background task:
     1. Reads reply text and conversation_id from notification
     2. Makes a REST API call to the WhatsApp server:
        POST /messages
        { conversation_id: conv_abc123, content: "on my way", sender: bob }
     3. Server processes it normally:
        → INCR seq counter → write to DynamoDB → deliver to Alice
     4. Background task exits
```

No WebSocket. No full app session. Just one REST call.

---

## What Bob does NOT have at this point

Bob replied from the notification banner. He has not opened WhatsApp. His client has:

```
✓ The notification preview: "Alice: hello??"   (from notification payload)
✗ Full conversation history                     (not synced yet)
✗ Messages seq=42 "hey" and seq=43 "where are you?"  (never received)
```

The notification only carried the latest message preview. The earlier messages in this offline session are not on Bob's device yet.

---

## What happens when Bob opens WhatsApp after replying

```
Bob opens WhatsApp
  → WebSocket established
  → pending_deliveries queried: {conv_abc123, first_undelivered_seq=42}
  → DynamoDB query: PK=conv_abc123, SK >= 42
  → returns seq 42, 43, 44 (Alice's messages)
  → Bob's outgoing reply is already in DynamoDB as seq=45
  → Full conversation renders:

    seq=42  Alice: "hey"
    seq=43  Alice: "where are you?"
    seq=44  Alice: "hello??"
    seq=45  Bob:   "on my way"    ← his notification reply, already delivered
```

The full history appears as if nothing unusual happened. The notification reply slotted into the correct position in the conversation.

---

## Why this matters for the design

Notification reply confirms that WebSocket is not the only message delivery path. REST works for low-frequency, non-realtime sends like notification replies. WebSocket is the primary path because it's persistent and low-overhead for real-time messaging — but the system is designed to handle both.

> [!important] Two delivery paths
> WebSocket → primary, real-time, persistent connection
> REST → fallback, notification replies, one-off sends when app is not open
