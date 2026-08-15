# What a daemon thread is

> **The threads which are executing in the background are called daemon threads.**

**Examples:** garbage collector, signal dispatcher, attach listener.

**These are the threads note `02` found** when it printed every live thread and discovered `main` was
not alone.

---

# What they are for

> **The main objective of daemon threads is to provide support for non-daemon threads (main thread).**

> [!question]- **The 70 mm screen, and the ten thousand people you never see.** His analogy for what
> "background support" means — and it is the same 70 mm screen note `01` used, now making a different
> point.
>
> On screen you see the hero, the heroine, a few character artists. **To put those people on screen,
> an enormous number of people work behind it.**
>
> *"Without makeup, can you please ask them to act on screen? Then we are much better than them.
> If heroines used their original voice, we would not be in a position to listen."*
>
> **Who is needed first?** The **producer** — without one there is nothing. Then the **director**. Then
> makeup, music director, choreographer, and so on.
>
> He describes visiting a shoot: a park scene with **two actors talking**. Around them: about **100
> supporting people**, ten controlling the onlookers, four or five buses, catering, and — the detail
> he enjoys — **the couples strolling in the background of the shot are also staff**, as are the
> balloon seller and the ice-cream vendor.
>
> **You never see the producer or the director on screen.** But without them nothing runs.
>
> > **The people in the background providing support are the daemon threads. The people on screen are
> > the non-daemon threads.**

## The concrete example

**The main thread runs low on memory.** The JVM runs the **garbage collector**, which destroys useless
objects so free memory improves — and **with that free memory the main thread continues.**

> **The garbage collector's purpose is to provide support for the main thread.** That is what a daemon
> thread does.

---

# Priority

> **Usually daemon threads run with low priority, but based on our requirement a daemon thread can run
> with high priority also.**

**The garbage collector traced through:**

| | main thread | garbage collector |
|---|---|---|
| normally | priority **5** | priority **1** — main keeps running |
| memory problem | | JVM **raises it to 10** — the collector runs |
| memory freed | | JVM **drops it back to 1** — main continues |

**Do not assume daemon means low priority permanently.** It is the default, not a rule.

---

# The three rules

## 1 — `isDaemon()` and `setDaemon()`

```java
public boolean isDaemon()
public void setDaemon(boolean b)
```

## 2 — Daemon status is inherited

Measured on JDK 25:

```
main thread isDaemon = false
default isDaemon     = false  (inherited from parent)
```

**The main thread is non-daemon**, so every thread it creates is non-daemon by default — exactly the
inheritance rule note `04` established for priority.

> [!info] **A daemon thread's children are daemons.** The property follows the parent thread in both
> directions, so a background worker that spawns helpers gets background helpers automatically.

## 3 — You cannot change it after `start()`

Measured on JDK 25:

```java
t.start();
t.setDaemon(true);      -> IllegalThreadStateException
```

> **We can change the daemon nature only before starting the thread. After starting, we get
> `IllegalThreadStateException`.**

> [!important] **The same exception as restarting a thread in note `02`.** `IllegalThreadStateException`
> is the JVM's general complaint that *"the thread is not in the right state for this request"* — and
> both cases are checks against `threadStatus` at the top of the method.

---

# When the JVM exits

**The rule that makes daemon threads worth having.**

> **Whenever the last non-daemon thread terminates, all daemon threads will be terminated
> automatically — regardless of their position.**

Measured on JDK 25, a **non-daemon** child:

```
  child thread 0
  child thread 1
  child thread 2
end of main thread (JVM will still wait)
  child thread 3
  ...
  child thread 9
```

**Main finished, and the JVM waited** for all ten iterations.

The same child made a **daemon**:

```
  child thread 0
  child thread 1
  child thread 2
end of main thread -> daemon dies with the JVM
```

**Killed mid-loop at count 2.** It never reached 3.

> [!important] **A daemon thread is not given a chance to finish, clean up, or run a `finally` block.**
> The JVM does not interrupt it or wait for it — it simply stops existing when the last non-daemon
> thread ends.
>
> **So never put anything that must complete in a daemon thread** — no writing a file, no flushing a
> buffer, no releasing an external resource. The moment the last real thread exits, your work is
> abandoned halfway.

## What this makes daemons good for

> [!info] **The right use is exactly the garbage collector's.** Work that is **useful while the
> application runs** and **pointless once it stops**: background monitoring, cache eviction, metrics
> collection, heartbeat pings.
>
> **The test to apply:** *if the JVM exited right now, mid-operation, would that be acceptable?* If
> yes, a daemon is right. If not, it must be a non-daemon thread and something must `join()` it.

---

# What this part established

| | |
|---|---|
| A daemon thread | executes **in the background** |
| Examples | **garbage collector**, signal dispatcher, attach listener |
| Their objective | **provide support for non-daemon threads** |
| The analogy | the crew behind the **70 mm screen** |
| Usual priority | **low** — but it can be high |
| The garbage collector | runs at 1, raised to **10** on memory pressure, dropped back |
| `isDaemon()` / `setDaemon()` | query and set |
| Default value | **inherited from the parent thread** |
| `main` is | **non-daemon** — so its children are too |
| Changing it after `start()` | ❌ **`IllegalThreadStateException`** |
| When the last non-daemon thread ends | **all daemons are killed immediately** |
| Do they finish, clean up, run `finally`? | ❌ **no** |
| Therefore | never put **essential work** in a daemon thread |
| The test | *would exiting mid-operation be acceptable?* |
