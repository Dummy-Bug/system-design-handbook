
> [!info] Side-by-side comparison
> All four approaches solve the same problem — getting data from server to client in near-real-time. They differ dramatically in how much waste they generate, what latency they impose, and whether they support bidirectional communication.

---

## The numbers at scale

Baseline assumptions (80/20 rule applied twice):
```
MAU               → 500M
DAU               → 20% of MAU = 100M
Concurrent online → 20% of DAU = 20M
Write QPS         → 10k messages/sec
Latency SLO       → p99 < 200ms end-to-end
```

---

## Short Polling

```
Poll interval assumed: 2 seconds

Requests/sec       = 20M users / 2s         = 10M req/sec
Empty responses    = (10M - 10k) / 10M      = 99.9% waste
Max message delay  = up to 2 seconds        → SLO breached immediately
Connection type    = new connection per poll → constant churn
```

**Verdict: rejected.** 10M req/sec, 99.9% empty. Latency fundamentally bounded by poll interval.

---

## Long Polling

```
Persistent connections = 20M (one per user, waiting)
Servers needed         = 20M / 100k          = 200 servers

Per-message reconnect cost:
  TCP + TLS + HTTP     = ~100ms overhead per message delivery
  At 10k messages/sec  = 10k reconnections/sec happening simultaneously

Send path cost         = separate HTTP POST = ~100ms per send
Total latency          = 100ms (reconnect) + 10ms (transit) + 100ms (send) = ~220ms → SLO breached
```

**Verdict: rejected.** 100ms reconnection tax on every message delivery burns the latency budget. Separate send path adds another 100ms per send.

---

## SSE

```
Persistent SSE connections = 20M (receive only)
Servers needed             = 20M / 100k     = 200 servers

Receive path:  server pushes over persistent connection → ~10ms latency ✓
Send path:     separate HTTP POST per message           → ~100ms overhead ✗

Total connections:
  SSE receive pool   → 20M persistent
  HTTP send pool     → 10k new/sec (constant churn)

Two connection pools. Two code paths.
```

**Verdict: rejected for chat.** Receive path is clean. Send path is broken — ~100ms per send, separate connection pool, dual code paths. Fine for notifications and dashboards where clients never send back.

---

## WebSockets

```
WebSocket connections = 20M (one per user, bidirectional)
Servers needed        = 20M / 100k            = 200 servers

Upgrade handshake (once per session):
  TCP + TLS + WS upgrade = ~100ms (paid once, amortized)

Per-message cost (every message after handshake):
  WebSocket frame overhead = ~2-14 bytes
  Network transit          = ~10ms
  Total per message        = ~10ms ✓

End-to-end latency:
  Send → server → store → push to recipient = ~30ms ✓ (15% of 200ms SLO)

Connection pools: 1 (handles both send and receive)
```

**Verdict: winner.** One connection per user, full-duplex, zero per-message overhead after initial handshake. 30ms end-to-end — well inside the 200ms SLO with headroom for storage and routing.

---

## Full comparison table

| | Short Polling | Long Polling | SSE | WebSocket |
|---|---|---|---|---|
| **Connections** | 10M new/sec | 20M persistent | 20M persistent + churn | 20M persistent |
| **Connection pools** | 1 | 1 | 2 (receive + send) | 1 |
| **Empty request waste** | 99.9% | 0% | 0% | 0% |
| **Receive latency** | up to poll interval | ~0ms | ~0ms | ~0ms |
| **Send overhead** | ~100ms (new conn) | ~100ms (new conn) | ~100ms (new conn) | ~0ms (same conn) |
| **Bidirectional** | half-duplex | half-duplex | half-duplex | full-duplex |
| **Protocol overhead** | 500-1000 bytes/msg | 500-1000 bytes/msg | 500-1000 bytes/msg | 2-14 bytes/msg |
| **Best use case** | never | low-freq updates | dashboards, notifications | chat, games, collab |

---

## Decision rule

```
Need server to push AND client to send over same connection?
  → WebSocket (only full-duplex option)

Server pushes only, client never sends back?
  → SSE (simpler, built on HTTP, no upgrade needed)

Low frequency updates, latency doesn't matter much?
  → Long polling (simple, widely supported)

Never use short polling at scale.
```

> [!tip] Interview framing
> "I'd reject short polling immediately — the math shows 10M req/sec with 99.9% waste. Long polling and SSE both fail on the send path — every send costs a new HTTP connection and ~100ms handshake. WebSockets give us one persistent full-duplex connection per user: 20M connections across ~200 servers, ~30ms end-to-end, zero per-message overhead. That's the protocol I'd use for chat."
