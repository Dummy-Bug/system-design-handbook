## Assumptions

```
New keys per day:       1B (1 billion new key-value pairs written daily)

Key size:               16 bytes (string key)
Value size:             1 KB (opaque byte blob — store doesn't parse it)

Total per record:       ~1 KB (key + metadata are negligible vs value)

Read:write ratio:       10:1 (read-heavy, but not as extreme as URL Shortener)

Peak multiplier:        3× (infrastructure has smoother traffic than consumer apps)

Retention:              10 years (data stored permanently, planning horizon of 10 years)

Replication factor:     3 (standard for durability in distributed DBs)
```

**Why 1 KB for value size?**
Most KV store use cases — user profiles, session data, feature flags, IoT readings — produce small values. DynamoDB caps items at 400 KB, but the average item is well under 1 KB. Using 1 KB is a defensible, commonly used assumption in interviews.

**Why 10:1 read:write ratio?**
A KV store serving something like user profiles or config data gets read far more than it gets updated. 10:1 is moderate — not as extreme as a URL Shortener (1000:1) because KV stores also serve write-heavy workloads. If the interviewer says "optimize for writes," you'd flip this closer to 1:1.

**Why 3× peak, not 10×?**
A general-purpose KV store is infrastructure — many services hit it with relatively smooth traffic patterns. A 10× spike makes sense for consumer apps (WhatsApp on New Year's Eve), but infrastructure behind a load balancer across many services smooths out individual spikes. 3× is the standard multiplier.

---

## QPS

```
Writes/day:        1B
Avg write QPS:     1B / 86,400 ≈ ~11.5K → round to 10K writes/sec

Peak write QPS:    10K × 3 = 30K writes/sec

Avg read QPS:      10K × 10 = 100K reads/sec
Peak read QPS:     100K × 3 = 300K reads/sec
```

At 300K peak reads/sec, a single machine can't handle this — even a well-tuned server tops out around 50K–100K simple reads/sec. This immediately tells us we need multiple nodes handling reads, which means partitioning (consistent hashing) and replication.

At 30K peak writes/sec, a single machine also can't keep up with durable disk writes at this rate. Writes need to be distributed across nodes too. 

---

## Storage

```
Data per day:          1B × 1 KB = 1 TB/day
Data per year:         1 TB × 365 ≈ 400 TB/year (rounded up)
10-year total (raw):   400 TB × 10 = 4 PB

With 3× replication:   4 PB × 3 = 12 PB total storage
```

**12 PB is massive.** If a single machine holds 10 TB of data comfortably, we need:

```
12 PB / 10 TB = 1,200 machines (just for storage)
```

This means consistent hashing and automatic data partitioning aren't optional — they're the only way to manage data placement across 1,200+ nodes. You can't manually assign which key goes where. The ring does it for you, and virtual nodes (vnodes) keep the distribution even.

---

## Bandwidth

```
Reads (peak):
  300K/sec × 1 KB = 300 MB/s × 8 = 2.4 Gbps

Writes (peak):
  30K/sec × 1 KB = 30 MB/s × 8 = 240 Mbps
```

2.4 Gbps peak read bandwidth is well within a standard 10 Gbps NIC (and this is spread across many nodes, not a single machine). Bandwidth is not a bottleneck for this system.

---

## Summary

```
Avg write QPS:      10K/sec     | Peak: 30K/sec
Avg read QPS:       100K/sec    | Peak: 300K/sec
Read:write ratio:   10:1

Storage (10 yrs):   4 PB raw → 12 PB with replication
Nodes needed:       ~1,200+ (at 10 TB per machine)

Peak bandwidth:     2.4 Gbps reads, 240 Mbps writes → not a bottleneck
```

---

## Architecture decisions this forces

```
300K peak reads/sec     → single node can't serve this — must partition reads
                          across nodes (consistent hashing + replication)

30K peak writes/sec     → single node can't absorb this — need distributed
                          writes with LSM Tree (memtable absorbs bursts)

12 PB total storage     → ~1,200 nodes minimum — consistent hashing with
                          vnodes for automatic data placement

1 KB value size         → small enough to store inline (no separate blob store
                          needed, unlike Pastebin's 10 KB pastes)
```

---

> [!tip] Interview framing
> "1 billion new keys per day, 1 KB average value size. 10:1 read:write ratio gives us 10K writes/sec and 100K reads/sec average — 30K and 300K at 3× peak. Over 10 years with 3× replication, that's 12 PB — about 1,200 machines at 10 TB each. Bandwidth is 2.4 Gbps peak reads, well within modern NICs. The key takeaway: at this scale, consistent hashing for partitioning and LSM Trees for write throughput aren't optional — they're survival requirements."
