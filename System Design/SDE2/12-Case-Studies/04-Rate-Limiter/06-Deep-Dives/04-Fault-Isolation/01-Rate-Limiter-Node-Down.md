
## Rate Limiter Node Down

The simplest failure scenario. Rate limiter nodes are stateless — all counter state lives in Redis. A node going down loses nothing.

---

## What Happens

You have 10 rate limiter nodes behind a load balancer. Node 3 crashes.

```
Normal flow:
  Request → Load Balancer → Node 3 → Redis → allow/block

Node 3 down:
  Load Balancer health check fails for Node 3
  LB stops routing to Node 3 (within 5-10 seconds)
  All traffic redistributed across remaining 9 nodes
```

Users experience nothing visible — maybe a brief latency spike during the 5-10 second health check detection window. After that, traffic routes normally to the remaining nodes.

---

## Why No State Is Lost

Rate limiter nodes are **completely stateless** (except for the in-process rule cache and local counters). All counter state — every user's request count — lives in Redis, not in the rate limiter node itself.

When Node 3 crashes:
- No counters are lost — they were never stored on Node 3
- No requests need to be replayed — Redis has the full state
- Any other node can handle any request — they all talk to the same Redis cluster

This is exactly why the base architecture decision to keep rate limiter nodes stateless was correct. Stateless nodes are trivially replaceable.

---

## Local Counter Loss

The one thing lost when Node 3 crashes is its **in-process local counters** — the Layer 1 pre-filter cache. These are small and ephemeral by design.

When traffic for affected users reroutes to Node 4, Node 4 starts with a fresh local counter for those users. For a brief window, those users bypass the local pre-filter and hit Redis directly. This is fine — Redis is the source of truth, and the local counter is only a performance optimization, not a correctness requirement.

---

## Summary

```
Detection     : LB health check → 5-10 seconds
Impact        : brief latency spike, then normal
State lost    : none (stateless nodes, Redis has all counters)
Local counter : resets on reroute, brief Redis hit increase
Recovery      : automatic — LB stops routing to dead node
User impact   : none visible
```
