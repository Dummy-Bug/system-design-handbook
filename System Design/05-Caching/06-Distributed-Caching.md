# Distributed Caching

## Why Single Node Doesn't Scale

> [!info] Single cache node has two fundamental problems at scale.

```mermaid
flowchart LR
    A["Single Cache Node"] --> B["Memory Limit<br/>10M users × 10KB = 100GB<br/>doesn't fit on one node"]
    A --> C["SPOF<br/>node goes down → entire cache gone<br/>all requests hit DB → DB collapses"]
    style B fill:#f8d7da,stroke:#dc3545,color:#000
    style C fill:#f8d7da,stroke:#dc3545,color:#000
```

Solution: distribute the cache across multiple nodes.

New problem: a request comes in for `user:123:profile` — which node do you go to?

---

## Consistent Hashing

> [!info] Hash keys to nodes on a ring. Adding/removing nodes only affects neighbouring keys — not the entire keyspace.

**Why not simple modulo hashing:**

```mermaid
flowchart LR
    A["hash('user:123') % 10 = 7<br/>→ node 7 ✓"] --> B["Add 1 node"]
    B --> C["hash('user:123') % 11 = 3<br/>→ node 3 ✗"]
    C --> D["~90% of all keys<br/>map to different nodes"]
    D --> E["Mass cache miss<br/>→ DB collapses"]
    style C fill:#f8d7da,stroke:#dc3545,color:#000
    style D fill:#f8d7da,stroke:#dc3545,color:#000
    style E fill:#f8d7da,stroke:#dc3545,color:#000
```

**Consistent hashing — before adding a node:**

```mermaid
flowchart LR
    A["Node A"] -->|"keys A→B owned by B"| B["Node B"]
    B -->|"keys B→C owned by C"| C["Node C"]
    C -->|"keys C→A owned by A"| A
```

**After adding Node D between B and C:**

```mermaid
flowchart LR
    A["Node A"] -->|"keys A→B owned by B"| B["Node B"]
    B -->|"keys B→D owned by D"| D["Node D ✨ new"]
    D -->|"keys D→C owned by C"| C["Node C"]
    C -->|"keys C→A owned by A"| A
    style D fill:#fff3cd,stroke:#ffc107,color:#000
```

Only the slice D takes over from C is remapped. Everything else untouched.

**Virtual nodes:** each physical node gets multiple positions on the ring for even distribution. Prevents hot spots when nodes have different capacities.

> [!tip] Interview answer: "I'd use consistent hashing so adding or removing cache nodes only remaps a minimal fraction of keys — roughly 1/N of the keyspace — instead of causing a mass cache miss."

---

## Cache Coherence

> [!info] Multiple nodes or replicas can hold different values for the same key. This is cache coherence — keeping them in sync.

```mermaid
flowchart LR
    W["Write"] --> P["Primary Node 7<br/>updated ✓"]
    W -.->|"not yet updated"| R1["Replica 7a<br/>old value ✗"]
    W -.->|"not yet updated"| R2["Replica 7b<br/>old value ✗"]
    R1 --> S["Next read hits Replica 7a<br/>→ stale data returned"]
    style R1 fill:#f8d7da,stroke:#dc3545,color:#000
    style R2 fill:#f8d7da,stroke:#dc3545,color:#000
    style S fill:#f8d7da,stroke:#dc3545,color:#000
```

**Solutions:**

```mermaid
flowchart LR
    subgraph Sync["Sync Replication"]
        S1["Write"] --> S2["Update all replicas"]
        S2 --> S3["Confirm success"]
        S3 --> S4["Consistent ✓<br/>but slower writes"]
        style S4 fill:#fff3cd,stroke:#ffc107,color:#000
    end
    subgraph Async["Async Replication — most caches use this"]
        A1["Write"] --> A2["Confirm after primary"]
        A2 --> A3["Replicas catch up later<br/>(milliseconds)"]
        A3 --> A4["Faster writes ✓<br/>brief staleness window"]
        style A4 fill:#d4edda,stroke:#28a745,color:#000
    end
```

**Simpler approach — primary reads:**

```mermaid
flowchart LR
    W["Writes"] --> P["Primary"]
    R["Reads"] --> P
    P -.->|"failover only"| Rep["Replicas<br/>not serving reads"]
    style Rep fill:#fff3cd,stroke:#ffc107,color:#000
```

Clean, no coherence issue. Works until scale gets huge.

**At massive scale:**

```mermaid
flowchart LR
    A["Small scale"] -->|"read from primary"| B["Strong consistency<br/>simple ✓"]
    C["Massive scale"] -->|"read from replicas"| D["Eventual consistency<br/>lower latency ✓"]
    style B fill:#d4edda,stroke:#28a745,color:#000
    style D fill:#fff3cd,stroke:#ffc107,color:#000
```

> [!important] Same trade-off as databases — CAP/PACELC applies to the cache layer too. No free lunch.

---

## Replication

> [!info] Read replicas serve two purposes — availability and read throughput.

```mermaid
flowchart LR
    subgraph Availability["Availability"]
        A1["Primary goes down"] --> A2["Replica promotes"] --> A3["Cache stays up ✓"]
        style A3 fill:#d4edda,stroke:#28a745,color:#000
    end
    subgraph Throughput["Read Throughput"]
        T1["Read load"] --> T2["Spread across replicas"]
        T2 --> T3["Primary not bottlenecked ✓"]
        style T3 fill:#d4edda,stroke:#28a745,color:#000
    end
```

**Replication lag:** async replication means replicas are slightly behind primary. Acceptable for most cache data — a few milliseconds of staleness.

---

## Two-Level Caching (L1 + L2)

> [!info] Local in-process cache (L1) + distributed Redis cache (L2). Best of both worlds.

```mermaid
flowchart TD
    R["Request comes in"] --> L1{"L1 hit?<br/>local, nanoseconds"}
    L1 -->|"hit"| RET1["Return immediately ✓"]
    L1 -->|"miss"| L2{"L2 hit?<br/>Redis, ~1ms"}
    L2 -->|"hit"| STORE1["Store in L1<br/>Return ✓"]
    L2 -->|"miss"| DB["Hit DB ~10ms+"]
    DB --> STORE2["Store in L2 + L1<br/>Return ✓"]
    style RET1 fill:#d4edda,stroke:#28a745,color:#000
    style STORE1 fill:#d4edda,stroke:#28a745,color:#000
    style STORE2 fill:#fff3cd,stroke:#ffc107,color:#000
```

```mermaid
flowchart LR
    A["L1 — local<br/>nanoseconds<br/>per-server only<br/>inconsistency risk"] -->|"miss"| B["L2 — Redis<br/>~1ms<br/>shared across all servers<br/>consistent"] -->|"miss"| C["DB<br/>~10ms+<br/>source of truth"]
    style A fill:#d4edda,stroke:#28a745,color:#000
    style B fill:#fff3cd,stroke:#ffc107,color:#000
    style C fill:#f8d7da,stroke:#dc3545,color:#000
```

Used by Instagram, Twitter, and most large-scale systems in production.

**L1 invalidation problem:** when data changes in Redis, local caches on each server still have the old value.

```mermaid
flowchart LR
    subgraph Sol1["Short TTL on L1"]
        S1["L1 entry expires quickly"] --> S2["Stale for at most TTL duration<br/>simple ✓"]
        style S2 fill:#d4edda,stroke:#28a745,color:#000
    end
    subgraph Sol2["Pub/Sub Invalidation"]
        P1["Data changes in Redis"] --> P2["Redis publishes invalidation event"]
        P2 --> P3["All servers subscribe<br/>→ clear L1 immediately ✓"]
        style P3 fill:#d4edda,stroke:#28a745,color:#000
    end
```

---

## Handling Node Failure

> [!info] Consistent hashing minimises the blast radius when a node fails.

```mermaid
flowchart LR
    subgraph NoReplicas["Without Replicas"]
        A1["Node 7 goes down"] --> A2["Keys routed to next node on ring"]
        A2 --> A3["Temporary cache misses"]
        A3 --> A4["Gradually repopulate<br/>rest of cluster unaffected ✓"]
        style A3 fill:#fff3cd,stroke:#ffc107,color:#000
        style A4 fill:#d4edda,stroke:#28a745,color:#000
    end
    subgraph WithReplicas["With Replicas"]
        B1["Primary fails"] --> B2["Replica promotes to primary"]
        B2 --> B3["No cache miss at all ✓<br/>seamless failover"]
        style B3 fill:#d4edda,stroke:#28a745,color:#000
    end
```

---

## Summary

| Concept | What it does | When to use |
|---|---|---|
| Consistent hashing | Minimal key remapping on node add/remove | Always |
| Cache coherence | Keep replicas in sync — async for speed, primary reads for simplicity | Whenever you have replicas |
| Replication | Availability + read throughput | Any production cache |
| Two-level caching | L1 local (nanoseconds) + L2 Redis (~1ms) | High-traffic systems |
| Node failure handling | Consistent hashing limits blast radius, replicas give seamless failover | Always |
