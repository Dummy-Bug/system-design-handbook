`database.py` opens with two lines that look like nothing, and one of them is the most misunderstood object in the project. This is the long version of what `create_engine` actually builds, derived by breaking the simpler thing first rather than by describing the finished thing.

```python
DATABASE_URL = "sqlite:///rangmanch.db"
engine = create_engine(DATABASE_URL, echo=True)
```

---

## The problem, before any engine

Strip every library away. Talking to SQLite from Python needs nothing but the standard library:

```python
import sqlite3

conn = sqlite3.connect("rangmanch.db")
conn.execute("INSERT INTO reviews (play_name, rating) VALUES ('Hamlet', 5)")
conn.commit()
conn.close()
```

Five lines, no framework, and it genuinely works. For a script that runs once and exits this is the whole story, and an engine would be pure overhead. Anything replacing it has to earn its place against this.

---

## Break it: one connection per request

Now make those five lines the body of a route, so they run once per request, and put the app under real traffic — say **200 requests per second**.

Every request now opens its own connection before it can do any work. For SQLite that is a file being opened, so it is cheap. For anything with a server on the other side it is a **TCP connection**, which means a **three-way handshake** — a full round trip on the network before a single byte of SQL has moved. Then the query runs, and then the connection is thrown away, so the next request pays the identical cost all over again.

That is the first thing wrong with the naive version: at 200 requests per second the app spends most of its time setting up phone calls rather than having conversations.

---

## `create_engine` is not a connection

Before fixing anything, the distinction that everything else depends on. `conn = sqlite3.connect(...)` reads like it connects, and it does. Does `engine = create_engine(...)` do the same thing?

Point both at a path that cannot possibly work:

```
sqlite3.connect(BAD)
   -> FAILED IMMEDIATELY: OperationalError - unable to open database file

create_engine('sqlite:////no/such/directory/nope.db')
   -> returned fine: Engine(sqlite:////no/such/directory/nope.db)
```

`sqlite3.connect` failed on that very line, because it really did try to open the file and there was nothing there. `create_engine` handed back a healthy-looking object for a database that **cannot exist**.

> [!important] An engine is not a connection. It is an object that knows **how** to make connections and has not made one yet. `create_engine` is pure configuration — nothing is contacted, nothing is opened, no error is possible, however wrong the URL is.

---

## What that laziness costs you

The upside is why the line can sit at the top of `database.py` at all: it runs at **import** time, before uvicorn starts, before any request exists, before the database even needs to be reachable.

The downside is that a typo produces no complaint. Change `rangmanch.db` to `rangmnach.db`, or point at a Postgres host that is down, and the line still succeeds. So which of these happens?

- **A** — the server refuses to start, the error is in the terminal immediately, nobody was ever served.
- **B** — the server starts cleanly, logs that startup is complete, looks entirely healthy, and hands a `500` to the first person who uses it.

Laziness on its own gives you **B**. The obvious guard is to make one connection at startup so the app proves the database is reachable before accepting traffic.

> [!important] This project is already in world A, and it is worth knowing precisely why. `main.py:9` calls `create_db_and_tables()` inside `lifespan`, which runs `SQLModel.metadata.create_all(engine)` — and creating tables genuinely has to talk to the database. Running the startup phase against a broken URL:
>
> ```
> running the startup phase with a broken DATABASE_URL...
>    STARTUP FAILED: OperationalError - (sqlite3.OperationalError) unable to open database file
> ```
>
> The server never reaches **Application startup complete**. But the thing saving you is the **lifespan hook**, as a side effect of creating tables — not the engine. An app that does not create tables at startup gets no such check and has to add one on purpose. The honest summary of laziness: nobody verifies the database is reachable unless something is written to verify it.

---

## The fix that fails: one shared connection

Back to the cost. Connections are expensive, so the first fix anyone reaches for is to stop making them: open **one** at startup, keep it in a module-level variable, and let every request share it. No handshake, ever again. Simpler than a pool, and it looks obviously correct.

It fails because a connection does one thing at a time, so every other request queues behind whoever is using it. Talking to a database is an **I/O-bound wait**, and serialising all of those waits through a single connection is exactly what an app cannot afford.

The arithmetic makes it concrete. If a query takes **20 ms**, one connection serves **50 queries per second** and nothing can push it higher. To handle 200 requests per second:

```
200 requests/sec  ×  0.02 sec each  =  4 connections busy at all times
```

Throughput multiplied by latency is how many you need in flight at once. So one shared connection removes the handshake cost and destroys the parallelism, which is the worse trade of the two.

> [!important] There is a second problem, and it is the one that is easy to assume away. It feels natural that a connection can only be used again once the previous request has finished with it — but nothing about a module-level variable enforces that. Two requests simply reach for the same object. That guarantee of **exactly one holder at a time** is not automatic; it is something that has to be provided by whatever hands connections out.

So the real requirement was never just **reuse connections**. It is three things at once: reuse them, have several available in parallel, and give each one to exactly one user at a time.

---

## The pool

That is precisely what a connection pool is, and the image that fits is a **bank branch**

The branch has **5 permanent counters**. A customer walks in, gets a counter to themselves, does their business, leaves, and the counter is immediately free for the next person. Nobody ever shares a counter — that is the one-holder guarantee. The counter is not dismantled between customers — that is the reuse. And five people can be served at once — that is the parallelism. All three requirements, from one arrangement.

What happens when all five are busy and a sixth customer arrives is where the real defaults live:

```
   default pool_size     = 5
   default max_overflow  = 10
   default timeout       = 30.0
```

Four stages, in this order:

1. **A permanent counter is free** — served immediately, no setup cost at all.
2. **All 5 are busy** — the branch opens a **temporary** counter rather than making anyone wait. `max_overflow=10` allows ten of them, so **15** customers can be served at once. The difference that matters: a temporary counter is dismantled the moment its customer leaves, so every one of them pays the full handshake again. Overflow is a pressure valve, not free capacity.
3. **All 15 are busy** — now the customer queues.
4. **Still queueing after 30 seconds** — the request gives up and raises a `TimeoutError`.

Stage 4 is the one to carry. A pool that is too small does not merely make an app slow; past a point it starts **failing requests outright**, and the error says nothing about the database, which is healthy the entire time.

That default `pool_size` of 5 is also not an arbitrary number — it is the arithmetic from the previous section made into a default, sized to keep a handful of queries genuinely in flight at once.

---

## The pool is per process, not per app

Everything above treats the pool as though the app has one. It doesn't, and the reason starts with something that looks unrelated: how Python handles a repeated import.

When Python imports a module, it runs that file top to bottom and stores the finished module in a cache called `sys.modules`. Every later import of the same name finds it in the cache and hands back the same object, without running the file again:

```
about to import db for the first time
   >>> db.py top-level code is running NOW
about to import db again, from another file
and directly, a third time
   same object every time: True
   'db' in sys.modules cache: True
```

Three imports, one execution. That is why `main.py` and `routes/reviews.py` both doing `from database import engine` get the identical object rather than each building their own.

But that cache lives **inside one process**. A brand-new process starts with an empty `sys.modules`, so it has to run `database.py` from scratch. And `uvicorn main:app --workers 4` starts four separate processes.

> [!important] Four workers means `database.py` executes **four times**, producing **four completely independent engines**, each with its own pool. They share no memory and no counter. `pool_size` is a per-process setting that reads like a per-app one.

So with `pool_size=5` and four workers, the app holds up to **20** connections under ordinary load. And the database has no way of knowing they belong together — it sees twenty clients that connected, authenticated, and are holding on. Every one counts against `max_connections` exactly like a connection from anywhere else: another service, a metrics exporter, a `psql` session someone opened to look around.

That mismatch is the whole trap. You reason about one application with one setting; the server counts individual clients.

### Where it actually breaks

Now suppose `pool_size` gets raised to `100`, on the reasoning that a bigger pool means more throughput. Four workers, `max_overflow=10` each:

```
4 × (100 + 10) = 440 connections the app may reach for
                 100 the Postgres server allows
```

The failure is not the pool queueing. That worker's pool believes it may open 110 and currently has, say, 30 open — **its own** 30, counted only for itself. It has capacity, so it has no reason to make anybody wait. It opens a real connection, and the server refuses it:

```
FATAL: sorry, too many clients already
```

> [!warning] The pool enforces **its own** limit and has no idea the server has one. Two separate ceilings, and only the lower one is real. Every worker independently concludes it is well within budget, and all four are correct locally while the total is over the line.

What reaches the application is that error surfacing as an `OperationalError` out of a random request — a `500`, on a route that worked a second ago, carrying a message about the database having too many clients. Retry and it may succeed, because some other worker just released one. Intermittent, spread unevenly across workers, and every word of it points at the database. The database is fine; it is doing exactly what it was configured to do. The app asked for 440 of something there were 100 of.

### Sizing it, then

Two different questions get confused into one here, and they have different answers.

**How many am I allowed?** Start at the server's limit and work backwards through the worker count:

```
4 workers × (pool_size + max_overflow)  ≤  the app's share of max_connections
```

The share is not the whole limit. Postgres holds back a few for superusers (`superuser_reserved_connections`, default 3), and the exporter, the migration tool, and your own `psql` session all need one. Budget around 80 of a 100-connection server for the app and the arithmetic gives `4 × (10 + 10) = 80`. Size it to land exactly on 100 instead, and the first time you open `psql` to debug the problem, you take a connection the app was counting on and cause the very error you are investigating.

**How many do I need?** This is the earlier arithmetic, and it is the one that actually decides the number:

```
throughput × latency = connections needed in flight
200 requests/sec × 0.02 sec = 4      -> across 4 workers, 1 per worker
```

The correct `pool_size` is the **smaller** of the two answers, and it is almost never the ceiling. Which reframes the original mistake: `pool_size=100` was not wrong merely because it exceeded what the server allows. It was wrong because nobody asked what the app needed — the number was chosen in the hope that bigger means faster. A pool sized above demand adds no throughput at all; it just holds idle connections that some other client cannot have.

---
