> Estimations tell us the **scale we're designing for** — so every architecture decision that follows is grounded in real numbers, not gut feel.
> We estimate in this order: users → searches → QPS → storage → bandwidth.

---

## Step 1 — User Scale

```
MAU (Monthly Active Users) = 1 Billion
DAU (Daily Active Users)   = 20% of MAU = 200 Million
```

> [!info] Why 20% of MAU for DAU?
> Not every monthly user visits every day. 20% is a standard industry assumption for a product with daily habits (search, social media). For a less sticky product you'd use 10%; for something like WhatsApp maybe 70%.

---

## Step 2 — Daily Search Volume

```
Average searches per user per day = 5
Total searches per day = 200M users × 5 searches = 1 Billion searches/day
```

> [!info] Where does "5 searches per day" come from?
> This is a reasonable assumption for Google — people search for news, directions, recipes, shopping, etc. In an interview, state your assumption and justify it briefly. The interviewer cares about your reasoning, not the exact number.

---

## Step 3 — Baseline Read QPS

Seconds in a day:
```
24 hours × 60 minutes × 60 seconds = 86,400 seconds/day
```

Baseline search QPS (searches, not typeahead calls yet):
```
1,000,000,000 searches/day ÷ 86,400 seconds = ~11,574 QPS
≈ 10,000 QPS  (rounded down for simplicity)
```

> [!info] Why round 86,400 to 100,000?
> Back-of-envelope math is about order of magnitude, not precision. Rounding 86,400 → 100,000 makes mental math faster and introduces only ~15% error — acceptable for estimation purposes. This is a standard interview trick:
> ```
> 1B / 86,400 = 11,574  (exact)
> 1B / 100,000 = 10,000  (rounded — close enough ✅)
> ```

---

## Step 4 — Typeahead QPS (Read Path)

Each search interaction involves the user typing a query character by character. With debouncing, not every keystroke fires a request — only pauses do.

```
Assumption: 3–5 debounced API calls per search interaction

Why 3–5?
  User types "paris weather" (13 chars)
  With 250ms debouncing, requests fire at natural pauses:
    pause after "par"     → request 1
    pause after "paris"   → request 2
    pause after "paris w" → request 3
    final pause           → request 4
  Realistic range: 3–5 calls per search
```

Worst case (5 calls per search):
```
5 typeahead calls × 10,000 search QPS = 50,000 Typeahead QPS (average)
```

---

## Step 5 — Write QPS (Search Submission)

Every time a user submits a search (clicks a suggestion or hits Enter), we record it to update popularity counters.

```
Assumption: 50% of DAU submit at least one new/unique query per day
  50% × 200M DAU = 100M write events per day

Write QPS = 100,000,000 ÷ 86,400 ≈ 1,000 write QPS (average)
```

```
Read : Write ratio = 50,000 : 1,000 = 50 : 1
```

> This confirms our NFR assumption — this system is overwhelmingly read-heavy. The write path can be async and batched without impacting user experience.

---

## Step 6 — Peak Traffic

Search traffic is not evenly distributed across the day. There are morning and evening spikes (commute times, lunch, after dinner). Major news events cause sudden bursts.

```
Peak multiplier = 20x

Peak typeahead QPS = 20 × 50,000 = 1,000,000 QPS
Peak write QPS     = 20 × 1,000  = 20,000 QPS
```

> [!info] Why 20x peak multiplier?
> Traffic on the internet typically peaks at 2–3x average for normal daily patterns. But search has sharp spikes — a breaking news event (election result, sports final) can drive 10–20x bursts as everyone searches simultaneously. Designing for 20x ensures the system handles these moments without degradation.

---

## Step 7 — Storage Estimation

How much data do we need to store in the suggestion index?

```
Unique queries worth storing suggestions for ≈ 10 Million
  (top searched queries — the long tail is too rare to matter)

Per prefix stored:
  Top 10 suggestions × avg 30 bytes each = 300 bytes per prefix

Number of unique prefixes (3–20 chars) for 10M queries:
  Each query generates ~10 prefixes on average (from 3 chars to full length)
  10M queries × 10 prefixes = 100M unique prefixes

Total storage = 100M prefixes × 300 bytes = ~30 GB
```

**30 GB fits comfortably in a Redis cluster** — a few nodes with 16–32 GB RAM each. This confirms that serving suggestions entirely from in-memory cache is feasible.

---

## Step 8 — Bandwidth Estimation

How much data flows in and out of the system per second?

**Read path (responses sent to clients):**
```
Each response = 10 suggestions × 30 bytes = 300 bytes
At peak 1M QPS:
  1,000,000 × 300 bytes = 300,000,000 bytes/sec = ~300 MB/s outbound
```

**Write path (requests received):**
```
Each write request = query string ~30 bytes
At peak 20,000 write QPS:
  20,000 × 30 bytes = 600,000 bytes/sec = ~0.6 MB/s inbound
```

Read dominates by 500:1. Bandwidth is manageable — modern CDN nodes handle tens of GB/s.

---

## Summary

| Metric | Value |
|---|---|
| MAU | 1 Billion |
| DAU | 200 Million |
| Daily searches | 1 Billion |
| Average typeahead QPS | ~50,000 |
| Peak typeahead QPS | ~1,000,000 |
| Write QPS (average) | ~1,000 |
| Peak write QPS | ~20,000 |
| Read : Write ratio | 50 : 1 |
| Storage (suggestion index) | ~30 GB |
| Peak outbound bandwidth | ~300 MB/s |

---

## What These Numbers Tell Us

```
1M peak QPS        → can't serve from a single machine → need distributed caching
30GB storage       → fits in RAM → serve everything from Redis, no disk reads
50:1 read/write    → optimise entirely for reads, writes can be async
300MB/s bandwidth  → CDN layer is essential to absorb traffic before it hits origin
```

Every architecture decision in the next file flows directly from these four conclusions.
