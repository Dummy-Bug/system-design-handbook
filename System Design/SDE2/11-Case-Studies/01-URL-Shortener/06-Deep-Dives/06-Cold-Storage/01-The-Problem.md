
> [!info] Not all URLs are equal — and treating them the same wastes a lot of money
> After 10 years, you have 50 billion URLs taking up 250TB of storage. But the vast majority of that data is never accessed. Keeping it all on expensive SSD is the wrong call.

---

## The access pattern reality

URLs are not uniformly accessed. A small fraction of URLs — the viral ones, the active campaigns, the popular links — absorb almost all the traffic. The rest sit untouched.

The 80/20 rule applies hard here:

```
~20% of URLs  →  80%+ of all redirects   (hot: recent, viral, active campaigns)
~80% of URLs  →  almost zero traffic      (cold: old, forgotten, one-time use)
```

In practice it's even more skewed than 80/20. Think about your own behaviour — how often do you click a link from a tweet that's 3 years old?

---

## The cost problem

Your storage estimate over 10 years:

```
50B URLs × 500 bytes per row = 25TB raw data
With indexes and overhead    = ~250TB total
```

All 250TB currently lives on SSDs in your DB shards. SSD storage costs roughly $0.10–$0.20 per GB per month. At 250TB:

```
250,000 GB × $0.15/GB/month = $37,500/month just for storage
```

Now consider: 80% of that data — 200TB — is URLs that haven't been clicked in months or years. You're paying $30,000/month to store data nobody is accessing.

S3 (object storage) costs $0.023/GB/month — roughly 6x cheaper than SSD:

```
200TB cold on S3:  200,000 GB × $0.023 = $4,600/month
200TB cold on SSD: 200,000 GB × $0.15  = $30,000/month

Savings: ~$25,400/month
```

The solution is **tiered storage** — keep hot URLs on fast SSD in the DB, move cold URLs to cheap object storage like S3.

---

> [!tip] Interview framing
> "After 10 years we have 250TB of URL data, but the 80/20 rule means ~80% of that data is cold — URLs that haven't been accessed in months. Keeping all of it on SSD is expensive. Tiered storage moves cold URLs to S3 at ~6x lower cost, keeping only hot URLs in the DB where fast random access matters."
