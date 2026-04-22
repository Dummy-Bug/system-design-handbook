
> [!info] The core idea
> Both OT and CRDT solve the same problem — merging concurrent edits in a collaborative document without losing anyone's work. They take fundamentally different approaches. OT needs a central server as arbiter. CRDT needs no coordination at all. The trade-off is simplicity vs decentralization.

---

## The core difference — coordination

**OT requires a central server.**

Every operation goes to the server. The server decides the order, transforms all concurrent operations based on what already happened, and sends the result back to all clients. Two clients cannot resolve conflicts on their own — the server is the arbiter.

```
Client A → Insert("X", pos=0) → Server → transforms → broadcasts to all clients
Client B → Insert("Y", pos=0) → Server → transforms → broadcasts to all clients
```

Without the server, clients are stuck. No offline editing possible.

**CRDT requires no central coordinator.**

Any two nodes can merge their states independently and always reach the same result. The data structure itself is designed so concurrent writes always converge — no server, no transformation logic needed.

```
Client A and Client B merge directly → same result guaranteed
```

Works offline. Works peer-to-peer. No single point of failure.

---

## Why is CRDT more complex for text?

A G-Counter is simple — each node has one number and merge is just max(). But text is not a counter. To support text editing with CRDTs, you need a data structure called **RGA — Replicated Growable Array**.

Every single character gets a unique ID, a logical timestamp, and a pointer to the previous character. The document is no longer a simple string — it's a linked structure of character nodes with metadata.

```
OT document:   "Hello" — just a string, positions are simple integers
CRDT document: each character carries a unique ID, timestamp, and predecessor pointer
```

This makes CRDT documents heavier in memory, harder to implement correctly, and more complex to reason about. For SDE-2 you do not need to know RGA internals — just know that CRDT for text is significantly more complex than OT.

---

## OT vs CRDT — when to use which

| | OT | CRDT |
|---|---|---|
| Needs central server | Yes | No |
| Works offline | No | Yes |
| Document structure | Simple string | Complex (unique ID per character) |
| Implementation complexity | Moderate | High |
| Used by | Google Docs | Figma, some newer editors |

**Use OT when** you have a central server and want a simpler implementation. Google Docs has been running on OT since 2009 — it works well.

**Use CRDT when** you need offline editing, peer-to-peer sync, or no central server. Figma uses CRDTs for collaborative design editing.

> [!tip] Interview framing
> "Google Docs uses OT — every operation goes through a central server which transforms concurrent operations and broadcasts the result. CRDT is an alternative that needs no server — any two clients can merge directly and always converge. But CRDT for text requires each character to carry a unique ID and metadata, making it significantly more complex to implement. Google chose OT for its simplicity. Newer tools like Figma use CRDTs for offline-first and peer-to-peer use cases."
