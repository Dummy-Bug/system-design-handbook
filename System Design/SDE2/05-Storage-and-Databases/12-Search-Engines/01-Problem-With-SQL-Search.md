# The Problem With SQL Search

## Start With the Naive Approach

You're building product search for an e-commerce site. You have a `products` table with 50 million rows. A user types **"wireless noise cancelling headphones"** in the search bar.

The obvious SQL query:

```sql
SELECT * FROM products
WHERE description LIKE '%wireless%'
  AND description LIKE '%noise%'
  AND description LIKE '%headphones%';
```

This looks reasonable. It works on a small dataset. But on 50 million rows, it falls apart completely — and it fails in two separate ways.

---

## Problem 1 — Performance

The `LIKE '%wireless%'` pattern has a leading wildcard. This means the database cannot use a B+Tree index at all — it has no idea where in the string the word might appear, so it has to check every character of every row.

The result: a **full table scan on every single search query**. Every user keystroke, every search — 50 million rows scanned from top to bottom. At scale this saturates your database, competes with live transactional traffic, and causes latency spikes across the entire system.

This is an O(n) operation where n is your total document count. There is no indexing trick in SQL that fixes a leading-wildcard `LIKE`.

---

## Problem 2 — Relevance (The Harder Problem)

Even if performance wasn't an issue, SQL search returns wrong results.

Say a product description reads:

> "Premium over-ear headphone with active noise cancellation and wireless Bluetooth"

The user searched for **"noise cancelling headphones"**.

The SQL query checks for the exact string `cancelling`. The document contains `cancellation`. These are different character sequences. SQL returns nothing — the product is invisible to the user despite being exactly what they want.

SQL has no concept of meaning, word variation, or linguistic similarity. It only knows: does this exact sequence of characters exist in this string?

> [!danger] The exact-match trap
> SQL `LIKE` is character matching, not meaning matching. "cancelled", "cancelling", "cancellation" are all the same concept to a human — and completely different strings to SQL.

---

## Problem 3 — No Ranking

Even if SQL could find all relevant documents, it has no way to sort them by relevance. Which product should appear first — the one where "headphones" appears once in a 5000-word description, or the one where it appears 20 times in a 100-word title? SQL treats them identically.

Users expect Google-style results: most relevant first. SQL cannot deliver this.

---

## Summary — Three Failures

```
SQL Search Failures:
┌─────────────────┬──────────────────────────────────────────┐
│ Performance     │ Full table scan, O(n), no index possible  │
│ Relevance       │ Exact match only, misses word variations  │
│ Ranking         │ No concept of "most relevant first"       │
└─────────────────┴──────────────────────────────────────────┘
```

SQL was designed for structured queries on exact values — not for understanding human language. The moment users type free text, you need a completely different tool built for exactly this problem.

That tool is built on an **inverted index**.
