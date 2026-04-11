## Phase 1 — Networking & Global Traffic (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Networking (OSI, TCP/UDP, DNS basics, HTTP/1-3, WebSockets).
> **SDE-3 Focus:** Moving from "how a request works" to "how to manage global traffic, edge compute, and protocol-level optimization."

### 1.1 — Global Traffic Management (Extension of SDE-2 1.1 & 1.4)
*In SDE-2, you know DNS resolution. In SDE-3, you manage global steering.*

- **Anycast Routing:** How one IP address can exist in 500 data centers. Used for DNS (1.1.1.1) and Global LBs.
- **BGP (Border Gateway Protocol):** How the internet actually routes. Understanding "BGP Hijacking" and "Routing Instability" as a cause for global outages.
- **Geo-Steering & Latency-Based Routing:** Beyond simple round-robin. Using Real User Monitoring (RUM) data to update DNS weights.
- **DNS at Scale:** Handling DNS propagation lag during a regional failover. Why "TTL=0" is a lie.

### 1.2 — High-Performance Transport (Extension of SDE-2 1.3 & 1.6)
*In SDE-2, you know TCP vs UDP. In SDE-3, you optimize the handshake.*

- **0-RTT & TLS 1.3:** The mechanics of sending data in the very first packet. Security vs. performance tradeoffs (Replay attacks).
- **Congestion Control Algorithms:** BBR (Google) vs. CUBIC. When to tune the kernel's TCP stack for high-throughput vs. low-latency workloads.
- **QUIC / HTTP3 Operationalization:** Why QUIC is hard to load balance (connection ID migration) and how to handle UDP blocking on corporate firewalls.

### 1.3 — Edge Computing & Origin Protection (Extension of SDE-2 1.10)
*In SDE-2, you use a CDN for assets. In SDE-3, you move logic to the edge.*

- **Edge Workers (Cloudflare Workers / Lambda@Edge):** Running A/B testing, auth, and request normalization at the edge to reduce origin load.
- **Origin Shielding:** Using a dedicated caching layer between the CDN and the Origin to prevent "Cache Stampedes" during a cache clear.
- **Request Collapsing:** Ensuring that 10,000 concurrent misses for the same file only result in ONE request to the Origin.

### 1.4 — Advanced API Governance (Extension of SDE-2 1.12)
*In SDE-2, you design an API. In SDE-3, you manage an ecosystem.*

- **Breaking Change Management:** Strategies for versioning (Header-based vs. URL-based) when you have 1,000+ consumers.
- **Schema Evolution:** Using Protobuf/Thrift for backward/forward compatibility in high-speed internal RPC.
- **Sidecar Traffic Control:** Using a Service Mesh (Istio/Linkerd) for protocol-level retries and circuit breaking without touching application code.
