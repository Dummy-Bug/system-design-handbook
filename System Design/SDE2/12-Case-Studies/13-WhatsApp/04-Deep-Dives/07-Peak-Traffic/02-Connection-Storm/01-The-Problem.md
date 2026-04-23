
> [!info] The connection storm — 500M WebSocket connections at midnight
> When 500M users open WhatsApp at the same time, every one of them needs a WebSocket connection. Each connection triggers a registry write. That registry write is the bottleneck.

---

## The connection layer

Each user needs a persistent WebSocket connection to a connection server. With modern hardware, a single connection server running Go or Node can handle roughly 1M concurrent WebSocket connections.

```
500M connections / 1M per server = 500 connection servers
```

500 servers is expensive but operationally manageable at WhatsApp scale. The connection establishment itself — TCP handshake, WebSocket upgrade, auth token validation — is not the bottleneck. These are CPU-bound and horizontally scalable.

---

## Where it breaks — the connection registry

Every time a user connects, the app server must record which connection server they're on:

```
HSET registry user:alice conn_server_7
```

This is what allows message routing — when Bob sends Alice a message, the app server looks up `registry:alice` to find which connection server to forward it to.

At midnight, 500M users connect in a very short window. That's 500M registry writes hitting Redis simultaneously.

```
500M registry writes / 100K ops per Redis node = 5,000 Redis primaries needed
```

You're not provisioning 5,000 Redis primaries. There has to be a better approach.

---

## The insight — registry writes don't need to be synchronous

The registry write is only needed when someone sends Alice a message. It does not need to be complete before Alice's connection is established and working. Alice can send and receive messages fine without her registry entry being written — the routing lookup only matters for *inbound* messages.

This means the registry write can be **delayed**. The connection is established immediately. The registry write is queued and processed asynchronously.

> [!important] Don't confuse connection establishment with registry registration
> The WebSocket connection is live the moment the handshake completes. The registry write is an administrative record for routing. These don't need to happen atomically.
