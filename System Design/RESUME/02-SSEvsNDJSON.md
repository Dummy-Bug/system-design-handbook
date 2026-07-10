# SSE vs NDJSON — Streaming Server→Client Events

When a server needs to push a live feed of events to a client — e.g. an AI agent showing "Understanding your query…" → "Looking up record…" → the final answer — two common transports are **SSE** and **NDJSON** over a long-lived HTTP response. This note builds both fully, then compares, using a generic streaming AI-agent as the example.

---

## The shared foundation: HTTP streaming ("a response that never ends")

Normal HTTP: request → full response → **connection closes**. Once closed, the server can't reach the client again.

Streaming trick: the server sends the headers, starts the body, and **keeps the body open** — dribbling out chunks over time and never sending the "done" signal. The client reads each chunk the instant it arrives. This is **not** SSE-specific — it's plain HTTP streaming, and **both SSE and NDJSON sit on top of it** (both are a streaming HTTP response). The only thing that differs between them is the **frame** — how you mark where one event ends and the next begins.

---

## SSE (Server-Sent Events) — full build

### 1. Wire format

An SSE event is one or more `field: value` lines, terminated by a **blank line** (`\n\n`). Only `data:` is required.

```
event: progress                              ← optional: a NAME for this event
data: {"message":"Understanding your query..."}   ← the payload
id: 42                                        ← optional: sequence id (the resume hook)
retry: 5000                                   ← optional: reconnect delay in ms
                                              ← BLANK LINE = event boundary
```

"Blank line ends it" literally means **two newlines in a row** (`\n\n` = hex `0a 0a`). See it with `cat -e` (a lone `$` line) or `curl -N` on a live stream. **One connection carries many events**, each separated by a blank line.

**SSE is text-only by spec** — content type is literally `text/event-stream`. Binary must be base64'd into text (~33% inflation).

### 2. The client — `EventSource`

The browser's built-in SSE client. You give it a URL; it (a) opens the connection, (b) buffers bytes and splits on the blank line, (c) fires a JS handler **per `event:` name**:

```js
const stream = new EventSource("/stream");   // GET only, no body
stream.addEventListener("progress", e => showSpinner(JSON.parse(e.data)));
stream.addEventListener("terminal_response", e => render(JSON.parse(e.data)));
```

**Critical constraint: `EventSource` is GET-only and cannot send a request body.** (The SSE *format* works over POST — a server can emit `text/event-stream` from a POST route — but the *browser client* can't call a POST. To consume SSE over POST you must hand-roll a fetch-based SSE parser, i.e. you lose the "free" client.)

### 3. The marquee feature — auto-reconnect + `Last-Event-ID`

Long connections drop (wifi, mobile handover, proxy timeout). `EventSource` handles it **automatically**:

```
connection drops after event #40
  → EventSource waits (retry: ms)
  → reopens connection, auto-sends header  Last-Event-ID: 40
  → server reads header, resumes from #41
  → client never noticed the gap
```

The `id:` field is the bookmark; `Last-Event-ID` is the resume request; `retry:` sets the backoff. **You write zero code for this** — it's the main thing SSE gives you for free. NDJSON gives you none of it.

---

## NDJSON (Newline-Delimited JSON) — full build

### 1. Wire format

Same held-open transport as SSE. The frame is as simple as it gets: **one JSON object per line, `\n` ends it.**

```
{"type":"progress","content":{"message":"Understanding your query..."}}
{"type":"progress","content":{"message":"Looking up record 123..."}}
{"type":"terminal_response","content":{"status":"SUCCESS",...}}
```

There are no `event:`/`id:`/`retry:` fields — if you want an event type, you put it **inside** the JSON (`"type":"progress"`). The server side is a single line per event:

```python
yield json.dumps(event) + "\n"      # the "+ \n" is the delimiter — that IS NDJSON
```

Also text-only (JSON is text).

### 2. The client — `fetch` + a reader loop (you write it yourself)

No built-in client. You re-implement what `EventSource` did:

```js
const res = await fetch("/chat", {
  method: "POST",                                  // ← the whole reason: POST + body
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ type: "message", text: userInput }),
});
const reader = res.body.getReader();
const decoder = new TextDecoder();
let buffer = "";
while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });   // bytes → text, append
  let nl;
  while ((nl = buffer.indexOf("\n")) !== -1) {          // carve out COMPLETE lines
    const line = buffer.slice(0, nl);
    buffer = buffer.slice(nl + 1);
    if (line.trim()) handleEvent(JSON.parse(line));     // route by event.type
  }
}
```

**The `buffer` is the subtle part** (and what an interviewer would probe): TCP hands you bytes in arbitrary chunks that don't respect your `\n` boundaries — one `read()` can give half an event or two-and-a-half. So you accumulate into a buffer and only slice off complete lines, keeping the partial remainder for the next chunk. `EventSource` does this internally for SSE; with NDJSON you do it (~15 lines).

---

## Frame comparison (same events, both formats)

| | SSE | NDJSON |
|---|---|---|
| Event boundary | blank line (`\n\n`) | single newline (`\n`) |
| Event type | `event:` field (out-of-band) | a key inside the JSON (`"type"`) |
| Lines per event | 2+ (`event:`, `data:`, …) | 1 |
| Content | text only | text only (JSON) |
| Built-in named fields | `event` / `id` / `retry` | none — all inside the JSON |
| Byte size | ~equal (framing overhead ≈ in-payload keys) | ~equal |
| Browser client | `EventSource` (built-in, **GET only**) | `fetch` + reader (you write ~15 lines) |
| Auto-reconnect + replay | ✅ free (`Last-Event-ID`) | ❌ none |

**Never pick between them on byte size — it's a wash.**

---

## Why choose NDJSON over SSE — the reasoning chain

For a streaming AI-agent endpoint that is a **POST**:

1. **The endpoint is a POST with a body** (the user message, or a HITL selection payload). The browser's native `EventSource` is **GET-only**, so it was never available.
2. **Yes, SSE works over POST** on the server — but only a **hand-rolled fetch SSE client** can consume it; you lose `EventSource`'s free benefits. So **you're on a fetch-based client either way.**
3. **Once you're on fetch regardless, SSE's frame buys nothing you need.** Events are already JSON, so NDJSON's split-on-`\n` is **simpler to parse** than SSE's multi-field `data:`/`event:`/`id:` frames.
4. **You don't need SSE's `Last-Event-ID` resume** — if the agent framework already persists graph/conversation **state** durably (checkpointing keyed by thread/session), recovery lives at a **better layer**. A dropped connection resumes from the persisted checkpoint (and mutating side effects are protected by idempotency keys), not by replaying a byte stream. SSE's replay recovers *transport frames* (ephemeral progress narration); the checkpoint recovers the *work*.

**What you give up (name it — it reads as senior):** SSE's built-in auto-reconnect + `Last-Event-ID` replay. For a single agent turn, a dropped connection just re-runs / resumes from the checkpoint, so that machinery isn't worth the extra client parsing.

---

## The proxy gotcha — NDJSON's one real weak spot

Between your server and the browser there's usually a **proxy** (commonly **Nginx**) that all traffic passes through. It can mess up a live stream in three ways, and a streaming-via-FastAPI-SSE response fixes all three *automatically* while a plain NDJSON `StreamingResponse` does **not** — you set them yourself. This is the one honest edge SSE has here.

1. **Proxy buffering → `X-Accel-Buffering: no` (the important one).** By default Nginx *buffers* a response — collects it into a batch before forwarding, which is efficient for a normal page but disastrous for a stream. It holds your events until the buffer fills or the response ends, so the user sees **nothing, then all progress events dump at once at the end** instead of live. The header `X-Accel-Buffering: no` tells Nginx "don't buffer this — forward every chunk instantly." *(Analogy: a mail forwarder who boxes up your letters and only mails the box when it's full, instead of forwarding each letter as it arrives.)*
2. **Idle-connection kill → keep-alive pings.** Some proxies close a connection that's been silent too long (e.g. 60s). If the agent thinks for a while and sends nothing, the connection can get cut mid-turn. The fix: send a tiny "ping" every ~15s so the proxy sees the connection is alive.
3. **Caching → `Cache-Control: no-cache`.** You never want a live, unique stream cached and replayed. This header says "always go live, don't save a copy." (Minor, but standard hygiene.)

**FastAPI's `EventSourceResponse` (SSE) sets all three for free. With NDJSON `StreamingResponse` you must set them manually** — especially #1. If you forget `X-Accel-Buffering: no` and an Nginx sits in front, your live progress feed arrives as one clump at the end. **Interview-honest framing:** "The one thing SSE gives me for free that NDJSON doesn't is proxy-friendliness — keep-alive pings and the anti-buffering header — so on the NDJSON path I set `X-Accel-Buffering: no` and `Cache-Control: no-cache` on the response myself."

---

## Backend scope note

For a backend interview, **you will NOT be asked to write the `fetch` reader, `TextDecoder`, or `EventSource` API details** — that's frontend plumbing, below the design-round altitude. What you MUST own:

- **Why the format choice** (one sentence): EventSource is GET-only, the endpoint is POST, so we stream NDJSON over fetch.
- **How it's consumed, conceptually** (one sentence): The client reads the response stream and splits on newlines, parsing one JSON event per line.

The wire format, the `type` field, the terminal/error events — that's an **API contract you designed**, which *is* backend work. Knowing how the client eats it is just knowing your own contract's other end.

---

## What actually gets streamed (structured events, not tokens)

Worth knowing the distinction: streaming **LLM tokens** (the ChatGPT typewriter effect) is different from streaming **structured events**. A common agent design streams *node-level updates* rather than tokens — the stream is a sequence of discrete, structured events:

- **Progress events** as the agent works ("Understanding your query…", "Looking up record…"), often emitted directly by graph nodes.
- An **interaction-required event** when the agent needs human input (HITL).
- A **terminal event** carrying the final answer (or a structured error).

Each is one JSON object per line (NDJSON). This is what **streamed structured events** means, as opposed to a raw token stream — and it's often the better choice because the frontend can render tool-in-progress states and HITL prompts, not just a typewriter blur.

---

## Token streaming vs structured events — when can you even stream tokens?

Three distinct things get conflated. Know the difference:

1. **Real (server-side) token streaming** — the server forwards each LLM token *as it's generated*. First words appear almost immediately (low *time-to-first-token*). This is the ChatGPT typewriter effect.
2. **Structured event streaming** — the server emits discrete structured events (progress → terminal); the final answer arrives as **one complete event**.
3. **Frontend-simulated typing** — the client receives the whole final answer in one event, then **animates it character-by-character locally**. Purely cosmetic: the user still waited for the *full* response to finish generating, so there is **no** time-to-first-token benefit. It just makes an already-arrived answer feel alive. (Progress events during the wait are what keep it from being dead air.)

### How token streaming actually works

An LLM is **autoregressive** — it generates one token at a time (each token feeds back in to produce the next). So the response is *always* built incrementally; the model never "has it all at once." Whether you *receive* the tokens incrementally is a call-site choice:

- `ainvoke(...)` — wait until every token is generated, return the full response.
- `astream(...)` — forward each token as the model emits it.

(Under the hood the model providers stream tokens to your server over **SSE** — `ainvoke` just quietly consumes that whole stream for you.) Real streaming looks like:

```python
async for chunk in llm.astream(window):
    yield json.dumps({"type": "token", "delta": chunk.content}) + "\n"
```

### The principle: when is token streaming even applicable?

> Token streaming is only safe when the LLM call is **guaranteed to be talking directly to the user** — its raw output IS, verbatim, what gets displayed.

Two common architectures break that guarantee. When they're present, you should **not** token-stream:

- **Structured output** — the LLM returns a structured object (intent, routing decision, entities, or a `message_to_user` field to be extracted). That's *data for the program*, not prose for the user. Streaming its raw tokens streams half-built JSON.
- **Tool calling** — a single call may come back as either a reply *or* a tool call (e.g. `ADD_USER(id=…)`), and **you don't know which until you parse the finished output.** You can't blindly stream tokens as the user's answer when half the time they're a function call.

That uncertainty is the crux: streaming commits you to *"these tokens are the user's answer"* **before** you know that's true. Only a call whose role is fixed as "compose the free-text reply" — a dedicated **responder node** — can make that promise.

This is why real agent UIs show **structured progress events** ("Searching…", "Looking up record…") during the reasoning/tool steps, and reserve **token streaming for the single final "write the answer" step.** Plain ChatGPT streams tokens because in a bare chat the model's output *is* the reply; add routing + tool-calling and most calls stop being replies, so you fall back to structured events + (optionally) one streamed final step.

**Interview line:** "We stream structured events, not tokens, because our LLM calls use structured output and tool-calling — the model's output is routing data or a tool call, not user-facing prose. Token streaming only makes sense for a call guaranteed to talk to the user, which would need a dedicated free-text responder step. Structured progress events also let the UI show tool-in-progress states."

---

## How to answer in interview

**"Why NDJSON over SSE?" — the full speakable answer (deploy incrementally, don't dump):**

> "The stream endpoint is a POST — the user message is in the body — and the browser's native EventSource is GET-only, so standard SSE was out. And yes, a server can emit SSE over POST, but only a hand-rolled fetch client can consume it, so we're off EventSource either way. Once we're on a fetch-based reader regardless, NDJSON's newline framing is simpler than parsing SSE frames, and our events are already JSON. We gave up SSE's Last-Event-ID replay, but we recover agent state through checkpointing, not the transport — so a dropped turn resumes from the checkpoint. For a single turn that's enough."

**That answer wins because it names the tradeoff you made** — the #1 signal of a senior engineer.

## Follow-up / pushback questions

### Pushback 1 — "You can hand-roll SSE over fetch too."

Concede it — SSE isn't tied to `EventSource`; you *can* parse SSE frames yourself over fetch. Then show why it's still worse **for a JSON payload**, and the point is dead simple: **SSE wraps every message in a `data:` label; NDJSON doesn't.**

Same event, on the wire:

```
SSE:     data: {"delta":"Hello"}
NDJSON:  {"delta":"Hello"}
```

With SSE your client must **strip the `data:` wrapper** off every line before it can read the JSON — plus handle the blank-line boundary, multi-line `data:` fields, and comment lines. With NDJSON there's no wrapper: split on `\n`, `JSON.parse`, done. When the payload is already JSON, SSE's frame is a wrapper you peel off *only to find the JSON you were always going to parse.*

And that wrapper only **earns its keep** when a built-in client (`EventSource`) parses it and handles reconnect *for free*. Over hand-rolled fetch you get none of that for free — so you'd pay the wrapper cost **without** the reward.

Also worth conceding cleanly: over POST both formats are on fetch, so the capability difference **mostly cancels out** (SSE loses EventSource's free client; NDJSON loses SSE's free proxy headers). Given that wash, client simplicity is the tie-breaker.

**Interview line:** "Sure, SSE works over fetch — but SSE wraps every message in a `data:` label I'd have to strip before reading the JSON inside, and reconnect I'd hand-build anyway since EventSource is off the table over POST. NDJSON drops the wrapper: the line *is* the JSON. Over POST the two mostly cancel out, so I picked the simpler client — I owned the frontend too and deliberately minimized client-side complexity."

### Pushback 2 — "What about reconnection?"

Why they ask: you gave up SSE's free auto-reconnect + `Last-Event-ID` replay, so they poke the hole — *"connections drop; how do you recover the in-flight turn?"*

**Two layers of recovery — keep them separate:**
- **Transport recovery** (what `Last-Event-ID` does): re-send the *events the client missed* while disconnected. Recovers the **stream of messages**.
- **State recovery** (what checkpointing does): the agent's actual *work/state* is persisted durably as it goes; on return you resume from the saved state. Recovers the **work itself**, independent of the transport.

**The trap to avoid — don't over-claim.** It's tempting to say "checkpointing makes reconnection a non-issue." It doesn't, fully: checkpointing preserves the *history*, but a raw disconnect isn't a clean HITL interrupt, so re-asking **re-runs the turn** (another LLM call + latency; side effects are protected by idempotency keys so nothing double-executes). Be honest that you re-execute.

**Why SSE wouldn't have saved you for free.** `Last-Event-ID` seamless resume needs a **server-side event buffer**: keep the turn running after the client vanished, buffer every event keyed by id, and replay from the last-seen id on reconnect. `EventSource` gives only the **client** half for free (auto-reconnect + sending the header) — the server buffer you build yourself (that's the manual `if i < start: continue` you see in replay examples). Worse: if your server *cancels* the in-flight work on disconnect (a common and reasonable default), there's **nothing to replay** — you'd have to *stop cancelling* AND build the buffer. That's the same server-side work in either format, so SSE doesn't hand you seamless resume; it hands you the client trigger for a buffer you still have to build.

**The YAGNI verdict (attach the trigger — this is what reads as senior).** Skipping resumable streaming is a deliberate call, not laziness, *as long as you name the condition that would flip it.* "I didn't build it, it's complex" = junior. "No requirement needed it yet, and here's what would make me build it" = senior.

**Interview line:**

> "I deliberately didn't build resumable streaming — the server-side event buffer and replay — because for a single short agent turn, re-running on the rare disconnect is cheap and safe via idempotency. That's a YAGNI call: no requirement justified it yet. If turns got long or expensive, or users needed seamless resume, I'd build the buffer — and at that point SSE's Last-Event-ID model would fit naturally, so I might switch. NDJSON itself I picked for the simpler client; the resume decision is separate."

> **Keep the two decisions distinct:** *why NDJSON over SSE* = client simplicity (pushback #1). *Why no reconnection/resume* = YAGNI (this one). Don't let an interviewer blur them — "NDJSON to avoid complexity" is weak because SSE-over-fetch isn't more complex; the complexity you actually skipped is the replay layer, skippable in either format.

### Pushback 3 — "Did you need WebSockets?"

Why they ask: WS is the famous "real-time" tech, so they're checking whether you know **when it's overkill** — reaching for it unnecessarily is a classic over-engineering tell.

**The core distinction — one-way stream vs two-way channel:**
- **HTTP streaming (SSE / NDJSON):** the client makes **one request**; the server **streams many responses back**. After the request, data flows **one direction only** (server → client). The client just listens.
- **WebSocket:** after a handshake, a **persistent two-way channel** — both sides send anytime, both directions, while the socket is open. Different protocol (`ws://`).

Classic WS use-cases are continuous **two-way** chat over one connection: multiplayer games, collaborative editing (live cursors), chat with typing indicators flowing both ways, a trading terminal you send orders through while prices stream back.

**Deciding question:** during a turn, does the client need to keep sending data over the same open connection? For an agent it's *"client sends one question → server streams the answer → done."* One-directional ⟹ **WS's two-way channel sits unused.**

**Anti-spam bonus (secondary, not the core reason):** turn-based request/response + a per-user concurrency guard (return `429` if a stream is already active) naturally bounds spamming. WS would make continuous client→server sending trivial, which you'd then have to rate-limit yourself. (A bonus of the model — you *can* rate-limit either transport, so don't lead with this.)

**Objection — "but you have human-in-the-loop, isn't that bidirectional?"**
No — HITL is modeled as **separate request/response cycles, not duplex**:

```
client POSTs question   ──►  server streams events... "interaction_required" ──► stream ENDS
client shows picker; user selects
client POSTs a NEW request (resume, tied by thread_id)  ──►  server streams the next leg
```

Each leg is still **one request → one-way stream back**. The selection travels as a *fresh POST*, not a message over a still-open socket. It's turn-based ping-pong, not continuous duplex — so WS still buys nothing.

**"Could WS do it all on one connection?" — yes, but it's worse:**

WS *could* carry the whole conversation (question, progress, HITL prompt, selection, continuation) over one socket. Two reasons not to:

1. **You're barely saving setup cost.** An **HTTP request ≠ a TCP connection.** HTTP **keep-alive** reuses the same warm TCP connection across separate requests, **skipping the handshake.** So the separate HITL POSTs don't re-pay the TCP+TLS handshake (~100–300 ms of round-trips) — it's paid once and reused. *(Caveat: if a human takes longer than the keep-alive idle timeout, the next POST pays a one-time fresh handshake — still far cheaper than holding a socket open the whole pause.)*

2. **The killer — WS holds a stateful socket open while a human thinks.** HITL means waiting on a *person* (10–60 s deciding). WS keeps that socket **open and pinned to one server** the entire deliberation. Request/response **ends the stream** at `interaction_required` — the connection closes, the server frees everything, and it reopens only when the user actually clicks. At scale: 10,000 users pondering a picker = **10,000 idle pinned WS connections** vs **0 held connections**. Request/response treats human think-time as *free*.

3. **General WS costs.** Stateful sockets pinned to one server need **sticky-session load-balancing** + connection lifecycle management (heartbeats, reconnection); plain HTTP requests any server can handle with standard load balancing. And WS's one real edge — **native binary frames** — is irrelevant when everything is JSON text.

**Interview line:**

> "No — for a turn it's one-directional: the client sends one question and the server streams the answer back, so WebSocket's full-duplex would sit unused. Even human-in-the-loop is modeled as separate request/response legs, not continuous duplex. WS *could* carry it all on one socket, but it'd hold a stateful connection open during every human pause — and HITL is full of human pauses — whereas request/response frees the connection during those gaps, so it scales better. WS also needs sticky-session load-balancing and connection management I don't need, and its binary-frame edge is moot for JSON."

---

**One-line summary:** *POST ⟹ no EventSource ⟹ fetch either way ⟹ NDJSON is the simpler frame; recovery lives in checkpointing, not Last-Event-ID.*
