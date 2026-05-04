#asyncio #queues #get #api #python

---

# `await get()` vs `get_nowait()` — The Asymmetry With Producer Side

> Prerequisite: [[queue-api-and-backpressure]], [[put-vs-put-nowait]] — establish the API surface and the producer-side "wait vs nowait" distinction.

The consumer side mirrors the producer's API:

```python
item = await queue.get()       # async — may suspend the consumer
item = queue.get_nowait()      # sync — instant or raises QueueEmpty
```

The shapes look symmetric, but they aren't. On the producer side, the difference between `put` and `put_nowait` vanished on an unbounded queue (covered in [[put-vs-put-nowait]]). On the consumer side, that escape hatch doesn't exist. This note walks through why, then maps each method to the situations where it actually fits.

---

## Why This Side Is Not Symmetric With the Producer Side

For `put`, the difference between the two methods **vanished on an unbounded queue** — there's always space, so neither version ever has reason to wait.

`get` doesn't have that escape hatch.

> [!important] `maxsize` controls the **ceiling** — whether the queue can be "full." Nothing controls the **floor** — every queue starts empty and can become empty again at any moment.

So the empty case is **always reachable**, no matter how you configured the queue. There's no bounded/unbounded toggle that makes `get` and `get_nowait` collapse to the same behavior. They always differ.

That makes the choice purely about what you actually want the consumer to do.

---

## The Common Case — Streaming Loop

Most of the time the consumer's only job is "sit and wait for the next item, forward it, repeat." The right shape is dead simple:

```python
while True:
    event = await queue.get()      # sleeps for free until something arrives
    yield serialize(event)
```

The consumer parks at `await get()`, costing zero CPU and zero loop ticks. The moment a producer pushes, the event loop wakes the consumer up, it processes the event, and goes back to sleep at `get()` again. No polling, no timing tuning, no busy waiting.

### Compare the wrong choice

```python
while True:
    try:
        event = queue.get_nowait()
        yield serialize(event)
    except asyncio.QueueEmpty:
        await asyncio.sleep(0.05)   # try again in 50ms
```

You're back to the polling anti-pattern. Every 50ms you wake up, check, find nothing, go back to sleep. Higher CPU. Up to 50ms latency per event for no reason. Drop the sleep and you burn 100% CPU spinning. There's literally no upside.

> [!tip] If your loop has nothing to do but wait for the next item, **always use `await get()`.**
> `get_nowait` in a tight polling loop is a code smell.

---

## When `get_nowait` Actually Fits

There are two real-world patterns where the consumer needs to stay in control instead of committing to a single `await get()`.

### 1. Opportunistic batching

You have a logging coroutine that ships logs over HTTP to a remote service. Every interesting event in your app pushes a log entry into a queue.

**Naive approach with `await get()`:**

```
log arrives → HTTP POST
log arrives → HTTP POST
log arrives → HTTP POST
```

If you're getting 1000 logs per second, that's 1000 HTTP requests per second. Each one carries connection overhead, network round-trip, server cost. Wasteful.

**Smarter approach with `get_nowait`:** every 100ms, drain *whatever's currently in the queue* — could be 0 entries, could be 50 — bundle them into **one** HTTP request, and ship.

```
... 100ms tick ...
drain queue → 47 entries → one HTTP POST
... 100ms tick ...
drain queue → 0 entries → skip
... 100ms tick ...
drain queue → 23 entries → one HTTP POST
```

Now you're doing 10 HTTP requests per second instead of 1000. **Same data, way fewer round-trips.**

The key word is **opportunistic** — the coroutine doesn't *want* to wait for more. It wants to grab what's there right now and move on. `await get()` would force it to block waiting for at least one entry, defeating the timer-based batching pattern.

> Pattern: "I have a fixed schedule. On each tick, take whatever's in the queue and do something with it. Don't wait."

### 2. Mixing the queue with other work

Imagine a worker coroutine that has three jobs at once:

1. Process events from a queue whenever they arrive.
2. Send a heartbeat ping to a monitoring server every 5 seconds (so the monitor knows you're alive).
3. Watch for a shutdown signal and exit cleanly when it fires.

If your worker just does:

```python
while True:
    event = await queue.get()    # stuck here forever if no events
    process(event)
```

…and no events arrive for 30 seconds, the worker is **completely frozen** at `await get()`. It never gets a chance to send the heartbeat (the monitor will mark you as dead) and never gets a chance to check for the shutdown signal (you can't kill the worker cleanly).

`await get()` is too committal. You've handed your entire attention to the queue.

The fix: never let the queue alone hold you hostage. Two ways:

- A small polling loop with `get_nowait` interleaved with the other tasks.
- Better: `asyncio.wait()` racing multiple awaitables at once — "wake me up when **any** of these happen: the queue has something, the 5-second timer fires, or the shutdown event triggers."

> Pattern: "I have multiple things competing for my attention. I can't afford to commit to waiting on just one of them, because the others would never get serviced."

---

## The Underlying Principle

> [!info] `await get()` is a **one-way commitment** to the queue.
> Most of the time that's exactly what you want — your job is just to forward events. But when your job is bigger than that (batching on a schedule, juggling multiple inputs), you need the consumer to stay in control of *when* it waits and *when* it does other things. That's what `get_nowait` (or `asyncio.wait`) gives you.

---

## Decision Rule

> [!tip] One-liner
> Consumer's only job is "wait and forward" → `await get()`.
> Consumer is on a fixed schedule and just wants whatever's there → `get_nowait`.
> Consumer is juggling multiple inputs → `asyncio.wait()` over several awaitables (or `get_nowait` for a quick fix).

---

## Mental Model

> `get` and `get_nowait` are the queue saying: "you choose what happens when there's nothing here — wait, or raise?"
> Unlike the producer side, the choice is always live. The empty state can happen to any queue, bounded or unbounded.
> Pick `await get()` when waiting *is* your job. Pick `get_nowait` when waiting would prevent you from doing your other jobs.
