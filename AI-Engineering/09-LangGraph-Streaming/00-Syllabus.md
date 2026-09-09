#langgraph #streaming #agents #lab #syllabus

# 09 · LangGraph Streaming — Syllabus

**10 notes, 108 rungs.** Framework-specific by design — this is one library's API, and it is the folder that will rot first.

> A rung is the **smallest thing that has to be understood before the next thing makes sense** — a node returns only when it finishes, therefore a slow node emits nothing, therefore progress must be guessed from outside, therefore the node needs its own channel. Rungs are not topics and not section headings. Eight to fifteen of them build one note.
>
> They are ordered so that **each rung either breaks the previous one or is forced by it.** That ordering is the whole design. A list of true statements about stream modes teaches nothing; a chain where every step is the answer to a problem the last step created is what sticks.

> [!important] Three folders, one subject, and this is the middle one
> | Folder | What it owns | Shelf life |
> |---|---|---|
> | [[../08-Streaming-And-SSE/00-Syllabus\|08 · Streaming and SSE]] | the **pipe** — framing, heartbeats, proxies, reconnection | portable, decades old |
> | **09 · LangGraph Streaming** (this) | the **framework** — modes, writers, chunk shapes, interrupts | perishable, moves every minor release |
> | [[../10-Token-Streaming/00-Syllabus\|10 · Token Streaming]] | the **payload** — what a token is, and what streaming costs you | portable, survives a framework swap |
>
> Read in that order. This folder is deliberately the one that ages, so the other two do not have to.

**Two halves, and the lab is the point.** Notes 1 to 6 are non-token streaming — every mode that works whether or not a model is involved — and note 7 runs them all side by side. Notes 8 and 9 are token streaming through the framework, and note 10 runs that. **Notes 8 to 10 assume folder 10 notes 1 to 3**, because `messages` mode cannot be understood before a token is.

> [!important] Version decides the shape of every example here
> `stream_version` defaults to **v1**, which yields `(mode, data)` tuples. **v2**, requiring 1.1 or later, yields `StreamPart` dicts you switch on with `chunk["type"]`. Typed projections arrive in 1.2 and supersede both.
>
> So the same three-line loop is written three different ways depending on a version you may not have chosen deliberately. **Check yours before running any rung in note 5.**

**Currency check (2026-09-08):** written against **langgraph 1.0.5**, which is v1-default. Latest is 1.2.11. Re-verify before relying on: whether `stream_version` still defaults to v1, whether `get_stream_writer()` still needs Python 3.11 for async, and whether the `nostream` tag still exists.

---

## How to teach from this

**One note per session, rungs in order, never skipping.** A skipped rung breaks the chain — the next one stops being a discovery and becomes a fact to memorise.

**This folder is run, not read.** Every mode here produces output you can print. A rung claiming what a mode yields, believed rather than observed, is worth nothing — the shapes differ from the documentation often enough that the run is the source of truth.

**Notes 7 and 10 are labs and are not optional.** They are where the modes stop being a list and become a shape you recognise.

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
9. The unit is the **step**, not the node — nodes running in parallel belong to one step, and their updates arrive separately within it.
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
8. A node returning nothing produces an update with an empty payload, which is not the same as no update at all.
9. **Neither mode carries model tokens** — both fire only when a node has finished.
10. So a system built entirely on `updates` delivers whole messages, which is exactly what most agents ship first and why they feel like they are not streaming.
11. `values` suits a UI that re-renders from state; `updates` suits one that reacts to what a node did.

> **Recall:** What does `updates` give you that `values` does not, and vice versa? · When do the two disagree, and why? · Why does a system built on `updates` feel unstreamed?
>
> **Stop:** No reducer semantics or channel internals — that is state design, not streaming.

---

## Note 3 · custom, The Channel You Control

11 rungs. **Break:** put a three-second sleep inside a node and watch the stream stay silent.

1. Both state modes fire when a node **returns**.
2. **Break it** — a node making three API calls over eight seconds emits nothing for eight seconds, then everything at once.
3. So anything the user sees during that gap must be invented outside the node.
4. Which is how a streaming layer ends up deriving progress from tool names, guessing at work it cannot see.
5. `get_stream_writer()` inside a node returns a function that emits immediately, mid-node.
6. `writer({"status": "fetching"})` reaches the consumer before the node has returned anything.
7. So the code that knows what it is doing says so, instead of being guessed at from outside.
8. The payload has no schema — it is whatever dictionary you pass, which is freedom and a versioning problem in equal measure.
9. **Break it on old Python** — in async code below 3.11 `get_stream_writer()` does not work, and the node must accept `writer: StreamWriter` as a parameter instead.
10. `custom` must be among the requested modes or the writes are silently discarded.
11. This is the correct home for a closed status vocabulary, because the mapping from work to user-visible code is made where the work happens.

> **Recall:** What does a slow node emit before it returns, and what follows from that? · What does `get_stream_writer` change about where progress is decided? · What are the two ways a `writer` call can silently produce nothing?

---

## Note 4 · tasks, checkpoints And debug

10 rungs. **Break:** raise an exception inside a node and watch which mode shows it.

1. `tasks` fires at task start and finish, carrying results and errors.
2. `checkpoints` fires at checkpoint boundaries, in the same shape `get_state()` returns.
3. Both **require a checkpointer** and yield nothing without one.
4. `debug` combines both and adds metadata.
5. **Break the assumption that these are more of the same** — they are not for the client, they are for you.
6. An exception inside a node is visible in `tasks` before any error handling has decided what the user sees.
7. `checkpoints` is what a resumable UI would be built on, because it exposes the same object a resume reads.
8. `debug` is a firehose: right for one bug, unusable as a habit, and expensive to leave on.
9. So the modes split by audience — `values`, `updates`, `messages`, `custom` face the client; `tasks`, `checkpoints`, `debug` face the operator.
10. Which is also a security line: operator modes carry internal names and payloads that must never be forwarded to a browser.

> **Recall:** Which two modes need a checkpointer, and what do they yield without one? · Where does a node's exception first become visible? · What is the audience split, and why is it also a security boundary?

---

## Note 5 · Combining Modes, And Reading The Chunk

12 rungs. **Break:** request two modes, print the raw item, and see whether it is a tuple or a dict.

1. `stream_mode` accepts a list, and every item comes back tagged.
2. In **v1** each item is a `(mode, data)` tuple, unpacked positionally.
3. In **v2** each item is a `StreamPart` dict — `{"type", "ns", "data"}` — switched on by `chunk["type"]`.
4. **Break your consumer** — the loop is written differently for each, and `stream_version` defaults to v1, so the shape depends on a choice you may never have made.
5. Which means an upgrade can change the streaming loop while nothing else in the code moves.
6. `ns` is the namespace: an empty tuple means the root graph.
7. A graph can contain subgraphs, and by default their interior is invisible.
8. **Break it** — a subgraph doing all the work streams nothing, and the parent looks like it hangs.
9. `subgraphs=True` includes them, and `ns` identifies which one, as a tuple of node and task id.
10. Combining modes is additive, never merged: two modes produce two independent series of items interleaved in time.
11. So requesting more modes never changes what an existing mode yields — which is what makes adding one a safe change.
12. Therefore the migration shape is always the same: add the new mode, ignore it, then start using it.

> **Recall:** What are the two chunk shapes and which version gives which? · What is invisible without `subgraphs=True`, and what does it look like from outside? · Why is adding a mode a safe change?

---

## Note 6 · Where The Interrupt Arrives

10 rungs. **Break:** interrupt a graph, print the raw chunk, and look for where it landed.

1. An interrupt pauses the graph **inside** a node, before it has returned.
2. It is not an exception and not a return value, so neither error handling nor node output will show it.
3. In **v1** it surfaces in `updates` under the key `__interrupt__`.
4. **Break the node-name consumer** — code that reads the first key as a node name sees `__interrupt__` as if it were one.
5. In **v2** it moves, arriving in `values` under an `interrupts` field.
6. So the interrupt is the single most version-sensitive thing in this folder, and it is also the most valuable to get right.
7. Requesting several modes does **not** change where it arrives — worth verifying rather than trusting, because a missed interrupt looks like a hung stream.
8. Once it arrives, **the stream ends**. Nothing further comes down that connection.
9. Resuming is a new run with a resume command, producing a new stream from the start.
10. So a paused turn is two streams rather than one interrupted stream, and any per-stream counter starts again.

> **Recall:** Why do neither error handling nor node output reveal an interrupt? · Where does it arrive in v1, and in v2? · What happens to the stream after it, and what does that mean for a resume?

---

## Note 7 · Lab — Every Mode, Side By Side

10 rungs. **This note is entirely a run.** One script, one graph, one question, seven printed outputs.

1. Build the three-node graph — state node, model node, interrupt node.
2. Run it seven times, once per mode, printing every item raw and unmodified.
3. Record, per mode: how many items, when the first arrives, and the shape of one item.
4. Confirm `values` grows and `updates` does not.
5. Confirm both are silent while a node with a sleep is running, and that `custom` is not.
6. Confirm `tasks` and `checkpoints` yield nothing without a checkpointer, then add one and confirm they do.
7. Raise inside a node; find which modes carry it and which stay silent.
8. Request `["updates", "custom"]` and confirm each item is tagged and neither series is altered.
9. Add a subgraph, run without `subgraphs=True`, then with it, and compare.
10. Write the seven shapes down in one table. **That table is the note.**

> **Recall:** From the table alone, name the mode for: a progress bar · a resumable UI · reacting to one node · debugging a node that throws.

---

## Note 8 · messages Mode

13 rungs. Assumes folder 10 notes 1 to 3. **Break:** point the node at a non-streaming model call and watch the mode go quiet.

1. `messages` yields 2-tuples of `(message_chunk, metadata)`.
2. It works by **intercepting model callbacks**, not by reading what a node returned.
3. **Break it** — a node calling the non-streaming method produces no callbacks, so the mode yields one item containing everything, and looks merely coarse rather than broken.
4. So `messages` is the only mode whose output depends on how the node calls the model, not on the graph.
5. `metadata["langgraph_node"]` says which node produced the chunk.
6. `metadata["tags"]` carries tags set on the model call, so a tag can select or exclude a source.
7. The `nostream` tag suppresses a call's tokens while the call still runs and still produces output.
8. **Break the node filter** — filtering on node name alone also admits every `ToolMessage` from the tools node, putting raw internal output in front of the user.
9. And it admits the complete message the framework republishes on the same channel after the fragments, which renders the answer twice.
10. So the filter is a conjunction: right node **and** right object type, tested with `isinstance` against the chunk class.
11. Tool arguments stream too, as `tool_call_chunks`, with name and id complete on the first chunk.
12. **Break the index assumption** — `index` may be `None` rather than `0`, so grouping fragments by index needs a fallback.
13. Therefore `messages` is the mode that most rewards printing before believing.

> **Recall:** Why is `messages` the only mode that depends on how the node calls the model? · What are the two things a node-name filter wrongly admits? · What is complete on the first tool chunk and what streams?

---

## Note 9 · astream Versus astream_events

10 rungs. Judgement — defend the choice, do not recall it.

1. There is a second streaming API, and it is not a variant of the first.
2. `astream` yields the **graph's own views**, selected by mode.
3. `astream_events` yields **lifecycle events for every runnable** in the run — model starts, tool starts, chain ends.
4. So one is a small set of curated projections and the other is a firehose you filter.
5. Token streaming exists in both: `messages` mode, or the `on_chat_model_stream` event.
6. `version="v2"` is required for graphs, and v1 returns empty parent ids.
7. **Break the late switch** — the two consumers look nothing alike, so choosing wrongly means rewriting rather than adjusting.
8. The rule of thumb: if the graph's own views answer your question, use `astream`; reach for events only when you need something no mode exposes.
9. In 1.2 and later, typed projections supersede both, giving independent iterators per projection instead of one branching loop.
10. Therefore this choice has a shelf life, and the reason for it should be written down where the next person will see it.

> **Defend:** Your UI needs tokens, tool starts, and a progress bar. Argue for one API over the other. · You are on 1.0.5 today and 1.2 is coming. Which do you pick, and what do you write down?

---

## Note 10 · Lab — Tokens Through The Graph

11 rungs. **This note is entirely a run**, and it is where notes 8 and folder 10 meet.

1. Point the model node at the streaming call. Confirm `messages` produces many items rather than one.
2. Count items against the reported output-token count. They will not match.
3. Print `type(msg).__name__` for every item and find the one that is not a chunk.
4. Sum the text of the fragments, then compare against the length of that non-chunk item. Equal means you have found the duplicate.
5. Add a tool call and watch `ToolMessage` arrive on the same channel.
6. Apply the conjunction filter from note 8 rung 10 and confirm all three exclusions at once.
7. Fold the fragments into one message, then check `type(...)` and the message-kind field on the result.
8. Check `usage_metadata` on the folded result. If you rebuilt the message, check it again.
9. Request `["updates", "messages"]` together and confirm the ordering: every fragment for a node arrives before that node's update.
10. Trigger the interrupt with both modes on and confirm it still arrives where note 6 says.
11. Write down the item count, the number of copies of the answer, and the ordering rule. **That is the note.**

> **Recall:** How many copies of the answer exist and on which channels? · What does the fold return, and what is wrong with it? · What ordering does a node's update have relative to its fragments?

---

## Coverage

None written yet. Note files will be numbered to match this list — note 3 becomes `03-Custom-Channel.md`.

| Note | Rungs | Written |
|---|---|---|
| 1 · The Graph Does Not Return, It Emits | 10 | no |
| 2 · values And updates | 11 | no |
| 3 · custom, The Channel You Control | 11 | no |
| 4 · tasks, checkpoints And debug | 10 | no |
| 5 · Combining Modes, And Reading The Chunk | 12 | no |
| 6 · Where The Interrupt Arrives | 10 | no |
| 7 · Lab — Every Mode, Side By Side | 10 | no |
| 8 · messages Mode | 13 | no |
| 9 · astream Versus astream_events | 10 | no |
| 10 · Lab — Tokens Through The Graph | 11 | no |

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

**Note 8 is the expensive one.** The node called the non-streaming method, so `messages` mode would have yielded a single item and the honest conclusion would have been that token streaming does not work in this framework. Rung 3 is that mistake, avoided by reading the provider adapter first.

**Note 8 rungs 8 to 10 were paid for in production code.** The answer arrived three times — fragments, then the republished complete message on the same channel, then a third copy through `updates`. The conjunction filter is what fixed it.

**Note 3 is unbuilt and should be.** Progress is still synthesised from tool names in `sse_events.py` rather than emitted by the node that knows. `get_stream_writer()` is the correct home for the status vocabulary already specified in `Current-Standing/TODO/03-Stream-Contract.md`.

**Note 6 rung 7 was verified rather than trusted**, because the disambiguation interrupt is the most distinctive behaviour in the system and a missed one is indistinguishable from a hang.

**Note 5 is the upgrade.** The stack is 1.0.5 and v1, so the loop unpacks tuples. Moving to 1.2.11 changes that loop and nothing else, which is recorded in `Current-Standing/TODO/05-Streaming-Build.md` phase 1.

---

## Interview hooks

The one that separates people who have used it from people who have read about it: **how do you show progress from inside a node that takes eight seconds** (note 3, and the answer is a writer, not a heuristic over tool names).

The one that catches everybody: **if you turn on two stream modes, how many times does the answer arrive** (note 8, and the answer is three).

The design question: **when would you use `astream_events` over `astream`** (note 9, and a good answer includes that the choice has a shelf life).

---

## Sources to verify against

- [LangGraph — Streaming](https://docs.langchain.com/oss/python/langgraph/streaming), the mode reference and the `nostream` tag
- [LangGraph `astream` reference](https://reference.langchain.com/python/langgraph/pregel/main/Pregel/astream)
- [`astream_events` reference](https://reference.langchain.com/python/langchain-core/runnables/base/Runnable/astream_events)
- [LangGraph 1.0 general availability](https://changelog.langchain.com/announcements/langgraph-1-0-is-now-generally-available) for the version boundaries
- [Typed projections over a content-block protocol](https://vadim.blog/langgraph-v3-event-streaming-typed-projections) for note 9 rung 9
- [Issue 4853 — tool call name and id across chunks](https://github.com/langchain-ai/langgraph/issues/4853) for note 8 rungs 11 and 12
