Interview questions on **JVM architecture and memory**, as asked at FAANG and FAANG-adjacent companies for a backend role at 3–5 years.

> [!important] **What changes at this tier.** Almost nothing here is a definition question. The interviewer assumes you know what the heap is and spends the time on **trade-offs, measurement and constraint**. Three things are being scored: do you reason from first principles rather than recall, do you attach **numbers** to claims, and do you volunteer **when not to do this**. It depends is the correct start to most of these answers — but only if the next sentence says **what it depends on**.
>
> The other shift: they will follow you down as far as you can go and then one step further, deliberately, to find the edge. Reaching the edge is fine. Bluffing past it is fatal.

> [!info] **How the ordering was decided, honestly.** There is no public dataset of interview question frequency, and this tier is the least documented of the three — companies ask under NDA and published lists are mostly reconstruction. This ordering is my judgement from sources surveyed in August 2026, weighted toward 2025–2026 material. Treat the **bands** as approximate here, more so than in the other two files.

**Coverage markers:** ✅ covered · ⚠️ partial · ❌ gap in our notes.

---

# Band A — the shapes that recur

### 1. Design an in-memory cache for a service that must never OOM.

- **Tests:** the flagship question of this tier. Memory knowledge applied to a design problem under a hard constraint.
- **Notes:** ❌ **gap** — bounded size versus soft references, eviction policy, what happens when entries are large and few versus small and many, and why a `WeakHashMap` is almost never the right answer for a cache.
- **The move that scores:** you bound it explicitly and you say how you would **size** the bound, rather than reaching for a reference type and hoping the collector saves you.

### 2. Your service has a p99 latency SLA of 100ms and misses it every few minutes. Walk me through the investigation.

- **Tests:** whether you connect GC to user-visible latency. Very common as an opening scenario.
- **Notes:** ❌ **gap** — GC logs, pause distribution, allocation rate, and ruling GC in or out before touching it.
- **The move that scores:** you **rule it out** first. Periodic p99 spikes are as often a downstream timeout or a connection pool as they are a collector.

### 3. G1 versus ZGC — which would you pick, and why?

- **Tests:** current knowledge plus the ability to justify with a number rather than an adjective.
- **Notes:** ❌ **gap** — collectors are absent from our notes entirely.
- **Recency:** ⬆ **highest on this list.** G1 default since Java 9; ZGC generational since JDK 21; CMS removed in JDK 14. The trade-off to state: ZGC buys sub-millisecond pauses largely independent of heap size, and pays for it in CPU and throughput. Whether that is worth it is a question about your latency SLA, and you should say so.

### 4. Your heap is capped at 4GB but the process is using 7GB of RSS. Where did the rest go?

- **Tests:** whether you understand that the heap is not the JVM's memory footprint. Excellent discriminator, and increasingly common.
- **Notes:** ❌ **gap** — Metaspace, code cache, thread stacks, direct byte buffers, GC's own structures, native allocations by libraries.
- **Recency:** ⬆ high, driven by container memory limits.
- **Partial credit exists in our notes:** `07` covers the code cache and `06` covers per-thread stacks, so two of the pieces are there.

### 5. Trace `new Foo()` from the allocation to the object being reclaimed.

- **Tests:** the whole lifecycle in one narrative. They are listening for where you go vague.
- **Notes:** ⚠️ the front half is strong — `05` § what `new Student(...)` does, in order, defaults before the constructor, reference into the caller's slot. The back half (TLAB allocation, promotion through the generations, reclamation) is a **gap**.

### 6. How would you prove a suspected memory leak, rather than guess at it?

- **Tests:** rigour. The word **prove** is doing the work — they want a method, not a tool name.
- **Notes:** ❌ **gap.** Two heap dumps separated in time, compare retained sets, find what grows; or watch live-set-after-full-GC trend upward across cycles.
- **The move that scores:** you name what would **disprove** it too.

### 7. Why is the JVM stack-based rather than register-based?

- **Tests:** first-principles reasoning about a design decision. A genuine favourite because there is no way to bluff it.
- **Notes:** ✅ `06` § operand stack — bytecode that names no registers does not need to know the target CPU's register count, which is what makes it portable.

---

# Band B — deeper mechanism, asked to find your ceiling

### 8. What is a TLAB and why does it exist?

- **Notes:** ❌ **gap.** Thread-local allocation buffers: each thread gets its own slice of Eden so allocation is a pointer bump with no contention.
- **Why it lands well:** it is the answer to how is heap allocation as cheap as it is, given the heap is shared? — which connects directly to `05`'s point that shared memory is not thread safe.

### 9. What are compressed oops, and what happens around 32GB of heap?

- **Notes:** ❌ **gap.** References are stored as 32-bit offsets below roughly 32GB; past that they widen to 64-bit and effective capacity can **fall** as the heap grows.
- **Why it is asked:** it is a genuinely counter-intuitive result, and it is the kind of thing you only know if you have sized a large heap.

### 10. What is escape analysis? Does every object go on the heap?

- **Notes:** ❌ **gap** — escape analysis and scalar replacement.
- **Chained follow-up:** So can you rely on it? — no, and saying so is the mature answer.

### 11. What is a safepoint? What is time-to-safepoint?

- **Notes:** ❌ **gap.** A pause cannot begin until every thread reaches a safepoint, so a thread that takes a long time to get there extends the pause even though the collector was fast.
- **Depth marker:** answering this well signals real production exposure.

### 12. What is a humongous object in G1, and why does it matter?

- **Notes:** ❌ **gap.** An allocation larger than half a region gets special handling and can drive full collections under pressure.

### 13. Allocation rate versus live set — which one drives GC cost?

- **Tests:** the sharpest single discriminator on this list.
- **Notes:** ❌ **gap.** Young-collection cost tracks what **survives**, not what was allocated, which is why a high-churn service with a small live set can be perfectly healthy.

### 14. After 20 redeploys the app dies with `OutOfMemoryError: Metaspace`. Diagnose it.

- **Notes:** ✅ `04` — our strongest section, and it answers this fully: a lingering reference keeps the old class loader alive, and with it every class it defined.

### 15. Why can you not rely on `finalize()`? What is the modern answer?

- **Notes:** ❌ **gap.** No guarantee it runs, no guarantee when, resurrection is possible, and it delays reclamation by an extra cycle. Modern: try-with-resources, and `Cleaner` where a safety net is genuinely required.

### 16. When would you deliberately use off-heap memory?

- **Notes:** ❌ **gap** — `DirectByteBuffer`, zero-copy IO, and taking large stable data out of the collector's reach.
- **Chained follow-up:** What did you give up? — manual lifetime management, and a different OOM that most dashboards do not watch.

### 17. Explain why wrapping code in `try` costs nothing at runtime.

- **Notes:** ✅ `06` § frame data — the exception table is data beside the code, consulted only after a throw; the guarded and unguarded versions compile to identical instructions.
- **Chained follow-up:** Then what is expensive? — throwing, and stack trace capture in particular.

### 18. How do virtual threads change memory behaviour at a million threads?

- **Notes:** ⚠️ `06` has the shape — stacks on the heap rather than fixed OS stacks. The consequences (GC now owns your thread stacks, pinning, `ThreadLocal` at that scale) are a **gap**.
- **Recency:** ⬆ high.

---

# Band C — the edge, where they are checking how far you go

### 19. What is a write barrier? What is a card table or remembered set?

- **Notes:** ❌ **gap.** How a young collection avoids scanning the old generation to find references into Eden.
- **Reaching your limit here is acceptable.** Most 3–5 YOE candidates do not have this, and the honest I know it exists and roughly why, I have not worked at that level is a fine answer.

### 20. What is AppCDS and what problem does it solve?

- **Notes:** ❌ **gap.** Class data sharing, and startup time as a memory-adjacent concern.
- **Recency:** ⬆ rising with serverless and scale-to-zero.

### 21. What is string deduplication? What are compact strings?

- **Notes:** ❌ **gap.** Compact strings (Java 9) changed `String`'s internal representation; GC-level deduplication is a separate opt-in.

### 22. Why does the JVM need both an interpreter and a JIT? Why not compile everything up front?

- **Notes:** ✅ `07` — including tiered compilation and profile-guided recompilation.
- **The move that scores:** the JIT knows which branch actually ran, which an ahead-of-time compiler cannot know.

### 23. Give me a case where raising `-Xmx` makes things worse.

- **Notes:** ❌ **gap.** A larger heap means a larger live set to trace, longer collections, and in a container it means the kernel kills you sooner.
- **Why it is a good question:** raising `-Xmx` is the reflex, and this asks you to argue against your own reflex.

---

# Gaps this file exposes

At this tier the gap list is longer than the covered list — which is the honest reading, not a failure of the notes. Durga's course is a 2016 JVM-internals course; it was never going to cover collectors or production tooling.

| # | Missing | Priority |
|---|---|---|
| 1 | **Collectors** — G1, ZGC, Shenandoah, defaults per JDK, choosing between them (Q3) | **highest** — also the most recency-sensitive |
| 2 | **Latency investigation** — GC logs, pause distribution, ruling GC in or out (Q2, Q6) | highest |
| 3 | **The JVM's real footprint** — heap vs RSS, native memory accounting (Q4) | high |
| 4 | **Allocation mechanics** — TLAB, allocation rate vs live set (Q8, Q13) | high |
| 5 | **Cache design under a memory bound** (Q1) | high |
| 6 | **Compressed oops and the 32GB cliff** (Q9) | medium |
| 7 | **Escape analysis / scalar replacement** (Q10) | medium |
| 8 | **Safepoints** (Q11), **humongous objects** (Q12), **write barriers / card table** (Q19) | medium → low |
| 9 | **`finalize()` deprecation and `Cleaner`** (Q15), **off-heap** (Q16) | medium |
| 10 | **AppCDS** (Q20), **compact strings / dedup** (Q21) | low |

> [!important] **What our notes do cover at this tier, and cover well.** Class loader leaks and Metaspace exhaustion (Q14), the zero-cost `try` (Q17), why the JVM is stack-based (Q7), the interpreter/JIT split and the code cache (Q22), and the front half of the object lifecycle (Q5). Those are real strengths — they are just a minority of what gets asked here.

---

# Reading across all three files

The single conclusion, if you only take one thing from this exercise:

> [!warning] **Our notes are strong on how the JVM is built and weak on how it behaves under load.** Class loading, memory areas, stack frames, the class file format — all solid, and better than most candidates will have. **Collectors, GC tuning, heap dumps, GC logs, container sizing** — almost entirely absent, and that is where the mid-tier and FAANG questions concentrate.
>
> Durga's GC chapter will not fix this. Its 13 parts cover eligibility, requesting collection and finalization — not how collectors work. **The Coder Army material closes part of it** (generations, mark-and-sweep, reference types, stop-the-world) and the rest — tooling, container behaviour, modern collectors — has no source yet on disk.
