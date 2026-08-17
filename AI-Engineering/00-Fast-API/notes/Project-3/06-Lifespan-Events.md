Every route so far runs in response to a request. **Lifespan** is different — it's code that runs **exactly once when the app starts**, and **exactly once when it shuts down**, regardless of how many requests happen in between.

---

## The pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    print("Database tables created")
    yield
    print("Shutting down the app")


app = FastAPI(title="Rangmanch Reviews API", lifespan=lifespan)
```

- **`@asynccontextmanager`** — plain Python, from the standard library's `contextlib`, nothing FastAPI-specific about it. It's what turns an `async` generator function into something usable as a context manager.
- **`yield` splits the function into two phases** — the exact same structural idea as the session dependency from the previous note, just operating at the scale of the whole application instead of a single request. 

> Everything **before** `yield` runs once, at startup. Everything **after** `yield` runs once, at shutdown. The app spends its entire running lifetime **paused** at that `yield` line.


- **`FastAPI(lifespan=lifespan)`** — the function itself is passed in, not called. FastAPI is the one that decides when to actually drive this generator forward: once at boot, resuming it once at shutdown.

The concrete use here: `create_db_and_tables()` — the `SQLModel.metadata.create_all(engine)` call from the database-setup note — runs exactly once, right as the app comes up, rather than needing to be triggered manually before every run.

> [!note] `create_all` is safe to call on every single startup, not just the first one. It checks what tables already exist and only creates what's missing — running it against a database that already has all its tables does nothing at all. This is why it's fine to wire it into lifespan and just let it run every time the app boots, rather than needing some separate **have I already set this up** check.


---

## The mystery of the missing print statement — actually explained

A genuinely common point of confusion: adding `print("Database tables created")` right after the setup code, expecting to see it in the terminal immediately on startup — and not seeing it. Worth resolving properly rather than shrugging it off, since it's a real, reproducible Python behavior, not a FastAPI quirk.

Reproducing it directly: running this exact lifespan, then killing the process, the full captured output looks like this —

```
INFO:     Started server process [62396]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8020 (...)
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [62396]
Database tables created
Shutting down the app
```

Both `print(...)` lines are there — but **at the very end**, after every one of uvicorn's own log lines, including the ones confirming the process already finished shutting down.

// deep dive needed for this callout 
> [!important] This is Python's own **stdout buffering** behavior, not a bug in the lifespan code. uvicorn's own status messages go through Python's `logging` module, which flushes its output immediately. A plain `print(...)` call, by contrast, only writes to a **buffer** — and when that output isn't going to an interactive terminal directly (piped to a file, captured by a process manager, or sometimes even inside certain editor-integrated terminals), Python delays actually flushing that buffer until it's full or the process exits. The print statement runs exactly when it's supposed to — the moment it becomes **visible** is what's delayed, sometimes until the whole process has already finished shutting down.

Two real fixes, if a print needs to be visible immediately rather than eventually:

- `print("Database tables created", flush=True)` — forces that one call to flush right away.
- Use Python's `logging` module instead of `print` for anything meant to be observed in real time — the same module uvicorn's own status lines already use, which is why **those** never had this problem in the first place.

---

The lifespan pattern wired into this project's actual entry point — `main.py`, for the first time genuinely running this app end to end.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables


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

Running this with `uvicorn main:app --reload` produces the `rangmanch.db` SQLite file — visible directly in the project directory once the app has started, created by `create_db_and_tables()` firing inside `lifespan` before the app is considered ready to serve requests. No route has to be hit first; the table exists the moment the server finishes booting.

Still just one route — `/` — same shape as the very first route in every earlier project. What's different about this file isn't the route count, it's that the app now genuinely owns a persistent database, set up automatically as part of starting up, rather than in-memory data or a hand-run setup step.

The actual review routes — `POST`/`GET`/`PATCH`/`DELETE` on `/reviews` — come next, and per the plan for this project, they won't live directly in this file: the next step is splitting routes into their own module rather than continuing to grow `main.py` indefinitely.