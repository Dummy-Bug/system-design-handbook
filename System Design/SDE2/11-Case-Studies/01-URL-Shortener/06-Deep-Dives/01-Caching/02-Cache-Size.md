
> [!info] The question
> How much RAM do you need in the cache to serve 80% of redirect traffic? The answer depends entirely on which URLs you cache — and the 80-20 rule tells you exactly which ones matter.

---

## The wrong way to calculate cache size

The first instinct is: to serve 80% of traffic, cache 80% of all URLs.

```
Total URLs over 10 years  = 50 billion
80% of those              = 40 billion URLs
Each entry                = 500 bytes (short_code + long_url + metadata)

Cache size = 40 billion × 500 bytes = 20,000,000,000,000 bytes = 20TB of RAM
```

20TB of RAM. That's not a cache — that's the entire database in memory. Obviously wrong.

The mistake is assuming all 50 billion URLs are being actively clicked right now. Most URLs go cold — created once, clicked a few times, and never touched again. A short URL from 3 years ago is not competing for cache space with one that just went viral.

---

## The 80-20 rule — applied correctly

The 80-20 rule (Pareto principle) states: **80% of traffic comes from 20% of URLs.**

In a URL shortener, this is even more extreme in practice. A celebrity posts a link, it gets clicked a million times in an hour. A random user shortens a link to send to their friend — it gets clicked 5 times total.

The key insight: you don't need to cache 80% of all URLs ever created. You need to cache the **top 20% of URLs that are actively hot right now**.

---

## What does "hot right now" mean?

URLs don't stay hot forever. A viral tweet drives traffic for a day or two. A news article link maybe a week. After that, clicks drop off and the URL goes cold.

A reasonable window for "active" URLs is **the last 3 days**. URLs created or clicked within the last 3 days are likely still receiving traffic. Anything older is mostly cold.

---

## The correct cache size calculation

**Step 1 — how many URLs are created per day?**

From the estimation:
```
URL creators per day  = 10M users
URLs per user per day = 3
URLs created per day  = 10M × 3 = 90M URLs/day
```

**Step 2 — how many URLs are active over a 3-day window?**

```
URLs per day      = 90M
Window            = 3 days
Active URLs       = 90M × 3 = 270M URLs
```

**Step 3 — apply the 80-20 rule**

You only need to cache the top 20% of those active URLs to serve 80% of traffic:

```
20% of 270M = 0.20 × 270,000,000 = 54M URLs to cache
```

**Step 4 — how much RAM does that require?**

Each cache entry stores the short code and long URL. From estimation, each entry is ~500 bytes:

```
54M entries × 500 bytes = 27,000,000,000 bytes = 27GB
```

**Step 5 — round to a practical number**

27GB is a comfortable fit on a single Redis instance. Provision 32GB to give headroom.

---

## How the cache grows over time

The cache doesn't fill up all at once. It grows day by day:

```
End of Day 1  → ~9GB  (Day 1 URLs cached: 90M × 20% × 500B ≈ 9GB)
End of Day 2  → ~18GB (Day 1 + Day 2)
End of Day 3  → ~27GB (Day 1 + Day 2 + Day 3) ← steady state reached
Day 4 onwards → Day 1 entries expire via TTL → stays at ~27GB
```

After 3 days, the cache reaches a steady state. New hot URLs come in, old ones expire. The total size stays around 27GB indefinitely — assuming traffic stays roughly constant.

---

## Why this is much better than 20TB

```
Naive approach  → cache 80% of all URLs ever → 20TB RAM → impossible
Correct approach → cache top 20% of URLs active in last 3 days → 27GB → one Redis instance
```

The difference is 750x. All because of one question: are you caching based on what exists, or what's actually being used right now?

---

> [!tip] Interview framing
> "I apply the 80-20 rule to the active window, not the full dataset. 80% of traffic comes from 20% of URLs. Hot URLs stay hot for roughly 3 days — after that they go cold. 3 days of URLs is 270M entries, 20% of that is 54M, at 500 bytes each that's ~27GB. One Redis instance handles this comfortably. The cache self-manages — new entries come in, TTL expires old ones, steady state stays around 27GB."

---

**Next:** Now that we know how big the cache is, how do we populate it? When do entries go in, and what happens when they expire?
