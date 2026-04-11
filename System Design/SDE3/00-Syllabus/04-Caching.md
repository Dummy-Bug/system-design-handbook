## Phase 4 — Caching (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Caching (Patterns like Cache-aside, Write-through, Eviction like LRU/LFU, TTLs, Distributed Caching with Redis, Basic cache problems like Stampede/Penetration).
> **SDE-3 Focus:** Moving from "how to use a cache" to "how to orchestrate global cache tiers, edge compute, and cache-consistency at global scale."

### 4.1 — Global Cache Orchestration (Extension of SDE-2 4.1 & 4.5)
*In SDE-2, you know Redis. In SDE-3, you manage a multi-region global cache fabric.*

- **Multi-Region Cache Sync:** Handling cache consistency when a write happens in US-East but the read happens in Asia-South. "Invalidate-All" vs. "Sync-to-All" tradeoffs.
- **Cache Warming at Scale:** Proactively populating the cache for 100M+ keys without crushing the DB during a new region rollout or after a massive cluster failure.
- **Global Hot-Key Mitigation:** Beyond local in-memory replicas—using "Edge Caching" and "Anycast" to absorb a 100M+ QPS spike for a single key (e.g., a celebrity's live tweet).

### 4.2 — Edge Compute & Cache Logic (Extension of SDE-2 4.1 & 1.10)
*In SDE-2, you use a CDN for static files. In SDE-3, you move logic to the Edge.*

- **Compute@Edge (Fastly VCL / Cloudflare Workers):** Moving auth, A/B testing, and "Personalized Feed Fragments" to the edge to avoid the 100ms round-trip to the origin.
- **Cache Key Normalization at Edge:** Using edge logic to strip query params, normalize headers (e.g., `Accept-Encoding`), and increase cache hit ratios by 20%+.
- **ESI (Edge Side Includes):** Stitching together a page from multiple cached fragments with different TTLs at the edge server.

### 4.3 — Advanced Cache Consistency (Extension of SDE-2 4.4)
*In SDE-2, you know TTLs. In SDE-3, you manage strict consistency.*

- **Lease-Based Caching:** Using leases (e.g., Facebook's McRouter approach) to prevent a "Stale Write" from overwriting a "Fresh Write" during high concurrency.
- **Probabilistic Early Recomputation (PER):** Avoiding the "Cache Stampede" not just with locks, but by having a small % of clients recompute the key *before* it expires based on a probability curve.
- **Two-Level Distributed Invalidation:** How a central DB write triggers an invalidation event that propagates to 50+ Redis clusters globally in <200ms.

### 4.4 — Caching Economics & Observability (Extension of SDE-2 4.1 & 12)
*In SDE-2, you track Hit Ratio. In SDE-3, you optimize the "Total Cost of Ownership" (TCO).*

- **Cache Hit Ratio vs. Origin Latency:** Calculating the "Sweet Spot" where adding 1TB of RAM to Redis saves $10k/month in DB scaling costs.
- **The "Uncacheable" Problem:** Identifying workloads where caching actually *increases* latency (e.g., high-churn metadata) and knowing when to "Bypass Cache" entirely.
- **Negative Caching at Scale:** Protecting against a "DDoS of 404s" by caching the *absence* of data with Bloom filters and short-lived "No-Found" entries.
