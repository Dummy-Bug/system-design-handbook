
> [!info] Building on the previous
> Raw IDs failed because they expose internals and break under sharding. Hashing solves the exposure problem — a hash looks random, reveals nothing. And we can hash on the app server, so no DB coordination needed. Let's try it.

---

## Approach 1 — Hash the long URL directly

Take the long URL, run it through a hash function (MD5, SHA-256), use the output as the short code.

```
Input  → https://very-long-url.com/with/path
MD5    → a3f8c2d1e9b047f6a1c3e5d8b2f4a6c9  (32 hex characters)
```

Problem: 32 characters is not short. A URL shortener with a 32-character code defeats the purpose.

So the instinct is to trim — just take the first 6 characters:

```
MD5 output  → a3f8c2d1e9b047f6...
Trimmed     → a3f8c2
Short URL   → bit.ly/a3f8c2
```

**Why trimming breaks uniqueness:**

A hash function maps any input to a fixed-length output. The full output is designed to be unique. When you trim it, you are throwing away bits — and with them, the uniqueness guarantee.

```
URL 1 → MD5 → a3f8c2d1e9b0...  → trimmed → a3f8c2
URL 2 → MD5 → a3f8c2aa71f3...  → trimmed → a3f8c2  ← collision ✗
```

Two completely different long URLs now map to the same short code. `bit.ly/a3f8c2` can only point to one of them. The other is lost.

This violates the core reliability requirement: **no two long URLs can share a short code.**

---

## Approach 2 — Hash the ID instead

The problem with hashing the long URL is that long URLs can be hundreds of characters. What if we hash something shorter — like the DB row ID?

```
DB assigns ID  → 4821903
Hash the ID    → 9b2f4a...  (shorter input, same hash length)
Trim to 6 chars → 9b2f4a
Short URL      → bit.ly/9b2f4a
```

The input is shorter, but the output length is still determined by the hash function — not the input. MD5 always outputs 128 bits regardless of whether you feed it 7 characters or 700.

So trimming still breaks uniqueness. The same collision problem applies.

---

## The fundamental problem with hashing

Hashing solves the exposure problem — the output looks random, reveals nothing about your internals. But it does not solve uniqueness when you trim, regardless of what you hash.

```
Full hash output  → guaranteed unique (by hash function design)
Trimmed output    → uniqueness broken (bits discarded = collisions possible)
```

---

> [!danger] Why this fails
> Trimming any hash — whether of the long URL or the ID — discards bits and breaks the uniqueness guarantee. You cannot trim a hash and claim it is still unique. The two goals (short code + unique) cannot both be satisfied by hashing alone.

