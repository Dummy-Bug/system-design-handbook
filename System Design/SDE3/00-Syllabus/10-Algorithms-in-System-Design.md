## Phase 10 — Algorithms in System Design (SDE-3 Extension)

> **Prerequisite:** Full mastery of SDE-2 Algorithms (Trie, Inverted Index, Graph Search, Consistent Hashing basics, Heap, Skip List, BM25).
> **SDE-3 Focus:** Moving from "how an algorithm works" to "how to orchestrate algorithms for massive-scale, low-latency, and memory-efficient global systems."

### 10.1 — Global Spatial Indexing (Extension of SDE-2 10.3 & 3.20)
*In SDE-2, you know Geohash. In SDE-3, you build global-scale spatial search.*

- **S2 Geometry (Google) & H3 (Uber):** Beyond "Prefix Queries"—understanding "Space-Filling Curves" (Hilbert Curve) and "Hexagonal Sharding." Why S2 IDs are better for range-scans than Geohashes.
- **Global Spatial Sharding:** How to shard a global dataset (e.g., Google Maps) so that nearby locations are always on the same shard while still avoiding "Hot Spots" in cities like NYC/London.
- **Hierarchical Routing Algorithms:** Using "Contraction Hierarchies" to precompute highways—solving the "Long-Distance Route" problem in milliseconds instead of seconds.

### 10.2 — Probabilistic Data Structures at Scale (Extension of SDE-2 7.4 & 10.4)
*In SDE-2, you know Bloom Filters. In SDE-3, you use them for 1PB+ of data.*

- **Count-Min Sketch (CMS) for Billing:** Beyond approximate counters—using "Log-Log Counting" to estimate frequency with 0.1% error for 1B+ unique events in 100KB of memory.
- **HyperLogLog (HLL) in Distributed Systems:** Beyond "DAU counting"—using HLL "Mergeability" to estimate unique users across 10 regions without moving the raw logs.
- **Cuckoo Filter:** A better "Bloom Filter" that supports *deletions* and has better CPU cache locality—used in high-performance networking and storage.

### 10.3 — Search & Ranking Orchestration (Extension of SDE-2 10.2)
*In SDE-2, you know Inverted Index. In SDE-3, you build the "Ranking Pipeline."*

- **Distributed Inverted Index Sharding:** sharding by "Document" vs. sharding by "Term"—understanding the "Fan-out" vs. "Latency" tradeoffs for 10B+ documents.
- **Vector Search & Embeddings (HNSW / FAISS):** Using approximate nearest neighbor search (ANN) for modern "Semantic Search" and "Recommendation Engines."
- **Two-Phase Ranking Pipeline:** How Google/YouTube use a fast "Retrieval Model" to find 1,000 candidates and then a slow "Deep ML Ranker" to sort the top 10.

### 10.4 — Algorithm Operationalization (Extension of SDE-2 10)
*The SDE-3 Bar: When do you use a "Real Algorithm" vs. a "Simple Workaround"?*

- **The "Good Enough" Principle:** When to use an O(N) scan + cache instead of an O(log N) tree to avoid operational complexity.
- **Cache-Oblivious Algorithms:** Designing algorithms that are optimized for the "Memory Hierarchy" (L1/L2/L3 cache) to achieve 10x speedups in high-throughput matching engines.
- **Rate-Limit Convergence (Token Bucket vs. GCRA):** Why the Generic Cell Rate Algorithm (GCRA) used in high-speed networking is more "Fair" than Token Bucket for 100M+ QPS.
