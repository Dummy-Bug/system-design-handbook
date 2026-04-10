# Why Column-Family Stores Exist

The best way to understand column-family stores is to start with a problem that breaks every other database type — and watch them fail one by one.


## The problem — Twitter analytics at scale

Imagine you're building Twitter's analytics dashboard. For every tweet, you want to track impressions, clicks, and retweets — broken down by hour and by country.

That sounds simple. But Twitter publishes **500 million tweets per day**. Each tweet gets events continuously — an impression every time someone scrolls past it, a click every time someone taps it. At even a conservative estimate of 10 impression events per tweet per hour, you're looking at:

```
500M tweets/day
× 10 impression events/tweet/hour
= 5 billion writes/day
= ~58,000 writes/second
```

And that's just impressions, and just the first hour. The real number is far higher. So what database do you reach for?

---

## Why SQL breaks first

SQL databases are row-oriented — every row is a complete record, stored together on disk. A single Postgres or MySQL node on modern hardware can absorb roughly **5,000–10,000 writes per second**.

At 58,000 writes/second, you've already blown past a single SQL node. You could shard across multiple nodes to get there — but then you've lost cross-shard joins, you're managing sharding logic yourself, and you're dealing with hotspots when all writes land on the same time-based shard. It becomes operationally painful fast.

But there's a deeper problem with SQL than just throughput. SQL stores data row by row. When an impression event comes in and you need to increment the `impressions` counter by 1, SQL has to:

1. Fetch the **entire row** from disk
2. Modify one field
3. Write the **entire row** back to disk

At 58,000 writes/second, you're reading and writing enormous chunks of data just to change a single number in each row. Most of that disk I/O is pure waste.

```
| tweet_id | hour | country | impressions | clicks | retweets |
|----------|------|---------|-------------|--------|----------|
| tweet_1  | 3pm  | IN      | 4200        | 310    | 89       |

→ to increment impressions: read this entire row, update one number, write it all back
→ clicks and retweets came along for the ride — never needed, never used
```

> [!important] SQL throughput ceiling
> A single SQL node handles ~5k–10k writes/sec. Twitter analytics needs ~58k writes/sec just for impressions. SQL would require aggressive sharding before you even start — and sharding SQL is not a free lunch.

---

## Why Key-Value stores fall short

Key-value stores are the obvious next thought — they're fast, they handle high write throughput (Redis handles ~100k ops/sec), and they're simple. You could store each row as a key:

```
tweet_1:IN:mobile:2026-04-01-03pm → { impressions: 4200, clicks: 310, retweets: 89 }
```

The write throughput problem is solved. But a new problem appears the moment you try to query.

If an analyst wants "give me all hourly impressions for tweet_1 in India", they need to query:

```
tweet_1:IN:mobile:2026-04-01-01am
tweet_1:IN:mobile:2026-04-01-02am
tweet_1:IN:mobile:2026-04-01-03am
... 24 separate keys ...
```

Key-value stores are designed for **point lookups** — fetch me the value for this exact key. They have no concept of "give me a range of related keys". Every hour is a separate round-trip to the database. At scale, this becomes unacceptably slow and complex.

---

## Why Document stores don't fit either

Document stores like MongoDB could store each tweet's analytics as a nested document:

```json
{
  "tweet_id": "tweet_1",
  "country": "IN",
  "hours": {
    "3pm": { "impressions": 4200, "clicks": 310, "retweets": 89 },
    "4pm": { "impressions": 5100, "clicks": 400, "retweets": 91 }
  }
}
```

But documents assume a **consistent shape** — every document has roughly the same fields. Analytics data is inherently **sparse**. Tweet A might have data for 30 countries, tweet B only for 3. Storing this in documents gets wasteful and messy — you end up with large nested objects full of absent fields.

More importantly, document stores weren't built to handle the update pattern here. **Every impression event requires fetching the document, modifying a nested counter, and writing the whole document back**. Same waste problem as SQL.

---

## The gap that column-family stores fill

Three databases, three different failure modes:

```
SQL          → hits write throughput ceiling (~5-10k/sec), wastes disk I/O reading whole rows

Key-Value    → no range queries — every related key is a separate round-trip

Document     → poor fit for sparse data, same row-read waste on frequent updates
```

Column-family stores were designed specifically to solve all three at once:
- **Write throughput** — built on LSM trees, absorb millions of writes/sec natively
- **Range queries** — row keys are sorted, so related data sits together on disk
- **Sparse data** — **missing cells don't exist at all, no NULLs, no wasted space**

