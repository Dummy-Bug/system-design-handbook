
> [!info] Long polling — the smarter naive fix
> Long polling eliminates the empty responses problem by making the server wait before responding. No message? Don't respond yet — hold the connection open until something arrives. It sounds clever. The numbers show where it falls apart.

---

## How it works

Instead of the server immediately responding with "nothing", it holds the connection open and waits. The moment a message arrives, it responds. The client immediately opens a new connection and waits again.

```
t=0s:   Client → "GET /messages" → Server ... (server holds, waiting)
t=0s:   Server is holding 20M connections open, all waiting
t=4s:   Alice sends Bob a message
t=4s:   Server → "1 new message" → Bob's client  (connection closes)
t=4s:   Bob's client immediately opens a new connection → Server ... (waiting again)
```

No more empty responses. The server only responds when there's something to say. Latency drops — the message arrives the moment it's available, not on the next poll cycle.

---

## The math — connections

Assumptions (80/20 rule applied twice):
```
MAU                   → 500M
DAU                   → 20% of MAU  = 100M
Concurrent online     → 20% of DAU  = 20M
```

Every online user holds one open connection waiting for messages:

```
Persistent connections held → 20M
Capacity per server (async) → 100k concurrent connections
Connection servers needed   → 20M / 100k = 200 servers
```

200 servers just to hold open connections doing nothing. Expensive, but manageable — this is the same cost you'd pay with WebSockets. So far long polling isn't worse.

---

## Where it breaks — the reconnection tax

Here's the real problem. Every time a message arrives, the connection closes and the client must reconnect. That reconnection pays the full handshake cost:

```
TCP handshake  → ~30ms
TLS handshake  → ~60ms
HTTP request   → ~10ms
Total          → ~100ms per reconnection
```

Write QPS is 10k messages/sec. Each message delivery closes one connection and triggers one reconnection:

```
Reconnections/sec       → 10k/sec
Cost per reconnection   → ~100ms of latency added
```

Your 200ms end-to-end SLO now looks like this:

```
Network transit (send)     → ~10ms
Server processing          → ~10ms
Reconnection overhead      → ~100ms
Network transit (receive)  → ~10ms
Total                      → ~130ms
```

You're burning 100ms — half your entire latency budget — on reconnection overhead that produces zero value. And this is the *average* case. Under load, TLS handshakes slow down. At peak 20k messages/sec, you have 20k reconnections happening simultaneously, all competing for server resources.

---

## The send path problem

Long polling only solves receiving. To send a message, the user still fires a separate HTTP POST — a brand new connection with its own handshake:

```
User sends a message:
  → New TCP connection    → ~30ms
  → New TLS handshake     → ~60ms
  → HTTP POST             → ~10ms
  Total                   → ~100ms just to initiate the send
```

So every user maintains two connection paths:
```
Receive path → 1 persistent long-poll connection (waiting)
Send path    → new HTTP connection per message sent (~100ms overhead each)
```

Two separate code paths. Two connection pools. And still paying 100ms per send.

---

## Verdict

Long polling is rejected. It fixes the empty response problem of short polling, but introduces a reconnection tax of ~100ms on every message delivery. Combined with a separate send path that costs another ~100ms per message, you've burned your entire latency budget before the message even reaches its destination.

> [!tip] When long polling is acceptable
> Long polling is fine for low-frequency updates — think GitHub showing "this PR was updated" or a dashboard refreshing every 30 seconds. When messages are rare and latency doesn't matter much, the reconnection cost is paid infrequently. It's only a disaster when messages are frequent and latency is tight.
