
> [!info] The core problem
> HTTP was designed for documents — a browser asks for a page, a server sends it back. That request-response model breaks the moment you need the server to push something to the client without the client asking first. Chat, live scores, stock prices, notifications — all of these need the server to initiate. HTTP, by design, cannot do that.

---

## How HTTP actually works

Every HTTP interaction follows the same pattern: the **client always speaks first**.

```
Client → "GET /messages"  → Server
Server → "here they are"  → Client

Client → "POST /send"     → Server
Server → "ok, sent"       → Client
```

The server never taps the client on the shoulder. It can only respond to requests. This is called **half-duplex** — both sides can communicate, but only in turns, and only the client gets to start.

This is fine for most of the web. You click a link, the server sends the page. You submit a form, the server saves it and responds. The client is always the initiator.

---

## Where it breaks

Imagine WhatsApp built purely on HTTP. Alice sends Bob a message. The message hits the server. Now what?

The server cannot push it to Bob's phone. Bob's phone is just sitting there, waiting. The server has no open connection to Bob — HTTP connections close after each response. There is no pipe to push through.

The only way Bob gets the message is if Bob's phone asks for it.

```
Bob's phone → "any new messages?"  → Server
Server      → "yes, here's one"    → Bob's phone
```

But Bob's phone has to know *when* to ask. If it asks every 5 seconds, Bob's messages are up to 5 seconds late. If it asks every 100ms, it's making 10 requests per second per user — most of them returning nothing.

This is the fundamental tension: **HTTP is pull, real-time requires push.**

---

## Half-duplex vs full-duplex

This distinction comes up in every real-time system interview.

**Half-duplex** — both sides can talk, but not at the same time. One side sends, the other responds. Like a walkie-talkie — you press the button, you talk, you release, the other side responds. HTTP is half-duplex. The client always initiates. The server always responds.

**Full-duplex** — both sides can talk simultaneously, independently, at any time. Like a phone call — you can both speak at once (though it's rude). Either side can initiate. Neither side has to wait for the other.

```
Half-duplex (HTTP polling):
  Client ──── request ────► Server
  Client ◄─── response ─── Server
  (client must ask first, every time)

Full-duplex (WebSocket):
  Client ◄────────────────► Server
  (either side can send at any time)
```

Real-time systems need full-duplex. The rest of this section walks through the four approaches — short polling, long polling, SSE, and WebSockets — showing with numbers why the first three fail and why WebSockets win.

---

> [!tip] Interview framing
> "HTTP is half-duplex — the client always initiates. Real-time systems need the server to push without waiting for a request. That's the problem we're solving. Short polling and long polling fake it by having the client ask repeatedly. SSE solves the receive direction but not the send. WebSockets give us true full-duplex — one persistent connection, both sides can push at any time."
