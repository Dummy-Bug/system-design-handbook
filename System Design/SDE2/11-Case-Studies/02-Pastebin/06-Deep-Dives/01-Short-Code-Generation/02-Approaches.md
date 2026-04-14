
> [!info] There are four main approaches to short code generation — each with different trade-offs on collision risk, complexity, and failure modes.
> Understanding why each approach loses helps you defend the one you chose.

---

## Approach 1 — Random Base62 + Collision Check

Generate 6 random Base62 characters, check if the code already exists in the DB, retry if it does.

```
short_code = random.choice(BASE62_ALPHABET, 6)
if EXISTS in pastes table:
    retry
else:
    use it
```

**Why it seems fine early on:**
At 1M pastes, collision probability per attempt = 1M / 56B = 0.002%. Near zero. Fast.

**Why it breaks at scale:**
At 3.65B pastes (year 10), collision probability = 3.65B / 56B = 6.5% per attempt. 1 in 15 writes needs a retry. At peak 30 writes/sec, that's ~2 retries/sec hitting the DB for nothing. And retries can chain — a retry can itself collide, requiring another retry.

**Verdict: works at small scale, degrades as the table fills. Not production-grade for long-lived systems.**

---

## Approach 2 — Snowflake ID → Trim → Base62

Generate a 64-bit Snowflake ID (timestamp + machine ID + sequence), take the lower N bits, Base62 encode them.

```
snowflake = generate_snowflake()   // 64-bit unique ID
trimmed   = snowflake & 0xFFFFFFFF // take lower 32 bits
short_code = base62_encode(trimmed)
```

**Why it seems attractive:**
Snowflake IDs are guaranteed unique across distributed nodes. No collision check needed.

**Why trimming breaks uniqueness:**
Two Snowflake IDs that differ only in their upper bits (timestamp component) will have identical lower bits. After trimming, they produce the same short code — collision reintroduced.

```
Snowflake A: 0001 0110 ... 1010 1100  (lower 32 bits: 1010 1100...)
Snowflake B: 0010 0110 ... 1010 1100  (lower 32 bits: 1010 1100...)
                                       ↑ same after trim → collision
```

You can't trim a guaranteed-unique value and keep the guarantee. The uniqueness lives in the full 64 bits.

**Full Base62 encoding of 64-bit Snowflake:**
2^64 ≈ 1.8 × 10^19. To represent this in Base62 you need:
```
62^10 = 8.4 × 10^17  → not enough
62^11 = 5.2 × 10^19  → enough
```
11 characters. Too long for a short code.

**Verdict: trimming kills uniqueness. Full encoding produces 11-char codes — too long. Snowflake doesn't fit cleanly.**

---

## Approach 3 — KGS (Key Generation Service)

A dedicated service pre-generates millions of unique Base62 codes offline, stores them in a `keys_available` table. App servers request batches of keys. No collision check at write time.

```
KGS generates: [aB3kZ9, xR2mP1, qT8nL4, ...]  → stored in keys_available table
App server requests batch of 1000 keys → moves them to keys_used table
On paste create: pop one key from local batch, use it
```

**Why it works well:**
Zero collision risk at write time. Keys are pre-validated. App servers hold local batches — no network hop per write.

**Why it's overkill here:**
Pastebin has 30 writes/sec at peak. KGS is designed for systems with thousands of writes/sec where the collision check DB round-trip becomes a bottleneck. At 30/sec, a simple DB check adds negligible latency.

KGS also adds operational complexity: the service itself is a SPOF (needs HA), key batches can be wasted if an app server crashes mid-batch, and the pre-generation job needs to stay ahead of consumption.

**Verdict: correct but over-engineered for Pastebin's write volume. Worth it at URL Shortener scale (1k writes/sec). Not worth it at 30 writes/sec.**

---

## Approach 4 — Redis INCR Counter (Chosen)

A global atomic counter in Redis. Each write increments the counter by 1 and gets back a unique integer. Base62 encode that integer → short code.

```
counter = REDIS INCR paste_counter   // atomic, returns 1, 2, 3, 4...
short_code = base62_encode(counter)  // "000001", "000002", ...
```

**Why it's correct:**
Redis INCR is atomic — no two calls ever return the same value. No collision possible. No collision check needed. No retry logic.

**Why the codes stay short:**
At 3.65B pastes, counter = 3,650,000,000. Base62 encode of 3.65B fits in 6 chars (62^6 = 56B). Codes grow naturally from "000001" to longer strings over time but stay at 6 chars for our entire 10-year window.

**Why it beats the alternatives at Pastebin's scale:**
- Simpler than KGS — no dedicated service, no batch management
- Correct unlike trimmed Snowflake
- No collision degradation unlike random generation
- Redis INCR is a single-operation, sub-millisecond call

**Trade-off — Redis as SPOF:**
If Redis goes down, short code generation stops. Mitigation: Redis Sentinel or Redis Cluster for HA. If Redis is temporarily unavailable, writes fail gracefully — pastes are not created, no corrupted state. Covered in Failures and Edge Cases.

**Verdict: chosen. Atomic, collision-free, simple, fast, fits Pastebin's write volume perfectly.**

---

## Comparison Table

| Approach | Collision-free | Code length | Complexity | Right for Pastebin? |
|---|---|---|---|---|
| Random + check | No (degrades) | 6 chars | Low | No |
| Snowflake trim | No (breaks) | 6 chars | Medium | No |
| Full Snowflake encode | Yes | 11 chars | Medium | No (too long) |
| KGS | Yes | 6 chars | High | Overkill |
| Redis INCR | Yes | 6 chars | Low | Yes ✓ |

---

> [!tip] Interview framing
> "Four approaches considered: random generation degrades at scale as collision probability grows; Snowflake trimming kills uniqueness; full Snowflake encoding produces 11-char codes; KGS is correct but overkill at 30 writes/sec. Redis INCR wins — atomic counter, guaranteed unique, simple, sub-millisecond. Fits Pastebin's write volume perfectly."
