# Thread pools

> **Creating a new thread for every job may create performance and memory problems. To overcome this,
> we should go for a thread pool.**

> **A thread pool is a pool of already-created threads, ready to do our job.**

> [!info] **The connection-pool analogy he starts from.** In JDBC, opening a connection for every
> query, using it, and closing it **costs performance and memory every single time**. So instead you
> create a **pool** of connections up front, borrow one when you need it, and **return it to the pool**
> when you are done — the same connection object serving many requests.
>
> **Replace "connection" with "thread" and that is a thread pool.**

## The arithmetic

**Ten independent jobs, the naive way:** create a thread, run the job, let it die. Ten times. **Ten
threads created and destroyed.**

**With a pool of five:** submit all ten. The five threads take the first five; as each finishes it
picks up another. **Five threads do ten jobs.**

> [!important] **This is the argument note `02` foreshadowed.** A thread **cannot be restarted** —
> `IllegalThreadStateException`. So a program doing a job a million times would create a million
> `Thread` objects. **Pools exist because threads cannot be reused, but the workers running your tasks
> can be.**

> **Java 1.5 introduced the thread pool framework, also known as the executor framework.**

---

# Creating and using a pool

```java
ExecutorService service = Executors.newFixedThreadPool(3);   // 3 threads

service.submit(job);                                          // submit a Runnable

service.shutdown();                                           // done with the service
```

| Step | |
|---|---|
| **Create** | `Executors.newFixedThreadPool(n)` |
| **Submit** | `service.submit(runnableJob)` |
| **Shut down** | `service.shutdown()` |

> [!info] **Note what you no longer write.** No `new Thread(...)`, no `t.start()`, no keeping track of
> which threads exist. *"We are not responsible to create threads — the executor service takes care of
> it."* **You define the job and submit it.**

---

# The demo

```java
import java.util.concurrent.*;

class PrintJob implements Runnable {
    String name;
    PrintJob(String name) { this.name = name; }

    public void run() {
        System.out.println(name + " ... job started by " + Thread.currentThread().getName());
        try { Thread.sleep(1000); } catch (InterruptedException e) {}
        System.out.println(name + " ... job completed by " + Thread.currentThread().getName());
    }
}

class ExecutorDemo {
    public static void main(String[] args) {
        PrintJob[] jobs = { new PrintJob("Durga"), new PrintJob("Ravi"), new PrintJob("Shiva"),
                            new PrintJob("Pavan"), new PrintJob("Sunny"), new PrintJob("Anil") };

        ExecutorService service = Executors.newFixedThreadPool(3);
        for (PrintJob job : jobs)
            service.submit(job);
        service.shutdown();
    }
}
```

**Six jobs, three threads.** Measured on JDK 25:

```
Ravi  ... job started   by pool-1-thread-2
Durga ... job started   by pool-1-thread-1
Shiva ... job started   by pool-1-thread-3
Ravi  ... job completed by pool-1-thread-2
Pavan ... job started   by pool-1-thread-2      ← thread-2 reused
Shiva ... job completed by pool-1-thread-3
Sunny ... job started   by pool-1-thread-3      ← thread-3 reused
Durga ... job completed by pool-1-thread-1
Anil  ... job started   by pool-1-thread-1      ← thread-1 reused
...
```

> [!important] **Read the thread names and the reuse is right there.** `pool-1-thread-2` runs **Ravi**
> and then **Pavan**. Three threads, six jobs — **each thread did two.** That is the whole point,
> visible in the output.

**The same six jobs through a pool of one:**

```
Durga ... started by pool-2-thread-1
Durga ... completed by pool-2-thread-1
Ravi  ... started by pool-2-thread-1
...
```

**Strictly sequential** — one thread, one job at a time, all six in order.

> [!info] **The pool size is the concurrency limit, and that is the knob.** Size 3 runs three at once;
> size 1 makes it serial. **Sizing it is the real decision:** roughly the number of CPU cores for
> CPU-bound work, and considerably more for I/O-bound work where threads spend their time waiting.

---

# Shutting down

```java
service.shutdown();
```

**Terminates the threads in the pool once the submitted jobs are done.**

> [!warning] **Without `shutdown()`, your program will not exit.** Pool threads are **non-daemon** by
> default, so the JVM waits for them (note `13`) — and they wait forever for more work. **A missing
> `shutdown()` is a hung process**, and it is the most common mistake with this API.

**Submitting after shutdown**, measured on JDK 25:

```
-> RejectedExecutionException
```

> [!info] **`shutdown()` versus `shutdownNow()`.** `shutdown()` is graceful — no new jobs accepted,
> already-submitted ones still run. **`shutdownNow()` attempts to stop running jobs immediately** by
> **interrupting** them — which only works if your job actually responds to interruption (note `06`).
>
> **To wait for completion**, `shutdown()` does not block. Use:
> ```java
> service.shutdown();
> service.awaitTermination(30, TimeUnit.SECONDS);
> ```

---

# The other factory methods

`Executors` provides more than the fixed pool:

| Method | Gives you |
|---|---|
| `newFixedThreadPool(n)` | exactly **n** threads |
| `newSingleThreadExecutor()` | **one** thread — jobs run in order |
| `newCachedThreadPool()` | grows as needed, **reuses** idle threads |
| `newScheduledThreadPool(n)` | jobs that run **later** or **repeatedly** |
| `newVirtualThreadPerTaskExecutor()` | a **virtual thread per task** (Java 21+) |

> [!important] **`newVirtualThreadPerTaskExecutor()` is the modern answer for I/O-bound work**, and it
> inverts the advice above. Virtual threads are cheap enough that **you no longer pool them** — you
> create one per task and let the JVM multiplex them onto carrier threads. **Pooling exists because
> platform threads are expensive; virtual threads are not.**
>
> For CPU-bound work, a fixed pool sized to the cores is still right.

---

# `submit()` and `Future`

> [!info] **`submit()` returns a `Future`, which the lecture does not use but which is the reason to
> prefer `submit()` over `execute()`.**
> ```java
> Future<?> f = service.submit(job);
> f.get();          // blocks until the job finishes
> ```
> **With a `Callable` instead of a `Runnable`**, the job can return a value and throw a checked
> exception, and `f.get()` hands you the result. **This is how you get an answer back out of a pooled
> task** — the problem note `11` solved by hand with `wait()`/`notify()`.

---

# What this part established

| | |
|---|---|
| The problem | a **new thread per job** costs performance and memory |
| A thread pool is | **already-created threads, ready to do our job** |
| The analogy | a **connection pool** in JDBC |
| Why pools are necessary | a thread **cannot be restarted** — but a worker can take another job |
| Introduced in | **1.5**, as the **executor framework** |
| Create | `Executors.newFixedThreadPool(n)` |
| Submit | `service.submit(runnable)` |
| Shut down | `service.shutdown()` |
| What you stop writing | `new Thread(...)`, `start()`, thread bookkeeping |
| The proof of reuse | **`pool-1-thread-2` runs two different jobs** |
| Pool size | the **concurrency limit** — cores for CPU work, more for I/O |
| Forgetting `shutdown()` | the **JVM never exits** — pool threads are non-daemon |
| Submitting after shutdown | **`RejectedExecutionException`** |
| `shutdownNow()` | interrupts running jobs — needs jobs that **respond to interruption** |
| To wait | **`awaitTermination(t, unit)`** |
| For I/O-bound work today | **`newVirtualThreadPerTaskExecutor()`** — do not pool virtual threads |
| To get a result back | **`submit()` returns a `Future`**; use `Callable` for a return value |
