
> [!info] The complete reconnect flow — from Bob's internet turning on to full message sync
> Every step from the OS detecting connectivity to Bob seeing all missed messages.

---

## Phase 1 — internet turns on, app is still closed

```
Bob's phone gets internet connection

Step 1 → OS re-establishes connection to APNs/FCM automatically
          No app involvement. This is OS-level infrastructure.

Step 2 → APNs/FCM had queued notification(s) waiting
          → delivers to Bob's phone immediately

Step 3 → Bob sees notification banner on lock screen:
          "Alice: hello??"   ← latest message preview

Bob has not opened WhatsApp yet. No WebSocket exists. No full history on device.
```

---

## Phase 2 — Bob taps the notification, WhatsApp opens

```
Step 4 → WhatsApp launches
          → reads conversation_id from notification payload → opens conv_abc123 directly

Step 5 → WhatsApp establishes WebSocket with WS server
          → HTTP upgrade → authenticated → WebSocket live

Step 6 → WS server writes to Redis registry:
          SET ws:bob → ws_server_3

Step 7 → WS server queries pending_deliveries:
          GET WHERE PK=bob
          → returns: [
              { conversation_id: conv_abc123, first_undelivered_seq: 42 },
              { conversation_id: conv_def456, first_undelivered_seq: 17 }
            ]
```

---

## Phase 3 — catch-up messages fetched and delivered

```
Step 8 → For each pending conversation, query DynamoDB in parallel:

          conv_abc123: PK=conv_abc123, SK >= 42
            → returns seq 42 "hey", seq 43 "where are you?", seq 44 "hello??"

          conv_def456: PK=conv_def456, SK >= 17
            → returns seq 17, 18, 19 from Carol

Step 9 → Push all messages to Bob over WebSocket in seq order

Step 10 → Bob's client inserts messages at correct seq positions
           → conversation renders with full history, correct order

Step 11 → Server deletes entries from pending_deliveries:
           DELETE {bob, conv_abc123}
           DELETE {bob, conv_def456}
```

---

## The full picture

```
Internet on
  ↓
OS → APNs/FCM → notification banner (latest message preview)
  ↓
Bob opens WhatsApp
  ↓
WebSocket established → Redis registry updated
  ↓
pending_deliveries queried → find all conversations with missed messages
  ↓
DynamoDB range queries (parallel) → fetch all missed messages
  ↓
Push to Bob over WebSocket → messages rendered in seq order
  ↓
pending_deliveries entries deleted
```

Bob sees every message Alice sent, in the correct order, within seconds of opening the app — regardless of how long he was offline.

> [!tip] Interview framing
> "When Bob's internet turns on, APNs/FCM delivers the queued notification via the OS-level connection — no app needed. When Bob opens WhatsApp, the WebSocket is created, we query pending_deliveries for his user_id, get the list of conversations with missed messages, do parallel DynamoDB range queries starting from first_undelivered_seq, and push everything to Bob. Full sync in one round trip per conversation."
