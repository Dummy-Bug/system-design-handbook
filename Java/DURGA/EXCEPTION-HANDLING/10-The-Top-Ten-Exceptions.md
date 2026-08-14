# First, who raises it

Before the list, the classification the list is organised by.

> Based on **the person who is raising the exception**, all exceptions are divided into two types.

> **JVM exceptions** — raised **automatically by the JVM** whenever a particular event occurs.
> Examples: `ArrayIndexOutOfBoundsException`, `NullPointerException`

> **Programmatic exceptions** — raised **explicitly by the programmer or by the API developer**.
> Example: `IllegalArgumentException`

> [!important] **This is the useful axis, and it is not the same as checked versus unchecked.** *Who raises it* tells you where to look when it happens. A JVM exception means the runtime caught you doing something impossible. A programmatic exception means **somebody wrote a `throw`** — either you, or the author of the library you called — because they decided your input or timing was wrong.

---

# The six raised by the JVM

### 1 · `ArrayIndexOutOfBoundsException`

Child of `RuntimeException`, so **unchecked**. Raised when you access an array element with an out-of-range index.

```java
int[] x = new int[10];
System.out.println(x[0]);      // valid
System.out.println(x[100]);    // AIOOBE
System.out.println(x[-100]);   // AIOOBE
```

```
0
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 100 out of bounds for length 10
```

```
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index -100 out of bounds for length 10
```

Both directions count as out of range — negative indices are not a separate error.

### 2 · `NullPointerException`

Child of `RuntimeException`, **unchecked**. Raised when you call a method on `null`.

```java
String s = null;
System.out.println(s.length());
```

```
Exception in thread "main" java.lang.NullPointerException: Cannot invoke "String.length()" because "<local1>" is null
```

> [!info] **That message is newer than the course.** **Helpful NullPointerExceptions** arrived in **Java 14** and are on by default: the JVM now names the method it could not invoke and the expression that was null. In 2016 this line read `java.lang.NullPointerException` and nothing else, and finding *which* reference was null in `a.b().c().d()` was manual work. Mention this if NPE debugging comes up in an interview — it is a concrete, current thing to know.

### 3 · `StackOverflowError`

Child of **`Error`**, so unchecked. Raised on recursive calls with no termination.

```java
static void m1() { m2(); }
static void m2() { m1(); }
public static void main(String[] a) { m1(); }
```

```
Exception in thread "main" java.lang.StackOverflowError
	at E.m2(E.java:1)
```

> [!info] **Mutual recursion, not self-recursion.** `m1` calls `m2` and `m2` calls `m1` — neither is directly recursive, and it overflows just the same. Each call is a frame on the runtime stack from part 1, and the stack has a finite size. The JVM chapter's stack note has this measured at specific depths against the `-Xss` flag.

### 4 · `NoClassDefFoundError`

Child of **`Error`**, unchecked. Raised when the JVM cannot find a required `.class` file.

```
$ java NoSuchClassAtAll
Error: Could not find or load main class NoSuchClassAtAll
Caused by: java.lang.ClassNotFoundException: NoSuchClassAtAll
```

> [!warning] **Measured behaviour differs from the lecture here.** The lecture says running `java Test` with no `Test.class` gives `NoClassDefFoundError`. On JDK 25 the launcher reports **`Could not find or load main class`, caused by `ClassNotFoundException`** — not `NoClassDefFoundError`.
>
> Both types exist and both are real; the distinction is worth knowing because it is itself an interview question:
>
> | | `ClassNotFoundException` | `NoClassDefFoundError` |
> |---|---|---|
> | Type | **`Exception`** — checked | **`Error`** — unchecked |
> | Raised when | an **explicit** lookup fails: `Class.forName("X")`, `loadClass` | the class was **present at compile time** but is missing at runtime |
> | Typical cause | a name typed at runtime that does not exist | a jar missing from the runtime classpath |
>
> `NoClassDefFoundError` still very much happens — it is the classic "compiled fine, exploded on the server" failure. It just is not what the missing-main-class case produces any more.

### 5 · `ClassCastException`

Child of `RuntimeException`, **unchecked**. Raised when you type-cast a parent object to a child type.

```java
Object o = new Object();
String s = (String) o;
```

```
Exception in thread "main" java.lang.ClassCastException: class java.lang.Object cannot be cast to class java.lang.String (java.lang.Object and java.lang.String are in module java.base of loader 'bootstrap')
```

The message now names both types **and their modules and class loader** — which is genuinely useful in the case where two versions of the same class are loaded by different loaders, and the error reads absurdly as `X cannot be cast to X`.

### 6 · `ExceptionInInitializerError`

Child of **`Error`**, unchecked. Raised if any exception occurs while performing **static variable initialisation** or **static block execution**.

```java
class Test { static int i = 10/0; }
```

```
Exception in thread "main" java.lang.ExceptionInInitializerError
Caused by: java.lang.ArithmeticException: / by zero
```

```java
class Test {
    static { 
	    String s = null; 
	    System.out.println(s.length()); 
    }
}
```

```
Exception in thread "main" java.lang.ExceptionInInitializerError
Caused by: java.lang.NullPointerException: Cannot invoke "String.length()" because "<local0>" is null
```

> [!important] **Note the `Caused by:` line — the original exception is preserved underneath.** The `ExceptionInInitializerError` is a wrapper saying *initialisation failed*; the chained cause tells you why. So when you meet this, the interesting information is always on the second line.
>
> This connects to the JVM chapter: static initialisation happens during the **initialization** phase of class loading, so a failure here means the class never becomes usable at all.

---

# The four raised explicitly

### 7 · `IllegalArgumentException`

Child of `RuntimeException`, **unchecked**. Raised by the programmer or API developer to indicate that **a method has been invoked with an inappropriate argument**.

```java
Thread t = new Thread();
t.setPriority(10);     // valid — range is 1 to 10
t.setPriority(100);    // invalid
```

```
Exception in thread "main" java.lang.IllegalArgumentException
	at java.base/java.lang.Thread.setPriority(Thread.java:1705)
```

> [!info] **Look at where the trace points: inside `Thread.setPriority`, in `java.base`.** That is the "API developer" half of the definition made visible. Somebody at Oracle wrote a range check and a `throw` — this exception exists because of a decision in library code, not because the JVM detected an impossible operation.

### 8 · `NumberFormatException`

Child of **`IllegalArgumentException`** — so also unchecked. Raised when converting a string to a number and the string is not properly formatted.

```java
int i = Integer.parseInt("10");     // fine
int j = Integer.parseInt("ten");    // NFE
```

```
10
Exception in thread "main" java.lang.NumberFormatException: For input string: "ten"
```

Worth knowing the parentage: `NumberFormatException` **is an** `IllegalArgumentException`, which makes sense — a badly formatted string is an inappropriate argument. So `catch (IllegalArgumentException e)` catches it too.

### 9 · `IllegalStateException`

Child of `RuntimeException`, **unchecked**. Raised to indicate that **a method has been invoked at an inappropriate time**.

The example is a servlet session — once a session has been invalidated, you cannot call anything on it:

```java
HttpSession session = req.getSession();
System.out.println(session.getId());   // fine
session.invalidate();
System.out.println(session.getId());   // IllegalStateException
```

> [!important] **The pair worth holding together: `IllegalArgumentException` is *wrong input*, `IllegalStateException` is *wrong time*.** Same call, same arguments — legal before `invalidate()`, illegal after. Nothing about the argument changed; the object's state did.

### 10 · `AssertionError`

Child of **`Error`**, unchecked. Raised to indicate that an `assert` statement has failed.

```java
assert(false);
System.out.println("not reached");
```

```
$ java -ea E
Exception in thread "main" java.lang.AssertionError
	at E.main(E.java:1)
```

> [!warning] **Assertions are disabled by default — you must run with `-ea`.** Without that flag the program above prints `not reached` and exits normally, because `assert` compiles to a check guarded by a runtime switch that is off.
>
> This is why assertions are for development and testing only, and never for validating input in production: in production they are almost certainly not running. Use an explicit `if` and `throw new IllegalArgumentException(...)` for anything that must always be checked.

---

# The summary table

| # | Exception / Error | Parent | Checked? | Raised by |
|---|---|---|---|---|
| 1 | `ArrayIndexOutOfBoundsException` | `RuntimeException` | unchecked | **JVM** |
| 2 | `NullPointerException` | `RuntimeException` | unchecked | **JVM** |
| 3 | `StackOverflowError` | `Error` | unchecked | **JVM** |
| 4 | `NoClassDefFoundError` | `Error` | unchecked | **JVM** |
| 5 | `ClassCastException` | `RuntimeException` | unchecked | **JVM** |
| 6 | `ExceptionInInitializerError` | `Error` | unchecked | **JVM** |
| 7 | `IllegalArgumentException` | `RuntimeException` | unchecked | **programmer / API developer** |
| 8 | `NumberFormatException` | `IllegalArgumentException` | unchecked | **programmer / API developer** |
| 9 | `IllegalStateException` | `RuntimeException` | unchecked | **programmer / API developer** |
| 10 | `AssertionError` | `Error` | unchecked | **programmer / API developer** |

> [!important] **Every one of the ten is unchecked.** Which is not a coincidence — these are the ones you meet constantly, and if any of them were checked, ordinary code would be unwritable. Every array access would need a `throws`, every method call on an object would need one. The checked exceptions are the ones about the *outside world* — files, networks, interruption — where a caller genuinely has an alternative to fall back on.
>
> Four of the ten are `Error`s rather than `Exception`s: **`StackOverflowError`, `NoClassDefFoundError`, `ExceptionInInitializerError`, `AssertionError`.** By part 2's rule those are non-recoverable, and that is exactly right — there is nothing sensible to do in a `catch` for any of them.
