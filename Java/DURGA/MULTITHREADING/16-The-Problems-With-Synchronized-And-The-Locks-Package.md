# The five problems with `synchronized`

Note `07` promised this: *"treat `synchronized` as the hero for now — after a few classes it will
become zero."* **This is where that happens.**

The two headline complaints are already known: **performance** (threads wait) and **deadlock**
(`synchronized` is the only cause, note `12`). Here they are itemised properly.

---

## 1 — No way to try for a lock without waiting

With `synchronized`, if the lock is unavailable, **the thread waits. That is the only option.** How
long? *"Maybe within 1 minute, or 10 minutes, or 1 hour, or 10 days — I don't know."*

> **What you want instead:** *"Try for the lock. If it is available, give it to me. If not, don't make
> me wait — I will do alternative work."*

> [!info] **The bus stop.** With `synchronized`, you wait for the bus however long it takes. What you
> want is: *"Is a bus here? Then I get on. Not here? I won't wait — I'll make another arrangement and
> carry on."*

## 2 — No way to specify a maximum waiting time

You cannot say *"wait up to 10 minutes for this lock, and if I don't get it, continue with something
else."* **It is wait forever or nothing.**

**And this is the deadlock connection:** a thread that can give up after a timeout **cannot be
deadlocked**.

## 3 — No control over which waiting thread gets the lock

Three threads are waiting, the lock is released. **Which one gets it?** Whatever the scheduler
decides. **There is no way to say "the longest-waiting thread should get it."**

## 4 — No API to list the waiting threads

**How many threads are waiting for this lock?** Four? Five? Eight? **There is no way to ask.**

## 5 — `synchronized` cannot span multiple methods

`synchronized` works **at method level** or **inside one method**. But consider:

```java
void m1() {
    // … acquire the lock HERE …
    m2();
    // … from here on the lock is not needed …
}

void m2() {
    // … still need the lock for part of this …
    // … release it HERE, in a different method …
}
```

> **Across multiple methods, `synchronized` cannot help.** You cannot open a lock in one method and
> close it in another.

---

# `java.util.concurrent.locks`

> **To overcome these problems, `java.util.concurrent.locks` was introduced in 1.5.**

> [!important] **Once you start using this package, you can stop using `synchronized` altogether.**
> *"Not required to use the `synchronized` keyword any more. But very unfortunately most programmers
> don't know about it, so people are still using `synchronized`."*

**Each problem, answered.** Measured on JDK 25 with `ReentrantLock`:

## 1 — `tryLock()`

```java
if (lock.tryLock()) {
    try { /* safe operations */ } finally { lock.unlock(); }
} else {
    /* alternative operations — no waiting at all */
}
```

```
did NOT get the lock -> doing alternative work instead
```

**Returns immediately** with `true` or `false`. **Never blocks.**

## 2 — `tryLock(time, unit)`

```java
boolean ok = lock.tryLock(1, TimeUnit.SECONDS);
```

```
waited 1006ms, acquired=false
```

**Waited exactly one second, then gave up** — and carried on.

> [!important] **This is the practical deadlock cure.** A thread that backs off after a timeout can
> release what it holds and retry, so the circular wait from note `12` cannot persist. **There is no
> resolution technique for a `synchronized` deadlock; with a timeout, the deadlock resolves itself.**

## 3 — the fairness policy

```java
ReentrantLock fair = new ReentrantLock(true);
```

```
new ReentrantLock(true).isFair()  = true
new ReentrantLock().isFair()      = false
```

**With fairness on, the longest-waiting thread gets the lock.** *"Be a bit fair — don't do fraud."*

> [!info] **Fairness is off by default, deliberately.** A fair lock must maintain the queue order,
> which costs throughput. **Turn it on when starvation matters** (note `12`), leave it off when
> throughput does.

## 4 — inspecting the waiters

```java
lock.getQueueLength()      // how many threads are waiting
lock.hasQueuedThreads()    // is anyone waiting?
lock.isLocked()            // is it held right now?
```

**Exactly the API `synchronized` never had.**

## 5 — locking across methods

```java
static void m1() { lock.lock();  m2();  /* … */ }
static void m2() { /* … */ lock.unlock(); }
```

Measured on JDK 25:

```
m1: acquired
m2: still holding it, now releasing HERE
m1: done
```

**Acquired in one method, released in another.** Impossible with `synchronized`.

---

# The trade you are making

> [!warning] **`lock()` and `unlock()` are not automatic — and that is the one real disadvantage.**
> `synchronized` releases the lock when the block exits, **however it exits**, including on an
> exception. A `Lock` does not.
>
> **So every `lock()` must be paired with `unlock()` in a `finally`:**
> ```java
> lock.lock();
> try {
>     // critical section
> } finally {
>     lock.unlock();      // ALWAYS, even if the body throws
> }
> ```
> **Forget the `finally` and one exception leaks the lock permanently** — every other thread blocks
> forever, which is a worse outcome than anything `synchronized` can produce. This is the trade:
> **more power, no safety net.**

---

# What this part established

| | |
|---|---|
| Problem 1 | no way to **try** for a lock without waiting |
| Problem 2 | no way to specify a **maximum waiting time** |
| Problem 3 | no control over **which** waiting thread gets the lock |
| Problem 4 | no **API** to list waiting threads |
| Problem 5 | cannot span **multiple methods** |
| The answer | **`java.util.concurrent.locks`**, since **1.5** |
| `tryLock()` | returns **immediately**, `true` or `false` |
| `tryLock(time, unit)` | waits **at most** that long |
| Why that cures deadlock | a thread can **back off** instead of waiting forever |
| Fairness policy | `new ReentrantLock(true)` — **longest waiting thread** wins |
| Default | **unfair**, for throughput |
| Inspection | `getQueueLength()` · `hasQueuedThreads()` · `isLocked()` |
| Across methods | `lock()` in one, `unlock()` in another |
| The cost | **you must call `unlock()` yourself** |
| Always | put `unlock()` in a **`finally`** |
