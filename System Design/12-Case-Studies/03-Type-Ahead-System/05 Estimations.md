# Type-Ahead System — Estimations

> [!question] Why estimate before designing?
> Numbers tell us **what we're up against**. Without them, architecture decisions are guesswork.
> With them, every decision that follows is grounded in reality.

We estimate in order: ==users → searches → QPS → storage → bandwidth==

---

## Step 1 — User Scale

```
MAU  (Monthly Active Users)  =  1 Billion
DAU  (Daily Active Users)    =  20% of MAU  =  200 Million
```

> [!info] Why 20% of MAU for DAU?
> Not every monthly user visits every day. 20% is the standard assumption for products with daily habits (search, social media). Less sticky products use 10%; something like WhatsApp might use 70%.

---

## Step 2 — Daily Search Volume

```
Average searches per user per day  =  5
Total searches per day  =  200M  ×  5  =  1 Billion searches/day
```

> [!info] Where does "5 searches/day" come from?
> A reasonable assumption for Google — news, directions, shopping, recipes. State your assumption and justify it briefly. The interviewer cares about your reasoning, not the exact number.

---

## Step 3 — Baseline Search QPS

Seconds in a day:
```
24 × 60 × 60  =  86,400 seconds
```

```
1,000,000,000 searches/day  ÷  86,400  =  ~11,574 QPS
                                        ≈  10,000 QPS  (rounded)
```

> [!tip] The rounding trick
> Back-of-envelope math is about **order of magnitude**, not precision.
> Rounding 86,400 → 100,000 makes mental math faster with only ~15% error — acceptable for estimation.
> ```
> Exact:    1B ÷ 86,400  =  11,574 QPS
> Rounded:  1B ÷ 100,000 =  10,000 QPS  ✅
> ```

---

## Step 4 — Typeahead QPS (Read Path)

Each search involves the user typing character by character. With debouncing, not every keystroke fires — only pauses do.

> [!example] How 3–5 calls happen per search
> User types `"paris weather"` (13 chars) with natural pauses:
> ```
> pause after "par"      →  request 1
> pause after "paris"    →  request 2
> pause after "paris w"  →  request 3
> final submit           →  request 4
> ```
> Realistic range: **3–5 debounced calls per search**

Worst case (5 calls per search):
```
5 typeahead calls  ×  10,000 search QPS  =  50,000 typeahead QPS  (average)
```

---

## Step 5 — Write QPS (Search Submission)

Not every search is a new query. There are two types:

| Write type | Example |
|---|---|
| **Repeat query** | "paris weather" — searched millions of times before |
| **New query** | "paris budget hotels 2026" — never seen before |

New queries drive the meaningful write load — they need to be inserted fresh into the index.

```
50% of DAU submit at least one new/unseen query per day
  →  50%  ×  200M  =  100M new query events/day

Write QPS  =  100,000,000  ÷  86,400  ≈  1,000 write QPS
```

```
Read : Write ratio  =  50,000 : 1,000  =  50 : 1
```

> [!success] The system is overwhelmingly read-heavy
> 50 reads for every 1 write. This ratio is a key constraint the design must respect.

---

## Step 6 — Peak Traffic

Search traffic is not uniform. Morning/evening spikes and breaking news events cause sudden bursts.

```
Peak multiplier  =  20x

Peak typeahead QPS  =  20  ×  50,000  =  1,000,000 QPS
Peak write QPS      =  20  ×   1,000  =     20,000 QPS
```

> [!info] Why 20x?
> Normal daily patterns peak at 2–3x average. But search has sharp spikes — a breaking news event (election result, sports final) drives everyone to search simultaneously. 20x covers these moments safely.

---

## Step 7 — Storage

How much data needs to be stored in the suggestion index?

### How many unique queries are worth storing?

Not every query ever typed needs to be in the index. Most queries are searched so rarely they would never appear in anyone's top 10 suggestions.

```
"paris weather"            → searched 50 million times  ← worth storing
"paris hotels"             → searched 30 million times  ← worth storing
"paris afsdkjhqwerty 123"  → searched 1 time            ← not worth storing
```

This is called the **long tail** — billions of rare, weird, one-off queries that are useless for autocomplete. We ignore them and keep only the most frequently searched queries.

> [!warning] Where does 10 Million come from?
> Honestly — it is an **assumption**, not a derived number.
> In an interview you would say: *"I'll assume we store the top 10M queries by frequency — the long tail beyond that is too rare to surface as a useful suggestion."*
>
> You could reasonably say 5M or 50M and the final storage number would scale proportionally. The exact number doesn't matter as much as the reasoning — we are cutting off the long tail.
>
> For reference: Google has indexed trillions of unique queries ever, but the top ~10–50M cover the vast majority of what people actually search for day to day.

### The math

```
Unique queries worth storing  ≈  10 Million

Each query "paris weather" must appear under all its prefixes:
  "par", "pari", "paris", "paris ", "paris w" ... (starting from 3 chars)
  → ~10 prefixes per query on average

Unique prefix keys  =  10M queries  ×  10 prefixes  =  100M prefix keys

Each prefix key stores top 10 suggestions:
  10 suggestions  ×  avg 30 bytes each  =  300 bytes per prefix key

Total storage  =  100M  ×  300 bytes  =  ~30 GB
```

---

## Step 8 — Bandwidth

**Read path — responses sent to clients:**
```
Each response  =  10 suggestions  ×  30 bytes  =  300 bytes
At peak 1M QPS:  1,000,000  ×  300 bytes  =  ~300 MB/s outbound
```

**Write path — requests received:**
```
Each write request  =  ~30 bytes (query string)
At peak 20k write QPS:  20,000  ×  30 bytes  =  ~0.6 MB/s inbound
```

```
Read : Write bandwidth  =  300 MB/s : 0.6 MB/s  =  500 : 1
```

---

## Summary

| Metric | Value |
|---|---|
| MAU | 1 Billion |
| DAU | 200 Million |
| Daily searches | 1 Billion |
| Average typeahead QPS | ~50,000 |
| **Peak typeahead QPS** | **~1,000,000** |
| Write QPS (new queries) | ~1,000 |
| Peak write QPS | ~20,000 |
| Read : Write ratio | 50 : 1 |
| Storage | ~30 GB |
| Peak outbound bandwidth | ~300 MB/s |

---

## What These Numbers Tell Us

> [!abstract] Four constraints the design must solve

| Observation | Constraint |
|---|---|
| 1M peak QPS | Cannot be served from a single machine |
| 30 GB storage | Must fit entirely in fast-access memory |
| 50:1 read/write ratio | Design must be optimised heavily for reads |
| 300 MB/s outbound bandwidth | Significant data transfer load at peak |

