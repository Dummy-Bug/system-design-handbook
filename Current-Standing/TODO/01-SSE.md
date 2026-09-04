# 01 — SSE

Item 1 of Table 1 in [[../10-Xarvis-Build-Plan]] · est. 40–60h · researched 2026-09-03

> [!abstract] The goal
> Not to ship SSE — Xarvis already streams. The goal is to **understand** it well enough to design it deliberately, because every LLM product streams this way and I want to answer, without notes, why SSE over WebSocket, how resumption works, what kills a stream in production, and how to stop burning tokens for a client that already left.
>
> Order matters: spec, then a toy, then break the toy, then read real code, then design. Reading other codebases first is how you copy shapes without knowing why they are there.

---

## The stack I am already on

`sse_events.py` imports `from fastapi.sse import ServerSentEvent`. That is **FastAPI's native SSE module, added in 0.135.0 in March 2026** — not the older `sse-starlette` package everyone still blogs about. Worth knowing, because most tutorials found by search are written against the old library.

What the native module gives for free:

- `EventSourceResponse` — event-stream framing, the `Content-Type` header, and **keep-alive pings**
- `ServerSentEvent` — supports `event`, `id`, `retry` and `comment` fields

> [!important] This changes the gap list from what I first assumed
> Heartbeat is probably **not** something I need to build — `EventSourceResponse` already sends keep-alive pings. The real question is **what the default ping interval is and whether it beats the proxy in front of me** (see step 3).
>
> Likewise `id:` and `retry:` are already supported by `ServerSentEvent`. I am simply not passing them. That is a decision I never made, rather than a feature I lack.

- [ ] Read the FastAPI SSE docs — https://fastapi.tiangolo.com/tutorial/server-sent-events/
- [x] Find the default ping interval in `EventSourceResponse` — **15 seconds, a float**
- [ ] Skim PR #15030 on the FastAPI repo, which added it — the discussion explains the design choices

---

## Step 1 — Read the spec, not a tutorial

- [ ] MDN, **Using server-sent events** — https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
- [ ] MDN, **EventSource** — the client half of the contract
- [ ] WHATWG HTML Living Standard, **Server-sent events** — the authoritative text

The entire wire format is four fields:

```
event: progress
data: {"message":"Looking up..."}
id: 42
retry: 3000

```

- [ ] Afterwards, from memory, write down what each of the four does
- [ ] Note the two rules that catch everyone: a frame ends with a **blank line**, and a line starting with `:` is a comment clients ignore — which is exactly how heartbeats are sent

Est. 30 minutes.

---

## Step 2 — Build the smallest possible thing

- [ ] A FastAPI endpoint yielding three events, then stopping
- [ ] Hit it with **`curl -N`**, not a client library — the raw bytes are the point

```
curl -N http://localhost:8000/stream
```

- [ ] Watch for the keep-alive comment frames appearing on their own, and time the gap between them

Est. 30 minutes.

---

## Step 3 — Break it, one thing at a time

Each break makes exactly one feature necessary. Nothing gets added because a tutorial said so.

- [ ] **Kill the server mid-stream.** The browser reconnects on its own, unprompted.
  → why **`retry:`** exists, and why reconnection is the client's job

- [ ] **Add `id:` to every frame, then kill it again.** The reconnect arrives carrying **`Last-Event-ID`**.
  → this is resumption, and its real cost is a **replay buffer** I do not have

- [ ] **Idle the stream for 90 seconds behind nginx.** Watch it die.
  → FastAPI's 15s ping should already prevent this. If it does, the lesson is about **interval choice against the proxy**, not about building heartbeats

- [ ] **Close the browser tab mid-stream.** Does the server notice? Does the model call stop?
  → the one that costs money, and it connects straight to token metering

- [ ] **Bonus:** put nginx in front without `X-Accel-Buffering: no` and watch streaming silently stop being streaming

> [!important] Heartbeat: FastAPI's 15s default is fine, and the number that matters is not 25
> An earlier version of this file said there is a ~25 second TCP keepalive ceiling. That was one bug report's environment stated as if it were a law, and it is wrong. **There is no universal ceiling.**
>
> What is actually true: an idle TCP connection is not kept alive by anyone. Every box between browser and server — carrier NAT, corporate proxy, load balancer, nginx — holds a finite table entry for the connection and deletes it after N seconds of no bytes. **When it does, it usually tells nobody**, so both ends still believe the connection is open while the middle has no route. The server writes into a socket going nowhere and the user watches a spinner forever, with no error anywhere.
>
> The real timeouts vary by environment: AWS ALB defaults to 60s, nginx `proxy_read_timeout` to 60s, mobile carrier NAT is often aggressive at 30s or less, corporate proxies are anything at all. **OS-level TCP keepalive is a different mechanism and useless here** — it defaults to 7200 seconds, and some NATs do not even count its empty probes as traffic. The SSE `: ping` comment is application data, so it resets every timer along the whole path. That is why the application-level heartbeat is the one that matters.
>
> **FastAPI's `EventSourceResponse` default is 15 seconds, which clears every common timeout comfortably.** The number to actually check is `proxy_read_timeout` on the nginx in front of Xarvis and the idle timeout on the load balancer if there is one — the ping must sit well under the smallest of those.
>
> This matters most in exactly the window Xarvis lives in — **the agent is thinking and calling tools, so no tokens are flowing yet.** That silent stretch is when connections die, and it is the stretch a chat UI can least afford to lose.

Est. 2 hours, and the highest-value 2 hours in this item.

---

## Step 4 — Read real implementations, with questions

Only now, and never as browsing.

- [ ] **Mine first** — `src/xarvis/streaming/sse_events.py` and the `SSE.md` I already wrote, read **against the spec**. Every place the spec offers something I did not use becomes the gap section of the design doc.
- [ ] **OpenAI** streaming chunk format — delta shape, and how completion is signalled
- [ ] **Anthropic** streaming — event types, and where it diverges from OpenAI
- [ ] **Vercel AI SDK** — the most-copied client implementation, and what it does about reconnection

Hold these questions while reading rather than reading generally:

- How is completion distinguished from a dropped connection?
- Is `id:` used at all — and if not, what did they decide instead?
- What happens to an error raised after `200 OK` has already gone out?
- Who owns cancellation: client, server, or both?

---

## Step 5 — Write the design doc

Ten decisions. Each should read as **I saw this break, here is what I am doing about it**.

- [ ] **1 · Event taxonomy** — which types exist, what each carries, who consumes them
- [ ] **2 · Frame contract** — `event:`, `data:`, `id:`, `retry:`, and what stays duplicated inside `data` for older clients
- [ ] **3 · Resumption** — id scheme, `Last-Event-ID`, and **replay buffer versus resume from checkpoint**
- [ ] **4 · Heartbeat** — accept FastAPI's 15s default, and record what `proxy_read_timeout` and the load-balancer idle timeout actually are, so a change to either does not silently break streaming
- [ ] **5 · Termination** — the done frame, and error signalling after `200 OK`
- [ ] **6 · Concurrency limiting** — where the counter lives once there is more than one worker
- [ ] **7 · Cancellation** — both halves: passive disconnect detection **and** an explicit stop endpoint
- [ ] **8 · Backpressure** — when the client reads slower than the model produces
- [ ] **9 · Client contract** — what the frontend must implement for any of this to work
- [ ] **10 · Deployment** — `X-Accel-Buffering`, load-balancer idle timeouts, keepalive

### Decision 3, and the architecture that goes with it

The production pattern for resumable streams is to **separate the prompt request from the response stream**: POST the message and get back a stream id, then GET the stream to consume it, with a token store behind it so a reconnect can replay.

Xarvis does not do this — a single POST both submits and streams, which is why a dropped connection loses the turn.

Two candidate answers, and the reasoning is worth more than the code:

- **Replay buffer** — faithful to exactly what the client already saw, but it means storing transient frames and choosing a retention window
- **Resume from checkpoint** — no new storage, since the checkpointer already holds per-thread state, but the client may see a different rendering of the same turn and mid-flight progress events are gone

### Decision 7, and the bug waiting inside it

> [!warning] Cancellation will break the token metering work if I am not deliberate
> A documented anti-pattern: **database writes on a request-scoped session during cancellation** leave transactions idle while holding row locks, because the session dies with the cancelled request.
>
> This lands directly on item 3 of the build plan. When a client cancels mid-stream I **still owe the token count** — those tokens were spent. So the usage write has to happen on a **fresh session**, wrapped in **`asyncio.shield`**, so it completes even though the caller was cancelled.
>
> Getting this wrong means either lost billing data or locked rows. Getting it right is a genuinely good interview story, because it sits exactly where streaming, cancellation and persistence meet.

Cancellation also has two halves, and most implementations only do one:

- **passive** — the client vanished, detect it and stop the model call
- **explicit** — a stop button, which means a cancel endpoint keyed by stream id

---

## Then, and only then, build

- [ ] Write tests against the **current** behaviour first — frame builders are pure functions, so this is the pytest entry point and a safety net for the rewrite
- [ ] Cut the branch, implement against the design doc
- [ ] Port forward the lessons already in the old code rather than discarding them:
  - the done frame exists so a client can tell **finished** from **dropped**
  - Gemini emits tool calls with empty content, so progress text is synthesised from the tool name
  - `type` is duplicated inside `data` for older clients, with documented removal criteria

> [!warning] Decide scope before starting, not halfway
> **Resumption is the part that expands**, because it drags in storage design and possibly the POST-then-GET split. Everything else here is a few days. Resumption alone can be a week.

---

## Definition of done

- [ ] Design doc written, all ten decisions recorded and reasoned
- [ ] Tests exist and pass over frame construction
- [ ] The four break experiments run personally, not read about
- [ ] I can answer out loud, without notes: why SSE over WebSocket, how resumption works, what kills a stream in production, and how to stop paying for a client that left

---

## Sources

- FastAPI, [Server-Sent Events tutorial](https://fastapi.tiangolo.com/tutorial/server-sent-events/) — native support since 0.135.0
- MDN, [Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
- [AI token streaming isn't about SSE vs WebSockets](https://zknill.io/posts/ai-token-streaming-isnt-about-sse-vs-websockets/) — the prompt/stream split and token store
- [Streaming AI Responses: SSE, WebSockets, TTFT, Backpressure](https://www.callmissed.com/en/blog/streaming-ai-best-practices)
- [Streaming Patterns in 2026 — SSE, WebSocket, gRPC, HTTP Streaming](https://blog.rajpoot.dev/posts/backend/streaming-patterns-2026/)
