#databases #protocols #bolt #http #binary

---

# Why Databases Have Their Own Protocols

You're building an app that talks to a database. Your first instinct: just use HTTP — it's everywhere, every language supports it, you already know it. So why do databases like Neo4j, PostgreSQL, and MongoDB all ship their own protocols instead?

---

## What HTTP Was Built For

HTTP is a request-response protocol:

```
Client: "Give me this resource."
Server: "Here it is." [connection ends or idles]
```

It was designed for documents — a browser asks for a page, a server sends it back. HTTP/1.1 added keep-alive so the TCP connection can be reused across multiple requests, which helps. But the fundamental shape is still: one request in, one response out, repeat.

---

## What a Database Actually Needs

A database interaction looks very different:

| Need | Why HTTP struggles |
|------|--------------------|
| Stream large result sets | HTTP sends one response body — you get everything or nothing |
| Keep a transaction open across multiple queries | HTTP is stateless by design |
| Send typed data efficiently | HTTP is text-based — every value is serialized to string and back |
| Multiplexed queries on one connection | HTTP/1.1 queues requests; HTTP/2 helps but adds complexity |

> [!info] HTTP keep-alive reuses the TCP connection, but the protocol is still text-based and request-response shaped. Databases need something that speaks their native concepts: rows, nodes, transactions, cursors.

---

## Binary Protocols

Database protocols like **Bolt** (Neo4j), **pgwire** (PostgreSQL), and **MongoDB Wire Protocol** are binary:

- Values are packed as typed bytes, not text strings
- A node with 10 properties doesn't have to be JSON-serialized and parsed — it arrives as structured bytes the driver reads directly
- Result sets stream back as a sequence of records, not one giant response body

**Example — sending the integer `42`:**

| Protocol | On the wire |
|----------|-------------|
| HTTP/JSON | `"42"` — 4 bytes, string, needs parsing |
| Binary | `0x2A` — 1 byte, already an integer |

At thousands of records per query, this compounds.

---

## Bolt Specifically

Neo4j's Bolt protocol runs over a persistent TCP connection (or TLS for encrypted). The URI looks like:

```
neo4j+s://abc123.databases.neo4j.io   # encrypted bolt (Aura)
bolt://localhost:7687                  # local unencrypted
```

The Python `neo4j` driver manages the connection pool for you — you never write raw bytes. But under the hood, every `session.run("MATCH ...")` call goes over this persistent binary channel, not an HTTP request.

---

## When Would You Use HTTP With a Database?

Some databases do expose an HTTP API alongside their binary protocol — Neo4j has one too. It's useful for:

- Quick one-off queries from a browser or curl
- Environments where only HTTP is available (some firewalls block custom ports)
- Simple read-only integrations that don't need performance

But application code that runs in a loop, handles transactions, or processes large results should always use the native driver over the binary protocol.

---

## Mental Model

> [!info] HTTP is a postal service — you write a letter, send it, get a reply. A database protocol is a phone call — the line stays open, you exchange information back and forth, and you hang up when the conversation is done.
