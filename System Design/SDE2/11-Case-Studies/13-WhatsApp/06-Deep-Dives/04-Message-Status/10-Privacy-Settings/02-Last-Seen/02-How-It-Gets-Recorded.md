
> [!info] How the last seen timestamp gets recorded — WS server on disconnect
> The WS server is the only component that knows when a connection drops. It owns the write.

---

## Who detects the disconnect

The WS server maintains a persistent TCP connection with Bob's client. It's the only component in the system that knows the exact moment that connection breaks.

Two disconnect scenarios:

**Graceful close — Bob closes the app**
```
Bob swipes WhatsApp closed
→ App sends TCP FIN packet
→ WS server receives FIN: "Bob's connection is closing"
→ WS server records: last_seen[bob] = now()
→ WS server deletes ws:bob from Redis registry
```

**Ungraceful close — signal lost, battery dies, OS kills app**
```
Bob's phone loses signal (underground, tunnel, airplane mode)
→ No TCP FIN packet sent
→ WS server detects: no heartbeat received from Bob for 30 seconds
→ WS server assumes connection is dead
→ WS server records: last_seen[bob] = now()
→ WS server deletes ws:bob from Redis registry
```

The heartbeat is a small ping/pong exchange between client and server every ~15-30 seconds. If the server misses a heartbeat, it marks the connection as dead and treats it as a disconnect.

---

## Where the timestamp is stored

The last seen timestamp needs to be durable and queryable by any WS server — because Alice might be connected to a different WS server than the one that handled Bob's session.

Two options:

**Redis** — fast, already used for the online registry. But Redis is in-memory — if the instance restarts, last seen data is lost. Acceptable only if you're okay with showing a slightly stale value after a restart.

**Users table in the primary DB (DynamoDB)** — durable, always available. Slightly slower than Redis but last seen doesn't need sub-millisecond latency.

In practice: write to both. Redis for fast reads (serving Alice's chat open request), primary DB as the durable source of truth.

```
WS server on disconnect:
  → UPDATE users SET last_seen = now() WHERE user_id = bob     (DynamoDB — durable)
  → SET last_seen:bob = now() in Redis                         (Redis — fast reads)
```

---

## The online/offline state in Redis

The existing Redis registry already tracks online status:

```
Redis registry:
  ws:bob → ws_server_3    (bob is online, on this server)
```

When Bob disconnects, the WS server deletes this key. Absence of the key means offline.

Last seen is a separate key — it persists after the `ws:bob` key is deleted:

```
Redis:
  ws:bob         → (deleted on disconnect)
  last_seen:bob  → "2024-01-15T09:42:00Z"    (persists)
```

Alice queries `last_seen:bob` and gets the timestamp. She queries `ws:bob` and gets nothing — Bob is offline.

---

## Graceful vs ungraceful — does it matter for accuracy?

In the graceful case, the timestamp is precise — it's exactly when Bob closed the app.

In the ungraceful case (signal loss), the timestamp is when the heartbeat timeout fired — which could be up to 30 seconds after the actual disconnect. Bob lost signal at 9:42:00, but last seen shows 9:42:30.

This 30-second gap is acceptable. Last seen accuracy at the second level is not a requirement — users interpret "last seen today at 9:42am" at minute-level granularity anyway.

> [!tip] Interview framing
> "The WS server detects disconnection — either via graceful TCP close or heartbeat timeout. On disconnect, it writes the timestamp to the users table for durability and to Redis for fast reads. The Redis online registry key is deleted; the last_seen key persists."
