## Option 2 — Multi-Leader

### How it works

Multiple nodes can accept writes for the same data — each one is a "leader." Unlike single-leader where writes funnel through one node, multi-leader lets writes go to any of the leaders independently. The leaders sync with each other **after the fact**, asynchronously.

```
Write path:
  Client in US     → Leader A (US)     → ack immediately → sync to Leader B later
  Client in Europe → Leader B (Europe) → ack immediately → sync to Leader A later

Each leader accepts writes locally without waiting for the other.
```

This is mainly designed for **multi-region deployments**. You put a leader in each region so users get low-latency writes to their local datacenter instead of crossing the ocean for every request.

### The conflict problem

Since multiple leaders accept writes independently, two clients can write to the **same key** at the same time on different leaders:

```
Leader A: put("user:123", "Alice")  → ack to client → success
Leader B: put("user:123", "Bob")    → ack to client → success

Both writes succeed. Both clients think they won.
Later, Leader A and Leader B sync and discover: two different values for "user:123."
```

This is a **write conflict** — and it's the fundamental cost of multi-leader. It doesn't exist in single-leader (because all writes go through one node, so they're naturally ordered).

### How do you resolve conflicts?

**Option A — Last Write Wins (LWW)**

Pick the write with the later timestamp. Simple, but dangerous.

The problem is clock drift — something we studied in the Distributed Clocks topic. Leader A's clock says 12:00:00.000, Leader B's clock says 12:00:00.050. If the "real" order was Leader B first then Leader A, but Leader B's clock is ahead, LWW picks the **wrong winner**. A perfectly valid write gets silently dropped. The client got a success ack, but their data is gone.

For some use cases this is acceptable — a user profile update where Alice vs Bob doesn't matter much. For others it's catastrophic — imagine both writes are updating an account balance. One update silently vanishes.

**Option B — Vector Clocks (detect conflict, let client resolve)**

Instead of picking a winner automatically, the system detects the conflict using vector clocks and stores **both versions**. On the next read, it returns both to the client: "these two writes conflicted, you decide which one to keep."

This is what DynamoDB originally did with its shopping cart — if two items were added concurrently from different devices, it kept both and merged them on the next read.

The downside: complexity is pushed to the client. Every client application needs conflict resolution logic. For a general-purpose KV store used by hundreds of different services, that's a heavy burden — every team using your store needs to understand and implement conflict handling.

### Why we reject it

Our system is **single-region**. All 1,200 nodes are in the same datacenter with sub-millisecond network latency between them.

Multi-leader's entire value proposition is **low-latency writes in multiple regions** — a leader in US, a leader in Europe, so no one crosses the ocean. In a single region, every node is already close to every other node. There's no latency problem to solve.

But you still pay the full cost:
- Conflict detection and resolution on every concurrent write
- Silent data loss with LWW, or client-side complexity with vector clocks
- More complex replication (leaders syncing bidirectionally instead of one-way)

All this complexity for **zero benefit** when all your nodes are in the same datacenter.

```
Multi-leader rejection:

  ✓ Multiple nodes accept writes — no single point of failure for writes
  ✓ Great for multi-region — low-latency local writes per region
  ✗ Concurrent writes to same key → conflicts are inevitable
  ✗ LWW → silent data loss from clock skew
  ✗ Vector clocks → pushes resolution complexity to every client
  ✗ We're single-region — multi-leader adds complexity for zero latency benefit
  ✗ Will revisit when we scale to Google-scale multi-region deployment
```

> [!important] Multi-leader isn't bad — it's just wrong for this context
> If the interviewer says "now make this work across US, Europe, and Asia," multi-leader becomes a serious contender. The rejection is about our current single-region scope, not about multi-leader as a concept.

---

> [!tip] Interview framing
> "Multi-leader is designed for multi-region — a leader in each datacenter so writes don't cross the ocean. We're single-region, so there's no latency benefit. But we'd still pay the full cost: concurrent writes to the same key cause conflicts. LWW silently drops writes due to clock skew. Vector clocks push conflict resolution to every client application. That's too much complexity for zero gain in a single-region deployment. If the interviewer pushes us to multi-region later, we'd revisit this."
