
> [!info] Full status flow — Bob's phone is dead for 3 days, then he turns it on
> Every tick state Alice sees, and when each one changes.

---

## The setup

Alice and Bob are chatting. The last message Bob read was seq=41 (last_read_seq=41). Bob's phone dies — battery completely dead.

Over the next 3 days, Alice sends 5 messages:

```
seq=42  "hey"
seq=43  "where are you?"
seq=44  "hello??"
seq=45  "is everything okay?"
seq=46  "call me when you can"
```

Each is stored in DynamoDB. Each triggers an attempt to deliver to Bob — no WebSocket found, Bob is offline. `pending_deliveries` entry created for Bob / conv_abc123 with `first_undelivered_seq=42`.

APNs is called for each message, but Bob's phone is off — APNs queues the latest notification, can't deliver to a dead device.

---

## Alice's view during these 3 days

```
All 5 messages: single tick ✓

last_delivered_seq = 41  (last WebSocket ack Bob sent, before phone died)
last_read_seq = 41

Every message seq=42 through seq=46:
  seq > last_delivered_seq → single tick
```

Alice sees single tick on all 5 messages. Nothing changes until Bob's phone turns on.

---

## Day 3 — Bob turns his phone on

**Step 1 — OS connects to APNs**

Bob's phone powers on. The OS re-establishes its persistent connection to APNs automatically. No app involvement.

APNs had the latest notification queued: "Alice: call me when you can"

APNs delivers it immediately:

```
Bob's lock screen: "Alice: call me when you can"
```

Alice's tick view: still single tick. Nothing has changed server-side yet. The notification was delivered by Apple's infrastructure, not WhatsApp's.

---

## Step 2 — Bob does NOT open WhatsApp yet

Bob sees the notification. He's just woken up, doesn't open the app.

Alice: still single tick on all 5 messages.

---

## Step 3 — Bob taps the notification, WhatsApp opens

Bob taps. WhatsApp launches. The app reads `conversation_id` from the notification payload and opens conv_abc123 directly.

**WebSocket established:**
```
WhatsApp → WS server: HTTP upgrade → authenticated → WebSocket live
WS server → Redis: SET ws:bob → ws_server_3
```

**pending_deliveries queried:**
```
GET WHERE PK=bob
→ { conversation_id: conv_abc123, first_undelivered_seq: 42 }
```

**DynamoDB range query:**
```
PK=conv_abc123, SK >= 42
→ returns seq 42, 43, 44, 45, 46
```

**All 5 messages pushed to Bob over WebSocket.**

---

## Step 4 — Bob's client sends cumulative delivery ack

Bob's client receives all 5 messages, renders them:

```
Bob's client → WS server: {
  type: "delivered",
  conversation_id: "conv_abc123",
  seq: 46
}
```

**Server updates message_status:**
```
UPDATE message_status
  SET last_delivered_seq = 46
  WHERE user_id=bob AND conversation_id=conv_abc123
```

**Server checks if Alice is online:**
```
GET ws:alice → ws_server_1   (Alice is online)
→ Push to Alice: { type: "status_update", conversation_id: conv_abc123, last_delivered_seq: 46 }
```

**Alice's view:**
```
seq=42 through seq=46: double tick ✓✓
```

All 5 messages flip from single to double tick simultaneously. Alice is at her desk and sees the ticks update in real time.

---

## Step 5 — Bob reads the messages (chat is already open)

Bob is already on the chat screen — he tapped the notification and it opened directly to conv_abc123. The messages are visible. His client fires a read event:

```
Bob's client → WS server: {
  type: "read",
  conversation_id: "conv_abc123",
  seq: 46
}
```

**Server updates message_status:**
```
UPDATE message_status
  SET last_read_seq = 46
  WHERE user_id=bob AND conversation_id=conv_abc123
```

**Push to Alice:**
```
{ type: "status_update", conversation_id: conv_abc123, last_read_seq: 46 }
```

**Alice's view:**
```
seq=42 through seq=46: blue tick ✓✓ (blue)
```

---

## The full tick timeline from Alice's perspective

```
Day 0, 9am   Alice sends seq=42        → single tick ✓
Day 0, 2pm   Alice sends seq=43        → single tick ✓
Day 1        Alice sends seq=44, 45    → single tick ✓
Day 3, 8am   Alice sends seq=46        → single tick ✓

Day 3, 9am   Bob turns phone on        → still single tick (notification only, no WebSocket)
Day 3, 9:02am Bob opens WhatsApp       → WebSocket established
Day 3, 9:02am Bob's client acks seq=46 → all 5 messages flip to double tick ✓✓ instantly
Day 3, 9:02am Bob's client reads chat  → all 5 messages flip to blue tick ✓✓ seconds later
```

Three days of single tick. Then within seconds of Bob opening the app, both double tick and blue tick arrive. Alice sees two rapid tick updates in quick succession.

> [!tip] Interview framing
> "While Bob's phone is off, Alice sees single tick — no WebSocket means no delivery ack. The moment Bob opens WhatsApp, WebSocket is established, pending messages are pushed, Bob's client sends a cumulative delivered ack, and all messages flip to double tick. If Bob opens the chat (which he does, since the notification lands him there), read event fires immediately after and blue tick follows. Both updates arrive within seconds."
