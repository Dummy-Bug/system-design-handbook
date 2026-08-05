The `create_task` fix left an open question. In that code we awaited `task1` first, then `task2` — the same order we created them. What if we flip it? Await `task2` first, then `task1`. Does task 2 now run first? Do the results come back swapped?

This example exists to break a very natural mental model: that `await task` means *"run this task now."* It doesn't. And seeing what it *actually* means changes how you write async code.

---

## Flip the awaits and watch what happens

One change from the `create_task` version — the awaits are swapped:

```python
async def main():
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    result2 = await task2                       # ← task2 awaited FIRST
    print("Task 2 fully completed")
    result1 = await task1
    print("Task 1 fully completed")
    return [result1, result2]
```

Some people expect task 2 to run first now. Others expect both to run but task 2 to finish first. The actual output:

```
Do something with 1...
Do something with 2...

Done with 1
Done with 2

Task 2 fully completed
Task 1 fully completed

['Result of 1', 'Result of 2']
Finished in 2.00 seconds
```

Still 2.00 seconds — still concurrent. And look closely: **task 1 still ran first, and still finished first** (`Done with 1` before `Done with 2`). Swapping the awaits changed *nothing* about execution. The only thing that moved is the print: `Task 2 fully completed` now comes before `Task 1 fully completed`, because `main()` refused to move past `await task2` until task 2 was done.

> [!important] `await` doesn't mean "run this now." The event loop runs **whatever is ready**, in its own order. What `await` guarantees is only this: **your code will not move past this line until the awaited thing is complete.** It's a completion checkpoint, not an execution command.

The animation makes the mechanism visible. Main suspends on `await task2` — but the loop picks up `fetch_data(1)` first (it was scheduled first and is ready). Both timers overlap as usual, and the 1-second timer fires first, so **task 1 completes while main isn't even awaiting it**:

![[AI-Engineering/00-Python-Utils/08-Async/Images/08-Await-Task2-Task1-Completes-Anyway.png]]

Task 1 is green — Complete — while `main()` still sits suspended on `await task2`. Nothing wakes main up, because task 1's completion isn't what it's waiting on. So what happens to task 1's return value? **It's saved in memory.** Later, when task 2 finally completes and main reaches `await task1`, there's nothing left to wait for — the await just pulls the already-stored result out and assigns it. Instant.

Under the hood the loop keeps its ready tasks in a **FIFO queue** (first in, first out) — whichever task became ready earliest gets run next, regardless of what anyone is awaiting. That's why "what you're awaiting" and "what runs next" are two unrelated things.

---

## You don't even need to await a task for it to run

Push the idea one step further. Replace the *first* await with a plain sleep — award nothing about task2 at that point:

```python
async def main():
    task1 = asyncio.create_task(fetch_data(1))
    task2 = asyncio.create_task(fetch_data(2))
    result1 = await task1
    print("Task 1 fully completed")
    result2 = await asyncio.sleep(2.5)   # ← not awaiting task2 at all!
    print("Task 2 fully completed")
    return [result1, result2]
```

```
Do something with 1...
Do something with 2...

Done with 1
Task 1 fully completed
Done with 2

['Result of 1', None]
Finished in 2.50 seconds
```

Both tasks still ran, in the same order, both completed — `Done with 2` appears even though nobody awaited task 2. The moment `main()` suspended on *any* awaitable (here the 2.5-second sleep), the loop got control and ran everything that was ready. Two details worth noticing in that output:

- `result2` is `None` — because it's now the return value of `await asyncio.sleep(2.5)`, and sleep returns nothing. Awaiting a thing gives you *that thing's* result, and this variable no longer holds task 2's result.
- Total time 2.50 seconds — the longest wait is now the sleep itself.

> [!info] Once a task is scheduled with `create_task`, it runs when the loop gets a chance — **whether or not you ever await it**. Awaiting is how you *collect the result and synchronise*, not how you *cause execution*.

---

## The design lesson — don't micromanage the loop

It's tempting, after tracing these examples, to start reasoning about exactly which task the loop will pick next and in what order everything interleaves. The advice is to deliberately *not* do that. Real async code runs tens or hundreds of tasks concurrently ; you won't know when each becomes ready, and you can't control it — the loop just does its job.

What you *do* control — the only thing you should enforce — is **completion points**: "do not move past this line until X is done." That's an `await`. If your code needs task 2 finished before step 5, await task 2 before step 5. Whether the loop happens to run main, task 1, or task 2 next is not your problem, and code that depends on that ordering is fragile by construction.

> [!tip] Interview framing: "`await` is a completion guarantee, not an execution trigger. Scheduled tasks run whenever the event loop is free — in ready-queue order, roughly FIFO — regardless of which one you're currently awaiting. If a task finishes while you're awaiting something else, its result is just held until your await for it, which then returns instantly. So in async design I only enforce *completion ordering* with awaits; I never try to control *execution ordering* — that's the loop's job."

There's a darker corollary to "the loop runs whatever is ready," though. Everything here relied on tasks *politely suspending* at their awaits. What if a task refuses to suspend — because someone put a blocking synchronous call inside it? That's the next example, and it breaks everything.
