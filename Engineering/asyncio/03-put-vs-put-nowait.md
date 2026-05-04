#asyncio #queues #put #api #python

---

# `await put()` vs `put_nowait()` — When the Difference Vanishes, and Why You Still Care

> Prerequisite: [[queue-api-and-backpressure]] — establishes the bounded vs unbounded distinction and the API surface this note goes deeper on.

[[queue-api-and-backpressure]] introduced the producer's two methods:

```python
await queue.put(item)       # async — may suspend the producer
queue.put_nowait(item)      # sync — instant or raises QueueFull
```

On a **bounded** queue, the difference is real: when the queue is full, `await put` suspends the producer until a slot frees up; `put_nowait` raises `QueueFull` immediately. That's the textbook answer.

But the more interesting case — and the one you actually hit in practice — is the **unbounded** queue, where the difference appears to vanish. This note walks through what happens during the suspend, why the difference disappears on unbounded queues, and the three reasons you should still pick deliberately.

---

## What "Wait" Really Means for a Coroutine

When `await queue.put(item)` "waits," it does **not** freeze the thread the way `time.sleep()` would. Here's the actual sequence:

1. Coroutine hits `await queue.put(item)`. Queue is full.
2. The queue tells the event loop: "park this coroutine until I free up a slot."
3. The coroutine is now **suspended** — not consuming CPU, just sitting in a "waiting" list inside the event loop.
4. The event loop is now free to run **any other ready coroutine** on the same thread.
5. Eventually the consumer calls `queue.get()`, freeing a slot. The queue tells the event loop: "wake the parked producer."
6. The event loop schedules the producer to resume. Next loop tick, `put` returns and the producer keeps running.

> [!info] "Wait" for a coroutine = voluntarily suspend at the `await` point so the loop can run other coroutines, and get woken up when a condition is met.
> No CPU spent waiting. Other work continues on the same thread.

The condition the producer is waiting on is purely **in-memory** (a slot freeing up in the queue). No network, no disk. But the mechanism — park, run others, wake on condition — is identical to how the loop handles real I/O waits.

---

## The Unbounded Case — the Difference Vanishes

Now make the queue unbounded:

```python
queue = asyncio.Queue()      # no maxsize → unbounded
```

There's no "full" state. A slot is *always* available. So the condition `put` would otherwise wait on is **already true forever**.

This means `await queue.put(item)` has no reason to park anyone. It just inserts and returns immediately.

> [!important] On an unbounded queue, `await queue.put(item)` and `queue.put_nowait(item)` are **behaviorally identical**. Both insert and return instantly. Neither suspends, neither raises.

The "wait vs no-wait" distinction has no teeth here. The difference vanishes.

---

## So Why Pick One Over the Other When They're Identical?

If they behave the same on unbounded queues, why bother choosing? Three reasons — none are about behavior, all are about **code shape**.

### 1. No `await` required at the call site

```python
await queue.put(item)     # caller must be `async def`
queue.put_nowait(item)    # works from anything — sync helper or async function
```

If a sync helper deep inside your code wants to push to the queue, `put_nowait` lets it. `await put` would force every emitter all the way down the call stack to be `async def`.

### 2. Clearer reading

When you read `put_nowait(...)`, you immediately know "this never blocks." When you read `await put(...)`, you (or a future reader six months from now) have to remember the queue is unbounded to be sure it won't block. One less thing to hold in your head.

### 3. No accidental yield point

Every `await` is a place the event loop **can switch to another coroutine** — even if the awaited operation returns immediately, the `await` itself is a yield point.

So this code:

```python
ctx.emit(StartedEvent(...))         # uses put_nowait under the hood
result = compute()
ctx.emit(DoneEvent(...))
```

runs the three statements with **no yield point** between them. Whereas:

```python
await queue.put(StartedEvent(...))
result = compute()
await queue.put(DoneEvent(...))
```

has two yield points. The event loop can technically switch to another coroutine right after each `put`. For most code this doesn't matter — but if you're inside a critical section where the producer's intent is "emit, work, emit, all in one shot," you don't want sneaky yield points sliding in.

---

## Decision Rule

> [!tip] One-liner
> Unbounded queue → `put_nowait`.
> Bounded queue with backpressure → `await put`.
> Bounded queue with explicit overflow handling → `put_nowait` + catch `QueueFull`.

The first case is the most common in per-request streaming pipelines. The second is the right shape for long-lived ingestion or background processing where the consumer's rate is the bottleneck. The third is for explicit "I'd rather drop this event than slow the producer down" policies — rare, but real.

---

## Mental Model

> [!info] `put` and `put_nowait` are the queue saying: "you choose what happens when there's no room — wait, or raise?"
> On an unbounded queue, the question never comes up, so the choice is purely about code style: clarity, callability from sync code, and avoiding accidental yield points.
