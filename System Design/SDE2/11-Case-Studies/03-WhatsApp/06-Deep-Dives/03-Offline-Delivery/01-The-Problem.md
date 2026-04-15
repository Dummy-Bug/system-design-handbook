
> [!info] Delivery requires a live connection — but recipients aren't always connected
> Every message delivery in the base architecture assumes Bob has an active WebSocket connection. The moment Bob goes offline, that assumption breaks.

---

## What the base architecture assumes

In the happy path, message delivery works like this:

```
Alice sends "hey"
  → WS Server receives it
  → Looks up Bob's ws_server_id in Redis registry
  → Forwards to Bob's WS server
  → Bob's WS server pushes to Bob's WebSocket
  → Bob sees "hey" instantly
```

This works perfectly — as long as Bob is connected.

---

## What breaks when Bob is offline

Bob closes WhatsApp and puts his phone down. Alice sends "hey."

```
Alice sends "hey"
  → WS Server receives it
  → Looks up Bob in Redis registry
  → No entry found
  → ??? 
```

There is no WebSocket to push to. The message has been received by the server, written to DynamoDB, assigned seq_no=42 — but it has nowhere to go. If the server does nothing, the message is silently lost from Bob's perspective. He will never see it.

---

## The two problems to solve

This is actually two separate problems that require two separate solutions:

```
Problem 1 — Storage gap
  How does the server hold the message safely until Bob reconnects?
  The message is in DynamoDB, but how does the server know to push it to Bob later?

Problem 2 — Delivery trigger  
  How does the server know when Bob comes back online?
  And how does Bob get notified before he even opens WhatsApp?
```

Problem 1 is solved by the pending deliveries table.
Problem 2 is solved by push notifications (APNs/FCM) and the WebSocket reconnect flow.

Both are covered in the following files.
