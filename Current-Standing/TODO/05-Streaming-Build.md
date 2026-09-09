# 05 — Token Streaming Build

Implementation tasks for [[02-Token-Streaming]] against [[03-Stream-Contract]] · scope: **admin agent only** · 2026-09-08

> [!abstract] What this is
> Every step needed to get token streaming live on the admin agent, small enough that each one either works or fails loudly, and none of them can half-work. Each task names the exact file, the exact change, the command that proves it, and how to undo it.
>
> Employee and onboarding are deliberately untouched. **The LangGraph upgrade is deferred** — see phase 1 — so everything here is built on the stack already running.

---

## What was found in the code, before any of this

Read on 2026-09-08 against `src/xarvis/`. Five things change the plan in [[02-Token-Streaming]].

### The node calls `ainvoke`, so there are no tokens to stream

`orchestration/admin/nodes/chatbot.py` lines 73 to 76:

```python
response = await asyncio.wait_for(
    admin_llm.ainvoke(base_window),
    timeout=TIMEOUT_SECONDS_PRIMARY,
)
```

`stream_mode="messages"` intercepts token callbacks from a streaming model call. `ainvoke` on `langchain-google-genai` calls the non-streaming endpoint, so there is nothing to intercept.

Verified by inspecting `ChatGoogleGenerativeAI` at 4.1.2 rather than assuming it: `_generate`, `_agenerate`, `_stream` and `_astream` are all defined separately on the class, and **`_agenerate` does not delegate to `_astream`**. So `ainvoke` genuinely reaches the non-streaming endpoint and fires no token callbacks.

> [!important] A fake model will tell you the opposite, and it is not lying
> A graph node calling `ainvoke` on `GenericFakeChatModel` **does** produce token chunks in `messages` mode, because that class implements only `_stream` and the base class aggregates it. Any test harness built on a fake model will therefore show streaming working before a single line of the node has changed.
>
> Gemini does not work that way. Do not let a green fake-model test stand in for this.

> [!important] The probe in [[02-Token-Streaming]] would have produced a false negative
> Running `stream_mode=["updates","messages"]` against the graph as it stands yields one message-mode chunk carrying the whole response, which looks identical to what `updates` already gives. The honest conclusion from that probe is that token streaming does not work — and it would be wrong.
>
> The first real change is in the node, not in the streaming service.

### The 10-second timeout changes meaning under streaming

`asyncio.wait_for(..., timeout=10)` around `ainvoke` is a **time-to-response** budget. The same wrapper around consuming an `astream` generator becomes a **total-generation** budget, so a healthy answer that takes 12 seconds to finish streaming is killed at 10 with a `TimeoutError` and falls through to the fallback LLM — which then re-answers a question the user was already watching being answered.

It has to become a first-token timeout instead. Task 2.3.

### The fallback decision needs a complete response, streaming does not have one

`is_invalid_gemini_response` at line 21 inspects finished content and finished `tool_calls` to decide whether to fall back. Under streaming you learn that only at the end, by which point tokens are already on the user's screen and cannot be retracted.

The resolution is in the predicate itself: invalid means **empty content and no tool calls**. So the first non-empty chunk proves validity. Hold tokens until the first content arrives, then commit and emit `text_start`. If the stream finishes having produced nothing, fall back with nothing yet sent and nothing to retract. Task 2.4.

### Two paths produce answers that will never emit a token

- `chatbot.py` lines 128 to 137 — the hard-fail path returns a hand-constructed `AIMessage`.
- The employee graph's `access_denied` node does the same, and is out of scope here but will matter later.

Neither is model output, so neither appears in `messages` mode. **The `updates` path must stay as the fallback for answers that arrive with no tokens**, which is the strongest argument for the dual-mode plan rather than a replacement.

### The terminator is emitted by the route, not the service

`server/routes/chat.py` line 161 yields `done_event()` after the service generator is exhausted. So the new `done` frame is a change to `chat.py`, not to either service. It also means the service returning early on an interrupt (`admin_streaming_service.py` line 65) still produces a terminator, which is correct and must stay true.

---

## Versions — the stack this is built on

Installed, and staying installed. The upgrade is deferred, so these are the versions every task below runs against.

| Package | Version | Note |
|---|---|---|
| `langgraph` | **1.0.5** | dual-mode streaming verified working |
| `langchain` | 1.0.5 | pins `langgraph>=1.0.2,<1.1.0` — the reason the upgrade widens |
| `langchain-core` | **1.2.6** | `content_blocks` verified present |
| `langchain-google-genai` | 4.1.2 | `_agenerate` does not delegate to `_astream` — see phase 2 |
| `langgraph-checkpoint` | 3.0.1 | |
| `langgraph-prebuilt` | 1.0.2 | |
| `langgraph-sdk` | 0.3.1 | |
| `langgraph_dynamodb_checkpoint` | 0.2.6.4 | declares `langgraph` with **no version bound** |
| `fastapi` | 0.141.1 | native `fastapi.sse`, 15s keep-alive default |
| Docker base | **python:3.11.12** | `get_stream_writer()` works in async above 3.11 |

---

## Phase 0 — Measure, before building anything

> [!important] This phase can cancel the rest of the work, which is why it is first
> Streaming does not make an answer arrive sooner. It changes when the first character appears. If typical answers are one or two sentences, the honest outcome is to delete the frontend animation and keep message-level frames, and phases 2 to 6 do not happen.

**0.1** — Pull `final_response_length` out of the outcome log. It is already recorded, in `ADMIN_OUTCOME_LOG`, `admin_streaming_service.py` line 178.

**0.2** — Compute the median and the 90th percentile over the last 14 days of admin turns.

**0.3** — Write both numbers down here:

```
median final_response_length   = ____ characters
p90    final_response_length   = ____ characters
sample size                    = ____ turns
```

**0.4** — Decide, and record the decision with the numbers next to it.

| Median length | Verdict |
|---|---|
| under ~200 characters | streaming saves a few hundred milliseconds. **Delete the animation, stop here.** |
| 200 to 600 | marginal. Proceed only if answers are visibly slow today |
| over ~600 | streaming earns its place. Proceed |

**Revert:** nothing was changed.

---

## Phase 1 — Upgrade LangGraph · DEFERRED 2026-09-08

Not done, deliberately. The build runs on the stack already installed. This section records why, and what the resolver found, so the work is not repeated when the upgrade does happen.

### Why it was deferred

The upgrade is not required for token streaming. Everything the build needs was verified present on the installed versions:

| Mechanism | On `langgraph==1.0.5` / `langchain-core==1.2.6` | Verified by |
|---|---|---|
| `stream_mode=["updates","messages"]` | yields `(mode, chunk)` 2-tuples | real graph run, 11 token chunks + 1 updates chunk |
| token chunks tagged by node | `metadata["langgraph_node"] == "chatbot"` | same run |
| `AIMessage.content_blocks` | present — `[{'type': 'text', 'text': ...}]` | direct call |
| `AIMessageChunk` addition | `'Pri' + 'ya'` gives `'Priya'` | direct call |
| `get_stream_writer` | importable from `langgraph.config` | direct import |
| `tool_call_chunks` | attribute present on `AIMessageChunk` | direct call |

What 1.2.11 would add is the `version="v2"` StreamPart shape and the service shrink that follows from it. Real, but not load-bearing, and taking it now would put an unrelated framework jump in the same deploy as the streaming change — a phase 2 bug and an upgrade bug would look identical.

### What the resolver found, when the upgrade is picked up again

Resolved with `uv pip compile` against Python 3.11, matching `python:3.11.12-slim-bullseye` in the Dockerfile.

> [!important] The LangGraph family does not move alone
> ```
> langchain==1.0.5 depends on langgraph>=1.0.2,<1.1.0
> ```
> LangChain has to move with it. Probing the floor: **1.1.0 and 1.2.0 both conflict** with `langgraph==1.2.11`; **1.3.0 is the minimum** that resolves, and the resolver picks 1.4.0. So it is four minor versions of the package that owns the agent loop, not a family-only bump.
>
> A second hidden pin: `langgraph-sdk>=0.4.2` requires `orjson>=3.11.5`, against the current `orjson==3.11.4`.

**Three packages in `requirements.txt` are never imported anywhere in `src/`**, and each one distorts the upgrade if left in:

| Package | Only reference | Effect of keeping it |
|---|---|---|
| `langgraph-checkpoint-redis==0.2.1` | `_create_redis_checkpointer()`, which raises `NotImplementedError` | forces a **downgrade to 0.1.0** to satisfy `langgraph-checkpoint==4.2.0` |
| `langgraph-runtime-inmem==0.20.1` | none | drags **`sse-starlette` back in**, which was deliberately removed in favour of native `fastapi.sse` |
| `redisvl==0.12.1` | none | drags in `redis==6.4.0` |

`neo4j` was checked at the same time and is heavily used — it stays.

With those three dropped, the resolution comes out clean:

| Package | From | To |
|---|---|---|
| `langchain` | 1.0.5 | 1.4.0 |
| `langchain-core` | 1.2.6 | 1.6.2 |
| `langchain-google-genai` | 4.1.2 | 4.2.1 |
| `langchain-openai` | 1.1.1 | 1.1.9 |
| `langgraph` | 1.0.5 | 1.2.11 |
| `langgraph-checkpoint` | 3.0.1 | 4.2.0 |
| `langgraph-prebuilt` | 1.0.2 | 1.1.0 |
| `langgraph-sdk` | 0.3.1 | 0.4.4 |
| `langgraph_dynamodb_checkpoint` | 0.2.6.4 | 0.3.1 |
| `langsmith` | 0.4.42 | 0.12.2 |
| `orjson` | 3.11.4 | 3.12.0 |

Added: `langchain-protocol`, `httpx2`, `httpcore2`, `pytz`, `setuptools`. Removed: the three unused ones. `pydantic` stays at 2.12.4.

### The smoke tests, kept for when it happens

Fresh virtual environment, never the existing one. Then: app imports and starts · admin with no tools · admin with one tool call · **the admin interrupt, triggered, ended, resumed, completed** · a thread paused on the old version and resumed on the new · employee plain, tool and access-denied paths · one full onboarding flow including a `pipeline_step` frame, since onboarding runs `RequestContext.emit` and `from_stream_event`, code the other two never touch · both outcome logs still emitting all six fields.

---

## Phase 1B — Capture the baseline · DONE 2026-09-08

Deferring the upgrade removed the step that established what current behaviour looks like, and every later task says byte-identical without one. This restores it. Nothing was changed; it is a recording.

### How to run it locally

`.env` is already configured for this and needs no edits: `ENV=local`, `SKIP_SESSION_AUTH=true`, `CHECKPOINTER_MODE=memory`, `LANGCHAIN_TRACING_V2=false`, and `HRMS_BASE_URL` pointed at staging. So a local run consumes no LangSmith quota and never touches production.

```
.venv/bin/python -m xarvis                     # port 8080, startup works without neo4j
curl -s -X POST localhost:8080/api/v1/session -c cookies.txt
curl -sN -X POST localhost:8080/api/v1/chat -b cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"type":"chat","message":"..."}' > baseline_plain.sse
```

> [!important] The session call is not optional, even with auth skipped
> `validate_session` runs at `request_context.py` line 49, **before** the `SKIP_SESSION_AUTH` short-circuit on line 52. Without an `xarvis_session` cookie it raises 401 and the skip is never reached. Create the session first.

`ENV=local` also means `create_session` takes the dev path and needs no OAuth code, so a bare POST with no body is enough. Every local turn runs as `DEV_USER` on `thread_id` `xarvis-local`, which is hardcoded — so **captures share one conversation** and later turns see earlier ones.

### 1B.1 to 1B.5 — the recorded baseline

| Capture | Frames | Sequence | `final_response_length` | Wall time |
|---|---|---|---|---|
| plain, no tool | **2** | `terminal_response` · `done` | 675 | fast |
| one tool call | **3** | `progress` · `terminal_response` · `done` | 71 | **12.1s** |
| HITL interrupt | **3** | `progress` · `interaction_required` · `done` | 0 | 6.1s |
| HITL resume | **3** | `progress` · `terminal_response` · `done` | 762 | 10.9s |

Saved as `baseline_plain.sse`, `baseline_tool.sse`, `baseline_hitl.sse`, `baseline_hitl_resume.sse`. These are the comparison target for 2.5, 2.7, 4.5 and 5.9. Identical means the frame sequence and count match, ignoring the answer text, which the model varies between runs.

### What the captures settled

**The route does emit a terminator after an interrupt.** The HITL capture ends `interaction_required` then `done`, so the service returning early at `admin_streaming_service.py` line 65 still reaches `yield done_event()` in the route. Task 6.3 changes what that frame says, not whether it arrives.

**Gemini's empty-text behaviour is real and intermittent** — which answers the second unknown in phase 3 ahead of the probe:

| Turn | Progress text | Source |
|---|---|---|
| leave balance | Let me fetch your leave balance details for you. | **the model** |
| `ask_human` | Let me check something with you... | `TOOL_PROGRESS_OVERRIDES` |
| work summary | Fetching employee work details... | `tool_progress_message()` |

Two of three tool calls carried no model text at all. The Gemini guard is load-bearing, and synthesised status has to stay for the laps that carry no text.

**Answer length varies far too much for one number to settle phase 0.** 675, 71, 0, 762 across four turns. The measurement has to come from production volume, not from a handful of local runs.

> [!important] Task 6.7 confirmed from a real run, not from reading
> The interrupt turn logged:
>
> ```
> "query": "Give me a summary",
> "tools_called": ["ask_human"],
> "tool_outcome": "unknown",
> "iteration_count": 2,
> "final_response_length": 0,
> "ended_normally": false
> ```
>
> **`ended_normally` is `false` and `tool_outcome` is `unknown` on a turn that worked perfectly.** Every HITL turn in production has been logging as abnormal. The only measurement in the system is wrong about the most distinctive feature in it, and the fix is task 6.7.

**Revert:** nothing was changed.

---

## Phase 2 — Make the model actually stream

Nothing in this phase touches the streaming service or the wire format. The output of the phase is that tokens exist.

**2.1** — In `orchestration/admin/nodes/chatbot.py`, add a module-level flag so every change in this phase is switchable without a deploy.

```python
STREAM_PRIMARY = os.getenv("ADMIN_STREAM_PRIMARY", "false").lower() == "true"
```

Default off. Every step below runs behind it.

**2.2** — Add a streaming branch alongside the existing `ainvoke` call. **Do not replace the existing call.** Both paths exist; the flag chooses.

The streaming branch consumes `admin_llm.astream(base_window)` and accumulates the chunks with LangChain's chunk addition, which is verified to work: `AIMessageChunk(content="Pri") + AIMessageChunk(content="ya")` gives `'Priya'`.

**2.2a** — Convert the accumulated chunk back to an `AIMessage` before returning it. This is not tidiness, it is the difference between working and silently losing the answer.

> [!important] Accumulating chunks does not give you an `AIMessage`
> `chunk + chunk` returns an **`AIMessageChunk`**, and the two differ in the one attribute the streaming service filters on:
>
> | Message | `.type` |
> |---|---|
> | `AIMessage` | `ai` |
> | accumulated `AIMessageChunk` | `AIMessageChunk` |
>
> `admin_streaming_service.py` line 74 lowercases that and tests it:
>
> ```python
> role = getattr(m, "type", getattr(m, "role", "")).lower()
> if role not in ("ai", "assistant"):
>     continue
> ```
>
> `aimessagechunk` is not in that tuple, so the message is skipped: **no `terminal_response`, no `progress`, `tools_called` never populated, and the outcome log wrong.** The answer disappears with no exception anywhere.
>
> It is invisible until the flag is on. Task 2.5 with the flag off passes clean, and then 2.7 fails for a reason that looks nothing like its cause.
>
> The conversion is verified to restore it — `AIMessage(content=acc.content, tool_calls=acc.tool_calls).type` gives `ai`. Carry `tool_calls` across explicitly; the whole Gemini guard depends on them surviving.

The node's contract with the graph is then unchanged, which is what lets the rest of the service stay untouched.

**2.3** — Replace the total-generation timeout with a **first-chunk** timeout on the streaming branch only.

The existing `asyncio.wait_for(..., 10)` must not wrap consumption of the generator. Time only the wait for the first chunk; once the first chunk has arrived, the model is responding and the budget is spent.

Record what a total timeout would have meant:

```
old semantics: entire response must complete within 10s
new semantics: first chunk must arrive within 10s, generation may then run
```

**2.4** — Move the validity decision to the first chunk.

`is_invalid_gemini_response` stays exactly as it is for the `ainvoke` path. For the streaming path the equivalent test is: did any chunk carry non-empty text, or did any chunk carry a tool call. If yes, the response is valid and the fallback is not taken. If the stream ends having produced neither, fall back exactly as today.

**Nothing is emitted to the client in this phase**, so there is still nothing to retract.

**2.5** — Verify with the flag **off**. All three phase-1B captures must diff clean. This is the step that proves the change is additive.

**2.6** — Verify with the flag **on**, using a log line inside the node counting chunks received. Not a client-visible change yet.

```
expected: chunk count > 1 on a multi-sentence answer
failure:  chunk count == 1 means the model is still not streaming
```

**2.7** — With the flag on, re-run all three phase-1B captures. Frames on the wire must still diff clean, because the node is still returning one complete message.

**2.8** — With the flag on, verify the **fallback** path still triggers. Force it by pointing `ADMIN_MODEL` at a bad model name so the primary fails.

**2.9** — With the flag on, verify the **hard-fail** path still returns its constructed `AIMessage`.

**Revert:** set `ADMIN_STREAM_PRIMARY=false`. No code removal needed.

### Result — 2026-09-08, all nine done

One file changed, `orchestration/admin/nodes/chatbot.py`: the flag, a `stream_primary_llm` helper, and a two-line branch at the primary call site. Nothing else in the repo was touched.

| Task | Check | Result |
|---|---|---|
| 2.5 | flag off, three captures vs baseline | **identical** on all three |
| 2.6 | chunk count with the flag on | **8, 3, 4, 3** — all above 1 |
| 2.7 | flag on, three captures vs baseline | **identical** on all three |
| 2.8 | fallback, forced with a bad `ADMIN_MODEL` | `PRIMARY_LLM_ERROR` then `Falling back to Fallback Admin LLM`, answer delivered |
| 2.9 | hard fail, forced with a bad API key | `PRIMARY_LLM_ERROR` · `FALLBACK_LLM_ERROR` · constructed `AIMessage` delivered |

**Gemini streams, and coarsely.** Eight chunks for a 675-character answer, three or four for a tool call. This is not per-token; it is a handful of blocks. The improvement in time-to-first-character is therefore real but smaller than a token-by-token stream would give, and that belongs in the phase 0 judgement.

### Two simplifications the tests earned

**2.4 does not need a separate validity path.** `is_invalid_gemini_response(None)` already returns `True`, so a helper returning `None` for a stream that yielded nothing falls through to the fallback with no new branch. One predicate serves both paths and cannot drift.

**The exception handlers need no change.** On Python 3.11 `asyncio.TimeoutError is TimeoutError`, so what `asyncio.timeout()` raises is exactly what the existing `except asyncio.TimeoutError` catches. Confirmed on 3.11.12 rather than assumed.

### Two things the design gained from being tested first

The helper was built and exercised against a fake model in a scratchpad before the repo was touched, across five cases: normal text, empty stream, tool call with no text, slow first chunk, slow middle chunk.

- **Tool-call chunks reassemble correctly.** Name, id and args survive: `{'name': 'get_employee_leave_balance_details', 'args': {'employee_id': '1000'}, 'id': 'call_1'}` from three fragments. Args arrive as partial JSON and are parsed once the block closes, so nothing needs to hand-assemble them.
- **The timeout is scoped to the first chunk only.** The slow-middle case ran 1.20s against a 0.3s budget and completed, which is the proof that the budget is not wrapping the loop. Getting this wrong kills healthy answers and hands them to the fallback.

The helper closes the generator in a `finally`, because a timeout cancels the pending `__anext__` and leaves it suspended on an open connection to the model.

### One temporary line to remove later

`logger.info("PRIMARY_STREAM_CHUNKS", extra={"chunks": chunk_count})` exists to satisfy 2.6. Keep it while the flag is still a flag; it is the only signal that the streaming path ran at all. It goes with the flag in 7.3.

---

## Phase 3 — Probe, on the streaming graph

Only now does the probe from [[02-Token-Streaming]] produce meaningful answers. A script, no service changes.

Two of the five unknowns are already settled by the harness test run on 2026-09-08, against a fake streaming model on the installed versions. They still get confirmed against real Gemini, but the expected answer is known rather than open:

| Settled | Answer |
|---|---|
| chunk shape when two modes are requested | `(mode, chunk)` 2-tuples. For `messages`, `chunk` is itself `(message, metadata)` |
| ordering | every `messages` chunk for a node arrives **before** that node's single `updates` chunk, which fires on node completion |
| does the answer arrive twice | **yes** — 11 token chunks, then an `updates` chunk carrying the same complete text |

**3.1** — Run the admin graph with `stream_mode=["updates", "messages"]` and print every chunk with its mode, unmodified.

**3.2** — Answer each unknown in writing, here:

```
Which nodes emit token chunks (metadata["langgraph_node"])
  expected "chatbot" -> ____

Does Gemini emit any .content before a tool call, at token level
  genuinely unknown, decides whether synthesised status stays -> ____

What tool_call_chunks looks like across chunks
  (expected: name and id on the first, arg fragments after, same index)
  -> ____

Does __interrupt__ still surface with two modes requested
  not yet verified, and it is the highest-risk answer here -> ____

Does the final answer arrive twice, once as tokens and once as an updates
  terminal_response
  expected YES, confirmed on the harness -> ____
```

**3.3** — Watch specifically for a **cumulative** `AIMessageChunk` — a chunk repeating text already sent. It is a reported behaviour in `messages` mode and naive concatenation would double-render the answer. Record whether it occurs.

```
cumulative chunks observed: yes / no
```

**3.4** — If the answer to the last unknown in 3.2 is yes, that is expected and already handled by the contract: `updates` stops being the source of answer text and becomes the source of everything else. Confirm and move on.

**Revert:** nothing was changed.

### Result — 2026-09-08, all five answered

Run against the real admin graph via `bootstrap_app()`, on three questions: a plain answer, a tool call, and one that interrupts. Nothing was changed to get these.

| Unknown | Answer |
|---|---|
| which nodes emit token chunks | `chatbot` **and `tools`** — the tools node emits `ToolMessage` into the same stream |
| does Gemini emit text before a tool call | **sometimes** — leave balance carried `Let me check your...`, `ask_human` carried nothing at all |
| `tool_call_chunks` shape | `name` and `id` complete on the **first** chunk, `index` is **`None`** rather than 0, and `args` arrived whole in one chunk rather than fragmented |
| does `__interrupt__` survive dual mode | **yes** — it arrives as an `updates` chunk under the `__interrupt__` key, exactly as today |
| does the answer arrive twice | **no — three times.** See below |

**Cumulative chunks: none.** Each `AIMessageChunk` is a distinct fragment, so no length-tracking dedupe is needed. Task 5.5 loses that clause.

> [!important] The answer arrives three times, not twice, and two of the three are inside `messages` mode
> On the plain question, `messages` mode yielded ten items: nine `AIMessageChunk` summing to **781 characters**, then a tenth item that is a plain **`AIMessage` carrying the whole 781 characters again**. The `updates` chunk then carried it a third time.
>
> ```
> [msg   1] type=AIMessageChunk  len=  77
> [msg   2] type=AIMessageChunk  len= 108
> ...
> [msg   9] type=AIMessageChunk  len=   0
> [msg  10] type=AIMessage       len= 781   <- the whole answer, again
> [upd   1] node='chatbot'                  <- and again
> ```
>
> The tenth item is the node's returned message being republished through the same channel. Emitting a `text_delta` for every `messages` item would therefore render the answer twice over.

### Two corrections this forces on phase 5

**5.3 — the filter needs a type test, not just a node test.** Filtering on `langgraph_node` alone lets through both the duplicate final `AIMessage` and every `ToolMessage` from the tools node, which would put raw tool output in front of the user. One test excludes all three, verified:

```python
meta.get("langgraph_node") == CHATBOT_NODE and isinstance(msg, AIMessageChunk)
```

| Message | `isinstance(msg, AIMessageChunk)` | |
|---|---|---|
| `AIMessageChunk` | `True` | deltas included |
| `AIMessage` | `False` | the duplicate excluded |
| `ToolMessage` | `False` | tool output excluded |

`AIMessageChunk` subclasses `AIMessage` rather than the reverse, so the parent does not satisfy the child's isinstance test. That asymmetry is what makes the one-line filter work.

**5.5 — `content` is a list of blocks, not a string.** Gemini through `langchain-google-genai` yields `[{'type': 'text', 'text': '...'}]`, and an empty list on a lap that carries only a tool call. `str(content)` would put a Python repr on the wire. The services already handle this shape at `admin_streaming_service.py` lines 81 to 89, and the token path must reuse it rather than inventing a second extractor:

```python
content = m.content
if isinstance(content, list):
    texts = [b.get("text") for b in content if isinstance(b, dict) and b.get("text")]
    full_text = "".join(texts)
else:
    full_text = str(content)
```

---

## Phase 4 — Frame builders

Additions only to `streaming/sse_events.py`. No existing function is modified or removed.

**4.1** — Add a sequence counter. It must be per-stream, not global — a module-level integer would interleave across concurrent users.

**4.2** — Add builders, one per contract frame:

```
message_start_event(run_id, thread_id, audience)
status_event(code)
text_start_event(block_id)
text_delta_event(block_id, text)
text_end_event(block_id)
reasoning_start_event(block_id) / reasoning_delta_event / reasoning_end_event
done_frame(stop_reason, usage, iterations, text=None)
error_frame(code, message, partial_output, retryable)
```

Every one routes through `assistant_event()`. **It stays the only place a frame is constructed**, which is the property worth protecting most in this whole change.

**4.3** — Add the status vocabulary and the fail-closed map.

```python
_STATUS = {
    # fill from the real admin tool registry
}

def status_for(tool_name: str) -> str:
    return _STATUS.get(tool_name, "working")
```

The `.get` default is the entire design. A tool added later with no entry resolves to `working` and leaks nothing.

**4.4** — Keep `tool_progress_message()` and `TOOL_PROGRESS_OVERRIDES` in place, untouched, for as long as the old path exists. They are deleted in phase 7, not now.

**4.5** — Verify: nothing imports the new builders yet, and all three phase-1B captures still diff clean.

**Revert:** delete the added functions.

### Result — 2026-09-08, all five done

Appended to `streaming/sse_events.py`, which grew from 108 to 315 lines. Nothing above the new section was modified, and `tool_progress_message()` and `TOOL_PROGRESS_OVERRIDES` are untouched as 4.4 requires.

| Task | What landed |
|---|---|
| 4.1 | `StreamFrames`, one instance per turn, holding that turn's `seq` |
| 4.2 | Eleven builders, every one routing through `assistant_event()` |
| 4.3 | `StatusCode` literal, `_STATUS_BY_TOOL` over **36 tools**, `status_for()` |
| 4.4 | old builders untouched |
| 4.5 | nothing imports the new code; all three captures still diff clean |

Verified by construction rather than by reading: `seq` runs 0,1,2,... within a stream and restarts at 0 for a second `StreamFrames`, every frame's SSE event name equals its `data.type`, and every frame carries `role: assistant`.

**The fail-closed map does what it is for.** `get_employee_salary_details` resolves to `looking_up_payroll`, `get_span_of_control_report` to `looking_up_team`, and an unmapped name — the tool somebody adds next month — to `working`. Nine codes cover thirty-six tools, deliberately: the user does not need to know which of four leave endpoints answered.

Two design points worth keeping:

- **`done(text=...)` carries the removal criterion in its own docstring**, not only in [[03-Stream-Contract]]. The previous transitional field in this module became permanent because its criterion lived in prose alone.
- **`error()` documents why `message` must never carry exception text** — raw `str(exc)` leaks tool names, hostnames and occasionally credentials into a browser.

### Types — `ty` clean, and it found two real defects

Everything added is annotated: `StatusCode`, `StopReason`, `ErrorCode` and `PartialOutput` as `Literal` unions, `_STATUS_BY_TOOL` as `dict[str, StatusCode]`, and every builder with parameter and return types.

Project-wide `ty` sits at **206 diagnostics before and after**, and both changed files report `All checks passed`.

Running it against the phase 2 helper was not cosmetic. It caught two things a reading pass had missed:

> [!important] `AsyncIterator` does not guarantee `aclose`, and mine was inside a `finally`
> ```
> error[unresolved-attribute]: Object of type `AsyncIterator[BaseMessage]` has no attribute `aclose`
> ```
> `llm.astream()` is typed as `AsyncIterator`; only `AsyncGenerator` declares `aclose`. Every LangChain implementation happens to be a generator, so it worked in every test. But an `AttributeError` raised from inside `finally` would have surfaced in place of whatever actually went wrong, on exactly the timeout path that block exists to handle.
>
> Now guarded with `getattr(agen, "aclose", None)`.

The second was `tool_calls` on the accumulator: `BaseMessageChunk` does not declare it, only `AIMessageChunk` does, and the Gemini guard downstream depends on it surviving. Resolved with one documented `cast` at the return rather than by widening the annotation until the checker went quiet.

Re-verified at runtime after the typing changes, because the `aclose` guard is a real behaviour change and not just an annotation: all three captures identical, four `PRIMARY_STREAM_CHUNKS` entries, zero errors in the log.

---

## Phase 5 — The admin token path, behind a second flag

**5.1** — Add a second flag, independent of the node one.

```python
ADMIN_TOKEN_FRAMES = os.getenv("ADMIN_TOKEN_FRAMES", "false").lower() == "true"
```

Two flags rather than one, so that a model that streams can be separated from frames that stream. If something breaks, this says which half.

**5.2** — In `admin_streaming_service.py`, change the mode to a list. **Everything after `node_name, node_output = next(iter(chunk.items()))` is written against an updates chunk**, so the tagged loop must be added around the existing body rather than replacing it.

```python
async for mode, chunk in graph.astream(input_data, config=config, stream_mode=["updates", "messages"]):
    if mode == "updates":
        ...  # the entire existing body, unchanged
    elif mode == "messages":
        ...  # new, and only reached when ADMIN_TOKEN_FRAMES is on
```

With the flag off, the `messages` branch does nothing and behaviour is unchanged. That is the whole safety property of this phase.

**5.3** — In the `messages` branch, filter with **both** tests confirmed in phase 3: `meta.get("langgraph_node") == CHATBOT_NODE and isinstance(msg, AIMessageChunk)`. The node test alone lets through the duplicate final `AIMessage` and every `ToolMessage` from the tools node.

**5.4** — Emit `text_start` on the **first non-empty chunk**, not on entering the branch. This matters: a turn that produces only a tool call must not open an empty text block.

**5.5** — Emit `text_delta` per chunk, extracting text from the **block list** as the services already do at `admin_streaming_service.py` lines 81 to 89. Phase 3 recorded no cumulative chunks, so no length-tracking dedupe is needed.

**5.6** — Emit `text_end` when the block finishes.

**5.7** — In the `updates` branch, when the flag is on, **suppress the `terminal_response` frame** — the answer already went out as deltas. Keep everything else the `updates` branch does: the interrupt, `tools_called`, dedup, outcome tracking.

**5.8** — Emit `status` frames from the `updates` branch using `status_for(tool_name)`, replacing the synthesised `progress` message, only when the flag is on.

**5.9** — Verify with the flag **off**. All three phase-1B captures diff clean.

**5.10** — Verify with the flag **on**:

```
[ ] plain answer      -> text_start, N x text_delta, text_end, done
[ ] answer with tool  -> status, then the text sequence
[ ] concatenated deltas equal the answer exactly, no duplication, no missing space
[ ] interrupt         -> interaction_required, stream ends, resume completes
[ ] hard-fail path    -> answer still arrives (via updates, no tokens)
[ ] recursion limit   -> error path still fires
[ ] outcome log       -> final_response_length still non-zero
```

Line 7 of that list is the one most likely to be quietly wrong. `final_response_length` reads `last_response_text`, which is set in the `updates` branch — if the answer now only arrives as deltas, the only measurement in the system silently goes to zero.

**5.11** — Fix `last_response_text` to accumulate from deltas when the flag is on, and confirm the log again.

**Revert:** set `ADMIN_TOKEN_FRAMES=false`.

### Result — 2026-09-08, all eleven done

One file changed, `streaming/services/admin_streaming_service.py`. `ty` clean; project-wide still 206.

**Flag off, all three captures identical.** Flag on:

| Turn | Frames |
|---|---|
| plain answer | `message_start` · `text_start` · **7 × `text_delta`** · `text_end` · `done` |
| tool answer | `message_start` · `status` · `text_start` · `text_delta` · `text_end` · `done` |
| interrupt | `message_start` · `status` · `interaction_required` · `done` |
| hard fail | `message_start` · **`terminal_response`** · `done` |

`terminal_response` is suppressed on the first three and correctly **not** suppressed on the fourth, which is the whole point of the `lap_streamed_text` guard: the hard-fail message is constructed rather than generated, so it never appears in `messages` mode and has reached the client by no other route.

**The status vocabulary holds.** A leave question produced `{"code": "looking_up_leave"}` and `ask_human` produced `{"code": "working"}` — the fail-closed default, since `ask_human` is deliberately unmapped. No tool name, no argument and no internal identifier appears anywhere on the wire.

**Deltas reconstruct the answer exactly** — 749 characters from seven fragments, ending `...How can I assist you today?`. No duplication, no missing whitespace.

### 5.11 was not needed, and the reason is worth keeping

The task predicted that `final_response_length` would silently fall to zero once the answer stopped arriving as `terminal_response`, since `last_response_text` is set in the `updates` branch.

It did not. Measured with the flag on: **749, 59, 0** — exactly the lengths of the streamed answers.

The prediction assumed the `updates` branch would stop seeing the message. It does not: 5.7 suppresses only the `yield`, and every line above it still runs, so `last_response_text`, `tools_called`, `seen` and the outcome log are all fed as before. Suppressing the emission rather than the processing is what made the measurement survive, and it is the reason to keep that shape if this is ever refactored.

### One design decision taken during the work

**Text blocks close per lap, not per turn.** A lap's `updates` chunk always arrives after all of its `messages` chunks, so that is where `text_end` fires. When Gemini emits a preamble before a tool call — `Let me check your leave balance...` — that becomes its own block, and the final answer becomes another.

The alternative, one block per turn, would have concatenated a transient preamble onto the persistent answer, which is exactly the confusion the contract's channel split exists to prevent.

### A finding that matters more than the phase

**The tool answer streamed as a single delta.** 59 characters, one fragment, no perceptible streaming at all. The plain answer managed seven fragments for 749 characters.

Combined with the coarse chunking already recorded in phase 2, the pattern is that **short answers do not stream in any meaningful sense**, and short answers are common here. Phase 0 is not a formality; it is the task that decides whether phases 4 to 6 were worth doing, and the local evidence is now pointing at borderline.

---

## Phase 6 — The terminator, in the route

**6.1** — In `server/routes/chat.py`, replace `done_event()` with `done_frame(...)` carrying `stop_reason`, `usage` and `iterations`.

This requires the service to hand those values to the route. Simplest form that does not restructure anything: the service yields a final internal marker the route converts, or the route reads them off a small object the service populates. Pick one and write down which.

**6.2** — Include `done.text` — the complete answer — as the transitional field, with the removal criterion from [[03-Stream-Contract]] written into the code comment next to it, not only in the document. The last transitional field in this codebase became permanent because the criterion lived only in prose.

**6.3** — Set `stop_reason` correctly for the interrupt case. The admin service `return`s at line 65, the route still yields a terminator, and it must say `awaiting_input` rather than `completed`.

**6.4** — Convert the two error paths in `admin_streaming_service.py` from `terminal_response` frames to `error` frames with closed codes.

```
RECURSION_LIMIT       -> code "timeout",  partial_output per the existing suppression rule
UNHANDLED_EXCEPTION   -> code "internal", partial_output "discard"
```

**6.5** — Confirm no raw exception text reaches the frame. Both handlers already build fixed user-facing strings, so this is a check rather than a change — but check it, because it is the leak that ships on the first unexpected 500.

**6.6** — Note the existing suppression at lines 134 to 136: a recursion limit hit after a response was already streamed returns silently. Under the new contract that path produces **no terminator at all**, which the client must treat as a failure. Emit `done` with `stop_reason: completed` there instead.

**6.7** — While in the service: `ended_normally` is never set to `True` on the interrupt path, so every HITL turn logs as abnormal. Fix it or record deliberately that an interrupt counts as abnormal. It is the only measurement in the system and it is currently wrong about the most distinctive feature.

**Revert:** restore `done_event()`.

### Result — 2026-09-08, all seven done

Two files changed: `server/routes/chat.py` and `streaming/services/admin_streaming_service.py`. `ty` clean, project-wide still 206.

### 6.1 — how the service hands the terminator to the route

The open question was how `stop_reason`, `usage` and `iterations` reach the route, since only the service knows them. Settled as: **the service emits its own terminator, and the route guarantees one exists.**

```python
last_event: Optional[ServerSentEvent] = None
async for event in turn.stream_fn(**turn.kwargs):
    last_event = event
    yield event

if last_event is None or last_event.event not in TERMINAL_EVENTS:
    yield done_event()
```

No new parameters, no shared mutable object, no sentinel to translate. A service that knows its own outcome emits it; one that does not still gets the legacy frame. **Employee and onboarding are untouched by this** — they never emit `done` or `error`, so they take the fallback branch, which every flag-off admin run exercises byte-identically against the baseline.

### What lands on the wire

| Turn | Frames |
|---|---|
| plain | `message_start` · `text_start` · `text_delta` × N · `text_end` · `done` |
| tool | `message_start` · `status` · `text_start` · `text_delta` × N · `text_end` · `done` |
| interrupt | `message_start` · `status` · `interaction_required` · `done`(`awaiting_input`) |
| resume | `message_start` · `status` × 4 · `text_start` · `text_delta` × 11 · `text_end` · `done` |

Exactly one terminator per stream and no legacy `[DONE]`, confirmed on every capture. A real `done` frame:

```json
{"stop_reason": "completed", "usage": {"input_tokens": 12214, "output_tokens": 799}, "iterations": 3, "text": "..."}
```

### 6.5 verified structurally, which is stronger than a sample

Both `frames.error()` call sites pass a **string literal**. There is no f-string, no `str(e)`, no interpolation of any kind on the path to `message`; the exception reaches only `logger.error(..., exc_info=True)`. Exception text cannot reach the wire, rather than happening not to in the cases tried.

> [!important] The runtime error path was not exercised end to end
> Forcing an unhandled exception by pointing the checkpointer at a missing DynamoDB table killed the app at bootstrap instead, so the request never reached the graph. Every other way of breaking it is caught inside the node and lands on the hard-fail path.
>
> The frame shape is unit-verified and the leak is structurally impossible, but **nobody has seen this frame produced by a real failure.** It is the one gap in the phase.

### 6.7 fixed and measured

Before, every HITL turn logged `tool_outcome: unknown`, `ended_normally: false`. After:

```
"query": "Give me a summary",
"tool_outcome": "awaiting_input",
"ended_normally": true,
```

### A bug this phase found in phase 2

The first `done` frame carried `usage: {"input_tokens": 0, "output_tokens": 0}`.

`stream_primary_llm` rebuilds an `AIMessage` from the accumulated chunk and copies `content`, `tool_calls`, `additional_kwargs` and `response_metadata` — **but not `usage_metadata`**. Confirmed in isolation: a chunk carrying `{'input_tokens': 120, 'output_tokens': 8}` rebuilt to `usage_metadata: None`.

Nothing fails when this happens. Token accounting simply reads zero for every streamed turn, and zero looks like a number rather than a missing one. It would have gone unnoticed until the metering work in item 3 of [[../10-Xarvis-Build-Plan]] tried to bill against it.

Fixed by carrying the field across. Real figures now: **5,916 in / 318 out** for a plain turn, **12,214 / 799** across three laps of a tool turn.

Those input counts are worth noticing on their own. A one-line question costs nearly six thousand input tokens because the admin system prompt plus persona plus policy is resent every lap, and a three-lap turn pays it three times. That is the number the metering and prompt-caching work exists to attack, and it is now measurable per turn without any new instrumentation.

---

## Phase 7 — Cleanup, only after the frontend has shipped

Not part of the same release.

**7.1** — Delete `done.text` once the frontend confirms `text_delta` accumulation is live. Record the date here.

**7.2** — Delete `tool_progress_message()` and `TOOL_PROGRESS_OVERRIDES` from `sse_events.py`.

**7.3** — Remove the `ADMIN_TOKEN_FRAMES` and `ADMIN_STREAM_PRIMARY` flags and the `ainvoke` branch in the node.

**7.4** — Keep the Gemini comment at `admin_streaming_service.py` lines 92 to 95 even though the branch it guards is no longer interesting. It records why the code is ordered as it is.

---

## Deferred, deliberately

| Item | Why not now |
|---|---|
| Employee agent | Strict subset of admin — no interrupt path. Port after admin is proven, mechanically |
| Onboarding agent | Different mechanism entirely (`RequestContext.emit`, `StreamEvent`). Out of scope for the build plan |
| **Deduplicating the two services** | [[02-Token-Streaming]] put this first. **Now it goes last.** Deduping before the frame shape settles means building a shared generator against the old contract and then rewriting it. Dedupe when both audiences are converted and the shared shape is known rather than guessed |
| Reasoning frames | Gemini thought summaries are off by default. The channel is in the contract; turning it on is a config change, not this build |
| Explicit stop endpoint | Open question back to the frontend, contract decision 7 |

---

## One bug found while reading, unrelated to streaming

`employee_streaming_service.py` line 41 to 42:

```python
node_name, node_output = next(iter(chunk.items()))
msgs = node_output.get("messages", [])
```

`admin_streaming_service.py` has a guard the employee service does not:

```python
node_name, node_output = next(iter(chunk.items()))
if not node_output:
    continue
msgs = node_output.get("messages", [])
```

Any employee node returning `None` raises `AttributeError` on `.get`, which the broad `except Exception` converts into a generic UNHANDLED_EXCEPTION frame — so it fails as a user-visible error with a misleading cause. One line, and it is the kind of divergence that deduplication exists to prevent.
