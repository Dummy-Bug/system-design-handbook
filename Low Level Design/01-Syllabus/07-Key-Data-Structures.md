## Phase 7 — Key Data Structures & Internals for LLD

> LLD relevance: Machine coding rounds test whether you can pick the right data structure
> for the job. Using a `List` where a `HashMap` is needed, or not knowing how to build
> an LRU cache, will cost you the round.

---

### 7.1 HashMap Internals (Know This Cold)
- **How it works**: Array of buckets. `hashCode()` → bucket index. Entries stored as linked list (or tree at 8+ collisions in Java 8+).
- **O(1) average** for get/put. O(n) worst case if everything hashes to same bucket.
- **Why it matters in LLD**: You'll use HashMap in EVERY problem — spot lookup, user lookup, ticket lookup. Understanding it lets you reason about performance.
- **Key design choice**: What's the key? What's the value?
  - Parking Lot: `Map<SpotId, ParkingSpot>`, `Map<VehicleNumber, Ticket>`
  - Library: `Map<ISBN, Book>`, `Map<MemberId, List<BorrowRecord>>`
  - Splitwise: `Map<UserId, Map<UserId, Double>>` for balance tracking
- **Collision handling interview question**: "What happens when two keys hash to the same bucket?" — linked list or balanced tree. This is why `equals()` and `hashCode()` must be consistent.

### 7.2 LRU Cache (Must Be Able to Implement from Scratch)
- **Problem**: Cache with fixed capacity. On capacity overflow, evict the least recently used item.
- **Data structure**: `HashMap<K, Node>` + `DoublyLinkedList`
  - HashMap: O(1) lookup by key
  - Doubly-linked list: O(1) move-to-front (on access) and remove-from-tail (eviction)
  - Head = most recently used, Tail = least recently used
- **Operations**:
  - `get(key)`: lookup in map → if found, move node to head, return value. If not found, return -1.
  - `put(key, value)`: if key exists, update value, move to head. If new, add to head. If over capacity, remove tail.
- **Why interviewers love it**: It combines two data structures, tests linked list manipulation, and has a clean OOP design.
- **Appears in**: Cache design (standalone problem), any system that needs bounded caching

### 7.3 LFU Cache (Know the Approach)
- **Problem**: Evict the least frequently used item. Ties broken by least recently used.
- **Data structure**: `HashMap<K, Node>` + `HashMap<frequency, DoublyLinkedList>` + `minFrequency` tracker
- **Harder than LRU** — interviewers may ask this as a follow-up or standalone
- **Key insight**: When you access a key, move it from frequency list `f` to frequency list `f+1`. If frequency list `minFrequency` becomes empty, increment `minFrequency`.

### 7.4 Priority Queue / Heap
- **What**: A queue where elements come out in priority order, not insertion order
- **Implementation**: Binary heap — O(log n) insert, O(log n) remove, O(1) peek
- **Min-heap vs max-heap**: Min-heap = smallest first, max-heap = largest first
- **Where it appears in LLD**:
  - Elevator: `PriorityQueue<FloorRequest>` — serve nearest floor first
  - Job Scheduler: `PriorityQueue<Job>` — highest priority job runs first
  - Top-K: Min-heap of size K — iterate items, if current > heap.peek(), replace
  - Task Manager: `PriorityQueue<Task>` by deadline
- **Custom comparator**: `new PriorityQueue<>((a, b) -> a.priority - b.priority)` — you'll write this in almost every Tier 2+ problem

### 7.5 TreeMap / Sorted Map
- **What**: Map that maintains keys in sorted order — O(log n) for all operations
- **Implementation**: Red-Black tree (self-balancing BST)
- **Key operations**: `floorKey(k)`, `ceilingKey(k)`, `subMap(from, to)` — range queries
- **Where it appears**:
  - Calendar: `TreeMap<StartTime, Meeting>` — find next free slot using `ceilingKey()`
  - Interval problems: Find overlapping intervals efficiently
  - Leaderboard: `TreeMap<Score, Set<PlayerId>>` — sorted by score

### 7.6 Deque (Double-ended Queue)
- **What**: Insert and remove from both ends in O(1)
- **Where it appears**:
  - Snake game: `Deque<Position>` — add head at front, remove tail from back
  - Sliding window problems
  - Undo/Redo: Two deques — undo stack and redo stack

### 7.7 Trie (Prefix Tree)
- **What**: Tree where each node is a character, paths from root form strings
- **O(L)** for insert, search, prefix search (L = string length)
- **Where it appears**: Autocomplete, dictionary, spell checker, phone book search
- **Implementation**: `Map<Character, TrieNode>` children + `boolean isEndOfWord`

### 7.8 Graph (Adjacency List)
- **Representation**: `Map<Node, List<Node>>` or `Map<Node, List<Edge>>`
- **Where it appears**:
  - Snake & Ladder: Board as directed graph, BFS for shortest path
  - Social network: `Map<UserId, Set<UserId>>` for follow relationships
  - Dependency resolution: Topological sort on task dependencies

### 7.9 Choosing the Right Data Structure

| Need | Data Structure | Why |
|------|---------------|-----|
| O(1) lookup by key | `HashMap` | Constant-time access |
| O(1) lookup + ordering | `LinkedHashMap` | Insertion/access order preserved |
| Sorted iteration | `TreeMap` | Keys always sorted |
| O(1) eviction of oldest | `DoublyLinkedList + HashMap` | LRU cache |
| Priority-based processing | `PriorityQueue` | Heap-based ordering |
| Thread-safe map | `ConcurrentHashMap` | Fine-grained locking |
| Thread-safe producer-consumer | `BlockingQueue` | Built-in blocking |
| Unique membership check | `HashSet` | O(1) contains |
| Prefix search | `Trie` | O(length) prefix lookup |
| Traversal/shortest path | `Graph + BFS/DFS` | Adjacency list |
