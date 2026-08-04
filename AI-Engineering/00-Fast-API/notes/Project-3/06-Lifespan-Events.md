Every route so far runs in response to a request. **Lifespan** is different — it's code that runs exactly once when the app starts, and exactly once when it shuts down, regardless of how many requests happen in between.

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
- **`yield` splits the function into two phases** — the exact same structural idea as the session dependency from the previous note, just operating at the scale of the whole application instead of a single request. Everything **before** `yield` runs once, at startup. Everything **after** `yield` runs once, at shutdown. The app spends its entire running lifetime "paused" at that `yield` line.
- **`FastAPI(lifespan=lifespan)`** — the function itself is passed in, not called. FastAPI is the one that decides when to actually drive this generator forward: once at boot, resuming it once at shutdown.

The concrete use here: `create_db_and_tables()` — the `SQLModel.metadata.create_all(engine)` call from the database-setup note — runs exactly once, right as the app comes up, rather than needing to be triggered manually before every run.

> [!note] `create_all` is safe to call on every single startup, not just the first one. It checks what tables already exist and only creates what's missing — running it against a database that already has all its tables does nothing at all. This is why it's fine to wire it into lifespan and just let it run every time the app boots, rather than needing some separate "have I already set this up" check.

---

## A naming collision worth untangling: two different `app`s

```python
async def lifespan(app: FastAPI):   # line A
    ...

app = FastAPI(..., lifespan=lifespan)   # line B
```

It's easy to look at these two lines and suspect a circular dependency — `lifespan` seems to need `app`, but `app` is defined *after* `lifespan`, and `app`'s own construction needs `lifespan`. **There is no circularity.** The `app` inside `lifespan(app: FastAPI)` on line A and the `app` created on line B are two unrelated things that happen to share a name.

When Python executes line A, it does not run the function body — `async def` just compiles the body into a function object and binds it to the name `lifespan`. The `app: FastAPI` in the parentheses is a **parameter declaration**, not a reference to anything that needs to already exist. `FastAPI` there is a **type annotation**, which only needs the *class* `FastAPI` to be in scope (already imported at the top) — not an instance of it. Defining a function with a parameter named `app` requires exactly as much as `def greet(name): print(name)` requires a variable called `name` to exist somewhere: none at all. `app` inside the signature is a purely **local name**, meaningless until the function is actually called with something.

So at line A: `lifespan` becomes a fully-formed function object, nothing left unfinished. At line B: `FastAPI(..., lifespan=lifespan)` runs — `lifespan` already exists in full by this point, and this line just hands that already-complete function object to `FastAPI()` as configuration, to be *called later*. The actual call only happens much further downstream, inside uvicorn's startup sequence, when Starlette invokes `lifespan(the_app_object)` — passing the fully-built `app` in as the argument at that point, long after line B has finished running.

**The sequence is strictly one-directional**: define `lifespan` → build `app`, handing it `lifespan` → *later*, something else calls `lifespan(app)`. Nothing here requires anything from the future.

---

## What a context manager actually is

Strip away `async` for a moment — this pattern has already been used, under a different name: `with open("file.txt") as f: ...`. A **context manager** is Python's general pattern for "run setup, do something, **guarantee** cleanup runs afterward — even if an exception happens in between." `open()` guarantees the file gets closed no matter what happens inside the `with` block, including a crash partway through.

`@contextlib.contextmanager` (the synchronous version) is a shortcut for building one of these from a single generator function, instead of writing a full class with `__enter__`/`__exit__` methods by hand:

- Everything **before `yield`** = the setup (`__enter__`)
- The **yielded value** = whatever `as x` would capture
- Everything **after `yield`** = the guaranteed cleanup (`__exit__`, functioning like a `finally` block)

`@asynccontextmanager` is the identical idea, for `async with` instead of `with`. FastAPI doesn't literally write `async with lifespan(app):` anywhere in *your* code — but internally, that's exactly the shape of what Starlette does with it: enter it at startup, exit it at shutdown, cleanup guaranteed either way.

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

> [!important] This is Python's own **stdout buffering** behavior, not a bug in the lifespan code. uvicorn's own status messages go through Python's `logging` module, which flushes its output immediately. A plain `print(...)` call, by contrast, only writes to a *buffer* — and when that output isn't going to an interactive terminal directly (piped to a file, captured by a process manager, or sometimes even inside certain editor-integrated terminals), Python delays actually flushing that buffer until it's full or the process exits. The print statement runs exactly when it's supposed to — the moment it becomes *visible* is what's delayed, sometimes until the whole process has already finished shutting down.

Two real fixes, if a print needs to be visible immediately rather than eventually:

- `print("Database tables created", flush=True)` — forces that one call to flush right away.
- Use Python's `logging` module instead of `print` for anything meant to be observed in real time — the same module uvicorn's own status lines already use, which is why *those* never had this problem in the first place.

---

## How "startup succeeded" actually gets signaled

`Application startup complete` shows up in the log after `yield` is reached — but nothing in the lifespan function *sends* a success signal. There is no flag being set anywhere. **The signal is simply whether an exception was raised.**

Concretely: Starlette's own startup logic runs `async with self.lifespan_context(app) as maybe_state:` — literally an `async with`, using the context manager built earlier. Underneath `@asynccontextmanager`, entering that context manager means "advance the generator until it hits `yield`." Two possible outcomes:

- **Nothing raised before `yield`** → the `async with` enters normally → Starlette treats that as success → logs `Application startup complete` → opens the socket.
- **Something raised before `yield`** → that exception propagates straight out of the same call → Starlette catches it as a startup failure.

Verified directly — raising inside the lifespan function, before `yield`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("about to fail")
    raise RuntimeError("startup exploded on purpose")
    yield
```

produces this real traceback, captured running it:

```
INFO:     Started server process [63603]
INFO:     Waiting for application startup.
ERROR:    Traceback (most recent call last):
  File ".../starlette/routing.py", line 638, in lifespan
    async with self.lifespan_context(app) as maybe_state:
  File ".../contextlib.py", line 214, in __aenter__
    return await anext(self.gen)
  File "main_broken.py", line 7, in lifespan
    raise RuntimeError("startup exploded on purpose")
RuntimeError: startup exploded on purpose

ERROR:    Application startup failed. Exiting.
```

That traceback exposes the actual mechanism directly, in Starlette's own source: line 638 is the literal `async with self.lifespan_context(app) as maybe_state:`, and underneath it, `contextlib`'s `__aenter__` calls `anext(self.gen)` — "advance the generator to its next `yield`." The raised exception surfaces straight out of `anext()`, straight out of `__aenter__()`, straight into Starlette's `async with` — caught there as `Application startup failed. Exiting.` And confirming the real consequence: a request against this broken app gets a flat connection refusal — the socket never opened at all.

> [!important] Reaching `yield` cleanly **is** the success signal, by the ordinary rules of how Python functions communicate outcomes — return normally, or raise. Lifespan doesn't invent a new signaling mechanism; it leans entirely on the one Python already has.
