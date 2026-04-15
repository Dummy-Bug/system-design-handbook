
> [!info] Where API Gateway and Load Balancer sit — and why placement matters
> In a chat system, the API Gateway behaves differently from a typical REST service. It handles the WebSocket upgrade at the edge, then steps out of the hot path entirely. Understanding why requires understanding the difference between HTTP and WebSocket at the protocol level.

---

## API Gateway placement

The API GW sits at the very edge — the first thing every client connection hits, before the Load Balancer.

```
Client → API Gateway → Load Balancer → Connection Server
```

For REST calls (chat history, inbox), this is standard — every request passes through the GW, gets validated, gets routed.

For WebSocket connections, the GW's role is front-loaded:

```
Phase 1 — HTTP Upgrade (GW is fully involved):
  Client → sends HTTP Upgrade request with Authorization header
  GW     → reads headers, validates token, checks rate limits
  GW     → forwards to LB → Connection Server
  Server → responds 101 Switching Protocols

Phase 2 — WebSocket frames (GW steps out):
  Alice sends "hey" → ws frame → Connection Server
  (API GW does NOT inspect this frame)
```

The GW does its job once, at connection time. Every message after that bypasses it.

---

## Why the API GW can't inspect WebSocket frames

This comes down to the difference between HTTP and WebSocket at the protocol level.

**HTTP — structured, parseable**

Every HTTP request is a self-contained text message with a well-defined format:

```
POST /messages HTTP/1.1
Host: chat.whatsapp.com
Authorization: Bearer token123
Content-Type: application/json
Content-Length: 45

{"content": "hey", "conversation_id": "abc"}
```

The API GW is an HTTP proxy. It reads this format: parse headers until `\r\n\r\n`, then read `Content-Length` bytes for the body. It can extract the `Authorization` header, validate the token, read the URL, apply routing rules. Every request is a fresh, complete, parseable unit.

**WebSocket — binary frames over a raw TCP stream**

After the upgrade, HTTP is gone. The connection becomes a persistent TCP pipe carrying WebSocket frames:

```
WebSocket frame structure:
  [2-14 byte binary header][payload bytes]

Header contains:
  - FIN bit: is this the last frame? (1 bit)
  - opcode: text / binary / ping / pong / close (4 bits)
  - mask bit + masking key (client→server frames are masked)
  - payload length (7 bits, extended if large)

That's it. No URL. No Authorization header. No Content-Type.
```

When Alice sends "hey", this travels over the wire:

```
HTTP POST (before upgrade):    POST /messages + Authorization: Bearer token123 + body
WebSocket frame (after):       [binary header][{"content":"hey","conversation_id":"abc"}]
```

The API GW is an HTTP proxy. It has no `Authorization` header to read, no URL to route on, no `Content-Type` to validate. It sees a stream of binary frames from a connection that was authenticated hours ago. It cannot apply per-message auth or routing rules the same way it does for HTTP.

> [!important] The underlying reason
> HTTP is stateless — each request is independent and carries full context. WebSocket is stateful — the connection carries the context (who this is, what session this belongs to) from the initial upgrade handshake. Auth is checked once at connection time. The connection server trusts every frame that arrives on an authenticated connection.

---

## What handles per-message validation then?

The **connection server** takes over:

```
Connection Server responsibilities after upgrade:
  - Validate frame size (reject messages over limit, e.g. > 10KB)
  - Validate payload structure (is it valid JSON? does it have required fields?)
  - Rate limit per connection (too many frames per second from one user)
  - Forward valid frames to App Server
```

This is lightweight validation — the connection server is not doing auth (already done by GW) or business logic (that's the App Server's job). It's just a sanity check on the raw frame.

---

## Load Balancer placement and sticky sessions

The LB sits between the API GW and the connection server fleet:

```
API GW → LB → [ws-server-1, ws-server-2, ..., ws-server-200]
```

For REST calls, the LB round-robins across app servers — each request is independent, any server can handle it.

For WebSocket connections, the LB must use **sticky sessions**:

```
Alice connects → LB assigns ws-server-3 → all Alice's frames go to ws-server-3
```

Why? Because the WebSocket connection is a stateful TCP connection to a specific server. If the LB tried to round-robin each frame to a different server, it would be routing frames to servers that don't have Alice's connection open. The connection would break.

Sticky sessions are typically implemented via IP hash or a session cookie set during the HTTP upgrade.

---

## Summary

```
API Gateway:
  → Sits at the edge, before LB
  → Full HTTP inspection on upgrade request (auth, rate limit)
  → Steps out after upgrade — cannot inspect WebSocket frames
  → Full inspection on all REST requests (chat history, inbox)

Load Balancer:
  → Sits between GW and connection server fleet
  → Sticky sessions for WebSocket connections (same server for lifetime of connection)
  → Round-robin for REST requests (stateless, any server)
```

> [!tip] Interview framing
> "The API GW handles auth once at connection time — during the HTTP upgrade. After that it's out of the hot path because it can't inspect raw WebSocket frames. Per-message validation (size, structure, rate limiting) moves to the connection server. The LB uses sticky sessions for WebSocket — you can't round-robin frames to different servers because the TCP connection is tied to one server."
