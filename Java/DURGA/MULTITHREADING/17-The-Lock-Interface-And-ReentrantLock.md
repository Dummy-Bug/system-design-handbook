# The `Lock` interface

> **`Lock` is a similar mechanism to the implicit lock acquired by `synchronized`, but with extended
> capabilities.**

## The methods

| Method | |
|---|---|
| `void lock()` | acquire the lock — **waits** if unavailable |
| `boolean tryLock()` | acquire **only if free**; returns immediately either way |
| `boolean tryLock(long time, TimeUnit unit)` | wait **at most** this long |
| `void lockInterruptibly()` | acquire the lock, but **allow interruption** while waiting |
| `void unlock()` | release the lock |

Confirmed on JDK 25 — `Lock` declares `lock`, `lockInterruptibly`, `tryLock` (×2), `unlock`, and
`newCondition`.

> [!important] **`lockInterruptibly()` is the one worth noticing.** A thread blocked in `lock()`
> ignores `interrupt()` completely, exactly like a thread blocked entering a `synchronized` method.
> **`lockInterruptibly()` lets a waiting thread be interrupted** — so it can be cancelled instead of
> blocking forever.
>
> That is the connection to note `06`: interruption is how cancellation works, and `synchronized`
> is deaf to it.

---

# `ReentrantLock`

> **`ReentrantLock` is the implementation class of the `Lock` interface, and it is a direct child
> class of `Object`.**

Confirmed on JDK 25: `ReentrantLock`'s superclass is **`Object`**.

## What "reentrant" means

> **A thread can acquire the same lock multiple times without any issue.**

**Internally the lock keeps a hold count per thread.** `lock()` increments it, `unlock()` decrements
it, and **the lock is released only when the count reaches zero.**

Measured on JDK 25:

```
start            holdCount = 0  isLocked=false
after lock()     holdCount = 1  isLocked=true
after lock()     holdCount = 2
after lock()     holdCount = 3
after unlock()   holdCount = 2  isLocked=true   <- still held
after unlock()   holdCount = 1  isLocked=true
after unlock()   holdCount = 0  isLocked=false  <- NOW released
```

> [!important] **One `unlock()` does not release a lock taken three times.** *"Even one-time unlock,
> no effect."* You must call `unlock()` **exactly as many times as you called `lock()`** — which is
> another reason the `try`/`finally` discipline from note `16` matters.

> [!info] **Why reentrancy is necessary, not a luxury.** Without it, a synchronized method calling
> another synchronized method **on the same object** would deadlock against itself — the thread would
> wait for a lock it already holds.
>
> **`synchronized` is reentrant too**, and always has been. Verified on JDK 25: a `synchronized`
> method calling another `synchronized` method on the same object works fine. `ReentrantLock` is named
> for the property because a `Lock` implementation *could* choose otherwise; the name tells you this
> one does not.

## The two constructors

```java
ReentrantLock l = new ReentrantLock();                 // creates a ReentrantLock
ReentrantLock l = new ReentrantLock(boolean fairness); // with the given fairness policy
```

Confirmed on JDK 25: **2** constructors.

| Fairness | Behaviour |
|---|---|
| **`true`** | the **longest waiting thread** acquires the lock if available — **first-come-first-served** |
| **`false`** *(default)* | **no guarantee** which waiting thread gets it |

> *"Be a bit fair — don't do fraud, don't be biased."*

> [!info] **The default is `false`, and that is a performance decision.** A fair lock must hand the
> lock to the head of the queue, which often means parking one thread and unparking another. An unfair
> lock lets a thread that is *already running* barge in and take it — fewer context switches, higher
> throughput.
>
> **Use fairness when starvation is the risk** (note `12`), not by default.

---

# The useful query methods

`ReentrantLock` adds methods `Lock` does not declare — the API note `16` said `synchronized` never had:

| Method | |
|---|---|
| `int getHoldCount()` | how many holds **the current thread** has |
| `boolean isLocked()` | is it held by **anyone**? |
| `boolean isHeldByCurrentThread()` | is it held by **me**? |
| `int getQueueLength()` | how many threads are **waiting** |
| `boolean hasQueuedThreads()` | is anyone waiting? |
| `boolean isFair()` | was it built with fairness? |

---

# Unlocking a lock you do not hold

Measured on JDK 25:

```java
new ReentrantLock().unlock();     -> IllegalMonitorStateException
```

> [!important] **The same exception as `wait()` outside a synchronized block** (note `10`).
> `IllegalMonitorStateException` always means one thing: **you tried to do something with a lock you
> do not own.**

---

# The shape of correct code

```java
Lock l = new ReentrantLock();

l.lock();
try {
    // critical section
} finally {
    l.unlock();
}
```

> [!warning] **The `finally` is not optional.** `synchronized` releases its lock on any exit path,
> including an exception. **A `Lock` does not** — miss the `finally` and one exception leaves the lock
> held forever, blocking every other thread permanently.
>
> **And with a `tryLock()`, unlock only if you actually got it:**
> ```java
> if (l.tryLock()) {
>     try { /* … */ } finally { l.unlock(); }
> } else {
>     /* alternative work */
> }
> ```
> Calling `unlock()` after a failed `tryLock()` throws `IllegalMonitorStateException`.

---

# `synchronized` versus `Lock`

The comparison this block of the chapter builds to:

| | `synchronized` | `Lock` |
|---|---|---|
| Acquire | implicit, on entry | **explicit** — `lock()` |
| Release | **automatic**, on any exit | **manual** — `unlock()` in a `finally` |
| Try without waiting | ❌ | ✅ **`tryLock()`** |
| Wait with a timeout | ❌ | ✅ **`tryLock(t, unit)`** |
| Interruptible while waiting | ❌ | ✅ **`lockInterruptibly()`** |
| Fairness | ❌ | ✅ **constructor flag** |
| Inspect waiters | ❌ | ✅ `getQueueLength()`, … |
| Span multiple methods | ❌ | ✅ |
| Reentrant | ✅ | ✅ |
| Can leak the lock | ❌ **impossible** | ✅ **if you forget `finally`** |

> [!important] **The last row is why `synchronized` has not disappeared.** It is safer by
> construction — there is no way to forget to release it. **Reach for a `Lock` when you need one of
> the capabilities above**; otherwise `synchronized` is simpler and cannot be got wrong.

---

# What this part established

| | |
|---|---|
| `Lock`'s methods | `lock` · `tryLock` · `tryLock(t,u)` · `lockInterruptibly` · `unlock` |
| `lockInterruptibly()` | waiting for the lock **can be interrupted** — `synchronized` cannot |
| `ReentrantLock` | the implementation class; direct child of **`Object`** |
| Reentrant means | a thread can acquire the **same lock multiple times** |
| The mechanism | a **hold count**, incremented by `lock()`, decremented by `unlock()` |
| The lock is released | only when the count reaches **zero** |
| Measured | 0 → 1 → 2 → 3 → 2 → 1 → **0** |
| `synchronized` is | **also reentrant** |
| Why reentrancy is needed | a synchronized method calling another would **deadlock against itself** |
| Two constructors | default, and **`(boolean fairness)`** |
| Fairness `true` | **longest-waiting thread** wins — first-come-first-served |
| Default | **`false`**, for throughput |
| Query methods | `getHoldCount` · `isLocked` · `isHeldByCurrentThread` · `getQueueLength` · `isFair` |
| `unlock()` without holding it | **`IllegalMonitorStateException`** |
| The required shape | `lock(); try { … } finally { unlock(); }` |
| Why `synchronized` survives | it **cannot leak** a lock |
