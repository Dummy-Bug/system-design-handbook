Interview questions on **JVM architecture and memory**, as asked by mid-tier product companies for a backend role at 3–5 years.

> [!important] **What this tier is testing.** They have real traffic, a platform team, and someone who has been paged at 3am for a GC pause. The bar moves from *can you define it* to **can you explain the mechanism and then debug it**. Almost every question here has a second half — *"and how would you find that?"* — and the second half is what you are scored on. Definitions get you to the follow-up; only the follow-up gets you the offer.

> [!info] **How the ordering was decided, honestly.** There is no public dataset of interview question frequency. This ordering is my judgement from how often each question recurs across the interview-prep sources surveyed in August 2026, weighted toward material published 2025–2026. Treat the **bands** as reliable and the order inside a band as approximate.

**Coverage markers:** ✅ covered · ⚠️ partial · ❌ gap in our notes.

---

# Band A — the core set, expect most of these

### 1. Walk me through the JVM memory areas.

- **Tests:** the whole model in one answer, delivered in a structure rather than a list.
- **Notes:** ✅ `05` and `06` — and the shared-vs-per-thread split is the framing that makes this answer sound organised rather than memorised.
- **Chained follow-up:** *"Which are shared and which are per thread, and what does that mean for thread safety?"*

### 2. Explain generational garbage collection — Eden, Survivor spaces, Old generation.

- **Tests:** the single most-asked GC question at this tier.
- **Notes:** ❌ **gap.** Not in our notes, and **not in Durga's GC chapter either** — I checked the PDF, zero hits for *generation*, *Eden*, *survivor*. This comes from the Coder Army material.
- **Chained follow-up:** *"Why split the heap at all?"* — because most objects die young, so collecting the young region cheaply and often beats scanning everything.

### 3. Minor GC versus Major/Full GC — what is the difference and which one hurts?

- **Notes:** ❌ **gap** — same source problem as Q2.

### 4. A service is slowly consuming memory and eventually dies. How do you debug it?

- **Tests:** methodology. **This is the highest-value question in this file.**
- **Notes:** ⚠️ `05` explains what a retention leak *is*; the **investigation workflow is a gap** — enabling a heap dump on OOM, capturing one from a live process, opening it in Eclipse MAT, reading the dominator tree to find what is retaining the memory.
- **What separates a good answer:** you look for the **retaining path**, not the biggest object. The biggest object is usually innocent.

### 5. Which garbage collector does your application use, and why that one?

- **Tests:** whether you have ever looked. A surprising number of candidates do not know their own default.
- **Notes:** ❌ **gap** — collectors are nowhere in the notes.
- **Recency:** ⬆ **high.** G1 has been the default since Java 9; ZGC is production-ready and generational since JDK 21. An answer that stops at "CMS" dates you badly, since CMS was removed in JDK 14.

### 6. Metaspace replaced PermGen in Java 8 — why?

- **Notes:** ✅ `04`, `05`. PermGen was fixed-size and lived in the heap; Metaspace is native memory that grows on demand, so "too many classes loaded" stopped being a heap-tuning problem.
- **Chained follow-up:** *"So can Metaspace still run out?"* — yes, and `04`'s class loader leak is exactly how.

### 7. What is a stop-the-world pause?

- **Notes:** ❌ **gap.**
- **Chained follow-up:** *"Does a concurrent collector eliminate it?"* — no. It shortens it. Anyone who says pauses go away entirely has not run one.

### 8. Explain strong, soft, weak and phantom references.

- **Tests:** a favourite because it separates people who have read about GC from people who have only used it.
- **Notes:** ❌ **gap** — Coder Army material, not Durga's.
- **Chained follow-up:** *"Where would you actually use a soft reference?"* — a memory-sensitive cache; and the honest senior answer is that you would usually reach for a real cache library instead.

### 9. Where do static variables live?

- **Tests:** looks trivial, is not.
- **Notes:** ✅ `05` § *The one row that trips everyone up* — the specification says method area; HotSpot holds the value slots in the `Class` object on the heap. Say "method area" first, then offer the detail. That sequence is the answer.

### 10. What is the string pool? What does `intern()` do?

- **Notes:** ⚠️ `05` covers the pool and literal-versus-`new`. **`intern()` itself is a gap**, including the trap that its return value must be assigned to have any effect.

---

# Band B — very likely once the conversation goes deeper

### 11. What are the ways to make an object eligible for GC?

- **Notes:** ⚠️ reachability is in `05`; the four named ways including **Island of Isolation** are in the GC chapter, transcribed but not written up.

### 12. Explain the parent delegation model. Why does it exist?

- **Notes:** ✅ `03` — and the *why* is the security argument: nobody can substitute their own `java.lang.String`.

### 13. You redeploy a web app several times and Metaspace fills up. What is going on?

- **Notes:** ✅ `04` — one of our strongest sections. Class loader leak: a lingering reference keeps the old loader alive, and with it every class it ever defined.
- **Recency:** still asked, though less often now that fewer teams run app servers with hot redeploy.

### 14. Which JVM flags have you actually set in production?

- **Notes:** ✅ `05` (`-Xmx`, `-Xms`), `06` (`-Xss`), `04` (`-XX:MaxMetaspaceSize`) · ❌ GC-selection and logging flags are a gap.

### 15. How do you read a GC log? What would tell you the collector is in trouble?

- **Notes:** ❌ **gap.** Unified logging (`-Xlog:gc*`) since JDK 9 is the current form; the old `-XX:+PrintGCDetails` flags are gone.

### 16. What does a heap dump contain, and what do you do with one?

- **Notes:** ❌ **gap** — tooling. `jmap`/`jcmd`, `-XX:+HeapDumpOnOutOfMemoryError`, Eclipse MAT, dominator tree, leak suspects.

### 17. What is stored in Metaspace versus the heap?

- **Notes:** ✅ `01` (the seven items), `05` (the description-versus-value distinction). This is a question our notes answer unusually well.

### 18. How can a `ThreadLocal` cause a memory leak?

- **Notes:** ❌ **gap.** The mechanism: a pooled thread outlives the request, so a value never `remove()`d stays reachable for the life of the thread.
- **Recency:** ⬆ rising, because thread pools are everywhere and virtual threads have put `ThreadLocal` back in the conversation.

### 19. `finalize()` is deprecated. What replaced it?

- **Notes:** ❌ **gap.** Durga's chapter teaches `finalize()` in four cases with no mention that it is deprecated for removal — this will need a `[!warning]` naming `Cleaner` and try-with-resources.

### 20. What is `UnsupportedClassVersionError` and how do you fix it?

- **Notes:** ✅ `08` — including that major version = Java version + 44, so the error message names both JDKs.

### 21. Name the different `OutOfMemoryError` messages you have seen.

- **Tests:** production exposure. Each variant points at a different region.
- **Notes:** ⚠️ *Java heap space* and *Metaspace* are covered; **GC overhead limit exceeded**, **Direct buffer memory**, and **unable to create new native thread** are a **gap**.

### 22. Does every object go on the heap?

- **Tests:** whether you know the JIT rewrites your assumptions.
- **Notes:** ❌ **gap** — escape analysis and scalar replacement.
- **Why it is a good question:** the textbook answer is "yes, always", and the real answer is "the compiler may prove otherwise and never allocate it."

### 23. How do virtual threads change the memory picture?

- **Notes:** ✅ `06` closing `[!info]` — the stack lives on the heap as a resizable chunk rather than as a fixed OS thread stack.
- **Recency:** ⬆ **high** — Java 21 material, and now a standard "are you current?" probe.

### 24. Your container has a 2Gi limit. What heap size do you set, and how?

- **Notes:** ❌ **gap** — `-XX:MaxRAMPercentage`, `UseContainerSupport`, and the fact that heap is only part of the JVM's real footprint.
- **Recency:** ⬆ **high.**

---

# Band C — depth probes, asked when the interviewer is enjoying themselves

### 25. What is inside a stack frame?

- **Notes:** ✅ `06` — local variable array, operand stack, frame data. One of our deepest sections, with measured `javap` output.

### 26. Why is the JVM stack-based rather than register-based?

- **Notes:** ✅ `06` § operand stack — portability: the bytecode does not have to know how many registers the CPU has.

### 27. What is the code cache?

- **Notes:** ✅ `07` § *Coder Army — where that native code lives*, including the silent fallback to interpreting when it fills.

### 28. How big is a Java object? What is in the object header?

- **Notes:** ❌ **gap** — header, alignment padding, compressed oops.

### 29. What is off-heap memory and when would you use it?

- **Notes:** ❌ **gap** — `DirectByteBuffer`, and the *Direct buffer memory* OOM variant from Q21.

### 30. What is the Java Memory Model — `volatile`, happens-before?

- **Notes:** ❌ **gap**, and **adjacent to this topic rather than inside it.** The name collides with "memory management" but the subject is visibility and ordering, not allocation. Included because interviewers slide between the two, and you should be able to notice the switch and say which one they mean.

---

# Gaps this file exposes

Ranked by cost at this tier.

| # | Missing | Where it will come from |
|---|---|---|
| 1 | **Generational heap + minor/major GC** (Q2, Q3) | Coder Army — **not in Durga's GC chapter** |
| 2 | **Leak investigation workflow** — heap dump, `jmap`/`jcmd`, MAT, dominator tree (Q4, Q16) | neither course; external |
| 3 | **Collectors** — Serial/Parallel/G1/ZGC/Shenandoah, defaults, when each (Q5) | neither course; external |
| 4 | **Stop-the-world** (Q7) | Coder Army |
| 5 | **Reference types** — soft/weak/phantom, `WeakHashMap` (Q8) | Coder Army |
| 6 | **GC logs**, unified `-Xlog:gc*` (Q15) | external |
| 7 | **Container-aware JVM sizing** (Q24) | external |
| 8 | **`ThreadLocal` leaks** (Q18) | external |
| 9 | **OOM variants** beyond heap and Metaspace (Q21) | external |
| 10 | **Escape analysis / scalar replacement** (Q22) | external |
| 11 | `intern()` (Q10), `finalize()` deprecation (Q19), object header (Q28), off-heap (Q29) | mixed |

> [!warning] **The pattern worth noticing.** Our notes are strongest exactly where Durga is strongest — class loading, memory areas, stack frames, the class file. They are weakest on **the collector itself and on tooling**, and that is where this tier concentrates its questions. Durga's GC chapter will not close it: it teaches eligibility, requesting and finalization, not how collectors work or how to debug them.
