
> [!info] WebSockets — the right tool
> WebSockets give you one persistent, full-duplex connection per user. Either side can send at any time. One handshake upfront, zero overhead per message after that. This is the protocol chat systems are built on.

---

## How it works

A WebSocket connection starts as a regular HTTP request — a special one called an **upgrade request**. The client asks the server to upgrade the connection from HTTP to WebSocket. If the server agrees, the HTTP connection is converted into a persistent WebSocket connection. From that point on, both sides can send frames at any time — no more request-response, no more client-initiates-only.

```
Step 1 — HTTP Upgrade (one time only):
  Client → "GET /ws HTTP/1.1"
            "Upgrade: websocket"
            "Connection: Upgrade"     → Server
  Server → "101 Switching Protocols"  → Client
  (connection is now a WebSocket)

Step 2 — Full-duplex communication (zero overhead per message):
  Server → frame: "new message from Alice" → Client   (server pushes)
  Client → frame: "here's my reply"        → Server   (client pushes)
  Both sides can send at any time, independently
```

The upgrade handshake happens once when the user opens the app. Every message after that travels as a lightweight WebSocket frame — no HTTP headers, no handshake, no new connection.

---

## The math — connections

Assumptions (80/20 rule applied twice):
```
MAU                   → 500M
DAU                   → 20% of MAU  = 100M
Concurrent online     → 20% of DAU  = 20M
```

Each online user holds exactly one WebSocket connection — for both sending and receiving:

```
WebSocket connections       → 20M  (one per online user, handles both directions)
Capacity per server (async) → 100k concurrent connections
Connection servers needed   → 20M / 100k = 200 servers
```

Same 200 servers as SSE. But now those 200 servers handle everything — send and receive — through a single connection pool. No second pool for sends.

---

## The latency math

The upgrade handshake is paid once per session:

```
TCP handshake   → ~30ms
TLS handshake   → ~60ms
WS upgrade      → ~10ms
Total (once)    → ~100ms  (paid when user opens the app, amortized over entire session)
```

Every message after that:

```
Client sends a message:
  WebSocket frame to server     → ~10ms (network, same region)
  Server processes + stores     → ~10ms
  Server pushes to recipient    → ~10ms
  Total end-to-end              → ~30ms
```

30ms end-to-end. You're using 15% of your 200ms latency SLO. You have 170ms of headroom for everything else — storage writes, routing logic, any cross-region latency. The protocol itself is no longer the bottleneck.

---

## Why WebSockets handle 100k connections per server

WebSocket servers use **async I/O** (epoll on Linux). Instead of one thread per connection — which would require 20M threads and terabytes of RAM — one thread watches thousands of connections simultaneously. The OS notifies the thread only when a connection has data.

```
Classic model (one thread per connection):
  1 thread   → ~1MB RAM (stack)
  20M threads → 20TB RAM  ← impossible

Async I/O model (epoll):
  1 thread handles ~10k connections
  20M connections / 10k per thread = 2,000 threads
  2,000 threads × 1MB = ~2GB RAM  ← totally fine
```

This is why modern WebSocket servers (Node.js, Netty, Go) can handle 100k+ concurrent connections on a single machine.

---

## WebSocket frames are tiny

HTTP has headers on every request — Content-Type, Authorization, Cookie, User-Agent — easily 500-1000 bytes of overhead per request. WebSocket frames strip all of that:

```
HTTP request overhead   → 500-1000 bytes per request
WebSocket frame header  → 2-14 bytes per message
```

For a 100-byte text message:
```
HTTP POST total size    → ~600-1100 bytes (message + headers)
WebSocket frame total   → ~114 bytes      (message + 14 byte header)
```

At 10k messages/sec:
```
HTTP bandwidth    → 10k × 1000 bytes = 10 MB/s
WebSocket         → 10k × 114 bytes  = 1.14 MB/s
```

WebSockets use ~9x less bandwidth than equivalent HTTP for the same message volume.

---

## What WebSockets don't solve

WebSockets solve the connection and latency problem. They don't solve:

- **Message routing** — if Alice is connected to server A and Bob is connected to server B, how does server A know to route Alice's message to server B? This is a separate problem solved by a routing layer (covered in the architecture deep dive).
- **Offline delivery** — if Bob is not connected, the WebSocket push fails. You need a message store and a push notification system for offline users.
- **Message ordering** — WebSockets deliver messages in the order they arrive at the server, but if two messages arrive simultaneously from different clients, ordering is not guaranteed. This requires sequence numbers per conversation.

---

> [!tip] Interview framing
> "WebSockets give us one persistent full-duplex connection per user. The upgrade handshake costs ~100ms once. Every message after that is ~0ms protocol overhead. At 20M concurrent users, we need ~200 connection servers using async I/O. The protocol is no longer the bottleneck — routing and storage become the interesting problems."
