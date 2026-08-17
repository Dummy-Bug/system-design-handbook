# `ThreadLocal`

> **`ThreadLocal` can be used to define a thread-scope variable.**

**The name says it: a variable that is local to a thread.**

> [!info] **The servlet scopes analogy he starts from.** In servlets, data can be stored at different **scopes**:
>
> | Scope | Lives for |
> |---|---|
> | **request** | one request — gone once that request is processed |
> | **session** | the whole session — you log into Gmail once, and every subsequent action knows who you are until you log out |
>
> **`ThreadLocal` adds a third: thread scope.** Data stored there is available **everywhere that thread goes**, for as long as it lives.

---

# The problem it solves

```java
public static void main(String[] args) {    // executed by the main thread
    m1();
}
void m1() { m2(); }
void m2() { /* the data fetched earlier is needed HERE */ }
```

**You fetched something at the top — a transaction ID, a database connection, a user ID — and you need it three calls deep.** The options without `ThreadLocal`:

- **pass it as a parameter** through every method in the chain, including methods that do not care about it
- **make it a static field** — but then every thread shares one value, which is wrong

> **`ThreadLocal` maintains a separate copy for every thread**, so each thread reads and writes its own without passing anything.

## The typical uses

> **For every thread a separate database connection is required. For every thread a separate counter variable. For every thread a separate customer ID.**

> [!question]- **The servlet transaction ID.** His worked scenario, and it is the realistic one.
>
> A servlet invokes several business methods, and you must **generate a unique transaction ID for each request** and make it available to all of them.
>
> **In the single-instance-multi-threaded servlet model, one thread is created per request.** So unique per request and unique per thread are the same requirement — and a `ThreadLocal` holding the transaction ID gives every business method access to the right one **without changing a single method signature**.

> [!important] **Without `ThreadLocal`, the programmer maintains this by hand.** If there are 1000 threads, how many counter variables must you maintain? 1000. You would need a map from thread to value, and you would have to clean it up. **`ThreadLocal` is that map, managed for you.**

---

# The methods

| Method | |
|---|---|
| `Object get()` | the **calling thread's** value |
| `void set(Object value)` | set the calling thread's value |
| `void remove()` | remove the calling thread's value |
| `protected Object initialValue()` | the value before any `set()` — **`null`** by default |

## Measured

```java
static ThreadLocal<Integer> plain = new ThreadLocal<>();
```

**Before any `set()`:**

```
main sees: null   <- null, not an error
```

**Three threads, each setting its own value:**

```
T3 set  55
T2 set  54
T1 set  53
T2 still sees 54  <- unaffected by others
T1 still sees 53  <- unaffected by others
T3 still sees 55  <- unaffected by others
main still sees: null  <- never touched
```

**One `ThreadLocal` object, four independent values.** Measured on JDK 25.

> **A thread can access its own local variable, and cannot access another thread's local variable.** T1's count cannot be read by T2, and vice versa.

**`remove()`:**

```
before remove: 99
after  remove: null
```

---

# Setting an initial value

**The classic form** — override `initialValue()` with an anonymous inner class:

```java
ThreadLocal<String> tl = new ThreadLocal<String>() {
    protected String initialValue() { return "abc"; }
};
```

Measured on JDK 25: `tl.get()` → **`abc`**, without any `set()`.

> [!important] **The modern form is one line**, added in Java 8:
> ```java
> ThreadLocal<Integer> tl = ThreadLocal.withInitial(() -> counter.incrementAndGet());
> ```
> Measured on JDK 25, three threads reading it:
> ```
> A -> 1
> B -> 2
> C -> 3
> ```
> **The supplier runs once per thread**, on that thread's first `get()` — which is exactly how you give each thread a distinct ID. **Prefer `withInitial()`**; the anonymous-subclass form still works and is what older code uses.

---

# Lifecycle

> **Once a thread enters the dead state, all its thread-local variables are eligible for garbage collection.**

**Values live and die with their thread**, so ordinary short-lived threads need no cleanup.

> [!warning] **With a thread POOL, this guarantee disappears — and it becomes a memory leak.** Pool threads (note `18`) **do not die** between tasks. A value set during one task **stays attached to that thread** and is visible to the next, unrelated task that thread picks up.
>
> **Two consequences, both bad:**
> - **data leaks between requests** — task B sees task A's user ID
> - **the object is never collected**, because the pool thread lives for the life of the application
>
> **The fix is always the same shape:**
> ```java
> try {
>     context.set(value);
>     doWork();
> } finally {
>     context.remove();      // ALWAYS
> }
> ```
> **`remove()` in a `finally`** — the same discipline as `unlock()` in note `17`, for the same reason. This is the single most common `ThreadLocal` bug in server code.

## Version

> **`ThreadLocal` was introduced in 1.2, and enhanced in 1.5** — it is not a 1.5 addition, which is worth knowing since the rest of this block is.

---

# What this part established

| | |
|---|---|
| `ThreadLocal` defines | a **thread-scope** variable |
| The analogy | servlet **request** and **session** scopes — this is **thread** scope |
| The problem | data needed deep in a call chain, **different per thread** |
| The alternatives | passing parameters everywhere, or a **shared static** that is wrong |
| Each thread gets | its **own copy**, from one `ThreadLocal` object |
| A thread **cannot** access | **another thread's** value |
| Methods | `get()` · `set(v)` · `remove()` · `initialValue()` |
| Default before `set()` | **`null`** |
| Classic initial value | override **`initialValue()`** in an anonymous subclass |
| Modern form | **`ThreadLocal.withInitial(supplier)`** — runs once per thread |
| Typical uses | per-thread **connection**, **transaction ID**, **user ID** |
| On thread death | values become **eligible for GC** |
| **With a thread pool** | ⚠️ threads **do not die** — values **leak between tasks** |
| The fix | **`remove()` in a `finally`** |
| Introduced in | **1.2**, enhanced in 1.5 |
