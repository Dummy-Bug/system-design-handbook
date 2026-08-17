Question-only practice sheet for **garbage collection specifically** for backend roles at 3–5 years. Company evidence and supplemental prompts are separated below; this file does not claim that every question was asked by a small startup.

> [!important] **What a startup is testing here.** They have no platform team and nobody who tunes JVMs. Every question below is a proxy for one worry: will this person write code that fills the heap and take production down. Plain, confident answers win. I've never tuned a collector, but here's how I'd approach a leak is perfectly acceptable at this tier — it is not at the other two.

> [!info] **How the ordering was decided, honestly.** There is no public dataset of question frequency. This is my judgement from how often each recurs across the interview-prep sources surveyed in August 2026, weighted toward 2025–2026 material. Treat the **bands** as reliable, the order inside a band as approximate.

> [!note] **Evidence boundary.** See the [interview company evidence map](../INTERVIEW-TIER-MAP.md). Questions marked company-reported are tied to a named report; the rest are supplemental interview-bank prompts.

**Coverage markers:** ✅ covered in the note listed · ⚠️ partial · ❌ gap in our notes.

---

# Band A — expect these in almost every screen

### 1. What is garbage collection and why does Java have it?

- **Tests:** the baseline. Almost universal as an opener.
- **Notes:** ✅ `01` — a daemon thread inside the JVM whose job is to destroy useless objects; C++ made the programmer do both creation and destruction and they neglected the second.
- **Chained follow-up:** So why is there no `delete` keyword in Java? — because the responsibility was deliberately taken away from the programmer. `01` answers this directly.

### 2. When does an object become eligible for garbage collection?

- **Tests:** whether you understand reachability rather than reciting a phrase.
- **Notes:** ✅ `02` — an object is eligible if and only if it has no references.

### 3. Can you force garbage collection? What does `System.gc()` do?

- **Tests:** whether you think you control something you don't. Very common, and easy to answer badly.
- **Notes:** ✅ `03` — it is a **request**, never a command; no guarantee it is honoured.
- **What loses points:** saying `System.gc()` calls the garbage collector. You cannot call it. You request that the JVM run it.

### 4. Have you ever had an `OutOfMemoryError`? What did you do?

- **Tests:** production exposure. **The most important question in this file** — the one they actually care about, and the only one where a story beats a definition.
- **Notes:** ⚠️ `06` covers what a memory leak **is**; the **diagnosis workflow is a gap**.

### 5. What is a memory leak in Java? Isn't that impossible with a garbage collector?

- **Tests:** the most-asked GC question after the basics, precisely because it sounds contradictory.
- **Notes:** ✅ `06` — objects no longer used but **not eligible**, because references are still held. The collector is working correctly and still cannot help.
- **Give an example unprompted:** a `static` collection that only ever grows.

### 6. What is `finalize()`?

- **Notes:** ✅ `04` — called by the collector just before destroying an object, to perform cleanup.
- **Recency:** ⬆ **say the modern half.** It has been deprecated since Java 9 and **marked for removal** since Java 18; compiling an override on a current JDK warns you. The replacements are try-with-resources with `AutoCloseable`, and `Cleaner` for a genuine safety net. Knowing this separates you from someone who learned Java from a 2014 course.

### 7. `OutOfMemoryError` versus `StackOverflowError`?

- **Tests:** mapping an error to a memory area. Cheap to ask, revealing.
- **Notes:** ✅ `06` for the OOM side, ✅ JVM chapter `06` for the stack side with measured recursion depths.
- **The detail worth adding:** both are `Error`, not `Exception` — you are not meant to catch them.

---

# Band B — common once the role touches production

### 8. What are the ways to make an object eligible for GC?

- **Notes:** ✅ `02` — nullifying, reassigning, objects created inside a method, Island of Isolation.
- **At this tier** the first three are enough; Island of Isolation is a bonus that will land well.

### 9. If an object is eligible, is it destroyed immediately?

- **Notes:** ✅ `02` and `03` — no. Eligible and collected are two events separated by an unknown amount of time.

### 10. Does the garbage collector work on the stack too?

- **Notes:** ✅ JVM chapter `06` — no. Stack frames free themselves when the method returns, so there is nothing for a collector to do.

### 11. What happens to an object created inside a method when the method finishes?

- **Notes:** ✅ `02` — eligible by default, because the local variables holding it were slots in a frame that no longer exists.
- **Chained follow-up:** Always? — no, and the three exceptions in `02` (returned and captured, returned and ignored, assigned to a `static`) are exactly the follow-up.

### 12. Is `finalize()` guaranteed to run?

- **Notes:** ✅ `05` and `06` — no. It runs only if the collector actually collects the object, and the collector's timing is not guaranteed at all.
- **Why this matters practically:** it is why you must not put connection-closing in `finalize()` and expect it to happen.

### 13. Your service memory keeps climbing until it dies. Where do you start?

- **Notes:** ❌ **gap** — the investigation workflow.
- **Recency:** ⬆ common at startups because somebody has to be the person who can do this, and there is nobody else.

---

# Band C — occasional depth probes

### 14. What algorithm does the garbage collector use?

- **Notes:** ⚠️ `06` names mark-and-sweep and correctly says the algorithm is vendor dependent. **Modern collectors are a gap.**

### 15. Can you call `finalize()` yourself?

- **Notes:** ✅ `04` — yes, and then it is an ordinary method call; the object is **not** destroyed.

### 16. What is `Runtime.getRuntime()`?

- **Notes:** ✅ `03` — a singleton obtained through a factory method; gives you `freeMemory()`, `totalMemory()` and `gc()`.

---

# Gaps this file exposes

| # | Missing from the notes | Why it matters here |
|---|---|---|
| 1 | **Leak diagnosis workflow** — heap dump, `jcmd`/`jmap`, Eclipse MAT | Q4 and Q13 — the two questions that carry the most weight at this tier |
| 2 | **Modern collectors** — that G1 is the default, roughly what it does | Q14; a sentence would do, and we don't have it |

Only two, and the first one is the one to close. At startup level our GC notes are otherwise in good shape — 14 of 16 questions are answered by material already written.

## Company-reported evidence

- **Razorpay SDE-1:** the Java round asked what a memory leak is and how to resolve it. [Report](https://www.naukri.com/code360/interview-experiences/razorpay/razorpay-interview-experience-dec-2021-exp-0-2-years)

The remaining collector, eligibility, and diagnosis prompts are supplemental practice prompts unless a named company report is attached to the individual question.
