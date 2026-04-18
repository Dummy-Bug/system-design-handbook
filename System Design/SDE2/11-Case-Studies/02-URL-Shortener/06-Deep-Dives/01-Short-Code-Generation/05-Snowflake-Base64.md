
> [!info] Building on the previous
> UUID is 128 bits — twice what we need — and trimming it breaks uniqueness. What if we used a 64-bit ID that is designed from the ground up for distributed systems? That's the Snowflake ID, originally built by Twitter to generate unique IDs across thousands of servers without any coordination.

---

## What is a Snowflake ID?

A Snowflake ID is a 64-bit integer. It is structured so that every machine in a distributed system can generate IDs independently — no central coordinator, no DB sequence, no locks.

```
|-- 41 bits --|-- 10 bits --|-- 12 bits --|
   timestamp    machine ID    sequence no.
```

- **41 bits** of millisecond timestamp — gives ~69 years of unique time values
- **10 bits** of machine ID — supports up to 1024 machines generating simultaneously
- **12 bits** of sequence — supports up to 4096 IDs per millisecond per machine

Two machines generating an ID at the exact same millisecond get different machine IDs, so their IDs never collide. One machine generating multiple IDs in the same millisecond increments the sequence. Globally unique, no coordination required.

---

## Encoding a Snowflake ID in base64

A Snowflake ID is 64 bits. How many base64 characters do we need to represent it?

**Step 1 — how many bits does one base64 character hold?**

```
2^1 = 2   → not enough
2^2 = 4   → not enough
2^3 = 8   → not enough
2^4 = 16  → not enough
2^5 = 32  → not enough
2^6 = 64  ✓

So 1 base64 character = 6 bits
```

**Step 2 — how many characters to encode 64 bits?**

```
Total bits         = 64
Bits per character = 6
Characters needed  = 64 / 6 = 10.67 → round up to 11 characters
```

So a full base64 encoding of a Snowflake ID gives an **11-character short code**:

```
Snowflake ID  → 1541815603606036480  (64-bit integer)
Base64        → VXzqK9mAAAB
Short URL     → bit.ly/VXzqK9mAAAB
```

Unique — guaranteed, no DB check needed. No trimming. The full 64-bit ID is encoded, all bits preserved.

---

## Is 11 characters a problem?

Industry standard URL shorteners (bit.ly, TinyURL) use 6-7 characters. 11 characters is noticeably longer.

```
bit.ly/x7k2p9q      ← 7 chars, clean
bit.ly/VXzqK9mAAAB  ← 11 chars, longer
```

It still works — the URL is functional and unique. But from a product perspective, 11 characters is longer than necessary. The question becomes: can we do better?

---

## Why base64 has a URL safety problem too

Base64 uses 64 characters: `a-z`, `A-Z`, `0-9`, `+`, `/`.

The `+` and `/` characters have special meaning in URLs:
- `/` is a path separator — a browser sees `bit.ly/x7k+p/9` and splits it as a path
- `+` is sometimes interpreted as a space in query strings

A short code containing these characters can break URL parsing. You'd need to percent-encode them (`+` → `%2B`, `/` → `%2F`), which makes the URL even longer and uglier.

This is a real practical problem — not just theoretical. Base64 is not safe for use in URLs without modification.

---

> [!danger] Why this isn't ideal
> Snowflake + base64 gives 11 characters — longer than the 6-7 industry standard. Base64 also has URL-safety issues with `+` and `/`. We need a base that is URL-safe and gets us closer to 6-7 characters.

---

**Next:** There's a URL-safe alternative to base64 that drops the two problematic characters. It's called base62 — and it's the industry standard for URL shorteners.
