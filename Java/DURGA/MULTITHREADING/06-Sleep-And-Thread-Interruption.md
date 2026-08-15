# `sleep()`

> **If a thread doesn't want to perform any operation for a particular amount of time, then we should
> go for the `sleep()` method.**

**Where you actually need it:**

| | |
|---|---|
| A **slide show** | rotate the slide, sleep two minutes, rotate, sleep two minutes |
| A **blinking bulb** in a GUI | show, sleep, hide, sleep |
| Anywhere a **fixed pause** is required | |

> [!question]- **The aside on sleeping, which is not about Java at all.** He stops the lecture for it,
> and it is one of the more forceful things he says.
>
> *"The worst thing in our life — which is going to kill our career — is nothing but sleeping only."*
>
> **At your age, six hours is the maximum.** *"If you sleep more than six hours, one nanosecond
> time — that nanosecond you are wasting. Not one minute or one hour. **One nanosecond.**"*
>
> He says he found a line in the Bible — *"sleeping makes a man very poor"* — underlined it, and wrote
> *"100% correct"* beside it. Then the observation behind it: he has watched students sleep through
> class, finish two or three years without a job, and end up borrowing 100 or 200 rupees from friends.
> *"Where was the cinema? In the classroom, sleeping."*
>
> **The observation he offers as evidence:** the person who is always attached to the bed is the person
> who is struggling, or about to be.

## The two overloads

```java
public static native void sleep(long milliseconds) throws InterruptedException
public static void sleep(long milliseconds, int nanoseconds) throws InterruptedException
```

Confirmed on JDK 25: **both static**, both throwing `InterruptedException`.

> [!important] **`join()` has a no-argument version; `sleep()` does not — and the reason is a good
> question.**
>
> **`join()` without an argument** means *"wait until that thread completes, however long that takes"*
> — a perfectly sensible request.
>
> **`sleep()` without an argument** would mean *"sleep forever"*. *"Sir, I want to sleep forever —
> that person is gone, recommended to send him out."* **There is no such thing**, so the method does
> not exist.
>
> **Whenever you sleep, a time period is compulsory.**

---

# Thread interruption

> **A thread can interrupt another sleeping or waiting thread by using the `interrupt()` method.**

```java
public void interrupt()
```

## The demo

```java
class MyThread extends Thread {
    public void run() {
        try {
            for (int i = 0; i < 5; i++) {
                System.out.println("I am lazy thread");
                Thread.sleep(2000);
            }
        } catch (InterruptedException e) {
            System.out.println("I got interrupted");
        }
    }
}

class ThreadInterruptDemo {
    public static void main(String[] args) {
        MyThread t = new MyThread();
        t.start();
        t.interrupt();                       // ← line 1
        System.out.println("End of main thread");
    }
}
```

Measured on JDK 25:

```
End of main thread
  I am lazy thread
  I got interrupted
```

**The loop printed once, not five times.** The thread slept, was interrupted, jumped to the `catch`,
and `run()` ended there.

| | |
|---|---|
| **With line 1** | the loop runs **once**, then `I got interrupted` |
| **Without line 1** | the loop runs **5 times**, and the `catch` never executes |

> [!info] **Which thread interrupts which.** `t.interrupt()` sits in `main`, so **the main thread
> interrupts the child thread.** Same shape as `join()` in note `05`: you call the method **on** the
> thread you are acting upon.

---

# The loophole

The question he builds to, and it is the interesting part:

> **What if you call `interrupt()` on a thread that is NOT sleeping and NOT waiting — one that is
> busy doing its job?**

His options: (1) an exception, (2) the interrupt call is wasted, (3) something else.

## Measured

```java
class Busy extends Thread {
    public void run() {
        for (int i = 0; i < 3; i++) System.out.println("busy: " + i);
        System.out.println("busy thread finished normally");
        Thread.sleep(100);                   // first sleep AFTER the interrupt
    }
}
b.start();
b.interrupt();       // while it is busy, not sleeping
```

Measured on JDK 25:

```
  busy: 0
  busy: 1
  busy: 2
  busy thread finished normally
  isInterrupted() at the end = true
  <- the STORED interrupt fired at the next sleep()
```

> **The interrupt call is not wasted, and no exception is thrown at the time. It is STORED.** The
> thread carries on undisturbed, and **the moment it next enters a sleeping or waiting state, the
> interrupt fires immediately** — `InterruptedException` at the very next `sleep()`.

> [!important] **This is the answer worth remembering, because both obvious guesses are wrong.**
>
> | Guess | |
> |---|---|
> | An exception is thrown right away | ❌ the thread is not sleeping, so there is nothing to interrupt |
> | The call is wasted | ❌ it is **remembered** |
> | **It is stored and applied at the next sleep/wait** | ✅ |
>
> **The mechanism:** every thread carries an **interrupt status flag**. `interrupt()` sets it.
> `sleep()` and `wait()` check it on entry and throw immediately if it is set. Measured above:
> `isInterrupted()` returned **`true`** while the thread was still running normally.

> [!warning] **Catching `InterruptedException` and ignoring it is a real bug.** The exception being
> thrown **clears** the interrupt status flag, so if you swallow it the interruption is lost and no
> code further up ever learns the thread was asked to stop.
>
> **The correct handling is one of two things:** let the exception propagate, or restore the flag
> before continuing —
> ```java
> catch (InterruptedException e) {
>     Thread.currentThread().interrupt();   // put the flag back
> }
> ```
> **This matters because interruption is how you cancel work in modern Java.** `Thread.stop()` is gone
> (note `02`), and executor shutdown is built on interruption — so a task that swallows the exception
> cannot be cancelled at all.

---

# `yield()`, `join()` and `sleep()` compared

The table these three sessions build to:

| | `yield()` | `join()` | `sleep()` |
|---|---|---|---|
| **Purpose** | give others of the same priority a chance | wait for **another thread** to finish | pause for **a fixed time** |
| **Static?** | ✅ static | ❌ instance, `final` | ✅ static |
| **Overloads** | **1** | **3** | **2** |
| **No-argument version** | ✅ | ✅ | ❌ **forever makes no sense** |
| **Throws `InterruptedException`** | ❌ | ✅ | ✅ |
| **Releases locks?** | ❌ | ❌ | ❌ |
| **Guaranteed?** | ❌ a **hint** | ✅ | ✅ (the duration is a minimum) |

> [!important] **The bottom row of that table is the one that gets examined.** **None of these three
> releases a lock** — only `wait()`, `notify()` and `notifyAll()` do (note `11`). A thread that sleeps
> or joins while holding a lock keeps it for the whole duration, which is how you build a deadlock by
> accident.

---

# What this part established

| | |
|---|---|
| `sleep()` | pause for **a particular amount of time** |
| Uses | slide shows, blinking displays, any **fixed pause** |
| Overloads | **two** — `(ms)` and `(ms, ns)` |
| Both are | **static**, both throw **`InterruptedException`** |
| No no-argument version | *"sleep forever"* is not a thing |
| `join()` has one | *"wait until it finishes"* is |
| `interrupt()` | one thread interrupting a **sleeping or waiting** thread |
| The effect | **`InterruptedException`** in the sleeping thread |
| Interrupting a **busy** thread | **not wasted, not an exception** — it is **stored** |
| When it fires | at the **next** `sleep()` or `wait()` |
| The mechanism | an **interrupt status flag** on every thread |
| The exception **clears** the flag | so swallowing it **loses** the interruption |
| Correct handling | rethrow, or **restore the flag** with `Thread.currentThread().interrupt()` |
| Why it matters | interruption is **how cancellation works** now that `stop()` is gone |
| None of `yield`/`join`/`sleep` | **releases a lock** |
