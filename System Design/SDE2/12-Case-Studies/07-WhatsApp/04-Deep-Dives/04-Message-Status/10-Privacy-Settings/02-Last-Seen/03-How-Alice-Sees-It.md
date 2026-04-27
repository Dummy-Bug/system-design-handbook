
> [!info] How Alice's client fetches Bob's last seen — piggybacked on chat open
> No separate API call. Last seen arrives bundled with the chat history on conversation open.

---

## When does Alice need last seen?

Alice only needs Bob's last seen timestamp when she opens a chat with him. It's displayed at the top of the conversation screen — "Last seen today at 9:42am" or "Online."

She doesn't need it while she's on her home screen or in a different chat. It's a per-conversation, on-demand piece of information.

---

## The naive approach — a separate API call

Alice opens the chat. Her client makes two calls:

```
GET /messages?conversation_id=conv_abc123    ← fetch chat history
GET /user/bob/last-seen                       ← fetch Bob's last seen
```

Two round trips. Two network calls. The second one is entirely dependent on Alice opening the chat — it will always happen together with the first.

---

## Piggybacking — one call, two pieces of data

Since both calls always happen together, bundle them into one:

```
GET /conversation/conv_abc123

Response:
{
  messages: [
    { seq: 42, content: "hey", sender: alice, timestamp: ... },
    { seq: 43, content: "where are you?", sender: alice, ... },
    ...
  ],
  bob_status: {
    online: false,
    last_seen: "2024-01-15T09:42:00Z"
  }
}
```

One round trip. Chat history and last seen arrive together. Alice's client renders both simultaneously.

This is piggybacking — hitching a free ride on a request that was already going to happen. The chat open request was always necessary. Last seen gets bundled in at zero additional network cost.

---

## What the server does to build this response

```
Alice opens conv_abc123
→ App server receives GET /conversation/conv_abc123

Step 1: fetch chat history
  → DynamoDB: PK=conv_abc123, SK >= last_read_seq (paginated)

Step 2: fetch Bob's status
  → Redis: GET ws:bob         → null (offline)
  → Redis: GET last_seen:bob  → "2024-01-15T09:42:00Z"

Step 3: assemble response
  → { messages: [...], bob_status: { online: false, last_seen: "..." } }
```

Both Redis reads happen in parallel — they're independent lookups. The response is assembled once both complete.

---

## Real-time updates — what if Bob comes online while Alice has the chat open

The chat open fetches a snapshot. But Bob might come online while Alice is actively in the conversation.

The WS server handles this — when Bob's WebSocket is established, the server pushes a presence event to Alice's client if Alice is in an active conversation with Bob:

```
Bob opens WhatsApp → WebSocket established → Redis: SET ws:bob
→ Presence service checks: who has conv_abc123 open right now?
→ Alice does → push to Alice's client: { bob_status: online }
→ Alice's screen updates: "Online"
```

And when Bob goes offline:

```
Bob closes WhatsApp → WS server detects disconnect
→ Push to Alice's client: { bob_status: last_seen: "9:42am" }
→ Alice's screen updates: "Last seen today at 9:42am"
```

The initial snapshot on chat open + real-time push events = Alice always sees accurate status without polling.

> [!tip] Interview framing
> "Last seen is fetched on chat open, piggybacked with the chat history response — one round trip, no separate API call. After that, presence updates are pushed over WebSocket in real time as Bob's status changes."
