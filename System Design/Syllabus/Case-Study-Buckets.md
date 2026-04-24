# Case Study Buckets

Comprehensive organization of system design case studies across leetdezine.com. Each bucket groups case studies by domain. Within a bucket, order is logical — later case studies build on earlier ones. Each case study has at least one **unique concept** that other case studies may reference.

> [!info] Level calibration happens later
> This list covers SDE-2, SDE-3, and SDE-3+ scope. Individual case studies will be tagged to their correct level once written. For now, the focus is on **breadth of coverage** and **logical dependency order**.

---

## Bucket 1 — Search & Discovery

| Order | Case Study | Unique Concept | Borrows From | Status |
|---|---|---|---|---|
| 1 | Web Crawler | Distributed BFS, URL frontier, politeness, robots.txt | — | Not started |
| 2 | Search Engine (Google Search) | Inverted index, PageRank, query processing at web scale | Web Crawler (input) | Not started |
| 3 | Top-K Heavy Hitters | Count-Min Sketch, min-heap, sliding window | — (algorithmic) | Not started |
| 4 | Type-Ahead / Autocomplete | Trie, prefix search, ranking suggestions | Top-K (for popular suggestions) | Not started |

---

## Bucket 2 — Social Media

| Order | Case Study | Unique Concept | Borrows From | Status |
|---|---|---|---|---|
| 1 | Instagram | Feed fan-out (write vs read) | — | In progress |
| 2 | YouTube | Upload + transcoding + adaptive bitrate | Top-K (trending videos) | Not started |
| 3 | Reddit | Voting/ranking, communities, nested comments | Instagram (feed), Top-K (top posts) | Not started |
| 4 | Twitter | Real-time search + type-ahead | Instagram (feed), Top-K (trending), Notification System, Type-Ahead | Not started |
| 5 | Snapchat | Ephemeral media, view-once, TTL deletion, Snap Map | Instagram (feed), YouTube (storage), Uber (geospatial, cross-bucket) | Not started |
| 6 | TikTok | For You Page — pure ML recommendation feed | Instagram (feed), YouTube (video delivery) | Not started |
| 7 | WhatsApp | WebSocket, real-time messaging, offline delivery | — (standalone) | Done ✅ |
| 8 | LinkedIn | Graph traversal, People You May Know, degrees of connection | Instagram (follow graph), WhatsApp (DMs), Twitter (search) | Not started |

---

## Bucket 3 — Location & Delivery

| Order | Case Study | Unique Concept | Borrows From | Status |
|---|---|---|---|---|
| 1 | Google Maps | Routing algorithms (Dijkstra/A*), shortest path, traffic data | — | Not started |
| 2 | Uber | Geospatial indexing (Geohash/S2), real-time driver matching | Google Maps (routing), Payment (cross-bucket) | Not started |
| 3 | Zomato / Blinkit | Last-mile delivery, ETA estimation, order tracking | Uber (geospatial), Google Maps (routing), Payment (cross-bucket) | Not started |
| 4 | Airbnb | Location-based search + reservation | Uber (geospatial), Hotel Reservation (booking) | Not started |

---

## Bucket 4 — Fintech

| Order | Case Study | Unique Concept | Borrows From | Status |
|---|---|---|---|---|
| 1 | Payment System | Idempotency, exactly-once, append-only ledger | — | Not started |
| 2 | Hotel / Ticket Reservation | MVCC, SERIALIZABLE, overbooking prevention | Payment (idempotent confirmation) | Not started |
| 3 | Stock Exchange | Order matching engine, price-time priority, low latency | Payment (exactly-once), Reservation (concurrency) | Not started |
| 4 | Banking Ledger | Double-entry bookkeeping at scale, append-only | Payment (ledger foundation) | Not started |
| 5 | Splitwise | Debt simplification, graph reduction algorithm | Payment (ledger) | Not started |

---

## Bucket 5 — Storage & Productivity

| Order | Case Study | Unique Concept | Borrows From | Status |
|---|---|---|---|---|
| 1 | Dropbox / Google Drive | Chunking, delta sync, content-addressable storage, dedup | — | Not started |
| 2 | Google Docs | Real-time collaboration, OT/CRDT | Dropbox (file storage), WhatsApp (WebSocket real-time, cross-bucket) | Not started |
| 3 | Gmail | Email threading, large attachments, spam filtering | Dropbox (attachments), Search Engine (cross-bucket) | Not started |
| 4 | Notion | Hierarchical block documents, permissions | Dropbox (storage), Google Docs (collaboration) | Not started |
| 5 | Calendar | Scheduling, recurrence rules, timezone handling | — (standalone) | Not started |

---

## Bucket 6 — Media Streaming

| Order | Case Study | Unique Concept | Borrows From | Status |
|---|---|---|---|---|
| 1 | Netflix | VOD, HLS/DASH, adaptive bitrate, CDN at scale | — | Done ✅ |
| 2 | Twitch | Live streaming, RTMP ingest, sub-second viewer latency | Netflix (CDN, adaptive bitrate) | Not started |
| 3 | Spotify | Audio streaming, offline download, recommendations | Netflix (CDN), Recommendation System (cross-bucket) | Not started |

---

## Bucket 7 — E-commerce

| Order | Case Study | Unique Concept | Borrows From | Status |
|---|---|---|---|---|
| 1 | Amazon | Product catalog, shopping cart, inventory management | Search Engine (cross-bucket), Payment (cross-bucket) | Not started |
| 2 | eBay | Auction, real-time bidding, race conditions | Amazon (catalog), Payment (transactions) | Not started |
| 3 | Shopify | Multi-tenant merchant platform, isolation | Amazon (catalog), Payment (per-merchant ledger) | Not started |

---

## Bucket 8 — Real-time Communication

| Order | Case Study | Unique Concept | Borrows From | Status |
|---|---|---|---|---|
| 1 | Zoom | WebRTC, STUN/TURN/ICE, video conferencing | — | Not started |
| 2 | Slack | Channels, threads, presence | WhatsApp (real-time messaging) | Not started |
| 3 | Discord | Voice channels, server/channel hierarchy | Zoom (voice), Slack (channels) | Not started |

---

## Bucket 9 — Data & Analytics

| Order | Case Study | Unique Concept | Borrows From | Status |
|---|---|---|---|---|
| 1 | Ad Click Aggregation | Stream processing, windowing, Flink/Kafka Streams | Top-K (cross-bucket) | Not started |
| 2 | A/B Testing Platform | Experiment allocation, statistical significance | — | Not started |
| 3 | Recommendation System | Collaborative filtering, embeddings, vector similarity | — | Not started |
| 4 | Monitoring (Prometheus/Grafana) | Time-series DB, high-cardinality metrics, alerting | — | Not started |
| 5 | Log Aggregation (ELK) | Log ingestion, full-text log search | Search Engine (cross-bucket) | Not started |

---

## Bucket 10 — Infrastructure Primitives

Foundational building blocks referenced by every other case study.

| Order | Case Study | Unique Concept | Status |
|---|---|---|---|
| 1 | URL Shortener | Short-code generation, redirect at scale | Done ✅ |
| 2 | Rate Limiter | Token bucket, sliding window, distributed Redis counters | Done ✅ |
| 3 | Unique ID Generator | Snowflake, 64-bit ID structure | Done ✅ |
| 4 | Pastebin | Blob storage, dedup, expiry | Done ✅ |
| 5 | KV Store | Consistent hashing, quorum, hinted handoff | Done ✅ |
| 6 | Notification System | Kafka fan-out, DLQ, retry, multi-channel | Done ✅ |
| 7 | Distributed Task Queue | Priority queues, delayed jobs, retries at scale | Not started |
| 8 | Message Queue (Kafka internals) | Partitions, offsets, consumer groups | Not started |
| 9 | API Gateway | Routing, auth, rate limiting, transformation | Not started |
| 10 | Load Balancer | L4 vs L7, health checks, consistent hashing routing | Not started |

---

## Bucket 11 — Gaming

| Order | Case Study | Unique Concept | Borrows From | Status |
|---|---|---|---|---|
| 1 | Leaderboard | Redis sorted set operations at scale | — | Not started |
| 2 | Matchmaking System | Player pairing, skill rating (Elo) | — | Not started |
| 3 | Online Multiplayer Game | State sync, anti-cheat, low-latency UDP | Matchmaking (pairing) | Not started |

---

## Cross-Bucket References

Some case studies are referenced across buckets. This keeps content DRY — the reader clicks through to the primary case study instead of seeing the same content duplicated.

| Primary Case Study | Referenced By |
|---|---|
| **Notification System** | Twitter, Reddit, LinkedIn, Zomato, Instagram |
| **Payment System** | Uber, Zomato, Airbnb, Amazon, eBay, Shopify |
| **Search Engine** | Gmail (search), Log Aggregation, Amazon (product search) |
| **Top-K Heavy Hitters** | YouTube, Reddit, Twitter, Ad Click Aggregation |
| **WhatsApp** | Google Docs (WebSocket real-time), Slack |
| **Dropbox** | YouTube (object storage mental model), Google Docs, Gmail, Notion |
| **Uber (geospatial)** | Zomato, Airbnb |

---

## How to Use This Document

1. **Building new case studies** — pick from the "Not started" rows. Follow the order within the bucket so dependencies are already written.
2. **Level tagging** — each case study will be tagged SDE-1/2/3/3+ once written, based on the depth covered. A single topic can appear at multiple levels with different depth.
3. **Website navigation** — buckets become the top-level categories on leetdezine.com. Each bucket is a landing page listing its case studies in order.
