
Who runs the collector? **The JVM.** Not you. And when does it run it?

> When exactly the JVM runs GC, **we can't expect** — it varies from JVM to JVM.

Some JVMs might run it in the morning, some in the evening, some in the afternoon. That is Durga Sir's joke, but the underlying point is serious and it is the honest state of affairs: the timing is vendor behaviour, and nothing in your code determines it.

---

# Two facts before the methods

> [!important] **Eligible is not collected.** These are two separate events with an unknown gap between them. Making an object eligible does nothing on its own; it is destroyed only when the collector next runs, and that is the JVM's decision, not yours.
>
> **You can request, not command.** If you know a large number of objects are eligible, you can ask the JVM to run the collector. It usually accepts — but **acceptance is not guaranteed**, and there is no way to force it.

> [!warning] **The wording matters, and it is a common mistake.** People say `System.gc()` calls the garbage collector. It does not. **You cannot call the garbage collector directly.** You can only request that the JVM run it — and the JVM may decline. Say it the wrong way and you have shown that you think you control something you do not.

There are **two ways** to make that request: through the `System` class, and through the `Runtime` class.

---

# Way 1 — `System.gc()`

The `System` class, in `java.lang`, contains a **static** method for this purpose:

```java
System.gc();
```

That is the whole of it, and it is what most programmers actually use.

---

# Way 2 — the `Runtime` class

This one needs more setup, because it is really about how a Java application talks to the JVM at all.

## The conversation

Picture your Java application on one side and the JVM on the other. The application wants something.

- I want to create 10,000 objects. How much free memory is there in the heap? — the JVM answers with a number of bytes.
- And what is the total heap size? — another number.
- That free memory may not be enough. Can you please run your garbage collector?

Three questions, and each one is a method. But to ask any of them, the application needs an object to speak through:

> A Java application can communicate with the JVM by using the **`Runtime` object**

## Two words you need first

`Runtime` lives in `java.lang` — as does `System` — and getting hold of one requires understanding two terms.

> [!important] **Singleton class** — a class for which we are allowed to create **only one object**. `Runtime` is a singleton, so you cannot create it with `new` or through a constructor.
>
> **Factory method** — you call a method **using the class name**, and that method returns **an object of the same class**. That is how you obtain a singleton's instance.

Which gives the one line that matters:

```java
Runtime r = Runtime.getRuntime();
```

`getRuntime()` is called on the class, and it hands back a `Runtime` object. That is a factory method — a static one.

## The three methods

| Method | Returns |
|---|---|
| `freeMemory()` | number of bytes of **free** memory in the heap |
| `totalMemory()` | number of bytes of **total** heap memory |
| `gc()` | requests the JVM to run the garbage collector |

> [!info] **`freeMemory()` and `totalMemory()` are already covered in the JVM chapter**, in `05-The five memory areas` — together with `maxMemory()` and the room-and-chairs analogy for how the three relate. This chapter is only interested in them as a way of **seeing** the collector do something.

## The program


```java
import java.util.Date;

class RuntimeDemo {

    public static void main(String args[]) {
    
        Runtime r = Runtime.getRuntime();
        
        System.out.println("total memory of the heap :" + r.totalMemory());
        System.out.println("free memory of the heap :" + r.freeMemory());

        for (int i = 0; i < 10000; i++) {
            Date d = new Date();
            d = null;
        }

        System.out.println("free memory of the heap :" + r.freeMemory());
        
        r.gc();
        
        System.out.println("free memory of the heap :" + r.freeMemory());
    }
}
```

Read the loop first, because it is doing something deliberate: it creates a `Date`, then immediately sets `d = null`. That is **Way 1 from the previous part** — nullifying the reference — applied ten thousand times. By the end of the loop, ten thousand objects are eligible.

Run it on JDK 25 with **the heap pinned so it cannot resize**, which is what makes the numbers readable:

```
java -Xms64m -Xmx64m RuntimeDemo

total memory of the heap :67108864
free memory of the heap  :64882384     ← at start
free memory of the heap  :64882384     ← after creating 10,000 Dates
free memory of the heap  :65791384     ← after r.gc()
```

Two things to read off that.

**The loop moved nothing.** Free memory is identical before and after creating ten thousand objects. A `Date` is a small object and ten thousand of them are far below the granularity at which a 64 MB heap reports a change. Do not expect the allocation itself to show up.

**`r.gc()` did something.** Free memory rose by about 0.9 MB — the collector ran, found the ten thousand unreachable `Date` objects, and reclaimed the space. That rise is the whole point of the program: it is the collector's work made visible.

> [!warning] **Pin the heap, or the numbers will mislead you.** Without `-Xms`/`-Xmx`, the default heap on a modern JVM both starts far larger and **resizes underneath you**. On the same machine with default settings, free memory after `r.gc()` reads **13 MB — down from 267 MB**, which looks like a catastrophic failure and is not one. G1 handed unused memory back to the operating system, so `totalMemory()` collapsed with it, and `freeMemory()` means **free space within the total**.
>
> If you ever need to measure this on an unpinned heap, the number that behaves sensibly is **`totalMemory() − freeMemory()`** — the memory actually in use, which falls after a collection exactly as you would expect.

## The reasoning exercise — and why every answer is possible

Before running anything, Durga Sir works through it with round numbers, and this is the most useful part of the lecture. Suppose:

- total memory = **100 bytes**
- free memory at the start = **80 bytes**
- free memory after creating 10,000 objects = **60 bytes**

Twenty bytes went into those objects. Now you call `r.gc()` and print free memory again. **What number comes out?**

| Answer | Why it is possible |
|---|---|
| **50** | The JVM ignored the request — the collector never ran. Meanwhile running your program itself consumed a little memory, so free went **down**. |
| **60** | The request was ignored, and the program's own execution used a negligible amount. Unchanged. |
| **70** | The collector ran but did not destroy all ten thousand objects — maybe four or five thousand — and stopped once there was enough room. |
| **80** | The collector ran and destroyed all ten thousand, returning exactly to the starting figure. |
| **90** | The collector ran, destroyed all ten thousand, **and** collected some of the useless objects already sitting in the 20 bytes that were in use before the loop even started. |

> [!important] **Every one of those five is a legitimate outcome, and that is the lesson.** The request may be refused, may be partly honoured, or may collect more than you expected. There is no deterministic answer, and any exam question implying there is one is wrong.

---

# `System.gc()` versus `Runtime`: which, and why

## The difference that generates exam questions

> - `gc()` in the **`System`** class is a **static** method — so it is called on the class name.
> - `gc()` in the **`Runtime`** class is an **instance** method — so it is called on an object reference.

That single distinction is the basis of a standard certification question. Which of the following are valid ways to request the JVM to run GC?

| | Statement | | Why |
|---|---|---|---|
| 1 | `System.gc();` | **valid** | `gc()` is static in `System`, so calling it on the class name is correct |
| 2 | `Runtime.gc();` | **invalid** | `gc()` is an **instance** method in `Runtime` — it cannot be called on the class name |
| 3 | `(new Runtime()).gc();` | **invalid** | it is calling on an object, but `Runtime` is a **singleton** — you cannot construct one with `new` |
| 4 | `Runtime.getRuntime().gc();` | **valid** | the factory method gives you the object, and `gc()` is called on it |

Option 3 is the one that catches people, because at a glance it looks right — it **is** calling the instance method on an instance. The failure is one step earlier, in how the instance was obtained.

## Which is recommended?

Neither, in production code. But the reason the question exists is worth a minute, because it turns on how `System.gc()` is implemented:

```java
public static void gc() {
    Runtime.getRuntime().gc();
}
```

`System.gc()` does nothing but turn around and call the `Runtime` version. **They are the same call**, with one extra static hop — which the JIT inlines away, so there is no performance difference worth naming.

> [!info] **Verified in the JDK 25 sources.** Pulled from `src.zip`, `java.base/java/lang/System.java` — the body is still exactly `Runtime.getRuntime().gc();`. This has not changed since the video.

> [!important] **Do not call either one in production.** An explicit request can trigger a full, stop-the-world collection that is far more disruptive than whatever you were trying to fix, and it overrides tuning decisions the collector was making on better information than you have. Many deployments run with **`-XX:+DisableExplicitGC`**, which turns both calls into no-ops precisely so that library code cannot do it.
>
> For the interview: know the two forms, know which of the four spellings are valid, know that `System.gc()` delegates to `Runtime`. Then know that the answer to when would you call it? is **almost never** — and if you need it for a demo, `System.gc()` is the one everybody writes, because it is one line.

---

# Where this leaves us

| Question | Answer |
|---|---|
| Who runs the garbage collector? | the JVM |
| When? | vendor dependent — unpredictable |
| Can you force it? | **no** |
| Can you request it? | yes — `System.gc()` or `Runtime.getRuntime().gc()` |
| Will the request be honoured? | no guarantee, but usually |
| Which is more convenient? | `System.gc()` |
| Which is marginally faster? | `Runtime.getRuntime().gc()` |
| Which should you use in production? | neither, in almost all cases |

