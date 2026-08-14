Interview questions on **exception handling specifically**, as asked by mid-tier product companies for a backend role at 3–5 years.

> [!important] **What changes at this tier.** They have real traffic, a support rota, and somebody who has spent an evening reading a stack trace that turned out to be the wrong exception entirely. The bar moves from *what does the keyword do* to **what does your error handling look like across a service**. Almost every question has a silent second half — *"and what would that look like in a codebase you owned?"* — and that half is what is scored.
>
> This is also where the chapter's boundary starts to show. Durga Sir teaches the language mechanism completely and teaches it well; **API-level error design is not in the course at all**, and it is roughly a third of what this tier asks.

> [!info] **How the ordering was decided, honestly.** No public dataset of question frequency exists. This is my judgement from sources surveyed in August 2026, weighted toward 2025–2026 material. Bands are reliable; order within a band is approximate.

**Coverage markers:** ✅ covered · ⚠️ partial · ❌ gap.

---

# Band A — the core set

### 1. What happens if an exception is thrown inside a `finally` block?

- **Tests:** the sharpest single question in this file, because it has a correct answer *and* a design consequence.
- **Notes:** ✅ `06`, measured — the `finally` exception wins, and the original is **gone without trace**. The note's program raises three exceptions and exactly one is reported.
- **Name it:** this is **exception masking**, and it is a real source of lost bugs. The failure you wanted to know about has been replaced by a failure in the cleanup code.
- **Then close it:** try-with-resources fixes this by **suppressing and attaching** the close-time exception rather than replacing it, so both survive. `11` covers `getSuppressed()`.

### 2. Explain exception propagation.

- **Tests:** whether you can trace control through the stack rather than recite the definition.
- **Notes:** ✅ `02`'s seven steps and `11`'s propagation section, plus `06`'s **fourteen nested cases** — which is more depth than this question usually gets.
- **The two rules to state:** a handler is searched for **innermost first**, and **every `finally` whose `try` was entered will run** on the way out, in order. Those two generate every case they can construct on a whiteboard.

### 3. Wrapping versus propagating — when do you catch and when do you let it go?

- **Tests:** judgement. **The most important question in this file** and the one most likely to be asked as a discussion rather than a quiz.
- **Notes:** ❌ **gap.** The course teaches the mechanism, never the strategy.
- **The answer that scores:** catch at a layer that can actually *do* something — retry, fall back, translate for the caller. Everywhere else, let it rise. The failure mode they are probing for is a `try`/`catch` around every method, which turns a stack trace into a shrug.
- **Chained follow-up:** *"How do you translate a `SQLException` into something your API can return?"* — which is Q4.

### 4. What is exception chaining, and why does it matter?

- **Tests:** whether you preserve causes or destroy them.
- **Notes:** ⚠️ `11` covers rethrowing; **`initCause`/`getCause` and the cause chain are a gap.**
- **The answer:** wrap the low-level exception in a domain exception and pass the original as the **cause**, so the new type is meaningful to the caller and the original stack trace is still in the log. A `catch` that logs the message and throws a fresh exception with no cause is how the real failure disappears.

### 5. How do you design a custom exception hierarchy for a service?

- **Notes:** ⚠️ `09` covers writing one exception; **designing a set of them is a gap.**
- **The shape to describe:** one base exception for your domain, a small number of children that map onto *how the caller must respond* — not-found, invalid-input, conflict, downstream-unavailable — and unchecked by default. `09` has the argument for unchecked, which is the half we do cover.
- **What they are listening for:** that your categories are chosen by **caller reaction**, not by which subsystem happened to fail.

### 6. What does try-with-resources compile into? What order are resources closed in?

- **Tests:** whether "syntactic sugar" means anything specific to you.
- **Notes:** ✅ `11` for the construct and the five conclusions; ⚠️ **reverse close order is worth confirming** and is the half people miss.
- **The answer:** it expands to a `try`/`finally` that closes each resource, in **reverse order of declaration** — the last one opened is closed first, which is what you want when a later resource was built from an earlier one.

### 7. Why is `catch (Exception e)` bad practice?

- **Tests:** whether you can argue against something that *works*.
- **Notes:** ⚠️ `04`'s ordering rules explain why it must come last; **the practice argument is a gap.**
- **The answer:** it catches things you did not anticipate and had no plan for, including bugs, and turns them into whatever your generic handler does. It also catches `RuntimeException`s that indicate a broken program, not a failed operation.
- **The precise version:** catching broadly is fine **at a boundary** — a request handler, a job runner — where the job is to turn any failure into a response and a log line. It is not fine three frames deep.

### 8. Multi-catch — what is the rule, and why is the variable implicitly final?

- **Notes:** ✅ `11` for the construct and the one rule; ⚠️ **the implicitly-final detail is thin.**
- **The rule:** the alternatives must not be in a parent-child relationship. `catch (IOException | Exception e)` does not compile, for the same reason a parent-before-child ordering does not.
- **Why the variable is effectively final:** the compiler cannot give it a single narrow type, so it types it as the nearest common supertype and forbids reassignment.

### 9. How do you handle exceptions across a whole web service?

- **Notes:** ❌ **gap** — this is a Spring question and the course predates the framing.
- **What to say:** a centralised handler — `@RestControllerAdvice` with `@ExceptionHandler` methods — mapping domain exceptions to status codes and one consistent error-body shape, so controllers contain no error plumbing.
- **Recency:** ⬆ if you can name **`ProblemDetail`** (the RFC 7807 error body, in Spring 6 / Boot 3) you are answering as of this year rather than 2019.

### 10. What are the exception-handling anti-patterns you watch for in review?

- **Notes:** ❌ **gap**, though `06`'s masking section is one of them arrived at from the other direction.
- **The list worth having ready:** an empty `catch`; catching and returning `null`; logging and rethrowing the same exception at every layer, so one failure prints four times; using exceptions for ordinary control flow; and `catch (Exception e)` deep in the call stack.

---

# Band B — mechanism, asked to find your ceiling

### 11. Walk me through the control flow of a nested `try`-`catch`-`finally`.

- **Notes:** ✅ **our strongest answer at this tier.** `06` traces all **fourteen** cases and flags four rows of the source table that cannot actually occur, verified by measurement.
- **Do not recite the table.** State the two rules from Q2 and derive whichever case they name. That is what is being tested.

### 12. What is a fully checked versus a partially checked exception?

- **Tests:** unusual, and a genuine discriminator — most candidates have never heard the terms.
- **Notes:** ✅ `03`, with measured compiler output.
- **Why it is not trivia:** it is the rule behind a real compiler error. `catch (Exception e)` over an empty `try` compiles; `catch (IOException e)` over the same `try` does not, giving `exception IOException is never thrown in body of corresponding try statement`. Partially checked types are the ones that escape that check.

### 13. Which combinations of `try`/`catch`/`finally` compile?

- **Notes:** ✅ `06`, eight measured rows.
- **The row that surprises people:** `try {} finally {} catch (…) {}` fails with `'catch' without 'try'` — because `finally` **closes** the construct, so the `catch` after it belongs to nothing.

### 14. What happens to an exception thrown in a thread other than `main`?

- **Notes:** ❌ **gap.** The chapter is single-threaded throughout.
- **The answer:** it terminates that thread only; `main` carries on unaware. It reaches the thread's `UncaughtExceptionHandler`, which by default prints to `System.err` — so in a thread pool, a task that throws can vanish silently unless you are checking the `Future`.
- **Why it is asked here:** it is the first place a mid-tier service gets bitten that a tutorial never covers.

### 15. Can a constructor throw an exception? What happens to the object?

- **Notes:** ❌ **gap.**
- **The answer:** yes, and the object is never returned — the reference is never assigned, so it is unreachable and eligible for collection immediately. This is why a constructor that acquires a resource and then throws leaks it, and why acquisition belongs in a factory or a try-with-resources.

### 16. What is `ExceptionInInitializerError` and when have you seen it?

- **Notes:** ✅ `10`, and the JVM chapter covers the class-initialisation half.
- **The detail that lands:** the class is left in a **failed** state, so the *next* access gives you `NoClassDefFoundError` instead — a different exception for the same root cause, which is why the second one is so confusing in a log.

### 17. Which compile-time errors can exception handling produce?

- **Notes:** ✅ `09` collects all **eight**, each measured.
- **Why this is a good answer to have:** "which of these does not compile" is a common written-round format, and the eight cover essentially all of them.

---

# Band C — the edge

### 18. `AutoCloseable` versus `Closeable`?

- **Notes:** ⚠️ `11` names `AutoCloseable` only.
- **The answer:** `Closeable` predates it, is restricted to `IOException`, and is idempotent by contract. `AutoCloseable` is the general one try-with-resources actually requires, and its `close()` may throw anything.

### 19. Is an untaken `try` block expensive?

- **Notes:** ✅ **JVM chapter `06`** — no. The guarded region is recorded in an **exception table** beside the bytecode, consulted only after a throw; guarded and unguarded code compile to identical instructions.
- **Why this answer stands out:** most candidates guess. This is a mechanism you can describe, and it sets up the FAANG-tier question about what *is* expensive.

### 20. `StackOverflowError` versus `OutOfMemoryError`?

- **Notes:** ✅ `10` and the JVM chapter `06`, with measured recursion depths.
- **The mapping:** one memory area each — the thread's stack, and the heap. Both are `Error`, so neither is yours to catch.

### 21. Can `finally` swallow an exception?

- **Notes:** ✅ `05` and `06` between them — a `return` in `finally` discards an in-flight exception, and an exception in `finally` replaces it.
- **The one-line summary worth memorising:** *`finally` overwrites whatever came before it* — its return value beats `try`'s, and its exception beats `try`'s.

---

# Gaps this file exposes

| # | Missing | Priority |
|---|---|---|
| 1 | **Wrap-vs-propagate strategy and exception chaining** (Q3, Q4) | **highest** — the discussion question of this tier |
| 2 | **Spring global handling** — `@RestControllerAdvice`, `ProblemDetail` (Q9) | highest, and the most recency-sensitive |
| 3 | **Anti-patterns as a checklist** (Q7, Q10) | high |
| 4 | **Designing an exception hierarchy for a service** (Q5) | high |
| 5 | **Exceptions and threads** — `UncaughtExceptionHandler`, pools, `Future` (Q14) | medium |
| 6 | **Constructors that throw** (Q15) | low |

> [!important] **What our notes answer unusually well here.** Exception masking with a measured three-exception program (Q1). Propagation, with fourteen nested cases and four errors in the source caught by measurement (Q2, Q11). Fully versus partially checked, which most candidates cannot define at all (Q12). The eight compile-time errors as a set (Q17). And the zero-cost `try` from the JVM chapter (Q19).
>
> **Thirteen of twenty-one answered outright.** The six gaps are all on the same side of one line: the course teaches the *language*, and this tier also asks about the *system*.
