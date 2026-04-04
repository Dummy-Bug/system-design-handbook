# Redis Patterns

---

## Distributed Lock

Multiple servers run the same background job — send email digests, process a payment, clean up expired sessions. Without coordination, every server picks up the same job simultaneously.

```mermaid
flowchart LR
    subgraph NoLock["Without Lock"]
        S1["Server 1 picks up payment job<br/>starts processing"]
        S2["Server 2 picks up payment job<br/>starts processing"]
        S1 & S2 --> R["Payment charged twice ✗"]
        style R fill:#f8d7da,stroke:#dc3545,color:#000
    end
```

You need only one server to run the job at a time. That's a distributed lock.

**How Redis does it:**

```
SET lock:payment:123 "server1" NX PX 5000
```

```
NX       → only set if key does NOT exist
PX 5000  → auto-expire after 5000ms

→ key doesn't exist: set it, return OK   → you got the lock
→ key already exists: do nothing, nil    → someone else has it, skip
```

```mermaid
flowchart LR
    A["SET lock:payment:123 NX PX 5000"]
    A -->|"key doesn't exist → OK"| B["Server 1 got the lock ✓<br/>process payment"]
    A -->|"key exists → nil"| C["Server 2 skipped ✓<br/>lock already taken"]
    style B fill:#d4edda,stroke:#28a745,color:#000
    style C fill:#fff3cd,stroke:#ffc107,color:#000
```

**Why the expiry?**

Server 1 gets the lock then crashes mid-job:

```mermaid
flowchart LR
    subgraph NoExpiry["Without PX 5000"]
        A["Server 1 crashes"] --> B["lock:payment:123 stays forever"]
        B --> C["No server can ever process this payment ✗<br/>stuck forever"]
        style C fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph WithExpiry["With PX 5000"]
        D["Server 1 crashes"] --> E["Lock auto-releases after 5 seconds"]
        E --> F["Next server picks it up and processes ✓"]
        style F fill:#d4edda,stroke:#28a745,color:#000
    end
```

---

## Rate Limiter

Limit each user to 100 API requests per minute.

---

### Fixed Window — INCR + EXPIRE

```
User makes a request
→ INCR rate:user:123:2026-04-04-14:01   ← key includes current minute
→ if count == 1 → EXPIRE key 60s        ← start timer on first request
→ if count > 100 → reject
```

```mermaid
flowchart LR
    A["14:00:00 → count = 1<br/>EXPIRE 60s set"] --> B["14:00:30 → count = 50 ✓"]
    B --> C["14:00:59 → count = 100 ✓"]
    C --> D["14:01:00 → count = 101 → rejected ✗"]
    D --> E["14:01:01 → new key<br/>count resets to 1 ✓"]
    style D fill:#f8d7da,stroke:#dc3545,color:#000
    style E fill:#d4edda,stroke:#28a745,color:#000
```

Simple — one integer key per user per minute. Resets automatically when key expires.

**The boundary problem:**

```mermaid
flowchart LR
    A["14:00:50 → 100 requests<br/>all allowed ✓ (window 1)"] --> B["14:01:10 → 100 requests<br/>all allowed ✓ (window 2)"]
    B --> C["200 requests in 20 seconds<br/>limit is supposed to be 100/min ✗"]
    style C fill:#f8d7da,stroke:#dc3545,color:#000
```

The window only asks "how many in this bucket?" — not "how many in the last 60 seconds?". At the boundary, a user can double their limit by straddling two windows.

---

### Sliding Window — Sorted Set

Track the timestamp of every request. Always look at the last 60 seconds from right now.

```
now = current timestamp in ms

ZADD rate:user:123 now "req:unique-id"          ← add this request (score = timestamp)
ZREMRANGEBYSCORE rate:user:123 0 (now - 60000)  ← remove requests older than 60s
count = ZCARD rate:user:123                     ← how many in last 60s?
if count > 100 → reject
```

No boundary problem — window slides with every request:

```mermaid
flowchart LR
    A["T=14:00:50<br/>user fires 100 requests"] --> B["T=14:01:10<br/>user tries another request"]
    B --> C["Sliding window checks:<br/>'how many between 14:00:10 and 14:01:10?'"]
    C --> D["Those 100 requests from 14:00:50<br/>are still inside the window"]
    D --> E["count = 100 → rejected ✗ correctly"]
    style E fill:#d4edda,stroke:#28a745,color:#000
```

**Fixed Window vs Sliding Window:**

```mermaid
flowchart LR
    subgraph Fixed["Fixed Window"]
        F1["1 integer key per user per minute<br/>tiny memory ✓<br/>boundary exploit possible ✗"]
        style F1 fill:#fff3cd,stroke:#ffc107,color:#000
    end
    subgraph Sliding["Sliding Window"]
        S1["1 sorted set entry per request<br/>more memory ✗<br/>exact accuracy ✓"]
        style S1 fill:#d4edda,stroke:#28a745,color:#000
    end
```

---

## Redis Sentinel

One Redis primary goes down — all cache reads and writes fail — every request falls through to DB — DB collapses.

**Sentinel** is a monitoring process that watches your Redis primary and automatically promotes a replica when the primary dies.

```mermaid
flowchart LR
    subgraph Normal["Normal State"]
        SN["Sentinel<br/>watching"] --> PN["Primary"]
        PN -->|"replicates"| R1N["Replica 1"]
        PN -->|"replicates"| R2N["Replica 2"]
        style PN fill:#d4edda,stroke:#28a745,color:#000
    end
    subgraph Failover["Primary Dies"]
        SF["Sentinels detect failure<br/>majority vote"] --> PF["Replica 1 promoted<br/>to Primary ✓"]
        PF -->|"replicates"| R2F["Replica 2 now follows<br/>new primary"]
        SF --> APP["App told new<br/>primary address"]
        style PF fill:#d4edda,stroke:#28a745,color:#000
    end
```

Your app doesn't talk to Redis directly — it asks Sentinel "who is the current primary?" and Sentinel points it to the right node.

**Why majority vote?**

If one Sentinel loses its network connection to the primary, it might think the primary is dead when it's actually fine. Requiring a majority prevents a single Sentinel from triggering a false failover.

**The unavoidable gap:**

```mermaid
flowchart LR
    A["Primary dies"] --> B["Sentinels detect"] --> C["Majority vote"] --> D["Promote replica"] --> E["App reconnects"]
    B2["~10–30 seconds of Redis unavailable<br/>every cache read fails → DB gets burst traffic"]
    A --> B2
    style B2 fill:#fff3cd,stroke:#ffc107,color:#000
    style E fill:#d4edda,stroke:#28a745,color:#000
```

During that window every cache read fails and requests hit DB. This is an accepted trade-off — Sentinel minimises the window but doesn't eliminate it.

---

## Redis Cluster

Sentinel handles failover — what happens when a node dies.
Cluster handles sharding — what happens when data is too big for one node.

```mermaid
flowchart LR
    A["One Redis node<br/>~64GB RAM limit"] --> B["1 billion users × 1KB profile<br/>= 1TB of data"]
    B --> C["Doesn't fit on one node ✗"]
    style C fill:#f8d7da,stroke:#dc3545,color:#000
```

Redis Cluster splits data across multiple nodes automatically using **key slots** (0–16383):

```mermaid
flowchart LR
    subgraph Cluster["Redis Cluster"]
        N1["Node 1<br/>slots 0 → 5460"]
        N2["Node 2<br/>slots 5461 → 10922"]
        N3["Node 3<br/>slots 10923 → 16383"]
    end
    A["SET user:123:profile"] -->|"hashes to slot 5432"| N1
    B["SET user:456:profile"] -->|"hashes to slot 7891"| N2
    style N1 fill:#d4edda,stroke:#28a745,color:#000
    style N2 fill:#d4edda,stroke:#28a745,color:#000
    style N3 fill:#d4edda,stroke:#28a745,color:#000
```

Your app doesn't need to know which node holds which key — the cluster handles routing. Each node also has its own replicas for failover, so you get sharding and availability together.

**Sentinel vs Cluster:**

```mermaid
flowchart LR
    subgraph Sentinel["Sentinel"]
        S1["One primary + replicas<br/>automatic failover on failure<br/>data fits on one node"]
        style S1 fill:#fff3cd,stroke:#ffc107,color:#000
    end
    subgraph Cluster["Cluster"]
        C1["Many primaries<br/>data sharded across them<br/>each primary has its own replicas"]
        style C1 fill:#d4edda,stroke:#28a745,color:#000
    end
```
