#sse #streaming #interview #questions

Two tiers, kept separate on purpose. **Verified** means it appears in a curated bank compiled from candidate materials and anonymised reports. **Derived** means it was written from what the topic contains — useful for rehearsal, not evidence anyone was asked it.

---

# Verified — asked as written

From `ombharatiya/AI-Engineer-Interview-Questions`, section 08, inference and production.

**Why do LLM products stream responses, and how does streaming actually work over HTTP?**
Marked as covering perceived latency, `Content-Type: text/event-stream`, incremental token delivery, proxy buffering, idle timeouts and reconnection. One question spanning four of the notes here.

**A user closes the tab halfway through a streamed response. What happens on the server, and what should happen?**
Marked as covering connection lifecycle, aborting generation, proxy buffering, framework-level disconnect detection, side-effect atomicity and durable resumable streams.

**How do you handle streaming when the model is emitting tool calls or structured JSON?**
Marked as covering incremental delta accumulation, block-indexed routing, partial-JSON parsing for the UI, validation gates, idempotency during retries and interleaved content types.

> [!warning] The third one is not covered by these notes at all
> Partial JSON parsing, incremental tool-call assembly and block-indexed routing appear nowhere in notes 1 to 8. The same repo carries a coding challenge for it — `12-coding-challenges/13_streaming_parser.py`, described as an SSE parser with incremental tool-call argument assembly.
>
> **A real gap, found by looking at real questions**, which is exactly what the derived set could not have told me.

# Verified — real production numbers

From the LLM gateway and serving platform case study in the same repo. Not questions, but the constraints an answer is expected to reason within.

```text
1  inter-token latency   < 40ms      above this the stream visibly stutters
2  p95 TTFT              < 700ms     for interactive routes at a 4k prompt
3  quota settlement      every 256 tokens
```

And four statements worth being able to defend:

- Most gateway traffic is streamed, which **constrains caching, quota settlement and retries** all at once.
- Once bytes have reached the client you **cannot transparently retry.** Retries are free only before the first token; after it, the gateway surfaces a typed terminal error mid-stream and the client decides.
- A long generation otherwise holds its full quota reservation for the whole call. Settling incrementally returns unused headroom early.
- **Client disconnects still settle.** Provider billing does not stop because the caller hung up, so neither does the platform's — and the abort is propagated backwards to actually stop generation.

> [!important] That last point is note 6, confirmed from outside
> The notes derived it from first principles: the tokens were produced, the provider charged for them, so the usage has to be recorded even though the request is being destroyed. A production gateway design states the same thing as a requirement.

# What the search actually found about frequency

**Streaming is not asked as a standalone topic.** The company files for OpenAI and Anthropic — the two most likely to test it — contain **no streaming questions at all.** OpenAI's guide mentions it once, inside a larger prompt: design the serving stack for a ChatGPT-scale assistant with streaming chat and multiple model tiers.

So it is absorbed into system design rather than examined on its own. Which changes how to prepare for it: not as a topic to be quizzed on, but as **the part of a serving-platform answer that most candidates handwave.**

---

# Derived — a rehearsal set

Everything below was written from the notes and from how 2026 guides describe these loops. **Nobody has reported being asked these.** They are answerable, they cover the material, and they are practice rather than reconnaissance.

# Transport choice

The most common opener, in some form, in every loop that touches streaming.

- Why SSE rather than WebSocket for streaming an LLM response?
- When would you choose WebSocket instead?
- Why not just poll the server every few hundred milliseconds?
- What does SSE give up compared to WebSocket?
- Does streaming make the response faster?

> [!important] What is being tested
> Whether the answer is about **direction of traffic and infrastructure cost**, or about vague notions of speed. Saying SSE is faster or lighter is the weak answer. Saying the traffic is one-directional so WebSocket's advantage does not apply while its cost does, and that SSE stays ordinary HTTP so every proxy already handles it, is the answer that survives a follow-up.
>
> The last question is a trap. Streaming does not reduce total latency at all.

# Protocol mechanics

Cheaper questions, usually early, often used to check whether the candidate has actually built one.

- How does the client know where one message ends and the next begins?
- What happens if the server forgets the blank line between frames?
- Can you send an image over SSE?
- What is `id:` for?
- What is `retry:` for, and who decides its value?
- What does a line beginning with a colon do?

> [!important] What is being tested
> The blank-line question separates people who have read about SSE from people who have shipped it, because **the failure is silence rather than an error** and only someone who has hit it describes it that way.

# Production failures

The highest-signal group, and the one most people are unprepared for.

- Streaming works perfectly on your laptop and not in production. What is your first check?
- The client shows nothing, but the server logs say every frame was written and the connection is open. Walk me through it.
- What kills an idle streaming connection when neither end has closed it?
- How do you choose a heartbeat interval?
- Your stream dies after exactly sixty seconds, every time. What is it?

> [!important] What is being tested
> Whether you know that **a blank screen with healthy logs is never a generation problem.** The three candidates are framing, buffering and a dead connection in the middle, and a good answer names all three plus how to separate them — everything arriving at once at the end means buffering, failing on the first frame every time means framing, failing only after a quiet stretch means the connection.
>
> The sixty seconds question has a specific answer, because sixty is the default idle timeout for both nginx and an AWS load balancer.

# Backpressure and resources

Where a backend interview goes once it is satisfied you know the protocol.

- The client reads slower than the model produces. What happens?
- Does one slow client slow down everybody else?
- You have a thousand concurrent streams. What does that cost?
- Someone puts a queue between the generator and the socket to decouple them. What breaks?
- Where do the model's tokens go while your generator is paused?

> [!warning] A common claim in prep material is wrong
> Several 2026 guides state that SSE has no backpressure and that WebSocket has it through TCP flow control. **Both run over TCP**, so TCP-level backpressure applies identically to each — a full send buffer suspends the write either way.
>
> What SSE genuinely lacks is an **application-level** signal: no way for the client to say slow down inside the protocol. That is a real and much narrower limitation, and being able to state it precisely is a strong signal in itself.

# Cancellation and cost

Increasingly common wherever the endpoint has a model behind it, because it is a money question.

- A user closes the tab mid-answer. What happens on the server?
- How much does that cost before anything stops?
- How do you implement a stop button?
- Your service runs on several instances. The stop request lands on a different one than the stream. Now what?
- After a cancellation, what do you still owe, and where does it get recorded?
- What is the difference between a coroutine being suspended and being cancelled?

> [!important] What is being tested
> The stop-button question is the good one, because the naive answer is to send the stop down the existing connection — which is impossible, since the stream only travels one way. Getting to a **separate request naming a stream id**, and then to the map from ids to running work, is the whole answer.
>
> The multi-instance follow-up is where most answers stop. A task cannot be stored in a shared cache; what can be shared is a flag the generator checks.

# Errors and limits

- An error occurs twelve seconds into a stream. How do you report it?
- Why can you not just return a 500?
- How does the client tell a stream that finished from one that died?
- Six tabs of your app work and the seventh hangs with no error. Why?
- What changes under HTTP/2?

> [!important] What is being tested
> That **the status line is sent before anything is generated**, so success was promised before it was known. The follow-up is what that costs — monitoring counting non-200s reports a healthy service while every request fails, and anything retrying on status has nothing to retry on.

# Resumption

Usually the deepest question asked, and the one that separates people who have shipped this.

- A connection drops halfway through an answer. How do you resume it?
- What does honouring `Last-Event-ID` require you to store?
- Replay the frames you sent, or rebuild the answer from saved state? Which, and why?
- Your agent runs forty-five seconds and emits two hundred progress updates. Does that change the answer?
- Where does the stream id come from, and what stops one user reading another's stream?
- How long do you keep a replay buffer, and what happens to someone who reconnects after it expires?

> [!important] What is being tested
> Whether the trade is understood rather than a preference recited. **Replay knows where the client was; re-deriving only knows where the answer ended up.** One costs storage with a retention policy, the other costs fidelity.
>
> The forty-five-second follow-up is deliberately designed to break a memorised answer — progress events are in neither, so a resumed long-running stream looks like a different product entirely.

---

# The three that recur most

Across every guide surveyed, these appear more than any others.

```text
1  why SSE and not WebSocket
2  how do you resume a stream that dropped mid-answer
3  how do you stop generating when the user closes the tab
```

The first is asked to check you have an opinion. The second is asked to find out whether you have shipped one. The third is asked because it is a cost question, and the follow-up is always about the bill.

# The one that catches people who only read

**What happens to an error thrown halfway through a stream?**

There is no good answer. Both options are bad, and knowing that both are bad — that closing the connection is indistinguishable from a network failure, and that an error frame hides the failure from every piece of HTTP tooling — is the answer.

---

# Sources

**For the verified section** — a curated bank compiled from candidate materials, published guides and anonymised reports:

- [`ombharatiya/AI-Engineer-Interview-Questions`](https://github.com/ombharatiya/AI-Engineer-Interview-Questions) — section `08-inference-and-production/questions.md` for the three questions, `11-ai-system-design/case-studies/10-llm-gateway-and-serving-platform.md` for the production numbers, and `12-coding-challenges/13_streaming_parser.py` for the streaming-parser exercise
- The company files under `14-company-interview-questions/` were checked directly. **OpenAI's and Anthropic's contain no streaming questions**, which is the finding above.

**For the mechanics behind the third question:**

- [Anthropic — streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming) and [fine-grained tool streaming](https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming)
- Real bugs from exactly this failure: [opencode #24137](https://github.com/anomalyco/opencode/issues/24137) where a tool call breaks when `function.name` arrives in a later chunk, and [pipecat #4987](https://github.com/pipecat-ai/pipecat/issues/4987) where the tool call id is empty because id and name arrive in separate deltas

**For the derived section** — architecture and guide articles that shaped the themes. **None is a question bank.**

- [Server-Sent Events in 2026 — streaming architecture and scalability](https://thebackenddevelopers.substack.com/p/server-sent-events-in-2026-streaming)
- [Streaming patterns in 2026 — SSE, WebSocket, gRPC, HTTP streaming](https://blog.rajpoot.dev/posts/backend/streaming-patterns-2026/)
- [AI token streaming, from SSE to durable sessions](https://websocket.org/guides/use-cases/ai-streaming/)
- [Streaming agent responses in production](https://niteagent.com/blog/2026-07-09-streaming-agent-responses-production-guide/)
- [GenAI and LLM system design interview guide 2026](https://prachub.com/resources/genai-llm-system-design-interview-guide-2026)
