# Interface methods

> **Every method present inside an interface is always `public` and `abstract`, whether we declare it
> or not.**

The interview follow-up is *why* — and both halves have a one-line answer.

## Why always `public`

> **To make this method available to every implementation class.**

The implementation class may sit in the **same package or a different one** — both are possible, and
the interface has no way to know. Anything less than `public` would rule out the second case.

## Why always `abstract`

> **An interface is a requirement specification. The implementation class is responsible for providing
> the implementation.**

*"This is the service I want."* The specification does not carry the implementation, by definition.

## The four equivalent declarations

Because both modifiers are implicit, all of these mean exactly the same thing inside an interface:

```java
void m1();
public void m1();
abstract void m1();
public abstract void m1();
```

## Which modifiers are rejected

Since an abstract interface method is **already** `public` and **already** `abstract`, anything
contradicting either is illegal. **The forbidden list is five:** `protected`, `final`, `synchronized`,
`native`, `strictfp`.

Measured on JDK 25:

| Modifier | Result |
|---|---|
| `protected` | ❌ `modifier protected not allowed here` |
| `final` | ❌ `modifier final not allowed here` |
| `synchronized` | ❌ `modifier synchronized not allowed here` |
| `native` | ❌ `modifier native not allowed here` |
| `strictfp` | ❌ `modifier strictfp not allowed here` |

> [!important] **`private` and `static` are *not* on that list — they are legal, but only with a
> body.** Write `private void m1();` with a semicolon and the compiler does not object to the modifier;
> it says `missing method body, or declare abstract`. Give it a body and it compiles. Measured on
> JDK 25, all four of these are legal:
> ```java
> interface I2 { static void m1() { } }
> interface I2 { default void m1() { } }
> interface I2 { private void m1() { } }
> interface I2 { private static void m1() { } }
> ```
> So the rule stated precisely: **an interface method is implicitly `public`** — except a `private`
> one — **and implicitly `abstract` only if it is not `default`, `static` or `private`.** Methods with
> bodies get their full treatment in `JAVA-8-FEATURES/05`; the rest of this session is about the
> abstract ones.

## The exam question

*Which of the following method declarations are allowed inside an interface?*

| Declaration | Allowed? | Why |
|---|---|---|
| `public void m1() { }` | ❌ | a body needs `default` or `static` |
| `private void m1();` | ❌ | `missing method body` — `private` requires one |
| `protected void m1();` | ❌ | `protected` is forbidden outright |
| `static void m1();` | ❌ | `missing method body` — `static` requires one |
| `public abstract native void m1();` | ❌ | `native` is forbidden outright |
| `abstract public void m1();` | ✅ | **valid** — modifier order is not important |

---

# Interface variables

## What they are for

The requirement specification says: *implement the college automation system, and wherever a college
name is required use `DurgaSoft`; wherever a location is required use `Hyderabad`.*

> **An interface can contain variables. The main purpose of an interface variable is to define
> requirement level constants.**

The methods say **what services** to implement; the variables say **which constants** to use while
implementing them.

## Always `public static final`

> **Every interface variable is always `public static final`, whether we declare it or not.**

Measured on JDK 25 — the source writes only `int x = 10;`:

```
$ javap V3
interface V3 {
  public static final int x;
}
```

**Three reasons, one per modifier:**

| Modifier | Why |
|---|---|
| **`public`** | to make the variable available to **every implementation class**, in any package |
| **`static`** | you **cannot create an object of an interface** — so it must be reachable **without one** |
| **`final`** | **multiple implementation classes** share it; if one could change it, **all the others would be affected** |

> [!info] **The `final` reason, concretely.** JDBC is implemented by Oracle, MySQL, IBM and others. They
> all see the same interface variable. If the Oracle driver could set it to 20, every other vendor's
> driver would silently see 20. **The implementation classes may read it; none may modify it.**

## The equivalent declarations

All of these are identical inside an interface:

```java
int x = 10;
public int x = 10;
static int x = 10;
final int x = 10;
public static int x = 10;
public final int x = 10;
static final int x = 10;
public static final int x = 10;
```

## Which modifiers are rejected

Measured on JDK 25:

| Modifier | Result | Why |
|---|---|---|
| `private` | ❌ `modifier private not allowed here` | it is already `public` |
| `protected` | ❌ `modifier protected not allowed here` | it is already `public` |
| `transient` | ❌ `modifier transient not allowed here` | see below |
| `volatile` | ❌ `modifier volatile not allowed here` | it is already `final` |

> [!question]- **Deep dive — why `transient` in particular is meaningless here.** A chain of three
> steps, and it is a nice piece of reasoning.
>
> `transient` marks a field to be **skipped during serialization**. But:
>
> 1. **Serialization means saving the state of an object.**
> 2. **You cannot create an object of an interface.**
> 3. No object ⇒ no state to save ⇒ **no serialization** ⇒ nothing for `transient` to exclude.
>
> And `volatile` fails for a simpler reason: `volatile` says *this value may change from another
> thread*, while `final` says *this value never changes*. `final volatile` is a contradiction, and the
> variable is already `final`.

## Initialization is mandatory, at the declaration

An interface variable is `static final`, and part 08 established the rule for those: **initialize
before class loading completion**, in one of two places — at the declaration, or in a **static block**.

> [!important] **But an interface cannot contain a static block.** No static blocks, no instance
> blocks, no constructors — an interface holds only methods and variables.
>
> **So one of the two legal places does not exist, leaving exactly one:**
> > **For interface variables we must perform initialization at the time of declaration.**

Measured on JDK 25:

```java
interface V2 { int x; }
```
```
error: = expected
```

The compiler is not saying "uninitialized" — it is saying **an `=` was expected right there**, because
that is the only place the value can go.

## The implementation class may read, not write

```java
interface I5 { int x = 10; }
class Mod implements I5 {
    public static void main(String[] a) { x = 777; }
}
```

Measured on JDK 25:

```
error: cannot assign a value to static final variable x
```

**But this compiles and prints 777:**

```java
class Loc implements I6 {
    public static void main(String[] a) { int x = 777; System.out.println(x); }
}
```

> [!important] **The two look almost identical, and the difference is one word.** The first *assigns to*
> the interface's variable. The second **declares a new local variable** that happens to share the
> name — it shadows the interface one and has nothing to do with it.
>
> **Declaring is fine; assigning is not.**

---

# Method naming conflicts

Two interfaces, both with a method called `m1`. What happens depends on exactly how they differ — and
there are three cases.

## Case 1 — same signature, same return type

```java
interface Left1  { public void m1(); }
interface Right1 { public void m1(); }

class C1 implements Left1, Right1 {
    public void m1() { System.out.println("one implementation serves both"); }
}
```

Measured on JDK 25 — compiles, prints once.

> **If two interfaces contain a method with the same signature and the same return type, then in the
> implementation class we have to provide implementation for only ONE method.**

> *"Left person came — where is my implementation? This is it. Right person came — where is mine? The
> same one. Both people require the same implementation, so one method serves both."*

## Case 2 — same name, different argument types

```java
interface Left2  { public void m1(); }
interface Right2 { public void m1(int i); }
```

Measured on JDK 25 — both must be implemented, and both run:

```
m1()
m1(int) 5
```

> **If two interfaces contain a method with the same name but different argument types, we must provide
> implementation for BOTH methods — and these methods are overloaded methods.**

## Case 3 — same signature, different return types

```java
interface Left3  { public void m1(); }
interface Right3 { public int m1(); }
```

**Try to implement both:**

```java
class C3 implements Left3, Right3 {
    public void m1() { }
    public int m1() { return 10; }
}
```

Measured on JDK 25:

```
error: method m1() is already defined in class C3
```

Because — as part 09 established — **the return type is not part of the signature**. Two methods named
`m1()` with no parameters are duplicates, whatever they return.

**Try implementing only one:**

```java
class C4 implements Left4, Right4 { public void m1() { } }
```
```
error: C4 is not abstract and does not override abstract method m1() in Right4
```

> [!question]- **Deep dive — the escape routes he tries, and why every one of them fails.** He asks the
> class five separate times whether a Java class can implement any number of interfaces simultaneously,
> gets a confident **yes** each time, and then walks them into this.
>
> **Attempt 1 — put both methods in the class.** `method m1() is already defined`.
>
> **Attempt 2 — declare the class abstract, implement one method, leave the other to a child.**
> ```java
> abstract class Test implements Left, Right { public void m1() { } }
> class SubTest extends Test { public int m1() { return 10; } }
> ```
> Now the child's `int m1()` is trying to **override** the parent's `void m1()` — and overriding
> requires the same return type:
> ```
> error: m1() in SubTest cannot override m1() in Test
>   return type int is not compatible with void
> ```
>
> **Attempt 3 — separate classes, or an inner class for one of them.** That is no longer implementing
> both *simultaneously*, which was the requirement.
>
> > **It is impossible to implement both interfaces simultaneously.**
>
> So the honest interview answer is: **"Yes, a Java class can implement any number of interfaces — with
> one exception: if two interfaces contain a method with the same signature but different return
> types, it is impossible."**

## The exception to the exception — covariant return types

> **Unless the return types are covariant** — a rule that arrived in **Java 1.5**.

```java
interface L { public Object m1(); }
interface R { public String m1(); }

class Cov implements L, R {
    public String m1() { return "covariant works"; }
}
```

Measured on JDK 25:

```
covariant works
```

**One method satisfies both**, because `String` **is** an `Object` — returning a `String` is a valid
way of returning an `Object`. Put the general type in one interface and the specific type in the
other, and the specific one implements both.

---

# Variable naming conflicts

Two interfaces, both with a variable `x`:

```java
interface LeftV  { int x = 777; }
interface RightV { int x = 888; }

class Var implements LeftV, RightV {
    public static void main(String[] a) { System.out.println(x); }
}
```

Measured on JDK 25:

```
error: reference to x is ambiguous
```

**But unlike the method case, this one has a fix.** Interface variables are `public static final`, and
static members are accessed through the type name:

```java
System.out.println(LeftV2.x);
System.out.println(RightV2.x);
```

Measured on JDK 25:

```
777
888
```

> [!important] **The asymmetry is the point of the section.**
> - **Method** naming conflict, case 3 → **no solution** — you cannot implement both.
> - **Variable** naming conflict → **always solvable** — qualify with the interface name.
>
> Because a variable is *read through* a name you can qualify, while a method must be *declared* in the
> class, where only one declaration can exist.

---

# What this part established

| | |
|---|---|
| Every interface method | implicitly **`public`** and **`abstract`** |
| Why public | available to every implementation class, in **any package** |
| Why abstract | the interface is a **specification**; the implementation class implements |
| Forbidden modifiers (his list) | `private`, `protected`, `static`, `final`, `synchronized`, `native`, `strictfp` |
| ⚠️ On JDK 25 | **`private` and `static` are now legal** with a body — the list is **five** |
| Modifier order | not important — `abstract public` = `public abstract` |
| Interface variables are for | **requirement level constants** |
| Every interface variable | implicitly **`public static final`** |
| Why public / static / final | reachable everywhere · no object exists · shared by all implementers |
| Forbidden | `private`, `protected`, `transient`, `volatile` |
| Why `transient` is meaningless | no object ⇒ no serialization ⇒ nothing to skip |
| Initialization | **at the declaration only** — an interface has no static block |
| The error | `= expected` |
| Implementation class | may **read**, may not **assign** |
| A local variable of the same name | legal — it shadows, it does not assign |
| Conflict case 1 — same signature, same return | **one** implementation serves both |
| Conflict case 2 — same name, different args | implement **both**; they are **overloaded** |
| Conflict case 3 — same signature, different return | **impossible** to implement both |
| The exception | **covariant** return types (since 1.5) |
| Variable conflict | `reference to x is ambiguous` — **fixable** by qualifying with the interface name |
