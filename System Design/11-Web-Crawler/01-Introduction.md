[Web Crawler](https://www.cloudflare.com/en-gb/learning/bots/what-is-a-web-crawler/)

When you search "best pizza near me" on Google, results appear in milliseconds. But Google isn't searching the internet _live_ in that moment. It already has a **copy of the internet** stored on its servers. That copy was built by a web crawler.

The whole pipeline has 3 stages:

```
Internet (billions of pages)
        ↓
   1. CRAWLING        ← web crawler visits pages and downloads them
        ↓
   2. INDEXING        ← organize the downloaded content so it's searchable
        ↓
   3. SEARCHING       ← user query hits the index, results come back fast
```

---

## Stage 1 — Crawling

A crawler is just a bot that does what you do manually in a browser — visits a URL, reads the page, clicks links to go to other pages — except it does this for billions of pages automatically.

**Where do seed URLs come from?**

Great question. Seed URLs are just the _starting points_. They come from:

- **Manually submitted URLs** — Google Search Console lets you tell Google "hey, my website exists"
- **Sitemaps** — websites publish a `sitemap.xml` file listing all their pages
- **Previously crawled pages** — once you crawl one page, you find links to hundreds of others. Those become new URLs to crawl. This is how the crawler _grows_ organically.
- **Old crawl data** — Google already crawled the web before. It just re-crawls periodically to catch updates.

So in practice, Google doesn't need many seeds — the web is so interlinked that starting from a few thousand popular sites, you'll eventually discover almost everything.

---

## Stage 2 — Indexing

After crawling, you have billions of raw HTML files. That's useless for search. You need to _organize_ it.

Indexing means building a structure called an **inverted index**. Think of it like the index at the back of a textbook.

Instead of:

```
Page A contains: "pizza", "cheese", "delivery"
Page B contains: "pizza", "restaurant", "NYC"
```

You flip it to:

```
"pizza"    → [Page A, Page B]
"cheese"   → [Page A]
"delivery" → [Page A]
"NYC"      → [Page B]
```

Now when you search "pizza NYC", Google looks up those two words in the index and instantly gets back the relevant pages. No need to scan billions of pages live.

This is why search is fast — the heavy work happened _before_ you searched.

---

## Stage 3 — Searching

User types a query → look it up in the inverted index → get candidate pages → rank them (PageRank, relevance, freshness, etc.) → return results.

This happens in milliseconds because the index is pre-built.

---

## Simple analogy

Think of a **library**:

- **Crawling** = a librarian going out and collecting every book in the world
- **Indexing** = organizing them by topic, author, keywords in a card catalog
- **Searching** = you ask the librarian for "books about pizza in NYC" and they check the card catalog instantly, rather than reading every book

---

So the crawler's job is really just _collection_. The intelligence of search comes from indexing and ranking, which are separate problems entirely.


Let's walk through the whole thing end to end.

---

## Step 1 — Google finds out LeetCode exists

LeetCode goes to **Google Search Console** and says "hey, my website is `leetcode.com`". They submit their **sitemap** which is just an XML file listing all their pages:

```xml
<urlset>
  <url><loc>https://leetcode.com/problems/two-sum</loc></url>
  <url><loc>https://leetcode.com/problems/reverse-linked-list</loc></url>
  <url><loc>https://leetcode.com/problems/binary-search</loc></url>
  ... (3000+ problems)
</urlset>
```

Google adds `https://leetcode.com` to its **seed URL list**. This is the starting point.

---

## Step 2 — Crawler visits LeetCode

Google's crawler (Googlebot) picks up `https://leetcode.com` from the queue and makes an HTTP request:

```
GET / HTTP/1.1
Host: leetcode.com
User-Agent: Googlebot
```

LeetCode's server responds with the HTML of the homepage. The crawler now has raw HTML in memory.

---

## Step 3 — Parser extracts links

The crawler reads through that HTML and pulls out every `<a href="...">` tag it finds:

```html
<a href="/problems/two-sum">Two Sum</a>
<a href="/problems/reverse-linked-list">Reverse Linked List</a>
<a href="/problems/binary-search">Binary Search</a>
```

It now has a list of new URLs:

```
https://leetcode.com/problems/two-sum
https://leetcode.com/problems/reverse-linked-list
https://leetcode.com/problems/binary-search
```

These get added to the **queue**.

---

## Step 4 — Crawler visits each problem page

Crawler picks `https://leetcode.com/problems/two-sum` from the queue and fetches it. The page HTML roughly contains:

```
Title: Two Sum
Difficulty: Easy
Description: Given an array of integers nums and an integer target,
return indices of the two numbers such that they add up to target.
Tags: Array, Hash Table
```

This raw content gets saved. Then the crawler moves to the next URL in the queue. It keeps doing this until every page in LeetCode is visited.

---

## Step 5 — Indexing begins

Now Google has raw content of every LeetCode page saved. But it's just a pile of HTML files — useless for search.

The indexer processes each page and builds an **inverted index**.

It reads the Two Sum page and extracts meaningful words (ignoring "the", "a", "of" etc.):

```
two, sum, array, integers, nums, target, return, indices, numbers, add, easy, hash, table
```

It does this for ALL pages and builds:

```
"two"        → [/problems/two-sum, /problems/two-pointers, ...]
"sum"        → [/problems/two-sum, /problems/subarray-sum, ...]
"array"      → [/problems/two-sum, /problems/binary-search, /problems/rotate-array, ...]
"hash"       → [/problems/two-sum, /problems/group-anagrams, ...]
"easy"       → [/problems/two-sum, /problems/reverse-linked-list, ...]
```

This index lives on Google's servers, ready to be queried instantly.

---

## Step 6 — User searches "two sum problem"

You type **"two sum problem"** in Google.

Google breaks it into tokens: `["two", "sum", "problem"]`

It looks up each word in the inverted index:

```
"two"     → [two-sum, two-pointers, ...]
"sum"     → [two-sum, subarray-sum, ...]
"problem" → [two-sum, binary-search, ...] ← almost every page matches this
```

It finds the **intersection** — pages that appear in all three lists. `two-sum` page shows up in all three. Strong match.

Then it **ranks** the results. Ranking considers things like:

- How many times do the words appear on the page?
- Are the words in the title? (yes — "Two Sum" is the title, strong signal)
- How many other sites link to this page?

`leetcode.com/problems/two-sum` comes out on top. Google returns it in milliseconds because **all of this lookup is on a pre-built index** — no live browsing happening.

---

## The full picture

```
LeetCode submits sitemap
        ↓
Googlebot fetches homepage
        ↓
Parser finds 3000 problem links
        ↓
Crawler fetches each problem page
        ↓
Indexer reads each page → extracts words → builds inverted index
        ↓
User searches "two sum problem"
        ↓
Google tokenizes query → looks up inverted index → finds matches → ranks → returns result
        ↓
Result appears in milliseconds ✓
```

The key insight is — **by the time you search, all the hard work is already done**. Google is just doing a very fast lookup on a pre-built index, not browsing the internet in real time.

