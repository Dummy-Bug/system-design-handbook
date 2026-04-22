# Cache Replication

> [!info] Read replicas serve two purposes — availability and read throughput. The trade-off is replication lag.

---

## Why replicate the cache

**Availability:**
```
Primary cache node goes down
Without replication: entire cache gone → all requests hit DB → DB collapses
With replication:    replica promotes → cache stays up → DB protected ✓
```

**Read throughput:**
```
10,000 cache reads/second on one node → node CPU saturated
With 3 replicas: ~3,333 reads/second each → headroom restored ✓
Primary not bottlenecked, replicas absorb read load
```

---

## Replication lag

With async replication (the default), replicas are slightly behind the primary. For cache data, this is almost always acceptable:

```
User updates setting → primary updated → replica 50ms behind
→ user's next read might hit replica → sees old value for 50ms
→ invisible to the user in practice
```

The same read-your-own-writes issue exists here as in DB replication. The same fix applies: route a user's reads to the primary for a short window after they write.

---

## Redis-specific replication

**Redis Sentinel** — monitors primary, auto-promotes a replica on failure:
```
Primary dies → Sentinel detects after ~10s → promotes best replica → redirects clients
~10-30 second failover window ← brief cache miss period
```

**Redis Cluster** — sharding + replication together:
```
Keyspace divided into 16,384 hash slots
Each slot group has a primary + replicas
Reads/writes route to the correct slot group automatically
Node failure → slot group's replica promotes → minimal disruption
```

> [!tip] Interview answer
> "I'd run Redis with at least one replica per node. Redis Sentinel handles automatic failover — if the primary dies, Sentinel promotes a replica within 10-30 seconds. During that window the cache is unavailable for that key range, but the system can fall back to the DB."
