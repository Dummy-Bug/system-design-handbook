Interview questions on **exception handling**, as asked by small startups and early-stage product teams for a backend role at 3–5 years.

> [!important] **What a startup is actually testing with these.** Not obscure syntax. They want to know whether you will notice failures, preserve useful diagnostics, and avoid turning a real bug into a silent success.

> [!info] **How the ordering was decided, honestly.** There is no public dataset of interview question frequency. This ordering is my judgement from the interview-prep sources surveyed in August 2026. Treat the **bands** as reliable and the **order inside a band** as approximate.

**Coverage markers** point at our own notes:

| Marker | Meaning |
|---|---|
| ✅ | covered in the note listed |
| ⚠️ | partly covered — the question would expose a thin spot |
| ❌ | **gap** — nothing in the notes answers this yet |

# Band A — expect these in almost every screen

### 1. What is an exception?

- **Tests:** the baseline vocabulary question.
- **Notes:** ✅ `01`.
- **Chained follow-up:** *"How is an exception different from an error?"*

### 2. What is the difference between `Exception` and `Error`?

- **Tests:** the exception hierarchy and recoverability judgement.
- **Notes:** ✅ `02`.

### 3. What is the difference between checked and unchecked exceptions?

- **Tests:** compiler enforcement and API design.
- **Notes:** ✅ `03`.

### 4. What is the difference between `throw` and `throws`?

- **Tests:** keyword precision.
- **Notes:** ✅ `07`, `08`, `09`.

### 5. What is `finally` used for, and will it always execute?

- **Tests:** cleanup semantics and edge cases.
- **Notes:** ✅ `05`.
- **Chained follow-up:** *"What happens if `System.exit(0)` is called?"*

### 6. Can you have multiple `catch` blocks? Does their order matter?

- **Tests:** subtype ordering and actual try/catch experience.
- **Notes:** ✅ `04`.

### 7. What is a custom exception, and when would you create one?

- **Tests:** domain modelling rather than catching library exceptions everywhere.
- **Notes:** ✅ `09`.

### 8. What is a `NullPointerException`, and how do you prevent it?

- **Tests:** practical failure prevention.
- **Notes:** ⚠️ `10` covers the exception; prevention is a gap.

# Band B — common once the role touches real code

### 9. Can you write `try` without `catch`?

- **Tests:** legal try/catch/finally combinations.
- **Notes:** ✅ `06`.

### 10. What happens if both `try` and `finally` contain `return` statements?

- **Tests:** control-flow precedence and review judgement.
- **Notes:** ✅ `05`.

### 11. What is try-with-resources?

- **Tests:** resource lifecycle and `AutoCloseable`.
- **Notes:** ✅ `11`.
- **Recency:** since Java 9, already-declared effectively-final resources can be used in the resource specification.

### 12. Can you draw the exception hierarchy?

- **Tests:** whether `Throwable`, `Exception`, `RuntimeException`, and `Error` are connected in your mental model.
- **Notes:** ✅ `02`, `04`.

### 13. What happens if nobody catches an exception?

- **Tests:** propagation and the default exception handler.
- **Notes:** ✅ `02`.

### 14. How do you read a stack trace?

- **Tests:** production debugging discipline.
- **Notes:** ✅ `02`.

### 15. Can you catch an `Error`?

- **Tests:** the difference between syntactic possibility and sensible recovery.
- **Notes:** ✅ `09`.

### 16. What is the difference between `final`, `finally`, and `finalize`?

- **Tests:** vocabulary and modern Java awareness.
- **Notes:** ✅ `05`.
- **Recency:** `finalize()` is deprecated and marked for removal in modern Java.

# Band C — occasional, usually as a depth probe

### 17. Should a custom exception be checked or unchecked?

- **Tests:** API design judgement.
- **Notes:** ✅ `09`.

### 18. What is the difference between `throw e` and `throw new Exception()` inside a catch block?

- **Tests:** cause and stack-trace preservation.
- **Notes:** ⚠️ `11` covers rethrowing; cause preservation is partial.

### 19. What happens when an exception is thrown from a `finally` block?

- **Tests:** exception masking.
- **Notes:** ✅ `06`.

### 20. What are the most common exception-handling mistakes in code review?

- **Tests:** practical engineering judgement.
- **Notes:** ⚠️ the mechanics are covered; the review checklist is a gap.

# Gaps this file exposes

| # | Missing from the notes | Why it matters here |
|---|---|---|
| 1 | NPE prevention discipline | the most common real application failure |
| 2 | Exception chaining and cause preservation | lost causes make production debugging harder |
| 3 | Logging and boundary handling | silent failures and duplicate logs are common review issues |
| 4 | Modern API-level error handling | backend services need consistent error responses |

The existing notes answer the language fundamentals well. The main gaps are prevention, observability, and service-level design.

## Interview-question sources

- [Java Guides: Java Exception Handling Interview Questions and Answers](https://www.youtube.com/watch?v=nWjYZnV_Gpk)
- [Baeldung: Java Exceptions Interview Questions](https://www.baeldung.com/java-exceptions-interview-questions)
- [Interview Kickstart: Java Exception Handling Interview Questions](https://interviewkickstart.com/blogs/interview-questions/java-exception-handling-interview-questions)

## Technical fact-checking only

- [Java Language Specification: Exceptions](https://docs.oracle.com/javase/specs/jls/se26/html/jls-11.html)
- [Oracle: The `throw` Statement](https://docs.oracle.com/javase/tutorial/essential/exceptions/throw.html)
- [Oracle: The `throws` Clause](https://docs.oracle.com/javase/tutorial/essential/exceptions/declaring.html)
