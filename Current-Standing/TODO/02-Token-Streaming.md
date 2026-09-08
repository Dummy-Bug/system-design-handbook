# 02 — Token Streaming

Prerequisite to item 1 of Table 1 in [[../10-Xarvis-Build-Plan]] · scope: admin and employee agents only · researched 2026-09-07

> [!abstract] The goal
> The user should watch the answer appear as the model writes it, the way ChatGPT and Claude do it. Today they watch a **fake** typing animation replayed over a response that already arrived in full, which means the animation is pure added latency dressed as responsiveness.
>
> This is not adding streaming. The system already streams — one frame per lap of the agent loop. This is changing the **granularity** of the final answer from one message to a sequence of tokens, and deleting a frontend animation that is currently working against us.

---

## What exists today

Three services, one per audience, all built the same way:

| File | Lines | Notes |
|---|---|---|
| `streaming/services/admin_streaming_service.py` | 181 | Handles the HITL `__interrupt__`; supports resume via `Command` |
| `streaming/services/employee_streaming_service.py` | 156 | No interrupt path; tracks an access-denied outcome |
| `streaming/services/onboarding_streaming_service.py` | 187 | **Out of scope** |
| `streaming/sse_events.py` | 93 | Every frame in the system is built here |

All three call `graph.astream(..., stream_mode="updates")`, which yields **a whole node's output per iteration**. That is why progress messages arrive as finished sentences.

The discriminator is one line, and it does two jobs at once — the same did-the-model-ask-for-a-tool signal the loop uses to decide whether to keep going:

```
event_type = "progress" if tool_names else "terminal_response"
```

Three things in there are load-bearing and easy to lose in a rewrite:

- **The Gemini guard.** Tool calls are read **before** the empty-text check, because Gemini routinely emits a tool call with no text. Checking text first silently dropped both the progress frame and the record that the tool ran. There is a comment saying so; keep the comment.
- **`assistant_event()` is the single choke point.** Every frame in the system is built by one function in `sse_events.py`. That is genuinely good design and the rewrite must not spread frame construction back out into the services.
- **The `finally` block** logs the outcome — tools called, iteration count, final response length, whether it ended normally. It is the only measurement in the system and it must survive.

> [!note] The two services are near-duplicates
> Lines 47 to 100 of the employee service are near-verbatim lines 73 to 125 of the admin service, and both error handlers plus both `finally` blocks are identical apart from the logger name. Any change to streaming shape currently has to be made twice and kept in sync by hand.
>
> That is worth fixing **as part of this**, not before and not after — a shared generator with the audience-specific bits injected. Doing it separately means touching the same code twice.

---

## The safe path — add a mode, do not replace one

The obvious plan is to swap `stream_mode="updates"` for `stream_mode="messages"`. **Do not do that.** Everything after `node_name, node_output = next(iter(chunk.items()))` is written against the shape of an updates chunk, so swapping the mode rewrites the whole service and puts the interrupt, the dedup and the outcome logging all at risk in one change.

`stream_mode` accepts a **list**. Pass both and each item arrives tagged with which mode produced it:

```python
async for mode, chunk in graph.astream(input_data, config=config, stream_mode=["updates", "messages"]):
```

Which gives a migration with no demolition:

- **`updates` keeps doing everything it does now** — the interrupt, progress frames, the terminal response, dedup, outcome tracking. Untouched.
- **`messages` is used for one new thing only** — token deltas from the final answer.

The rewrite becomes an addition. If the new path is wrong, delete it and the old behaviour is still there.

---

## Unknowns to resolve before writing any service code

None of this can be designed from documentation. Run the existing graph in the new mode and print what comes out — a script, no service changes, thirty minutes.

- [ ] **Which nodes emit tokens**, so we know what to filter on via `metadata["langgraph_node"]`
- [ ] **Does Gemini emit any `.content` at all before a tool call**, or is the empty-text behaviour present at token level too. **This decides the whole design** — if there is no text, there is nothing to stream on intermediate laps and synthesised progress stays exactly as it is
- [ ] **What `tool_call_chunks` looks like** while arguments stream in fragments, and whether tool names are complete on the first chunk or assembled across several
- [ ] **Whether `__interrupt__` still surfaces** when two modes are requested. The which-Priya pause is the most distinctive thing in the codebase and it must survive
- [ ] **Whether both modes fire for the same message**, which would mean the final answer arrives twice — once as tokens and once as a whole `terminal_response`

That last one is the likely trap. If it happens, the terminal frame becomes a completion marker rather than a payload, and the client assembles the answer from deltas.

---

## The steps

**1 · Probe.** The script above. Write down what each of the five unknowns actually returns. Est. 30 min.

**2 · Decide the frame contract.** Given what the probe shows, settle: is there a new `token` event type, or do deltas ride inside `progress`. Does `terminal_response` still carry the full text, or become an end marker. This is decision 1 of the SSE design doc and it cannot be settled before step 1. Est. 30 min.

**3 · Deduplicate the two services first.** One generator, audience-specific behaviour injected — the interrupt path, the node allowlist, the outcome label. Nothing else changes yet, so the diff is provably behaviour-preserving. Est. 2h.

**4 · Add the token path behind a flag.** Both modes, deltas emitted only for the final answer, old behaviour intact when the flag is off. Est. 3h.

**5 · Delete the frontend animation.** Coordinate first — it is not my repo. Est. unknown, and it is the change that actually delivers the win.

**6 · Measure.** Before and after: time to first visible character, and total time to full answer. Est. 30 min.

---

## Measure before believing it was worth it

> [!important] The payoff scales with answer length and nothing else
> Streaming does not make the answer arrive sooner. Total time is unchanged. What changes is **when the first character appears**.
>
> So if a typical `terminal_response` is one or two sentences — Priya K.'s salary is ₹18L — token streaming saves a few hundred milliseconds and the honest design decision may be to **delete the animation and keep message-level frames**. If answers turn out to be paragraphs, leave policy explanations or multi-employee summaries, it earns its place properly.
>
> `final_response_length` is already in the outcome log. **Read it before building, not after.**

---

## What must survive, verbatim

- [ ] The Gemini guard — tool calls read before the empty-text check, comment intact
- [ ] The HITL interrupt and resume, admin only
- [ ] `done_event()` and its docstring — a finished stream and a cut stream are otherwise identical
- [ ] Errors delivered as content, never as a status code, because the status is fixed at 200 the moment the first byte leaves
- [ ] The outcome log in `finally`, both services
- [ ] `assistant_event()` as the only place a frame is constructed

---

## Definition of done

- [ ] The five unknowns answered from a real run, written down
- [ ] One shared generator, not two near-identical ones
- [ ] Tokens stream for the final answer, with synthesised progress still covering laps that carry no text
- [ ] The frontend animation deleted, not merely bypassed
- [ ] Time to first visible character measured before and after, both numbers recorded
- [ ] Everything in the survive list still works, demonstrated rather than assumed
