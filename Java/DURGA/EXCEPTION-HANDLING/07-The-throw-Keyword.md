
> Sometimes we can create the exception object **explicitly** and hand it over to the JVM **manually**, by using the `throw` keyword.

```java
throw new ArithmeticException("/ by zero");
```

> [!important] **The distinction that gets asked.** For **predefined** exceptions, the JVM raises them for you — that is the automatic path. For **customized (user-defined)** exceptions, nobody raises them but you, so `throw` is the only way they ever happen. That is the real use of the keyword, and it is why part 9 on customized exceptions depends on this one.

---

# Case 1 — `throw` works only for `Throwable` types

An ordinary class cannot be thrown, however much you want to throw it.

```java
class Test3 {
    public static void main(String[] args) {
        throw new Test3();
    }
}
```

Measured on JDK 25:

```
T1.java:1: error: incompatible types: T1 cannot be converted to Throwable
```

Now make the very same class part of the hierarchy:

```java
class Test3 extends RuntimeException {
    public static void main(String[] args) {
        throw new Test3();
    }
}
```

```
Exception in thread "main" T3
	at T3.main(T3.java:1)
```

It compiles and runs. **One `extends` clause is the whole difference** — the class is now a `Throwable`, so it is throwable.

> [!info] **Notice what got printed as the exception name: just `T3`.** No `java.lang` prefix and no description, because the class is in the default package and nothing was passed to the constructor. That is what a bare custom exception looks like in a stack trace, and it is a good argument for always giving yours a message.

## Throwing a reference variable

`throw` takes an expression, not necessarily a `new`. So you can throw a variable — and that opens a trap.

**Non-null reference:**

```java
class Test3 {
    static ArithmeticException e = new ArithmeticException("boom");
    public static void main(String[] args) {
        throw e;
    }
}
```

```
Exception in thread "main" java.lang.ArithmeticException: boom
	at T3.<clinit>(T3.java:1)
```

**Null reference:**

```java
class Test3 {
    static ArithmeticException e;          // never assigned → null
    public static void main(String[] args) {
        throw e;
    }
}
```

```
Exception in thread "main" java.lang.NullPointerException: Cannot throw exception because "T3.e" is null
	at T3.main(T4.java:2)
```

> [!important] **Throwing `null` gives you a `NullPointerException`, not the exception you named.** The type of the variable is irrelevant at runtime — `throw` needs an actual object to hand to the JVM, and there is none. The declared type `ArithmeticException` never enters into it.

> [!warning] **Two things in the non-null output are worth stopping on, and the second is not in the lecture.**
>
> The trace says **`<clinit>`**, not `main` — `<clinit>` being the static initialiser. The exception was **thrown** from `main` on line 4, but the trace points at line 1 where it was **created**.
>
> That is because a stack trace is captured **when the exception object is constructed**, not when it is thrown. Confirmed directly:
>
> ```java
> ArithmeticException e = new ArithmeticException("made here");   // line 3
> throw e;                                                       // line 4
> ```
> ```
> Exception in thread "main" java.lang.ArithmeticException: made here
> 	at T7.main(T7.java:3)          ← line 3, the creation, not line 4, the throw
> ```
>
> **Practical consequence:** never cache or reuse exception objects. A pre-built exception carries the stack trace of wherever it was built, which will point you at the wrong place entirely when you are debugging. Always `throw new …` at the point of failure.

---

# Case 2 — nothing may follow a `throw`

> After a `throw` statement we can't take any statement directly, otherwise we get a compile-time error saying **unreachable statement**.

```java
class Test3 {
    public static void main(String[] args) {
        throw new ArithmeticException("/ by zero");
        System.out.println("hello");
    }
}
```

```
T5.java:3: error: unreachable statement
    System.out.println("hello");
    ^
```

And the contrast that makes the rule precise:

```java
class Test3 {
    public static void main(String[] args) {
        System.out.println(10/0);
        System.out.println("hello");
    }
}
```

```
compiles fine

Exception in thread "main" java.lang.ArithmeticException: / by zero
	at T6.main(T6.java:2)
```

**This one compiles.** `10/0` is guaranteed to throw — obviously, to a human — and `"hello"` is just as unreachable in practice. But it compiles anyway.

> [!important] **The difference is what the compiler is allowed to reason about.** `throw` is a **control-transfer statement**: by definition nothing after it can execute, and the language requires the compiler to reject the dead code.
>
> `10/0` is an **expression that happens to fail at runtime**. The compiler does not evaluate expressions to decide reachability — it applies flow rules — and by those rules `System.out.println(10/0)` completes normally, so the next line is reachable.
>
> So **unreachable statement** is not a claim about what will really happen. It is a claim about what the flow rules can prove.

---

# What this part established

| | |
|---|---|
| What `throw` does | creates the exception object **explicitly** and hands it to the JVM manually |
| What it can throw | **`Throwable`** types only — otherwise `incompatible types` |
| Throwing `null` | gives a **`NullPointerException`**, whatever the variable's declared type |
| Where a stack trace comes from | the point the exception was **constructed**, not thrown — so never reuse exception objects |
| After a `throw` | **no statement may follow** — `unreachable statement` |
| Its real purpose | raising **customized exceptions**, which nothing else can raise |

