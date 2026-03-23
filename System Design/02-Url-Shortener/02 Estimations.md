[[02 Design.pdf]]

### Functional Requirements
 
1. User should be able to come up on the platform, give an original URL and get a shortened version of it.
2. Whenever anyone opens the short url , they should be redirected to the original URL.
3. User can give a custom short string , and if that short string is not already used , we can allocate that to the URL.*(This is an additional feature)*

---
## Non-Functional Requirements

1. High availability for redirects → **99.9% uptime**
2. Low latency redirects → **< 100ms p99**

---

### Assumptions and Calculations

* **MAU**
	Assuming 1Million as monthly active users.
	50% of this create on an average 2 short urls daily.
	it means 1M short urls daily -> 400M short URLs in one year. assume peak
	year can have 500M short URLS.
	
* **QPS**
	1M short urls in one day =>  1M / 100,000(seconds) -> 10 QPS 

* **Storage**
	* We want to run this service for next **20 years**
		500M* 5Years = 2500M urls -> 2.5B urls
		so for 20 years -> 500M* 20Years  = 10,000M -> 10B urls in total

	**Schema**
	*(Pk , Original Url , shortUrl)*
	1. PK - BigInt -> 8Bytes
	2. Original Url - assume average length to be 25(200-300 chars nowdays so 200Bytes) chars -> 200 Byte
	3. Short Url -> assume average length to be 12 chars -> 12 Byte
	so total 8+200+12 ~ 250Bytes including metadata
	
- for 5 years: 500M * 250Bytes = 125GB 
- for 20 years: 125GB * 4 = 500GB

---

---
## System Capacity

1. 500M URLs/year
2. ~10 QPS average writes → 5x peak → **50 QPS peak writes**
3. Read:Write ratio = 100:1 (URL shorteners are extremely read-heavy; a single viral link can get millions of hits) → ~1000 QPS average reads → 5x peak → **5000 QPS peak reads**
4. Storage: 125 GB (5 years), 500 GB (20 years)

### Why Cache Is Mandatory (Not Optional)

Key observation:

- Writes: **~50 QPS**
- Reads: **~5000 QPS** 
- Read/Write ratio = **100:1**

Hitting MySQL for every redirect:

- Increases latency
- Burns DB connections
- Breaks 99.9% SLA under spikes

➡️ **Redirects must be served from cache**



## How to calculate Read factor

---

**Way 1: Bottom-up from user behavior (preferred)**

Think about what actually happens with a short URL:

- Someone creates 1 short URL → then **shares it** on WhatsApp, Twitter, email, etc.
- That 1 URL gets clicked by maybe **50–200 different people**
- So for every 1 write, you get ~100 reads

That's your 100:1 ratio — it comes directly from the nature of the product, not a magic number.

---

**Way 2: Top-down from MAU**

You already have:

- 1M MAU, 50% are **creators** → 500K creators
- The other 50% are **pure consumers** (they only click links, never create)
- Plus creators themselves also click other links

So your **reader pool is much larger than your writer pool** — easily 100x.

---

**How to say it in an interview**

> _"URL shorteners are inherently read-heavy. A single URL gets created once but can be clicked by hundreds of people — think a viral WhatsApp forward or a tweet. I'll conservatively assume 100 reads per write, giving a 100:1 ratio. That means ~1000 QPS average reads and ~5000 QPS at peak."_

That one sentence of justification is all the interviewer needs. The exact number (100x vs 80x vs 150x) doesn't matter — **the reasoning does.**




