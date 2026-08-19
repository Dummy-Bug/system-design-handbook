Every route so far runs in response to a request. **Lifespan** is different — it's code that runs **exactly once when the app starts**, and **exactly once when it shuts down**, regardless of how many requests happen in between.

---

## The pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting up")
    yield
    print("shutting down")


app = FastAPI(title="Rangmanch Reviews API", lifespan=lifespan)
```

- **`@asynccontextmanager`** — plain Python, from the standard library's `contextlib`, nothing FastAPI-specific about it. It's what turns an `async` generator function into something usable as a context manager.
- **`yield` splits the function into two phases.**

> Everything **before** `yield` runs once, at startup. Everything **after** `yield` runs once, at shutdown. The app spends its entire running lifetime **paused** at that `yield` line.

- **`FastAPI(lifespan=lifespan)`** — the function itself is passed in, not called. FastAPI is the one that decides when to drive this generator forward: once at boot, and resuming it once at shutdown.

Read the example above and the whole shape is visible: `starting up` prints before the first request is ever served, `shutting down` prints after the last one, and nothing in between touches the function at all.

---

## What it's actually for

Printing messages is the smallest possible demonstration, not the point. Lifespan exists for **work that must happen once and must be finished before the app accepts traffic**, and for the matching cleanup on the way out. The recurring cases:

- **Setting up a database** — creating tables, or verifying the database is even reachable, before the first request can fail on it.
- **Loading something expensive into memory** — a machine-learning model, a large lookup table. Doing this per request would be ruinous; doing it once at boot costs nothing afterwards.
- **Opening shared connections** — a cache, a message queue, an external service — and closing them cleanly on shutdown.
- **Warming a cache** so the first user doesn't pay for a cold one.

The common thread is that all of these are **process-scoped**, not request-scoped. They belong to the application's lifetime, and there was previously nowhere natural to put them.

> [!important] The two halves are not optional extras of each other. The code after `yield` is the only place guaranteed to run as the app goes down — closing connections, flushing buffers, releasing whatever startup acquired. A lifespan that only sets things up and never tears them down is a leak waiting for a deploy.

---

## Where it lands in this project

This project uses lifespan for the first case on that list: creating the database tables at startup.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    print("Database tables created")
    yield
    print("Shutting down the app")


app = FastAPI(
    title="Rangmanch Reviews API",
    description="Theater reviews API for Pune's Rang Manch",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "Welcome to Rangmanch Review API"}
```

`create_db_and_tables()` is imported from this project's `database.py`, and what it does — along with the engine it needs to do it — is the subject of a later note. All that matters here is the **timing**: it runs inside `lifespan`, so the tables exist the moment the server finishes booting. No route has to be hit first, and nothing has to be run by hand before starting the app.

Running this with `uvicorn main:app --reload` produces the `rangmanch.db` SQLite file directly in the project directory, created before the app is considered ready to serve anything.

Still just one route — `/` — the same shape as the first route in every earlier project. What's different isn't the route count; it's that the app now owns a persistent database, set up automatically as part of starting up, rather than in-memory data or a hand-run setup step.
