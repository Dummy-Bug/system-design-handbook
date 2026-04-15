
> [!info] Connection server failure — what the client experiences
> When a connection server dies, the clients connected to it don't get a graceful notification. The TCP socket goes dead, and the client detects this through heartbeats and reconnects automatically.

---

## The failure scenario

Connection server 7 goes down — hard crash, OOM kill, power cut, network partition. It gets no chance to notify anyone. 1 million users were connected to it.

From the client's perspective, the WebSocket connection goes silent.

---

## How the client detects the failure

WhatsApp clients send a **heartbeat ping** to the connection server every N seconds (typically 30-60 seconds on mobile to preserve battery). The connection server responds with a pong.

When server 7 dies:

```
Client → ping → server 7
Server 7: dead, no response
Client: no pong received within timeout
→ Client marks connection as dead
→ Client initiates reconnect
```

In many cases the TCP socket itself breaks immediately when the server process dies — the OS sends a TCP RST or FIN. The client's socket library detects this without waiting for a heartbeat timeout.

```
Server 7 process killed
→ OS sends TCP RST to all 1M connected clients
→ Client socket libraries detect broken connection immediately
→ All 1M clients begin reconnect simultaneously
```

The heartbeat is the fallback for silent failures — network partitions where the connection appears alive but packets are being dropped.

---

## The reconnect flow

The client reconnects to the same entry point — the load balancer. It has no knowledge of individual connection servers.

```
Client detects dead connection
→ Client connects to load balancer (same URL as original connection)
→ LB health checks have detected server 7 is down (within seconds)
→ LB routes to any healthy server (e.g. server 3)
→ New WebSocket established on server 3
→ Auth token validated
→ Registry update queued: user:alice → server3
→ Alice is back online
```

The client doesn't need to know which server died or why. It just reconnects to the LB and gets routed to a healthy server automatically.

> [!tip] Interview framing
> "Clients detect the dead connection via TCP RST or heartbeat timeout. They reconnect to the load balancer — which has already stopped routing to the dead server via health checks. The client is back online within seconds, no manual intervention needed."
