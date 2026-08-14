
> We require some place to maintain cleanup code which should be executed **always** — irrespective of whether an exception is raised or not, and whether it is handled or not. Such a place is nothing but the **`finally` block**.

```java
try {
    // risky code
} catch (X e) {
    // handling code
} finally {
    // cleanup code
}
```

Three blocks, three jobs. That mapping is worth memorising as a unit: **risky / handling / cleanup**.

---

# The speciality, in three cases

> The speciality of the `finally` block is that it will be executed **always** — irrespective of whether the exception is raised or not raised, and whether it is handled or not handled.

All three measured on JDK 25.

## Case 1 — no exception

```java
try {
    System.out.println("try block executed");
} catch (ArithmeticException e) {
    System.out.println("catch block executed");
} finally {
    System.out.println("finally block executed");
}
```

```
try block executed
finally block executed

exit code: 0
```

No exception, so no `catch`. **`finally` runs anyway.**

## Case 2 — exception raised, catch matches

```java
try {
    System.out.println("try block executed");
    System.out.println(10/0);
} catch (ArithmeticException e) {
    System.out.println("catch block executed");
} finally {
    System.out.println("finally block executed");
}
```

```
try block executed
catch block executed
finally block executed

exit code: 0
```

All three blocks, in order. Normal termination.

## Case 3 — exception raised, catch does *not* match

```java
try {
    System.out.println("try block executed");
    System.out.println(10/0);
} catch (NullPointerException e) {        // wrong type
    System.out.println("catch block executed");
} finally {
    System.out.println("finally block executed");
}
```

```
try block executed
finally block executed
Exception in thread "main" java.lang.ArithmeticException: / by zero
	at F3.main(F3.java:2)

exit code: 1
```

> [!important] **Case 3 is the one that proves the claim.** The exception was *not handled* — the program dies abnormally with exit code 1 — and **`finally` still ran**, before the default handler printed anything. That is what "irrespective of whether handled or not" means in practice: the cleanup happened on the way out.

---

# `return` versus `finally`

> Even though a `return` statement is present in the `try` or `catch` block, **first `finally` will be executed**, and only after that will the `return` statement be considered. **`finally` dominates `return`.**

```java
try {
    System.out.println("try block executed");
    return;
} catch (ArithmeticException e) {
    System.out.println("catch block executed");
} finally {
    System.out.println("finally block executed");
}
```

```
try block executed
finally block executed
```

The `return` is *pending* while `finally` runs. Cleanup cannot be skipped by returning early — which is exactly the guarantee that makes `finally` worth having.

## When all three return

> If a `return` statement is present in the `try`, `catch` **and** `finally` blocks, then the **`finally` block's `return`** will be considered.

```java
public static int m1() {
    try {
        System.out.println(10/0);
        return 777;
    } catch (ArithmeticException e) {
        return 888;
    } finally {
        return 999;
    }
}
```

```
999
```

Read the path: `10/0` throws, so `return 777` never happens. The catch matches and prepares `return 888`. Then `finally` runs — and **its `return 999` replaces the pending one.** The value the caller sees is 999.

> [!warning] **This works, and you must never write it.** A `return` inside `finally` silently discards whatever the `try` or `catch` was returning — and it discards **exceptions** the same way, so a thrown exception can vanish without trace.
>
> Modern `javac` says so directly. Compiling that method with `-Xlint:all` on JDK 25:
>
> ```
> R2.java:6: warning: [finally] finally clause cannot complete normally
> ```
>
> Learn it because it is asked — *what does this print?* is a standard puzzle, and the answer is 999. Then know that the compiler considers it a defect.

---

# `finally` versus `System.exit(0)`

> There is **only one situation** where the `finally` block won't be executed: whenever we are using the **`System.exit(0)`** method. Then the JVM itself will be shut down, and in this case the `finally` block won't be executed. **`System.exit(0)` dominates the `finally` block.**

```java
try {
    System.out.println("try");
    System.exit(0);
} catch (ArithmeticException e) {
    System.out.println("catch block executed");
} finally {
    System.out.println("finally block executed");
}
```

```
try

exit code: 0
```

Only `try`. **`finally` did not run.** And the reason is not a special case in the language — there is no JVM left to run it. `System.exit()` shuts the whole thing down.

> [!important] **The chain of dominance, which is a clean way to remember all of this.**
> `finally` dominates `return` — a pending return waits for cleanup.
> `System.exit(0)` dominates `finally` — nothing waits for anything, the JVM is gone.

> [!info] **About that argument.** It is a **status code**, and it need not be zero — any integer is legal. By convention **zero means normal termination and non-zero means abnormal termination.** The code is used by whatever launched the JVM; as far as your program's own behaviour is concerned, zero or non-zero makes no difference to the result.

---

# `final` versus `finally` versus `finalize`

## `final`

> **`final` is a modifier** applicable to **classes, methods and variables.**

| Applied to | Effect |
|---|---|
| a **class** | child class creation is not possible — **inheritance is blocked** |
| a **method** | **overriding** that method is not possible |
| a **variable** | **reassignment** is not possible — it becomes a constant |

## `finally`

> **`finally` is a block**, always associated with `try`-`catch`, to maintain **cleanup code** which should be executed always — irrespective of whether an exception is raised or not, and whether it is handled or not.

## `finalize`

> **`finalize` is a method**, always invoked by the **garbage collector** just before destroying an object, to perform **cleanup activities**.

## Putting them side by side

| | `final` | `finally` | `finalize` |
|---|---|---|---|
| What is it | a **modifier** | a **block** | a **method** |
| Applies to | classes, methods, variables | `try`-`catch` | objects |
| Who invokes it | — | the JVM, on leaving the construct | the **garbage collector** |
| Purpose | prevent inheritance / overriding / reassignment | cleanup, always | cleanup, before destruction |

> [!important] **The two notes that turn this from a list into an answer.**
> **1.** `finally` is for cleanup related to the **`try` block**; `finalize()` is for cleanup related to the **object**. Different scopes entirely.
> **2.** For maintaining cleanup code, **`finally` is recommended over `finalize()`** — because we cannot expect the exact behaviour of the garbage collector.

> [!warning] **`finalize()` is deprecated for removal, and the second note above is the reason why.** The garbage collector's timing is not guaranteed at all, so cleanup attached to it may happen late or never. This is covered in full in the garbage collection chapter — [[04-Finalization-And-Memory-Leaks|finalization and memory leaks]] — including measured proof that its exceptions are silently swallowed and that it runs only once per object even if the object becomes eligible twice.
>
> The modern answer to *"where does cleanup go?"* is **`try`-with-resources**, which is part 10 of this chapter. `finally` remains correct and is what try-with-resources is built on top of.

---

# What this part established

| | |
|---|---|
| `finally` exists because | cleanup cannot safely live in `try` (may be skipped) or `catch` (may not run) |
| When does it run | **always** — exception or not, handled or not |
| The one exception | **`System.exit()`** — the JVM is gone |
| Versus `return` | `finally` runs first; a `return` in `finally` **overrides** the pending one, and the compiler warns |
| `final` / `finally` / `finalize` | a **modifier**, a **block**, a **method** — unrelated beyond the spelling |
