
> [!info] The question
> TTL expires entries after 3 days. But what if the cache fills up before the TTLs expire — during a traffic spike? You need an eviction policy to decide which entries to remove when memory runs out.

---

## TTL handles time — eviction handles space

These are two different mechanisms solving two different problems:

```
TTL        → controls how long an entry lives (time-based expiry)
Eviction   → controls what gets removed when memory is full (space-based removal)
```

TTL runs automatically on every entry regardless of memory. Eviction only triggers when the cache hits its memory limit. They work together, not instead of each other.

---

## The eviction options

Redis supports several eviction policies. The relevant ones:

**noeviction** — when memory is full, refuse new writes. Returns an error.
- Wrong here. You never want your cache to start returning errors just because it's full.

**allkeys-lru** — when memory is full, evict the least recently used key across all keys.
- Good default. The key that hasn't been accessed for the longest time gets removed first.

**volatile-lru** — when memory is full, evict the least recently used key among keys that have a TTL set.
- Better for this use case. All our cache entries have TTLs. This evicts the coldest entry among all TTL-bearing entries — exactly what we want.

**allkeys-lfu** — evict the least frequently used key.
- Also reasonable. LFU tracks how many times a key has been accessed, not just when it was last accessed. A key accessed 1000 times yesterday but not today would survive LFU longer than LRU.

---

## The right choice — LRU + TTL

Use **volatile-lru** eviction combined with a 3-day TTL on every entry.

```
TTL = 3 days         → every entry automatically expires after 3 days
volatile-lru         → if cache fills up, coldest entry (by last access time) is evicted first
```

Why LRU over LFU here? URL traffic is bursty and time-sensitive. A URL that went viral yesterday and got 1M clicks might be completely cold today. LRU correctly identifies it as cold — it hasn't been accessed recently. LFU would keep it around because of its historical click count, wasting cache space on a dead URL.

LRU matches the nature of URL traffic: recency matters more than historical frequency.

---

## When does eviction actually trigger?

With ~27GB steady-state cache size and a provisioned Redis instance of 32GB, the memory limit is almost never hit under normal load.

```
Steady state cache size  → ~27GB
Provisioned Redis RAM    → 32GB
Headroom                 → ~5GB
```

Day-to-day, TTL handles everything. Entries expire after 3 days, new entries come in, the cache stays around 27GB. LRU eviction sits idle.

Eviction only triggers during unexpected traffic spikes — a URL goes viral far beyond normal scale, millions of new entries flood the cache simultaneously, and the 32GB limit is hit before TTLs can expire old entries.

```
Normal operation    → TTL expires old entries → cache stays ~27GB → LRU never triggers
Traffic spike       → cache fills to 32GB → LRU kicks in → coldest entries evicted
Spike subsides      → cache drains back to ~27GB via TTL → LRU idle again
```

LRU is a safety net, not the primary mechanism. TTL does the daily work. LRU protects against the unexpected.

---

> [!danger] Common mistake
> Thinking of LRU and TTL as alternatives. They are not. TTL expires entries based on age. LRU evicts entries based on access recency when space runs out. You need both — TTL to keep the cache fresh, LRU to handle overflow gracefully.

---

> [!tip] Interview framing
> "I use volatile-lru eviction with a 3-day TTL on every entry. Under normal load, TTL handles everything — entries expire after 3 days, cache stays at ~27GB, LRU never triggers. During traffic spikes when the cache fills up, LRU evicts the coldest entries first. LRU is the safety net, TTL is the primary mechanism. They solve different problems — time vs space."

---

**Next:** Now that the caching strategy is complete, let's see the full updated redirect flow with Redis in place.
