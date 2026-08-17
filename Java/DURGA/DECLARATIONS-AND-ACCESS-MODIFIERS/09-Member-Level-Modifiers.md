# Member level modifiers

**Member** means **method or variable**. Four access modifiers, in order of increasing reach.

---

## `public`

> **If a member is declared `public`, we can access that member from anywhere.**

And then the twist he warns about before anyone gets comfortable.

```java
package pack1;

class A {                                  // NOT public
    public void m1() { … }                 // public
}
```

From another package, `m1` is `public` — so it should be reachable. Measured on JDK 25:

```
error: A is not public in pack1; cannot be accessed from outside package
```

> [!important] **The rule to take away:**
> > **Before checking member visibility, we have to check class visibility.**
>
> Even though the method is public, the class is not public — that's why it is useless. **Both the class and the member must be public** before anything outside the package can reach it.

And the mirror case — public class, default method. Measured on JDK 25:

```
error: m1() is not public in A2; cannot be accessed from outside package
```

Two different messages for the two different failures: the first names the **class**, the second names the **method**.

---

## default

> **If a member is declared default** (no modifier written) **we can access it only within the current package.** From outside the package, we cannot.
>
> **Hence default access is also known as package level access.**

---

## `private`

> **If a member is `private`, we can access it only within the class.** From outside the class, we cannot — not even from a subclass.

**And `private abstract` is illegal**, for a reason that is pure logic:

> **An abstract method must be available to the child classes so they can provide the implementation. Private methods are not available to the child classes. Hence `private abstract` is an illegal combination for methods.**

Measured on JDK 25:

```
error: illegal combination of modifiers: abstract and private
```

> [!info] **Three illegal pairs, one pattern.** `final abstract`, `strictfp abstract`, `private abstract` — every one of them pairs `abstract` with something that contradicts a child will implement this later. `final` says nobody may override it, `strictfp` says the body behaves a certain way, `private` says nobody can see it.

---

## `protected` — the most misunderstood modifier in Java

He names it that before explaining it, and the rest of the session earns the label.

> **If a member is declared `protected`, we can access it:**
> - **anywhere within the current package**, and
> - **outside the package, only in child classes.**

Or as a formula:

> **protected = default + kids**

## Within the same package — all three forms work

```java
package pack1;

public class A {
    protected void m1() { System.out.println("the most misunderstood modifier"); }
}
```

```java
package pack1;

public class B extends A {
    public static void main(String[] args) {
        A a = new A();   a.m1();     // parent reference, parent object
        B b = new B();   b.m1();     // child reference, child object
        A a1 = new B();  a1.m1();    // parent reference, child object
    }
}
```

Measured on JDK 25:

```
the most misunderstood modifier
the most misunderstood modifier
the most misunderstood modifier
```

**All three.** Inside the package, a protected member behaves exactly like a default one — parent reference or child reference, it does not matter.

## Outside the package — only one form works

Same three shapes, now from `pack2`, in a class `C extends A`. Measured on JDK 25:

| | Code | Result |
|---|---|---|
| 1 | `A a = new A(); a.m1();` | ❌ `m1() has protected access in A` |
| 2 | `C c = new C(); c.m1();` | ✅ **valid** |
| 3 | `A a1 = new C(); a1.m1();` | ❌ `m1() has protected access in A` |

**Look at what 1 and 3 have in common: the reference type is `A`.** 2 is the only one whose reference type is the child.

> **Outside the package we can access protected members only in child classes, and we must use the child reference. A parent reference cannot be used to access protected members from outside the package.**

## The six-case puzzle

Now three levels: `A` in `pack1`; `C extends A` and `D extends C` in `pack2`. `main` is in **`D`**.

Measured on JDK 25:

| | Code | Result |
|---|---|---|
| 1 | `A a = new A(); a.m1();` | ❌ |
| 2 | `C c = new C(); c.m1();` | ❌ |
| 3 | `D d = new D(); d.m1();` | ✅ **valid** |
| 4 | `A a1 = new C(); a1.m1();` | ❌ |
| 5 | `A a1 = new D(); a1.m1();` | ❌ |
| 6 | `C c1 = new D(); c1.m1();` | ❌ |

**Exactly one of the six compiles.** Every failure is `error: m1() has protected access in A`.

> [!important] **The rule, in its full and final form:**
> > **Outside the package, we can access protected members only in child classes, and we must use that particular child class's reference.**
>
> From `D` class, if we want to access, we should use `D` class reference only.
>
> Case 2 is the one that catches everybody — `C` **is** a child of `A`, and `c` **is** a child reference. But the access is happening **inside `D`**, and from inside `D` the only reference type that works is `D`. Case 6 catches the rest: `new D()` is a `D` object, but the **reference** is `C`, and the reference type is what the compiler checks.
>
> When he ran this live the class first answered three valid, then two, then one — and the answer is one.

> [!question]- **Deep dive — why the rule is about the reference type and not the object.** The reason the JLS gives, and it makes the six cases obvious rather than arbitrary.
>
> The purpose of `protected` is to let a subclass work on **its own inherited state** — not to give it a general key to every instance of the parent. If `D` could call `a.m1()` on any `A`, then any class anywhere could reach a protected member just by declaring itself a subclass and then handling other people's objects. The subclass would become a loophole in the parent's encapsulation.
>
> So the language restricts it: from inside `D`, a protected member of `A` is accessible only through a reference **of type `D` or a subtype** — that is, only on objects that are me or my kind. Since the compiler works from the **static** reference type, `C c1 = new D()` fails even though the object really is a `D`.

---

# The visibility summary table

| Accessed from | `private` | default | `protected` | `public` |
|---|:---:|:---:|:---:|:---:|
| within the **same class** | ✅ | ✅ | ✅ | ✅ |
| **child** class of the **same package** | ❌ | ✅ | ✅ | ✅ |
| **non-child** class of the **same package** | ❌ | ✅ | ✅ | ✅ |
| **child** class **outside** the package | ❌ | ❌ | ✅ ***child reference only*** | ✅ |
| **non-child** class **outside** the package | ❌ | ❌ | ❌ | ✅ |

**Two conclusions read straight off it:**

> **The most restricted access modifier is `private`. The most accessible is `public`.**
>
> **`private` < default < `protected` < `public`**

---

# Which to use

> **Recommended modifier for a data member (variable): `private`.**
> **Recommended modifier for a method: `public`.**

The reasoning is one sentence each:

- **Variables private** — because of **data hiding**, the OOP principle. In C the default modifier for a variable is private only.
- **Methods public** — a method is my service, and my service should be accessible to several people.

Data in, behaviour out.

---

# What this part established

| | |
|---|---|
| `public` member | reachable from anywhere — **but the class must be public too** |
| The rule | **check class visibility before member visibility** |
| default | **package level access** |
| `private` | within the class only |
| `private abstract` | ❌ — abstract needs a child to implement it; private hides it from children |
| `protected` = | **default + kids** |
| Inside the package | parent **or** child reference, both fine |
| Outside the package | **only in child classes**, and **only through that child's own reference** |
| The six-case puzzle | exactly **one** of six compiles |
| Why reference type, not object | otherwise any subclass would be a loophole in the parent's encapsulation |
| Most restricted → most accessible | `private` < default < `protected` < `public` |
| Recommended for variables | **`private`** — data hiding |
| Recommended for methods | **`public`** — a method is a service |
