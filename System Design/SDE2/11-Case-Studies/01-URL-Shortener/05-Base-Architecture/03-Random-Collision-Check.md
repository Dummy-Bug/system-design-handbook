
> [!info] Building on the previous
> Hashing failed because trimming breaks uniqueness. So instead of deriving the short code from the input, what if we just generate a random short string and check the DB to confirm it's free? No hashing, no trimming — just generate and verify.

---

## The approach

Generate a random N-character string. Check if it already exists in the DB. If not, use it. If yes, generate another one.

```
Generate → x7k2p9
Check DB → not found → insert → return bit.ly/x7k2p9 ✓

Generate → a3f8c2
Check DB → already exists → generate again
Generate → q9m3r7
Check DB → not found → insert → return bit.ly/q9m3r7 ✓
```

This guarantees uniqueness — you only insert if the slot is free. No trimming, no derivation. Just randomness + verification.

---

## Choosing the base — how many characters do we need?

First, figure out how many unique short codes the system needs to generate over its lifetime.

From the estimation:
```
~1k writes/second
~90M URLs/day
~50 billion URLs over 10 years (with growth buffer)
```

So the short code space must have **at least 50 billion unique values**.

**Why base16 doesn't work:**

Base16 (hex) uses 16 characters per position: `0-9` and `a-f`.

Step 1 — how many unique combinations for N characters?

```
1 character → 16^1 = 16 combinations
2 characters → 16^2 = 256 combinations
4 characters → 16^4 = 65,536 combinations
8 characters → 16^8 = 4,294,967,296 ≈ 4.3 billion   ← not enough (need 50B)
9 characters → 16^9 = 68 billion                      ← enough, but 9 chars is too long
```

To cover 50 billion with base16, you need at least 9 characters. That's long — not what a URL shortener should produce.

**Why base64 works:**

Base64 uses 64 characters per position: `a-z`, `A-Z`, `0-9`, `+`, `/`.

Step 1 — how many unique combinations for N characters?

```
1 character → 64^1 = 64 combinations
2 characters → 64^2 = 4,096 combinations
3 characters → 64^3 = 262,144 combinations
4 characters → 64^4 = 16,777,216 ≈ 16.7 million combinations
5 characters → 64^5 = 1,073,741,824 ≈ 1 billion combinations    ← not enough
6 characters → 64^6 = 68,719,476,736 ≈ 68 billion combinations  ✓ (68B > 50B)
```

**6 characters in base64 covers the entire 10-year URL space.** This is why URL shorteners use 6-7 character codes.

---

## The collision check is fast — not a full scan

A natural concern: to check if a short code exists, do you scan every row in the DB across every shard?

No. You put a **unique index** on the short code column. An index turns the lookup into O(log n) — it reads a small tree structure, not every row. Even across shards, you only hit the one shard that owns that short code. The check is fast.

---

## The problem — collision rate grows over time

Early on, the DB is mostly empty. You generate a random 6-char code, almost certainly it's free, insert immediately. One round trip.

But after the DB fills up — say 40 billion entries out of a possible 68 billion — most slots are taken. You generate a random code, it collides. Generate again, collides again. You might need many retries just to find one free slot. Each retry is a DB round trip.

```
At 10% full  → collision on ~1 in 10 attempts  → fast
At 50% full  → collision on ~1 in 2 attempts   → slowing down
At 80% full  → most attempts collide           → many retries
```

URL creation latency degrades as the system fills up. At scale and high fill rate, this becomes a real problem.

---

> [!danger] Why this fails at scale
> Random generation with collision check works well early on but degrades as the DB fills up. Collision probability increases with fill rate, causing more retries per insertion, which means higher and less predictable write latency. The system gets slower over time.

---

**Next:** The collision problem comes from pure randomness — there's no coordination. What if we use a globally unique ID generator — like a UUID — that guarantees uniqueness without any DB check?
