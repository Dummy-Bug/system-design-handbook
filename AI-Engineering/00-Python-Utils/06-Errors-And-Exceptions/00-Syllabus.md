#python #exceptions #error-handling #reliability #python-utils #syllabus

# 06 · Errors & Exceptions — Syllabus

16 concepts. **Generic** — the language's error model plus the reliability patterns built on it.

> Two halves that belong together. The first is the language: the hierarchy, chaining, exception groups. The second is what you *do* with failure in a distributed service — retries, backoff, timeouts, circuit breakers. Splitting them would leave the patterns floating without their mechanism.

**Why this sits sixth:** exception classes need inheritance (02), retry decorators need decorators (03), and `except*` only makes sense alongside `TaskGroup` — which is already written up in folder 08 and currently has *no* companion explanation of the exception-group machinery it raises.

**Currency check (2026-08-04):** the recent history here is unusually active. **`ExceptionGroup` and `except*` (PEP 654) landed in 3.11**, together with `asyncio.TaskGroup` — they are two halves of one design. **`add_note()` (PEP 678)** also arrived in 3.11. Python 3.14 relaxed the parenthesis requirement on multi-exception `except` clauses. Verify all three against the changelog before writing.

---

## A · The language model

**1. The exception hierarchy**
`BaseException` → `Exception` → everything else. Why `KeyboardInterrupt` and `SystemExit` sit *outside* `Exception`, and why `except Exception:` is therefore the right broad catch and `except BaseException:` almost never is.

**2. `try` / `except` / `else` / `finally`**
All four clauses, including the two that get skipped: `else` (ran only if no exception) and the interaction of `finally` with `return`.

**3. Catching precisely**
Multiple exception types, ordering from specific to general, and why bare `except:` is a bug rather than a style choice.

**4. Raising, and re-raising**
`raise`, bare `raise` inside an `except` block to preserve the traceback, and why `raise e` is subtly worse.

**5. Exception chaining**
`raise X from Y`, `raise X from None`, and `__cause__` vs `__context__`. Turning "an error happened while handling another error" from noise into a readable causal chain.

**6. Custom exception classes**
Designing a hierarchy — one base class per subsystem so callers can catch at whatever granularity they need. **Already done in the FastAPI notes** (custom exception + `add_exception_handler`) without discussing the design principle.

**7. `add_note()`**
Attaching runtime context to an exception as it propagates, without wrapping or losing the original.

## B · Concurrent failure

**8. `ExceptionGroup` and `except*`**
When several things fail *at once*, a single exception can't represent it. The group type, the `except*` syntax that filters by member type, and the fact that multiple `except*` clauses can each fire for one group.

**9. `TaskGroup` and structured concurrency failure**
What actually happens when one task in a group raises: siblings cancelled, errors collected, an `ExceptionGroup` raised at the boundary. **This is the missing companion to `08-Async/07`**, which introduces `TaskGroup` without explaining the exception machinery it depends on.

**10. `CancelledError`**
Why it inherits from `BaseException` and not `Exception` (so a broad `except Exception:` doesn't accidentally swallow a cancellation), and the rule that a caught `CancelledError` must be re-raised.

**11. Timeouts**
`asyncio.timeout()` / `wait_for`, what a timeout does to the task underneath, and why every outbound network call in a production agent needs one.

## C · Reliability patterns

**12. Retries and backoff**
Which errors are retryable (transient network, 429, 5xx) and which are not (400, auth, validation). Exponential backoff, jitter and why it exists, retry budgets/caps. Idempotency as the precondition that makes retrying safe at all.

**13. Circuit breakers**
Closed / open / half-open. Failing fast instead of piling requests onto a service already falling over. **Named in Sarvam's Week 9.**

**14. Graceful degradation and fallbacks**
Fallback models, cached responses, partial results. The judgement call: when a degraded answer beats an error, and when it's actively worse.

**15. Error handling at the API boundary**
Mapping internal exceptions to HTTP status codes in one place; never leaking stack traces to clients; correlation IDs so a user-facing error can be traced back to a span. Bridges toward the observability work.

**16. `warnings`, and logging exceptions properly**
`logger.exception()` vs `logger.error()`, keeping the traceback, and not logging the same error at three levels of the stack.

---

## Deferred

| Topic | Goes to |
|---|---|
| `TaskGroup` mechanics and the event loop | 08 (written) |
| Tracing, spans, correlation IDs in depth | outside this vault (`02-Observability`) |
| Pydantic `ValidationError` specifics | 09 (written) |
| `pytest.raises`, testing failure paths | 10 |

## Where this already shows up in these notes

`00-Fast-API` — custom exception classes + `add_exception_handler`, and `HTTPException` throughout the CRUD routes. `08-Async/07` — `TaskGroup`, whose failure semantics are exactly concepts 8–10. `09-Pydantic` — `ValidationError` in nearly every note.

## Interview hooks

*"A tool call to an external API fails intermittently — walk me through what your agent does."* The full answer touches retryable-vs-not, backoff with jitter, timeouts, circuit breaking, and fallback — concepts 11–14 in sequence. Sarvam names backpressure and circuit breakers explicitly (Week 9) and LangGraph exception handling (Week 5).

## Sources to verify against

- [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html) — the hierarchy for concept 1
- [PEP 654 — Exception Groups and `except*`](https://peps.python.org/pep-0654/) · [PEP 678 — Exception Notes](https://peps.python.org/pep-0678/) · [PEP 3134 — Exception Chaining](https://peps.python.org/pep-3134/)
- [`asyncio` — timeouts and cancellation](https://docs.python.org/3/library/asyncio-task.html)
