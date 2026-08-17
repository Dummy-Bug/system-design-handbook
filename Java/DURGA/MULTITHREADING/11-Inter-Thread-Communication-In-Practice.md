# The five conclusions so far

Note `10`'s results, collected — he spends an hour and a half on these alone:

> **1.** Two threads can communicate using **`wait()`, `notify()`, `notifyAll()`**.
> **2.** These methods are in the **`Object`** class, not `Thread`.
> **3.** They can be called **only from a synchronized area** — otherwise `IllegalMonitorStateException`. **4.** If a thread calls **`wait()`**, it releases the lock **immediately** and enters the waiting state. **5.** If a thread calls **`notify()`**, it releases the lock — **but not necessarily immediately**.

> [!important] **Conclusion 5 is the one that differs from 4, and the wording matters.** `wait()` releases the lock **at once**, because the whole point is to let the other thread in. `notify()` only releases the lock **when it leaves the synchronized block** — the notifying thread carries on to the end of its block first.

> **`wait()`, `notify()` and `notifyAll()` are the ONLY methods where a thread releases a lock.** Except for these, a thread never gives up a lock it holds.

**The reason is self-evident once stated:** if the waiting thread did not release the lock, the notifying thread could never get in to perform the update — and if the notifier never released it, the waiter could never resume. **Communication requires both sides to let go.**

---

# The problem, in code

```java
class ThreadB extends Thread {
    int total = 0;

    public void run() {
        for (int i = 1; i <= 100; i++)
            total = total + i;
    }
}

class ThreadA {
    public static void main(String[] args) {
        ThreadB b = new ThreadB();
        b.start();
        System.out.println(b.total);       // main thread wants the answer
    }
}
```

**The child computes 1+2+…+100 = 5050.** The main thread wants to print it.

## What actually gets printed

Measured on JDK 25, six consecutive runs:

```
0  0  0  0  0  0
```

**Zero every time** — `main` reaches the print before the child has done anything.

> [!important] **But zero is not the only possible answer, and that is worse than always being wrong.** Three outcomes are possible:
>
> | | When |
> |---|---|
> | **0** | main prints before the child starts |
> | **5050** | the child finishes first |
> | **anything between** | main prints while the child is **mid-loop** — 1653, 4851, … |
>
> His own runs produced `4851` and `1653`. **A bug that usually gives 0 and occasionally gives 1653 is far harder to find than one that always fails.**

---

# Three fixes, two of them wrong

## Attempt 1 — `sleep()`

```java
b.start();
Thread.sleep(10000);        // wait 10 seconds, surely that's enough
System.out.println(b.total);
```

**It gives 5050.** And it is wrong anyway.

> [!question]- **Ten seconds — will the loop finish?** The exchange with the class, and the point he is making about underestimating the machine.
>
> He asks the class whether a 100-iteration loop will finish within 10 seconds. **Most say it may not.**
>
> > Make sure — you people are unfit for a software engineering job, because you are underestimating the computer. In one nanosecond a computer can perform millions of operations.
>
> He walks it down: 10 seconds? Yes. **1 second?** Yes. **100 milliseconds?** Yes. **10 milliseconds?** Yes. **1 millisecond?** Yes. **1 nanosecond?** Don't keep any doubt — 5050 is the answer.
>
> The lesson is not really about `sleep`. It is that **a loop of 100 additions is nothing**, and intuitions about how long code takes are usually off by orders of magnitude.

**Why `sleep()` is still the wrong answer — two reasons:**

1. **You sleep too long.** If the update is ready in a microsecond, the other 9.999 seconds are pure waste, and system performance suffers.
2. **You might not sleep long enough.** For a bigger calculation, 10 seconds may not be enough — and then you print an **intermediate value** and never know.

> **When the update will be ready, we don't know. So sleeping for a fixed amount of time is not good programming practice.**

## Attempt 2 — `join()`

```java
b.start();
b.join();                   // wait for the child to finish
System.out.println(b.total);
```

**Also gives 5050.** Also wrong.

**Why:** `join()` waits for the **entire thread** to finish. Suppose `run()` is:

```java
public void run() {
    for (int i = 1; i <= 100; i++) total = total + i;    // update ready HERE
    // … one crore more lines of code …
}
```

> **The update is ready after the for loop. But with `join()` my main thread waits until the whole crore of lines is done too. Why should I wait when the value I need was ready in the middle?**

## Attempt 3 — `wait()` and `notify()`

```java
class ThreadB extends Thread {
    int total = 0;

    public void run() {
        synchronized (this) {
            for (int i = 1; i <= 100; i++)
                total = total + i;
            this.notify();                 // update is ready — tell the waiter
        }
    }
}

class ThreadA {
    public static void main(String[] args) throws InterruptedException {
        ThreadB b = new ThreadB();
        b.start();

        synchronized (b) {
            b.wait();                      // wait for the notification
            System.out.println(b.total);
        }
    }
}
```

Measured on JDK 25:

```
total = 5050
```

> **The main thread is not required to wait a single extra nanosecond.** The moment the update is ready, `notify()` fires and the waiter resumes — no fixed delay, no waiting for unrelated work.

## The comparison

| Approach | Correct? | Problem |
|---|---|---|
| nothing | ❌ | **0, 5050, or anything between** |
| `sleep(n)` | ⚠️ | too long **wastes time**; too short gives a **wrong value** |
| `join()` | ⚠️ | waits for the **whole thread**, not for the **update** |
| **`wait()` / `notify()`** | ✅ | waits for **exactly the event you care about** |

> [!important] **The distinction worth carrying: `join()` waits for a THREAD; `wait()` waits for a CONDITION.** If what you need is this thread is completely done, `join()` is the right and simpler tool. If what you need is this particular thing has happened — and work continues afterwards — only `wait`/`notify` expresses it.

---

# Both sides need the synchronized area

**Remove the `synchronized` blocks and the program compiles but throws.** Measured on JDK 25:

```
java.lang.IllegalMonitorStateException
```

**Conclusion 3 in action.** `b.wait()` needs the lock of `b`, so it must be inside `synchronized (b)`. `this.notify()` needs the lock of the child object, so it must be inside `synchronized (this)`.

> [!warning] **Always call `wait()` inside a loop, not an `if`.** The idiom every real codebase uses is:
> ```java
> synchronized (b) {
>     while (!b.ready)      // not: if (!b.ready)
>         b.wait();
>     use(b.total);
> }
> ```
> **Two reasons.** A thread can wake from `wait()` **without any notification at all** — a **spurious wakeup**, which the specification explicitly permits. And with several waiters, `notifyAll()` wakes everyone, so by the time your thread reacquires the lock another may already have consumed the update.
>
> **The one-line rule: after waking, re-check the condition that made you wait.** The example above works because there is exactly one waiter and one notifier — real code rarely has that guarantee.

---

# What this part established

| | |
|---|---|
| `wait()` releases the lock | **immediately** |
| `notify()` releases the lock | **not necessarily immediately** — at the end of its block |
| These three are | the **only** methods where a thread releases a lock |
| Why both must release | otherwise the update or the notification could never happen |
| Without coordination | **0, 5050, or any intermediate value** |
| Why that is dangerous | it usually gives one wrong answer and **occasionally** another |
| `sleep(n)` | ❌ too long **wastes time**, too short gives a **wrong value** |
| `join()` | ❌ waits for the **whole thread**, not the **update** |
| `wait()` / `notify()` | ✅ waits for **exactly the event** |
| The distinction | **`join()` waits for a thread; `wait()` waits for a condition** |
| Both sides need | a **synchronized** area on the same object |
| Otherwise | **`IllegalMonitorStateException`** |
| Always wait in | a **`while` loop**, never an `if` — spurious wakeups are permitted |
