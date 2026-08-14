
# Risky code and handling code

> In our program the code which may raise an exception is called **risky code**. We place the risky code inside a **`try` block**, and the corresponding handling code inside a **`catch` block**.

```java
try {
    // risky code
} catch (Exception e) {
    // handling code
}
```

That is the whole shape. Everything else in this part is consequences of it.

## Without, and with

The same three statements, twice.

```java
class Test {
    public static void main(String[] args) {
        System.out.println("statement1");
        System.out.println(10/0);
        System.out.println("statement3");
    }
}
```

Measured on JDK 25:

```
statement1
Exception in thread "main" java.lang.ArithmeticException: / by zero
	at Test.main(Test.java:4)

exit code: 1
```

`statement1` printed. Then the exception, unhandled, so the default exception handler takes over and **`statement3` never runs**. Abnormal termination.

Now guard it:

```java
class Test {
    public static void main(String[] args) {
        System.out.println("statement1");
        try {
            System.out.println(10/0);
        } catch (ArithmeticException e) {
            System.out.println(10/2);
        }
        System.out.println("statement3");
    }
}
```

```
statement1
5
statement3

exit code: 0
```

> [!important] **The exit code is the cleanest way to see the difference.** `1` versus `0`, from programs that differ only by a `try`/`catch`. The exception still happened in both — `10/0` is still `10/0` — but in the second one the program **continued and terminated normally**, which is the definition of graceful termination from part 1.
>
> Note also *what* the catch block did: it printed `10/2`. That is the "alternative way" from part 1 made concrete — not a repair of the division by zero, a different route to carrying on.

---

# Control flow in try-catch

The four cases, and they are worth knowing as a set .

```java
try {
    statement1;
    statement2;
    statement3;
}
catch (X e) {
    statement4;
}
statement5;
```

| Case | Situation | Statements executed | Termination |
|---|---|---|---|
| **1** | no exception | 1, 2, 3, 5 | **normal** |
| **2** | exception at statement 2, **catch matches** | 1, 4, 5 | **normal** |
| **3** | exception at statement 2, **catch does not match** | 1 | **abnormal** |
| **4** | exception at statement **4 or 5** | — | **always abnormal** |

Case 2 is the one to read twice: **statement 3 does not run.** The exception happened at statement 2 and control left the `try` block immediately; handling it does not resume where it stopped.

Case 4 is the trap. An exception inside the `catch` block, or after the whole construct, has nothing guarding it — so it goes straight to the default handler.

## Three consequences

> **1.** Within the `try` block, if an exception is raised anywhere, **the rest of the `try` block won't be executed** — even though we handled that exception. Hence we should place **only risky code** inside the `try` block, and the length of the `try` block should be **as short as possible**.

> **2.** If a statement raises an exception and it is **not part of any `try` block**, it is always abnormal termination.

> **3.** There may be a chance of an exception being raised inside `catch` and `finally` blocks too, in addition to the `try` block.

> [!important] **Point 1 is the practical rule, and it is why long `try` blocks are a design smell.** Everything after the failure point inside the `try` is skipped. Wrap ten statements and you cannot tell which of them ran; wrap the one risky statement and you can. Keep `try` blocks short — not for style, but because the block's length is exactly the amount of code whose execution becomes uncertain.

---

# Three ways to print exception information

> The **`Throwable`** class defines the following methods to print exception information to the console.

| Method | Prints |
|---|---|
| **`printStackTrace()`** | name of the exception : description **+ stack trace** |
| **`toString()`** | name of the exception : description |
| **`getMessage()`** | **only the description** |

All three on the same `ArithmeticException`, measured on JDK 25:

```
--- printStackTrace() ---
java.lang.ArithmeticException: / by zero
	at Print3.main(Print3.java:4)

--- toString() ---
java.lang.ArithmeticException: / by zero

--- getMessage() ---
/ by zero
```

Three levels of detail, and the difference between them is exactly one piece of information at each step: the stack trace, then the type name.

> [!important] **The default exception handler internally uses `printStackTrace()`.** Which is why the output in part 2 looked the way it did — that was not a special format the JVM invented for fatal errors, it was this method, called for you.

> [!info] **Which one to reach for.** `getMessage()` when you want the description for a user-facing message; `printStackTrace()` when you are diagnosing. In production code neither goes to the console — you pass the exception to a logger, which captures the same information with a timestamp and a level attached. Durga Sir uses `printStackTrace()` in the lecture because it is visible on screen, not because it belongs in real code.

---

# Multiple catch blocks

> The way of handling an exception **varies from exception to exception**. Hence for every exception type it is recommended to take a **separate catch block**.

Which makes this **not** recommended:

```java
try {
    // …
} catch (Exception e) {
    // one default handler for absolutely everything
}
```

and this the right shape:

```java
try {
    // …
} catch (FileNotFoundException e) {
    // use a local file
} catch (ArithmeticException e) {
    // perform these arithmetic operations instead
} catch (SQLException e) {
    // don't use the Oracle DB, use MySQL
} catch (Exception e) {
    // default handler for anything else
}
```

The point is not tidiness. **A `FileNotFoundException` and an `SQLException` need genuinely different recoveries** — a local file in one case, a different database in the other. One catch block cannot express both, so a single `catch (Exception e)` is an admission that you have not thought about what to do.

## The hierarchy you are ordering against


![[Java/DURGA/EXCEPTION-HANDLING/Images/01-Exception-Hierarchy.png]]

> [!important] **The colours are the whole point of the picture.** Green is **checked**, blue is **unchecked**, red is `Error`. And the boundary is a single clean cut: **`RuntimeException` and everything below it** is blue, **everything else under `Exception`** — `IOException`, `SQLException`, `ClassNotFoundException` — is green. That one line in the tree is what part 3 is about.
>
> Note also that `Object` sits above `Throwable`. Which matters only because it means an exception object is an **ordinary object** — it can be stored in a variable, passed to a method, put in a list. Part 6 throws one from a static field on the strength of that.

> [!warning] **Two relationships are flattened in this diagram, and both are asked about.**
>
> **`NumberFormatException` is drawn as a direct child of `RuntimeException`.** It is really a child of **`IllegalArgumentException`**, which is the child of `RuntimeException`. So `catch (IllegalArgumentException e)` catches a `NumberFormatException`, which you would not guess from the picture.
>
> **`OutOfMemoryError` and `StackOverflowError` are drawn as siblings of `VirtualMachineError`.** Both are really **children** of it.
>
> Missing levels are exactly what turns a pair of catch blocks into `has already been caught`, so when the ordering rule below bites and you cannot see why, the answer is usually an inheritance step the diagram does not draw.

## Order matters, and getting it wrong will not compile

> If `try` with multiple catch blocks is present, then the **order of catch blocks is very important**. It should be from **child to parent**. By mistake, if we take from **parent to child**, we get a compile-time error.

**Parent first — wrong:**

```java
try {
    System.out.println(10/0);
} catch (Exception e) {
    e.printStackTrace();
} catch (ArithmeticException e) {
    e.printStackTrace();
}
```

Measured on JDK 25:

```
Wrong.java:7: error: exception ArithmeticException has already been caught
        } catch (ArithmeticException e) {
          ^
1 error
```

> [!important] **The error message is the explanation.** *`exception ArithmeticException has already been caught`* — because `catch (Exception e)` above it would match every `ArithmeticException` too, the second block is **unreachable**. The compiler refuses dead code it can prove is dead.

> So the rule *child to parent* is not a convention. It follows from the fact that catch blocks are tried **in order, top to bottom**, and the first matching one wins. Put the widest net first and nothing narrower below it can ever fire.

**Child first — correct:**

```java
try {
    System.out.println(10/0);
} catch (ArithmeticException e) {
    System.out.println("arithmetic handler");
} catch (Exception e) {
    System.out.println("general handler");
}
```

```
compiles OK
arithmetic handler
```


> [!info] **Which of the two catch blocks ran, above?** `arithmetic handler` — the child. That confirms the matching is by order and specificity, not by "best fit": `Exception` would have matched too, and never got the chance.

---

# What this part established

| | |
|---|---|
| Risky code goes in | the **`try`** block — and only risky code, kept short |
| Handling code goes in | the **`catch`** block |
| After a handled exception | the rest of the `try` block is **skipped**; execution resumes **after** the construct |
| Exception in `catch` or after the construct | **always abnormal** termination |
| Printing | `printStackTrace()` › `toString()` › `getMessage()`, in decreasing detail |
| Multiple catch blocks | one per exception type, ordered **child → parent** |
| Parent before child | **compile error** — `has already been caught` |

