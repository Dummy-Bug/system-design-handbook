# Green threads

> Don't feel that next I am going to cover red thread, yellow thread.

> **Java multithreading is implemented by using two models:**
> **1.** the **green thread model**  **2.** the **native OS model**

## Green thread model

> **The thread which is managed completely by the JVM, without taking underlying OS support, is called a green thread.**

**Everything is handled by the JVM** — creation, scheduling, switching. The operating system does not know these threads exist.

> **Very few operating systems, like Sun Solaris, provide support for the green thread model. Anyway, the green thread model is deprecated and not recommended to use.**

## Native OS model

> **The thread which is managed by the JVM with the help of the underlying OS is called the native OS model.**

> **All Windows-based operating systems provide support for the native OS model.**

**This is what you are actually using.** Note `02` said the same thing from the other direction: a platform thread is mapped **one-to-one onto an OS thread**, and the scheduling decision belongs to the **OS scheduler**, not the JVM.

> [!important] **Green threads came back, under a different name.** The idea — many threads managed entirely by the JVM with no OS thread each — is exactly what **virtual threads** are. They were dropped as green threads in Java 1.3 and returned in **Java 21** with a working implementation.
>
> | | Green threads (1.0–1.2) | Virtual threads (21+) |
> |---|---|---|
> | Managed by | the **JVM** alone | the **JVM**, on carrier threads |
> | OS thread per thread | **no** | **no** |
> | Status | **removed** | **current** |
>
> **The difference is what killed the original:** green threads could not use more than one CPU, and a single blocking OS call froze every thread in the JVM. Virtual threads solve both by multiplexing onto a pool of real platform threads.
>
> So green thread is still a fair interview question, and **the best answer connects it to virtual threads** rather than treating it as dead history.

---

# Stopping a thread

```java
t.stop();
```

> **If we call `stop()`, immediately the thread will enter the dead state.**

**And you must not do it.**

> Killing a thread in the middle of execution — is it recommended? Killing a person in the middle of life is not good.

## Why it is dangerous

```java
public void run() {
    // open a DB connection
    // read the data          ← t.stop() called HERE
    // close the DB connection
}
```

**The thread dies mid-read.** The close never runs.

> **Who is going to close the database connection? No one. One database connection you are going to waste.** The resources which were opened may never be released.

> [!important] **This is the same argument as `finally` in `EXCEPTION-HANDLING/05` and as daemon threads in note `13`** — cleanup code that never runs. `stop()` is worse than both, because it can strike **at any instruction**, so there is no place you could put cleanup that is safe.
>
> It also releases every lock the thread held **instantly**, potentially leaving shared objects half-modified — data inconsistency (note `07`) created deliberately.

---

# What the JDK does now

Compiling a call to `stop()` produces a deprecation note. **But the runtime behaviour has moved further than deprecation.** Measured on JDK 25:

```
stop()    -> java.lang.UnsupportedOperationException
suspend() -> java.lang.NoSuchMethodException
resume()  -> java.lang.NoSuchMethodException
```

| Method | On JDK 25 |
|---|---|
| **`stop()`** | still declared — **throws `UnsupportedOperationException`** |
| **`suspend()`** | **removed from the class entirely** |
| **`resume()`** | **removed from the class entirely** |

Confirmed with `javap java.lang.Thread`: only `public final void stop();` remains, carrying `@Deprecated(since="1.2", forRemoval=true)`.

**Bisected with `--release`:** `suspend()` and `resume()` compile at **22** and fail at **23**.

> [!warning] **Code calling `suspend()` or `resume()` no longer compiles at all**, and code calling `stop()` compiles but throws the moment it runs. **There is no way to force-kill a thread in modern Java**, and that is deliberate.
>
> **The replacement is cooperative cancellation:**
> ```java
> class Worker extends Thread {
>     private volatile boolean running = true;
>     public void shutdown() { running = false; }
>     public void run() {
>         while (running) { /* work */ }
>         // cleanup runs normally
>     }
> }
> ```
> or **`interrupt()`** from note `06`, which is what the executor framework uses. **The thread decides when it is safe to stop** — which is the only way the cleanup can be guaranteed to run.

> [!info] **`suspend()` and `resume()` were deadlock-prone by design.** `suspend()` froze a thread **without releasing its locks**, so if it was suspended inside a synchronized block, any thread needing that lock — including the one meant to call `resume()` — blocked forever. **A guaranteed deadlock**, which is why they went first.

---

# What this part established

| | |
|---|---|
| Two models | **green thread** and **native OS** |
| Green thread | managed **completely by the JVM**, no OS support |
| Supported by | very few OSes, like **Sun Solaris** — **deprecated** |
| Native OS model | JVM **with** the underlying OS — what you actually use |
| The idea returned as | **virtual threads** (Java 21) |
| Why green threads failed | **one CPU only**, and one blocking call froze everything |
| `stop()` | puts the thread **straight into the dead state** |
| Why that is dangerous | **cleanup never runs**; locks drop mid-update |
| `stop()` on JDK 25 | declared, but throws **`UnsupportedOperationException`** |
| `suspend()` / `resume()` on JDK 25 | **removed entirely** — will not compile |
| Removed in | **Java 23** |
| Why they were removed first | `suspend()` froze a thread **holding its locks** — a certain deadlock |
| The modern way to stop a thread | a **`volatile` flag**, or **`interrupt()`** |
| The principle | **the thread decides when it is safe to stop** |
