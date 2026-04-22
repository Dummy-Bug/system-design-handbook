
## Assumptions

```
MAU:                10M
DAU:                20% × 10M = 2M

Writes per DAU:     0.5 pastes/day  (occasional tool, not daily habit)

Read:write ratio:   100:1           (pastes are read many more times than created)

Peak multiplier:    3×              (Pastebin doesn't go viral — 3× is realistic)

Paste size:         ~10KB           (100 lines × 100 chars = 10,000 bytes)

Retention:          10 years
```

**Why 0.5 writes per DAU?**
Pastebin is a developer tool used occasionally — during debugging, sharing a config, sending a log snippet. The average active user creates a paste roughly once every two days, not multiple times daily. Contrast this with Twitter (multiple posts/day) or chat (dozens of messages/day). 0.5 is a conservative, defensible number.

**Why 100:1 read:write ratio?**
A paste gets shared via a link. One person creates it, many people read it — teammates, colleagues, people on a forum. The read traffic far outweighs creation traffic, similar to URL Shortener but less extreme (1000:1 there because URLs get tweeted and go viral; pastes are shared in smaller circles).

---

## QPS

```
Writes/day:       2M × 0.5 = 1M writes/day
Avg write QPS:    1M / 100,000 = 10 writes/sec
Peak write QPS:   10 × 3 = ~30 writes/sec

Avg read QPS:     10 × 100 = 1,000 reads/sec
Peak read QPS:    1,000 × 3 = ~3,000 reads/sec
```

At 3,000 peak read QPS, a single Postgres instance (10k–50k reads/sec) can handle this comfortably. But 10KB per paste means each read is heavier than a URL redirect — caching becomes important not just for throughput but for reducing DB I/O on large payloads.

---

## Storage

```
Writes/day:         1M
10-year total:      1M × 3,650 = 3.65B pastes

Per paste:          ~10KB (content) + ~100 bytes (metadata) ≈ 10KB
Raw storage:        3.65B × 10KB = 36.5TB
Replication (3×):   36.5 × 3 = ~110TB
Index overhead (1.3×): ~143TB

→ ~150TB for 10 years
```

**150TB crosses the sharding threshold.** A single Postgres machine handles ~10TB practically before ops becomes painful. At 150TB we need sharding — same conclusion as URL Shortener.

Note: metadata (user_id, created_at, expiry, short_code) is negligible at ~100 bytes per row vs 10KB of paste content. Storage is dominated entirely by the paste text — not indexes, not metadata.

---

## Bandwidth

```
Convert rule: bytes/sec × 8 = bits/sec  (NICs are rated in bits)

Outgoing (paste reads):
  Avg:  1,000/sec × 10KB = 10 MB/s × 8 = 80 Mbps
  Peak: 3,000/sec × 10KB = 30 MB/s × 8 = 240 Mbps

Incoming (paste writes):
  Avg:  10/sec × 10KB = 100 KB/s × 8 = 0.8 Mbps
  Peak: 30/sec × 10KB = 300 KB/s × 8 = 2.4 Mbps
```

240 Mbps peak outgoing is well under a standard 10Gbps NIC (10,000 Mbps). No bandwidth constraint — CDN is not required for bandwidth reasons. (We may still want one for latency if users are globally distributed.)

---

## Summary

```
Avg write QPS:     10/sec    | Peak: 30/sec
Avg read QPS:      1,000/sec | Peak: 3,000/sec
Read:write ratio:  100:1
Storage (10 yrs):  ~150TB    → sharding required
Peak bandwidth:    240 Mbps  → fits single NIC, no CDN needed for BW
```

---

## Architecture decisions this forces

```
Read QPS 3,000   → single DB handles this, but caching helps with 10KB payloads

Storage 150TB    → sharding required (>10TB per machine limit)

Bandwidth 240Mbps → no CDN needed for bandwidth alone

Paste size 10KB  → content should be stored separately from metadata(content in blob store or text column, metadata in main DB)
```

The last point is new compared to URL Shortener. A URL row is 500 bytes — everything fits in one DB row. A paste is 10KB of content plus metadata. At scale it's worth separating the content blob from the metadata to allow independent scaling — small metadata reads are fast, large content reads go to a separate store.

---

> [!tip] Interview framing
> "10M MAU, 2M DAU, 0.5 writes per DAU = 1M writes/day = 10 writes/sec avg, 30 peak. 100:1 read:write = 1k reads/sec avg, 3k peak. Storage: 3.65B pastes × 10KB = 36.5TB raw, ~150TB with replication and indexes — sharding required. Bandwidth: 3k reads × 10KB = 30 MB/s = 240 Mbps peak — fits on one NIC, no CDN needed for bandwidth."
