
> [!info] The notification carries a preview — not the full message history
> What arrives on Bob's phone via APNs/FCM is a small payload. It shows enough to understand the message, but the full history only arrives after the app opens.

---

## What the notification payload contains

APNs and FCM deliver a JSON payload with strict size limits (APNs: 4KB, FCM: 4KB). The payload is not a full message dump — it's just enough to show a useful notification:

```json
{
  "title": "Alice",
  "body": "hey",
  "conversation_id": "conv_abc123",
  "sender_id": "alice",
  "seq_no": 42
}
```

Bob sees on his lock screen:

```
WhatsApp
Alice: hey
```

That's it. No message history. No previous messages. Just the preview of the latest message.

---

## Multiple messages while offline — only the latest shows

Alice sends three messages while Bob is offline:

```
seq=42 "hey"
seq=43 "where are you?"
seq=44 "hello??"
```

Each triggers a separate APNs call. But APNs collapses notifications for the same app and conversation — the latest replaces the previous:

```
Bob's lock screen shows:
  "Alice: hello??"    ← only the latest
```

The earlier two messages ("hey" and "where are you?") are not visible on the lock screen. They will be delivered when Bob opens WhatsApp and the full sync happens.

---

## Why message content is kept minimal in notifications

**Privacy:** If Bob's phone is on a table and someone else glances at it, the full conversation being visible in the notification is a privacy concern. WhatsApp gives users settings to show/hide message content in notifications for exactly this reason.

**Size limits:** APNs and FCM have a 4KB payload limit. Full message content for multiple messages would exceed this quickly.

**Not needed:** The notification's only job is to nudge Bob to open the app. The full history is delivered over WebSocket once he does. The payload just needs to be descriptive enough to make Bob want to open it.

---

## What the app does with the payload on tap

When Bob taps the notification:

```
1. WhatsApp launches (full app, not background process)
2. Uses conversation_id from notification payload to open the right chat
3. Establishes WebSocket connection
4. Full sync kicks in → fetches all missed messages from pending_deliveries
5. Bob sees complete conversation history
```

The notification payload's `conversation_id` is the navigation hint — it tells WhatsApp which chat to open directly rather than dropping Bob at the inbox.
