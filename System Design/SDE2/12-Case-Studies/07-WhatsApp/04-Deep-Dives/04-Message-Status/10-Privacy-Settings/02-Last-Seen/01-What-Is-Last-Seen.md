
> [!info] What "last seen" is — and the two events that drive it
> A timestamp showing when Bob was last active on WhatsApp. Generated from two system events: app open and app close.

---

## What Alice sees

When Alice opens a chat with Bob, she sees one of two things at the top of the screen:

```
Online                        ← Bob has WhatsApp open right now
Last seen today at 9:42am     ← Bob last had WhatsApp open at 9:42am
```

"Online" means Bob's WebSocket is live at this moment. "Last seen" means it isn't — and this is when it last was.

---

## The two events

Last seen is driven by exactly two events in the system:

**Event 1 — App opens**

Bob opens WhatsApp. The app establishes a WebSocket connection with the WS server. The moment that connection is live, Bob is considered online.

```
Bob opens WhatsApp
→ WebSocket established
→ Redis registry: SET ws:bob → ws_server_3
→ Bob's status: ONLINE
→ Alice sees: "Online"
```

**Event 2 — App closes (or connection drops)**

Bob closes WhatsApp — or his phone loses signal, locks, or the OS kills the app. The WebSocket connection breaks.

The WS server detects the disconnection — either via a graceful TCP close or a heartbeat timeout — and records the timestamp:

```
Bob closes WhatsApp
→ WebSocket disconnects
→ WS server detects: connection for bob gone
→ Records: last_seen[bob] = now()
→ Redis registry: DEL ws:bob
→ Bob's status: OFFLINE
→ Alice sees: "Last seen today at 9:42am"
```

---

## What drives the timestamp — close, not open

The last seen timestamp is always the **disconnect time**, not the connect time.

If Bob opened WhatsApp at 9:30am and closed it at 9:42am, last seen shows 9:42am. Alice knows Bob was active until 9:42am — not when he first opened the app. The closing moment is what matters.

---

## Why "online" and "last seen" are separate states

They feel like one feature but they're two distinct states:

```
ONLINE      → WebSocket is live right now
             → updated in real time as Bob uses the app
             → disappears the moment Bob closes the app

LAST SEEN   → timestamp of the most recent disconnect
             → persists after Bob goes offline
             → Alice can see it even hours or days later
```

"Online" is ephemeral — it exists only while the connection is live. "Last seen" is durable — it's stored and served on demand.
