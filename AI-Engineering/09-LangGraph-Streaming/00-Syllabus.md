#langgraph #streaming #agents #lab #syllabus

# 09 · LangGraph Streaming — Syllabus

**11 notes, 114 rungs.** Framework-specific by design — this is one library's API, and it is the folder that will rot first.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — a node returns only when it finishes, therefore a slow node emits nothing, therefore progress must be guessed from outside, therefore the node needs its own channel. Rungs are not topics and not section headings. Eight to fifteen of them build one note.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.** That ordering is the whole design. A list of true statements about stream modes teaches nothing; a chain where every step is the answer to a problem the last step created is what sticks.

> [!important] Three folders, one subject, and this is the middle one
> | Folder | What it owns | Shelf life |
> |---|---|---|
> | [[../08-Streaming-And-SSE/00-Syllabus\|08 · Streaming and SSE]] | the **pipe** — framing, heartbeats, proxies, reconnection | portable, decades old |
> | **09 · LangGraph Streaming** (this) | the **framework** — modes, writers, item shapes, interrupts | perishable, moves every minor release |
> | [[../10-Token-Streaming/00-Syllabus\|10 · Token Streaming]] | the **payload** — what a token is, and what streaming costs you | portable, survives a framework swap |
>
> Read in that order. This folder is deliberately the one that ages, so the other two do not have to.

**Two halves, and the lab is the point.** Notes 1 to 7 are non-token streaming — every mode that works whether or not a model is involved — and note 8 runs them all side by side. Notes 9 and 10 are token streaming through the framework, and note 11 runs that. **Notes 9 to 11 assume folder 10 notes 1 to 3**, because `messages` mode cannot be understood before a token is.

> [!important] Version decides the shape of every example here
> `astream` takes a `version` parameter. It defaults to **v1**, which yields `(mode, data)` tuples. **v2** yields typed `StreamPart` dicts you switch on with `chunk["type"]` — `ValuesStreamPart`, `UpdatesStreamPart` and five more.
>
> The parameter **does not exist at all before 1.1.0**, released 2026-03-10. On the whole 1.0 line there is no choice to make and no v2 to reach for, so crossing that boundary adds an option rather than changing a default. **This is why the shape material is not taught in note 6** — none of it can be run on the installed stack, so it waits for the upgrade and gets its own note there.

**Currency check (2026-09-09):** written against **langgraph 1.0.10**, which has no `version` parameter at all. Latest is 1.2.11, where it defaults to v1. Verified today against both wheels: `TAG_NOSTREAM` still exists, and `get_stream_writer()` still carries the Python 3.11 restriction in async code. Re-verify whether `version` still defaults to v1 when the upgrade note is written.

---

## How to teach from this

**One note per session, rungs in order, never skipping.** A skipped rung breaks the chain — the next one stops being a discovery and becomes a fact to memorise.

**This folder is run, not read.** Every mode here produces output you can print. A rung claiming what a mode yields, believed rather than observed, is worth nothing — the shapes differ from the documentation often enough that the run is the source of truth.

**Notes 8 and 11 are labs and are not optional.** They are where the modes stop being a list and become a shape you recognise.

**Recall is per note, from memory, file closed.** Recognising an answer does not count.

**Spacing:** re-test notes 1 to 6 after the first lab, and everything after the second.

---

## The lab

A small graph, in its own project, that you can break freely — not Xarvis. `projects/python-lab` already has uv configured and is the obvious home, but a separate `langgraph-lab` keeps the pytest material clean.

The graph needs exactly three things and no more: **a node that returns state**, **a node that calls a model**, and **a node that pauses on an interrupt**. Everything in notes 1 to 9 can be demonstrated on that.

---

## Note 1 · The Graph Does Not Return, It Emits

10 rungs. No break — this is framing.

1. A graph run is a loop over nodes, not a single function call.
2. `invoke()` runs the whole loop and hands back the final state.
3. **Break it** — an agent loop can run twenty laps over thirty seconds, and `invoke` gives you nothing at all until the last one finishes.
4. So the interior of the run has structure worth exposing: which node ran, what it changed, what the model said, how far along it is.
5. `stream()` and `astream()` yield while the loop is still running.
6. **Break the assumption that there is one obvious thing to yield** — full state, only the changes, model tokens, and your own progress messages are four different answers, all reasonable.
7. So there is a `stream_mode` parameter rather than a single stream shape.
8. The modes are not alternatives: `stream_mode` accepts a list, and each yielded item is tagged with which mode produced it.
9. The unit is the **step**, not the node — a step is the set of nodes with nothing left to wait for, so wiring decides how many there are, and updates from one step arrive separately within it.
10. It is a generator, so nothing runs until something consumes it, and abandoning the loop abandons the run.

> **Recall:** What does `invoke` discard that streaming keeps? · Why is there a mode parameter instead of one stream shape? · What is the unit of a step, and why is it not the node?

---

## Note 2 · values And updates

11 rungs. **Break:** run the same graph twice, once with each mode, and diff the output.

1. `values` yields the **complete state** after each step.
2. `updates` yields **only what the node returned**, keyed by node name.
3. So `values` gives you `{"messages": [...], "actor": {...}, ...}` and `updates` gives you `{"chatbot": {"messages": [...]}}`.
4. **Break `values`** — to know what actually changed you must diff against the previous snapshot yourself, and the snapshot grows with the conversation.
5. **Break `updates`** — it tells you what the node returned, not what the state became, so a reducer that merges or appends means the two disagree.
6. That disagreement is the entire distinction: `values` is state, `updates` is intent.
7. Multiple updates within one step arrive as separate items rather than merged.
8. A node returning nothing still produces an update, so the item count follows the nodes rather than the changes — but the payload is `None`, and a node returning `{}` is normalised to `None` too, so a consumer that indexes into the payload crashes on both.
9. **Neither mode carries model tokens** — both fire only when a node has finished.
10. So a system built entirely on `updates` delivers whole messages, which is exactly what most agents ship first and why they feel like they are not streaming.
11. `values` suits a UI that re-renders from state; `updates` suits one that reacts to what a node did.

> **Recall:** What does `updates` give you that `values` does not, and vice versa? · When do the two disagree, and why? · Why does a system built on `updates` feel unstreamed?
>
> **Stop:** One appending reducer is used as apparatus and never explained past what the demonstration needs. No catalogue of reducers, no channel internals, no designing them — that is state design, not streaming.

---

## Note 3 · custom, The Channel You Control

10 rungs. **Break:** put a three-second sleep inside a node and watch the stream stay silent.

1. Both state modes fire when a node **returns**.
2. **Break it** — a node making three API calls over eight seconds emits nothing for eight seconds, then everything at once.
3. So anything the user sees during that gap must be invented outside the node.
4. Which is how a streaming layer ends up deriving progress from tool names, guessing at work it cannot see.
5. `get_stream_writer()` inside a node returns a function that emits immediately, mid-node.
6. `writer({"status": "fetching"})` reaches the consumer before the node has returned anything.
7. So the code that knows what it is doing says so, instead of being guessed at from outside.
8. The payload has no schema — it is whatever dictionary you pass, which is freedom and a versioning problem in equal measure.
9. `custom` must be among the requested modes or the writes are silently discarded.
10. This is the correct home for a closed status vocabulary, because the mapping from work to user-visible code is made where the work happens.

> **Recall:** What does a slow node emit before it returns, and what follows from that? · What does `get_stream_writer` change about where progress is decided? · When does a `writer` call silently produce nothing?

---

## Note 4 · tasks, checkpoints And debug

4 rungs. **Break:** stream `checkpoints` on a graph compiled without a checkpointer and count what comes out.

1. `tasks` fires at task start and finish, carrying results and errors.
2. `checkpoints` fires at checkpoint boundaries, in the same shape `get_state()` returns.
3. `checkpoints` **requires a checkpointer** and yields nothing whatsoever without one. `tasks` does not — it works on a bare `compile()`.
4. `debug` combines both and adds metadata, so without a checkpointer it does not fail either — it silently drops to the half it can still produce.

> **Recall:** What are the two records `tasks` emits for one node, and what joins them? · Which mode needs a checkpointer, what does it yield without one, and what does `debug` do instead of failing? · What does the `debug` envelope carry that neither of the other two does?
>
> **Stop:** This note is the three shapes and nothing else. What the modes are for, where an exception surfaces, and what survives a crash all belong to the next one.

---

## Note 5 · Not For The Client

9 rungs. **Break:** raise an exception inside a node and watch which mode shows it.

1. **Break the assumption that these are more of the same** — they are not for the client, they are for you.
2. An exception inside a node is visible in `tasks` before any error handling has decided what the user sees.
3. `checkpoints` is what a resumable UI would be built on, because it exposes the same object a resume reads.
4. A node's output is written the moment that node **returns**, not when the step commits — so a step killed halfway keeps the part that finished, and a resume replays it marked as cached rather than running it again.
5. **Break the assumption that this is a guarantee** — it is a setting. `durability` defaults to `"async"`, and `"exit"` writes only on a clean finish, so a process that is killed leaves nothing at all behind.
6. And it only ever protects **return values**: a side effect a node performed before dying is invisible to the checkpoint, so the resume runs that node again from the top and does it twice.
7. `debug` is a firehose: right for one bug, unusable as a habit, and expensive to leave on.
8. So the modes split by audience — `values`, `updates`, `messages`, `custom` face the client; `tasks`, `checkpoints`, `debug` face the operator.
9. Which is also a security line: operator modes carry internal names and payloads that must never be forwarded to a browser.

> **Recall:** Where does a node's exception first become visible? · A step is killed with one of its two nodes finished — what survives, and what must `durability` be for that to hold? · What is the audience split, and why is it also a security boundary?

---

## Note 6 · Combining Modes, And Reading The Item

9 rungs. **Break:** request two modes, print the raw item, and see whether it is a dict or a tuple.

1. `stream_mode` accepts a list, and every item comes back tagged — a list of **one** already changes the shape, so it is the brackets and not the count that does it.
2. **Break your consumer** — string against list is not a mode change, and the same typo raises on `updates` while unpacking silently on `values`, because one is keyed by node and the other by state field.
3. A graph can contain another compiled graph, wired in as an ordinary node.
4. **Break it** — the subgraph does all the work and streams one item named after the node it is wired in as, so its interior is invisible from outside.
5. `subgraphs=True` includes that interior, prefixing every item with a namespace.
6. The namespace is a tuple — `()` is the root graph, `('lookup:<task id>',)` is the node the subgraph is running under.
7. So an item's arity is decided by two independent flags: one element, two, or three, and neither flag mentions the other in its own documentation.
8. Combining modes is additive, never merged: two modes produce two independent series of items interleaved in time, each series exactly what it would have been alone.
9. So requesting more modes never changes what an existing mode yields, which makes the migration shape always the same — add the new mode, ignore it, then start using it.

> **Recall:** Why does a list of one mode change the item shape? · What is invisible without `subgraphs=True`, and what does it look like from outside? · Why is adding a mode a safe change?

> [!note] The v1 and v2 item shapes are deliberately not here
> An earlier draft of this note taught the `(mode, data)` tuple against the `StreamPart` dict, switched on by a `version` parameter. The installed stack is 1.0.10, which has no `version` parameter and no `StreamPart` anywhere in the package, so none of it could be run. It moves to its own note, written alongside the Xarvis LangGraph upgrade, where the change is real and testable rather than described.

---

## Note 7 · Where The Interrupt Arrives

13 rungs. **Break:** interrupt a graph, print the raw item, and look for where it landed.

1. An interrupt pauses the graph **inside** a node, before it has returned.
2. It is not a return value, and the exception it does raise never reaches the caller — so neither error handling nor node output will show it.
3. **Break it from inside the node** — `GraphInterrupt` inherits from `Exception`, so a defensive `except Exception` around the `interrupt()` call swallows the pause and completes the turn with a wrong answer and no symptom.
4. It surfaces in `updates` under the key `__interrupt__`, as an item of its own.
5. **Break the node-name consumer** — code that reads the first key as a node name sees `__interrupt__` as if it were one, and the payload under it is a tuple rather than an update dict.
6. It arrives in `values` too, under the same key, but riding on a state item rather than alone — so the key is stable across modes and the shape around it is not.
7. The payload is a **tuple** of `Interrupt` objects, each carrying `.value` and `.id`, so reaching the question a node asked is two unwrappings deep and neither is suggested by the key.
8. Requesting several modes does not move it — it arrives in **every** mode that carries it, twice over for `updates` plus `values`, with one shared `.id` that is the only way to dedupe.
9. Once it arrives, **the stream ends**, while the graph still has a pending task — so the interrupt item is the only thing distinguishing a pause from a completed turn.
10. Resuming is a new run with a resume command, and it does not replay: the new stream picks up at the pending node.
11. So a paused turn is two streams rather than one interrupted stream, and every per-stream quantity starts again.
12. **Break the tuple intuition** — two nodes interrupting in the same step produce **two items of length 1**, not one item of length 2.
13. And with two pending, `Command(resume=value)` **raises**: the answers must be a map from interrupt id to value, which is what `.id` is really for.

> **Recall:** Why do neither error handling nor node output reveal an interrupt? · What key does it arrive under, and how does its shape differ between `updates` and `values`? · What are the two jobs `.id` does, and which one is mandatory?

> [!note] The `interrupts` field is not part of this note either
> An earlier draft had the interrupt moving to a `values` field named `interrupts` under a v2 item shape. Measured on 1.0.10, it is already in `values`, under `__interrupt__`, the same key `updates` uses — nothing moved and no `interrupts` field exists here. Whatever the later versions do with it belongs in the upgrade note, alongside the v1 and v2 shapes cut from note 6.

---

## Note 8 · Lab — Every Mode, Side By Side

11 rungs. **This note is entirely a run.** One graph held still, five questions, six modes, five tables.

1. One graph, three nodes, half a second of work each, writer calls in the first and third — the value of the note is entirely in the controls.
2. Run it once per mode and record items, first arrival, last arrival and bytes.
3. `updates` is the **only** mode silent while the first node works; every other mode has something on the wire before any node returns.
4. The cost order is the reverse of the usefulness order on a screen — `custom` is the cheapest at 102 bytes and the only mode carrying words written for a human.
5. Every item is a `dict`, and the keys are the mode: three keyed by names you chose, three keyed by the framework.
6. `checkpoints` yields **zero** without a checkpointer and `debug` silently halves; `tasks`, `values`, `updates` and `custom` need nothing.
7. **Break every mode at once** — a node throws, and not one of the six carries the error.
8. Set a `step_timeout` and only `tasks` and `debug` gain the error record; no client mode ever does.
9. Every mode loses items at a subgraph boundary, `custom` most starkly at zero against one.
10. Write it all down in one table. **That table is the note.**
11. `messages` is the seventh mode and the one this note cannot measure, because it yields nothing unless a node calls a model.

> **Recall:** From the table alone, name the mode for: a progress bar · a resumable UI · reacting to one node · debugging a node that throws.

---

## Note 9 · messages Mode

13 rungs. Needs a provider. **Break:** point the node at a model with streaming disabled and watch the mode collapse to one item.

1. `messages` yields 2-tuples of `(message_chunk, metadata)` — a tuple with a **single** mode requested, unlike every other mode.
2. The answer is the fragments concatenated in arrival order; no index, no reassembly.
3. On a reasoning model the first fragments carry **empty** `content`, with the words in `additional_kwargs["reasoning_content"]`.
4. **Break the assumption that the node decides** — a node calling `invoke` still streams, because requesting the mode attaches a `_StreamingCallbackHandler` and `chat_models.py` checks for exactly that.
5. **Break it properly** — `disable_streaming=True` on the model yields **one** item, and an `AIMessage` rather than an `AIMessageChunk`, while `updates` is identical either way.
6. `metadata["langgraph_node"]` says which node, `metadata["tags"]` says which call — 13 keys repeated on every fragment.
7. The `nostream` tag suppresses a call's fragments at the source while the call still runs and still produces output, which beats filtering at the consumer.
8. `messages` has a **second source**: the handler also emits node outputs, deduped by message id.
9. **Break the dedupe** — a node returning a newly built `AIMessage` has an id nothing has seen, so the complete answer is republished and renders twice, invisibly to every other mode.
10. **Break the node filter** — a `ToolMessage` from the tools node is a message, so raw internal output renders in front of the user.
11. So the filter is a conjunction: right node **and** right object type, because node name admits the republished message and type admits the wrong node's fragments.
12. Tool calls arrive here too, and **how** they fragment is the provider's choice — Groq sends one chunk with complete `args` and `index` of `0`.
13. Therefore accumulate with `+` and read `tool_calls` off the sum, which is correct for one chunk or forty, and never touches `index`.

> **Recall:** Why does asking for the mode change how a node's `invoke` runs? · What are the two things a node-name filter wrongly admits, and why does each defeat a different single condition? · Which parts of this note are LangGraph's and which are the provider's?

---

## Note 10 · astream Versus astream_events

12 rungs. Judgement — defend the choice, do not recall it.

1. There is a second streaming API, and it is not a variant of the first — different method, different shape, different loop.
2. An `astream` item is a tuple; an event is a **dict of seven keys**, an envelope with `event`, `data` and where it came from.
3. `astream_events` yields lifecycle events for **every runnable** in the run — measured, 3 `updates` items against **83 events** on one turn.
4. Everything callable is a runnable, including your conditional edge function, which reports a start and an end.
5. Both carry the same tokens, and **no line of the consumer survives the move** between them.
6. **Break the late switch** — the unpacking, the type test and the payload path all differ, so choosing wrongly means rewriting rather than adjusting.
7. The one thing only events give: a **tool start, by name and arguments, before the tool returns**. No mode exposes that.
8. The `version` parameter defaults to `v2`, so the widely copied `version="v2"` changes nothing; `v1` warns that it is deprecated.
9. **Break v3** — it raises on a graph, and the message names `CompiledGraph` as supported while `compile()` hands you a `CompiledStateGraph`.
10. `stream_events` refuses `v1` and `v2` and points at `v3`, which a graph cannot use, so **on a graph, events are asynchronous or nothing**.
11. So two parameters named `version` sit on the two APIs, taking values that look alike and meaning unrelated things.
12. Therefore the choice has a shelf life, and the **reason** for it goes in a comment next to the consumer, naming what the other API could not give.

> **Defend:** Your UI needs tokens, tool starts, and a progress bar. Argue for one API over the other. · You are on 1.0.10 today and 1.2 is coming. Which do you pick, and what do you write down? · Somebody's code passes `version="v2"`. Which API is it calling, and does the argument change anything?

---

## Note 11 · Lab — Tokens Through The Graph

12 rungs. **This note is entirely a run**, and it is where notes 9 and folder 10 meet.

1. One graph carrying every problem at once — a tool call, a model, a deliberate duplicate.
2. **Three kinds of object on one channel**: `AIMessageChunk`, `AIMessage`, `ToolMessage`, from two nodes.
3. Five counts that are all different: items, fragments, fragments with text, characters, billed tokens.
4. Most fragments carry **no text** — the reasoning pass, billed and invisible, which is why a stream looks slow at the start.
5. Find a duplicate you did not write: assemble the fragments, compare against every whole message from that node.
6. Fold the fragments and the result is still an `AIMessageChunk`.
7. **Break the obvious filter** — `AIMessageChunk` subclasses `AIMessage`, so `isinstance(x, AIMessage)` is `True` for both and discriminates nothing.
8. **Break the fold** — across two model calls it concatenates strings, turning `finish_reason` into `tool_callsstop` and the model name into itself twice.
9. A rebuilt `AIMessage` loses `usage_metadata` and `response_metadata`, so cost tracking records nothing and it looks like zero rather than an error.
10. With both modes on, **every fragment for a node arrives before that node's update**, which makes the update a usable end-of-node marker.
11. An interrupt with both modes on lands on `updates` and `messages` yields nothing, so interrupt handling cannot live in the fragment consumer.
12. Write down the copies of the answer and the ordering rule. **That is the note.**

> **Recall:** How many copies of the answer exist and in what shapes? · What does the fold return, and what are the two things wrong with it? · What ordering does a node's update have relative to its fragments, and why?

---

## Coverage

Note files are numbered to match this list — note 3 is `03-Custom-Channel.md`.

| Note | Rungs | Written |
|---|---|---|
| 1 · The Graph Does Not Return, It Emits | 10 | **yes** |
| 2 · values And updates | 11 | **yes** |
| 3 · custom, The Channel You Control | 10 | **yes** |
| 4 · tasks, checkpoints And debug | 4 | **yes** |
| 5 · Not For The Client | 9 | **yes** |
| 6 · Combining Modes, And Reading The Item | 9 | **yes** |
| 7 · Where The Interrupt Arrives | 13 | **yes** |
| 8 · Lab — Every Mode, Side By Side | 11 | **yes** |
| 9 · messages Mode | 13 | **yes** |
| 10 · astream Versus astream_events | 12 | **yes** |
| 11 · Lab — Tokens Through The Graph | 12 | **yes** |

---

## Deferred

| Topic | Goes to |
|---|---|
| SSE framing, heartbeats, proxies, reconnection | [[../08-Streaming-And-SSE/00-Syllabus\|08 · Streaming and SSE]] |
| What a token is, decoding, chunk against token, cost | [[../10-Token-Streaming/00-Syllabus\|10 · Token Streaming]] |
| Rendering half-written markdown, moderating a stream | [[../10-Token-Streaming/00-Syllabus\|10 · Token Streaming]] notes 8 and 9 |
| Graph construction, reducers, state channel design | outside this folder — this is streaming only |
| Checkpointer backends, TTL, resume semantics | `06-Agent-Reliability` |
| Async generators and closing one early | `00-Python-Utils/04-Generators-And-Iterators` |

---

## Where this shows up in Xarvis

The admin agent ran on `stream_mode="updates"` alone from the beginning, which is note 2 rung 10 exactly — whole messages, and a fake typing animation in front of them to make it look otherwise.

**Note 9 rung 4 is the expensive one, and it was learned the hard way twice.** The admin node calls the non-streaming method, and the build doc concluded from that — plus a true reading of the provider, whose two methods share nothing — that `messages` mode could produce no tokens. Measured on 2026-09-10: the check is one layer above the provider and turns purely on whether a handler is attached, so the call streams the moment the mode is requested. A single item on the mode is not evidence either way, because rung 8's second source produces exactly one with no tokens involved.

**Note 9 rungs 8 to 10 were paid for in production code.** The answer arrived three times — fragments, then the republished complete message on the same channel, then a third copy through `updates`. The conjunction filter is what fixed it.

**Note 3 is unbuilt and should be.** Progress is still synthesised from tool names in `sse_events.py` rather than emitted by the node that knows. `get_stream_writer()` is the correct home for the status vocabulary already specified in `Current-Standing/TODO/03-Stream-Contract.md`.

**Note 7 rung 5 is already paid for in the onboarding driver.** `_graph_driver` unwraps the payload with `isinstance(raw_interrupt, (list, tuple))` and then `hasattr(raw_interrupt, "value")` — two guards that are exactly the tuple and the `Interrupt` object, written by someone who met them the hard way rather than from the docs.

**Note 7 rung 3 is an open question there.** Any node that calls `interrupt()` inside a broad `except Exception` swallows the pause, and the turn completes with no symptom. Worth a grep during the upgrade session rather than an assumption.

**The upgrade gets its own note, written when it happens.** The stack is 1.0.10, so the loop unpacks tuples because nothing else is on offer, and the v2 item shape cannot be demonstrated on anything installed here. Moving the version is recorded in `Current-Standing/TODO/05-Streaming-Build.md` phase 1, and the note comes with it.

---

## Interview hooks

The one that separates people who have used it from people who have read about it: **how do you show progress from inside a node that takes eight seconds** (note 3, and the answer is a writer, not a heuristic over tool names).

The one that catches everybody: **if you turn on two stream modes, how many times does the answer arrive** (note 9, and the answer is three).

The design question: **when would you use `astream_events` over `astream`** (note 10, and a good answer includes that the choice has a shelf life).

---

## Sources to verify against

- [LangGraph — Streaming](https://docs.langchain.com/oss/python/langgraph/streaming), the mode reference and the `nostream` tag
- [LangGraph `astream` reference](https://reference.langchain.com/python/langgraph/pregel/main/Pregel/astream)
- [`astream_events` reference](https://reference.langchain.com/python/langchain-core/runnables/base/Runnable/astream_events)
- [LangGraph 1.0 general availability](https://changelog.langchain.com/announcements/langgraph-1-0-is-now-generally-available) for the version boundaries
- [Issue 4853 — tool call name and id across chunks](https://github.com/langchain-ai/langgraph/issues/4853) for note 9 rungs 11 and 12
