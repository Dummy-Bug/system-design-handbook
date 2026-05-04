#langgraph #asyncio #request-context #checkpointer #serialization #lifecycle

---

# Where Should an Event Queue Live in a LangGraph App?

> Prerequisite: [[architecture-inversion]] — establishes that nodes push events into a queue and a streaming service drains them.

You've decided that nodes will push events into a queue and a streaming service will drain them. Good. Now: **where does the queue object actually live?**

You have three plausible homes:

1. A module-level global — `_event_queue = asyncio.Queue()` at the top of some file.
2. A field on the graph state — passed through every node like any other state.
3. A field on a per-request context object (e.g. a `RequestContext` set in middleware).

Only option 3 works. This note explains why the other two are traps.

---

## Option 1 — Module-Level Global

Looks clean. One queue, available everywhere, no plumbing.

```python
# stream_bus.py
event_queue = asyncio.Queue()
```

```python
# any node
from stream_bus import event_queue
event_queue.put_nowait(event)
```

> [!danger] What breaks
> Two users hit the streaming endpoint at the exact same moment. Both pipelines run concurrently in the same Python process. Both push into the same queue. The streaming service for User A reads events for User B. User A sees User B's data on screen. PII leak, broken UX, potential security incident.

A module-level global means **one queue for the entire process** — all requests share it. There's no way for the consumer to tell "this event belongs to my request."

The fix is conceptually obvious: the queue must be **scoped to a single request**. Producer (node running for request A) and consumer (streaming response for request A) must be the only two parties touching that particular queue.

---

## Option 2 — Field on Graph State

State already gets passed to every node. So why not put the queue there?

```python
class PipelineState(TypedDict):
    user_message: str
    # ... other domain fields ...
    event_queue: asyncio.Queue   # ← seems easy
```

This breaks for a deeper reason: **the checkpointer.**

LangGraph snapshots state to durable storage between every node execution. That's literally how `interrupt()` (HITL) works — the graph pauses, state is persisted, the request ends, and minutes later a new request resumes the graph from the saved state.

In production, that storage is usually DynamoDB / Postgres / Redis. The state has to be **serialized** before it can travel to storage.

> [!important] What's actually inside an `asyncio.Queue`?
> - A reference to the running asyncio event loop
> - Internal locks and futures waiting on `get()`
> - A `collections.deque` holding the items
>
> None of this is serializable. None of this means anything outside the live process that created it.

### The Phone-Line Analogy

Think of an `asyncio.Queue` as a phone line between two people standing in the same room.

- One person (the node) puts messages onto the line.
- The other person (the streaming service) picks them up.
- It only works because both are alive, both in the room, right now.

Now imagine someone says "let's save this phone line to a database." What would you actually save? You can write the words "phone line" on paper and mail it to a warehouse — but the **connection itself** didn't travel. A week later you pull the paper out and you have words, not a phone line.

That's `asyncio.Queue`. A live, in-process connection. There is nothing meaningful you can serialize and ship to DynamoDB.

### Even If You Could Serialize It

Suppose serialization magically worked. The HITL flow makes it pointless anyway:

```
1. Node emits event → streaming service reads it → user sees it.
2. Graph hits interrupt() → stream ends → HTTP response closes.
   ↳ The streaming service object is gone.
3. Minutes later, user clicks "Confirm" → brand-new HTTP request.
   ↳ A brand-new streaming service starts.
```

Even if the queue object survived the round-trip to storage, the original consumer (streaming service from step 1) **doesn't exist anymore**. The deserialized queue would be a phone line to a person who left the building.

---

## Option 3 — Per-Request Context (the right answer)

The queue belongs on whatever object is **born and dies with one HTTP request**. In FastAPI apps, that's typically a `RequestContext` object set up in middleware via `ContextVar`.

```python
class RequestContext:
    def __init__(self, ...):
        self.event_queue: asyncio.Queue[StreamEvent] = asyncio.Queue()

    def emit(self, event: StreamEvent) -> None:
        self.event_queue.put_nowait(event)
```

Lifetime alignment is the whole point:

| Object | Lifetime | Can hold a live `asyncio.Queue`? |
|---|---|---|
| Module-level global | Process lifetime | Technically yes — but shared by all requests, so wrong |
| Graph state field | Persisted forever via checkpointer | No — must be serializable |
| Per-request context | One HTTP request | **Yes** — never persisted, never shared |

> [!success] One-line takeaway
> The queue needs both ends (producer + consumer) alive at the same moment. The container holding it must have the same lifetime. A per-request context object has exactly that lifetime.

---

## Mental Model

> [!info] Match the lifetime of the container to the lifetime of what it holds.
> - A live in-process resource (queue, lock, open socket, file handle) needs a short-lived per-request container.
> - Persistent business data (user profile, workflow state, audit logs) belongs in long-lived storage that can survive serialization.
>
> Mixing the two — putting a live resource into persistent storage — is the bug.

This isn't unique to LangGraph. The same trap exists any time you're tempted to "just stuff this into the session/state/cache for convenience." Ask: can this object be serialized, stored for hours, and rehydrated meaningfully? If not, it doesn't belong there.
