
> [!info] The server already knows if Bob is online — it just has to check the Redis registry
> The connection registry was built to route messages to the right WebSocket server. It doubles as an online/offline detector for free.

---

## The Redis connection registry

Every time a user establishes a WebSocket connection, the WS server writes an entry to Redis:

```
SET ws:bob → ws_server_3
SET ws:alice → ws_server_1
```

Every time a user disconnects, the entry is deleted.

This means at any point in time, the Redis registry is a live map of who is online. If `ws:bob` exists in Redis — Bob is online. If it doesn't — Bob is offline.

---

## How the server uses this for delivery

When Alice's message arrives and needs to be delivered to Bob:

```
Step 1 → GET ws:bob from Redis

Step 2a → Entry found: ws_server_3
           → Bob is online
           → Forward message to ws_server_3
           → ws_server_3 pushes to Bob's WebSocket
           → Done

Step 2b → No entry found
           → Bob is offline
           → Do not attempt WebSocket delivery
           → Trigger offline delivery flow (covered in next files)
```

No separate online/offline status service needed. The registry check that was already needed for routing doubles as the online check. One Redis lookup, two purposes.

---

## What "offline" actually means here

Offline means one of three things:

```
1. Bob closed WhatsApp              → WebSocket closed, registry entry deleted
2. Bob's internet dropped           → WebSocket timed out, registry entry deleted
3. Bob's phone is off entirely      → Same as above from the server's perspective
```

From the server's perspective, all three look identical — no registry entry. The offline delivery mechanism handles all three the same way.
