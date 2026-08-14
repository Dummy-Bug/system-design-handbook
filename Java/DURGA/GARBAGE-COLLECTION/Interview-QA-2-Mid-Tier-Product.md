Question-only practice sheet for **garbage collection specifically** for product-company backend roles at 3–5 years. Company evidence and supplemental prompts are separated below; “mid-tier” is not treated as an official public ranking.

> [!important] **What changes at this tier.** They have real traffic and somebody who has been paged for a GC pause. The bar moves from *what is it* to **explain the mechanism, then debug it**. Nearly every question here has a silent second half — *"and how would you find that?"* — and that is what is actually scored. This is also where the chapter's own boundary starts to hurt: Durga Sir teaches eligibility, requesting and finalization, and this tier asks mostly about the collector itself.

> [!info] **How the ordering was decided, honestly.** No public dataset of question frequency exists. This is my judgement from sources surveyed in August 2026, weighted toward 2025–2026 material. Bands are reliable; order within a band is approximate.

> [!note] **Evidence boundary.** See the [interview company evidence map](../INTERVIEW-TIER-MAP.md). Questions marked company-reported are tied to a named report; the rest are supplemental interview-bank prompts.

**Coverage markers:** ✅ covered · ⚠️ partial · ❌ gap.

---

# Band A — the core set

### 1. Explain generational garbage collection — Eden, survivor spaces, old generation.

- **Tests:** the single most-asked GC question at this tier.
- **Notes:** ❌ **gap**, and not a fixable one from this course — I searched the chapter PDF and there are zero hits for *generation*, *survivor*, *Eden*.

### 2. Minor GC versus Major/Full GC — which one hurts?

- **Notes:** ❌ **gap**, same source problem.

### 3. Which garbage collector does your application use, and why?

- **Tests:** whether you have ever looked. Many candidates do not know their own default.
- **Notes:** ❌ **gap** — collectors are absent from our notes entirely.
- **Recency:** ⬆ **high.** G1 default since Java 9. CMS **removed** in Java 14 — naming it as a current option dates you badly. ZGC became generational in JDK 21.

### 4. A service is slowly consuming memory until it dies. Walk me through debugging it.

- **Tests:** methodology. **Highest-value question in this file.**
- **Notes:** ⚠️ `06` explains what a leak is; the **investigation is a gap** — enabling `-XX:+HeapDumpOnOutOfMemoryError`, capturing a dump from a live process, opening it in Eclipse MAT, reading the dominator tree.

### 5. What is a stop-the-world pause?

- **Notes:** ❌ **gap.** All application threads are frozen so the collector can work without memory changing underneath it.
- **Chained follow-up:** *"Do concurrent collectors eliminate it?"* — **no**, they shorten it. Every collector still stops the world sometimes. Claiming otherwise is a tell that you have not run one.

### 6. Explain strong, soft, weak and phantom references.

- **Tests:** a favourite, because it separates people who have read about GC from people who have only used it.
- **Notes:** ❌ **gap.**
- **The one-line each:** strong prevents collection entirely; **soft** is collected at the collector's discretion when memory is tight, which makes it suitable for memory-sensitive caches; **weak** does not survive the next collection at all, and is what `WeakHashMap` keys use; **phantom** never gives you the object back and exists for post-mortem cleanup notification.

### 7. What is a memory leak in Java, and give a real example.

- **Notes:** ✅ `06` — objects unused but not eligible, because references are still held.
- **Examples worth having ready:** a `static` collection that only grows; a cache with no eviction; a listener nobody unregisters; a `ThreadLocal` never `remove()`d on a pooled thread.
- **`ThreadLocal` specifically is a gap** in the notes and is asked increasingly often.

### 8. `finalize()` is deprecated — why, and what replaced it?

- **Notes:** ✅ `04` and `05` cover the deprecation and name the replacements; the *reasons* are strongest in `05`.
- **The reasons, and our notes demonstrate each:** no timing guarantee at all; **uncaught exceptions inside it are silently swallowed** (`05` Case 3, measured); **object resurrection** is possible (`05` Case 4, measured); every finalizable object survives at least one extra collection cycle.
- **Replacements:** try-with-resources with `AutoCloseable`; `Cleaner` where a safety net is genuinely needed — and `Cleaner` deliberately cannot resurrect, because the cleaning action is never given the object.

### 9. Can you force garbage collection?

- **Notes:** ✅ `03` — request only. Plus `System.gc()` delegates to `Runtime.getRuntime().gc()`, **verified in the JDK 25 sources** in that note.

---

# Band B — likely once the conversation deepens

### 10. What are the ways to make an object eligible for GC?

- **Notes:** ✅ `02` — all four, including Island of Isolation with the sinking-ship explanation of why internal references count for nothing.

### 11. What is Island of Isolation?

- **Notes:** ✅ `02` — a group of objects referencing only each other with no external reference. Whole group is eligible.
- **Why it is asked:** it proves you understand reachability rather than reference counting, and it is the standard way to show that reference counting alone would leak.

### 12. Which class's `finalize()` runs, and how many times?

- **Notes:** ✅ `04` Case 1 and `05` Case 4 — the **eligible object's own class's** method runs, and it runs **only once per object**, however many times that object becomes eligible.
- **Both are measured on JDK 25** in those notes, including the resurrection program proving the once-only rule via hash codes.

### 13. Does the JVM run GC automatically? When?

- **Notes:** ✅ `06` — yes, on low memory, and the measured demo shows the trigger point moved from 100,000 objects in 2016 to 1,000,000 on JDK 25, with five identical runs collecting different amounts each time.
- **This is a good story to tell** — it demonstrates the "no guarantees" answer instead of asserting it.

### 14. How do you read a GC log?

- **Notes:** ❌ **gap.** Unified logging (`-Xlog:gc*`) since JDK 9; the old `PrintGCDetails` flags are gone.
- **What to look for:** pause durations and their distribution, collection frequency, and whether full collections are happening at all.

### 15. Which GC-related JVM flags have you set?

- **Notes:** ⚠️ `-Xmx`/`-Xms` in JVM chapter `05`, `-XX:+DisableExplicitGC` in `03`. **Collector selection and pause-time goal flags are a gap.**

### 16. What happens if `finalize()` throws an exception?

- **Notes:** ✅ `05` Case 3 — depends entirely on who called it. Programmer called it → abnormal termination. Collector called it → **silently ignored**, program continues. Measured, with exit codes 1 and 0.
- **The precision that makes it an exam question:** the JVM ignores **only uncaught** exceptions. A `catch` block runs in both cases.

### 17. Name the `OutOfMemoryError` variants you have seen.

- **Notes:** ⚠️ *Java heap space* and *Metaspace* are covered across the two chapters. **GC overhead limit exceeded**, **Direct buffer memory** and **unable to create new native thread** are a **gap**.

### 18. What is the difference between `Error` and `Exception`, using OOM as the example?

- **Notes:** ✅ `06` — `OutOfMemoryError` is an `Error`, not an `Exception`, and the notes flag that the chapter PDF gets this wrong by writing `OutOfMemoryException`.

---

# Band C — depth probes

### 19. What algorithms do collectors use?

- **Notes:** ⚠️ `06` names mark-and-sweep and correctly says it is vendor dependent. **Mark-compact and copying are a gap.**

### 20. Why does `freeMemory()` sometimes go *down* after a collection?

- **Notes:** ✅ `03` — measured on JDK 25. G1 uncommits heap back to the OS, so `totalMemory()` shrinks and free shrinks with it, even though **used** memory fell.

### 21. What is `Cleaner` and how is it different from a finalizer?

- **Notes:** ⚠️ named in `04` and `05` as the replacement; **the mechanics are a gap.**

### 22. Can garbage collection cause a `ClassNotFoundException` or unload classes?

- **Notes:** ✅ JVM chapter `04` — class loader leaks, and how discarding a loader makes its classes collectable.

---

# Gaps this file exposes

Ranked by cost at this tier.

| # | Missing | Source |
|---|---|---|
| 1 | **Generational heap + minor/major GC** (Q1, Q2) | not in Durga's chapter — Coder Army |
| 2 | **Collectors** — G1, ZGC, Shenandoah, defaults per JDK (Q3) | neither course; external |
| 3 | **Leak investigation** — heap dumps, MAT, dominator tree (Q4) | neither course; external |
| 4 | **Stop-the-world** (Q5) | Coder Army |
| 5 | **Reference types** — soft/weak/phantom, `WeakHashMap` (Q6) | Coder Army |
| 6 | **GC logs**, `-Xlog:gc*` (Q14) | external |
| 7 | **`ThreadLocal` leaks** (Q7) | external |
| 8 | **Collector-selection and pause-goal flags** (Q15) | external |
| 9 | **OOM variants** beyond heap and Metaspace (Q17) | external |
| 10 | **Mark-compact and copying** (Q19), **`Cleaner` mechanics** (Q21) | mixed |

> [!warning] **The pattern.** Our notes are strong on everything the *programmer* controls — eligibility, requesting, finalization, leaks — and near-empty on the *collector itself*. That is not a defect in the notes; it is the shape of the course. This tier asks about both roughly equally, so about half these questions are currently unanswerable from what is written.

## Company-reported evidence

- **Swiggy SDE-1:** the Java-focused fundamentals round included JVM and garbage collection. [Report](https://leetcode.com/discuss/post/7642548/)
- **Walmart SWE III, 2.9 years:** the core-Java round explicitly asked about garbage collection. [Report](https://leetcode.com/discuss/post/6597820/walmart-swe-iii-interview-experience-ind-nvna/)

The collector-selection, tooling, and production-debugging prompts beyond those reports are supplemental practice prompts.
