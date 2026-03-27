1. Html data -> Blob storage like AWS s3
2. Site metadata -> Url of the site , last crawled time,robot.txt,s3 link of html content
3. Sites to visited (like one website can have many links contained inside it for it's own pages or other website's webpages ) -> we can use BFS to parse such trees, choosing BFS over DFS because let's say we want to travel till 50 depth of hyperlinks even in DFS we can do this but it is more complex to design .In BFS we can use distributed Queue also making a distributed Stack for DFS is more more complex than making a distributed Queue because it is already a solved problem in form of Kafka , amazon SQS etc etc and we are not getting any extra benefit of using DFS.


Using MongoDB for metadata storage because we have to also store robots.txt and this file contains key value pair of data.
and also we do not have any relational requirements too.

Whenever we have to parse any URL then in that case we will get some more URLs and even for those urls we have to do parsing.

so when a new HTML content is added or updates we parse it in Page reader service which would use s3 link fro metadata fetches the html content from s3 and from that HTML when we get new hyperlinks and then this service put back the nested hyperlinks inside the Queue.

![[Excalidraw/Drawing 2026-03-27 12.34.55.excalidraw]]


one of the potential bottleneck in this design is DNS , if we crawl Wikipedia then inside it we will have million other urls and if we hit every url to DNS to get the IP then we would get rate limit by DNS which can cause problems around performance , so instead of relying on one DNS we should try to move to multiple DNS infra.

We can introduce some level of caching layer , so we can put response from DNS inside this Redis cache with TTL.

![[Excalidraw/Drawing 2026-03-27 13.49.05.excalidraw]]


when we are going to crawl wikipedia urls then it wil give us more wikipedia urls and we add them to the distributed queue so we may hit lot of wikipedia url, so we can get rate limit by wikipedia itself.

> When we are adding new urls to distributed queue instead of putting all the urls inside the same topic we can distribute them across multiple topics assuming we are using Kafka and for every topic we have some priority so from queue-A we can pick more urls to parse instead of queue-B etc. so we have to devise a strategy using our queueing infra to have different priorities for urls to avoid DDOS on a site which lot of internal self hyperlinks. 

when we are hitting a particular URL say wikipedia/google , wikipedia/apple then both of these have common domain so apart from this URL collection(url,lastCrawledAt,s3Link,id ,robot.txt) we can have domain collection(domain,lastcrawledAt ,robot.txt) , so from last crawled of domain we can check that if this domain was crawled recently then do not need to add it inside the queue and whenever we are putting back the data inside the queue we can have a job schedular that would add different-different hyperlinks inside the distributed queue according to the crawl delay , for example let's say we find 10 more hyperlinks we add a delay of 10 seconds atleast.at 10:40 we found 10 new urls then at 10:50 first url would be added inside the queue then 10:60 next one and so on.

![[Excalidraw/Drawing 2026-03-27 14.05.30.excalidraw]]
why not use proxy when crawl node is going to hit the website ? but for 1 million hyperlinks of wikipedia how many proxies are we gonna deploy ?

> Web crawler node should be self aware about rate limits , instead of hitting the website and then relies that it has rate limit us.we should self rate limit us. we should have our own late rimiter which would be redis based token rate limitter.


We should not be storing the same data again and again , so when we get the data from any website instead of directly put it inside the s3 we should first put it inside the metadata store where we can store some kinda hash of the data , so now if recrawling happens we can directly match the hash if it matches then we know the data is still the same.so we do not restore that data and we can directly point the old s3 url to new website as well(like if it was a new website but the content was similar to already present website).

## The First Approach — Hash Index (Metadata Store)

When you crawl a page you generate a **hash of its content**. Think of a hash as a fingerprint of the content.

```
MD5("Two Sum problem content...") = "a3f8c2d1"
```

Same content will always produce the same hash. Even one character change produces a completely different hash.

---

## What you store in the metadata store

A simple key-value structure:

```
Hash          →   S3 URL
"a3f8c2d1"   →   s3://bucket/two-sum.html
"b7e2f9a4"   →   s3://bucket/binary-search.html
```

---

## How it works in 3 scenarios

**Scenario 1 — Brand new page, never seen before**

```
Crawl page → generate hash "a3f8c2d1"
Check metadata store → hash not found
Store HTML in S3 → s3://bucket/two-sum.html
Save hash → "a3f8c2d1" : s3://bucket/two-sum.html
```

**Scenario 2 — Re-crawling same page, content unchanged**

```
Re-crawl leetcode.com/two-sum → generate hash "a3f8c2d1"
Check metadata store → hash FOUND
Content hasn't changed → skip S3 write
Just point to existing s3://bucket/two-sum.html
```

**Scenario 3 — New website, same content as existing page**

```
Crawl newsite.com/two-sum → generate hash "a3f8c2d1"
Check metadata store → hash FOUND
Different URL but identical content
Don't store again → just point newsite.com/two-sum to existing s3://bucket/two-sum.html
```

This is the part you mentioned — _"point the old S3 URL to the new website"_. You're not duplicating storage, just adding a new pointer to existing content.

---

## The full picture

```
Crawl page
    ↓
Generate hash
    ↓
Check metadata store
    ↓
Hash exists? ──── YES ──→ reuse existing S3 URL, no new storage
    ↓
    NO
    ↓
Store in S3
    ↓
Save hash → S3 URL mapping in metadata store
```

---

## The Second Approach — Bloom Filter

A Bloom Filter is a **memory efficient data structure** that answers one question:

_"Have I seen this URL before?"_

It answers either:

- **Definitely NO** — never seen this URL
- **Probably YES** — likely seen this URL before

Notice it never says **definitely YES**. That's the tradeoff — it can have false positives but never false negatives. We'll come back to this.

---

## What you store in the Bloom Filter

Just the URLs you've already crawled. No S3 URLs, no hashes of content. Just:

```
"leetcode.com/two-sum"        → marked as seen
"leetcode.com/binary-search"  → marked as seen
"leetcode.com/reverse-linked-list" → marked as seen
```

---

## How it works in 3 scenarios

**Scenario 1 — Brand new URL, never crawled before**

```
Discover leetcode.com/merge-sort
Check Bloom Filter → "Definitely NOT seen"
Proceed to crawl the page
After crawling → mark "leetcode.com/merge-sort" in Bloom Filter
```

**Scenario 2 — URL already crawled**

```
Discover leetcode.com/two-sum again
Check Bloom Filter → "Probably seen before"
Skip crawling entirely
No network request made ✅
```

**Scenario 3 — False positive (Bloom Filter's weakness)**

```
Discover leetcode.com/new-problem (brand new, never crawled)
Check Bloom Filter → "Probably seen before" ← WRONG ANSWER
Skip crawling this page entirely
This page never gets crawled ❌
```

This is the risk of Bloom Filters — occasionally a new URL gets incorrectly flagged as already seen and gets skipped. In practice the false positive rate is kept very low, around **1%**, which is acceptable.

---

## The full picture

```
Discover URL
    ↓
Check Bloom Filter
    ↓
"Probably seen"? ── YES ──→ Skip, don't crawl
    ↓
    NO
    ↓
Crawl the page
    ↓
Mark URL in Bloom Filter
    ↓
Process and store content
```

---

## Why Bloom Filter and not just a Hash Set?

Great question. You could use a regular Hash Set to track visited URLs. But:

```
10B URLs × average URL size ~100 bytes
= 10^10 × 100 = 10^12 bytes = 1TB just to store URLs
```

1TB of RAM just for URL deduplication is expensive and impractical.

Bloom Filter stores the same 10B URLs in roughly **~10GB of memory** — 100x more efficient. That's why it's used.

---

## Side by side now

```
Discover URL
    ↓
BLOOM FILTER CHECK ← "have I crawled this URL before?"
    ↓ No
Crawl the page, get HTML
    ↓
Generate hash of content
    ↓
HASH INDEX CHECK ← "have I stored this content before?"
    ↓ No
Store in S3
```

Bloom Filter = guards the **crawling step**

Hash Index = guards the **storage step**
