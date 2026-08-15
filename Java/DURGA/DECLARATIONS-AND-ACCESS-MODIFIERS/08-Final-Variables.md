# The three kinds of variable

Everything in this part hangs off one classification:

| Kind | Declared | Lives |
|---|---|---|
| **instance** variable | in the class, without `static` | one copy **per object** |
| **static** variable | in the class, with `static` | one copy **per class** |
| **local** variable | inside a method, block or constructor | on the **stack**, temporarily |

The question is what `final` does to each — and the answer is different all three times.

---

# Instance variables

## What makes a variable an instance variable

600 students, each with a name and a roll number:

| | name | roll number |
|---|---|---|
| student 1 | Durga | 101 |
| student 2 | Ravi | 102 |
| … | | |
| student 600 | Shiva | 700 |

> **If the value of a variable varies from object to object, such variables are called instance
> variables** — also known as **object level variables**.
>
> **For every object, a separate copy of the instance variables is created.**

600 students means **600 names and 600 roll numbers**.

## The default value

```java
class X {
    int x;
    public static void main(String[] a) { System.out.println(new X().x); }
}
```

Measured on JDK 25:

```
0
```

> **For instance variables we are not required to perform initialization explicitly — the JVM always
> provides default values.**

## What `final` changes

```java
class X { final int x; }
```

Measured on JDK 25:

```
error: variable x not initialized in the default constructor
```

> **If an instance variable is declared `final`, the JVM will NOT provide a default value. We must
> perform initialization explicitly — whether we are using the variable or not.**

## Where you may initialize it

> **Rule: for final instance variables we must perform initialization before CONSTRUCTOR COMPLETION.**

Which gives exactly three places:

| # | Place | Example |
|---|---|---|
| 1 | **at the time of declaration** | `final int x = 10;` |
| 2 | **inside an instance block** | `final int x; { x = 10; }` |
| 3 | **inside a constructor** | `final int x; X() { x = 10; }` |

Measured on JDK 25 — **all three compile.**

> [!info] **Why exactly those three, and why the rule is phrased that way.** The instance control flow
> runs: instance variable assignments and instance blocks **first**, then the constructor. All three
> places sit before the constructor finishes — so "before constructor completion" is not an arbitrary
> cut-off, it is a description of what has already run by then.

**Anywhere else fails.** Measured on JDK 25:

```java
class X { final int x; public void m1() { x = 10; } }
```
```
error: cannot assign a value to final variable x
```

A method runs **after** the constructor — by then the object exists and `x` is already fixed.

---

# Static variables

## What makes a variable static

Add a **college name** to those 600 students. Every one of them says `DurgaSoft`.

> **If the value of a variable is NOT varied from object to object, such variables are not recommended
> as instance variables** — you would create 600 identical copies, wasting memory. *"How many times do
> we need to create `DurgaSoft`? 600 times."*
>
> **Declare such variables at class level using the `static` modifier.** Then **one copy** is created
> at class level and **shared by every object**.

## The default value, and what `final` changes

```java
class X { static int x; }
```

Prints `0` — same as instance variables, the JVM provides the default.

```java
class X { final static int x; }
```

Measured on JDK 25:

```
error: variable x might not have been initialized
```

> [!info] **The two cases give two different messages.** The *static* case says
> `might not have been initialized`; the *instance* case above named the constructor explicitly. Do not
> expect one message to cover both.

## Where you may initialize it

> **Rule: for final static variables we must perform initialization before CLASS LOADING COMPLETION.**

Which gives **two** places, not three:

| # | Place | Example |
|---|---|---|
| 1 | **at the time of declaration** | `final static int x = 10;` |
| 2 | **inside a static block** | `final static int x; static { x = 10; }` |

Measured on JDK 25 — both compile. And a constructor is now **too late**:

```java
class X { final static int x; X() { x = 10; } }
```
```
error: cannot assign a value to static final variable x
```

> [!important] **The two rules side by side, which is the examinable pair:**
>
> | | Deadline | Legal places |
> |---|---|---|
> | final **instance** variable | before **constructor completion** | declaration, **instance block**, **constructor** |
> | final **static** variable | before **class loading completion** | declaration, **static block** |
>
> The static one is stricter because class loading happens **before any object exists** — and a
> constructor only runs when one is created. The deadline explains the list in both cases.

---

# Local variables

## What they are

> **Variables declared inside a method, a block, or a constructor — to meet the temporary requirements
> of the programmer — are called local variables.**

Also known as **temporary variables**, **stack variables** (they live in stack memory) or **automatic
variables**.

## The JVM provides nothing

> **For local variables the JVM does NOT provide any default values** — not even when they are not
> final. **We must perform initialization explicitly before using them.**

> [!info] **Why the difference.** Instance and static variables are **standard data** — part of an
> object or part of a class, so the JVM initialises them. A local variable is **temporary data**,
> alive only for the length of a method call, so the JVM leaves it to you.

Measured on JDK 25:

| Code | Result |
|---|---|
| `int x; System.out.println("hello");` | ✅ **valid** — prints `hello` |
| `int x; System.out.println(x);` | ❌ `variable x might not have been initialized` |

> **If we are not using the local variable, it is not required to initialize it.** The requirement is
> **before use**, not at declaration.

## And `final` changes nothing about that

The question he sets up carefully, because the instinct from the previous two sections is wrong:

```java
public static void main(String[] args) {
    final int x;
    System.out.println("hello");
}
```

*"Compile-time error, or `hello`?"*

Measured on JDK 25:

```
hello
```

> [!important] **This is the asymmetry of the whole part.**
> - final **instance** and final **static** variables must be initialized **whether used or not**.
> - a final **local** variable must be initialized **only before use** — exactly like a non-final one.
>
> *"Even though the local variable is final, before using only we have to perform initialization. If we
> are not using it, it is not required — even though it is final."*

---

# The only modifier a local variable may have

`public`, `private`, `protected` and default control **where** a variable can be accessed. But a local
variable's scope is **already fixed** — it is visible inside its method or block and nowhere else. So
those words have nothing to say about it.

> **The only applicable modifier for a local variable is `final`.** Any other modifier is a
> compile-time error.

Measured on JDK 25:

| Modifier on a local variable | Result |
|---|---|
| `public` | ❌ `illegal start of expression` |
| `private` | ❌ `illegal start of expression` |
| `protected` | ❌ `illegal start of expression` |
| `static` | ❌ `illegal start of expression` |
| `transient` | ❌ `illegal start of expression` |
| `volatile` | ❌ `illegal start of expression` |
| **`final`** | ✅ **valid** |

> [!info] **And a local variable is not final by default.** *"Some people may feel by default every
> local variable is final. No — if you want, you can apply it."*

> [!question]- **Deep dive — the student whose Java was "not working properly".** A story he tells to
> make this rule stick, and it is a good diagnostic lesson.
>
> A working professional came to him at the end of a session: *"Sir, in my system Java is not working
> properly."* He assumed a `PATH` or `CLASSPATH` problem — until she added: **"Some programs compile
> and run fine, but some don't."**
>
> *"I got a shock — because if it were a path problem, NO program should work."*
>
> He asked her to write one of the failing programs:
>
> ```java
> class Test {
>     public static void main(String[] args) {
>         public int x = 10;
>         System.out.println(x);
>     }
> }
> ```
>
> **`public` on a local variable.** *"The problem is not with Java. The problem is with your program."*
>
> The diagnostic point is worth as much as the rule: **"it works for some programs and not others"
> rules out the environment entirely.** A broken installation fails uniformly.

## And "no modifier means default" does not apply either

> **If we don't declare any modifier, then by default it is default access — but this rule applies only
> to instance and static variables, NOT to local variables.**

A local variable with no modifier is not "default access". It has no access modifier at all, because
access modifiers are meaningless for it.

---

# Formal parameters

```java
class FP {
    public static void main(String[] args) { m1(10, 20); }
    public static void m1(int x, int y) {
        x = 100; y = 200;
        System.out.println(x + "..." + y);
    }
}
```

| Term | What it means |
|---|---|
| `10, 20` at the call site | **actual parameters** (actual values, arguments) |
| `int x, int y` in the signature | **formal parameters** |

Measured on JDK 25:

```
100...200
```

The reassignment inside `m1` works, and `x` and `y` are visible only inside `m1`.

> **Formal parameters of a method are simply local variables of that method.**

**Everything above therefore applies to them** — including which modifier they may carry:

> **Hence a formal parameter can be declared `final`. And if a formal parameter is declared `final`, we
> cannot perform reassignment within the method.**

Measured on JDK 25:

```java
public static void m1(final int x, int y) { x = 100; }
```
```
error: final parameter x may not be assigned
```

> [!info] **Parameters get their own message.** Reassigning any other final variable says
> `cannot assign a value to final variable x`; a **final parameter** gets the dedicated
> `final parameter x may not be assigned`.

> [!info] **The exam form of this.** *"Consider the following code — (a) no compile-time error,
> (b) compile-time error because a formal parameter cannot be declared final, (c) compile-time error
> because reassignment is not allowed."*
>
> **The answer is (c).** Option (b) is the trap: declaring the parameter `final` is perfectly legal —
> it is the **reassignment** that fails.

---

# What this part established

| | |
|---|---|
| Instance variable | value **varies** object to object; **one copy per object** |
| Static variable | value **does not vary**; **one copy per class**, shared |
| Local variable | temporary; **stack**, automatic |
| JVM default values | provided for **instance and static**; **never** for local |
| final **instance**, uninitialised | ❌ `variable x not initialized in the default constructor` |
| final **static**, uninitialised | ❌ `variable x might not have been initialized` |
| final instance — deadline | before **constructor completion** |
| — legal places | declaration · **instance block** · **constructor** |
| final static — deadline | before **class loading completion** |
| — legal places | declaration · **static block** (a constructor is **too late**) |
| Assigning elsewhere | `cannot assign a value to final variable x` |
| final **local**, unused | ✅ **valid** — no initialization needed |
| final local, used | must be initialized **before use**, same as non-final |
| The only local modifier | **`final`** — everything else is `illegal start of expression` |
| Local variables are **not** final by default | correct |
| "No modifier = default access" | applies to instance/static only, **not** local |
| Formal parameters are | **local variables** of that method |
| A final formal parameter | legal — but **cannot be reassigned** |
| That error on JDK 25 | `final parameter x may not be assigned` |
