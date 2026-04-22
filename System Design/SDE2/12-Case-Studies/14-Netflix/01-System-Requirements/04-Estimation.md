# Estimation — Netflix

> See `03-Streaming-Concepts.md` for a full explanation of bitrate, bandwidth, throughput and latency in streaming vs non-streaming systems.

For bandwidth estimation we use **25 Mbps per stream** as the worst case (all users on 4K). In reality the average is closer to 5–8 Mbps since most users watch at 1080p or below.

---

## Assumptions

- 300M MAU
- 50% DAU → 150M DAU
- Average watch time per user per day = 1 hour
- Peak multiplier = 3x average
- 20,000 titles total (movies + TV series)

---

## Concurrent Viewers

```
150M DAU watch 1 hour out of 24 hours

Average concurrent viewers = 150M × (1/24) = 6.25M
Peak concurrent viewers    = 6.25M × 3     = ~20M
```

---

## Bandwidth

```
Worst case bitrate = 25 Mbps per stream (4K)
Peak bandwidth     = 20M × 25 Mbps
                   = 500,000,000 Mbps
                   = 500,000 Gbps
                   = 500 Tbps
```

> [!important] Why this number matters
> 500 Tbps cannot be served from a single data center — a standard server NIC maxes out at 10 Gbps. This single number justifies Netflix's entire CDN strategy — Open Connect, their in-house CDN with thousands of servers placed directly inside ISP networks globally.

---

## Storage

### Content Storage

Each title is stored in multiple resolutions and codecs — 4K, 1080p, 720p, 480p across H.264, H.265, and AV1. Combined, one title takes roughly **100 GB**.

```
40% movies  → 8,000 titles  × 100 GB              =   800,000 GB =  0.8 PB
60% series  → 12,000 series × 50 episodes × 100 GB = 60,000,000 GB = 60.0 PB

Total content storage ≈ 64 PB
```

64 PB is chosen as the nearest power of 2 — clean for back-of-envelope math.

### Metadata Storage

Each title carries title, description, cast, director, genre, S3 URLs — roughly 1 KB per title.

```
20,000 titles × 1 KB = 20 MB — negligible
```

Metadata storage is irrelevant at this scale. The problem is entirely content storage and bandwidth.

---

## Summary

| Metric | Value |
|--------|-------|
| Peak concurrent viewers | ~20M |
| Peak bandwidth | ~500 Tbps |
| Total content storage | ~64 PB |
| Metadata storage | ~20 MB (negligible) |
