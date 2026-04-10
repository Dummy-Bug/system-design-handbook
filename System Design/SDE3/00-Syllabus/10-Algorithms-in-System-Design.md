## Phase 10 - Algorithms Used in System Design

> HLD relevance: these are not coding-round algorithm drills.
> They are the data-structure and search ideas that appear inside the deep-dive parts of large systems.

### SDE-3 depth bar for this phase
- Know where the algorithm fits in a real system.
- Know the operational tradeoff, not just the time complexity.
- Be able to explain what happens when the data grows, skews, or becomes distributed.

### 10.1 Trie (Prefix Tree)
- Prefix search in O(L), where L is the query length.
- Fits autocomplete and type-ahead systems.
- Distributed trie awareness: sharding by prefix and caching hot prefixes.
- Senior-level depth: compare trie with sorted-set or search-index alternatives for practical systems.

### 10.2 Inverted Index
- Term -> posting-list mental model.
- Core of search systems, document retrieval, and mailbox search.
- Tokenization, stemming, ranking, and index freshness matter operationally.
- Senior-level depth: explain why search index is not the source of truth.

### 10.3 Graph Algorithms
- BFS for frontier expansion and shortest path in unweighted graphs.
- DFS for traversal, reachability, and dependency exploration.
- Dijkstra for weighted shortest path.
- A* for route search with heuristic pruning.
- PageRank awareness for search / relevance systems.
- Senior-level depth: connect algorithm choice to latency, precomputation, and freshness tradeoffs.

### 10.4 Data Structures Worth Knowing Internally
- Hash map for lookup-heavy systems.
- B+ tree for SQL indexes and range scans.
- Skip list for Redis-like ordered structures.
- Heap for scheduler / top-K / priority systems.
- Ring buffer for logs and streaming internals.
- Senior-level depth: explain when the data structure helps the storage engine, not just the app layer.

### 10.5 Consistent Hashing (Algorithm Detail)
- Key and node placement on the same ring.
- Virtual nodes for better load balance.
- Minimal remapping on membership change.
- Operational tradeoffs: hotspot risk still exists even when remapping is small.

### 10.6 Probabilistic Structures and Streaming-Friendly Algorithms
- Bloom filter for negative membership checks.
- HyperLogLog for approximate cardinality.
- Count-Min Sketch for approximate frequency.
- Min-heap plus sketch for top-K heavy hitters.
- Senior-level depth: understand the error model and when approximate results are acceptable.
