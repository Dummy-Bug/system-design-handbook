
> [!info] Building on the previous
> Base62 + Snowflake gives URL-safe codes but 11 characters. We only need 36 bits to cover 50 billion URLs. So why not just take the lower 36 bits of the Snowflake ID and encode those in base62 for a 6-character code?

---

## The temptation

**Step 1 — how many bits do we actually need to cover 50 billion URLs?**

We need 2^n ≥ 50 billion. Build up from known anchors:

```
2^10 = 1,024               ≈ 1 thousand
2^20 = 1,048,576           ≈ 1 million
2^30 = 1,073,741,824       ≈ 1 billion     ← not enough
2^33 = 8,589,934,592       ≈ 8.5 billion   ← not enough
2^35 = 34,359,738,368      ≈ 34 billion    ← not enough
2^36 = 68,719,476,736      ≈ 68 billion    ✓  (68B > 50B)
```

So **36 bits is enough** to cover our entire 10-year URL space.

**Step 2 — how many base62 characters does 36 bits encode to?**

```
Total bits         = 36
Bits per character = 5.95  (base62)
Characters needed  = 36 / 5.95 = 6.05 → round up to 6 characters  ✓
```

From the math:
```
We need to cover 50 billion unique URLs over 10 years
2^36 = 68 billion  →  36 bits is enough
36 bits / 5.95 bits per base62 char = ~6 characters
```

A Snowflake ID is 64 bits. We only need 36 of them. The idea: take the lower 36 bits, encode in base62, get a 6-character unique short code.

```
Snowflake ID (64 bits) → 0001 0111 0100 ... [lower 36 bits: 1101 0010 ...]
Take lower 36 bits     → 1101 0010 1011 0110 0001 0100 0011 1001 0100
Encode in base62       → x7k2p9   ← 6 characters ✓
```

Looks perfect. But does it guarantee uniqueness?

---

## Why truncation breaks uniqueness

The Snowflake ID is unique across all 64 bits — the timestamp, machine ID, and sequence all contribute. Two different Snowflake IDs are guaranteed to differ somewhere in those 64 bits.

But when you take only the lower 36 bits, you discard 28 bits. Two completely different Snowflake IDs can share the same lower 36 bits:

```
Server 1, t=1000ms, seq=5  → Snowflake → ...101[lower 36: 110100101...]
Server 2, t=2000ms, seq=5  → Snowflake → ...011[lower 36: 110100101...]
                                                             ↑
                                         same lower 36 bits — collision ✗
```

The upper bits (timestamp, machine ID) made them different. You threw those away. Now both map to the same 6-character short code.

---

## This keeps coming back to the same wall

Every approach that tries to get to 6 characters by truncating a larger unique identifier hits the same problem:

```
Full 64-bit Snowflake  → unique ✓ / 11 chars ✗
Truncated to 36 bits   → 6 chars ✓ / not unique ✗
Full 128-bit UUID      → unique ✓ / 22 chars ✗
Trimmed UUID           → short  ✓ / not unique ✗
```

You cannot get both by truncating. To get a short unique code, you need an ID that is **natively short** — one where all the bits contribute to uniqueness and the total bit count is already small enough to encode in 6 characters.

---

## The resolution — three options

**Option 1: Accept 11 characters**

Use the full Snowflake ID encoded in base62. 11 characters, guaranteed unique, no collision check. Works. Just slightly longer than ideal.

**Option 2: Random 6-char base62 + collision check**

Generate a random 6-character base62 string. Check the DB. If taken, regenerate. Unique index makes the check fast. Degrades at high fill rates — but for base architecture, this is acceptable.

**Option 3: Pre-generated key database (deep dive)**

A separate service pre-generates millions of unique 6-character base62 codes offline and stores them in a key DB. When a short URL is needed, pop one from the pool. Always unique, always 6 chars, no collision risk. This is the production-grade solution — covered in Deep Dives.

---

> [!tip] Interview framing
> For base architecture, **Option 2** — random 6-char base62 + collision check — is the right call. It's simple, it works end to end, and the degradation at high fill rates is a known limitation you flag explicitly as a reason to improve in deep dives. Never pretend a simple solution has no weaknesses — name them.

---

**Next:** Now that we understand how short codes are generated, let's put the full base architecture together — the complete end-to-end system for both flows.
