Everything asyncio gives you rests on one polite convention: tasks **suspend themselves** at their awaits, handing the thread back to the event loop. This example is about what happens when a task doesn't — because someone put ordinary blocking code inside an async function. It is the single most common way real asyncio codebases lose their concurrency without anyone noticing.

---

## The setup — `time.sleep` smuggled into a coroutine

Take the working `create_task` example and change exactly one line inside `fetch_data`: replace `await asyncio.sleep(param)` with `time.sleep(param)`.

```python
async def fetch_data(param):
    print(f"Do something with {param}...")
    time.sleep(param)            # ← blocking call inside an async function
    print(f"Done with {param}")
    return f"Result of {param}"

async def main():
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    result1 = await task1
    print("Task 1 fully completed")
    result2 = await task2
    print("Task 2 fully completed")
    return [result1, result2]
```

Note what you *can't* write: `await time.sleep(param)` is simply an error — `time.sleep` isn't awaitable, it was never coded to suspend itself and yield to a loop (the exact point from the vocabulary note). But nothing stops you from *calling* it inside a coroutine. The function still compiles, the tasks still get created and scheduled, everything *looks* like the working example. Run it:

```
Do something with 1...
Done with 1
Task 1 fully completed
Do something with 2...
Done with 2
Task 2 fully completed
['Result of 1', 'Result of 2']
Finished in 3.01 seconds
```

**Three seconds — concurrency is gone.** And it's worse than the bare-await trap: look at the first two lines. In every working example both `Do something with...` lines appeared together at the start. Here `Do something with 2...` doesn't appear until task 1 is *completely finished*. The tasks didn't even overlap their starts.

---

## Why — a task that never suspends never yields

Walk the animation. Main suspends on `await task1`; the loop runs `fetch_data(1)`; it prints; it reaches `time.sleep(1)`. The sleep starts — but there was **no await**, so the task **never suspends**. It just stands there, running, holding the only thread, while the sleep blocks:

![[AI-Engineering/Python-Async/Images/09-Time-Sleep-Blocks-The-Event-Loop.png]]

Read that frame carefully — it's the whole failure in one image. The blocking sleep is ticking in Background I/O with the annotation spelled out: *"time.sleep() blocks the entire event loop — no other tasks can run during this time!"* The running task still says **Running** (it never suspended), and the other task sits **Ready** — ready, waiting, and completely starved. The event loop can't run it. The event loop can't run *anything*. Control only returns when the blocking call finishes on its own.

When the sleep completes there's nothing to "wake up" — no timer-fires-and-notifies dance, because we never registered one. The synchronous code just continues to the next line, finishes task 1, and only *then* does the loop get control and start task 2 — which promptly blocks the thread again for two more seconds. Sequential execution, `1 + 2 = 3` seconds, with async syntax decorating every line.

> [!danger] One blocking call anywhere in a task freezes **every** task on the loop. Cooperative multitasking has no referee: the loop cannot interrupt a running task, so a task that doesn't voluntarily suspend holds the entire single thread hostage. This is the "one greedy cook stops the whole McDonald's" failure from the first note, realised in code.

A small aside the animation walkthrough surfaced: after task 1 completes, *both* main and task 2 are ready — and the loop picks **task 2**, not main, because task 2 entered the ready queue first (FIFO, as in the previous note). Corey's own advice applies: don't obsess over that ordering; the lesson is only that readiness order, not await order, decides what runs.

---

## `time.sleep` is a stand-in for every blocking call you actually use

Nobody ships `time.sleep` to production. But this failure is exactly what happens with any synchronous library call inside async code, and the realistic culprit list is long:

- **`requests.get(...)`** — the classic. The `requests` library is synchronous; one slow HTTP call inside a coroutine freezes every other request your service is juggling. Async web requests need an async library: **httpx** or **aiohttp**.
- Synchronous database drivers, blocking file I/O, anything that talks to the network or disk without `await` in front of it.
- Heavy CPU work — a tight loop crunching numbers never hits an await, so it blocks just the same.

> [!important] The rule: inside async code, every I/O call must be an **awaitable from an async-compatible library**. `time.sleep` → `asyncio.sleep`; `requests` → `httpx`/`aiohttp`; sync DB driver → its async counterpart. Async needs async all the way down — one synchronous hole in the stack and the loop stalls there.

**What this example guarantees you'll remember:** blocking code inside a coroutine doesn't error, doesn't warn, and doesn't crash — it silently serialises your entire application. The only symptoms are timing (3s instead of 2s) and starts that don't overlap. Profile for it; you won't see it in the code's shape.

> [!tip] Interview framing: "The event loop is single-threaded and cooperative, so a blocking call inside a coroutine — `time.sleep`, `requests.get`, a sync DB driver — never yields, and every other task starves until it returns. The code still runs, just with zero concurrency, which makes it a silent performance bug. The fix is async-native libraries for anything that waits — asyncio.sleep, httpx, async drivers. And if a blocking library has no async alternative, you push it off the loop into a thread or process pool."

That last escape hatch — *what if the blocking library is the only option?* — is precisely the next example: `asyncio.to_thread` and `run_in_executor`.
