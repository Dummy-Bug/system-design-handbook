#sse #streaming #http #errors #limits

**A streaming response commits to being a success before it has produced anything.** Everything awkward about failing halfway through follows from that one fact, and the workarounds for it are the reason SSE clients look the way they do.

# The status code is sent first

An HTTP response begins with a status line, then headers, then the body. In that order, on the wire.

```text
1  HTTP/1.1 200 OK                    ← sent immediately
2  Content-Type: text/event-stream
3
4  data: ...                          ← sent over the next twenty seconds
```

For an ordinary response this ordering is invisible, because the whole thing is assembled and sent together — the server knows whether it succeeded before it writes anything.

A stream cannot work that way. The headers have to go out at the beginning, so the client knows a stream is starting and can begin listening. **At that moment nothing has been generated, no tool has been called, and nothing is known about whether any of it will work.**

> The server has already promised `200 OK` for an answer it has not started.

# So a failure halfway through cannot be a failure

Twelve seconds in, a tool call fails, or the model returns nonsense, or a database is unreachable.

```text
1  raise HTTPException(status_code=500)
```

That does nothing useful. The 200 left the building twelve seconds ago and cannot be recalled — the client read it, believed it, and has been appending tokens to the screen ever since.

Two options remain, and neither is good.

## Option one — close the connection

The server stops writing and drops the connection.

The problem is that this is **indistinguishable from a network failure.** A stream that ends and a stream that dies look identical to the client: bytes stop arriving. So the client has to guess, and whichever guess it makes is wrong half the time.

Worse, a browser doing SSE properly will treat it as a drop and **reconnect** — so a deliberate failure turns into a retry loop against a server that is going to fail again.

## Option two — send the error as a frame

```text
1  event: error
2  data: {"message":"could not reach the records system"}
3
```

This works, and it is what production systems do. But notice what it costs: **the error is now application data rather than an HTTP failure.** Nothing in the transport says anything went wrong.

- monitoring that counts non-200 responses sees a success
- a load balancer's error rate stays flat
- anything retrying on HTTP status has nothing to retry on
- the client must be written to understand this specific frame, or it will render an error object as though it were an answer

> [!important] The status code stops being the source of truth
> Once a response streams, whether it succeeded is a property of its **content**, not its status line. Every piece of tooling that assumes otherwise — dashboards, retries, alerting — is now looking at the wrong thing, and will report a service as healthy while every request fails twelve seconds in.

# Which is why a terminal frame matters

Given that a clean finish and a dead connection look the same, the only way to distinguish them is for the server to say so explicitly:

```text
1  event: done
2  data: [DONE]
3
```

Without it, a client cannot tell the difference between an **answer that finished** and a **connection that died** — so it either shows an error every time a request succeeds, or hides every real failure. There is no third behaviour.

With it, three outcomes become distinguishable:

```text
1  done frame arrives     → finished properly
2  error frame arrives    → failed, and here is why
3  neither, stream ends   → the connection died
```

# Failing before the stream starts is easier

All of the above applies only after the headers are sent. Anything checkable **before** that can still use ordinary HTTP.

```text
1  is the caller authenticated       → 401, normally
2  is the request well-formed        → 400, normally
3  are they over their quota         → 429, normally
4  ─────────────────────────────────────────────────
5  headers go out — 200 OK
6  ─────────────────────────────────────────────────
7  everything after this             → an error frame, or nothing
```

Which makes that line a genuine design boundary. **Anything that can be validated early should be**, because the tools available on the near side of it are enormously better than the ones on the far side.

# The other limit: how many streams a browser will open

A browser will not open unlimited connections to one domain. Over HTTP/1.1 the cap is six, and **an open stream occupies one of them for its entire life.**

> Six tabs of the same application, each with a stream open, and the seventh tab does not get a slow response. It gets nothing at all — **the request is never sent**, because **there is no connection available** to send it on.

> [!warning] It presents as a hang, not an error
> The seventh tab shows a request that never completes. There is no error in the browser and nothing in the server logs — because **the request never reached the server.** It is queued inside the browser, waiting for one of the six to free up, and none of them will until a stream ends.

## Why six, and why HTTP/2 does not have the problem

In HTTP/1.1 a response body is simply bytes on the connection until it ends. **Nothing anywhere marks which response a given byte belongs to.**

So a server cannot send a little of one answer and then a little of another — the client would glue them into one mangled response. The only safe rule is to finish one before starting the next, which is exactly why a connection is occupied for a whole response.

HTTP/2 added the missing marker. Every piece of data is cut into chunks that each carry a **stream number**:

```text
1  [stream 1]  data: In recent years, AI
2  [stream 3]  data: Artificial intelligence
3  [stream 1]  data:  has transformed
4  [stream 5]  data: The field of AI
5  [stream 3]  data:  has become
6  [stream 1]  data:  how we work
```

All on one connection, all mixed together. The browser reads the number on each chunk and files it into the right tab.

That labelling is the entire difference. Once every chunk says which conversation it belongs to, interleaving becomes possible — and the cap rises from six to whatever the two ends agree on when the connection opens, typically around a hundred.

```text
1  six tabs writing essays, then a seventh
2
3  HTTP/1.1   the seventh request is never sent. that tab shows nothing,
4             with no error, for as long as the essays take
5
6  HTTP/2     the seventh gets its own stream number on the same connection.
7             all seven interleave and all seven progress
```

## What sharing one connection costs

Sharing a connection means sharing that connection's problems.

If a single packet is lost, **TCP holds back everything behind it** until it has been retransmitted — because TCP guarantees in-order delivery and has no idea those bytes belong to seven independent things. One lost packet briefly stalls all seven essays.

Six separate HTTP/1.1 connections do not have that: a loss on one affects only that one. HTTP/2 traded that isolation for the ability to run a hundred streams instead of six, which is almost always the better deal — and it is the exact problem HTTP/3 was built to solve.
