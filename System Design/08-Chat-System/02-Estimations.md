- DAU - 50M, per user assume 100 messages per day , so we can see 500M writes per day. 
- Assuming peak load to be 20x , so (500M * 20) = 10B writes,
  so write QPS -> 10 * 10^9 / 10^5 -> 1M writes per second.


# Major APIs

1. Send message(from,to,text,media:[s3links]) // no need of group_id as we are focusing only on 1:1 chat.
2. Recent chats (user_id) : `List<Chats>` 
3. Open chat thread (current_user,other_user,chat_id)

**Real-Time Communication**

| Protocol         | Reason Rejected                                                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Short Polling    | Bombards server with requests even when no messages exist                                                                            |
| Long Polling     | Each message requires new HTTP connection → high reconnection overhead at 1M QPS                                                     |
| SSE              | Server → client only. Client would need a separate HTTP connection to send messages → two connections per user, wasteful and complex |
| **WebSockets** ✅ | Persistent bidirectional connection. One connection per user handles both sending and receiving with minimal overhead                |

Perfect way to think about it. Let's walk through each one with the exact same scenario:


**A sends "hey", B replies "hello back"**

---

**Short Polling**

```
A types "hey" → POST /messages (sends fine)

B's client is polling every 3 seconds:
B poll #1 → "any messages?" → "nope"
B poll #2 → "any messages?" → "nope"
B poll #3 → "any messages?" → "yes! A said hey"  ← up to 3 sec delay

B types "hello back" → POST /messages (sends fine)

A's client is polling every 3 seconds:
A poll #1 → "any messages?" → "nope"
A poll #2 → "any messages?" → "yes! B said hello back" ← up to 3 sec delay
```

**Why it breaks:**

- Message delivery is delayed by poll interval
- Even when nobody is talking, both clients are hammering server every 3 seconds
- At 5M users → 5M requests every 3 seconds even at 3am when nobody is chatting

---

**Long Polling**

```
A types "hey" → POST /messages (sends normal HTTP request)

B's client opens connection and waits:
B → "any messages?" → server holds connection...
message arrives → server responds → B gets "hey" instantly ✅
connection closes

B types "hello back" → POST /messages (sends HTTP)

A's client is waiting:
A → "any messages?" → server holds connection...
message arrives → server responds → A gets "hello back" instantly ✅
connection closes

// both immediately open new connections and wait again
```

**Why it breaks:**

- Message delivery is actually instant ✅
- But every time a message arrives, **connection closes and reopens**
- In an active conversation that's happening constantly
- Each reconnection = new TCP handshake = overhead
- At 5M users in active conversations → millions of reconnections per second

---

**SSE**

```
// Server → Client stream is open for both A and B

A's client has open SSE stream ← receiving from server ✅
B's client has open SSE stream ← receiving from server ✅

A types "hey"        → POST /messages (separate HTTP request)
Server pushes to message from A to B via SSE stream ✅

B types "hello back" → POST /messages (separate HTTP request)
Server pushes message to A from B via SSE stream ✅



```

**Why it breaks:**

- Receiving works perfectly fine ✅
- But **sending requires a separate HTTP connection**
- So every user now has **2 connections open simultaneously**
    - 1 SSE connection for receiving
    - 1 HTTP connection every time they send
- At 5M users → 10M+ connections
- More complex to manage than WebSockets

---

**WebSocket**

```
A has 1 persistent WS connection open
B has 1 persistent WS connection open

A types "hey" → sent over A's WS connection → server → pushed over B's WS connection → B gets it instantly ✅

B types "hello back" → sent over B's WS connection → server → pushed over A's WS connection → A gets it instantly ✅
```

**Why it works perfectly:**

- Single connection per user handles both sending and receiving
- Connection never closes during the session
- No reconnection overhead
- No polling overhead
- No duplicate connections

---

**Summary table for this exact scenario:**

||A sends "hey"|B receives instantly?|B sends "hello back"|A receives instantly?|Connections per user|
|---|---|---|---|---|---|
|Short Polling|✅|❌ up to 3s delay|✅|❌ up to 3s delay|1 but reopens every 3s|
|Long Polling|✅|✅|✅|✅|1 but reopens every message|
|SSE|✅ extra HTTP|✅|✅ extra HTTP|✅|2 (SSE + HTTP)|
|WebSocket|✅|✅|✅|✅|1 persistent|

**Conclusion:** WebSockets is the only viable option.

> WebSockets give us a persistent bidirectional connection. One connection per user handles both sending and receiving, with minimal overhead compared to repeated HTTP connections.






