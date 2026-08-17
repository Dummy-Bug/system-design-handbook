Interview questions on **JVM architecture and memory**, as asked by small startups and early-stage product teams for a backend role at 3–5 years.

> [!important] **What a startup is actually testing with these.** Not depth. They have no platform team, no JVM specialist, and usually no staging environment worth the name. Every one of these questions is a proxy for one worry: **will this person take production down and not know why.** A confident, plain answer plus one real story beats a textbook recital every time — and I've never had to tune a JVM, here's what I'd do first is an acceptable answer here in a way it is not at the other two tiers.

> [!info] **How the ordering was decided, honestly.** There is no public dataset of interview question frequency. This ordering is my judgement from how often each question recurs across the interview-prep sources surveyed in August 2026, weighted toward material published 2025–2026. Treat the **bands** as reliable and the **order inside a band** as approximate.

**Coverage markers** point at our own notes, so a gap here is a gap in the wiki:

| Marker | Meaning |
|---|---|
| ✅ | covered in the note listed |
| ⚠️ | partly covered — the question would expose a thin spot |
| ❌ | **gap** — nothing in the notes answers this yet |

---

# Band A — expect these in almost every screen

### 1. What is the difference between heap and stack memory?

- **Tests:** whether you can talk about memory at all. This is the opener and it is nearly universal.
- **Notes:** ✅ `05` (heap), `06` (stack), and the comparison table in `06` § **Pulling the five together**
- **Chained follow-up:** Which one is thread safe? — and the good answer is structural: the stack is per-thread so nothing is shared; the heap is one region for the whole JVM.

### 2. What is the JVM? How is it different from the JDK and the JRE?

- **Tests:** vocabulary, and whether you know what you actually ship.
- **Notes:** ✅ `01` § **The JVM**, § **Where the JRE went**
- **Recency:** the modern answer matters — since JDK 9 there is no separate inner JRE directory, and saying so marks you as current rather than as someone who learned this in 2014.

### 3. Who frees memory in Java? What is garbage collection?

- **Tests:** the baseline mental model. Startups ask this to check you know you are **not** in control of deallocation.
- **Notes:** ⚠️ scattered — the reachability rule is in `05`, but the GC chapter is not written yet.

### 4. Where do local variables, instance variables and static variables live?

- **Tests:** the three-way split. Extremely common because it is easy to mark.
- **Notes:** ✅ `05` § **The one row that trips everyone up**, `06` § **Where each kind of variable lives**
- **Chained follow-up:** And where does the object itself live? — the trap is conflating the variable with the object. A reference can sit in the stack while the object it names is on the heap.

### 5. Have you ever seen an `OutOfMemoryError`? What did you do about it?

- **Tests:** whether you have operated a real service. **This is the single most important question in this file** — it is the one they actually care about, and the only one where a story beats a definition.
- **Notes:** ⚠️ `05` has the leak-by-retention callout; the **diagnosis workflow is a gap**
- **What they want to hear:** you looked at what was retaining memory rather than just raising `-Xmx`.

### 6. Is Java pass-by-value or pass-by-reference?

- **Tests:** a classic. Nearly everyone gets the headline right and fumbles the object case.
- **Notes:** ✅ `06` § **Coder Army — Java is pass-by-value is just two slot arrays**
- **Chained follow-up:** Then why did my list change inside the method? — because the **reference** was copied by value, and both copies point at one heap object.

### 7. `StackOverflowError` versus `OutOfMemoryError` — what is the difference?

- **Tests:** whether you can map an error to a memory area. Cheap to ask, very revealing.
- **Notes:** ✅ `06` final `[!warning]`, with measured recursion depths and `-Xss`

### 8. What happens when you run `java Main`?

- **Tests:** end-to-end mental model. Often used as a let's see how deep this goes opener.
- **Notes:** ✅ `05` § **Coder Army — the order the areas actually come into existence**, plus `01` for the loading detail

---

# Band B — common, and likely if the role touches production

### 9. When does an object become eligible for garbage collection?

- **Notes:** ⚠️ `05` covers the reachability rule and that eligible ≠ collected. The four named ways (nullify, reassign, method scope, Island of Isolation) are in the **GC chapter, not yet written**.

### 10. Can you force garbage collection? What does `System.gc()` do?

- **Notes:** ❌ **gap** — GC chapter. The answer they want is it is a request, not a command.

### 11. What is the difference between `String s = "hello"` and `new String("hello")`?

- **Notes:** ✅ `05` § **Coder Army — the string pool**
- **Why startups like it:** it is a memory question disguised as a String question, and it catches people who have only ever used `==` on strings by accident.

### 12. Can you have a memory leak in Java? Give an example.

- **Notes:** ✅ `05` § **Coder Army — a memory leak in a garbage-collected language**
- **Chained follow-up:** How would you find it? — see the gap under Q5.

### 13. Have you ever set `-Xmx` or `-Xms`? Why?

- **Notes:** ✅ `05` § **Setting the heap size**, including why setting `-Xms` equal to `-Xmx` is a production pattern.

### 14. What is Metaspace? What was PermGen?

- **Notes:** ✅ `04` and `05` — Metaspace is native memory outside the heap, grows on demand, capped with `-XX:MaxMetaspaceSize`.
- **Recency:** PermGen has been gone since Java 8. Knowing **why** it was replaced is the differentiator.

### 15. Your service runs in a container with a 512Mi limit and keeps getting OOMKilled, but the JVM never logs an `OutOfMemoryError`. What is happening?

- **Notes:** ❌ **gap** — nothing in the notes covers container-aware JVM sizing.
- **Recency:** ⬆ **high — this is a 2024–2026 question** and startups hit it constantly because everything ships in Kubernetes. The distinction being tested is **the kernel killed the process** versus **the JVM ran out of heap**, and that heap is only one part of what the JVM's RSS actually is.

### 16. What does `finalize()` do?

- **Notes:** ❌ **gap** — GC chapter. Note that the modern half of the answer (deprecated for removal, use `Cleaner` or try-with-resources) is also not in the notes.

---

# Band C — occasional, usually as a depth probe

### 17. What is a class loader?

- **Notes:** ✅ `01`, `02`, `03`

### 18. `ClassNotFoundException` versus `NoClassDefFoundError`?

- **Notes:** ⚠️ `02` names `NoClassDefFoundError` under `LinkageError`, but the **side-by-side distinction is a gap**. Worth closing — it comes up whenever someone has fought a classpath.

### 19. What is JIT compilation?

- **Notes:** ✅ `07`

### 20. Does the garbage collector touch the stack?

- **Notes:** ✅ `06` § **Coder Army — why local variables are not simply kept on the heap**. The answer is no, and the reason is that frames free themselves.

---

# Gaps this file exposes

Ordered by how likely they are to cost you at this tier.

| # | Missing from the notes | Why it matters here |
|---|---|---|
| 1 | **Diagnosing an OOM in production** — heap dump, `jmap`/`jcmd`, Eclipse MAT, dominator tree | Q5 is the most important question in this file and we cannot answer the follow-up |
| 2 | **Container-aware JVM** — `UseContainerSupport`, `MaxRAMPercentage`, OOMKilled vs `OutOfMemoryError` | Q15, and it is the most **recent** thing on the list |
| 3 | **GC basics** — eligibility, `System.gc()`, `finalize()` and its modern replacement | Q9, Q10, Q16 — all in the unwritten GC chapter |
| 4 | `ClassNotFoundException` vs `NoClassDefFoundError` side by side | Q18 |

The first two are not in Durga's course at all, at any point. They will have to come from elsewhere.
