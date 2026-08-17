Question-only practice sheet for **exception handling** for product-company backend roles at 3–5 years. Company evidence and supplemental prompts are separated below; “mid-tier” is not treated as an official public ranking.

> [!important] **What this tier is testing.** They have real traffic and real support incidents. The bar moves from what does the keyword do? to **where should an exception be handled, translated, logged, retried, or allowed to propagate across a service?**

> [!info] **How the ordering was decided, honestly.** There is no public dataset of interview question frequency. This ordering is my judgement from the interview-prep sources surveyed in August 2026. Treat the **bands** as reliable and the **order inside a band** as approximate.

> [!note] **Evidence boundary.** See the [interview company evidence map](../INTERVIEW-TIER-MAP.md). Questions marked company-reported are tied to a named report; the rest are supplemental interview-bank prompts.

**Coverage markers:** ✅ covered · ⚠️ partial · ❌ gap in our notes.

# Band A — the core set, expect most of these

### 1. What happens if an exception is thrown inside a `finally` block?

- **Tests:** exception masking and cleanup safety.
- **Notes:** ✅ `06`.

### 2. Explain exception propagation through nested method calls.

- **Tests:** stack unwinding and handler selection.
- **Notes:** ✅ `02`, `06`, `11`.

### 3. When should you catch an exception, and when should you let it propagate?

- **Tests:** service-layer judgement.
- **Notes:** ❌ gap — the notes teach mechanics, not strategy.

### 4. What is exception chaining, and why does it matter?

- **Tests:** preserving the original cause while translating an error.
- **Notes:** ⚠️ `11` covers rethrowing; cause-chain design is a gap.

### 5. How would you design a custom exception hierarchy for a service?

- **Tests:** categories based on caller action rather than implementation detail.
- **Notes:** ⚠️ `09` covers one custom exception; hierarchy design is a gap.

### 6. What does try-with-resources compile into, and in what order are resources closed?

- **Tests:** desugaring, reverse close order, and suppressed exceptions.
- **Notes:** ✅ `11`; close-order detail is partial.

### 7. Why is `catch (Exception e)` often bad practice?

- **Tests:** catching unexpected bugs versus handling a boundary failure.
- **Notes:** ⚠️ `04` covers ordering; review practice is a gap.

### 8. What is multi-catch, and what restrictions apply to its alternatives?

- **Tests:** Java 7 syntax and parent/child exception relationships.
- **Notes:** ✅ `11`.

### 9. How do you handle exceptions across a whole web service?

- **Tests:** centralized handling and consistent API responses.
- **Notes:** ❌ gap — Spring/global API handling is outside the notes.

### 10. What exception-handling anti-patterns do you look for in review?

- **Tests:** production judgement.
- **Notes:** ❌ gap — no dedicated review checklist.

# Band B — very likely once the conversation goes deeper

### 11. Walk through a nested `try`/`catch`/`finally` control-flow example.

- **Tests:** deriving behavior instead of memorizing isolated rules.
- **Notes:** ✅ `06`.

### 12. What is a fully checked versus a partially checked exception?

- **Tests:** compiler exception analysis.
- **Notes:** ✅ `03`.

### 13. Which combinations of `try`, `catch`, and `finally` compile?

- **Tests:** syntax and compiler diagnostics.
- **Notes:** ✅ `06`.

### 14. What happens to an exception thrown in a thread other than `main`?

- **Tests:** thread boundaries and uncaught exception handling.
- **Notes:** ❌ gap.

### 15. Can a constructor throw an exception? What happens to the object?

- **Tests:** constructor failure and partial initialization.
- **Notes:** ❌ gap.

### 16. What is `ExceptionInInitializerError`, and how can it lead to `NoClassDefFoundError`?

- **Tests:** class initialization failure.
- **Notes:** ✅ `10`; JVM class initialization notes are also relevant.

### 17. What compile-time errors can exception handling produce?

- **Tests:** written-round compiler reasoning.
- **Notes:** ✅ `09`.

### 18. What is the difference between `AutoCloseable` and `Closeable`?

- **Tests:** resource API contracts.
- **Notes:** ⚠️ `11` names `AutoCloseable`; the comparison is a gap.

### 19. Is an untaken `try` block expensive?

- **Tests:** JVM exception-table mechanics.
- **Notes:** ✅ JVM Architecture `06`.

### 20. Can `finally` swallow an exception?

- **Tests:** `return` and exception replacement behavior.
- **Notes:** ✅ `05`, `06`.

# Band C — depth probes, asked when the interviewer is enjoying themselves

### 21. How should a service wrap a `SQLException` or downstream exception before exposing it to an API caller?

- **Tests:** translation boundaries and cause preservation.
- **Notes:** ❌ gap.

### 22. How would you map domain exceptions to HTTP responses?

- **Tests:** error contract design.
- **Notes:** ❌ gap.

### 23. How do exceptions propagate through `Future` and `CompletableFuture`?

- **Tests:** asynchronous failure semantics.
- **Notes:** ❌ gap.

### 24. How would you prevent one failure from being logged four times across service layers?

- **Tests:** logging ownership and observability.
- **Notes:** ❌ gap.

### 25. When is retrying an exception safe, and what must accompany the retry?

- **Tests:** transient failure classification, idempotency, backoff, and jitter.
- **Notes:** ❌ gap.

# Gaps this file exposes

| # | Missing | Priority |
|---|---|---|
| 1 | Catch-versus-propagate strategy and exception chaining | **highest** — the core service-design discussion |
| 2 | Global web-service error handling | highest for Spring backend roles |
| 3 | Async exception propagation | high — common source of invisible failures |
| 4 | Review anti-patterns and logging ownership | high — directly tied to production debugging |
| 5 | Retry semantics and idempotency | medium to high for distributed services |

The existing notes are strongest on propagation, `finally`, try-with-resources, compiler rules, and nested control flow. The gaps are mostly service and concurrency concerns.

## Interview-question sources

- [Baeldung: Java Exceptions Interview Questions](https://www.baeldung.com/java-exceptions-interview-questions)
- [Interview Kickstart: Java Exception Handling Interview Questions](https://interviewkickstart.com/blogs/interview-questions/java-exception-handling-interview-questions)
- [Java Guides: Scenario-Based Java Exception Handling Interview Questions](https://www.youtube.com/watch?v=uWri9ALwjdg)

## Technical fact-checking only

- [Java Language Specification: Exceptions](https://docs.oracle.com/javase/specs/jls/se26/html/jls-11.html)
- [Oracle: The `try` Statement](https://docs.oracle.com/javase/tutorial/essential/exceptions/try.html)
- [Oracle: Try-with-resources](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html)

## Company-reported evidence

- **Atlassian P50:** an LLD interview report explicitly says exception handling was evaluated along with tests and corner cases. [Report](https://leetcode.com/discuss/interview-experience/6399521/Atlassian-P50-or-Jan-2025/)
- **Oracle, 2 YOE:** a Java interview report lists exceptions, custom exceptions, and checked versus unchecked exceptions. [Report](https://www.geeksforgeeks.org/interview-experiences/oracle-interview-experience-2-years-experienced/)

The service-boundary, retry, async, and observability prompts beyond those reports are supplemental practice prompts.
