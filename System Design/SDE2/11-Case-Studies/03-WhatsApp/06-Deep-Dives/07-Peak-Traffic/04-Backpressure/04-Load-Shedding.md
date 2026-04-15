
> [!info] Load shedding — rejecting requests before the system crashes
> Once the in-memory queue is full, the app server stops accepting new requests. It returns 429 to the connection server, which translates it into a WebSocket error for the client.

---

## The rejection chain

When the app server's queue is full, it cannot accept more work. It returns HTTP 429 to whoever called it — in this case, the connection server.

The connection server receives the 429, translates it into a WebSocket error message, and sends it back to the client over the existing connection.

```
Alice sends a message during overload:
→ Connection server → HTTP POST to App Server
→ App Server: queue full → returns HTTP 429
→ Connection server: receives 429
→ Connection server: sends WS error to Alice

{
  "type": "ERROR",
  "code": "SERVER_BUSY",
  "message": "Server is busy. Please retry.",
  "retry_after_ms": 2000
}

→ Alice's UI: message marked as failed, "tap to retry"
```

---

## Why HTTP 429 works here but not at the client boundary

The connection server and app server communicate over HTTP — internal service-to-service calls. HTTP status codes work perfectly here. 429 is unambiguous: "I'm overwhelmed, back off."

At the client boundary, the connection is WebSocket — no HTTP status codes. That's why the connection server translates the internal 429 into a structured WebSocket message before forwarding to the client.

```
Internal (HTTP):    App Server → 429 → Connection Server      ✅ HTTP works
External (WS):      Connection Server → WS error → Client     ✅ WS message works
```

---

## What happens next

The client retries after the `retry_after_ms` window. By then, one of two things has happened:

1. The spike has passed and the app server queue has drained
2. Auto-scaling has added new app servers and the load has distributed

Either way, the retry succeeds. The user experiences a 2-second delay on one message. The system never crashed.

> [!tip] Interview framing
> "When the app server queue fills, it returns 429 to the connection server. The connection server translates this into a WebSocket error with a retry_after field. The client retries after the backoff window. Auto-scaling runs in parallel and restores capacity within minutes."
