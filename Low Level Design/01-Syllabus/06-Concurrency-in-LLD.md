## Phase 6 — Concurrency Essentials for LLD

> LLD relevance: Machine coding rounds at Rippling, Flipkart, Google, and Amazon
> frequently test thread safety. "Two users book the last spot simultaneously — what happens?"
> If you can't answer this, you lose the round even if your OOP design is perfect.

---

### 6.1 Why Concurrency Matters in LLD
- Real systems have multiple users acting simultaneously
- Two users booking the same parking spot, two threads updating the same account balance, two bidders placing bids at the same millisecond
- Without concurrency control, you get: double-booking, lost updates, inconsistent state
- **Interview frequency**: Almost every Tier 2+ problem can be asked with a concurrency twist

### 6.2 Thread Safety Fundamentals
- **Race condition** — two threads read-modify-write shared state, interleaving causes incorrect result
  ```
  Thread A: reads balance = 100
  Thread B: reads balance = 100
  Thread A: writes balance = 100 - 50 = 50
  Thread B: writes balance = 100 - 30 = 70   ← Lost update! Should be 20
  ```
- **Critical section** — the code block that accesses shared mutable state
- **Mutual exclusion (mutex)** — only one thread can execute the critical section at a time
- **Atomicity** — an operation completes fully or not at all, no partial state visible

### 6.3 Synchronized / Locks

#### Intrinsic lock (synchronized in Java)
- `synchronized(this) { ... }` — acquires lock on the object, only one thread enters
- Simple but coarse — locks the entire object even if only one field is being modified
- **Method-level**: `synchronized void park(Vehicle v)` — locks on `this` for the entire method
- **Block-level**: `synchronized(spotMap) { ... }` — locks only the specific shared resource

#### Explicit locks (ReentrantLock in Java)
- `lock.lock(); try { ... } finally { lock.unlock(); }` — always unlock in finally
- Advantage over synchronized: supports tryLock (non-blocking), timeout, fairness, interruptibility
- **When to use**: When you need tryLock ("try to acquire the spot, if someone else got it, move on")

#### Read-Write Lock (ReentrantReadWriteLock)
- Multiple readers can hold the lock simultaneously — reads don't block each other
- A writer needs exclusive access — blocks all readers and other writers
- **When to use**: Read-heavy data structures — parking lot availability (many reads, few writes)
- **In machine coding**: "Multiple users checking available spots (read) concurrently is fine. But when someone parks (write), that spot must be exclusively locked."

### 6.4 Atomic Operations
- `AtomicInteger`, `AtomicReference`, `AtomicBoolean` — lock-free thread-safe operations
- `compareAndSet(expected, new)` — CAS operation, the foundation of optimistic concurrency
- **When to use**: Simple counters (available spot count), flags (is spot occupied), sequence generators
- **Example**: `availableSpots.decrementAndGet()` is atomic — no lock needed for a simple counter

### 6.5 Concurrent Collections
- `ConcurrentHashMap` — thread-safe HashMap, fine-grained locking (per-segment, not whole map)
  - Use instead of `Collections.synchronizedMap(new HashMap<>())` which locks the entire map
- `CopyOnWriteArrayList` — thread-safe list, copies on write (good for read-heavy, write-rare: observer lists)
- `BlockingQueue` — thread-safe queue, `put()` blocks if full, `take()` blocks if empty
  - Use for producer-consumer: task queues, order processing, elevator request queue
- `ConcurrentLinkedQueue` — non-blocking thread-safe queue, for high-throughput scenarios

### 6.6 Producer-Consumer Pattern
- **Problem**: One or more threads produce work items, one or more threads consume them — without busy-waiting
- **Solution**: `BlockingQueue` between producers and consumers
- **Example**: Elevator system — users press buttons (produce requests) → elevator controller consumes requests from a `PriorityBlockingQueue` and processes them
- **Example**: Task scheduler — clients submit tasks → `BlockingQueue` → worker threads pick up tasks
- **Key property**: Producers and consumers are decoupled — they only know about the queue

### 6.7 Deadlock
- **What**: Thread A holds Lock1, waits for Lock2. Thread B holds Lock2, waits for Lock1. Both wait forever.
- **4 conditions** (all must be true for deadlock):
  1. Mutual exclusion — resource is non-shareable
  2. Hold and wait — thread holds one resource, waits for another
  3. No preemption — can't force a thread to release its lock
  4. Circular wait — A waits for B, B waits for A
- **Prevention**:
  - Lock ordering — always acquire locks in the same order (e.g., always lock spot before lock payment)
  - Timeout — `tryLock(timeout)` — give up if you can't acquire in time
  - Lock-free design — use atomic operations instead of locks where possible
- **In machine coding**: If your parking system locks the `Spot` first then `Ticket`, and another path locks `Ticket` first then `Spot` — deadlock. Establish and document a lock ordering.

### 6.8 Common Concurrency Patterns in LLD Problems

| Problem | Concurrency Need | Solution |
|---------|-----------------|----------|
| Parking Lot — two users claim last spot | Mutual exclusion on spot assignment | `synchronized` on spot or `CAS` on spot status |
| Elevator — multiple floor requests | Thread-safe request queue | `PriorityBlockingQueue` |
| BookMyShow — two users book same seat | Optimistic locking on seat | `compareAndSet` or DB-level version check |
| Snake & Ladder — multiple players, turn order | Turn synchronization | `ReentrantLock` + condition variable, or turn-based state |
| Splitwise — concurrent expense adds | Thread-safe balance updates | `ConcurrentHashMap` + `AtomicDouble` per user balance |
| Cache (LRU) — concurrent reads and writes | Read-write lock on cache | `ReentrantReadWriteLock` or `ConcurrentLinkedHashMap` |

### 6.9 The Interview Answer Pattern
When the interviewer asks "what about concurrency?":

1. **Identify the shared mutable state** — "The parking spot's occupied flag is shared state"
2. **Identify the race condition** — "Two threads read it as empty, both try to park"
3. **Choose the right tool** — "I'd use `synchronized` on the individual spot object — granular enough that other spots aren't blocked"
4. **State the tradeoff** — "This adds per-spot lock overhead but prevents double-booking. At this scale it's fine — we're not doing millions of parks per second"

Don't just say "I'd add synchronized." Explain WHY and WHERE.
