## Phase 10 - Algorithms Used in System Design

> HLD relevance: these algorithms appear inside the critical parts of case studies.
> SDE-3 does not require coding them from scratch in interviews, but you should understand why they fit and what they cost.

### 10.1 Trie
- prefix lookup
- autocomplete and type-ahead
- distributed trie awareness

### 10.2 Inverted index
- term -> posting list
- query lookup and posting-list merge
- search serving systems

### 10.3 Graph algorithms
- BFS
- DFS
- Dijkstra
- A*
- PageRank awareness

### 10.4 Data structures worth knowing
- hash map
- B+ tree
- skip list
- min / max heap
- ring buffer

### 10.5 Probabilistic structures
- Bloom filter
- HyperLogLog
- Count-Min Sketch
- when approximate answers are worth it

### 10.6 Top-K and ranking patterns
- heap-based top-K
- sketch + heap combinations
- leaderboard-style ranking

### 10.7 Consistent hashing - algorithm detail
- key and node placement on the ring
- virtual nodes
- remapping behavior on membership change
- operational use in cache and KV systems

