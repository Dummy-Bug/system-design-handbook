## Phase 3 — Collections Internals

> Interview relevance: "How does HashMap work internally?" is the #1 most-asked Java interview question
> at every level. SDE-2 candidates need to explain load factor, rehashing, and treeification — not just
> "it's O(1)." Knowing internals also lets you pick the right collection and explain performance trade-offs
> in system design and LLD rounds.

> **Note**: LLD Phase 7 covers choosing the right data structure and HashMap/LRU usage. This phase covers internal implementation details that interviewers drill on.

---

### 3.1 Collection Hierarchy
- `Iterable` → `Collection` → `List`, `Set`, `Queue`
- `Map` is a separate hierarchy (not a Collection)
- **List** — ordered, allows duplicates: `ArrayList`, `LinkedList`, `CopyOnWriteArrayList`
- **Set** — no duplicates: `HashSet`, `LinkedHashSet`, `TreeSet`
- **Queue** — FIFO + priority: `LinkedList`, `PriorityQueue`, `ArrayDeque`, `BlockingQueue`
- **Map** — key → value: `HashMap`, `LinkedHashMap`, `TreeMap`, `ConcurrentHashMap`
- **Deque** — double-ended queue: `ArrayDeque` (preferred), `LinkedList`
- Know the hierarchy — interviewers ask "what does TreeSet extend?" or "does Map extend Collection?"

### 3.2 ArrayList Internals
- **Internal structure**: a resizable array (`Object[]`)
- **Default capacity**: 10 (when first element is added)
- **Growth strategy**: when full, creates a new array at 1.5x the old capacity (`oldCapacity + (oldCapacity >> 1)`) and copies all elements
- **`add(element)`** — amortized O(1). Most adds are O(1), but resizing triggers an O(n) copy. Averaged out, still O(1).
- **`add(index, element)`** — O(n). Must shift all elements from `index` onward by one position.
- **`get(index)`** — O(1). Direct array access.
- **`remove(index)`** — O(n). Must shift all elements after `index` backward.
- **When to use**: almost always. Random access, iteration, appending at the end.
- **`ensureCapacity(n)`** — if you know the size upfront, pre-allocate to avoid resizing: `new ArrayList<>(10000)`

### 3.3 LinkedList — When Actually Useful
- **Internal structure**: doubly linked list. Each node has `prev`, `next`, `item`.
- **`add(element)`** — O(1) at head or tail
- **`get(index)`** — O(n). Must traverse from head or tail.
- **`remove()`** — O(1) if you have the node reference (via iterator). O(n) if by index.
- **The truth**: LinkedList is almost never the right choice. ArrayList wins for random access, iteration (cache locality — array elements are contiguous in memory, linked list nodes are scattered across the heap), and even most insertion/deletion scenarios.
- **When LinkedList wins**: implementing a Deque (use `ArrayDeque` instead), or when you're removing elements while iterating very frequently (still rare).
- **Interview answer**: "I'd use ArrayList. LinkedList is almost never the right choice due to cache locality. The only scenario where LinkedList has an edge is constant-time removal during iteration, but even that's rare."

### 3.4 HashMap Deep Dive (Interview Favorite)
- **Internal structure**: an array of buckets (`Node<K,V>[] table`). Each bucket is a linked list (or tree at 8+ collisions).
- **Default capacity**: 16 buckets
- **Load factor**: 0.75 — when 75% of buckets are occupied, the map **rehashes** (doubles capacity and redistributes all entries). Trade-off: lower load factor = more memory, fewer collisions. Higher = less memory, more collisions.
- **How `put(key, value)` works**:
  1. Compute `key.hashCode()`
  2. Spread the hash (bitwise operations to reduce collisions): `hash = hashCode ^ (hashCode >>> 16)`
  3. Bucket index = `hash & (capacity - 1)` (this is why capacity is always a power of 2)
  4. If bucket is empty → insert new node
  5. If bucket has entries → walk the linked list, compare keys using `.equals()`. If key exists, update value. If not, append new node.
- **Treeification** (Java 8+): when a single bucket's linked list grows to 8+ nodes, it converts to a Red-Black tree. Worst-case lookup goes from O(n) to O(log n) per bucket. Untreeifies back to linked list when count drops to 6.
- **Rehashing**: when entry count exceeds `capacity * loadFactor`, the table doubles in size. Every entry is redistributed to new buckets. This is O(n) — can cause a latency spike if it happens mid-request.
- **Why `hashCode()` and `equals()` contract matters**: if two objects are `.equals()` but have different `hashCode()`, they'll land in different buckets → HashMap can't find the key → silent data loss. This is the #1 production bug from incorrect hashCode.
- **Null key**: HashMap allows one null key (goes to bucket 0). `Hashtable` and `ConcurrentHashMap` do not allow null keys.

### 3.5 LinkedHashMap — Access Order & LRU
- **Internal structure**: HashMap + a doubly-linked list threading through all entries in insertion order
- **Insertion-order mode** (default): iterating gives entries in the order they were inserted
- **Access-order mode**: `new LinkedHashMap<>(capacity, loadFactor, true)` — every `get()` or `put()` moves the entry to the end. Least recently used entry is at the head.
- **Building LRU cache**: override `removeEldestEntry()` to evict when size exceeds capacity:
  ```
  protected boolean removeEldestEntry(Map.Entry eldest) {
      return size() > MAX_CAPACITY;
  }
  ```
- **This is the simplest LRU implementation in Java** — one class, no manual linked list management. Know both this approach and the manual `HashMap + DoublyLinkedList` approach (LLD Phase 7).

### 3.6 TreeMap / TreeSet
- **Internal structure**: Red-Black tree (self-balancing BST)
- **All operations O(log n)**: get, put, remove, containsKey
- **Keys must be `Comparable`** or you must provide a `Comparator` at construction
- **Unique operations** that HashMap can't do:
  - `floorKey(k)` — greatest key ≤ k
  - `ceilingKey(k)` — smallest key ≥ k
  - `subMap(from, to)` — range view
  - `firstKey()`, `lastKey()` — min/max
- **When to use**: when you need sorted iteration or range queries. If you just need O(1) lookup, HashMap is always faster.
- **TreeSet** — a TreeMap where the value is a dummy. Same Red-Black tree, same O(log n), same sorted guarantees.

### 3.7 HashSet
- **The truth**: HashSet is literally a HashMap where every value is the same dummy object (`PRESENT = new Object()`)
- `add(e)` → `map.put(e, PRESENT)`
- `contains(e)` → `map.containsKey(e)`
- All the same performance characteristics as HashMap — O(1) average, depends on good `hashCode()`
- **Know this because**: interviewers love asking "how does HashSet ensure uniqueness?" → it uses the key of a HashMap, and HashMap checks `hashCode()` + `equals()` for key collision.

### 3.8 PriorityQueue
- **Internal structure**: binary heap (min-heap by default)
- **`offer()`** — O(log n), inserts and sifts up
- **`poll()`** — O(log n), removes root and sifts down
- **`peek()`** — O(1), returns root without removing
- **Not sorted**: iterating a PriorityQueue does NOT give elements in priority order. Only `poll()` guarantees order.
- **Custom comparator**: `new PriorityQueue<>(Comparator.comparingInt(Task::getPriority))` — max-heap: `Comparator.reverseOrder()`
- Covered in LLD Phase 7 — listed here for completeness of the collections map.

### 3.9 Fail-Fast vs Fail-Safe Iterators
- **Fail-fast** (`ArrayList`, `HashMap`, `HashSet`): if the collection is modified while iterating (not through the iterator), throws `ConcurrentModificationException`. Detects via an internal `modCount` counter.
  ```
  for (String s : list) {
      list.remove(s);  // ConcurrentModificationException!
  }
  ```
  Fix: use `iterator.remove()` or `list.removeIf(predicate)`.
- **Fail-safe** (`ConcurrentHashMap`, `CopyOnWriteArrayList`): iterates over a snapshot or segments. Won't throw CME, but may not reflect latest modifications.
- **Interview question**: "What happens if you modify a HashMap while iterating?" → ConcurrentModificationException (fail-fast). Use ConcurrentHashMap if concurrent modification is needed.

### 3.10 Immutable Collections
- **`Collections.unmodifiableList(list)`** — returns a read-only **view** of the original list. If the original list changes, the "unmodifiable" view changes too. Not truly immutable.
- **`List.of("a", "b")`** (Java 9+) — truly immutable. Any modification throws `UnsupportedOperationException`. Does not allow null elements.
- **`List.copyOf(existingList)`** (Java 10+) — creates an immutable copy. Original can change without affecting the copy.
- **`Collections.emptyList()`** — immutable empty list. Singleton. Use when returning empty results instead of `null`.
- **When to use**: returning collections from methods (defensive copy), public API boundaries, thread safety without synchronization.

### 3.11 Comparable vs Comparator
- **`Comparable<T>`** — natural ordering, defined inside the class: `class Student implements Comparable<Student> { compareTo(Student o) { ... } }`
- **`Comparator<T>`** — external ordering, defined outside the class: `Comparator.comparing(Student::getAge).thenComparing(Student::getName)`
- **When to use which**: Comparable for the one "default" sort order (age for Person, name for City). Comparator for every other sort order — you can have multiple Comparators for the same class.
- **Java 8 Comparator utilities**:
  - `Comparator.comparing(keyExtractor)` — sort by one field
  - `.thenComparing(keyExtractor)` — secondary sort
  - `.reversed()` — reverse order
  - `Comparator.naturalOrder()`, `Comparator.reverseOrder()`
  - `Comparator.nullsFirst()`, `Comparator.nullsLast()` — handle nulls
