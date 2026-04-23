## What Is a Cascading Failure?

A cascading failure is when one failure triggers another, which triggers another, creating a domino effect that can take down the entire cluster. The initial failure is survivable — it's the chain reaction that kills the system.

The pattern is always the same: **failure → load shift → overload → more failure → more load shift**.

---

## Why VNodes Already Protect Against Single Node Failures

When a node dies, its load redistributes to other nodes. Without vnodes, the two neighboring nodes on the ring absorb ALL the extra load — potentially doubling their traffic. That could push them over the edge.

But with vnodes (256 per physical node), the dying node's load is spread across **dozens of different nodes** on the ring. Each node picks up a tiny fraction:

```
Without vnodes:
  Node D dies (500 reads/sec)
  → Node E absorbs 250 reads/sec extra (50% increase) → dangerous
  → Node F absorbs 250 reads/sec extra (50% increase) → dangerous

With vnodes:
  Node D dies (500 reads/sec)
  → Spread across ~30 different nodes
  → Each picks up ~17 reads/sec extra (~3% increase) → barely noticeable
```

Even if a full rack dies (10 nodes), vnodes distribute the load so thinly that no individual node gets overwhelmed. VNodes are our first line of defense against load-based cascading failures.

---

## When VNodes Can't Help — Traffic Spikes

VNodes protect against **redistributed** load. But they can't help when **all nodes** are overloaded simultaneously. A viral event, a marketing campaign, or a DDoS causes 10x normal traffic — every node goes from 500 reads/sec to 5,000 reads/sec at the same time.

```
Normal day:
  Every node: 500 reads/sec at 10% capacity → comfortable

Viral event:
  Every node: 5,000 reads/sec at 100% capacity → drowning
  No load to redistribute — EVERYONE is overwhelmed
```

Without protection, nodes start dying under the load. Each death shifts more traffic to survivors, who are already at their limit. They die too. The cluster collapses.

This is where our three defenses come in.

---

## Defense 1 — Rate Limiting (Node Protects Itself)

Each node knows its own capacity — say 6,000 requests/sec before performance degrades. Beyond that threshold, it **rejects** excess requests immediately with a 503 "service unavailable" error instead of trying to serve them.

### Example — viral traffic spike

```
Normal: 500 requests/sec → all served ✓
Spike:  8,000 requests/sec hits Node B

Without rate limiting:
  Node B tries to serve all 8,000
  → Memory fills up queuing requests
  → Garbage collection pauses spike
  → Response times go from 5ms to 2,000ms
  → Clients timeout → retry → even MORE load
  → Node B crashes
  → Its load shifts to neighbors → they crash → cascade

With rate limiting (cap at 6,000/sec):
  Requests 1-6,000:    → served normally, 5ms response time
  Requests 6,001-8,000: → instantly rejected with 503
  
  Node B stays healthy. 75% of requests succeed.
  The 25% that got rejected can retry on a different node.
  Node B stays alive, stays in gossip, keeps serving.
```

The key insight: **it's better to reject some requests than to crash and reject ALL requests.** A node returning 503 is still alive — it participates in gossip, serves most requests, and can recover when the spike passes. A crashed node is completely gone.

---

## Defense 2 — Circuit Breaker (Coordinator Protects the Node)

Rate limiting is the node protecting itself. A circuit breaker is the **coordinator** protecting a struggling node by stopping sending it requests.

The coordinator tracks the error rate from each node. If a node starts returning errors or timing out frequently, the coordinator **opens the circuit** — stops sending requests to that node for a cooldown period. After the cooldown, it sends a few test requests. If they succeed, the circuit closes and normal traffic resumes.

### Example — Node C is struggling

```
Coordinator tracking Node C:

  Request 1: success (2ms)
  Request 2: success (3ms)
  Request 3: timeout (5000ms)
  Request 4: timeout (5000ms)
  Request 5: 503 error
  Request 6: timeout (5000ms)

  Error rate: 4 out of 6 = 67% → exceeds threshold (50%)
  → OPEN circuit for Node C
  → Stop sending requests to Node C for 30 seconds
  → Route to other replicas instead
```

After 30 seconds:

```
  → Send ONE test request to Node C
  → If success → CLOSE circuit → resume normal traffic
  → If failure → keep circuit OPEN → wait another 30 seconds
```

```
Circuit breaker states:

CLOSED (normal)  → requests flow to the node normally
                 → if error rate exceeds threshold → switch to OPEN

OPEN (tripped)   → no requests sent to the node
                 → node gets time to recover
                 → after cooldown period → switch to HALF-OPEN

HALF-OPEN (test) → send a few test requests
                 → if they succeed → switch to CLOSED
                 → if they fail → switch back to OPEN
```

Without a circuit breaker, the coordinator keeps sending requests to a struggling node, piling on more load and preventing recovery. The circuit breaker gives the node **breathing room** to recover.

---

## Defense 3 — Exponential Backoff with Jitter (Client Spreads Out Retries)

When a client gets a 503, the natural instinct is to retry immediately. But if 1,000 clients all get 503 at the same time and all retry immediately — that's another spike of 1,000 requests hitting the system at once. This is the **thundering herd** problem.

### Without backoff — thundering herd

```
Time 0ms:    1,000 clients send requests → node overloaded → all get 503
Time 1ms:    1,000 clients retry immediately → same spike → all get 503 again
Time 2ms:    1,000 clients retry again → same spike → node crashes
```

The retries ARE the attack. Each retry wave is just as big as the original spike.

### With exponential backoff — spreading the load

Each client waits longer before each retry:

```
Client A:
  Attempt 1: fails → wait 100ms → retry
  Attempt 2: fails → wait 200ms → retry
  Attempt 3: fails → wait 400ms → retry
  Attempt 4: succeeds ✓
```

But there's still a problem — if 1,000 clients all start at the same time with the same backoff schedule, they all retry at 100ms, then all at 300ms, then all at 700ms. Still synchronized spikes.

### With jitter — breaking synchronization

Add a random delay (jitter) to each wait time:

```
Client A: wait 100ms + random(0-50ms) = 127ms
Client B: wait 100ms + random(0-50ms) = 103ms
Client C: wait 100ms + random(0-50ms) = 148ms
Client D: wait 100ms + random(0-50ms) = 111ms
...

Instead of 1,000 retries hitting at exactly 100ms:
  → retries spread across the 100ms-150ms window
  → each millisecond gets ~20 retries instead of 1,000
  → node can handle this easily
```

```
Without jitter:     |||||||||| (all at once)
With jitter:        |  | |  | ||  | | |  (spread out)
```

The combination of exponential backoff and jitter transforms a synchronized retry storm into a smooth, manageable trickle of retries.

---

## All Three Defenses Together

```
Viral traffic spike hits the cluster:

1. Rate limiting (per node):
   → Each node caps at 6,000 req/sec
   → Excess requests instantly rejected with 503
   → Nodes stay alive and healthy

2. Circuit breaker (coordinator):
   → If a node starts failing, coordinator stops sending it traffic
   → Node gets breathing room to recover
   → Traffic routes to healthy nodes

3. Exponential backoff + jitter (client):
   → Rejected requests retry with increasing delays
   → Random jitter prevents synchronized retry storms
   → Retries spread out into a manageable trickle

Together: the spike is absorbed, not amplified.
  → Nodes stay alive (rate limiting)
  → Struggling nodes get relief (circuit breaker)  
  → Retries don't create new spikes (backoff + jitter)
```

> [!tip] Interview framing
> "Cascading failures happen when one overloaded node crashes, shifting load to neighbors who then crash too — a domino effect. Our first defense is vnodes: when a node dies, its load spreads across dozens of nodes instead of two neighbors, so the extra load per node is tiny. For traffic spikes where all nodes are overwhelmed, we have three layers: rate limiting per node (reject excess requests with 503 instead of crashing), circuit breakers at the coordinator (stop sending traffic to a struggling node so it can recover), and exponential backoff with jitter at the client (spread retries over time to prevent thundering herd). The principle is: it's better to reject some requests than to crash and reject all requests."
