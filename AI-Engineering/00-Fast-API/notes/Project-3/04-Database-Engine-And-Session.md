Two pieces make the database actually usable from a FastAPI app: an **engine** (the thing that knows how to talk to the database at all) and a **session dependency** (the thing that hands each request a connection to work with, without every request opening a brand-new one).

---

## The engine

```python
from sqlmodel import create_engine

DATABASE_URL = "sqlite:///rungmunch.db"
engine = create_engine(DATABASE_URL, echo=True)
```

`create_engine` takes a **database URL** and configures the connection. The URL's prefix identifies which database and driver to use — `sqlite:///` here, `postgresql://` for Postgres, and so on — the same "swap the database without rewriting the application" promise from the ORM note, made concrete: changing databases later is largely a matter of changing this one string.

`echo=True` is a **development-only** flag: it prints every generated SQL statement to the console as it runs. Genuinely useful for seeing what SQLModel is actually doing behind the Python-object syntax — and something to turn off once an application is no longer being actively debugged, since it's pure log noise in production.

### `engine` and `Session` are not the same kind of thing

Worth being precise about the difference, since both get used constantly but play very different roles:

- **`engine`** is built **once**, at module load, and lives for the entire running life of the app — every part of the app that needs the database imports and reuses this same one object. It's not an active connection to anything by itself; it's the configuration plus a managed pool of connections, kept ready.
- **`Session`** is created **fresh, per use** — one is opened, used to run some queries or stage some changes, and closed again, over and over, for as long as the app keeps running.

The parallel worth holding onto, since it directly mirrors something already covered: `engine` is to the whole app what `app = FastAPI(...)` is — built once, alive for the app's entire lifetime. `Session` is to one unit of work what a single request being handled is — created fresh, does its one job, and finishes, repeatedly.

`engine` staying as one shared object throughout the app isn't something SQLAlchemy enforces or guards against — calling `create_engine(...)` a second time elsewhere would simply produce a second, independent engine with its own separate connection pool. What actually keeps it to one in practice is Python only running a module's top-level code once: `engine = create_engine(...)` sits at the top of `database.py`, so it executes exactly once, and every file that does `from database import engine` afterward gets a reference to that same already-built object rather than triggering the line again. The "only one" property is a matter of consistently importing it from one place, not something the `Engine` class itself defends against being broken.

---

## Creating the tables

```python
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

Every SQLModel class defined with `table=True` registers itself with `SQLModel.metadata` the moment it's defined. `create_all(engine)` walks through everything registered there and creates the corresponding tables in the actual database — one call, regardless of how many table classes exist. Where this function actually gets *called* (so it runs once, at the right moment) is a separate question — that's what the lifespan note covers next.

---

## The session dependency — the real version of an earlier hypothetical

Back when the request lifecycle's dependency-resolution stage was first covered, a database session was used as the *example* of what a dependency typically provides — described, but not yet built. This is that example, made real:

```python
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session
```

```python
@app.post("/reviews")
def create_review(review: ReviewCreate, session: Session = Depends(get_session)):
    ...
```

A few things worth being precise about:

- **`yield`, not `return`.** This makes `get_session` a **generator-based dependency**, and FastAPI specifically recognizes this pattern. Code *before* the `yield` runs as setup, the *yielded value* is what gets injected into the route as `session`, and anything *after* the `yield` (were there anything here) would run as cleanup, once the request has finished being handled — not before.
- **`with Session(engine) as session:`** — the same context-manager pattern as opening a file. When the generator resumes past its `yield` (because the request is done), the `with` block's exit logic runs automatically, closing the session. No `try`/`finally` needs to be written by hand here — the context manager already handles it.
- **`Depends(get_session)`** is what actually wires this dependency into a route — the concrete syntax behind the abstract "dependency resolution" stage covered much earlier, now doing real work: FastAPI calls `get_session()`, takes what it yields, and hands that to the route as the `session` parameter.

> [!note] No `@asynccontextmanager` here, unlike `lifespan` — and deliberately so, not an omission. `lifespan` is driven by Starlette's ASGI lifespan handling, which calls `async with` directly on it — for that to work, it genuinely has to be a real context manager object, which is exactly what `@asynccontextmanager` produces from a plain generator. `get_session`, by contrast, is consumed by FastAPI's own `Depends(...)` machinery, which has built-in native support for **any function that yields exactly once** — no decorator required. FastAPI drives the generator itself: runs it up to `yield`, injects the yielded value into the route, then resumes it (running whatever comes after `yield`) once the request finishes. Same setup/yield/cleanup shape in both places, but two different consumers with two different requirements — only one of them demands an actual context manager object.

> [!important] This is not "a new connection for every single request." Database connections are relatively expensive to open, so they're **pooled** — a limited set of connections shared across requests, handed out and returned rather than created fresh each time. `get_session` participates in that pooling; it doesn't bypass it. The `with` block ensures a session gets returned to the pool promptly once a request is done with it, rather than being held open indefinitely.

The overall shape — a small amount of code producing a large amount of behavior — is intentional. Session lifecycle, connection pooling, and automatic cleanup are all happening underneath these two or three lines; the comments in the actual source exist specifically because so much is implied by so little code.
