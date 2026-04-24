# Instagram Scale Estimations

## Starting Point — Daily Active Users

Instagram has **500 million DAU**. Every number below flows from this.

---

## Write QPS — How Many Posts Per Second?

Assume each user posts roughly **2 times per week**. That gives us posts per day:

```
Posts/day = 500M users × (2/7) ≈ 100M posts/day
```

Convert to per second (86,400 seconds in a day, round to 100,000 for simplicity):

```
Write QPS = 100M / 100,000 = ~1,000 writes/sec
```

---

## Read QPS — How Many Feed Loads Per Second?

Instagram is overwhelmingly read-heavy. Users scroll far more than they post. A reasonable read-to-write ratio for a social feed is **1,000x**:

```
Read QPS = 1,000 writes/sec × 1,000 = ~1,000,000 reads/sec (1M rps)
```

---

## Storage — How Much Data Per Day?

Every post is either a photo or a short video. Assume:
- **80% of posts are images** — compressed Instagram photo ≈ **2MB**
- **20% of posts are short videos** — compressed short video ≈ **50MB**

**Image storage per day:**
```
800 writes/sec × 2MB = 1,600 MB/sec
1,600 MB/sec × 86,400 sec = ~138,000 GB ≈ 138 TB/day
```

**Video storage per day:**
```
200 writes/sec × 50MB = 10,000 MB/sec = 10 GB/sec
10 GB/sec × 86,400 sec = ~864,000 GB ≈ 1 PB/day
```

**Total storage per day:**
```
138 TB + 1,000 TB ≈ 1,140 TB ≈ 1.2 PB/day
```

**Over 5 years:**
```
1.2 PB/day × 365 days × 5 years ≈ 2,190 PB ≈ 2.4 EB
```

With replication (3x copies) and peak traffic buffer (2x), plan for roughly **5 EB** of total storage capacity.

---

## Bandwidth — Read Traffic

When a user loads their feed, assume **5 posts load per request** — a mix of images and videos.

Average post size:
```
(0.8 × 2MB) + (0.2 × 50MB) = 1.6MB + 10MB = ~12MB per post
```

Raw read bandwidth:
```
1M reads/sec × 5 posts × 12MB = ~60 TB/sec
```

**60 TB/sec is orders of magnitude beyond what any set of origin servers can serve.** A standard server NIC handles 10 Gbps. To serve 60 TB/sec raw you would need ~48,000 servers — completely impractical.

> [!danger] Common mistake in interviews
> Do not try to solve the bandwidth problem during estimation. Surface the number, flag it as a problem, and defer to the deep dive.
> *"60 TB/sec is far beyond what origin servers can handle. We'll address this in the deep dive."*


---

## Summary

| Metric               | Number                                    |
| -------------------- | ----------------------------------------- |
| DAU                  | 500M                                      |
| Write QPS            | ~1,000/sec                                |
| Read QPS             | ~1M/sec                                   |
| Storage per day      | ~1.2 PB                                   |
| Storage over 5 years | ~2.4 EB (~5 EB with replication + buffer) |
| Raw read bandwidth   | ~60 TB/sec                                |
