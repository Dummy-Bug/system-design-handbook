
> [!info] Telling the client they've been rate limited
> You can't return HTTP 429 over a WebSocket connection. The error goes back as a WebSocket message on the same channel.

---

## The problem with HTTP status codes

Rate limiting on REST APIs is simple — return HTTP 429 Too Many Requests. The client sees the status code and backs off.

WebSocket is a different protocol. Once the connection is upgraded, there are no HTTP requests and no HTTP status codes. Everything is messages — in both directions. A rejection has to be communicated as a message from server to client.

---

## The solution — error message on the same channel

When Alice's message is rejected by the rate limiter, the connection server sends a structured error back over the same WebSocket connection:

```json
{
  "type": "ERROR",
  "code": "RATE_LIMITED",
  "message": "Too many messages. Slow down.",
  "retry_after_ms": 1000
}
```

The client-side SDK handles this message type. It marks the message as "not sent" in the UI (the clock icon instead of a tick), and surfaces a "try again" option to the user after the retry window expires.

---

## What the user sees

```
Alice types message 11 and hits send
→ Message appears in UI with "sending..." state
→ Connection server rejects it, sends ERROR back
→ SDK receives ERROR, marks message as failed
→ UI shows message with red indicator + "Not delivered. Tap to retry."
→ After 1 second, Alice can retry
```

This is the same UX as a failed delivery due to network issues — the user is never confused, they just tap retry.

> [!tip] Interview framing
> "Since this is WebSocket, we can't return HTTP 429. The connection server sends a structured error message back over the same connection with a retry_after field. The client SDK handles it — marks the message as failed and surfaces a retry option."
