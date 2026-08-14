Interview questions on **exception handling specifically**, as asked at FAANG and FAANG-adjacent companies for a backend role at 3–5 years.

> [!important] **What changes at this tier.** Definitions are assumed and the keywords are assumed. The time goes on **cost, design and failure semantics**, and three things are scored: do you reason from first principles, do you attach **numbers** to claims, and do you volunteer *when not to do this*.
>
> Exception handling is a good topic for them because it sits on a fault line: it is a language feature everyone has used, and a distributed-systems problem almost nobody has thought about carefully. The questions cross that line deliberately — they start at `try`/`catch` and end at retries and idempotency.

> [!info] **How the ordering was decided, honestly.** No public dataset exists, and this tier is the least documented of the three — published lists are largely reconstruction. Judgement from sources surveyed in August 2026, weighted toward 2025–2026. Treat the bands as **approximate here**, more so than in the other two files.

**Coverage markers:** ✅ covered · ⚠️ partial · ❌ gap.

---

# Band A — the shapes that recur

### 1. What does throwing an exception actually cost?

- **Tests:** the flagship question of this tier. It is asked because the honest answer requires knowing *which part* is expensive, and most people answer "exceptions are slow" and stop.
- **Notes:** ⚠️ **JVM `06`** gives the free half — the exception table, and why an untaken `try` costs nothing. **The cost of the throw itself is a gap.**
- **The answer:** the `try` is free, `catch` dispatch is cheap, and the expense is **capturing the stack trace** in the `Throwable` constructor — `fillInStackTrace()` — which walks the stack and allocates proportionally to its depth. Published benchmarks put an exception with a stack trace an order of magnitude above one without; the ratio grows with stack depth, which is why the same exception is far more expensive inside a deep framework stack than in a microbenchmark.
- **The move that scores:** you then say **when it matters** — a validation path throwing per request in a hot loop — and when it does not, which is nearly always.

### 2. Design the error model for a public API.

- **Tests:** the design question of this tier. Open-ended on purpose.
- **Notes:** ❌ **gap.**
- **The shape:** a small, stable set of categories chosen by **what the caller must do** — retry, fix the request, give up, escalate — each with a stable machine-readable code, a human-readable message, and a correlation id. Versioned, because error codes are part of your contract as much as the success schema.
- **The move that scores:** you say what you will **not** expose. Stack traces and downstream exception class names leak your internals and become a dependency you cannot change.

### 3. Argue for and against checked exceptions.

- **Tests:** whether you can hold both sides of a genuine language-design controversy.
- **Notes:** ⚠️ `09` has the practical recommendation and its reasoning; **the full argument is a gap.**
- **For:** the compiler forces the caller to make a decision about a failure they can actually recover from. It is the only mechanism in Java that puts a failure mode in the type system.
- **Against:** it does not compose — it forces `throws` up the whole call chain, it breaks down entirely across lambdas and streams, and the pressure it creates in practice is to write `catch (Exception e) {}` to make the compiler quiet, which is worse than no checking at all.
- **The close:** essentially no language designed since has adopted them, and Java's own modern APIs lean unchecked. Say that, then say the case where you would still use one.

### 4. How does the JVM implement `try`/`catch`? Why is it "zero-cost"?

- **Notes:** ✅ **JVM `06` — our strongest answer anywhere on this list.** The guarded range lives in an **exception table** attached to the method, consulted only when a throw occurs; guarded and unguarded code compile to identical instructions.
- **Follow the thread to the trade:** zero-cost on the non-throwing path is bought by making the throwing path expensive — the runtime must search tables frame by frame while unwinding. That is the design decision, and naming it as a decision is what separates this from a memorised fact.

### 5. When is using an exception for control flow acceptable?

- **Tests:** whether "never use exceptions for control flow" is a rule you repeat or a rule you understand.
- **Notes:** ❌ **gap.**
- **The answer:** almost never, and the reason is readability before performance — control flow that jumps frames is hard to follow. The legitimate exception is a genuinely exceptional early exit from deep recursion, and there you use a **stackless** exception, which is Q8.
- **The counter-case worth raising yourself:** parsing. `Integer.parseInt` throwing `NumberFormatException` on ordinary user input is exception-as-control-flow shipped in the JDK, and it is why `NumberFormatException` shows up in profiles of request-validation code.

### 6. A downstream call fails. Walk me through how you decide to retry.

- **Tests:** the question that leaves the language entirely. Very common at this tier and rarely prepared for.
- **Notes:** ❌ **gap** — nothing in the course reaches this.
- **The distinction to lead with:** **transient versus permanent**. A timeout or a 503 is worth retrying; a 400 will fail identically forever. Your exception hierarchy should make that classification *visible to the caller*, which is the link back to Q2.
- **The three things that must accompany a retry:** a bound, exponential backoff **with jitter**, and idempotency — retrying a non-idempotent write is how one failure becomes two charges.
- **The move that scores:** you mention that retries amplify load, so a retry policy without a circuit breaker turns a partial outage into a total one.

### 7. Suppressed exceptions — why were they designed that way?

- **Tests:** whether you can reason about *why* an API is shaped as it is.
- **Notes:** ✅ `11` covers `getSuppressed()`, and `06` demonstrates the problem it solves with a measured program.
- **The argument:** before try-with-resources, an exception from `close()` in a `finally` block **replaced** the original exception, so the cleanup failure hid the real one. Neither can be discarded and only one can be thrown, so the language keeps the primary and attaches the rest. `06`'s program raises three exceptions and reports one — that is the before picture, and it is a strong thing to be able to cite from measurement.

---

# Band B — mechanism, asked to find your ceiling

### 8. What is a stackless exception and when would you use one?

- **Notes:** ❌ **gap.**
- **The answer:** the four-argument `Throwable` constructor takes `writableStackTrace`; pass `false` and the trace is never captured, which removes essentially all the cost from Q1. Historically the same was done by overriding `fillInStackTrace()`.
- **When:** a pre-allocated singleton exception on a genuinely hot path where the trace is never read. **Say the cost too** — you lose the trace, so it is only defensible when the throw site is unambiguous.

### 9. How do exceptions behave across asynchronous boundaries?

- **Tests:** where most Java developers' exception knowledge stops.
- **Notes:** ❌ **gap.** The chapter is single-threaded throughout.
- **The answer:** a `try`/`catch` around the code that *submits* work catches nothing — the exception happens on another thread, in another stack. It surfaces when you ask for the result: wrapped in `ExecutionException` from `Future.get()`, or in `CompletionException` on the `CompletableFuture` path, where `exceptionally` and `handle` are the composition points.
- **The failure mode to name:** submit to a pool with `execute` rather than `submit`, never inspect the `Future`, and the exception is silently swallowed. This is one of the most common real sources of invisible failure in a Java service.

### 10. Why is catching `Throwable` dangerous?

- **Notes:** ⚠️ `09` establishes that catching `Error` is legal and pointless.
- **The sharper answer:** it catches `OutOfMemoryError` and `StackOverflowError`, from which your handler probably cannot run correctly anyway — and it catches `ThreadDeath` and interruption-related failures, so it can defeat shutdown. A process in an unknown state that keeps serving traffic is worse than one that dies and gets restarted.

### 11. What happens to `finally` when the JVM exits?

- **Notes:** ✅ `05`, measured — `System.exit(0)` skips it entirely.
- **The extension they are after:** shutdown hooks are the mechanism that *does* run, and they are not guaranteed either — `SIGKILL` and a hard crash bypass everything. So durable cleanup cannot live in the process; it has to be recoverable from outside, which is why idempotent startup recovery beats careful shutdown.

### 12. `ExceptionInInitializerError`, then `NoClassDefFoundError` for the same class. Explain.

- **Notes:** ✅ `10`, plus the JVM chapter on class initialisation.
- **The mechanism:** static initialisation runs once. If it throws, the class is marked **erroneous**, and every later attempt to use it fails with `NoClassDefFoundError` — a different error, same root cause, with the original long gone from the log.
- **Why it is asked:** it is a genuinely confusing production symptom, and explaining it proves you understand class initialisation rather than just exceptions.

### 13. Can you recover from an `OutOfMemoryError`?

- **Notes:** ⚠️ `02` argues non-recoverability; the practical nuance is a gap.
- **The honest answer:** not in general — your handler needs to allocate, and there is nothing to allocate from. The narrow exception is when you *know* the cause was one bounded allocation, and even then the heap may be so pressured that the process is unusable.
- **The senior half:** the right response is usually to fail fast and let the orchestrator restart you, with a heap dump on exit (`-XX:+HeapDumpOnOutOfMemoryError`) so the cause survives the restart.

---

# Band C — the edge

### 14. Where do causes get lost in a log, and how do you prevent it?

- **Notes:** ❌ **gap.**
- **The failure modes:** wrapping without passing the cause; logging `e.getMessage()` instead of `e`, which discards the trace and often prints `null`; and log-and-rethrow at four layers, which turns one incident into four unrelated-looking entries.
- **The fix:** log at the boundary, once, with the full throwable, and carry a correlation id so one failure is one searchable story.

### 15. Java has no `Result` type. Should it?

- **Tests:** language design, asked to see how you think when there is no correct answer.
- **Notes:** ❌ **gap.**
- **The trade:** a `Result`/`Either` makes failure part of the return type, so it composes through streams and cannot be ignored — which is exactly what checked exceptions failed to achieve. The cost is that every caller unwraps it, and it does not interoperate with a JDK and ecosystem built on throwing.
- **The pragmatic close:** use it inside a module where you control both sides; do not put it on an interface that ordinary Java code has to call.

### 16. Multi-catch — does it generate different bytecode from separate catches?

- **Notes:** ⚠️ `11` covers the construct, not its compilation.
- **The answer:** yes — one handler with multiple exception-table entries pointing at the same range, rather than duplicated handler bodies. It is a genuine reduction, not only source-level sugar.

### 17. What ordering guarantees do nested `finally` blocks give you?

- **Notes:** ✅ `06` — every `finally` whose `try` was **entered** runs, innermost first, verified across fourteen measured cases.
- **The subtlety:** *entered*, not *reached*. Failing before the `try` means its `finally` never runs, which is why acquisition must happen immediately before the `try`, or inside try-with-resources where the language enforces the pairing.

### 18. How would you find the most-thrown exception in production?

- **Notes:** ❌ **gap.**
- **The answer:** exception rate as a first-class metric tagged by type, not just log grep — because the ones that matter are usually being caught and never reaching the log. A profiler's exception-allocation view finds throws that no log line records at all.
- **Why it is a good question:** it inverts the topic. Every other question is about handling exceptions; this one is about knowing they are happening.

---

# Gaps this file exposes

At this tier the gap list is longer than the covered list, which is the honest reading rather than a failure of the notes — a 2016 course on the language mechanism was never going to cover retry semantics or async failure propagation.

| # | Missing | Priority |
|---|---|---|
| 1 | **The cost of a throw** — `fillInStackTrace`, depth-proportional capture (Q1) | **highest** — the flagship question |
| 2 | **Retry semantics** — transient vs permanent, backoff, jitter, idempotency, circuit breaking (Q6) | highest |
| 3 | **API error model design** (Q2) | highest |
| 4 | **Async failure propagation** — `ExecutionException`, `CompletionException`, swallowed pool tasks (Q9) | high |
| 5 | **The checked-exception argument, both sides** (Q3) | high |
| 6 | **Stackless exceptions** (Q8) | medium |
| 7 | **Exception-as-control-flow, defensibly** (Q5) | medium |
| 8 | **Observability** — cause preservation, exception metrics (Q14, Q18) | medium |
| 9 | **`Result` types and why Java lacks them** (Q15) | low |

> [!important] **What our notes *do* answer well here, and it is more than the gap table suggests.** How the JVM implements `try`/`catch` and why it is zero-cost (Q4) — from the JVM chapter, and a genuinely strong answer. Why suppressed exceptions exist, argued from a measured three-exception program (Q7). `finally` versus `System.exit` (Q11). The `ExceptionInInitializerError` → `NoClassDefFoundError` sequence (Q12). And nested `finally` ordering, backed by fourteen measured cases (Q17).
>
> **Five solid answers out of eighteen**, and one of them — Q4 — is a question most candidates cannot answer at all. The other thirteen need material that is about systems rather than syntax, and none of it exists on disk yet.
