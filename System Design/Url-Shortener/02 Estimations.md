[[02 Design.pdf]]

### Functional Requirements
 
1. User should be able to come up on the platform, give an original URL and get a shortened version of it.
2. Whenever anyone opens the short url , they should be redirected to the original URL.
3. User can give a custom short string , and if that short string is not already used , we can allocate that to the URL.*(This is an additional feature)*

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
	2. Original Url - assume average length to be 25 chars -> 25 Byte
	3. Short Url -> assume average length to be 7 chars -> 7 Byte
	so total 8+25+7 => 40Bytes
	
	- so for 5 years we need a storage of 2.5B* 40Byte -> 100B* Byte => 100GB
	- for next 20 years - 100GB * 4 -> 400GB

---

### Non Functional Requirements

1. 500M urls per year
2. 10 Write Queries Per Second average -> 5x -> 50 qps
3. for read queries peak load can be 100x(peak write QPS) -> 5000 qps
4. Availability -> 99.9% for redirects

---

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




