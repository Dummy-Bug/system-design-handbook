#python #asyncio #async #concurrency #python-utils #syllabus

# 08 · Async — Syllabus

20 concepts. **Generic** — the asyncio runtime itself, not FastAPI's or LangGraph's use of it.

> Written **after** seven notes already existed, so this list was derived from the language surface first and the existing notes checked off against it afterwards — not the other way round. That ordering matters: deriving it from what's already written would have silently confirmed that everything important was covered. It isn't. Nine of the twenty concepts have no note, and the missing ones cluster in exactly one place — **what happens when things go wrong or go slow**: cancellation, timeouts, queues, concurrency limits, and the `def`-vs-`async def` trap that costs a FastAPI service its concurrency.

**Where this sits.** Three folders share this territory and the split is deliberate:

- **07 · Concurrency Models** owns the *constraint and the alternatives* — the GIL, threads, processes, pools, and the decision framework for picking a model at all.
- **08 · Async** (this folder) owns the *runtime mechanics* — how the loop schedules, what a Task is, how cancellation is delivered, how work is coordinated inside one loop.
- **06 · Errors** owns the *failure-handling patterns* built on top — `ExceptionGroup`, `except*`, retries, circuit breakers.

So `TaskGroup` appears in both 06 and 08 on purpose: **here** it is "how does it schedule and cancel", **there** it is "what do I catch". Async *iteration* — `async for`, async generators, streaming — belongs to **04**, which claimed it as its Section D.

**Currency check (2026-08-05):** this machine runs Python 3.13.3; 3.14 is current stable. Version lines that matter and should be re-verified before relying on them: **`asyncio.TaskGroup`** and **`asyncio.timeout()`** are 3.11+; **`asyncio.to_thread`** is 3.9+; the low-level `get_event_loop`/`new_event_loop` idioms are long-deprecated in favour of `asyncio.run` and **`asyncio.Runner`** (3.11+). The live one to check: **eager task factories** (3.12+) and any 3.14 changes to task scheduling or to the default behaviour of `asyncio.run`. Also confirm the current state of **free-threaded builds interacting with asyncio**, which is where 07's currency question spills into this folder.

---

## A · The runtime

**1. The event loop**
One thread, one queue of ready callbacks, running them one at a time forever. Everything else in this folder is a way of putting something on that queue or taking it off. The framing that makes the rest land: the loop is not doing your work in parallel — it is filling the gaps *between* your waits.

**2. `asyncio.run` and the loop lifecycle**
Who creates the loop, who closes it, and what happens to tasks still pending when it shuts down. Why you almost never call `get_event_loop()` yourself any more, why `asyncio.run` cannot be called from inside a running loop, and what `asyncio.Runner` (3.11+) adds when one loop must span several entry points.

**3. Coroutine function vs coroutine object**
`async def f` defines a coroutine *function*; calling it returns a coroutine *object* and **runs none of the body**. The single most common beginner surprise, and structurally the same distinction as `square` vs `square(5)` from folder 03 — the parentheses build a thing, they don't run it.

**4. The three awaitables**
Coroutine, Task, Future — what each one is, which one the loop actually schedules, and why a Future is the low-level primitive you rarely write by hand but constantly receive.

**5. What `await` actually does**
Marks a point where this function may *suspend and hand the thread back*. Not "wait here" in the blocking sense — "I have nothing to do until this resolves, run someone else". A function with no `await` in its body never yields, no matter how many `async` keywords it carries.

## B · Scheduling and ordering

**6. `await` vs `create_task` — the bare-await trap**
Awaiting a coroutine directly means *scheduled and run to completion in one step*: three one-second calls take three seconds and look perfectly asynchronous while doing so. `create_task` is what puts work on the loop *without* waiting for it. This is the difference between async code and concurrent code.

**7. `await` guarantees completion, not execution order**
Awaiting task B before task A does not make B run first — the loop decides ordering, and the await only says "don't continue past this line until it's done". The design lesson underneath: don't try to micromanage the scheduler.

**8. `gather` and `TaskGroup`**
Running a batch and collecting results. The real difference between them is not syntax but **failure semantics** — what happens to the other twenty tasks when one raises, and what a partially-completed batch leaves behind.

**9. `as_completed`, `wait`, and `wait_for`**
Results in completion order rather than submission order, waiting on a subset, and putting a deadline on a single await. The everyday use: streaming results back as they land instead of blocking on the slowest one in the batch.

**10. Keeping a reference to a fire-and-forget task**
`asyncio.create_task(...)` without storing the result is a real bug: the loop holds only a weak reference, so a background task can be garbage-collected mid-flight and vanish without a traceback. Silent, intermittent, and near-impossible to reproduce on demand — which is exactly why it's worth knowing before meeting it.

## C · Not blocking the loop

**11. Blocking the event loop**
One synchronous call inside one coroutine freezes *every* task in the process, because a task that never suspends never hands the thread back. `time.sleep` is the teaching example; in real code it's a sync database driver, a `requests` call, `json.loads` on a 40 MB payload, or a CPU-bound loop.

**12. Escape hatches — `to_thread` and `run_in_executor`**
When the blocking call can't be removed, move it off the loop's thread and await *that*. Threads for I/O-bound blocking, a process pool for CPU-bound work — the sizing and the pool mechanics themselves belong to 07.

**13. Detecting a blocked loop**
The part usually skipped: `asyncio` debug mode, the slow-callback warning threshold, and why a service that "gets slower under load for no reason" is usually one blocking call away from an explanation. Without this concept, 11 and 12 are advice you can't act on because you can't tell whether the problem is present.

## D · Coordinating work inside one loop

**14. `asyncio.Queue` — producer/consumer and backpressure**
The async mirror of `queue.Queue`. A *bounded* queue is the simplest real backpressure mechanism there is: when the consumer falls behind, `put` suspends and the producer slows down on its own. The alternative — an unbounded queue — is a memory leak with good manners.

**15. `Semaphore`, `Lock`, and `Event`**
Limiting concurrency rather than maximising it. Firing 5,000 requests at a provider concurrently is trivial and will get you rate-limited; a `Semaphore(20)` is the one-line fix. `Lock` for the surprisingly-real case of shared mutable state between tasks, `Event` for one task signalling many.

**16. Cancellation mechanics**
How cancellation is actually delivered — `CancelledError` raised *at the next await point*, not immediately — and what that implies. `task.cancel()`, why cleanup belongs in `finally`, why swallowing `CancelledError` breaks shutdown, and `asyncio.shield` for the work that must survive. What to *catch* is 06's; how it's *delivered* is here.

**17. Timeouts**
`asyncio.timeout()` (3.11+) as a context manager and `wait_for` as the older call, what gets cancelled when the deadline passes, and the design question that outlives the syntax: which layer owns the deadline when a request spans three services.

## E · Async in a real service

**18. `def` vs `async def` in a web framework**
The trap worth its own concept: FastAPI runs a plain `def` handler in a threadpool but runs an `async def` handler **on the loop**. So a blocking call in a sync handler is merely slow, while the same call in an async handler stalls the entire process. The wrong keyword is a one-word change that inverts the failure mode.

**19. Living with sync libraries**
Real services are mixed. Which client libraries have async versions, what a sync SDK inside an async service costs, and the honest middle path — wrapping in `to_thread` and bounding the pool — versus rewriting.

**20. Debugging and observing async code**
Reading a traceback that crosses an await boundary, `asyncio.all_tasks()` for "what is this process actually doing", task names, and why a stuck async service usually looks idle from the outside. The bridge to `02-Observability`.

---

## Coverage — what is written and what is not

The seven existing notes were numbered in **writing order**, before this syllabus existed, so file numbers do not match concept numbers and are not being renamed — the notes carry Obsidian image embeds with absolute vault paths.

| # | Concept | Note |
|---|---|---|
| 1 | The event loop | `02-The-Vocabulary…` |
| 2 | `asyncio.run` and loop lifecycle | — |
| 3 | Coroutine function vs object | `02-The-Vocabulary…` |
| 4 | The three awaitables | `02-The-Vocabulary…` |
| 5 | What `await` does | `02-The-Vocabulary…` |
| 6 | The bare-await trap | `03-The-Bare-Await-Trap…` |
| 7 | Completion, not order | `04-Await-Guarantees…` |
| 8 | `gather` and `TaskGroup` | `07-Gather-And-TaskGroup` |
| 9 | `as_completed`, `wait`, `wait_for` | — |
| 10 | Fire-and-forget task references | — |
| 11 | Blocking the event loop | `05-Blocking-The-Event-Loop` |
| 12 | `to_thread` / `run_in_executor` | `06-Escape-Hatches…` |
| 13 | Detecting a blocked loop | — |
| 14 | `asyncio.Queue` and backpressure | — |
| 15 | `Semaphore`, `Lock`, `Event` | — |
| 16 | Cancellation mechanics | — |
| 17 | Timeouts | — |
| 18 | `def` vs `async def` in a framework | — |
| 19 | Living with sync libraries | — |
| 20 | Debugging async code | — |

`01-Why-Async-What-Concurrency-Means` maps to no concept here by design — it is the I/O-bound vs CPU-bound and cooperative-multitasking framing, which belongs to **07** and was written here first.

**11 of 20 written.** The nine gaps are not evenly spread: sections A and B are nearly complete, and everything in D is missing. That is the useful finding — the notes cover *making things run concurrently* and cover none of *keeping that under control*, which is the half that appears in production incidents and in interviews.

## Deferred

| Topic | Goes to |
|---|---|
| GIL, threads, processes, pool sizing, model choice | 07 |
| Async generators, `async for`, `StopAsyncIteration`, streaming responses | 04 |
| `async with`, `__aenter__`/`__aexit__`, `@asynccontextmanager`, `AsyncExitStack` | 05 |
| `ExceptionGroup`, `except*`, retries, backoff, circuit breakers | 06 |
| Testing async code, `pytest-asyncio` | 10 |
| WebSockets, WebRTC, audio frames | outside this vault (Sarvam Month 3) |

## Where this already shows up

`00-Fast-API` — every route is `async def`, and concept 18 is the thing those notes assume without stating. Xarvis — the LangGraph agents run on an event loop with 10s/15s timeouts and a fallback path, which is concepts 16 and 17 in production; the rate-limit middleware is concept 15's territory. `09-Pydantic` and `01-Type-Hints` annotate coroutines throughout.

## Interview hooks

Sarvam names **async Python** in the Stage 2 screen ("async Python execution models") and again in Week 9 — *"`asyncio` internals, task groups, backpressure handling, process pools for CPU-bound work"*, plus rate limiting and connection pooling. Backpressure is concept 14 and currently unwritten. The three questions that recur: *"you made everything `async` and it got no faster — why?"* (concept 6), *"how do you stop one slow call from taking down the service?"* (16, 17), and *"how would you limit concurrent calls to a provider?"* (15).

## Sources to verify against

- [`asyncio` — standard library docs](https://docs.python.org/3/library/asyncio.html), particularly the *Developing with asyncio* page for concept 13
- [PEP 492 — `async`/`await` syntax](https://peps.python.org/pep-0492/) · [PEP 3156 — the asyncio module](https://peps.python.org/pep-3156/)
- FastAPI's *async* concurrency page, for concept 18 — it is the clearest statement of the threadpool-vs-loop split
