The claim that FastAPI handles concurrent requests better than Flask is easy to state and easy to leave unexamined. Tracing one concrete example — a `GET /hello/<id>` endpoint that looks a name up in a database and returns `"Hello {name}"` — through each model makes the difference mechanical instead of a slogan.

Setup for all four traces: the DB round-trip takes 100ms. Two requests arrive close together — Request A (`id=1`, Elon Musk) and Request B (`id=2`, someone else).

---

## One WSGI worker, single-threaded

The baseline: one process, one thread, no extra workers.

> [!warning] This is **not** what a plain `flask run` gives you. Flask's development server has been **threaded by default since Flask 1.0**, so `flask run` overlaps these two requests and finishes in ~100ms — it behaves like the `gthread` trace further down, not like this one. Reaching the serial trace below deliberately takes `flask run --without-threads`. The trace is still the right place to start, because it is the mechanism every other model here gets measured against; it just isn't a default anyone hits by accident.

```
t=0ms    Request A arrives. Worker thread starts executing the view function.

t=0ms    Thread calls db.query(id=1) — a BLOCKING call.

t=0-100ms   Thread does nothing. Not "working slowly" — nothing. It cannot
            look at Request B, cannot start anything else. It is parked,
            waiting for bytes to arrive on the DB socket.
            
t=100ms  DB responds. Thread resumes, builds "Hello Elon Musk", sends it.

t=100ms  ONLY NOW does the thread become free to look at Request B.

t=100ms  Worker picks up B, calls db.query(id=2).

t=100-200ms  Same blocking wait.

t=200ms  Response B sent.
```

**Total: 200ms, fully serial.** Request B's user waits 100ms before their request is even looked at — not because the DB is busy, but because the one thread available was idle on A's call and had no way to switch to B during that idle time.

> [!important] This is the literal meaning of **one request per worker.** The worker isn't the CPU — the CPU is doing nothing during that 100ms too. The worker is a thread, and a blocking call doesn't return control to anything else until it finishes.

---

## Flask in production — gunicorn, 4 sync workers (processes)

Gunicorn's default `sync` worker class forks **separate OS processes**, each a full copy of the app loaded independently into memory, each listening on the same shared socket.

```
t=0ms    Request A → OS routes it to Worker Process 1

t=0ms    Request B → OS routes it to Worker Process 2

t=0-100ms   Both processes independently blocked on their own DB call,
            AT THE SAME TIME — genuine parallelism now
            
t=100ms  Both respond, roughly together
```

**Total: ~100ms for both.** Real overlap, because A and B are on separate processes, each free to sit idle without blocking the other.

The **concurrency ceiling is now the worker count**. A 5th simultaneous request queues until one of the 4 finishes its DB call — **even though all 4 workers are doing nothing but waiting at that exact moment**. Scaling this to 1,000 concurrent slow requests means something close to 1,000 worker processes: 1,000 fully loaded Python interpreters, real memory and real OS scheduling overhead, even though 999 of them are idle on I/O at any instant.

---

## Flask, one process, multiple threads (gunicorn `gthread`, `--threads 4`)

A process is not capped at one thread — that was a design choice of the default `sync` worker, not a hard limit. `gthread` runs several OS threads inside one process.

```
Process 1
├── Thread 1: db.query(id=1) → GIL released while waiting on the socket
└── Thread 2: db.query(id=2) → picks up the GIL, starts its own query,
                                 also releases it while waiting
```

**Why this works despite Python's GIL:** the **Global Interpreter Lock** means only one thread in a **process** executes Python **bytecode** at any instant — no real parallel **computation** within one process. But **a blocking I/O call releases the GIL while it waits.** So Thread 1, parked inside `db.query()`, has let go of the GIL; Thread 2 is free to start its own query in the meantime. Both can be genuinely waiting on their own DB calls simultaneously, in one process.

This buys the same kind of overlap as more processes, but cheaper — **threads share one loaded copy of the app instead of each process duplicating it**.

**The limit:** if the work were CPU-bound instead of I/O-bound — resizing an image rather than waiting on a DB — the GIL would prevent the overlap. Only one thread could actually be computing at a time; **separate processes would be required for real parallelism**.

---

## FastAPI/ASGI — one worker, async

Requires an **async** DB driver — `asyncpg` for Postgres, `motor` for Mongo — something that supports `await`.

```
t=0ms    Request A arrives. Event loop starts running the coroutine for A.

t=0ms    Coroutine hits: await db.query(id=1)

t=0ms    This does NOT block the thread. It registers "wake me when the DB
         socket has data" with the OS, then hands control back to the event   
         loop.
         
t=0ms    Event loop is free — it picks up Request B, starts its coroutine.

t=0ms    Coroutine B hits: await db.query(id=2). Same thing — yields control back.

t=0ms    Both DB queries are now in flight AT THE SAME TIME, on one thread.

t=100ms  DB responds to both around the same time. The OS tells the event
         loop both sockets are ready.
         
t=100ms  Event loop resumes coroutine A exactly where it left off, sends its response.

t=100ms  Event loop resumes coroutine B, sends its response too.
```

**Total: ~100ms for both — on a single thread.** No extra processes, no extra threads. The 100ms of **waiting for the DB** was never idle time: the moment A started waiting, the same thread used the gap to go start B.

This is **cooperative multitasking**: a coroutine voluntarily gives up the thread the instant it has nothing to do but wait, and the event loop uses that gap to advance someone else. Nobody was ever blocked; the DB was busy, the thread never was.

> [!important] The landmine. This only works if the DB call is genuinely non-blocking. Write `async def` but call a **synchronous** driver like `psycopg2` inside it, and that call does not yield — it freezes the thread exactly like the single-threaded WSGI worker did. Worse, actually: since one thread runs the **entire** event loop, that single blocking call stalls every other request in the whole app, not just its own. Code that looks async but isn't turns a fast framework into something slower than plain Flask — the concrete case behind the **moving parts you never see** warning.

---

## FastAPI/ASGI — multiple workers

`uvicorn main:app --workers 4` spawns 4 separate processes, same idea as gunicorn — except **each process runs its own independent event loop**, doing the full async trace above on its own.

```
Process 1's event loop: juggling however many requests land on it, concurrently

Process 2's event loop: juggling its own set, concurrently

Process 3, Process 4: same
```

The concurrency ceiling isn't **4 requests** the way it was for 4 sync WSGI processes — it's **4 processes, each capable of holding many requests in flight at once.** If one event loop comfortably juggles ~200 concurrent I/O-bound requests, 4 workers gets you toward 800 on the same hardware that gave sync WSGI a ceiling of 4.

---

## Threads vs. coroutines for I/O-bound work

Flask-with-threads and FastAPI-async both overlap I/O waits within a single process. They are not the same mechanism, and the difference shows up at scale.

**1. Cost per unit of concurrency.**

An OS thread is a real, heavy object — the OS reserves it its own stack (commonly 512KB–8MB depending on the platform), and the kernel has to context-switch between threads, an actual kernel-level operation with real cost.

A coroutine is a **user-space object** — a few kilobytes, no OS involvement, no kernel context switch. Nothing preempts it; it hands control back voluntarily at `await`.

| | Cost for 1,000 concurrent requests |
|---|---|
| Flask + OS threads | ≈ 1,000 threads, several GB of **reserved address space**, plus 1,000 kernel-scheduled entities |
| FastAPI + coroutines | ≈ 1,000 coroutines ≈ a few MB, all invisible to the kernel |

> [!note] Be careful with that GB figure, because it is the one an interviewer will push on. A thread's stack is **reserved address space**, not memory actually consumed — pages get committed only as they're touched, so a thread that never recurses deeply costs tens of KB of real RAM, not 8MB. The honest version of the cost argument isn't **threads eat all your RAM**; it's that every thread is an object the **kernel** has to know about and schedule, while a coroutine is invisible to the kernel entirely. Scheduling and context-switch overhead is what stops scaling at thousands of threads, well before memory does.

At tens of concurrent requests this barely registers. At thousands, it's the entire reason ASGI exists — not that async code computes faster, but that each unit of **waiting** costs almost nothing.

**2. When control can switch.**

An OS thread can be preempted by the scheduler at almost any point, mid-instruction, whenever the OS decides — unpredictable from the programmer's side. Two threads touching the same shared mutable state need locks, because the interleaving could land anywhere.

A coroutine only yields at an explicit `await`. Nothing switches underneath it between two `await` points — that stretch of code runs atomically with respect to other coroutines. Easier to reason about, fewer locks required for the same correctness guarantee.

---

## Where they converge again

For **CPU-bound** work, threads and coroutines land in the same place: one process has one GIL, whether the concurrency is built from OS threads or coroutines. Neither buys real parallel computation. Both need separate processes to actually compute two things at the same instant.

The divergence is entirely on the **I/O-bound** side — which is most of what a typical backend spends its time doing. That is the actual, mechanical reason ASGI outperforms WSGI for this workload, rather than a property to take on faith.

## Full comparison

| | Flask (WSGI), 1 worker | Flask (WSGI), 4 processes | Flask (WSGI), 1 process × 4 threads | FastAPI (ASGI), 1 worker | FastAPI (ASGI), 4 workers |
|---|---|---|---|---|---|
| A + B, same time | 200ms, serial | ~100ms, parallel | ~100ms, overlapped | ~100ms, concurrent | ~100ms, concurrent |
| Concurrency ceiling | 1 in-flight request | 4 in-flight requests | 4 in-flight requests, cheaper | many (event-loop bound) | many × 4 |
| Mechanism | none — fully blocking | separate processes | GIL released during I/O wait | cooperative yield at `await` | event loop × processes |
| Cost per concurrent unit | — | one full process each | one OS thread each | one coroutine each (cheap) | one coroutine each × N processes |
| CPU-bound work | serial | parallel | still serial (GIL) | still serial (GIL) | parallel |
