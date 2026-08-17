
## The problem it replaced

Up to Java 6, closing a resource meant a `finally` block, and it meant this shape:

```java
BufferedReader br = null;
try {
    br = new BufferedReader(new FileReader("abc.txt"));
    // use br
} catch (IOException e) {
    // handling code
} finally {
    if (br != null)
        br.close();
}
```

> **Problems with this approach:**
> - The programmer is compulsorily required to close all opened resources, which **increases the complexity** of the programming.
> - We must write the `finally` block explicitly, which **increases the length** of the code and reduces **readability**.

And the declaration has to live **outside** the `try` — which is why it needs `= null`, and why the `finally` needs a null check before it can close anything.

## The replacement

```java
try (BufferedReader br = new BufferedReader(new FileReader("abc.txt"))) {
    // use br — it will be closed automatically
} catch (IOException e) {
    // handling code
}
```

> The main advantage is that the resources opened as part of the `try` block **will be closed automatically** once control reaches the end of the `try` block, **either normally or abnormally**. We are not required to close them explicitly, so the complexity of programming is reduced, and no `finally` block is needed.

## The five conclusions

> **1.** We can declare any number of resources, but they must be separated by **semicolons**: `try (R1 ; R2 ; R3)`

> **2.** All resources must be **`AutoCloseable`** — the class must implement `java.lang.AutoCloseable`, directly or indirectly. All database, network and file-IO resources already do, so in practice there is nothing extra for you to do.

> **3.** All resource reference variables are **implicitly final**, so you cannot reassign them inside the `try` block.

> **4.** Until 1.6, a `try` had to be followed by `catch` or `finally`. With try-with-resources, **`try` alone is valid.**

> **5.** The `finally` block effectively becomes redundant, because closing is no longer your job.

## Measured

A tiny `AutoCloseable` that announces itself, so the closing is visible:

```java
class Res implements AutoCloseable {
    
    String name;
    
    Res(String n) { 
	    name = n; 
	    System.out.println("opened " + n); 
	}
    public void close() { 
	    System.out.println("closed " + name); 
    }
}
```

```java
try (Res r1 = new Res("R1"); Res r2 = new Res("R2")) {
    System.out.println("inside try");
    throw new RuntimeException("boom");
} catch (RuntimeException e) {
    System.out.println("caught: " + e.getMessage());
}

try (Res r3 = new Res("R3")) {        // no catch, no finally
    System.out.println("inside second try");
}
```

On JDK 25:

```
opened R1
opened R2
inside try
closed R2
closed R1
caught: boom
--- and with no catch or finally at all ---
opened R3
inside second try
closed R3
```

> [!important] **Three things in that output that the conclusions above do not spell out.**
>
> **Resources close in reverse order of declaration** — `R2` before `R1`. Which is what you want, since a later resource may depend on an earlier one.
>
> **They close before the catch block runs.** `closed R2` and `closed R1` both appear above `caught: boom`. So by the time your handler executes, the resources are already gone — you cannot use them in the `catch`.
>
> **The body threw an exception and they closed anyway.** That is the normally or abnormally clause, demonstrated.

And conclusion 3, measured:

```java
try (Res r = new Res("A")) {
    r = new Res("B");
}
```

```
TF.java:2: error: auto-closeable resource r may not be assigned
```

> [!info] **Java 9 relaxed the syntax.** You may now use an **existing effectively-final variable** as a resource, instead of being forced to declare it inside the parentheses:
>
> ```java
> Res r = new Res("existing");
> try (r) {                        // legal since Java 9
>     System.out.println("inside try");
> }
> ```
> ```
> opened existing
> inside try
> closed existing
> ```
>
> Useful when the resource is handed to you rather than created on the spot.

## Suppressed exceptions — the part the course cannot cover

This is where try-with-resources stops being merely shorter and becomes **more correct**, and it closes a loop opened back in part 5.

Recall the masking problem: when `finally` throws, the original exception disappears. Reproduced with the old approach:

```java
try {
    throw new RuntimeException("body failed");
} finally {
    throw new IllegalStateException("close failed");
}
```

```
Exception in thread "main" java.lang.IllegalStateException: close failed
```

**The real failure — `body failed` — is gone.** You are left debugging the cleanup code.

Now the same situation with try-with-resources, where `close()` is what fails:

```java
class BadRes implements AutoCloseable {
    public void close() { throw new IllegalStateException("close failed"); }
}

try (BadRes r = new BadRes()) {
    throw new RuntimeException("body failed");
} catch (Exception e) {
    System.out.println("primary   : " + e);
    for (Throwable s : e.getSuppressed())
        System.out.println("suppressed: " + s);
}
```

```
primary   : java.lang.RuntimeException: body failed
suppressed: java.lang.IllegalStateException: close failed
```

> [!important] **Both survive.** The body's exception is the primary one, and the failure from `close()` is **attached to it** as a suppressed exception, retrievable with `getSuppressed()` and printed in the stack trace under a `Suppressed:` heading.
>
> That is the strongest argument for try-with-resources, and it is not about brevity at all. The hand-written `finally` version silently destroys the information you most need. **Say this if an interviewer asks why try-with-resources is preferred** — it's shorter is the weak answer; it doesn't lose the original exception is the real one.

---

# Multi-catch block

## The problem

Before Java 7, even when several exceptions needed **identical** handling, each needed its own block:

```java
try {
    // …
} catch (ArithmeticException e) {
    e.printStackTrace();
} catch (NullPointerException e) {
    e.printStackTrace();
} catch (ClassCastException e) {
    System.out.println(e.getMessage());
} catch (IOException e) {
    System.out.println(e.getMessage());
}
```

Four blocks, two distinct behaviours, and a lot of duplication.

## The replacement

> The main advantage of a multi-catch block is that we can write a **single catch block which can handle multiple different exceptions.**

```java
try {
    // …
} catch (ArithmeticException | NullPointerException e) {
    e.printStackTrace();
} catch (ClassCastException | IOException e) {
    System.out.println(e.getMessage());
}
```

Measured on JDK 25:

```java
try {
    System.out.println(10/0);
} catch (ArithmeticException | NullPointerException e) {
    System.out.println("caught: " + e);
}
```

```
caught: java.lang.ArithmeticException: / by zero
```

## The one rule

> In a multi-catch block there should be **no relation between the exception types** — not child-to-parent, not parent-to-child, not the same type — otherwise we get a compile-time error.

```java
catch (ArithmeticException | RuntimeException e) { }
```

```
MC2.java:3: error: Alternatives in a multi-catch statement cannot be related by subclassing
```

> [!important] **The reason is the same as the catch-ordering rule from part 4.** `RuntimeException` already covers every `ArithmeticException`, so naming both makes one of them redundant — and the compiler rejects alternatives it can prove are pointless. Listing a parent alongside its own child is exactly the **has already been caught** situation, expressed inside a single block.
>
> One more property worth knowing: in a multi-catch, the parameter is **implicitly final** — you cannot reassign `e` inside the block. With a single type you can.

---

# Exception propagation

A name for something already seen:

> Within a method, if an exception is raised and that method does not handle it, the exception object will be **propagated to the caller**, and then the caller method is responsible for handling it. This process is called **exception propagation**.

That is exactly the walk from part 2 — `doMoreStuff` to `doStuff` to `main`, each asked in turn for handling code. Part 2 described the mechanism; this is its name.

> [!info] **And `throws` is how you make propagation legal for a checked exception.** Part 7's chain — every method declaring `throws InterruptedException` — is propagation that the compiler has been told about in advance. For unchecked exceptions propagation happens with no declaration at all.

---

# Rethrowing an exception

> To convert one exception type into another, we can use the rethrowing concept.

```java
try {
    System.out.println(10/0);
} catch (ArithmeticException e) {
    throw new NullPointerException("converted");
}
```

```
Exception in thread "main" java.lang.NullPointerException: converted
	at RT.main(RT.java:3)
```

An `ArithmeticException` went in; a `NullPointerException` came out.

> [!warning] **Written exactly like that, this is a bug rather than a technique.** The original exception is discarded — no `Caused by:` line, no stack trace pointing at the division. You have replaced real diagnostic information with a type of your choosing, which is the masking problem again.
>
> The correct form **chains the cause**:
>
> ```java
> catch (ArithmeticException e) {
>     throw new IllegalStateException("could not compute rate", e);   // ← cause
> }
> ```
>
> Now the stack trace carries a `Caused by: java.lang.ArithmeticException: / by zero` section and you can see both layers. Every sensible exception class has a constructor taking a `Throwable` cause for this purpose.
>
> **Where it is genuinely useful:** at an architectural boundary. A data-access layer catches `SQLException` — a checked, vendor-specific, low-level thing — and rethrows it as an unchecked `DataAccessException` so callers are not coupled to JDBC. That is what Spring does throughout, and it is the same technique with the cause attached.

---

# What this part established

| | |
|---|---|
| try-with-resources closes | **automatically**, at the end of the `try`, normally or abnormally |
| Closing order | **reverse** of declaration, and **before** the `catch` runs |
| Resource requirements | must be **`AutoCloseable`**; reference is **implicitly final** |
| `try` alone | **valid** with resources — no `catch` or `finally` needed |
| Why it is genuinely better | it **preserves the primary exception** and attaches close failures as **suppressed** |
| Multi-catch | one block, several types, `\|`-separated |
| Multi-catch restriction | the types must be **unrelated by subclassing** |
| Exception propagation | an unhandled exception passes to the **caller** |
| Rethrowing | converts one type into another — **always pass the original as the cause** |

---

