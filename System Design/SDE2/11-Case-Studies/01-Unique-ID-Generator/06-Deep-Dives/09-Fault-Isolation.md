# Fault Isolation

## The architecture

The ID generator runs as multiple stateless nodes behind a load balancer. Callers (Tweet service, Order service, etc.) never talk to a specific node directly — they always go through the LB.

```
Tweet Service ──→ Load Balancer ──→ ID Generator Node A
Order Service ──→                ──→ ID Generator Node B
Chat Service  ──→                ──→ ID Generator Node C
```

Stateless nodes mean any node can handle any request — no session state, no sticky routing needed.

---

## Node failure

If an ID generator node crashes, the load balancer detects it via health checks and stops routing traffic to it. All subsequent requests go to the remaining healthy nodes.

**What if a node crashes mid-request — after generating the ID but before returning it?**

The caller receives a timeout. It retries. The retry goes to a different healthy node, which generates a fresh ID and returns it successfully.

```
Caller → Node A: generates ID=5001, crashes before returning
Caller: timeout → retries
Caller → Node B: generates ID=6200, returns successfully ✅
```

What happened to ID=5001? It was generated in Node A's memory and never returned to any caller. No record was ever written with that ID. It's a gap in the ID space — and gaps are acceptable. Our FRs never required contiguous IDs.

> [!important] Retries are safe here
> The ID generator is a pure generation service — it doesn't write anything to a database. Retrying simply generates a new ID. There is no risk of double-issuing the same ID to the same caller because the crashed node's ID was never returned.

---

## ID space gaps on node crash

Any IDs that were in-flight or pre-loaded in a crashed node's memory are lost forever. This is identical to the KGS crash scenario — gaps appear in the ID sequence but no correctness is violated.

```
Node A issued: 5000, 5001, 5002... crash ...gap... 
Node B continues: 6200, 6201, 6202...
```

IDs are still globally unique. IDs are still time-sortable. The gap is invisible to callers.

---

## Load balancer failure

The load balancer is the entry point for all callers — if it goes down, no IDs can be generated regardless of how many healthy nodes exist.

Fix: run multiple load balancers behind a **Virtual IP (VIP)**. A VIP is a single IP address shared across multiple LB instances. If the active LB goes down, the VIP automatically fails over to a standby LB — transparent to callers.

```
Callers → VIP → Active LB → ID Generator nodes
                   ↓ fails
               Standby LB takes over (same VIP)
```

---

## No cascading failure risk

Unlike a KV store or a database, the ID generator has no shared state between nodes. Each node generates IDs independently using its own machine ID and local counter. A node failure cannot corrupt another node's counter or ID space.

This makes fault isolation simple — nodes fail independently, callers retry safely, and the system continues serving at reduced capacity until the failed node recovers or is replaced.

---

## Summary

| Failure | What happens | Recovery |
|---|---|---|
| Node crashes before returning ID | Caller times out, retries to another node | New ID generated, gap in ID space — acceptable |
| Node crashes with in-memory IDs | Those IDs lost forever | Gap in ID space — acceptable |
| Load balancer down | All requests fail | VIP + standby LB, automatic failover |
| Multiple nodes down simultaneously | Reduced throughput | Remaining nodes handle load; add nodes to restore capacity |
