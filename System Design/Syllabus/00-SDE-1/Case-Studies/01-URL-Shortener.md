# URL Shortener

## Problem Statement
- What we're building
- Core user flows (shorten a URL, redirect a short URL)
- Out of scope for SDE-1 (analytics, custom aliases, expiry)

## Functional Requirements
- Create a short URL from a long URL
- Redirect short URL to original
- URL must be unique

## Non-Functional Requirements
- Reads are far more common than writes
- Short codes must not collide
- Low latency on redirect

## Capacity Estimation
- DAU, read/write ratio
- Storage per URL, total storage
- QPS for reads and writes

## High-Level Design
- Client → API server → DB
- Redirect flow
- Short code generation (hash vs random)

## Deep Dives
- Short code generation — MD5 hash, base62 encoding, collision handling
- Database choice — why SQL works here
- Caching redirects — what to cache, TTL, cache-aside
- What happens when the same long URL is shortened twice
