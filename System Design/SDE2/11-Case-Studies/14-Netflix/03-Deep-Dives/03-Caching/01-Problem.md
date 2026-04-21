## The Problem — One S3 Bucket Fails on Two Fronts

The transcoding pipeline stores all chunks in a single S3 bucket — say **US East (Virginia)**.

**Problem 1 — Distance.** A user in Mumbai clicks play on Inception. Every chunk has to travel from Virginia to Mumbai and back.

```
Mumbai → Virginia ≈ 13,000 km

one-way   = 13,000 / 200,000 = 65ms
round trip = 130ms
real world (routing hops + congestion) ≈ 200–300ms
```

200–300ms of network delay is paid on every single chunk request for the entire movie — before a single byte of video has arrived. Users in Asia, Africa, and South America all face this penalty.

**Problem 2 — Throughput.** Squid Game Season 3 releases. Netflix has 300 million global users — 5% are Indian, so **15 million Indian users**. Not all of them watch simultaneously — assume 1% are streaming at the same moment:

```
15 million × 1% = 150,000 concurrent users
```

Each user is watching a 1 hour episode. One hour = 3,600 seconds. Each chunk is 4 seconds of video. So every user needs to fetch:

```
chunks per user = 3,600 / 4 = 900 chunks to watch the full episode
```

150,000 users each fetching 900 chunks — that is 135 million total chunk requests. These are not all at once — they are spread across the 1 hour episode:

```
total requests      = 150,000 × 900 = 135 million requests
requests per second = 135 million / 3,600 seconds = 37,500 requests/second
```

AWS S3 has a throughput limit of **5,500 GET requests per second per prefix**:

```
demand = 37,500 requests/second
limit  =  5,500 requests/second

overflow = 32,000 requests/second throttled
         = 85% of chunk requests failing
```

> [!danger] Why single S3 bucket fails
> Two independent problems. Distance: users 13,000 km away face 200–300ms latency on every chunk request. Throughput: 150,000 concurrent Indian users generate 37,500 requests/second against S3's 5,500/second limit — 85% of requests get throttled. Either problem alone would break streaming. Together they make a single S3 bucket completely unviable at scale.

---

## Naive Fix — Replicate S3 to Multiple Regions

The obvious fix: add S3 regions close to users. A Mumbai bucket for India, a Tokyo bucket for Japan, a São Paulo bucket for Brazil. Distance drops to near zero — users now hit a local bucket. Problem 1 solved.

But Problem 2 — throughput — does not go away. The same 150,000 concurrent Indian users now hit the **Mumbai S3 bucket** instead of Virginia. The number of requests is identical:

```
demand = 37,500 requests/second
limit  =  5,500 requests/second

overflow = 32,000 requests/second throttled
         = 85% of chunk requests failing
```

Moving the bucket closer did not reduce the number of requests hitting it. 85% of Indian users still get throttled. Buffer drains. Video freezes.

> [!danger] Why multi-region S3 fails
> Replication solves distance but not load. Every user still makes a direct request to S3. The Mumbai bucket gets the exact same 37,500 requests/second that Virginia was getting — it is just geographically closer now. S3 is an origin store, not a serving layer. It was never designed to absorb millions of concurrent streaming requests.

---

## The Fix — Cache Popular Chunks Close to Users

The insight is simple: if 150,000 Indian users all want the same Squid Game chunk, why fetch it from S3 150,000 times? Fetch it **once**, store a copy on a server inside India, and serve all 150,000 users from that local copy.

S3 gets exactly **1 request** — the first time anyone asks for that chunk. Every subsequent request is served from the local cache.

```
Without cache:
150,000 users → 37,500 requests/second → Mumbai S3 → throttled (85% fail)

With cache:
150,000 users → cache server in Mumbai → 1 request to S3 (first user only)
                                       → 149,999 requests served from local cache
```

This solves both problems at once:

- **Distance** — the cache server is physically inside the user's city. Round trip latency drops to single-digit milliseconds.
- **Load on S3** — instead of 150,000 requests hitting S3, only the very first request goes to S3. S3 load drops by 99.999%.

> [!important] The key insight
> S3 is an origin store — it holds the source of truth. It was never designed to serve millions of concurrent streaming requests. The fix is to stop serving chunks directly from S3 and instead cache them on servers placed close to users worldwide.
