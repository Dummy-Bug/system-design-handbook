# Cache Invalidation

## The Problem

> [!info] DB has the truth. Cache has a copy. DB gets updated. Cache still has the old value. How do you keep them in sync?

> [!danger] "There are only two hard things in computer science: cache invalidation and naming things."
> The reason it's hard: cache doesn't automatically know when the DB changes. You have to tell it — or wait for time to expire it.

---

## TTL-Based Invalidation

> [!info] Set a timer. When it expires, the key is deleted. Next request fetches fresh from DB.

```mermaid
flowchart LR
    A["T=0s<br/>key cached"] --> B["T=300s<br/>key expires automatically"]
    B --> C["T=301s<br/>request comes in → cache miss"]
    C --> D["fetch from DB"]
    D --> E["repopulate cache<br/>serve fresh ✓"]
    style E fill:#d4edda,stroke:#28a745,color:#000
```

**What's good:**
- Simple — no extra infrastructure
- Works for most cases — slight staleness is acceptable for most data

**The blind spot:**

```mermaid
flowchart LR
    A["T=10s<br/>user updates profile in DB"] --> B["290 seconds of<br/>stale data served from cache"]
    B --> C["T=300s<br/>TTL finally expires"]
    style B fill:#f8d7da,stroke:#dc3545,color:#000
```

**Choosing TTL:**

```mermaid
flowchart LR
    A["News feed like count<br/>stale 30s is fine"] -->|"TTL = 30s"| X["✓"]
    B["User profile<br/>stale 5min is fine"] -->|"TTL = 300s"| Y["✓"]
    C["Bank balance<br/>stale 1s is not fine"] -->|"don't cache / TTL = 1s"| Z["⚠️"]
    style A fill:#d4edda,stroke:#28a745,color:#000
    style B fill:#d4edda,stroke:#28a745,color:#000
    style C fill:#fff3cd,stroke:#ffc107,color:#000
    style X fill:#d4edda,stroke:#28a745,color:#000
    style Y fill:#d4edda,stroke:#28a745,color:#000
    style Z fill:#fff3cd,stroke:#ffc107,color:#000
```

> [!tip] Always set a TTL as a safety net — even if you use other invalidation strategies. Prevents stale data from living forever if something goes wrong.

---

## Event-Driven Invalidation

> [!info] Invalidate the cache key the moment the DB is updated. No stale window.

```mermaid
flowchart LR
    A["User updates profile"] --> B["Write to DB"]
    B --> C["DELETE cache key<br/>user:123:profile"]
    C --> D["Next read → cache miss"]
    D --> E["Fetch fresh from DB"]
    E --> F["Repopulate cache ✓"]
    style F fill:#d4edda,stroke:#28a745,color:#000
```

**What's good:**
- Cache invalidated instantly — no stale window
- Reacts to DB changes, not just time

**What's bad:**
- Needs infrastructure — who triggers the invalidation?
- Delete → miss → repopulate — one slow request after every write

**How to trigger:**

```mermaid
flowchart TD
    W["DB Write"] --> A["App Code<br/>simplest — delete key after every DB write"]
    W --> B["CDC<br/>Debezium streams DB change events<br/>→ Kafka → cache consumer invalidates"]
    W --> C["Message Queue<br/>write service publishes event<br/>cache service consumes and deletes"]
```

---

## Write-Through as Invalidation

> [!info] Instead of deleting the key on write, update it. No miss after the write.

```mermaid
flowchart LR
    A["User updates profile"] --> B["Write to DB"]
    B --> C["Write new value to cache<br/>simultaneously"]
    C --> D["Next read → cache hit<br/>serves new value directly ✓"]
    style D fill:#d4edda,stroke:#28a745,color:#000
```

**Difference from event-driven:**

```mermaid
flowchart LR
    subgraph ED["Event-Driven"]
        E1["Write to DB"] --> E2["DELETE key"] --> E3["Next read = MISS"] --> E4["Repopulate from DB"]
        style E3 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph WT["Write-Through"]
        W1["Write to DB"] --> W2["UPDATE key"] --> W3["Next read = HIT ✓"]
        style W3 fill:#d4edda,stroke:#28a745,color:#000
    end
```

**What's good:**
- No cache miss after write — better for read-heavy systems
- Cache always consistent

**What's bad:**
- Write latency increases — must update both DB and cache synchronously

---

## Cache Versioning

> [!info] Instead of invalidating a key, change the key itself. Old keys expire naturally.

```mermaid
flowchart TD
    subgraph Write["On Update"]
        W1["user:123:profile:v1 exists"] --> W2["User updates bio"]
        W2 --> W3["Write user:123:profile:v2"]
        W2 --> W4["Set user:123:current-version = v2"]
        W1 --> W5["v1 untouched → expires via TTL"]
    end
    subgraph Read["On Read"]
        R1["Read request"] --> R2["Fetch user:123:current-version → v2"]
        R2 --> R3["Fetch user:123:profile:v2 → fresh data ✓"]
        style R3 fill:#d4edda,stroke:#28a745,color:#000
    end
```

**Where it really shines — CDNs:**

```mermaid
flowchart LR
    subgraph Bad["Push Invalidation — painful"]
        O1["Deploy new JS"] --> O2["Invalidate app.js on all CDN edges"]
        O2 --> O3["Slow to propagate (minutes)"]
        O2 --> O4["Some edges unreachable → inconsistent"]
        O2 --> O5["CDN charges per invalidation request"]
        style O3 fill:#f8d7da,stroke:#dc3545,color:#000
        style O4 fill:#f8d7da,stroke:#dc3545,color:#000
        style O5 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph Good["Versioned URL — sidesteps all of it"]
        N1["Deploy new JS"] --> N2["New URL: app.v2.js"]
        N2 --> N3["Brand new resource everywhere ✓"]
        N2 --> N4["Old URL expires naturally via TTL"]
        style N3 fill:#d4edda,stroke:#28a745,color:#000
        style N4 fill:#d4edda,stroke:#28a745,color:#000
    end
```

This is why production JS bundles look like `app.a3f9c2.js` — the hash IS the version.

**The hidden cost for DB-backed data — two cache lookups per read:**

```mermaid
flowchart LR
    subgraph Normal["Normal Cache Read"]
        A1["Read request"] --> A2["Fetch user:123:profile"]
        A2 --> A3["Done ✓ — 1 cache hit"]
        style A3 fill:#d4edda,stroke:#28a745,color:#000
    end
    subgraph Versioned["Versioned Cache Read"]
        B1["Read request"] --> B2["Fetch user:123:current-version → v2"]
        B2 --> B3["Fetch user:123:profile:v2 → data ✓<br/>2 cache hits minimum"]
        B2 --> B4["Version key miss?<br/>DB call to resolve → then cache lookup<br/>= 2 round trips before any data"]
        style B3 fill:#fff3cd,stroke:#ffc107,color:#000
        style B4 fill:#f8d7da,stroke:#dc3545,color:#000
    end
```

> [!danger] At scale this doubles cache round trips for every read. 10M reads/day becomes 20M cache calls. Latency adds up.

> [!tip] Cache versioning is best for CDN static assets. For DB-backed data, event-driven or write-through is simpler — the two-step version lookup adds unnecessary complexity.

---

## Stale-While-Revalidate

> [!info] TTL expires, request comes in — serve stale immediately, refresh in background. User never waits.

```mermaid
flowchart LR
    subgraph TTL["Normal TTL Expiry"]
        T1["Key expires"] --> T2["Cache miss"]
        T2 --> T3["User waits for DB fetch"]
        T3 --> T4["Slow response ⚠️"]
        style T4 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph SWR["Stale-While-Revalidate"]
        S1["Key expires"] --> S2["Serve stale immediately ✓"]
        S1 --> S3["Background: fetch fresh from DB"]
        S3 --> S4["Cache updated → next request fresh"]
        style S2 fill:#d4edda,stroke:#28a745,color:#000
    end
```

**Difference from refresh-ahead:**

```mermaid
flowchart LR
    subgraph RA["Refresh-Ahead — proactive"]
        R1["T=45s — key still alive"] --> R2["Background refresh fires"]
        R2 --> R3["T=60s — already fresh<br/>zero stale responses ✓"]
        style R3 fill:#d4edda,stroke:#28a745,color:#000
    end
    subgraph SWR2["Stale-While-Revalidate — reactive"]
        W1["T=60s — key expires"] --> W2["Request hits → serve stale ⚠️"]
        W2 --> W3["Background refresh fires"]
        W3 --> W4["Next request gets fresh ✓"]
        style W2 fill:#fff3cd,stroke:#ffc107,color:#000
        style W4 fill:#d4edda,stroke:#28a745,color:#000
    end
```

**Use when / Don't use when:**

```mermaid
flowchart LR
    subgraph OK["✅ Acceptable staleness"]
        A["News feed<br/>2 seconds stale = fine"]
        B["Type-ahead<br/>slightly stale suggestions = fine"]
        C["Leaderboard<br/>rank 5s ago = fine"]
    end
    subgraph NO["❌ Staleness not acceptable"]
        D["Bank balance<br/>stale even once = wrong"]
        E["Inventory<br/>stale count = overselling"]
    end
    style OK fill:#d4edda,stroke:#28a745,color:#000
    style NO fill:#f8d7da,stroke:#dc3545,color:#000
    style A fill:#c3e6cb,stroke:#28a745,color:#000
    style B fill:#c3e6cb,stroke:#28a745,color:#000
    style C fill:#c3e6cb,stroke:#28a745,color:#000
    style D fill:#f5c6cb,stroke:#dc3545,color:#000
    style E fill:#f5c6cb,stroke:#dc3545,color:#000
```

---

## The Full Picture

| Strategy | How it works | Stale window | Trade-off |
|---|---|---|---|
| TTL-based | Key auto-deletes after timer | Up to TTL duration | Simple — always use as safety net |
| Event-driven | Delete key on every DB write | None | Instant — needs infrastructure |
| Write-through | Update key on every DB write | None | No miss after write — slower writes |
| Cache versioning | Change the key, old expires naturally | None | Best for CDN — two lookups for DB-backed data |
| Stale-while-revalidate | Serve stale, refresh in background | One request | Great for feeds and type-ahead |

> [!important] Most production systems combine strategies:
> TTL as the safety net + event-driven for critical data + stale-while-revalidate for feeds.
> No single strategy fits everything — choose per data type.
