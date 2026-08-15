# The three ways to prevent thread execution

A thread is running happily and you need to stop it — **temporarily, not permanently.**

> **We can prevent a thread execution by using the following methods:**
> **1.** `yield()`  **2.** `join()`  **3.** `sleep()`

> [!info] **Every one of these, and every pair of them, is an interview question.** *"What is the
> purpose of `yield()`? What is the difference between `yield()` and `join()`? Between `yield()` and
> `sleep()`?"* — the comparisons matter as much as the methods.

This session covers `yield()` and `join()`; `sleep()` is next.

---

# `yield()`

> **`yield()` causes the current executing thread to pause and give the chance to other waiting
> threads of the same priority.**

**Running → Ready.** The thread does not sleep and does not block — it steps back into the ready
queue and is immediately eligible again.

```mermaid
flowchart LR
    R["<b>Running</b>"] -->|"yield()"| RD["<b>Ready / Runnable</b>"]
    RD -->|"scheduler picks it again"| R
```

> [!important] **A yielding thread may be picked again immediately.** If no other thread of the same
> priority is waiting, the scheduler can hand the processor straight back. **`yield()` is an offer, not
> a transfer.**

> [!question]- **The village with two landline phones.** His analogy for yielding — why you step aside
> when others are waiting.
>
> Before mobile phones — 1999, 2000 — his village had **two landline connections in total**. To speak
> to his parents from outside, he would call a **PP number** (a public phone), ask them to fetch his
> mother or father, and call back **ten minutes later**.
>
> **One phone, many people waiting.** If you are on a call and a queue has formed, you finish and step
> aside so the next person gets a turn — even though you might want to keep talking. **That is
> `yield()`**: voluntarily giving up the processor because others are waiting for it.

## The demo

```java
class MyThread extends Thread {
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println("child thread");
            Thread.yield();
        }
    }
}
```

Measured on JDK 25:

```
main thread
main thread
main thread
main thread
  child thread
  child thread
main thread
  child thread
  child thread
  child thread
```

**The main thread got several turns**, which is the yield taking effect — but the interleaving is not
predictable.

> [!warning] **`yield()` is a hint the platform may ignore entirely.** He says so himself: *"some
> platforms won't provide proper support for the `yield()` method"* — the same caveat as thread
> priorities in note `04`.
>
> **The modern Javadoc is blunter:** `yield()` is *"a hint to the scheduler"* and *"it is rarely
> appropriate to use this method."* **Never use it to coordinate threads** — use `join()`,
> `wait()`/`notify()`, or the concurrency utilities. Its remaining legitimate use is in busy-wait
> loops, and even there `onSpinWait()` is the modern replacement.

> **The thread which requires more processing time is recommended to call `yield()` frequently** — so
> it does not monopolise the processor.

---

# `join()`

> **If a thread wants to wait until another thread completes, then it should call `join()` on that
> thread.**

```java
t1.join();     // "I will wait until t1 finishes"
```

**The thread calling `join()` enters the waiting state**, and resumes when the target thread is
terminated.

## The demo

```java
JoinThread t = new JoinThread();
t.start();
t.join();
System.out.println("main thread");
```

Measured on JDK 25:

```
  child thread
  child thread
  child thread
main thread  <- prints only AFTER the child finished
```

**Guaranteed order** — unlike priorities in note `04`, which gave no such guarantee.

> [!important] **This is the tool note `04` pointed at.** If you need thread A to finish before thread
> B continues, **`join()` is the answer** — not `setPriority()`. It is a real synchronisation
> guarantee, not a scheduling hint.

## Who calls it on whom

The direction confuses people, and it is worth stating precisely:

| You want | Write |
|---|---|
| **T1** to wait for **T2** | inside T1: **`t2.join()`** |
| **T3** to wait for **T2** | inside T3: **`t2.join()`** |
| **main** to wait for the child | inside main: **`child.join()`** |

> **The thread that must wait calls `join()` on the thread it is waiting for.** You name the thread you
> are waiting *for*, and the call happens in the thread doing the waiting.

## The three overloads

```java
public final void join() throws InterruptedException
public final void join(long milliseconds) throws InterruptedException
public final void join(long milliseconds, int nanoseconds) throws InterruptedException
```

Confirmed on JDK 25 — all overloads are **`final`**, **not static**, and all declare
**`InterruptedException`**.

> [!important] **`join()` is an instance method; `yield()` and `sleep()` are static.** Measured:
>
> | Method | static? | throws `InterruptedException`? |
> |---|---|---|
> | **`yield()`** | ✅ **static** | ❌ no |
> | **`join()`** | ❌ instance, **final** | ✅ yes |
> | **`sleep()`** | ✅ **static** | ✅ yes |
>
> **The pattern is not arbitrary.** `yield()` and `sleep()` act on *the thread calling them*, so there
> is no object to name — they are static. `join()` acts on *a particular other thread*, so it must be
> called on that object.
>
> **Every `join()` overload throws `InterruptedException`**, so it must be handled or declared — a
> compile error otherwise, since it is a checked exception.

> [!warning] **`join()` does not release any locks the waiting thread holds.** Like `sleep()`, and
> unlike `wait()`. A thread that calls `join()` while holding a lock keeps that lock for the whole
> wait — which is one way to build the deadlock in note `12`.

---

# What this part established

| | |
|---|---|
| Three ways to prevent execution | **`yield()`** · **`join()`** · **`sleep()`** |
| `yield()` | give the chance to other waiting threads **of the same priority** |
| State change | **Running → Ready** |
| It may be re-picked | **immediately** — it is an offer, not a transfer |
| Platform support | **not guaranteed** — a hint the scheduler may ignore |
| Modern advice | *"rarely appropriate to use this method"* |
| `join()` | wait until **another thread completes** |
| Who calls it | the thread that **must wait**, naming the thread it waits **for** |
| The guarantee | **real** — unlike priorities |
| Overloads | `join()` · `join(ms)` · `join(ms, ns)` |
| `yield()` / `sleep()` | **static** — they act on the **current** thread |
| `join()` | **instance and final** — it acts on **another** thread |
| `join()` and `sleep()` | throw **`InterruptedException`** |
| `yield()` | does **not** throw |
| `join()` and locks | **releases nothing** — only `wait()` does that |
