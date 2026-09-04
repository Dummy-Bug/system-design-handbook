#sse #streaming #fastapi #http #agents #syllabus

# 08 · Streaming and SSE — Syllabus

**9 notes, 124 rungs.** Generic — the protocol and its production failure modes, not Xarvis's implementation, which is mapped at the bottom.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — `COPY` runs once, therefore the edit does nothing, therefore there are two files, therefore the container is running a photograph. Rungs are not topics and not section headings. Eight to fifteen of them build one note.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.** That ordering is the whole design. A list of true statements about SSE teaches nothing; a chain where every step is the answer to a problem the last step created is what sticks.

**Two halves, trained differently.** Notes 1 through 7 are mechanism — what the protocol does and how it fails — and respond to retrieval practice, so the rungs are the recall unit. Note 8 is design judgement, and the evidence says retrieval drills do **not** transfer to problem-solving, so it is worked as a position defended against changed constraints rather than recalled.

**Currency check (2026-09-04):** FastAPI gained a native `fastapi.sse` module in **0.135.0, March 2026** — `EventSourceResponse` and `ServerSentEvent`, with a **15-second float default ping**. Most SSE material found by search targets the older `sse-starlette` package and its imports will not match. Re-verify before relying on: the ping default, whether `ServerSentEvent` still exposes `comment`, and nginx's current `proxy_buffering` defaults.

---

## How to teach from this

**One note per session, rungs in order, never skipping.** A skipped rung breaks the chain — the next one stops being a discovery and becomes a fact to memorise.

**Where a rung says break, it is run, not read.** Watching a stream die silently at 90 seconds produces a problem the fix attaches to. Reading that heartbeats exist produces a fact that decays.

**Recall is per note, from memory, file closed.** Recognising an answer does not count.

**Two rabbit holes are marked and binding** — TCP internals in note 4, HTTP/2 framing in note 7. Both are deep, satisfying, and pay back nothing here.

**Spacing:** re-test notes 1 to 4 after finishing note 6, and all eight after the implementation is done. Same-day re-testing is close to wasted, because retrieval works when forgetting has started.

---

## Note 1 · Why Stream At All

11 rungs. No break — this is framing.

1. A full LLM answer takes 8 to 30 seconds to generate.
2. A user staring at an empty screen cannot tell a working system from a hung one, and reloads.
3. Streaming does not make the answer arrive sooner — total time is unchanged.
4. What changes is **when the first token appears** — a few hundred milliseconds instead of thirty seconds.
5. So the metric is **time to first token**, which is a different number from total latency and improves while latency does not.
6. Polling is the obvious solution: the client asks repeatedly.
7. **Break polling** — to feel live you would ask every 100ms, which is 300 requests to deliver one answer, and still always one interval behind.
8. SSE instead holds **one** HTTP response open and writes into it over time.
9. WebSocket also stays open, but is bidirectional and requires an upgrade handshake every proxy, load balancer and CDN in the path must understand.
10. LLM output is **one-directional** — the server has everything to say, the client only listens — so WebSocket's advantage does not apply while its cost does.
11. SSE is ordinary HTTP, so existing auth, logging, compression and routing already work unchanged.

> **Recall:** Why does streaming not reduce total latency? · What makes polling unusable for this rather than merely inefficient? · Which property of LLM output decides SSE over WebSocket?

---

## Note 2 · The Wire Format

13 rungs. **Break:** yield three frames, read them with `curl -N`, then delete one blank line.

1. A frame is a set of `field: value` lines.
2. A **blank line** terminates the frame — that is the entire framing protocol.
3. **Break it** — remove the blank line and the client receives nothing at all, with no error, because it is still waiting for a frame that never ends.
4. `data:` carries the payload.
5. Several `data:` lines in one frame are joined by the client with newlines.
6. Which is how a multi-line message is sent without escaping anything.
7. It is all UTF-8 text — **there is no binary SSE**, so anything else must be encoded into text first.
8. With no `event:` field, every frame arrives at one generic handler.
9. So the client ends up switching on something inside the payload to tell frames apart.
10. `event:` names the frame, making `progress` and `done` separate listeners — a routing decision, not a formatting one.
11. `id:` stamps a position on the frame and, on its own, does **nothing**.
12. Its purpose is that the browser remembers the last id and sends it back on reconnect — every resumption story starts here.
13. `retry:` sets the client's reconnect delay in milliseconds, server-controlled, so a loaded server can back every client off without a client release.
14. A line beginning with `:` is a comment and clients ignore it — bytes carrying no meaning, which turns out to be exactly what note 4 needs.

> **Recall:** What terminates a frame, and what is the symptom when it is missing? · Which field does nothing by itself, and what makes it matter? · Why is a comment the right shape for a heartbeat?
>
> **Stop:** No WHATWG parsing algorithm, BOM handling, or field-name edge cases.

---

## Note 3 · The Browser Client

12 rungs. **Break:** kill the server mid-stream and watch the browser reconnect with no code from you.

1. `EventSource` is the browser's built-in SSE client.
2. It handles framing, dispatch, reconnection and id tracking for free.
3. **Break the server** — the browser reconnects on its own after the retry interval.
4. So reconnection is **normal**, not an error, and the endpoint must handle being reopened.
5. And a dropped connection is not something to surface to the user as a failure.
6. `EventSource` issues **GET only**.
7. And cannot set request headers.
8. So there is no `Authorization` header — auth must travel in a cookie or a query string.
9. And query strings land in access logs, which is why this constraint changes designs.
10. On reconnect the browser sends **`Last-Event-ID`** carrying the last id it saw.
11. The server is expected to replay everything after it — but the protocol supplies **only the handshake**, and the buffer of already-sent frames is yours to build.
12. `fetch` with `ReadableStream` lifts the GET and header limits, at the cost of owning framing, dispatch and reconnection yourself.
13. Most `fetch` implementations quietly skip reconnection, which is how a stream never comes back after a tunnel drop.

> **Recall:** Name two things `EventSource` cannot do and what each forces. · What exactly arrives on reconnect and what is the server obliged to do with it? · What does a team lose the moment it moves to `fetch`?
>
> **Stop:** No `EventSource` polyfill, no spec-level state machine.

---

## Note 4 · Streams Die In The Middle

16 rungs. **Break:** put nginx in front with defaults and let the stream idle for 90 seconds.

1. The assumption to break: an open TCP connection stays open until someone closes it.
2. **Break it** — leave a stream idle behind nginx and it dies on its own.
3. Every box in the path — carrier NAT, corporate proxy, load balancer, nginx — holds a table entry for the connection.
4. Those tables are finite, so each box deletes entries after N seconds with no bytes.
5. When it does, it usually **tells neither end**.
6. So both ends still believe the connection is open while the middle has no route for it.
7. The server writes into a socket going nowhere, the user watches a spinner, and **no error is raised anywhere** — this is a zombie connection.
8. The fix is therefore to push bytes through often enough that no box ever calls the connection idle.
9. A comment frame is bytes carrying no meaning, which is exactly the right shape for that.
10. The interval does not come from a standard — it comes from the **smallest idle timeout in your path**.
11. AWS ALB defaults to 60s, nginx `proxy_read_timeout` to 60s, mobile carrier NAT is often considerably less.
12. OS-level TCP keepalive is a **different mechanism** and does not solve this — it defaults to 7200 seconds.
13. And some NATs do not count its empty probes as traffic at all, so even tuned it may not refresh the entry.
14. FastAPI's `EventSourceResponse` already pings every **15 seconds**, which clears every common timeout — so the work is checking the proxy config, not building heartbeats.
15. Separately, nginx **buffers upstream responses by default**, collecting frames and forwarding them together.
16. **Break it** — the whole answer arrives in one lump at the end, works perfectly in development because there is no proxy, and nothing about the symptom points at nginx. `X-Accel-Buffering: no` or `proxy_buffering off`.

> **Recall:** Why does a reclaimed NAT entry produce no error on either end? · What must the ping interval be smaller than, and how would you find that number? · Why does proxy buffering never reproduce locally?
>
> **Stop:** **Rabbit hole.** No TCP congestion control, window scaling, or NAT implementation. That boxes hold finite state and reclaim it is the whole usable insight.

---

## Note 5 · Streaming From The Server

12 rungs. **Break:** close the tab mid-stream and check whether the generator is still calling the model.

1. The endpoint is a generator that yields frames.
2. The framework writes each yielded frame to the socket.
3. If the client reads more slowly than you produce, that write blocks.
4. A blocked write suspends the coroutine.
5. So production slows to match consumption on its own — **backpressure is free**.
6. **Break it** — put an unbounded queue between the producer and the socket.
7. Now the producer never blocks, and memory grows without limit: an unbounded queue is a memory leak with good manners.
8. Close the browser tab mid-stream.
9. The generator keeps running, because nothing told it otherwise.
10. With an LLM behind it, that means still calling the model.
11. On per-token pricing that is not wasted CPU — it is **a line on an invoice** for output nobody will read.
12. So the generator has to check for disconnection rather than assume it will be stopped.

> **Recall:** Why is backpressure usually free, and which single design choice destroys it? · What is still running after the tab closes, and what does it cost?
>
> **Stop:** No asyncio scheduling internals. Delivery mechanics belong to `00-Python-Utils/08-Async` concept 16.

---

## Note 6 · Cancellation And Cost

12 rungs. **Break:** cancel a stream that writes usage data, then look for idle transactions.

1. Passive cancellation is the client vanishing — detect it and stop.
2. Explicit cancellation is a stop button, which is a different problem.
3. The stream is one-directional, so **it cannot carry a message back upstream**.
4. So stopping needs a separate endpoint.
5. Keyed by a stream id, which means the client must have been given one.
6. When a run is cancelled you **still owe the token count** — those tokens were already spent.
7. So a usage write has to happen after cancellation, not before it.
8. **Break it** — do that write on the request-scoped session.
9. The session dies with the cancelled request, mid-transaction.
10. Leaving a transaction idle while holding row locks, which surfaces later as unrelated queries hanging.
11. The fix is a **fresh session**, plus `asyncio.shield` around the write.
12. Shield is what makes the write survive the very cancellation that triggered it.

> **Recall:** Why can a stop button not be sent over the stream? · What is still owed after a cancellation, and why? · What exactly goes wrong with a request-scoped session here?

---

## Note 7 · Errors And Limits

14 rungs. **Break:** raise an exception after two frames have already been sent, then open seven tabs.

1. `200 OK` and the headers go out **before** the first frame.
2. Once sent, the status code is committed.
3. **Break it** — raise halfway through generation and discover you cannot return a 500.
4. Option A is an error event frame the client is built to understand.
5. Option B is closing the connection.
6. But a closed connection is **indistinguishable from a network drop**.
7. So without a convention the client either shows an error on success or hides a real failure.
8. Which is why an explicit terminal frame exists — it is the only way to distinguish finished from dropped.
9. Separately, HTTP/1.1 allows **six connections per domain** per browser.
10. An open SSE stream occupies one for its entire life.
11. **Break it** — seven tabs, and the seventh hangs with no error at all.
12. HTTP/2 multiplexes over one connection, raising the practical ceiling to around 100.
13. Which is why this bug is now rare, and far more confusing when it appears, since it depends on the negotiated protocol.
14. Related, in your own process: an in-process stream counter caps **per worker, not per user**, so two workers silently double the limit and ten make it meaningless.

> **Recall:** Why can a mid-stream failure not be a 500? · What are the two ways to signal it and what is wrong with each? · Why does the connection cap produce a hang rather than an error?
>
> **Stop:** **Rabbit hole.** No HTTP/2 frame types, HPACK, or stream prioritisation. That multiplexing removes the per-domain cap is the entire relevant fact.

---

## Note 8 · Resumption

13 rungs. **No break — this note is worked as a design problem.** It is also the one that appears in interviews.

1. The default shape is a single POST that both submits the message and streams the answer.
2. So the work's lifetime is tied to the connection's lifetime.
3. **Break it** — drop the connection and the entire turn is lost, including work already done.
4. Splitting them: POST the message, receive a **stream id**, then GET the stream.
5. Now the work continues server-side regardless of the connection.
6. And a reconnect can **rejoin a run already in flight** rather than starting over.
7. To honour `Last-Event-ID` you need the frames you already sent.
8. That is a replay buffer — transient storage, plus a retention window you have to choose.
9. A system that **already checkpoints its state** has a second option available.
10. Re-derive the answer from that state instead of replaying frames.
11. The trade is faithfulness against storage: replay shows exactly what the client saw, checkpoint shows the same answer possibly rendered differently.
12. Either way **mid-flight progress events are gone**, because they were never part of the state.
13. And the split creates a new attack surface: a stream id is guessable, so something must stop user A consuming user B's stream.

> **Design questions — take a position, then defend it against the change:**
> Choose replay or checkpoint for a chat agent and justify it. **Now the agent runs 45 seconds and emits 200 progress events — does the answer change?** · Where does the stream id come from, and what stops A reading B's stream? · How long is the buffer retained, and what happens to a client that reconnects after it expired? · The client reconnects while the model is still generating — rejoin live, or start over?
>
> **Stop:** **Do not implement resumption in v1.** This is the scope trap — it drags in storage design, retention policy and the POST/GET split, and it is the most likely reason this work overruns.

---

## Note 9 · Streaming Structured Output

21 rungs. **Break:** run a JSON parser on a single delta and watch it fail on every one of them.

1. Text streams naturally because half a sentence is still worth showing — a partially rendered word is fine.
2. A tool call is not text. It is JSON, and half a JSON object is not valid JSON.
3. `{"location": "Ban` cannot be parsed by anything, ever, no matter how lenient.
4. So the ordinary parser cannot run per delta, which is what makes this different from streaming an answer.
5. Providers therefore send tool arguments as a **stream of string fragments**, not as objects.
6. Anthropic names this explicitly — a delta of type `input_json_delta` carrying a `partial_json` field.
7. The fragments are concatenated in arrival order to rebuild the argument string.
8. And they **do not respect JSON boundaries** — a fragment can end mid-key, mid-value, or mid-string.
9. So the only safe rule is to buffer everything and parse once, at the end.
10. Which requires a signal for the end — `content_block_stop`, a separate event from the deltas themselves.
11. One response can contain **several tool calls**, and their deltas are interleaved rather than sequential.
12. So a single buffer is wrong. It would concatenate fragments from different calls into one corrupt string.
13. Every delta therefore carries an **index**, the position of the content block it belongs to, and buffering is per index.
14. The failure when this is missed is not an error — it is arguments from two different tool calls silently merged.
15. OpenAI-compatible responses split along a different seam: the call's `id` and its `function.name` can arrive in **separate chunks**.
16. So accumulating arguments is not sufficient — the identity of the call is itself assembled over time.
17. This is a real and repeated production bug, not a hypothetical, with issues filed against multiple agent frameworks.
18. Showing structured output as it arrives — a form filling in field by field — needs a **lenient parser** that tolerates an unterminated object.
19. Which forces a product decision about what half an object means: render what exists, or wait for the whole thing.
20. Schema **validation is end-only**. Validating a partial object is meaningless, because absent fields are indistinguishable from not-yet-arrived fields.
21. And a partially streamed tool call must not execute twice on a retry, which makes idempotency a streaming concern rather than only a networking one.

> **Recall:** Why can a lenient parser not rescue you from parsing per delta? · What does `index` prevent, and what is the symptom when it is ignored? · Why is validating a partial object meaningless rather than merely premature?
>
> **Stop:** Do not learn every provider's event vocabulary. Two shapes — fragments plus a terminator, and an index for interleaving — cover all of them.

---

## Coverage

Nothing written yet. Note files are numbered to match this list — note 4 becomes `04-Streams-Die-In-The-Middle.md`.

| Note | Rungs | Written |
|---|---|---|
| 1 · Why Stream At All | 11 | — |
| 2 · The Wire Format | 13 | — |
| 3 · The Browser Client | 12 | — |
| 4 · Streams Die In The Middle | 16 | — |
| 5 · Streaming From The Server | 12 | — |
| 6 · Cancellation And Cost | 12 | — |
| 7 · Errors And Limits | 14 | — |
| 8 · Resumption | 13 | — |
| 9 · Streaming Structured Output | 21 | — |

---

## Deferred

| Topic | Goes to |
|---|---|
| Async generators, `async for`, `StopAsyncIteration` | `00-Python-Utils/04-Generators-And-Iterators` |
| Cancellation delivery, `CancelledError`, `asyncio.shield` mechanics | `00-Python-Utils/08-Async` concept 16 |
| Rate limiting, quota windows, token accounting | `05-Cost-And-Latency` |
| Tracing a streamed agent run, span boundaries | `02-Observability` |
| WebSocket, WebRTC, audio frames | outside this vault |

---

## Where this shows up in Xarvis

`src/xarvis/streaming/` builds every frame in one place, with typed Pydantic events carrying `Literal` discriminators. **Note 7 rung 8 is already solved there** — `done_event()` exists precisely so a client can tell finished from dropped, and its docstring says so.

What is missing maps onto specific rungs rather than vaguely: **no `id:` or `retry:`** (note 2 rungs 11–13, note 3 rungs 10–11), **`active_stream.py` counts per process** (note 7 rung 14), and **client disconnect is undetected** (note 5 rungs 8–12), which on a per-token API is rung 11's invoice. Note 4 is settled — the 15-second default ping clears every common timeout; what remains is recording what the proxy is actually configured to.

---

## Interview hooks

The three that recur: **why SSE and not WebSocket** (note 1, and the answer is direction plus infrastructure, not speed) · **how do you resume a stream that dropped mid-answer** (note 8, which separates people who have shipped it) · **how do you stop generating when the user closes the tab** (note 5, and the follow-up is always cost).

The one that catches people who only read: **what happens to an error thrown halfway through a stream** (note 7 rungs 1–8). There is no good answer, and knowing there is no good answer is the answer.

---

## Sources to verify against

- [MDN — Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) and the `EventSource` reference
- [WHATWG HTML Living Standard — Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html), the authoritative text
- [FastAPI — Server-Sent Events](https://fastapi.tiangolo.com/tutorial/server-sent-events/), native since 0.135.0
- [AI token streaming isn't about SSE vs WebSockets](https://zknill.io/posts/ai-token-streaming-isnt-about-sse-vs-websockets/) — the submission/consumption split
