# Redis Persistence

> [!info] Redis is RAM. RAM is wiped on crash or restart. Persistence is how Redis saves its data to disk so it can recover — not for querying like a real DB, just for crash recovery.

```mermaid
flowchart LR
    subgraph Without["Without Persistence"]
        A1["Redis crashes"] --> A2["Restarts → all keys gone"] --> A3["Cold start<br/>every request is a cache miss"] --> A4["DB collapses ✗"]
        style A4 fill:#f8d7da,stroke:#dc3545,color:#000
    end
    subgraph With["With Persistence"]
        B1["Redis crashes"] --> B2["Restarts → loads data from disk"] --> B3["Warm cache restored<br/>DB never sees the spike ✓"]
        style B3 fill:#d4edda,stroke:#28a745,color:#000
    end
```

Disk is only touched on crash recovery. Normal reads and writes still go to RAM — persistence doesn't slow down your cache.

---

## RDB — Periodic Snapshots

Every N minutes, Redis takes a full snapshot of everything in memory and writes it to disk.

```mermaid
flowchart LR
    A["T=0min<br/>snapshot saved"] --> B["T=5min<br/>snapshot saved"] --> C["T=7min<br/>Redis crashes ✗"]
    C --> D["On restart:<br/>loads snapshot from T=5min"]
    D --> E["2 minutes of writes lost ⚠️"]
    style C fill:#f8d7da,stroke:#dc3545,color:#000
    style E fill:#fff3cd,stroke:#ffc107,color:#000
    style D fill:#d4edda,stroke:#28a745,color:#000
```

**What's good:**

```mermaid
flowchart LR
    subgraph Good["RDB strengths"]
        A["Small file<br/>compact binary snapshot"]
        B["Fast restart<br/>load one file, done"]
        C["Low overhead<br/>snapshot runs in background<br/>doesn't block reads/writes"]
    end
    style A fill:#d4edda,stroke:#28a745,color:#000
    style B fill:#d4edda,stroke:#28a745,color:#000
    style C fill:#d4edda,stroke:#28a745,color:#000
```

**What's bad:**

```mermaid
flowchart LR
    subgraph Bad["RDB weakness"]
        A["Data loss<br/>always lose writes since last snapshot<br/>not suitable where even 1 min loss is unacceptable"]
    end
    style A fill:#f8d7da,stroke:#dc3545,color:#000
```

---

## AOF — Append Only File

Every write command gets logged to a file on disk immediately.

```mermaid
flowchart LR
    A["SET user:123 'John'<br/>→ appended to file"] --> B["INCR page:views<br/>→ appended to file"] --> C["ZADD leaderboard 9500<br/>→ appended to file"]
    C --> D["Redis crashes"]
    D --> E["Replay every command from log<br/>→ full recovery ✓<br/>almost zero data loss"]
    style D fill:#f8d7da,stroke:#dc3545,color:#000
    style E fill:#d4edda,stroke:#28a745,color:#000
```

**What's good:**

```mermaid
flowchart LR
    subgraph Good["AOF strengths"]
        A["Durable<br/>logs every write, minimal data loss"]
        B["Configurable sync<br/>flush every command, every second,<br/>or let OS decide"]
    end
    style A fill:#d4edda,stroke:#28a745,color:#000
    style B fill:#d4edda,stroke:#28a745,color:#000
```

**What's bad:**

```mermaid
flowchart LR
    subgraph Bad["AOF weaknesses"]
        A["Large file<br/>every command logged, grows forever"]
        B["Slow restart<br/>replaying thousands of commands takes time"]
    end
    style A fill:#f8d7da,stroke:#dc3545,color:#000
    style B fill:#f8d7da,stroke:#dc3545,color:#000
```

---

## Hybrid — RDB + AOF Together

```mermaid
flowchart LR
    A["Redis crashes"] --> B["Load RDB snapshot<br/>restore base state quickly ✓"]
    B --> C["Replay only AOF entries<br/>since the last snapshot"]
    C --> D["Faster than full AOF replay ✓<br/>More durable than RDB alone ✓"]
    style B fill:#d4edda,stroke:#28a745,color:#000
    style C fill:#fff3cd,stroke:#ffc107,color:#000
    style D fill:#d4edda,stroke:#28a745,color:#000
```

This is what Redis recommends for production.

---

## Summary

| Mode | How it works | Restart speed | File size | Data loss risk |
|---|---|---|---|---|
| RDB | Snapshot every N minutes | Fast | Small | Up to N minutes |
| AOF | Log every write | Slow | Large | Near zero |
| Hybrid | RDB for base + AOF for recent writes | Fast | Medium | Near zero — recommended for production |

> [!important] For most caching use cases, some data loss on crash is acceptable — cache is a copy of DB data anyway. RDB alone is often fine. Hybrid is for when you can't afford even a few minutes of cache miss after a restart.
