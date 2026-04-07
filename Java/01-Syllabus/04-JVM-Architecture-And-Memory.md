## Phase 4 — JVM Architecture & Memory

> Interview relevance: "How does garbage collection work?" and "Where does this object live in memory?"
> are standard SDE-2 questions. Understanding the JVM lets you reason about performance, debug memory leaks,
> and explain why certain code patterns are slow — critical for system design and production readiness.

> **Note**: You have existing JVM notes in `Java/01-07`. This phase goes deeper — GC algorithms,
> memory leaks, OOM diagnosis, and JIT compilation.

---

### 4.1 How Java Code Runs — The Full Pipeline
- **Compilation**: `javac` compiles `.java` source → `.class` bytecode. Bytecode is platform-independent.
- **Class Loading**: JVM loads `.class` files into memory on demand (lazy loading).
- **Bytecode Interpretation**: JVM interprets bytecode line by line. This is slow.
- **JIT Compilation**: JVM detects "hot" methods (called thousands of times) and compiles them to native machine code at runtime. After JIT, those methods run at near-C speed.
- **Why Java is "slow to start, fast at steady state"**: the first few seconds are interpreted (slow), then JIT kicks in for hot paths (fast). This is why long-running servers (which Java was built for) perform well, but short CLI scripts feel sluggish.
- **Tiered compilation** (default since Java 8): interprets first → C1 (quick compile, basic optimizations) → C2 (slower compile, aggressive optimizations). JVM profiles as it runs and optimizes what matters most.

### 4.2 JVM Memory Areas

```
JVM Memory
├── Heap (shared across all threads)
│   ├── Young Generation (Eden + Survivor S0 + S1)
│   ├── Old Generation (Tenured)
│   └── String Pool (moved to heap since Java 7)
├── Metaspace (class metadata — replaced PermGen in Java 8)
├── Thread Stacks (one per thread, private)
│   └── Stack Frames (local variables, return address, operand stack)
├── PC Registers (one per thread)
└── Native Method Stacks (for JNI calls)
```

- **Heap** — where all objects live. Shared across all threads. Managed by the garbage collector. This is where most of the action happens.
- **Metaspace** — stores class metadata (class names, method signatures, field info). Grows dynamically (no fixed PermGen limit). Can still run out of memory if class loading goes wrong.
- **Thread Stack** — one stack per thread. Stores stack frames for each method call. Each frame contains local variables (primitives live here), return address, and intermediate results. Fixed size per thread (`-Xss` flag, default ~512KB–1MB).
- **String Pool** — interned strings live here. Since Java 7, it's part of the heap (so it's garbage-collected).

### 4.3 Stack vs Heap — What Goes Where
- **Stack**: primitives, local variable references, method parameters, return addresses. Per-thread, fast (just push/pop), fixed size.
- **Heap**: all objects (including arrays, Strings, wrappers like Integer). Shared, slower (GC manages it), dynamic size.
- `int x = 5;` → `5` is on the stack.
- `Integer x = 5;` → `Integer` object is on the heap, reference to it is on the stack.
- `String s = "hello";` → `String` object in the string pool (on the heap), reference `s` is on the stack.
- **Why this matters**: stack memory is automatically freed when a method returns (no GC needed). Heap memory requires garbage collection → GC pauses.
- **Escape analysis** (JIT optimization): if the JVM detects that an object never escapes the method (not returned, not stored in a field), it may allocate it on the stack instead of the heap. No GC needed. This is why microbenchmarks can be misleading.

### 4.4 Class Loading
- **Three class loaders** (delegation model):
  1. **Bootstrap** — loads core Java classes (`java.lang.*`, `java.util.*`) from `rt.jar`. Written in native code.
  2. **Extension (Platform)** — loads standard extensions from `jre/lib/ext`. Since Java 9, loads platform modules.
  3. **Application** — loads your classes from the classpath. This is the one that loads your code.
- **Delegation model**: Application loader asks Extension first, Extension asks Bootstrap first. Bootstrap tries first, then Extension, then Application. This ensures core classes (like `java.lang.String`) can never be replaced by user code — security feature.
- **Custom class loaders** — used by app servers (Tomcat loads each webapp with its own classloader for isolation), plugin systems, and hot-reloading frameworks.
- **`ClassNotFoundException` vs `NoClassDefFoundError`**: ClassNotFoundException = class not on classpath at load time. NoClassDefFoundError = class was available at compile time but missing at runtime.

### 4.5 Garbage Collection — Fundamentals
- **The problem**: objects are allocated on the heap. When they're no longer needed, the memory must be reclaimed. Manual memory management (like C/C++) is error-prone. GC automates it.
- **GC Roots** — the starting points for determining what's alive:
  - Local variables on the stack of active threads
  - Static fields of loaded classes
  - Active thread objects
  - JNI references
- **Reachability analysis**: start from GC roots, traverse all references. Anything reachable = alive, keep it. Anything unreachable = garbage, collect it.
- **Generational hypothesis**: most objects die young (temporary variables, intermediate results). Few objects live long (caches, connection pools). This is why the heap is split into generations.

### 4.6 Generational GC — Young + Old
- **Young Generation** (short-lived objects):
  - **Eden** — new objects are allocated here
  - **Survivor S0 and S1** — objects that survive a GC cycle are copied here
  - **Minor GC** — collects only the Young Generation. Fast (young gen is small). Runs frequently.
  - Objects that survive multiple Minor GCs are **promoted** to Old Generation.
- **Old Generation** (long-lived objects):
  - Objects that survived many Minor GC cycles
  - **Major GC / Full GC** — collects the entire heap (Young + Old). Slow. Causes a stop-the-world pause.
- **The flow**: new object → Eden → survives GC → Survivor → survives more GCs → Old Gen → eventually collected by Major GC (or lives forever).

### 4.7 GC Algorithms — Know These by Name
- **Serial GC** — single thread, stop-the-world for both minor and major GC. Simple. Only for small apps or client-side apps. `-XX:+UseSerialGC`
- **Parallel GC** (default before Java 9) — multiple threads for GC, but still stop-the-world. Better throughput than Serial. `-XX:+UseParallelGC`
- **G1 GC** (default since Java 9) — divides heap into regions (not just young/old). Collects the regions with the most garbage first ("Garbage First"). Aims for predictable pause times. Good general-purpose choice for server apps. `-XX:+UseG1GC`
- **ZGC** (Java 15+ production-ready) — ultra-low latency. Pauses are sub-millisecond regardless of heap size (even terabytes). Uses colored pointers and load barriers. For latency-sensitive applications (trading, real-time systems). `-XX:+UseZGC`
- **Shenandoah** — similar to ZGC, low-pause, concurrent. Red Hat's GC. `-XX:+UseShenandoahGC`
- **Interview answer**: "For most server applications, G1 is the default and works well. If I need sub-millisecond pauses for latency-sensitive systems, I'd use ZGC."

### 4.8 Memory Leaks in Java — Yes, They Exist
- Java has GC, so it can't have memory leaks, right? **Wrong.** A memory leak in Java = objects that are reachable (so GC can't collect them) but are no longer logically needed by the application.
- **Common causes**:
  - **Static collections that grow forever**: `static List<Event> events = new ArrayList<>();` — events added but never removed. List grows until OOM.
  - **Unclosed resources**: InputStream, Connection, ResultSet — if not closed, they hold native memory and OS handles.
  - **Listeners/callbacks not deregistered**: register an observer on an event bus but never unsubscribe. The event bus holds a reference, preventing GC.
  - **Inner class holding outer reference**: non-static inner class keeps the outer object alive even when the outer is no longer needed.
  - **ThreadLocal not cleaned up**: ThreadLocal values persist for the lifetime of the thread. In a thread pool, threads are reused — old ThreadLocal values accumulate.
  - **Cache without eviction**: `HashMap<Key, BigObject>` used as a cache but never evicted. Use `WeakHashMap` or a bounded cache (Caffeine, Guava Cache).

### 4.9 Common OOM Errors
- **`java.lang.OutOfMemoryError: Java heap space`** — heap is full, GC can't free enough. Fix: increase `-Xmx`, find and fix the leak, reduce object creation.
- **`java.lang.OutOfMemoryError: Metaspace`** — too many classes loaded (common in hot-reloading frameworks, excessive dynamic proxies). Fix: increase `-XX:MaxMetaspaceSize`, find the class loader leak.
- **`java.lang.OutOfMemoryError: GC overhead limit exceeded`** — GC is spending >98% of time collecting but recovering <2% of memory. The heap is almost full with live objects. Fix: increase heap or find the leak.
- **`java.lang.StackOverflowError`** — infinite recursion or extremely deep call stack. Fix: fix the recursion bug, increase `-Xss` (rarely the right fix).
- **Diagnostic tools**: heap dumps (`-XX:+HeapDumpOnOutOfMemoryError`), `jmap`, `jvisualvm`, `Eclipse MAT` for analysis.

### 4.10 JVM Tuning Basics — Know These Flags
- `-Xms512m` — initial heap size (512 MB)
- `-Xmx4g` — maximum heap size (4 GB)
- `-Xss1m` — thread stack size (1 MB)
- `-XX:+UseG1GC` — select G1 garbage collector
- `-XX:MaxGCPauseMillis=200` — G1 target max pause time
- `-XX:+HeapDumpOnOutOfMemoryError` — dump heap on OOM for post-mortem analysis
- **Don't over-tune**: for most applications, set `-Xms` and `-Xmx` to the same value (avoid heap resizing), use G1, and let the JVM handle the rest. Premature JVM tuning is as bad as premature code optimization.
