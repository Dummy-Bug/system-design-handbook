## Phase 10 — Algorithms Used in System Design

> HLD relevance: These algorithms appear inside the deep-dive sections of specific case studies.
> Don't over-invest here — know each algorithm well enough to explain why you'd use it.

### 10.1 Trie (Prefix Tree)
- Data structure — tree where each node = one character
- Insert, search, prefix search all O(L) where L = string length
- Use cases
  - Type-ahead / autocomplete — find all words with a given prefix
  - Spell check — find nearest valid word
- At scale — distributed trie, shard by first character
- Alternative — Redis Sorted Set with lexicographic range queries (simpler to operate)
- Directly applies to: Type-Ahead / Autocomplete case study

### 10.2 Inverted Index
- Maps term → list of document IDs containing that term
- Build: tokenize documents, stem words, record doc ID for each term
- Query: look up term, intersect/union posting lists
- Scoring: TF-IDF or BM25 — rank by relevance
- Elasticsearch is an inverted index at scale
- Directly applies to: Web Search, Type-Ahead, Gmail search case studies

### 10.3 Graph Algorithms
- BFS (Breadth-First Search)
  - Shortest path in unweighted graph (number of hops)
  - Level-by-level traversal
  - Use: web crawler (frontier exploration), social graph (degrees of separation)
- DFS (Depth-First Search)
  - Reachability, cycle detection, topological sort
  - Use: dependency resolution, social graph analysis
- Dijkstra's Algorithm
  - Shortest path in weighted graph (non-negative weights)
  - Priority queue of (cost, node), relax edges
  - Use: Google Maps routing, network path optimization
- A* Algorithm
  - Dijkstra + heuristic (estimated remaining distance)
  - Faster for geo routing because heuristic prunes search space
  - Use: Google Maps turn-by-turn navigation
- PageRank
  - Random walker on web graph — probability of landing on each page
  - High in-links from authoritative pages = high rank
  - Iterative computation, typically run in batch
  - Use: Google Search ranking, recommendation systems
- Directly applies to: Google Maps, Web Crawler, Google Search case studies

### 10.4 Data Structures Worth Knowing Internally
- Hash Map — O(1) average lookup, the foundation of caches and indexes
- B+ Tree — O(log n), used in all SQL database indexes, supports range scans
- Skip List — O(log n) probabilistic, Redis Sorted Set implementation
- Min/Max Heap — O(log n) insert/extract, used in job schedulers, top-K problems
  - Top-K with a min-heap of size K: iterate stream, pop min when size exceeds K
- Circular Buffer / Ring Buffer — fixed-size FIFO, used in log buffers, rate limiting

### 10.5 Consistent Hashing (Algorithm Detail)
- Already covered in Phase 5, but the algorithm detail matters for case studies
- Hash function maps keys and nodes to the same ring (0 to 2^32)
- Key is assigned to first node clockwise from its hash position
- Virtual nodes — each physical node has 150–200 virtual positions on the ring
- Adding a node — only keys between new node and its predecessor move
- Removing a node — only keys owned by removed node reassign to successor
- Directly applies to: Key-Value Store, Distributed Cache case studies
