## Functional 

1. Given a set of seed URLs, crawl all reachable pages and store their HTML content
2. Extract links from crawled pages and crawl those recursively
3. Support adding new seed URLs to the system at any time
4. Avoid crawling the same URL twice in the same crawl cycle
5. Periodically start a new crawl cycle to re-crawl pages and capture updates
6. Respect `robots.txt` — don't crawl pages a website has disallowed

## Estimations

- There are around 1.42 Billion websites on the internet and out of them around 200-210M are active websites. Roughy 200K new websites are created every single day that are 3 new sites per second.
- So if each website has say 10 pages then we end up crawling 10B individual pages.

Throughput
```Math

10 days  → 10B pages
1 day    → 1B pages
1 second → 1B / 86,400 ≈ 10,000 pages/second
```

Storage
```Math

Assuming every page is around -> 1MB per site -> 10^6 Bytes per page

10^10 pages -> 10^10 * 10^6
-> 10^16 -> 10PB of data

For future proofing we might have to store 5x of data so 50PB of data.

We have to crawl 10k pages per second
1Page -> 1MB of data 
so 10^6Bytes * 10^4 -> 10^10 -> 10GB of data per second we are downloading 
1Byte -> 8 Giga bits
**10GB -> 80Giga bits

hence to download 10GB of data per second we need 80Gbps of bandwidth

The bandwidth given by normal machines is around 1Gbps , so we might have to be aware that how powerful machines we have so that we can know how many machines we gonna need for achieing 10GB download per second .

High-end machines like EC2 instances can support up to 200Gbps of network bandwidth, however in practice we should not assume full utilization. Accounting for overhead from other processes, OS networking stack, and shared infrastructure, a realistic usable bandwidth is around 25% — so effectively ~50Gbps per machine.

Since we need 80Gbps total, theoretically 2 such machines suffice for bandwidth alone. However in practice we would provision more to account for peak load , fault tolerance and headroom
```


## Final estimations

```
Total pages        = 10B
Throughput         = ~10,000 pages/second
Page size          = ~1MB
Storage            = ~10PB
Data ingestion     = ~10GB/second
Network bandwidth  = ~80 Giga bits per second
Machines needed    = ~10 minimum (bandwidth alone)
```

## Non Functional

1. **Fault tolerant** — if a crawler worker crashes, no URLs should be lost or skipped
2. **Horizontally scalable** — should handle crawling 10B pages within 10 days.
3. **Scalable storage** — capable of storing ~50PB of raw HTML
4. **Polite** — respect per domain rate limits, avoid overwhelming any single server


## Network Bandwidth

This is about **fetching** — how much data is coming **in from the internet** into your crawler machines.

```
Crawler machines ←——— 10GB/second ——— Internet (LeetCode, Google, etc.)
```

This is an **inbound network** concern. Do your crawler machines have enough network capacity to pull 10GB/second from external servers?

---

## Data Ingestion

This is about **storing** — how much data is being **written into your storage system** from your crawler machines.

```
Crawler machines ———— 10GB/second ——→ Storage System (S3, HDFS)
```

This is a **write throughput** concern. Can your storage system handle 10GB/second of writes?

---

## Why they're the same number here

Because we're storing every page we fetch without any filtering or compression. So whatever comes in from the internet goes straight to storage.

But imagine if you compressed the HTML before storing:

```
Network bandwidth = 10GB/second  (raw HTML coming in)
Data ingestion    = 2GB/second   (compressed HTML going to storage)
```

Now they diverge. So they're the same number **by coincidence of our assumptions**, not by definition.






