
> [!info] The right opening move in the interview
> When an interviewer asks "what happens to your short code generation as the DB fills up?", the first answer to reach for is a Bloom Filter. It's a real improvement. It reduces DB load. But it doesn't fix the core problem — and knowing why it falls short is what leads you to the real solution.

---

## What a Bloom Filter is

A Bloom Filter is a probabilistic data structure that answers one question: **"have I seen this key before?"**

It gives you one of two answers:
- **"Definitely not present"** — the key has never been added. This answer is always correct.
- **"Probably present"** — the key might be in the set. This can be a false positive (it says present, but it's actually not).

It never has false negatives. If it says "not present", you can trust it completely.

```
Bloom Filter loaded with all existing short codes

Check "x7k2p9":
→ "Definitely not present" → safe to use, no DB lookup needed ✓
→ "Probably present"       → might be a false positive, regenerate
```

---

## How it improves the collision check

Without a Bloom Filter, every single creation attempt hits the DB:

```
Generate code → DB lookup → collision? → retry → DB lookup → ...
```

Each retry is a full DB read. At 18 retries per creation and 1k creations/sec, that's 18,000 DB reads/sec just for collision checking.

With a Bloom Filter loaded in Redis (or in-memory), the check happens in microseconds without touching the DB:

```
Generate code → Bloom Filter check
→ "Definitely not present" → use it → DB INSERT → done (0 extra DB reads)
→ "Probably present"       → regenerate (might be false positive, but no DB hit)
```

The vast majority of "probably present" answers at high fill rate are true positives — the code really is taken. Whether true positive or false positive, you just regenerate. No DB lookup wasted.

Early on (DB mostly empty), almost every Bloom Filter check returns "definitely not present" → zero extra DB reads for collision checking. The DB lookup that remains is just the INSERT.

---

## What it doesn't fix

Here is the part that matters. The Bloom Filter made each retry cheaper — it eliminated the DB read per retry. But it did not reduce **the number of retries**.

At 53 billion codes used out of 56 billion:

```
Collision probability = 53B / 56B = 94.6%

Without Bloom Filter: ~18 retries, each hitting DB → 18 DB reads
With Bloom Filter:    ~18 retries, none hitting DB → 0 DB reads, but still 18 attempts
```

You're still spinning through 18 random code generations before finding a free one. The CPU work, the random number generation, the Redis checks — all still happen 18 times per creation.

The Bloom Filter is an optimization on top of a fundamentally broken approach. It reduces the cost per retry but does nothing about the retry count itself.

---

## Bloom Filter memory cost

A Bloom Filter for 56 billion entries at 1% false positive rate:

```
Bits needed = -(n × ln(p)) / (ln(2))²

n = 56,000,000,000
p = 0.01 (1% false positive rate)

ln(0.01) = -4.605
(ln(2))²  = 0.693² = 0.480

Bits = -(56B × -4.605) / 0.480
     = 56B × 4.605 / 0.480
     = 56B × 9.59
     = 537 billion bits
     = 537B / 8
     = ~67 GB
```

67GB is manageable in Redis with a high-memory node. Not cheap, but not impossible. Redis even has a native Bloom Filter module (RedisBloom) that handles this exactly.

---

> [!tip] Interview framing
> "First optimization: Bloom Filter in Redis. Checks if a code is taken in microseconds without hitting the DB. At low fill rate, nearly every check returns 'definitely not present' — zero DB reads for collision checking. The problem: at 94% fill rate you still need ~18 attempts before finding a free code. Bloom Filter makes each attempt cheaper, but doesn't reduce the attempt count. That's the gap the pre-generated key pool fills."
