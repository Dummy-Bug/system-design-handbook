
> [!info] The collision problem no one talks about at launch
> Random short code generation with a collision check works perfectly when the DB is mostly empty. The problem is silent — it doesn't show up for years. But as the DB fills, it gets progressively worse until creation becomes unusably slow.

---

## How short code generation works today

In the base architecture, every URL creation follows this flow:

```
1. Generate random 6-char base62 code → "x7k2p9"
2. Check DB: SELECT * FROM urls WHERE short_code = 'x7k2p9'
3. If row exists → collision → regenerate and repeat from step 1
4. If no row → INSERT into DB → done
```

This is correct. It guarantees uniqueness. At launch it works beautifully.

---

## Why it breaks as the DB fills

The total number of possible 6-char base62 codes is 56 billion. Early on, almost none of them are taken. Generate a random code — the chance it's already used is negligible.

But think about what happens as URLs accumulate over years.

**At 10 million URLs stored:**

```
Codes taken:    10,000,000
Total possible: 56,000,000,000

Collision probability = 10M / 56B = 0.018%

→ You almost never hit a collision
→ Nearly every creation is one DB lookup and done
```

Fine. No problem.

**At 40 billion URLs stored:**

```
Codes taken:    40,000,000,000
Total possible: 56,000,000,000

Collision probability = 40B / 56B = 71%

→ 71% of codes you generate are already taken
→ Expected retries before finding a free code:
   1 / (1 - 0.71) = 1 / 0.29 = ~3.4 retries on average
→ 3-4 DB lookups per creation
```

Getting bad.

**At 48 billion URLs stored:**

```
Codes taken:    48,000,000,000
Total possible: 56,000,000,000

Collision probability = 48B / 56B = 86%

→ 86% of codes you generate are already taken
→ Expected retries = 1 / (1 - 0.86) = 1 / 0.14 = ~7 retries
→ 7 DB lookups per creation
```

**At 53 billion URLs stored:**

```
Codes taken:    53,000,000,000
Total possible: 56,000,000,000

Collision probability = 53B / 56B = 94.6%

→ Expected retries = 1 / (1 - 0.946) = 1 / 0.054 = ~18 retries
→ 18 DB lookups per creation
```

At 1k creations/sec, that's 18,000 extra DB reads per second just to find a free code. The creation endpoint has become 18x more expensive on the DB than it was at launch.

---

## Why this is a time bomb

The system launches fine. For the first few years — when the DB holds tens or hundreds of millions of URLs — collision rate is so low that nobody notices. The retry logic sits dormant.

Then, gradually, the DB fills. Collision rate climbs. Retries per creation climb with it. DB read load on creation climbs. At some point, a DBA notices DB load has quietly doubled, then tripled, then the creation endpoint starts timing out under peak load.

By the time it's noticeable, it's already a crisis. The root cause — the retry loop — has been in production for years untouched.

---

> [!tip] Interview framing
> "Random generation with collision check works fine when the DB is mostly empty. But collision probability = codes taken / total codes. At 40B used out of 56B, that's 71% — 3-4 retries per creation. At 53B used, it's ~18 retries — 18x the DB load for creation. It's a silent time bomb that builds over years."
