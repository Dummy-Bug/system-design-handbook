# Deadlock

> *"What is a deadlock? A lock without a key."*

The technical definition:

> **If two threads are waiting for each other forever, such type of infinite waiting is called
> deadlock.**

Ask the first thread why it is waiting: *"I'm waiting for the second thread."* Ask the second:
*"I'm waiting for the first."* **Neither will ever move.**

---

# `synchronized` is the cause

> **The `synchronized` keyword is the only reason for a deadlock situation.**

> [!important] **This reframes the keyword completely.** Note `07` introduced `synchronized` as the
> solution to data inconsistency. Here it is the **problem creator**:
>
> > *"Sir, I don't use the `synchronized` keyword — then I'm sure your program never enters a deadlock
> > situation."*
>
> **No `synchronized`, no deadlock. Guaranteed.** Which is another reason for the rule from note `07`:
> **if there is no specific requirement, never use it.**

## There is no cure

> **There are no resolution techniques for deadlock, but several prevention techniques are
> available.**

> [!warning] **Once a program is deadlocked, nothing can be done from inside it.** You cannot detect
> and recover in code — the threads are blocked in the JVM, not in your logic. **The only remedy is to
> kill the process.**
>
> *"Prevention is better than cure"* — and here there is no cure at all.

---

# A program that deadlocks

```java
class A {
    public synchronized void d1(B b) {
        System.out.println("Thread1 starts execution of d1() method");
        try { Thread.sleep(6000); } catch (InterruptedException e) {}
        System.out.println("Thread1 trying to call B's last()");
        b.last();
    }
    public synchronized void last() {
        System.out.println("Inside A, this is last() method");
    }
}

class B {
    public synchronized void d2(A a) {
        System.out.println("Thread2 starts execution of d2() method");
        try { Thread.sleep(6000); } catch (InterruptedException e) {}
        System.out.println("Thread2 trying to call A's last()");
        a.last();
    }
    public synchronized void last() {
        System.out.println("Inside B, this is last() method");
    }
}

class DeadLock extends Thread {
    A a = new A();
    B b = new B();

    public void m1() { this.start(); a.d1(b); }     // main thread runs a.d1(b)
    public void run()  { b.d2(a); }                 // child thread runs b.d2(a)

    public static void main(String[] args) {
        DeadLock dl = new DeadLock();
        dl.m1();
    }
}
```

Measured on JDK 25:

```
Thread1 starts execution of d1() method
Thread2 starts execution of d2() method
Thread1 trying to call B's last()
Thread2 trying to call A's last()
```

**And then nothing, forever.** The program had to be killed.

## The trace

| Step | Main thread | Child thread |
|---|---|---|
| 1 | enters `a.d1(b)` — **takes A's lock** | enters `b.d2(a)` — **takes B's lock** |
| 2 | sleeps 6s | sleeps 6s |
| 3 | calls `b.last()` — **needs B's lock** | calls `a.last()` — **needs A's lock** |
| 4 | **B's lock is held by the child** → waits | **A's lock is held by main** → waits |

```mermaid
flowchart LR
    M["<b>main</b><br/>holds A's lock"] -->|"needs B's lock"| C["<b>Thread-0</b><br/>holds B's lock"]
    C -->|"needs A's lock"| M
```

> [!important] **The `sleep(6000)` is what makes it reliable.** Without it, one thread would probably
> finish before the other started, and the deadlock would only appear occasionally. **The sleep
> guarantees both threads grab their first lock before either asks for the second** — which is exactly
> the interleaving that deadlocks.
>
> **In production this is what makes deadlocks so nasty:** they need a specific timing, so they pass
> every test and appear under load.

> [!question]- **The negotiation that goes nowhere.** His dramatisation of why neither thread will
> yield — and it is why the situation is unrecoverable.
>
> He walks up to Thread1: *"Do you have any lock with you?"* — *"Yes, I have A's lock."* — *"Then why
> are you waiting?"* — *"I want B's lock."*
>
> Thread2: *"Yes, I have B's lock. I'm waiting for A's lock."*
>
> So he negotiates. **To Thread1:** *"You're waiting anyway — you can't do anything with that lock.
> Release it, and within one minute I'll get you both locks."*
>
> **Thread1:** *"First bring me B's lock, then within half a minute I'll release mine."*
>
> **To Thread2**, the same offer. **Thread2:** *"First bring me A's lock, then I'll release mine."*
>
> **Each will only release after receiving.** There is no order in which anyone can go first — which
> is precisely why no resolution technique exists.

---

# The JVM detects it

Modern JVMs will tell you. Taking a thread dump of the hung process:

```
Found one Java-level deadlock:
=============================
"main":
  waiting to lock monitor 0x0000600001bf0270 (object 0x000000070fe193d8, a B),
  which is held by "Thread-0"

"Thread-0":
  waiting to lock monitor 0x0000600001bf0340 (object 0x000000070fe18828, a A),
  which is held by "main"

Java stack information for the threads listed above:
===================================================
"main":
	at B.last(DeadLock.java:17)
	- waiting to lock <0x000000070fe193d8> (a B)
	at A.d1(DeadLock.java:6)
	- locked <0x000000070fe18828> (a A)
```

Measured on JDK 25 with `jcmd <pid> Thread.print`.

> [!important] **This is the practical skill worth having: when a Java process hangs, take a thread
> dump.** `jcmd <pid> Thread.print` or `jstack <pid>` — and the JVM does the cycle detection for you,
> naming both threads, both objects, and the exact lines.
>
> **It does not fix anything** — the process is still dead — but it turns *"the server is frozen"*
> into a two-line diagnosis. This is the tooling the `GARBAGE-COLLECTION` notes flagged as missing from
> the course, doing real work.

## Prevention

> [!info] **The standard prevention technique, since he leaves it to the OS course.** **Always acquire
> multiple locks in the same global order.** The program above deadlocks because main takes A then B,
> while the child takes B then A. **If both took A then B, no cycle could form** — whoever gets A first
> proceeds, and the other waits for A without holding B.
>
> Other approaches: hold one lock at a time; use `tryLock()` with a timeout from
> `java.util.concurrent.locks` (part 17) so a thread can back off instead of blocking forever.

---

# Deadlock versus starvation

The distinction he closes on, and it is examinable.

| | **Deadlock** | **Starvation** |
|---|---|---|
| The waiting is | **infinite** | **long, but finite** |
| Will it ever end? | ❌ **never** | ✅ **eventually** |

> **Long waiting of a thread, where the waiting never ends, is a deadlock. Long waiting which ends at
> some point is starvation.**

> [!info] **The example: a low-priority thread with high-priority threads constantly arriving.** It
> waits, and waits — but the moment there are no high-priority threads left, **it gets the CPU**. It
> was starved, not deadlocked.
>
> **The test to apply:** *is there any future in which this thread proceeds?* If yes, starvation. If
> the answer is no by construction, deadlock.

---

# What this part established

| | |
|---|---|
| Deadlock | two threads **waiting for each other forever** |
| The cause | **the `synchronized` keyword** — the only one |
| No `synchronized` | **no deadlock**, guaranteed |
| Resolution techniques | **none** |
| Prevention techniques | **several** |
| The classic shape | two threads take **two locks in opposite orders** |
| Why `sleep` is in the demo | it **guarantees** the bad interleaving |
| Why real deadlocks are hard | they need **specific timing** — they pass tests, fail under load |
| Why nobody yields | each will release **only after receiving** |
| Diagnosis | **`jcmd <pid> Thread.print`** — the JVM finds the cycle itself |
| The standard prevention | acquire multiple locks in **the same global order** |
| Alternative | **`tryLock()` with a timeout** |
| **Starvation** | long waiting that **does eventually end** |
| The test | *is there any future where this thread proceeds?* |
