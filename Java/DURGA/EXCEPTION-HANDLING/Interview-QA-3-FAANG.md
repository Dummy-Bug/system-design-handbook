Question-only practice sheet for **exception handling** at FAANGM and adjacent top-tier companies for backend roles at 3–5 years. The FAANGM label is a company bucket, not proof that every listed prompt came from a FAANG interview.

> [!important] **What changes at this tier.** Definitions are assumed. The interview moves to cost, failure semantics, API contracts, asynchronous boundaries, retry behavior, and what the system should do when recovery is not realistic.

> [!info] **How the ordering was decided, honestly.** There is no public dataset of interview question frequency, and this tier is the least documented. This ordering is reconstructed from advanced Java interview themes surveyed in August 2026. Treat the **bands** as approximate here.

> [!note] **Company taxonomy and evidence boundary.** See the [interview company evidence map](../INTERVIEW-TIER-MAP.md). Atlassian and Rippling are adjacent top-tier product companies; Razorpay is India top-tier product. Documentation is used only for technical fact-checking.

**Coverage markers:** ✅ covered · ⚠️ partial · ❌ gap in our notes.

# Band A — the shapes that recur

### 1. What does throwing an exception actually cost?

- **Tests:** JVM implementation, allocation, and stack-trace capture.
- **Notes:** ⚠️ JVM Architecture `06` covers the zero-cost non-throwing path; throw cost is a gap.

### 2. How would you design the error model for a public API?

- **Tests:** stable categories, machine-readable codes, correlation, and information exposure.
- **Notes:** ❌ gap.

### 3. Argue for and against checked exceptions.

- **Tests:** language-design trade-offs rather than a memorized preference.
- **Notes:** ⚠️ `09` covers the practical recommendation; the full argument is a gap.

### 4. How does the JVM implement `try`/`catch`, and why is the non-throwing path often described as zero-cost?

- **Tests:** exception tables and the throwing-path trade-off.
- **Notes:** ✅ JVM Architecture `06`.

### 5. When is using an exception for control flow acceptable?

- **Tests:** readability, performance, and edge-case judgement.
- **Notes:** ❌ gap.

### 6. A downstream call fails. How do you decide whether to retry?

- **Tests:** transient versus permanent failures, idempotency, backoff, jitter, and circuit breaking.
- **Notes:** ❌ gap.

### 7. Why were suppressed exceptions added to try-with-resources?

- **Tests:** primary versus cleanup failures.
- **Notes:** ✅ `06`, `11`.

# Band B — deeper mechanism, asked to find your ceiling

### 8. What is a stackless exception, and when would you use one?

- **Tests:** stack-trace cost and the observability trade-off.
- **Notes:** ❌ gap.

### 9. How do exceptions behave across asynchronous boundaries?

- **Tests:** `Future`, `ExecutionException`, `CompletionException`, and swallowed pool failures.
- **Notes:** ❌ gap.

### 10. Why is catching `Throwable` dangerous?

- **Tests:** fatal errors, shutdown, and process health.
- **Notes:** ⚠️ `09` covers catching `Error`; the complete boundary argument is a gap.

### 11. What happens to `finally` when the JVM exits?

- **Tests:** `System.exit`, shutdown hooks, and durable cleanup.
- **Notes:** ✅ `05`.

### 12. Explain the `ExceptionInInitializerError` to `NoClassDefFoundError` sequence.

- **Tests:** failed class initialization and later access.
- **Notes:** ✅ `10` and JVM Architecture notes.

### 13. Can you recover from `OutOfMemoryError`?

- **Tests:** recoverability boundaries and operational response.
- **Notes:** ⚠️ `02` covers non-recoverability; operational handling is a gap.

# Band C — the edge, where they are checking how far you go

### 14. Where do causes get lost in a log, and how do you prevent it?

- **Tests:** full throwable logging, cause preservation, and single-boundary logging.
- **Notes:** ❌ gap.

### 15. Should Java have a `Result` or `Either` type?

- **Tests:** failure-as-data versus exceptions and ecosystem trade-offs.
- **Notes:** ❌ gap.

### 16. Does multi-catch generate different bytecode from separate catches?

- **Tests:** source-level convenience versus compiled handler structure.
- **Notes:** ⚠️ `11` covers multi-catch syntax; bytecode detail is a gap.

### 17. What ordering guarantees do nested `finally` blocks provide?

- **Tests:** entered blocks, unwinding order, and masking.
- **Notes:** ✅ `06`.

### 18. How would you find the most-thrown exception in production?

- **Tests:** metrics, profiling, caught exceptions, and log blind spots.
- **Notes:** ❌ gap.

# Gaps this file exposes

| # | Missing | Priority |
|---|---|---|
| 1 | Cost of throwing and stackless exceptions | **highest** — the flagship runtime question |
| 2 | Retry semantics and idempotency | highest for distributed systems |
| 3 | Public API error-model design | highest for platform/backend roles |
| 4 | Async failure propagation | high |
| 5 | Cause preservation and exception metrics | medium to high |
| 6 | `Result` types and exception-as-control-flow judgement | medium |

The current notes answer JVM exception mechanics, suppressed exceptions, class initialization, and nested `finally` behavior well. The main gaps are systems design, observability, and asynchronous execution.

## Interview-question sources

- [Interview Kickstart: Java Exception Handling Interview Questions](https://interviewkickstart.com/blogs/interview-questions/java-exception-handling-interview-questions)
- [Java Guides: Scenario-Based Java Exception Handling Interview Questions](https://www.youtube.com/watch?v=uWri9ALwjdg)
- [Baeldung: Java Exceptions Interview Questions](https://www.baeldung.com/java-exceptions-interview-questions)

## Technical fact-checking only

- [Java Language Specification: Exceptions](https://docs.oracle.com/javase/specs/jls/se26/html/jls-11.html)
- [Oracle: Try-with-resources](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html)
- [Oracle: Unchecked Exceptions](https://docs.oracle.com/javase/tutorial/essential/exceptions/runtime.html)

## Company-reported evidence

- **Atlassian P50:** an LLD interview report explicitly says exception handling was evaluated along with tests and corner cases. [Report](https://leetcode.com/discuss/interview-experience/6399521/Atlassian-P50-or-Jan-2025/)

The runtime-cost, error-model, retry, and async prompts above are supplemental advanced prompts unless a named report is attached to the individual question.
