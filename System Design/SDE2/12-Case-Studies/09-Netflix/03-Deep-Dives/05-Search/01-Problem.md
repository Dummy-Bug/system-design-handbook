# Search Deep Dive — The Problem With LIKE at Scale

## What LIKE Actually Does

When the base architecture runs `SELECT * FROM movies WHERE title LIKE '%leo%'`, PostgreSQL cannot use any index on the title column. The reason is the leading wildcard — `%leo%` means "leo can appear anywhere in the string." An index on title is sorted alphabetically. To find all strings containing "leo" somewhere in the middle, PostgreSQL has no choice but to open every single row and scan the raw text character by character.

This is called a **full table scan**. For 20,000 movie titles it takes maybe 10ms — acceptable. The problem is that the search runs across far more than just titles.

---

## The Real Scope of a Netflix Search Query

A user searching "leo" expects to find:

- The animated show *Leo* — title match
- *Inception* — Leonardo DiCaprio stars in it, cast field match
- *The Aviator* — DiCaprio again, cast field match
- *Romeo + Juliet* — "leo" in the description ("Leonardo DiCaprio plays Romeo")

This means the query has to scan title, cast, description, and genre fields — across 20,000 movies and 600,000 episodes. That is 620,000 rows with multiple text columns each.

```
620,000 rows × 4 text columns = 2.48 million text fields scanned per query
```

At 20,000 titles this is still manageable. But short search prefixes make it worse. A user typing just **"st"** matches hundreds of thousands of rows — Stranger Things, Star Wars, Stripes, The Sting, Stardust, every episode of every show with "st" anywhere in any field.

---

## The Scale Problem

Netflix has 150M DAU. Search is not rare — users search whenever they want something specific. Assume 1% are searching at any given moment:

```
1% of 150M = 1.5M search queries per minute
           = 25,000 queries per second
```

Each of those 25,000 queries is a full table scan across 2.48 million text fields. And this is happening on the same PostgreSQL instance that is also:

- Serving homepage genre rows for 150M DAU
- Handling movie detail page loads
- Processing cast lookups for recommendations

At normal load, PostgreSQL handles the homepage traffic comfortably with indexed reads. Full-text scans are a completely different workload — they are CPU-heavy, IO-heavy, and unindexable. Adding 25,000 of them per second onto the same database that powers everything else collapses the entire content serving layer.

```
Normal PostgreSQL read (indexed)     → microseconds, low CPU
LIKE full scan (unindexed)           → milliseconds, high CPU
25,000 full scans/second             → database saturates
Homepage loads, detail pages, cast   → all slow down or fail
```

> [!danger] Search pollutes the entire content database
> A `LIKE` query competes for the same CPU, IO, and connection pool as every other query on that database. At 25,000 searches per second, the search load doesn't just slow down search — it slows down every other read on the same instance. Hitting the genre service for the homepage takes longer. Movie detail pages load slower. Everything degrades together.

---

## The Second Problem — Typos

Even if the performance problem were solved, `LIKE` has a correctness problem. It only matches exact substrings.

A user types **"strannger things"** — one extra "n". `LIKE '%strannger%'` returns zero results. The user gets a blank search page for one of Netflix's most popular shows.

```
LIKE '%strannger%' → no match
LIKE '%stranger%'  → Stranger Things ✅
```

These differ by exactly one character — one extra "n". To a human, these are obviously the same word. To `LIKE`, they are completely different strings with no relationship.

Typos, fast typing, non-native speakers spelling phonetically — these happen constantly. A search system that returns zero results for a one-character mistake is not a search system users trust.

---

## What Is Actually Needed

Two problems that `LIKE` on PostgreSQL cannot solve:

```
Problem 1 — Performance
  25,000 full table scans/second on a shared database
  → need a dedicated system with a pre-built search index

Problem 2 — Typo tolerance
  Exact substring matching fails on any misspelling
  → need fuzzy matching that tolerates 1-2 character differences
```

Both are solved by a purpose-built search engine — covered in the next file.
