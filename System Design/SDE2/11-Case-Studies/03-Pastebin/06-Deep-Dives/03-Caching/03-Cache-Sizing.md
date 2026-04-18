
> [!info] Cache sizing tells you how much RAM you need — and whether caching is affordable at all.

---

## The 80/20 rule

Not all pastes receive equal traffic. In practice, roughly **20% of pastes receive 80% of reads**. These are the hot pastes — shared links, popular snippets, incident logs being read by a whole team. If you can keep that 20% in cache, you serve 80% of your read traffic from Redis.

This is the standard cache sizing heuristic for read-heavy systems. The exact ratio varies by system, but 80/20 is a reliable starting point for estimation.

---

## The math

```
Daily writes:       1M pastes/day
Hot fraction (20%): 200K pastes

Content per paste:  10KB
Cache per day:      200K × 10KB = 2GB

Active window:      3 days (most reads happen within 3 days of creation)
Total cache needed: 2GB × 3 = 6GB
```

A **16GB Redis instance** comfortably covers this with headroom for metadata overhead and traffic spikes. This is not expensive infrastructure — a single Redis node with 16GB RAM costs a few hundred dollars a month.

---

## Why the active window is 3 days

Pastes have a maximum expiry of 30 days, but traffic doesn't spread evenly across 30 days. Most shared links get clicked in the first few days after creation — when someone pastes a config during an incident, the team reads it that day. When someone shares a code snippet in a chat, it gets read within hours. After a few days, reads drop off sharply.

Using a 3-day active window is conservative and defensible. If data showed reads clustered within 1 day, you could size down. If reads stayed elevated for a week, you'd size up. Start with 3 days and adjust based on observed hit rates.

---

## Cache hit rate target

```
Good:      80–90% hit rate
Very good: 90–95% hit rate
```

With 80/20 sizing and a 3-day window, you should expect 80–90% cache hit rate. This means 80–90% of reads never touch Postgres or S3 — they return from Redis in ~1ms and easily meet the p99 < 50ms SLO.

The remaining 10–20% are cache misses — first reads on newly created pastes, or cold pastes that were evicted. These still hit Postgres + S3 and may take 50–200ms. At 80% hit rate and 3k peak reads/sec, that's ~600 requests/sec going to Postgres + S3. Postgres handles this fine (10k–50k reads/sec capacity), and S3 is designed for parallel high-throughput access.

---

> [!tip] Interview framing
> "80/20 rule — 20% of pastes get 80% of reads. 1M writes/day × 20% = 200K hot pastes × 10KB = 2GB/day. 3-day active window = 6GB. A 16GB Redis instance covers it with headroom. Target hit rate 80–90% — at that rate most reads never touch Postgres or S3."
