#python #context-managers #with #resource-management #python-utils #syllabus

# 05 · Context Managers — Syllabus

13 concepts. **Generic** — the protocol, not any one library's managers.

> Smaller than its neighbours, and that's correct — this is a narrow protocol with wide reach. The reason it earns a folder rather than a paragraph is that **its async variant is load-bearing for everything else in this vault**: FastAPI lifespan, database sessions, HTTP client lifetimes, and every **acquire a connection, guarantee release** pattern in a concurrent service.

**Why this sits fifth:** `@contextmanager` converts a generator into a context manager, so folder 04 has to come first. After that, this is a short folder.

**Currency check (2026-08-04):** stable. `contextlib.asynccontextmanager` (3.7+) and parenthesised multi-item `with` (3.10+) are the two additions that matter. Worth verifying `contextlib.aclosing` and `AsyncExitStack` behaviour if you rely on them for streaming teardown.

---

## A · The protocol

**1. The problem `with` solves**
`try/finally` written correctly, every time, without the caller having to remember. Files left open, locks never released, sessions never closed — all the same bug shape.

**2. `__enter__` and `__exit__`**
What `__enter__` returns (the thing bound by `as`), and the three arguments `__exit__` receives when an exception is in flight.

**3. Suppressing exceptions from `__exit__`**
Returning truthy from `__exit__` swallows the exception. Powerful, and almost always the wrong choice — worth knowing precisely so you can recognise it in someone else's code.

**4. Writing one as a class**
The explicit version, so the decorator version reads as a shortcut.

## B · The generator route

**5. `@contextlib.contextmanager`**
One `yield`, splitting setup from teardown. Everything before `yield` is `__enter__`; everything after is `__exit__`. **This is the exact shape of FastAPI's `get_session` dependency** — already used in those notes, explainable only now that folders 03 and 04 exist.

**6. `try/finally` around the `yield`**
Why teardown code sitting bare after `yield` does **not** run if the body raises, and what the correct form looks like. The single most common bug in hand-written context managers.

**7. When the decorator isn't needed at all**
`with` only accepts an object implementing the protocol, which is the entire reason `@contextmanager` exists. But a caller that drives the generator **itself** — FastAPI's `Depends`, a `pytest` fixture with `yield` teardown — needs no wrapper, because nothing is calling `with` on it. Same generator, two kinds of consumer, and only one of them requires the decorator. The question to be able to answer: **who is driving this generator, and do they use `with`?**

**8. Multiple context managers**
Nesting, comma-separated form, and the 3.10+ parenthesised multi-line form.

## C · Async

**9. `async with`, `__aenter__` / `__aexit__`**
The async protocol — needed whenever acquisition or release itself involves I/O (opening a connection, committing a transaction, closing an HTTP session).

**10. `@asynccontextmanager`**
The async twin of concept 5. **Already used in the FastAPI notes for the `lifespan` handler** — start-up before `yield`, shutdown after — again used without explanation.

**11. Async cleanup under cancellation**
What runs when a task is cancelled mid-body, and why this is the subtle failure mode in long-lived streaming connections. Connects to backpressure/cancellation from folder 04 and cancellation in folder 08.

## D · The toolkit

**12. `contextlib` helpers**
`suppress`, `closing`, `aclosing`, `redirect_stdout`, `nullcontext`. `nullcontext` in particular for the **conditionally use a context manager** case that otherwise duplicates a code block.

**13. `ExitStack` / `AsyncExitStack`**
Composing a dynamic, unknown-at-write-time number of context managers. The escape hatch when nesting won't do — e.g. opening N connections determined at runtime.

---

## Deferred

| Topic | Goes to |
|---|---|
| Generators and `yield` themselves | 04 (written) |
| `@contextmanager` as a decorator construct | 03 (written) |
| Locks as context managers (`with lock:`) | 07 |
| Cancellation and `TaskGroup` semantics | 08 (written) |
| `pytest` fixtures with `yield` teardown | 10 |

## Where this already shows up in these notes

`00-Fast-API` — `get_session` (`yield` + teardown) and the `lifespan` handler (`@asynccontextmanager`) are both in the Project-3 notes. The Project-3 engine-and-session note now carries the concept-7 comparison — why `lifespan` needs the decorator and `get_session` does not — but states it by effect; the protocol underneath it is concepts 1-2 here. `08-Async` uses `async with` for task groups.

## Interview hooks

**How would you guarantee a database connection is returned to the pool even if the handler raises?** — a context manager, and being able to say why `try/finally` inside the generator is required rather than optional. Sarvam's §3 names connection pooling directly.

**Why does FastAPI's `lifespan` need `@asynccontextmanager` when its `get_session` dependency doesn't?** — concept 7. The answer is about who drives the generator, not about async versus sync, which is what makes it a real question rather than a trivia one.

## Sources to verify against

- [`contextlib`](https://docs.python.org/3/library/contextlib.html)
- [PEP 343 — The `with` Statement](https://peps.python.org/pep-0343/) · [PEP 492](https://peps.python.org/pep-0492/) for `async with`
- [`with` statement reference](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement)
