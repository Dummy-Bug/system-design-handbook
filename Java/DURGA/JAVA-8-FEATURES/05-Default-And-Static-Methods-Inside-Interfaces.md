# What an interface could hold, version by version

Before Java 8, an interface was a list of declarations and nothing else.

> **Until 1.7, every method present inside an interface is always `public` and `abstract`, whether we declare it or not.**

All of these are identical:

```java
void m1();
public void m1();
abstract void m1();
public abstract void m1();
```

**Then things were added — but only to methods.**

| Version | What an interface may contain |
|---|---|
| up to 1.7 | `public abstract` methods only |
| **1.8** | **+ default methods, + static methods** |
| **9** | **+ private methods** |

> [!important] **Variables never changed, in any version.** Every variable present inside an interface is always `public static final`, whether it is 1.7, 1.8 or 1.9. Variables-wise no additions. He is asked this directly and answers it directly: **no enhancements related to variables in the newer versions of Java.** Still true on JDK 25.

> [!info] **Private methods, verified.** He mentions them as coming in 1.9. Measured on JDK 25 — a private method and a private static method inside an interface both compile and run. Bisecting with `--release`: **rejected at 8, accepted at 9.**
> ```
> error: private interface methods are not supported in -source 8
>   (use -source 9 or higher to enable private interface methods)
> ```
> They exist so several `default` methods can share helper code without exposing it.

---

# Default methods

## The problem they solve

An interface with two methods, and implementation classes written against it:

```java
interface Interf {
    public void m1();
    public void m2();
}
class Test1 implements Interf { public void m1(){} public void m2(){} }
class Test2 implements Interf { public void m1(){} public void m2(){} }
class Test3 implements Interf { public void m1(){} public void m2(){} }
```

Compiles fine. **How many implementation classes could there be?** Any number.

> [!info] **His example of how many is realistic.** The `Collection` interface is implemented by `ArrayList`, `LinkedList`, `Vector`, `Stack`, `TreeSet`, `HashSet`, `LinkedHashSet` and more. The interface is only one, but implementation classes are multiple.

**Now add one method tomorrow:**

```java
public void m3();
```

Measured on JDK 25:

```
error: Test1 is not abstract and does not override abstract method m3() in Interf
error: Test2 is not abstract and does not override abstract method m3() in Interf
error: Test3 is not abstract and does not override abstract method m3() in Interf
3 errors
```

**Three classes, three errors.** With a hundred implementers it is a hundred errors — and if they belong to other people, in other codebases, you have broken all of them.

> **So once we define an interface and implementation classes already exist, we are not allowed to add any new method to it. That interface is final — we cannot change it.**

That is the wall Java 8 had to get past.

## The fix

```java
interface Interf2 {
    public void m1();
    public void m2();
    default void m3() { System.out.println("Default Method"); }
}
class T1 implements Interf2 { public void m1(){} public void m2(){} }
class T2 implements Interf2 { public void m1(){} public void m2(){} }
class T3 implements Interf2 { public void m1(){} public void m2(){} }
```

Measured on JDK 25 — **compiles, and every implementation class can call `m3()`**:

```
Default Method
Default Method
```

Nothing in `T1`, `T2` or `T3` changed. They never mention `m3` at all.

> **The main objective of default methods: without affecting implementation classes, we can add new methods to an interface.**

The implementation classes get a choice:

- **use** the default method as it is
- **override** it if the default does not suit them
- **ignore** it entirely

## Why the word `default`

Asked in the session, and worth getting right because there is a trap in it.

> [!important] **It is NOT the default modifier.** Default (package-level) access means **no modifier written**, and you are **never allowed to write `default` as an access modifier**. The keyword here means something else entirely: **a method that already has a default implementation.**
>
> And it only exists inside an interface. Measured on JDK 25:
> ```java
> class InClass { default void m1() { … } }
> ```
> ```
> error: modifier default not allowed here
> ```
> Inside a **class**, `default` already means something — the `default` case of a `switch` statement.

## Its other two names

> **Default methods are also known as defender methods or virtual extension methods.**

He stops to unpack the English word, because it explains the whole concept:

> What is the meaning of defender? Defense means protection. A player whose task is to protect their own goal. The person who is going to save our life — that person is called a defender.

**What is it defending?** The implementation classes.

> Why we are using the word defender — it is going to provide protection to all the implementation classes. 'You are not required to implement this method. I am adding it. If you want, you can use it; if you are not satisfied, you can override; if you don't want, you can ignore.'

> [!info] **And why this mattered so much.** If this concept were not there inside Java, then we may miss a number of new features — streams, and several things. All the remaining enhancements are based on this concept. That is literally true: `Collection.stream()` is a default method. Without default methods, adding `stream()` to `Collection` would have broken every collection class ever written.

## Overriding one

```java
interface Interf { default void m1() { System.out.println("Default Method"); } }

class Test implements Interf {
    public void m1() { System.out.println("Overriding version of default method"); }
    public static void main(String[] args) { new Test().m1(); }
}
```

The overriding version runs, not the default. And it must be `public` — the ordinary overriding rule, since the default method is implicitly public.

## The one thing you cannot default: `Object` class methods

```java
interface Obj { default int hashCode() { return 10; } }
```

Measured on JDK 25:

```
error: default method hashCode in interface Obj overrides a member of java.lang.Object
```

> [!important] **The reason is worth reasoning through rather than memorising.** The point of a default method is to **make a method available to the implementation class**. But every class is already a child of `Object`, so `hashCode()`, `equals()`, `toString()` are **already available** to every implementation class.
>
> Test is already a child of Object. Object class methods are already available. Why do we need to make them available through a default method? It is not required — so it is not allowed.

---

# Default methods and multiple inheritance

## First, why classes cannot do it

```java
class P1 { public void m1() { System.out.println("P1 method"); } }
class P2 { public void m1() { System.out.println("P2 method"); } }
class MI extends P1, P2 { }
```

Measured on JDK 25:

```
error: '{' expected
class MI extends P1, P2 { }
                   ^
```

> After `P1` I'm not expecting a comma, I'm expecting a curly brace. It is telling very clearly: don't take comma P2.

Note **where** the error is — at the comma. The compiler rejects the syntax before anything else, and even if you are not calling it, you still get the compile error.

**The reason** is the ambiguity: `P1` has `m1()`, `P2` has `m1()`, and if `C` extends both, `c.m1()` has no answer.

> **This is called the ambiguity problem, or the diamond problem / diamond access problem.** If multiple parents contain the same method with different implementations, there is no way for the child to say which one it wants. So Java does not allow multiple inheritance for classes.

> [!question]- **Deep dive — Python allows it, so how does Python solve the ambiguity?** He goes off the syllabus for this, calling it beyond our limit, and it is worth keeping because it shows the problem is a design choice rather than a law of nature.
>
> ```python
> class P1:
>     def m1(self): print("P1 method")
>
> class P2:
>     def m1(self): print("P2 method")
>
> class C(P1, P2):
>     pass
>
> c = C()
> c.m1()
> ```
>
> **Python resolves it by declaration order.** `class C(P1, P2)` → `P1`'s method wins. Swap them to `class C(P2, P1)` → `P2`'s method wins. If the first parent does not have the method, the next one gets the chance.
>
> In Java there is no way to solve this problem, but in Python there is a way. Python's rule is the **method resolution order**; Java's designers rejected order-dependence as too implicit and banned the situation instead.
>
> His prediction — maybe Java 14, Java 15 they may include class-level multiple inheritance, or the Python style may be copied into Java — has **not** happened. Verified on JDK 25: a class still cannot extend two classes.

## Now the same problem with default methods

Two interfaces, both with a **default** `m1()` — now both have implementations, so the ambiguity is real:

```java
interface Left  { default void m1() { System.out.println("Left Default Method"); } }
interface Right { default void m1() { System.out.println("Right Default Method"); } }
class Dia implements Left, Right { }
```

Measured on JDK 25:

```
error: types Left and Right are incompatible;
  class Dia inherits unrelated defaults for m1() from types Left and Right
```

**inherits unrelated defaults** — exactly the diamond problem, arriving through interfaces.

## The fix: override it

> **When two interfaces contain a default method with the same signature, the implementation class must compulsorily override it — otherwise compile-time error.**

**Option 1 — write your own:**

```java
class Fix1 implements Left2, Right2 {
    public void m1() { System.out.println("Test Class Method"); }
    public static void main(String[] a) { new Fix1().m1(); }
}
```

Measured on JDK 25: `Test Class Method`

**Option 2 — pick one of the inherited ones**, with `InterfaceName.super.methodName()`:

```java
public void m1() { Left3.super.m1(); }
```
```java
public void m1() { Right4.super.m1(); }
```

Measured on JDK 25:

```
Left Default Method
Right Default Method
```

> [!important] **`Left.super.m1()` is the syntax to memorise.** It is the only way to name **which** inherited default you want, and it exists nowhere else in the language.

> **So multiple inheritance IS possible with interfaces, even with default methods** — an interface can extend multiple interfaces, and both can have the same default method, **because the implementation class can always override and disambiguate.** The impossibility applies to classes only.

> [!info] **And if both interfaces declare the same abstract method?** No problem and no ambiguity — the implementation class provides the one implementation, which satisfies both.

---

# Static methods inside interfaces

## Why they were allowed

The argument is about **cost**.

| | Interface | Class |
|---|---|---|
| Constructors | ❌ never | ✅ |
| Instance blocks | ❌ never | ✅ |
| Static blocks | ❌ never | ✅ |
| Weight | **lightweight** | **heavyweight, costly** |

> An interface never contains a constructor, never contains a static block, never contains an instance block. Just declarations. That's why an interface is not a heavyweight component — it is a very lightweight component.

Now consider **utility methods** — `add`, `subtract`, `product`. They take arguments, compute, return. They touch no instance variable and need no object. Before 1.8 they had to live inside a **class** anyway.

> **If everything is static and nowhere related to an object, what is the need of going for a class? Better to go for an interface.**

> [!info] **The analogy — hiring an IAS officer to sweep the house.** If you require a sweeper only, to sweep your house — you are not required to recruit an IAS officer. Recruiting an IAS officer for sweeping purposes, how much stupidness is that? If everything is static, going for a class is the same stupidness.

## How to call one — the four candidates

```java
interface Interf3 {
    public static void sum(int a, int b) { System.out.println("The Sum: " + (a + b)); }
}
class Stat implements Interf3 {
    public static void main(String[] args) {
        Stat t = new Stat();
        t.sum(10, 20);        // 1 — via an object reference
        Stat.sum(10, 20);     // 2 — via the implementation class name
        sum(10, 20);          // 3 — directly
        Interf3.sum(10, 20);  // 4 — via the interface name
    }
}
```

**Only number 4 is valid.** Measured on JDK 25, the first three all fail:

```
error: cannot find symbol   (line 7)
error: cannot find symbol   (line 8)
error: cannot find symbol   (line 9)
```

> **Interface static methods are by default NOT available to the implementation class.** So you cannot reach one through an object reference, through the implementation class name, or by calling it directly. **They must be called using the interface name.**

Keep only form 4 and it works. Measured on JDK 25: `The Sum: 30`

## And the class need not implement the interface at all

```java
class Stat3 {                      // note: no "implements"
    public static void main(String[] args) { Interf5.sum(3, 4); }
}
```

Measured on JDK 25: `The Sum: 7`

> Whether it is the implementation class or a non-implementation class, the interface static method behaves the same. **No priority for implementation classes**, because it is a static method — nowhere related to an object.

> [!info] **A consequence: `overriding` does not apply.** Since the method is not available to the implementation class, you can declare a method with the identical signature in that class and it is **valid but not overriding** — two unrelated methods that happen to share a name. Measured on JDK 25: both the `static` and the instance version compile fine alongside the interface's static method.

## `main()` inside an interface

Since `main` is just a static method:

```java
interface Iface {
    public static void main(String[] args) {
        System.out.println("Interface Main Method");
    }
}
```

```
$ javac Iface.java
$ java Iface
Interface Main Method
```

Measured on JDK 25 — **you can run an interface directly from the command prompt.**

---

# What this part established

| | |
|---|---|
| Up to 1.7, interface methods | always **`public abstract`**, declared or not |
| 1.8 added | **default** methods and **static** methods |
| 9 added | **private** methods (rejected at `--release 8`, accepted at 9) |
| Interface variables | always **`public static final`** — **unchanged in every version** |
| Adding a method to an interface | breaks **every** implementation class |
| Default method purpose | **add new methods without affecting implementation classes** |
| Also known as | **defender methods**, **virtual extension methods** |
| Why `defender` | it **protects** the implementation classes from being broken |
| Why this mattered | streams and most later features depend on it |
| The `default` keyword | not the access modifier — it marks a **default implementation** |
| `default` inside a class | ❌ `modifier default not allowed here` |
| `Object` methods as defaults | ❌ already inherited by every class, so not allowed |
| Classes extending two classes | ❌ error at the **comma** — the **diamond / ambiguity problem** |
| Python | allows it, resolving by **declaration order** |
| Two interfaces, same default | ❌ `inherits unrelated defaults for m1()` |
| The fix | **override it** — write your own, or call `Left.super.m1()` |
| Multiple inheritance with interfaces | **allowed**, because the child can always disambiguate |
| Why static methods in interfaces | **utility methods** — an interface is lightweight, a class is costly |
| Calling an interface static method | **only** through the **interface name** |
| Non-implementing classes | can call it just as well — no priority for implementers |
| `main()` in an interface | legal — the interface runs from the command prompt |
