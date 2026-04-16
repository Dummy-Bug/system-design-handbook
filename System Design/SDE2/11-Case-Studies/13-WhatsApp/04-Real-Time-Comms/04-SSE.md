
> [!info] SSE — Server-Sent Events
> SSE fixes the reconnection problem for receiving messages. One persistent connection, server pushes whenever it wants, no reconnection on each message. But it's a one-way street — and that's a fatal flaw for chat.

---

## How it works

SSE opens one persistent HTTP connection and keeps it open for the lifetime of the session. The server streams events down it whenever something arrives. No polling, no reconnection per message — the pipe stays open.

```
t=0s:   Client opens SSE connection → Server (stays open)
t=4s:   Alice sends Bob a message
t=4s:   Server pushes event down the open SSE stream → Bob's client
t=10s:  Another message arrives
t=10s:  Server pushes again → Bob's client
        (same connection, still open)
```

For receiving messages, this is actually good. Low latency — the message arrives the moment it's pushed. No reconnection overhead. One persistent connection per user.

---

## The math — receive side

Assumptions (80/20 rule applied twice):
```
MAU                   → 500M
DAU                   → 20% of MAU  = 100M
Concurrent online     → 20% of DAU  = 20M
```

Each online user holds one persistent SSE connection for receiving:

```
SSE connections held        → 20M
Capacity per server (async) → 100k concurrent connections
Servers needed (receive)    → 20M / 100k = 200 servers
```

So far identical to long polling — 200 servers. No improvement yet.

---

## The fatal flaw — SSE is receive-only

SSE is built on HTTP. HTTP is half-duplex. The client can receive data over the SSE stream, but **it cannot send data back over that same connection**. The stream only flows one way — server to client.

So when a user wants to send a message, they must open a completely separate HTTP connection:

```
User A's connections:
  Receive path → 1 persistent SSE connection   (server pushes to A)
  Send path    → new HTTP POST per message sent (~100ms handshake each)
```

Now count the total connections in the system:

```
SSE receive connections  → 20M persistent (one per online user)
HTTP send connections    → 10k new/sec     (one per message sent, short-lived but constant churn)
```

Two connection pools. Two code paths. And the send path still pays the full ~100ms handshake cost on every single message:

```
TCP handshake  → ~30ms
TLS handshake  → ~60ms
HTTP POST      → ~10ms
Total per send → ~100ms
```

---

## The browser connection limit

SSE runs over HTTP/1.1. Browsers enforce a limit of **6 concurrent connections per domain** under HTTP/1.1. An SSE connection burns one of those 6 permanently for the lifetime of the session.

```
Browser connection budget:  6 total
SSE connection:             1 (permanently held)
Remaining for everything:   5
```

On a page that makes multiple API calls simultaneously (loading images, fetching data), burning one connection permanently on SSE creates contention. HTTP/2 lifts this limit via multiplexing, but not all environments support HTTP/2, and SSE's fundamental one-way limitation remains regardless.

---

## Where SSE actually fits

SSE is not useless — it's just the wrong tool for chat. It's the right tool when:

- The server needs to push updates to the client
- The client never needs to send data back over the same channel
- Low frequency updates are acceptable

```
Good fit for SSE:
  → Live sports scores (server pushes score updates)
  → Stock price tickers (server pushes price changes)
  → Deployment status dashboards (server pushes build events)
  → Notification banners (server pushes "you have a new message" alerts)

Bad fit for SSE:
  → Chat (bidirectional — users both send and receive)
  → Multiplayer games (high-frequency bidirectional)
  → Collaborative editing (bidirectional, latency-sensitive)
```

---

## Verdict

SSE is rejected for chat. It solves the receive path cleanly — one persistent connection, server pushes, no reconnection overhead. But it cannot solve the send path. Every message send costs a new HTTP connection and ~100ms of handshake overhead. You end up with two separate connection pools, two code paths, and the same latency problem on sends as long polling.

> [!important] SSE vs WebSocket — the one-liner
> SSE = server to client only, built on HTTP, simple to implement, great for dashboards and notifications. WebSocket = full-duplex, both sides can push, one connection handles everything. If you need bidirectional real-time communication, it's WebSocket. If you only need the server to push occasional updates, SSE is simpler and perfectly adequate.
