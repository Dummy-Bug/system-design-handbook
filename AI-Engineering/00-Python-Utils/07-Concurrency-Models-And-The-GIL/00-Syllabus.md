#python #gil #threading #multiprocessing #concurrency #python-utils #syllabus

# 07 · Concurrency Models & the GIL — Syllabus

18 concepts. **Generic** — the three models and the constraint that shapes them.

> Deliberately scoped **around** folder 08, not overlapping it. `08-Async/01` already establishes I/O-bound vs CPU-bound and the single-thread/cooperative framing; `08-Async/06` already covers `to_thread` and `run_in_executor` as escape hatches **from inside** an event loop. **This folder owns what those notes assume:** what the GIL actually is, the threading and multiprocessing primitives themselves, worker-pool design, and the decision framework for picking a model in the first place.

**Why this sits seventh — immediately before Async:** asyncio is one of three concurrency models, and it's the wrong one for a large class of problems. Learning the constraint and the alternatives first makes `08-Async` read as **here is the model for I/O-bound work** rather than **here is how you do concurrency in Python.**

**This folder also carries a resume-defence obligation.** The 25,000 → 300,000 records/day claim rests on worker-pool concurrency, connection pooling, and Redis distributed locking. Concepts 11–16 are exactly that claim's supporting surface, and it needs to survive two minutes of probing.

**Currency check (2026-08-04):** the most actively-changing area in the language right now, and every claim below needs re-verification against the current changelog before use. **PEP 703 free-threaded (no-GIL) builds** shipped as an **experimental** separate build in 3.13 and moved toward officially-supported status in 3.14 — confirm exactly where that status sits today, since **does Python still have a GIL?** now has a version-dependent answer and getting it wrong in an interview is costly. Also verify: **PEP 684** per-interpreter GIL (3.12), **PEP 734** subinterpreters exposed as a standard-library module (3.14), and the current default `multiprocessing` start method per platform, which has been migrating away from `fork`.

---

## A · The constraint

**1. What the GIL actually is**
A single mutex around the interpreter, such that only one thread executes Python bytecode at a time. Not a Python-the-language feature — a CPython-the-implementation one.

**2. Why it exists**
Reference-counting memory management. Without a global lock, every `Py_INCREF`/`DECREF` needs its own synchronisation, which historically made single-threaded code **slower**. The GIL is a deliberate trade, not an oversight.

**3. What the GIL does and does not block**
It does **not** prevent threads from being useful: it is released around blocking I/O and inside many C extensions (NumPy et al.). It **does** prevent two threads from running Python bytecode in parallel. This distinction is the entire reason threads still help I/O-bound work.

**4. Free-threaded Python**
PEP 703, the `--disable-gil` build, and what changes when the GIL is gone: real parallel bytecode execution, at some single-threaded cost, with an ecosystem of C extensions that must be rebuilt for compatibility. Where this stands **right now** is the version question from the currency check.

**5. Per-interpreter GIL and subinterpreters**
PEP 684 / PEP 734 — the other escape route: multiple interpreters in one process, each with its own GIL. How it differs from both threads and processes.

## B · Threads

**6. `threading` basics**
`Thread`, `start`, `join`, daemon threads. What a thread costs vs a process.

**7. Race conditions and atomicity**
Why `counter += 1` is not atomic, and what **thread-safe** actually claims. The GIL does **not** make your code thread-safe — a common and confidently-stated misconception.

**8. Synchronisation primitives**
`Lock`, `RLock`, `Semaphore`, `Event`, `Condition`, `Barrier`. All usable as context managers (folder 05) — `with lock:` is the idiom.

**9. Deadlocks**
The four conditions, lock ordering as the standard prevention, and why `RLock` exists.

**10. `queue.Queue`**
The producer/consumer pattern done safely. `join()`/`task_done()`, and bounded queues as the simplest form of backpressure.

## C · Processes

**11. `multiprocessing`**
`Process`, `Pool`, and the fundamental difference: separate memory, so no shared state and no GIL contention.

**12. The cost of process boundaries**
Everything crossing between processes must be pickled. Start-up cost, memory duplication, and the cases where the serialisation overhead exceeds the parallelism gain — the thing that makes naive **just use multiprocessing** slower.

**13. Start methods**
`fork` vs `spawn` vs `forkserver` — platform defaults, why `fork` is hazardous alongside threads, and what that means for a service that forks workers.

**14. Sharing data between processes**
`Value`, `Array`, `Manager`, `shared_memory`. When shared memory beats passing messages.

## D · Pools, and designing for throughput

**15. `concurrent.futures`**
`ThreadPoolExecutor` / `ProcessPoolExecutor` behind one API. `submit` vs `map`, `Future`, `as_completed`, exception propagation out of a worker. **The most practical entry point for the majority of real work** — and the layer `asyncio.to_thread` sits on top of.

**16. Sizing a worker pool**
Why the right worker count differs for I/O-bound (high, bounded by the downstream service and the connection pool) versus CPU-bound (roughly core count). Connection pooling as the usual real bottleneck, and Amdahl's law as the ceiling on any of it.

**17. Distributed locking**
When one process's `Lock` is insufficient because the work spans machines. Redis-based locking, lock expiry and the liveness/safety trade, and an honest read of the Redlock debate. **Directly the 25K → 300K claim's foundation.**

## E · Choosing

**18. The decision framework**
One table, defensible in an interview: I/O-bound + many concurrent waits → asyncio; I/O-bound + blocking libraries you can't rewrite → thread pool; CPU-bound → process pool (or a C extension that releases the GIL); mixed → an event loop delegating CPU work to a process pool. Plus the honest fourth option: the bottleneck is the database, and none of the above will help.

---

## Deferred

| Topic | Goes to |
|---|---|
| Event loop, coroutines, `await`, `TaskGroup` | 08 (written) |
| `to_thread` / `run_in_executor` **from inside** async code | `08-Async/06` (written) |
| I/O-bound vs CPU-bound first framing | `08-Async/01` (written) |
| `CancelledError`, timeouts, retries | 06 (written) |
| Kafka / SQS / distributed task queues | outside this vault |

## Where this already shows up

`08-Async/01` introduces single-process/single-thread and cooperative multitasking; `08-Async/06` uses thread and process pools without explaining the primitives underneath. The Repute ingestion work (25K → 300K/day) is worker pools + connection pooling + Redis locking — concepts 15–17.

## Interview hooks

Three questions this folder answers, in ascending difficulty: **does the GIL make Python threads useless?** (no — I/O releases it), **why did adding processes make it slower?** (pickling and start-up cost, concept 12), and **how did you get from 25K to 300K records a day?** — where the expected follow-ups are pool sizing, connection-pool limits, and what the lock was actually protecting. Sarvam §3 names thread/worker-pool concurrency and Redis Redlock explicitly; Week 9 names process pools for CPU-bound work.

## Sources to verify against

- [`threading`](https://docs.python.org/3/library/threading.html) · [`multiprocessing`](https://docs.python.org/3/library/multiprocessing.html) · [`concurrent.futures`](https://docs.python.org/3/library/concurrent.futures.html) · [`queue`](https://docs.python.org/3/library/queue.html)
- [PEP 703 — Making the GIL Optional](https://peps.python.org/pep-0703/) · [PEP 684 — Per-Interpreter GIL](https://peps.python.org/pep-0684/) · [PEP 734 — Multiple Interpreters in the Stdlib](https://peps.python.org/pep-0734/)
- Redis distributed-locking documentation, for concept 17 — read the criticism alongside the spec
