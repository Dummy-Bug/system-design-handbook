Everything this project needs to talk to SQLite lives in one thirteen-line file, `database.py`. It defines three things, and the rest of the app imports them: an **engine**, a function that **creates the tables**, and a function that **hands out sessions**.

## The whole file, before taking it apart

```python
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///rangmanch.db"
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

`sqlite:///rangmanch.db` — the protocol prefix, three slashes, then a filename. SQLite needs no separate server process and no credentials, so that one string is the entire configuration, and running the app creates `rangmanch.db` as a real file in the project directory the first time the tables are made.

> [!note] `DATABASE_URL` is hardcoded here, which is fine for a local SQLite file during development and is a placeholder rather than a pattern to copy. A real deployment keeps it in an environment variable, so that a connection string — a hosted Postgres URL typically embeds a username and password — never sits in version control.

---

## The engine

```python
engine = create_engine(DATABASE_URL, echo=True)
```

An **engine** is the thing that knows
1. how to **reach** this database, and 
2. **hands out connections** to whoever needs one.

Three properties, and all three matter :

> **It is built once and lives for the whole process.** `engine = create_engine(...)` sits at the top of `database.py`. The first time anything imports that module, Python runs the file top to bottom and keeps the finished module **in memory**, in a dictionary called `sys.modules`. Every later `from database import engine` — from `main.py`, from `routes/reviews.py`, from anywhere — finds it already sitting in that dictionary and hands back the same object, without running the file again. What gets cached is the whole module, which is why `create_db_and_tables` and `get_session` come back from it too rather than being rebuilt.

> **It holds a pool of connections.** Opening a connection to a database is expensive — **for anything with a server on the other side it means a network round trip before a single query can run**. So instead of opening one per request and throwing it away, the engine keeps a small set of them and hands them out and takes them back. **That reuse is most of what the engine is for**.

> **It opens nothing until something asks.** `create_engine` is pure configuration; it does not contact the database at all. Which means a typo in `DATABASE_URL` raises no error on this line — the failure surfaces later, when something first tries to use it.

The URL prefix is what selects the database: `sqlite:///` here, `postgresql://` elsewhere. Changing it does genuinely regenerate the SQL for the new database, which is the ORM promise made concrete — but it is not a whole migration. The data does not move, the new database's driver has to be installed, and a stricter database will reject rows SQLite quietly accepted.

### `echo=True` — seeing the SQL

**This is a development flag that prints every statement the ORM generates**, as it runs. It is the one setting that makes the translation layer visible. Creating a review with it on produces:

```
BEGIN (implicit)
INSERT INTO reviewtable (play_name, rating, created_at) VALUES (?, ?, ?)
[generated in 0.00007s] ('Hamlet', 5, '2026-08-19 14:08:49.193120')
COMMIT
```

Reading those four lines one at a time:

- **`BEGIN (implicit)`** — a transaction opened. Everything after this is provisional until something finalises it.
- **`INSERT INTO ... VALUES (?, ?, ?)`** — the SQL statement itself, **with blanks in it**. Three question marks where three values should go. Nobody wrote this by hand; it was generated from a Python object.
- **`('Hamlet', 5, '2026-08-19 ...')`** — the values, on their **own line**, sent as a separate thing.
- **`COMMIT`** — the transaction finalised. Now it is permanent.

### Why the values being on a separate line matters

Imagine the values had been pasted into the statement instead, which is what writing SQL by hand normally means:

```sql
INSERT INTO reviewtable (play_name, rating) VALUES ('Hamlet', 5)
```

That is one string. Now a user submits a play name of `'); DROP TABLE reviewtable; --` and the string becomes:

```sql
INSERT INTO reviewtable (play_name, rating) VALUES (''); DROP TABLE reviewtable; --', 5)
```

The database reads that as **two commands**, and the second one deletes the table. This is **SQL injection**: getting a value you supplied to be read as **command** rather than as **data**.

The `?` version cannot do that. The database is handed the statement first — here is the shape of the command, with three blanks — and the values afterwards, labelled as data. It never re-reads them looking for SQL. A play name containing `DROP TABLE` is just an odd-looking string that gets stored as a play name.

> [!important] This is not something the note is doing carefully — it is what an ORM does by construction. It never builds a statement by joining strings together, so there is no seam for a value to escape through. Writing raw SQL with Python string formatting removes that protection immediately, which is why `text("SELECT ... " + user_input)` is the one pattern to never write.

Worth turning off once an application is no longer being actively debugged, since in production it is pure log noise.

---

## What a Session is

An engine can hand you a connection. A **session** is what you actually work through.

**A session is a workspace for one unit of work.** Hand it objects and it keeps track of them; change them and it remembers what changed; tell it to commit and it works out the SQL needed and sends it.

> It **borrows a connection from the engine's pool** only at the moment it genuinely needs to talk to the database, and gives it back when it closes.

That last part is why a session per request does not mean a connection per request. **Sessions are cheap Python objects**; **connections are the scarce resource**, and **the engine is what rations them**.

The two are used constantly and are easy to conflate, so the distinction is worth stating flatly:

| | Lifetime | What it is |
|---|---|---|
| **`engine`** | the whole process | knows how to reach the database, holds the pool. Built once at import. |
| **`Session`** | one unit of work | a workspace that tracks objects and batches changes. Created fresh, used, closed, repeatedly. |


---

## Creating the tables

```python
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

Every SQLModel class defined with `table=True` registers itself with `SQLModel.metadata` the moment it is defined. `create_all(engine)` walks through everything registered there and creates the corresponding tables in the actual database — one call, regardless of how many table classes exist.

Where this function gets **called** was settled in the lifespan note: inside `lifespan`, so it runs exactly once as the app boots and the tables exist before the first request arrives.

> [!note] `create_all` is safe to call on every single startup, not just the first one. It checks which tables already exist and creates only what is missing, so running it against a database that already has all its tables does nothing at all. That is why it can simply be wired into lifespan and left to run on every boot, with no separate **have I already set this up** check anywhere.
>
> Safe is not the same as complete, though. It only ever **creates missing tables** — it will not **alter a table that already exists**. Add a column to `ReviewTable` tomorrow and `rangmanch.db` will not gain it: no error, no warning, **just a silent mismatch until something queries that column and fails**. **Changing a table that already holds data is a separate job, handled by a migration tool such as Alembic**.

---

## Handing a session to a route

Every route that touches the database needs a session. None of them should be building one by hand — that would put the same open-it, use-it, close-it dance into every single route, and the closing half would get forgotten eventually. FastAPI's dependency system exists for exactly this: a route declares what it needs, and something else is responsible for supplying it and cleaning it up.

`get_session` is that supplier, and it is the concrete version of the database-session example the request-lifecycle note used when dependency resolution was first described.

```python
def get_session():
    with Session(engine) as session:
        yield session
```

```python
@app.post("/reviews")
def create_review(review: ReviewCreate, session: Session = Depends(get_session)):
    ...
```

Three things worth being precise about:

- **`yield`, not `return`.** This makes `get_session` a **generator-based dependency**, which FastAPI recognises specifically. Code **before** the `yield` is setup, the **yielded value** is what gets injected into the route as `session`, and anything **after** the `yield` is cleanup.
- **`with Session(engine) as session:`** — the same context-manager pattern as opening a file. When the generator resumes past its `yield`, the `with` block's exit logic runs automatically and closes the session, returning its connection to the pool. No `try`/`finally` has to be written by hand.
- **`Depends(get_session)`** is what wires it in. FastAPI sees that parameter, calls `get_session()` itself, takes whatever the function yields, and passes it in as `session`. The route never calls `get_session` — it only declares that it wants one.

### Cleanup runs later than it looks

The code after `yield` does **not** run the moment the route function returns. Instrumenting both with print statements and sending one real request gives the exact order:

```
>>> [get_session] BEFORE yield: opening session
>>> [get_session] about to yield the session
>>> [route] create_review STARTED
>>> [route] create_review FINISHED, about to return
>>> [get_session] AFTER yield: closing session (cleanup)
```

Setup, then the route start to finish, then — only after the response has been prepared and sent — the line after `yield`. Cleanup is the very last thing that happens, strictly after the caller already has their response in hand.

> [!important] Which is the guarantee that matters: **the session is open for the entire time the route is running, without exception** — and it stays open a little longer still, through the response being built. That is what makes it safe for a route to return a database object and let FastAPI serialise it afterwards.

---

## Reference

> [!note]- Why `get_session` needs no `@asynccontextmanager`, when `lifespan` does
> Both functions have the identical shape — some setup, a `yield`, some cleanup — so one of them carrying a decorator and the other not looks like an oversight. It isn't. Building it up in four steps.
>
> **1 — what `with` does.** `with open("file.txt") as f:` guarantees two things happen: something at the start, something at the end, even if the middle crashes. For a file that is open and close. For `with` to work at all, the thing after it must be a **special kind of object** — one that has a defined start step and a defined end step written into it. A plain function is not that; `with some_function()` is meaningless.
>
> **2 — what both of these functions actually are.** A function with `yield` in it is a **generator**: a function you can pause. Call it, it runs until the `yield`, then stops and waits. Something else can resume it later, and it carries on from there. `get_session` runs until it yields a session and waits; `lifespan` runs its startup, yields, and waits for the whole life of the app. Both are generators, and structurally they are the same thing.
>
> **3 — who drives each one.** Somebody has to do that running and resuming, and it is a different somebody in each case. `get_session` is driven by FastAPI's `Depends(...)`, which contains code written specifically to drive generators: run it to the `yield`, take the value, hand it to the route, come back and resume afterwards. It works on a **bare generator**. `lifespan` is driven by Starlette, which does not hand-drive anything — it simply writes `async with lifespan(app):` and lets Python do the work. And from step 1, `with` will not accept a generator.
>
> **4 — so what the decorator is for.** `@asynccontextmanager` is an **adapter**. It takes your generator and wraps it in the special object shape `with` requires. That is its entire job.
>
> | | Driven by | Needs the decorator? |
> |---|---|---|
> | `get_session` | FastAPI's `Depends`, which drives generators itself | **No** |
> | `lifespan` | Starlette, which uses `async with` | **Yes** |
>
> The one-line version: **the decorator is there because Starlette uses `with` and FastAPI doesn't.** Nothing about it is to do with async versus sync.
