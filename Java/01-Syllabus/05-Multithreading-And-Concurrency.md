## Phase 5 — Multithreading & Concurrency (Advanced)

> Interview relevance: Google, Amazon, and Flipkart all test concurrency at SDE-2. Not just "what is synchronized"
> but "design a thread-safe rate limiter" or "why does double-checked locking need volatile?" This phase builds
> on LLD Phase 6 and goes into the mechanics that separate SDE-1 from SDE-2.

> **Note**: LLD Phase 6 covers synchronized, ReentrantLock, ReadWriteLock, atomic operations,
> concurrent collections, producer-consumer, and deadlock. This phase goes deeper into the JMM,
> thread pools, CompletableFuture, and advanced synchronizers.

---

### 5.1 Thread Lifecycle — States & Transitions
- **NEW** — thread created but `start()` not called yet
- **RUNNABLE** — `start()` called, thread is running or ready to run (OS decides scheduling)
- **BLOCKED** — waiting to acquire a monitor lock (another thread holds the `synchronized` block)
- **WAITING** — waiting indefinitely for another thread's signal (`wait()`, `join()`, `park()`)
- **TIMED_WAITING** — waiting with a timeout (`sleep(ms)`, `wait(ms)`, `join(ms)`)
- **TERMINATED** — thread has finished execution (returned from `run()` or threw an exception)
- **Why this matters**: `Thread.getState()` is your debugging tool. If a thread is BLOCKED, another thread holds the lock. If WAITING, it's waiting for a signal that may never come (potential deadlock).

### 5.2 Java Memory Model (JMM) — The Critical Foundation
- **The problem**: each CPU core has its own cache. When Thread A writes `x = 5` on Core 1, Thread B on Core 2 might still see the old value of `x` from its cache. Writes are not instantly visible across threads.
- **JMM defines**: when a write by one thread is guaranteed to be visible to a read by another thread. This is called a **happens-before** relationship.
- **Happens-before rules** (know these):
  - **Program order**: within a single thread, every statement happens-before the next
  - **Monitor lock**: an unlock happens-before every subsequent lock of the same monitor
  - **volatile**: a write to a volatile field happens-before every subsequent read of that field
  - **Thread start**: `thread.start()` happens-before any action in the started thread
  - **Thread join**: all actions in a thread happen-before `join()` returns
  - **Transitivity**: if A happens-before B, and B happens-before C, then A happens-before C
- **Why this matters**: without happens-before, the compiler and CPU are free to **reorder** instructions for performance. Your code might execute in a different order than you wrote it. JMM is the contract that prevents this from breaking your program.

### 5.3 `volatile` — Visibility, Not Atomicity
- **What volatile guarantees**: a write to a volatile variable is immediately visible to all threads. No caching, no reordering past the volatile access.
- **What volatile does NOT guarantee**: atomicity. `volatile int count; count++;` is still not thread-safe — `count++` is read-modify-write (3 operations). Two threads can read the same value and both increment.
- **When to use volatile**: flags and state variables read by multiple threads, where only one thread writes. `volatile boolean shutdown = false;` — writer sets to true, readers check it.
- **Double-checked locking** — the classic example:
  ```
  class Singleton {
      private static volatile Singleton instance; // volatile is REQUIRED here
      static Singleton getInstance() {
          if (instance == null) {
              synchronized (Singleton.class) {
                  if (instance == null) {
                      instance = new Singleton(); // without volatile, partially
                  }                               // constructed object may be visible
              }
          }
          return instance;
      }
  }
  ```
  Without `volatile`, Thread B might see a non-null reference to a partially constructed object (due to instruction reordering). `volatile` prevents this.

### 5.4 ExecutorService & Thread Pools
- **Why pools**: creating a new thread per task is expensive (OS thread creation, stack allocation, context switching). A thread pool reuses a fixed set of threads across many tasks — same concept as connection pooling for databases.
- **`Executors` factory methods**:
  - `newFixedThreadPool(n)` — n threads, unbounded task queue. Use for CPU-bound work.
  - `newCachedThreadPool()` — creates threads on demand, reuses idle ones (60s timeout). Use for short-lived async tasks. Danger: unbounded thread creation under load.
  - `newSingleThreadExecutor()` — one thread, tasks execute sequentially. Use when you need ordering.
  - `newScheduledThreadPool(n)` — supports `schedule()` and `scheduleAtFixedRate()`. Use for periodic tasks.
- **`ThreadPoolExecutor` — the real constructor** (what the factory methods hide):
  ```
  new ThreadPoolExecutor(
      corePoolSize,    // threads kept alive even when idle
      maxPoolSize,     // maximum threads under load
      keepAliveTime,   // how long excess threads idle before dying
      timeUnit,
      workQueue,       // queue for tasks when all core threads are busy
      rejectionPolicy  // what to do when queue is full AND max threads reached
  )
  ```
- **Rejection policies** (when everything is saturated):
  - `AbortPolicy` (default) — throws `RejectedExecutionException`
  - `CallerRunsPolicy` — the submitting thread runs the task itself (natural backpressure)
  - `DiscardPolicy` — silently drops the task
  - `DiscardOldestPolicy` — drops the oldest queued task
- **`shutdown()` vs `shutdownNow()`**: `shutdown()` stops accepting new tasks, finishes running ones. `shutdownNow()` interrupts running tasks and returns queued ones. Always call `shutdown()` in a `finally` block.

### 5.5 Callable, Future & CompletableFuture
- **`Runnable`** — `void run()`. Can't return a result. Can't throw checked exceptions.
- **`Callable<V>`** — `V call() throws Exception`. Returns a result. Can throw.
- **`Future<V>`** — handle to an async computation. `future.get()` blocks until the result is ready. `future.get(timeout, unit)` blocks with timeout. `future.isDone()` checks if complete.
- **The problem with Future**: `get()` is blocking. You can't chain operations. You can't combine two futures. You can't react when it completes.
- **`CompletableFuture<V>`** — the fix. Non-blocking, composable, chainable:
  - `supplyAsync(() -> fetchData())` — run in ForkJoinPool
  - `.thenApply(data -> transform(data))` — transform the result
  - `.thenCompose(data -> anotherAsyncCall(data))` — chain another async operation (flatMap)
  - `.thenCombine(otherFuture, (a, b) -> merge(a, b))` — combine two independent futures
  - `.exceptionally(ex -> fallback())` — handle errors
  - `.thenAccept(result -> log(result))` — consume the result (no return)
  - `.allOf(f1, f2, f3)` — wait for all. `.anyOf(f1, f2, f3)` — wait for first.
- **When to use**: any I/O-bound async work — calling external APIs, DB queries in parallel, fan-out requests. The backbone of reactive-style Java code.

### 5.6 Fork/Join Framework
- **What it solves**: divide-and-conquer parallelism. Split a large task into subtasks, process them in parallel, merge results.
- **`ForkJoinPool`** — a specialized thread pool that uses **work-stealing**: idle threads steal tasks from busy threads' queues. Keeps all cores busy.
- **`RecursiveTask<V>`** — returns a result. Override `compute()`: if task is small enough, compute directly. Otherwise, fork into subtasks and join results.
- **`RecursiveAction`** — no return value. Same pattern.
- **`ForkJoinPool.commonPool()`** — shared pool used by parallel streams and CompletableFuture. Default parallelism = number of CPU cores.
- **When to use**: CPU-bound divide-and-conquer (merge sort, array processing, tree traversal). Not for I/O-bound work.

### 5.7 Synchronizers
- **`CountDownLatch`** — one-time gate. N threads wait for M events. Latch counts down from M to 0, then all waiting threads proceed. Cannot be reset. Use: "wait for all services to initialize before accepting traffic."
- **`CyclicBarrier`** — reusable rendezvous. N threads all wait at the barrier until all N arrive, then all proceed together. Can be reused. Use: "all 4 game players must finish their turn before the next round starts."
- **`Semaphore`** — permits. Controls how many threads can access a resource simultaneously. `acquire()` takes a permit (blocks if none available), `release()` returns one. Use: rate limiting, connection pool bounds, bounded resource access.
- **`Phaser`** — flexible synchronizer combining features of CountDownLatch and CyclicBarrier. Supports dynamic party count. Advanced — know it exists.
- **When each**: CountDownLatch for one-time "wait for everything to be ready." CyclicBarrier for repeated "everyone waits for everyone." Semaphore for "limit concurrent access to N."

### 5.8 ThreadLocal
- **What**: gives each thread its own private copy of a variable. No synchronization needed because each thread accesses only its own copy.
- **Use cases**: per-request context (user ID, trace ID, transaction), SimpleDateFormat (not thread-safe — each thread gets its own), per-thread database connection.
- **Memory leak risk**: in thread pools, threads are reused. ThreadLocal values persist across task executions. If you set a ThreadLocal in task A but don't clean it up, task B running on the same thread sees task A's value. Always call `threadLocal.remove()` in a `finally` block.
- **`InheritableThreadLocal`** — child threads inherit the parent's value. Use with caution — can cause confusion with thread pools.

### 5.9 Virtual Threads (Java 21) — Project Loom
- **The problem**: platform threads (OS threads) are expensive — ~1MB stack each, limited by OS (typically max ~10K threads per JVM). A server handling 100K concurrent requests can't create 100K platform threads.
- **Virtual threads**: lightweight threads managed by the JVM, not the OS. Millions of them can exist simultaneously. Each has a tiny initial stack (a few hundred bytes) that grows on demand.
- **How they work**: virtual threads are scheduled onto a small pool of platform threads (carrier threads). When a virtual thread blocks on I/O (database call, HTTP request), the JVM unmounts it from the carrier thread and mounts another virtual thread. No thread is wasted waiting on I/O.
- **Creating them**: `Thread.startVirtualThread(() -> doWork())` or `Executors.newVirtualThreadPerTaskExecutor()`
- **When to use**: I/O-bound workloads with high concurrency — web servers, microservices making many downstream calls. Replaces reactive frameworks (WebFlux, RxJava) for many use cases.
- **When NOT to use**: CPU-bound work (virtual threads don't make CPU work faster — same cores). Synchronized blocks (virtual threads pinned to carrier thread while holding a monitor — use ReentrantLock instead).
- **Interview signal**: mentioning virtual threads in a Google interview shows you know modern Java. "For this high-concurrency server, I'd use virtual threads — millions of concurrent connections without the memory overhead of platform threads."
