Question-only practice sheet for **garbage collection specifically** at FAANGM and adjacent top-tier companies for backend roles at 3–5 years. The FAANGM label is a company bucket, not proof that every listed prompt came from a FAANG interview.

> [!important] **What changes at this tier.** Definitions are assumed. The time goes on **trade-offs, measurement and constraint**, and three things are scored: do you reason from first principles, do you attach **numbers** to claims, and do you volunteer *when not to do this*. "It depends" is the right opening only if the next sentence says **what it depends on**.
>
> They will also follow you down until you hit your limit, deliberately. Hitting it is fine. Bluffing past it is not — and GC is a topic where bluffing is unusually easy to detect, because the follow-up is always "what did you measure?"

> [!info] **How the ordering was decided, honestly.** No public dataset exists, and this tier is the least documented of the three — published lists are mostly reconstruction. Judgement from sources surveyed in August 2026, weighted toward 2025–2026. Treat the bands as **approximate here**, more so than in the other two files.

> [!note] **Company taxonomy and evidence boundary.** See the [interview company evidence map](../INTERVIEW-TIER-MAP.md). Publicis Sapient and Swiggy are included as adjacent product-company evidence, not as literal FAANGM. Documentation is used only for technical fact-checking.

**Coverage markers:** ✅ covered · ⚠️ partial · ❌ gap.

---

# Band A — the shapes that recur

### 1. Your p99 latency spikes every few minutes. Is it GC? Prove it.

- **Tests:** whether you connect the collector to user-visible latency, and whether you *rule things out* before acting.
- **Notes:** ❌ **gap** — GC logs, pause distribution, correlating pause timestamps against the latency spikes.

### 2. G1 versus ZGC — pick one for this service and justify it.

- **Tests:** current knowledge, expressed as a trade-off rather than a preference.
- **Notes:** ❌ **gap.**
- **Recency:** ⬆ **highest on the list.** The trade to state: ZGC gives sub-millisecond pauses largely independent of heap size, and pays in CPU and throughput. Whether that is worth it is a question about your latency SLA — say so, then ask what the SLA is.

### 3. Design an in-memory cache that cannot cause an OOM.

- **Tests:** GC knowledge applied to design under a hard constraint. The flagship question of this tier.
- **Notes:** ❌ **gap** — bounded size versus soft references, eviction policy, and why `WeakHashMap` is almost never the right answer for a cache.

### 4. Allocation rate versus live set — which drives collection cost?

- **Tests:** the sharpest single discriminator on this list.
- **Notes:** ❌ **gap.**

### 5. Walk me from `new Foo()` to the object being reclaimed.

- **Notes:** ⚠️ the front half is strong — `02` and JVM `05` cover allocation, defaults before the constructor, and how the object becomes unreachable. **TLAB allocation, promotion through generations and reclamation are a gap.**

### 6. Why was finalization removed from Java? Argue it properly.

- **Tests:** whether you can reason about language design, not just recite a deprecation notice.
- **Notes:** ✅ **our strongest question at this tier** — `05` demonstrates two of the four reasons with measured programs.
- **The four reasons:** no timing guarantee, so it cannot manage resources; **uncaught exceptions silently swallowed** (`05` Case 3, exit code 0 versus 1); **resurrection** — an object can make itself reachable during its own finalization (`05` Case 4, same hash code printed twice); and every finalizable object costs an extra collection cycle.
- **Then close it:** `Cleaner` fixes resurrection *by construction* — the cleaning action never receives the object, so it has nothing to resurrect.

### 7. How would you *prove* a memory leak rather than guess?

- **Tests:** rigour. The word *prove* is doing the work.
- **Notes:** ❌ **gap.** Two heap dumps separated in time, compare retained sets, find what grows; or trend the live set after full collections across cycles.

---

# Band B — mechanism, asked to find your ceiling

### 8. What is a TLAB and why does it exist?

- **Notes:** ❌ **gap.** Each thread gets its own slice of Eden, so allocation is a pointer bump with no contention.
- **Why it lands:** it answers *"how is allocation this cheap when the heap is shared?"* — which connects straight back to JVM `05`'s point that shared memory is not thread safe.

### 9. What is a safepoint, and what is time-to-safepoint?

- **Notes:** ❌ **gap.** A pause cannot begin until every thread reaches a safepoint; a thread slow to get there extends the pause even when the collector itself was fast.
- **Depth marker:** answering this well signals genuine production exposure.

### 10. What is a humongous object in G1?

- **Notes:** ❌ **gap.** An allocation larger than half a region gets special handling and can drive full collections under pressure.

### 11. When would you use a soft reference, and when would you not?

- **Notes:** ❌ **gap.**
- **The senior answer:** rarely. Soft references hand your eviction policy to the collector, which decides on memory pressure rather than on your access patterns. A bounded cache with a real eviction policy is almost always better. Weak references are for canonical mappings and listeners; phantom references are a cleanup-notification mechanism, not a cache tool.

### 12. Why does an untaken `try` cost nothing, and what *is* expensive?

- **Notes:** ✅ JVM `06` — the exception table is data beside the code, consulted only after a throw; guarded and unguarded compile to identical instructions.
- **The GC connection:** throwing allocates, and stack trace capture allocates proportionally to depth — which is how exception-as-control-flow shows up as allocation pressure.

### 13. Explain the once-only finalization rule and why it is dangerous.

- **Notes:** ✅ `05` Case 4, measured.
- **The danger:** a resurrected object can never be finalized again, so if the cleanup mattered, it silently never happens the second time. Cleanup that fails invisibly is worse than cleanup that fails loudly.

### 14. After 20 redeploys the app dies with `OutOfMemoryError: Metaspace`. Diagnose it.

- **Notes:** ✅ JVM `04` — our strongest section anywhere. A lingering reference keeps the old class loader alive, and with it every class it ever defined.

### 15. `System.gc()` — what actually happens, and why is it banned in most codebases?

- **Notes:** ✅ `03` — including that it delegates to `Runtime.getRuntime().gc()`, **verified in the JDK 25 sources**, and that `-XX:+DisableExplicitGC` exists to neutralise it.
- **The senior half:** it can trigger a full stop-the-world collection that is far more disruptive than the problem it was called to fix, and it overrides tuning decisions made on better information than you have.

---

# Band C — the edge

### 16. What is a write barrier? What is a card table or remembered set?

- **Notes:** ❌ **gap.** How a young collection avoids scanning the old generation to find references pointing into Eden.
- **Reaching your limit here is acceptable** — "I know it exists and roughly why, I haven't worked at that level" is a fine answer at 3–5 years.

### 17. Why does the heap sometimes shrink after a collection, and when is that bad?

- **Notes:** ✅ `03`, measured — G1 uncommits memory back to the OS, so `totalMemory()` and `freeMemory()` both fall while **used** falls too.
- **Why it can be bad:** in a container with a fixed limit, giving memory back and re-committing it later is wasted work; `-Xms` equal to `-Xmx` is the usual answer.

### 18. Give me a case where raising `-Xmx` makes things worse.

- **Notes:** ❌ **gap.** A larger heap means a larger live set to trace and longer collections; in a container it means the kernel OOM-kills you sooner.
- **Why it is a good question:** raising `-Xmx` is the reflex, and this asks you to argue against your own reflex.

### 19. What does the JVM guarantee about collector behaviour?

- **Notes:** ✅ `06` — almost nothing, and the note lists the five questions with no guaranteed answer, then demonstrates the fifth (whether all eligible objects are destroyed) with five identical runs producing five different results.

### 20. String deduplication and compact strings — what are they?

- **Notes:** ❌ **gap.** Compact strings changed `String`'s internal representation in Java 9; GC-level deduplication is a separate opt-in feature.

---

# Gaps this file exposes

At this tier the gap list is longer than the covered list, which is the honest reading rather than a failure of the notes — a 2016 course on eligibility and finalization was never going to cover collector internals or production tooling.

| # | Missing | Priority |
|---|---|---|
| 1 | **Collectors** — G1, ZGC, Shenandoah, choosing between them (Q2) | **highest**, most recency-sensitive |
| 2 | **Latency investigation** — GC logs, pause distribution, ruling GC in or out (Q1, Q7) | highest |
| 3 | **Allocation mechanics** — TLAB, allocation rate versus live set (Q4, Q8) | high |
| 4 | **Cache design under a memory bound** (Q3, Q11) | high |
| 5 | **Generational internals** — promotion, humongous objects, write barriers (Q5, Q10, Q16) | medium |
| 6 | **Safepoints** (Q9) | medium |
| 7 | **Heap sizing trade-offs** (Q18) | medium |
| 8 | **String dedup / compact strings** (Q20) | low |


## Company-reported evidence

- **Publicis Sapient:** the Java round explicitly covered G1, ZGC, heap structure, GC tuning, and stop-the-world events. [Report](https://leetcode.com/discuss/post/7509276/)
- **Swiggy SDE-1:** the Java fundamentals round included JVM and garbage collection. [Report](https://leetcode.com/discuss/post/7642548/)

These are adjacent product-company reports, not proof that the full question set is asked at a particular FAANGM company. The remaining advanced prompts are supplemental practice prompts.
