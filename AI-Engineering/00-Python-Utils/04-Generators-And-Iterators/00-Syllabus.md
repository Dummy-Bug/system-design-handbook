#python #generators #iterators #streaming #python-utils #syllabus

# 04 · Generators & Iterators — Syllabus

17 concepts. **Generic** — the protocol and the syntax, not any one streaming framework.

> This is the folder that quietly unlocks three others. `@contextmanager` (05) is a generator with one `yield`. `async def` coroutines (08) grew out of generator machinery. And **every token-by-token LLM response, every SSE endpoint, every NDJSON stream is an async generator** — which is a named Sarvam requirement and currently a blank space in these notes.

**Why this sits fourth:** it needs nothing but functions, and two later folders are built directly on top of it. Doing it after decorators means `@contextmanager` can be explained as **a decorator that converts a generator into a context manager** — both halves already known.

**Currency check (2026-08-04):** `itertools.batched` is 3.12+. The `aiter()` / `anext()` builtins are 3.10+. Async generators and `async for` are long-stable (3.6+). Worth verifying: `contextlib.aclosing` and async-generator finalisation semantics, which are the sharp edge in production streaming code.

---

## A · The iterator protocol

**1. Iterable vs iterator — not the same thing**
An iterable can **produce** an iterator (`__iter__`); an iterator produces **values** (`__next__`) and exhausts. A list is iterable and can be looped twice; its iterator can't. The single most common source of **why is my generator empty the second time?**

**2. `__iter__`, `__next__`, `StopIteration`**
The full protocol, and how `StopIteration` is the agreed signal for **done** rather than an error.

**3. What a `for` loop actually does**
Desugared into `iter()` + repeated `next()` + `StopIteration` handling. Worth writing out by hand once.

**4. Writing an iterator as a class**
The verbose version — so the generator version afterwards lands as an obvious simplification rather than magic.

## B · Generators

**5. `yield` — a function that pauses**
The mental shift: the function doesn't run to completion and return; it suspends at `yield`, holding its entire local state, and resumes on the next `next()` call. **This is the same suspend/resume idea that `await` uses** — worth flagging forward to folder 08.

**6. Laziness, and why it matters at scale**
Producing values one at a time instead of building a list. Constant memory over a 10 GB file or an unbounded stream. The concrete framing: a list of a million results is a million objects in RAM; a generator is one.

**7. Generator expressions**
`(x for x in ...)` vs the list comprehension `[...]`. When the parens can be omitted.

**8. Infinite generators**
Sequences with no end, made safe by lazy consumption plus `islice` / `break`.

**9. `yield from`**
Delegating to a sub-generator. The readable way to chain and flatten.

**10. Return values and `StopIteration.value`**
A generator **can** return a final value; where it ends up and why it's easy to miss.

## C · Generators as two-way channels

**11. `.send()`, `.throw()`, `.close()`**
A generator can **receive** values, not just produce them. Rarely written by hand today — but this is the machinery `async`/`await` was built on, and knowing it is what makes coroutines stop feeling arbitrary.

**12. Cleanup: `try/finally` inside a generator**
Guaranteeing teardown even when a consumer abandons the generator early. **Directly explains FastAPI's `get_session` dependency** — `yield` the session, close it after — which the FastAPI notes used without unpacking the mechanism.

## D · Async iteration — the Sarvam-critical section

**13. Async generators**
`async def` + `yield` together. What you get: something that can `await` between yields — i.e. produce a value, wait on I/O, produce the next.

**14. `async for`, `__aiter__` / `__anext__`, `StopAsyncIteration`**
The async mirror of section A.

**15. Streaming responses end to end**
The full path: an LLM client yielding tokens → your async generator transforming them → FastAPI `StreamingResponse` / SSE / NDJSON → the client rendering progressively. **Named explicitly in the Sarvam requirements** (**SSE and NDJSON streaming over long-lived HTTP sessions to expose agent progress in real time**). Includes the framing question: what does time-to-first-token mean for a user, versus total latency?

**16. Backpressure and cancellation**
What happens when the consumer is slower than the producer, or disconnects mid-stream. Async-generator finalisation, `aclosing()`, and why a dropped HTTP connection must not leak a still-running generation.

## E · The toolkit

**17. `itertools` essentials**
`islice`, `chain`, `groupby`, `tee`, `count`/`cycle`/`repeat`, `batched` (3.12+). Batching in particular is the everyday one — chunking a stream of documents into embedding-sized batches is exactly `batched`.

---

## Deferred

| Topic | Goes to |
|---|---|
| `@contextmanager` as a context manager | 05 |
| Event loop, `await`, `TaskGroup` | 08 (written) |
| The WebSocket/audio-frame side of streaming | outside this vault (Sarvam Month 3) |

## Where this already shows up in these notes

`00-Fast-API` — `get_session` uses `yield` for setup/teardown and the notes explain the **effect** without the **mechanism**. `08-Async` — coroutines throughout, built on the suspend/resume idea introduced here. `09-Pydantic/03` — `default_factory=list` is adjacent to the laziness discussion.

## Interview hooks

Two questions land here constantly: **what's the difference between a list comprehension and a generator expression, and when does it matter?** and **how would you stream an LLM response to a client?** The second is the one Sarvam's stack makes unavoidable — token streaming appears in their Backend Engineer role description directly.

## Sources to verify against

- [`itertools`](https://docs.python.org/3/library/itertools.html) · [`contextlib`](https://docs.python.org/3/library/contextlib.html) (for `aclosing`)
- [PEP 255 — Simple Generators](https://peps.python.org/pep-0255/) · [PEP 380 — `yield from`](https://peps.python.org/pep-0380/) · [PEP 525 — Asynchronous Generators](https://peps.python.org/pep-0525/)
- FastAPI `StreamingResponse` docs, for concept 15
