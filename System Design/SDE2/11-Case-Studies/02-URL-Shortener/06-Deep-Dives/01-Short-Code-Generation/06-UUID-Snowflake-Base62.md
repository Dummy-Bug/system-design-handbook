
> [!info] Building on the previous
> Snowflake + base64 gives 11 characters and has URL-safety issues. The fix for URL safety is base62 — drop the two problematic characters. But does switching to base62 get us closer to 6-7 characters?

---

## What is base62?

Base62 is base64 with `+` and `/` removed:

```
a-z  → 26 characters
A-Z  → 26 characters
0-9  → 10 characters
-----------
total → 62 characters   (no + or /)
```

Every character in base62 is safe to use directly in a URL — no percent-encoding needed. This is why base62 is the industry standard for URL shorteners.

---

## The math — does it get shorter?

**Step 1 — how many bits per base62 character?**

Base62 has 62 possible values per character. 62 doesn't land exactly on a power of 2, so we use logarithms:

```
We need: 2^x = 62
x = log2(62) = log(62) / log(2) = 1.792 / 0.301 ≈ 5.95 bits per character
```

Compare to base64:
```
base64 → 2^6 = 64  → exactly 6 bits per character
base62 → 2^5.95    → ≈ 5.95 bits per character  (slightly less)
```

The difference is tiny — base62 packs just barely less information per character than base64.

**Step 2 — how many characters to encode a Snowflake ID (64 bits)?**

```
Total bits         = 64
Bits per character = 5.95  (base62)
Characters needed  = 64 / 5.95 = 10.75 → round up to 11 characters
```

**Step 3 — how many characters to encode a UUID (128 bits)?**

```
Total bits         = 128
Bits per character = 5.95  (base62)
Characters needed  = 128 / 5.95 = 21.5 → round up to 22 characters
```

Switching from base64 to base62 does not meaningfully change the length. Both give 11 characters for a Snowflake ID and 22 characters for a UUID.

```
Snowflake + base64  → 11 chars (URL-unsafe)
Snowflake + base62  → 11 chars (URL-safe) ✓
UUID + base64       → 22 chars (URL-unsafe)
UUID + base62       → 22 chars (URL-safe)
```

Base62 solves the URL-safety problem. The length stays the same.

---

## Where we stand

We have a uniqueness-guaranteed, URL-safe short code — but it's 11 characters instead of the 6-7 we want.

The reason: Snowflake IDs are 64 bits, but we only need 36 bits to cover our entire 10-year URL space.

```
2^36 = 68 billion  >  50 billion (our 10-year estimate)  ✓
36 bits / 5.95 bits per char = ~6 characters  ✓
```

If we could use just 36 bits, we'd get 6 characters in base62. The natural next thought: take a Snowflake ID and use only the lower 36 bits. Trim the rest.

But there's a problem with that.

---

> [!important] Base62 is the right encoding — but we still have a length problem
> Base62 solves URL safety. For our 10-year scale, 36 bits (6 base62 chars) is theoretically enough. But we can't just take the lower 36 bits of a Snowflake ID — and the reason why is the most important concept in this entire section.

---

**Next:** Why can't we truncate the Snowflake ID to 36 bits and call it done?
