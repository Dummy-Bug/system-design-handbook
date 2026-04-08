# Sequential Writes and Page Cache

> [!info] Kafka stores everything on disk — yet handles millions of events per second. This seems contradictory until you understand two things: sequential writes are as fast as memory writes, and the OS page cache means recent reads never touch disk at all.

---

## "Disk is slow" — the wrong mental model

When people say disk is slow, they mean **random writes** — where the disk head has to physically seek to different locations to write scattered data. That's slow.

```
Random write:
Disk head at position 1000 → seek to position 50000 → write
                           → seek to position 3000  → write
                           → seek to position 80000 → write
Each seek = milliseconds of latency
~100–200 MB/sec throughput on HDD
```

Kafka never does this. It only ever **appends to the end of a file** — the disk head never moves backward.

```
Sequential write:
Disk head at position 1000 → write → position 1001
                           → write → position 1002
                           → write → position 1003
No seeking. Ever.
~600–700 MB/sec on HDD, 3–4 GB/sec on SSD
```

This is the same reason LSM trees in Cassandra are fast for writes — always sequential, never random. Sequential disk I/O approaches RAM speeds on modern hardware.

---

## The OS page cache

When the OS writes data to disk, it doesn't immediately flush it. It keeps a copy in RAM — this is called the **page cache**. It's automatic, managed by the OS, and exists on every Linux machine.

When Kafka appends a new event:

```mermaid
sequenceDiagram
    participant P as Producer
    participant K as Kafka
    participant PC as Page Cache (RAM)
    participant D as Disk

    P->>K: send click event
    K->>PC: write to page cache
    PC->>D: OS flushes to disk (async, sequential)
    K->>P: ACK producer
```

The write is acknowledged after hitting the page cache — not after hitting disk. The OS handles the actual disk flush asynchronously in the background. This makes writes feel like memory writes to Kafka.

---

## The full read flow

**Case 1 — Consumer reading recent events (common case)**

```mermaid
sequenceDiagram
    participant C as Consumer
    participant K as Kafka
    participant PC as Page Cache (RAM)
    participant D as Disk

    C->>K: give me events from offset 1000
    K->>PC: check page cache
    PC->>K: found in RAM (recently written)
    K->>C: return events directly from RAM
    Note over D: disk never touched
```

Recent events are almost always in the page cache because they were just written there. A consumer reading in real-time is effectively reading from RAM.

**Case 2 — Consumer replaying old events**

```mermaid
sequenceDiagram
    participant C as New ML Service
    participant K as Kafka
    participant PC as Page Cache (RAM)
    participant D as Disk

    C->>K: give me events from offset 0 (30 days ago)
    K->>PC: check page cache
    PC->>K: not in RAM (too old, evicted)
    K->>D: sequential read from disk
    D->>K: returns events (fast — sequential)
    K->>C: return events
```

Old events not in page cache are read sequentially from disk — still fast because Kafka never needs to seek.

---

## Why this matters at scale

```
100,000 events/sec written to Kafka
→ All land in page cache first (RAM write speed)
→ OS flushes sequentially to disk in background
→ Consumers reading recent events → served from RAM
→ Consumers replaying history → served by sequential disk read
→ No random I/O anywhere in the system
```

> [!important] Kafka deliberately avoids managing its own cache. It relies entirely on the OS page cache — which is already highly optimised and shared across processes. This keeps Kafka's own memory footprint small and lets the OS do what it's best at.

> [!tip] **Interview framing:** "Kafka is disk-based but fast because it only ever does sequential writes — appending to the end of a log file. The OS page cache means recent reads are served from RAM. Old reads are sequential disk reads. There's no random I/O anywhere, which is why it sustains millions of events per second on commodity hardware."
