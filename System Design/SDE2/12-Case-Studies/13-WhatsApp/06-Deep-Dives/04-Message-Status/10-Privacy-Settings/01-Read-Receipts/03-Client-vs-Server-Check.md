
> [!info] Who suppresses the read event — the client or the server?
> The client has the information. The server shouldn't do work it doesn't need to do.

---

## The question

Bob has read receipts turned off. He opens a chat. The read event needs to be suppressed — Alice should not get a blue tick.

Two places can enforce this:

**Option 1 — Client suppresses**
Bob's client checks its local cache. `read_receipts_on = false`. Client never sends the read event. Nothing travels over the network.

**Option 2 — Server suppresses**
Bob's client sends the read event normally. WS server receives it, checks Bob's setting in the users table (or cache), sees `read_receipts_on = false`, drops the event. Never updates `last_read_seq`. Never pushes to Alice.

Both produce the same outcome. Which is right?

---

## The case for server-side (and why it's wrong)

The argument for server-side enforcement: "keep logic on the server, clients should stay dumb."

This sounds like good architecture — centralise decisions, don't trust clients. But here the argument breaks down.

Bob opens 200 chats in a day. With server-side suppression:

```
200 read events travel over WebSocket to the server
200 times server checks Bob's setting (even if cached, it's still a network round-trip per event)
200 events are dropped
Result: 200 unnecessary network calls, 200 unnecessary server operations
```

Every single one of those was guaranteed to be dropped before it even left Bob's phone. The client knew. It just didn't act on that knowledge.

---

## The case for client-side (and why it wins)

Bob's client has the setting cached locally from login. It knows — before sending anything — that read receipts are off.

```
Bob opens chat
→ check local cache: read_receipts_on = false
→ do not send read event
→ 0 bytes sent over network
→ 0 server operations
→ 0 DB reads
```

The read event never exists. It's not generated, not sent, not received, not dropped. The problem is solved at the cheapest possible point — before any cost is incurred.

This is a general principle: **validate and filter as early as possible.** The earlier you catch something, the cheaper it is.

```
Cost hierarchy (cheapest to most expensive):
  Client local check     → memory read, ~nanoseconds
  Network call           → milliseconds + bandwidth
  Server compute         → CPU + memory
  DB read                → I/O + latency
```

The client check is at the bottom of this hierarchy — the absolute cheapest option.

---

## But what about a malicious client?

A valid concern in security-sensitive systems: if you only enforce on the client, a modified client could bypass it and send read events anyway.

WhatsApp is a closed ecosystem — the app is signed, distributed through app stores, and not modifiable by users. A tampered client is out of scope for this design. The server-side check as defence-in-depth is a valid SDE-3+ concern, but not the primary enforcement mechanism.

For this design: **client-side suppression is the answer.**

---

## The rule in one line

> [!important] Suppress at the source
> If the client knows an event will be dropped, it should never send it. Don't generate unnecessary network traffic that the server will discard.

> [!tip] Interview framing
> "Bob's client checks its locally cached setting before sending the read event. If read receipts are off, the event is never generated — it never touches the network or the server. We don't rely on server-side dropping because the client already has the information needed to make the decision."
