## Phase 10 - Algorithms Used in System Design

> HLD relevance: these are not coding-round algorithms.
> These are the common data-structure and search ideas that appear inside system design case studies.

### 10.1 Trie
- prefix search in O(L)
- used for autocomplete and type-ahead
- alternative - sorted set with lexicographic range in smaller systems

### 10.2 Inverted index
- term -> document list
- used in search systems
- powers search over documents, emails, and web pages

### 10.3 Graph algorithms - know the use cases
- BFS - shortest path in unweighted graph, crawler frontier
- DFS - traversal and dependency analysis
- Dijkstra - shortest path in weighted graph, maps and routing
- A* - optimized path search with heuristic

### 10.4 Data structures that matter in design discussions
- hash map - fast lookup
- B+ tree - database index
- heap - scheduler and top-K
- skip list - Redis sorted set internals awareness
- ring buffer - logs and streaming buffers

### 10.5 Consistent hashing
- node add/remove should not remap all keys
- used in caches and key-value stores
- SDE-1 only needs practical intuition here

