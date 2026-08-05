Every example so far created tasks one at a time and awaited them one at a time, by hand. Fine for two tasks; miserable for fifty URLs. Real async code batches: *fire off a group of tasks, run them all concurrently, collect all the results*. Python gives you two tools for it — `asyncio.gather` and `asyncio.TaskGroup` — and the real difference between them isn't syntax. It's **what happens when one task fails.**

The demo file runs the same two fetches four ways, one section after another:

```python
async def fetch_data(param):
    await asyncio.sleep(param)
    return f"Result of {param}"

async def main():
    # 1 — Create Tasks Manually (the way we've done it so far)
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    result1 = await task1
    result2 = await task2
    print(f"Task 1 and 2 awaited results: {[result1, result2]}")

    # 2 — Gather Coroutines
    coroutines = [fetch_data(i) for i in range(1, 3)]
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    print(f"Coroutine Results: {results}")

    # 3 — Gather Tasks
    tasks = [asyncio.create_task(fetch_data(i)) for i in range(1, 3)]
    results = await asyncio.gather(*tasks)
    print(f"Task Results: {results}")

    # 4 — Task Group
    async with asyncio.TaskGroup() as tg:
        results = [tg.create_task(fetch_data(i)) for i in range(1, 3)]
        # All tasks are awaited when the context manager exits.
    print(f"Task Group Results: {[result.result() for result in results]}")
```

```
Task 1 and 2 awaited results: ['Result of 1', 'Result of 2']
Coroutine Results: ['Result of 1', 'Result of 2']
Task Results: ['Result of 1', 'Result of 2']
Task Group Results: ['Result of 1', 'Result of 2']
Finished in 8.00 seconds
```

Eight seconds is not a failure — it's four groups run one after another, each internally concurrent at 2 seconds: `4 × max(1,2) = 8`. Within every group, the waits overlapped.

---

## `gather` — one await for a whole batch

Two mechanics to read carefully:

**The `*` unpacking.** `gather` doesn't take a list — it takes individual awaitables as arguments. `asyncio.gather(*coroutines)` unpacks the list, exactly as if you'd passed each item separately. Forget the asterisk and you've passed one list-shaped argument; it fails.

**Coroutines or tasks — both work, and the difference is familiar.** Section 2 hands `gather` bare *coroutine objects*: nothing was scheduled when the list was built (building a list of coroutines schedules nothing — same lesson as the bare-await trap), and it's `gather` itself that schedules them all and runs them concurrently. The animation catches that moment — main suspended on the `await asyncio.gather(...)` line, both fetches on the loop, **both timers overlapping in Background I/O**:

![[AI-Engineering/00-Python-Utils/08-Async/Images/12-Gather-Coroutines-Both-Timers.png]]

Section 3 hands `gather` a list of *tasks* instead — those were scheduled the moment `create_task` ran, before `gather` was even called. Which to pass? If you only want the results, coroutines are fine — `gather` schedules them for you. If you want to **monitor or interact with the tasks before they complete** (check status, cancel one, name them), create tasks — that's the extra functionality tasks carry.

---

## `TaskGroup` — the context-manager way (Python 3.11+)

Section 4 looks different from everything so far — `async with`:

```python
async with asyncio.TaskGroup() as tg:
    results = [tg.create_task(fetch_data(i)) for i in range(1, 3)]
    # All tasks are awaited when the context manager exits.
print(f"Task Group Results: {[result.result() for result in results]}")
```

This is the first **async context manager** in the series. Just like functions, context managers can be async when their setup or teardown needs to do I/O work — hence `async with`. (They show up all over real async code: network sessions, file handles, database connections.)

The striking thing: **there is no `await` anywhere.** You don't await the tasks inside the block, and you don't await anything after it. The TaskGroup awaits *for* you — **when the `async with` block exits, it suspends there until every task created in the group is complete.** The animation shows the setup state: both `tg.create_task` tasks scheduled and Ready while main is still inside the block:

![[AI-Engineering/00-Python-Utils/08-Async/Images/13-TaskGroup-Tasks-Ready-On-Exit.png]]

After the block, each item in `results` is a completed Task, so you collect values with `.result()`.

---

## The real difference — failure semantics

For the happy path the two are interchangeable. The choice is entirely about errors:

**`gather` with `return_exceptions=True` — everything runs to the end, no matter what.** Every awaitable in the gather finishes, succeed or fail. The result is a list where each position holds *either* the result *or* the exception object for that slot. Use this when partial success is valuable: crawling 100 URLs, you don't want 99 good pages thrown away because one URL hung.

**`gather` with the default `return_exceptions=False` — avoid it.** On the first failure it raises that one exception. You don't get the other errors, you don't get the successful results — and the *other tasks keep running unsupervised*, orphaned. Corey's blunt recommendation (he even caught his own demo missing the flag on one gather): if you use `gather`, set `return_exceptions=True`; he sees almost no good use case for the default.

**`TaskGroup` — all succeed together or fail together.** On the first failure it **cancels all the other tasks**, then raises an `ExceptionGroup` bundling every exception from the failed (and cancelled) tasks. Better error reporting, proper cleanup, no orphans. There's no option to keep running after a failure — that's the point. Use it when the tasks are parts of one job that only makes sense whole.

| | `gather(..., return_exceptions=True)` | `TaskGroup` |
|---|---|---|
| One task fails | others **keep running** to completion | others are **cancelled** |
| You get back | list mixing results and exception objects | `ExceptionGroup` raised with all errors |
| Orphaned tasks | never (everything completes) | never (everything cancelled + awaited) |
| Use when | partial success is useful (URL crawl) | all-or-nothing jobs |
| Avoid | the `return_exceptions=False` default — first error raised, successes lost, tasks orphaned | |

> [!tip] Interview framing: "For batches I use `gather` or `TaskGroup`, and I choose on failure semantics. `gather` with `return_exceptions=True` runs every task to completion and returns a list mixing results and exceptions — right when partial success matters, like crawling many URLs. `TaskGroup` is all-or-nothing: first failure cancels the rest and raises an ExceptionGroup with proper cleanup — right when the tasks form one job. The trap is gather's *default*, `return_exceptions=False`: it raises the first error, loses the successful results, and leaves the other tasks running orphaned — I basically never want that. Mechanics worth mentioning: gather takes unpacked awaitables (`*tasks`), and TaskGroup is an async context manager that awaits everything at block exit, no explicit await."

That closes out the core machinery: what async is, the vocabulary, how concurrency actually starts, what `await` does and doesn't promise, how the loop gets blocked, the thread/process escape hatches, and batch running with proper error handling. What's left in the video is the payoff: taking a real synchronous codebase and converting it to async step by step — httpx, semaphores, async file writes — plus profiling and the async-vs-threads-vs-processes decision. That's the next session.
