## Phase 11 — Case Studies (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Case Studies (baseline architectures, basic tradeoffs, scaling path).
> **SDE-3 Focus:** Moving beyond "how to build the system" to "how to operate, evolve, and secure the system at 100x scale, multi-region, and under extreme operational constraints."

### The "Senior Evolution" Framework (Extension of SDE-2 11)
*In SDE-2, you build the diagram. In SDE-3, you build the "Plan for Evolution."*

For every case study, assume the SDE-2 architecture is your **starting point**. In an SDE-3 loop, you must also address:
- **Zero-Downtime Migration:** How to move from the old legacy system to the new one.
- **Blast Radius Control:** How a failure in one region or tenant doesn't take down the fleet.
- **Operational Observability:** What metrics will you alert on at 3 AM?
- **Disaster Recovery (DR):** How to recover when an entire AWS region vanishes.

---

### 11.1 — Global Messaging (WhatsApp / Chat)
- **Extension of SDE-2 15:**
  - **The "Home Region" Problem:** How to manage users moving across continents while keeping latency low.
  - **Large Group "Hotspots":** Handling 1,000+ members in a group where one message causes a "Fan-out Storm."
  - **Presence at Scale:** Beyond the "online" bit—managing "Presence Storms" when 1M+ users reconnect simultaneously after a network dip.

### 11.2 — Global Feed & Ranking (Twitter / Instagram)
- **Extension of SDE-2 16:**
  - **Ranking Fallback Logic:** What does the feed look like if the ML model service has 50% latency?
  - **Denormalized Feed Recovery:** If your precomputed feed cache is lost, how do you rebuild it for 100M users without crushing the DB?
  - **Multi-Region Consistency:** Handling "Read-Your-Own-Writes" when a user posts in the US and immediately flies to Europe.

### 11.3 — High-Integrity Payments (Stripe / Ledger)
- **Extension of SDE-2 19 & 20:**
  - **The "Exactly-Once" Reality:** Moving beyond the buzzword—how to handle the "In-Doubt" transaction when the 2PC coordinator crashes halfway.
  - **Dispute & Reversal Workflows:** Designing the system to "Undo" complex financial chains safely.
  - **Auditability vs. Performance:** How to store every single version of a transaction without slowing down the hot path.

### 11.4 — Geo-Spatial Orchestration (Uber / Maps)
- **Extension of SDE-2 22 & 27:**
  - **Moving Hotspots:** Handling "New Year's Eve" in Manhattan—where 50,000 drivers and riders are all in the same 1km geohash.
  - **ETA Pipeline Isolation:** Separating the "Ride Request" path from the "ETA Estimation" path so that a slow ETA service doesn't stop people from booking rides.
  - **Global Geo-Sharding:** How to move shard boundaries dynamically as traffic moves across the globe during the day.

### 11.5 — Collaborative Editing (Google Docs)
- **Extension of SDE-2 28:**
  - **CRDT vs. OT in Production:** The operational reality—handling "Metadata Growth" in CRDTs and "Serialization Bottlenecks" in OT.
  - **Offline Replay Conflicts:** What happens when a user stays offline for 2 weeks and then tries to merge 1,000 edits?

---

### What an SDE-3 Answer Looks Like
- "I'll start with the standard SDE-2 architecture using a partitioned KV store for storage. However, for SDE-3, the real challenge is **Migration** and **Blast Radius**..."
- "Instead of a single global cluster, I'd move to a **Cell-Based Architecture** where each cell is self-contained. This limits any configuration error to only 5% of our users."
- "For the database, I'd choose a **NewSQL layer like Spanner** because the cost of managing a manual sharding layer for 1PB of data is operationally too risky for a senior team."
