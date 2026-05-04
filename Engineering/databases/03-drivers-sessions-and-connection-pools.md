#databases #drivers #sessions #connection-pool #async

---

# Drivers, Sessions, and Connection Pools

You install a database client library — say `pip install neo4j` — and write three lines to connect. But under the hood three different things are happening at three different lifetimes. If you don't separate them in your head, you'll either leak connections, share state across unrelated requests, or block your event loop.

---

## What Is a Driver, Really?

A driver is a **client library that knows the database's protocol**. Same idea as an HTTP client like OkHttp:

| Layer | HTTP | Database |
|-------|------|----------|
| Application code | "Get this resource" | "Run this query" |
| Client library | Frames request as HTTP, parses response | Frames query as binary protocol, parses typed result |
| OS | TCP socket | TCP socket |

Without a driver, your app would have to:
1. Open a raw TCP socket to the DB port
2. Do the protocol handshake (version negotiation, auth)
3. Encode queries and parameters into the binary wire format
4. Decode response streams back into language-native types

Nobody does this by hand. The driver handles all of it.

---

## Why a Pool, Not a Single Connection?

When you create a driver, it doesn't open one connection — it manages a **pool**, typically up to ~100 by default.

> [!info] Imagine your web server handles 50 concurrent requests, each running a query. With one connection, requests queue sequentially — concurrency dies. With a pool, requests grab an idle connection, run their query, and return it.

Connections are **expensive** to create:
- TCP handshake
- TLS handshake (for encrypted connections)
- Protocol handshake
- Authentication

You don't want to pay this cost per query. You pay it once per connection, then reuse.

---

## Sessions Are Lighter Than Connections

Here's where many people get confused. A session is **not** a connection.

| Object | What it is | Cost |
|--------|------------|------|
| Driver | The client library + connection pool | Heavy — create once per app |
| Session | A logical scope for related queries | Cheap — create freely |
| Connection | An actual TCP pipe | Pooled, reused |

When you open a session, **no connection is grabbed yet**. The session only borrows a connection from the pool when you actually run a query — and may even release it back between queries.

```python
async with driver.session() as session:        # cheap, no connection grabbed
    result = await session.run("MATCH ...")    # NOW a connection is borrowed
    # ... use result ...
# session closed, connection back in pool
```

---

## What Does a Session Actually Do?

A session is a **scope** for a sequence of related queries. Three things it gives you:

1. **A consistent database target** — all queries in the session run against the same database
2. **Transaction grouping** — multiple queries can share one transaction (atomic unit)
3. **Causal consistency** — read-your-writes across the queries inside the session (covered separately)

> [!info] Driver = the library. Connection = the wire. Session = the conversation.

---

## The Three Lifetimes

```
App startup ──────────────────────────────────────── App shutdown
   │                                                       │
   └─ Driver (1, singleton, opened in bootstrap) ──────────┘

   Per request / per logical operation:
       │
       └─ Session (created on demand, lives for the operation)
              │
              └─ Connection (borrowed from pool, returned after query)
```

| Object | Lifetime | Count |
|--------|----------|-------|
| Driver | Whole application | 1 (singleton) |
| Session | One unit of work | Many, transient |
| Connection | Pooled | Up to ~100, shared |

---

## Why Not Share a Session Across Requests?

Tempting — the driver is shared, why not the session too? Three reasons:

1. **Sessions aren't concurrency-safe.** You can't run two `await session.run(...)` calls in parallel on the same session. The driver expects sequential operations within a session.

2. **Logical scopes mix.** Two unrelated requests would share state (bookmarks, transaction context) for no reason.

3. **Sessions are cheap anyway.** Creating one is just a Python object — opening a connection is what's expensive, and that's already pooled.

> [!important] Standard pattern: one shared driver per app, one fresh session per logical operation, connections pooled and reused underneath.

---

## Sync vs Async

Most database drivers ship both versions:

```python
# Sync — blocks the calling thread
from neo4j import GraphDatabase
with GraphDatabase.driver(uri, auth=auth) as driver:
    driver.verify_connectivity()

# Async — yields to the event loop
from neo4j import AsyncGraphDatabase
driver = AsyncGraphDatabase.driver(uri, auth=auth)
await driver.verify_connectivity()
```

For an async web framework (FastAPI, aiohttp), **always use the async driver**. The sync driver blocks the event loop on every query, killing concurrency.

---

## Mental Model

> [!info] A driver is a library that speaks the database's language. A connection is a phone line. A session is one specific conversation. The pool is a switchboard that connects sessions to phone lines as needed.
