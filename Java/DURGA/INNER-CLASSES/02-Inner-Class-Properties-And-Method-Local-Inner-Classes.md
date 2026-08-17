# Accessing the outer class's members

Note `01` covered how to reach **into** an inner class. This is the other direction — from inside the inner class, what of the outer class can you see?

```java
class Outer {
    int x = 10;              // instance variable of Outer
    static int y = 20;       // static variable of Outer

    class Inner {
        public void m1() {
            System.out.println(x);
            System.out.println(y);
        }
    }

    public static void main(String[] args) {
        new Outer().new Inner().m1();
    }
}
```

Is this valid? **Most people hesitate at `System.out.println(y)`**, because an inner class is such a thoroughly instance-level thing — every one of them needs an enclosing object to exist at all — that reaching a **static** variable feels like it should be out of bounds.

It is not, and the distinction is one word:

> **Declaring is different from accessing.** Whatever rules govern what an inner class may **declare**, they say nothing about what it may **access**.

Measured on JDK 25:

```
10
20
```

> From a normal or regular inner class we can access **both static and non-static members** of the outer class **directly**.

Instance variable, static variable, private variable, public variable — it makes no difference.

---

# Three variables named x

Now the twist. Take the same name at three different levels:

```java
class Outer {
    int x = 10;                     // instance variable of OUTER

    class Inner {
        int x = 100;                // instance variable of INNER

        public void m1() {
            int x = 1000;           // LOCAL variable of m1
            System.out.println(x);
            System.out.println(this.x);
            System.out.println(Outer.this.x);
        }
    }

    public static void main(String[] args) {
        new Outer().new Inner().m1();
    }
}
```

Three variables, all called `x`, in three different contexts. Measured on JDK 25:

```
1000
100
10
```

Each line reaches a different one:

| Written as | Reaches | Value |
|---|---|---|
| `x` | the **local** variable of `m1` — the nearest one | `1000` |
| `this.x` | the **current inner class object**'s variable | `100` |
| `Outer.this.x` | the **current outer class object**'s variable | `10` |

> **Within an inner class, `this` always refers to the current inner class object.** If we want to refer to the current outer class object, we have to use **outer class name `.this`**.

```mermaid
flowchart TB
    L["<code>x</code><br/><i>local variable of m1</i><br/><b>1000</b>"]
    I["<code>this.x</code><br/><i>current Inner object</i><br/><b>100</b>"]
    O["<code>Outer.this.x</code><br/><i>current Outer object</i><br/><b>10</b>"]
```

## Why not `super.x`?

The obvious guess for reaching the outer class is `super.x`. **The compiler rejects it**, and note `01` already said why:

> The outer class is **not** the parent class and the inner class is **not** the child class.

Measured on JDK 25:

```
error: cannot find symbol
            System.out.println(super.x);
                                    ^
```

`Inner`'s superclass is `Object`, which has no `x`. The relationship to `Outer` is **has-a**, and `super` only ever means is-a.

> [!important] **`Outer.this` is the syntax that exists because there is no inheritance here.** If the outer class really were a parent, `super` would have done the job and this syntax would not need to exist. Its existence is the proof of the has-a rule.

> [!info] **This arrangement is only needed when there is a naming conflict.** With three `x`s you need a way to say which one. If the names were distinct, plain `x` would reach whichever one is in scope and none of this would be required.

---

# Which modifiers apply

For an **outer class** — recapped from the modifiers topic:

`public`, **default**, `final`, `abstract`, `strictfp` — **five**.

For an **inner class**, those five **plus** `private`, `protected` and `static` — **eight**.

Measured on JDK 25, all sixteen cases:

| Modifier | Outer class | Inner class |
|---|---|---|
| `public` | ✅ | ✅ |
| **default** | ✅ | ✅ |
| `final` | ✅ | ✅ |
| `abstract` | ✅ | ✅ |
| `strictfp` | ✅ | ✅ |
| `private` | ❌ | ✅ |
| `protected` | ❌ | ✅ |
| `static` | ❌ | ✅ |
| **Total** | **5** | **8** |

The three that only an inner class gets are exactly the three that need an enclosing type to be meaningful — `private` and `protected` are about visibility **within** something, and `static` is the fourth category of inner class.

> [!info] **`strictfp` counts but does nothing.** All floating-point expressions are evaluated strictly by default, so the keyword is a no-op and `javac` warns that it is not required — see `DECLARATIONS-AND-ACCESS-MODIFIERS/07`. It remains an **applicable modifier**, so the counts of 5 and 8 are what to give.

---

# Nesting of inner classes

Can an inner class contain another inner class? Yes.

> Inside an inner class we can declare another inner class — that is **nesting of inner classes**, and it is possible.

```java
class A {
    class B {
        class C {
            public void m1() {
                System.out.println("innermost class method");
            }
        }
    }
}
```

Three levels. To call `m1()` you need a `C` object; to get a `C` you need a `B`; to get a `B` you need an `A`. So the chain from note `01` just repeats:

```java
class Test {
    public static void main(String[] args) {
        A a = new A();
        A.B b = a.new B();
        A.B.C c = b.new C();
        c.m1();
    }
}
```

Measured on JDK 25:

```
innermost class method
```

And the class files show the nesting depth directly:

```
A.class
A$B.class
A$B$C.class
```

> **Do not assume only one level.** Any number of levels of inner classes is acceptable.

---

# Method local inner classes

The second of the four categories.

> Sometimes we can declare a class **inside a method**. Such types of inner classes are called **method local inner classes**.

## Why they exist — the nested method problem

The motivation is worth following, because it explains a restriction in the language.

Suppose you have a method with 50,000 lines in it, and some functionality is needed **repeatedly** inside it. The best reusable component in Java is a method, so the natural move is to define that functionality as a method and call it wherever needed:

```java
class Test {
    public void m1() {
        // … 50,000 lines …

        public void sum(int x, int y) {          // ✗ a method inside a method
            System.out.println("the sum is " + (x + y));
        }

        sum(10, 20);
        sum(100, 200);
        sum(1000, 2000);
    }
}
```

**This does not compile.**

> **Declaring a method inside another method is not possible in Java. The nested method concept is not allowed.**

So how do you get the functionality? **Two options.**

**Option 1 — declare `sum` at class level.** It works. But if this functionality is required **only** by `m1` and nowhere outside it, you would not want it visible at class level.

**Option 2 — the way round the restriction.** You cannot put a method inside a method. But you **can** put a **class** inside a method, and a class can certainly contain a method:

```java
class Test {
    public void m1() {
        class Inner {
            public void sum(int x, int y) {
                System.out.println("the sum is " + (x + y));
            }
        }

        Inner i = new Inner();
        i.sum(10, 20);
        i.sum(100, 200);
        i.sum(1000, 2000);
    }

    public static void main(String[] args) {
        Test t = new Test();
        t.m1();
    }
}
```

Measured on JDK 25:

```
the sum is 30
the sum is 300
the sum is 3000
```

```mermaid
flowchart LR
    A["method inside a method<br/><i>nested methods</i><br/><b>❌ not allowed in Java</b>"] -->|"so instead"| B["<b>class</b> inside a method,<br/>with the method inside it<br/><b>✅ method local inner class</b>"]
```

> **The main purpose of a method local inner class is to define method-specific, repeatedly required functionality.** They are best suited to **meeting nested method requirements** — wherever nested methods are required, we can run the show with method local inner classes.

## Their scope, and why they are rare

Where is that `Inner` class accessible? Only inside `m1`, exactly like a local variable declared there.

> We can access method local inner classes **only within the method where we declared them**. Outside that method we cannot access them. **Because of this lesser scope, method local inner classes are the most rarely used type of inner class.**

And the companion fact, which he plants here for later:

> **The most commonly used type of inner class is the anonymous inner class.**

Do not answer normal or regular just because that is the one covered so far.

---

# Instance method versus static method

A method local inner class can be declared inside **either** an instance method or a static method. But there is a difference between the two, and it is the ordinary static rule showing through.

```java
class Test {
    int x = 10;                 // instance variable
    static int y = 20;          // static variable

    public void m1() {          // instance method
        class Inner {
            public void m2() {
                System.out.println(x);       // line 1
                System.out.println(y);
            }
        }
        new Inner().m2();
    }

    public static void main(String[] args) {
        new Test().m1();
    }
}
```

Measured on JDK 25:

```
10
20
```

Now make `m1` **static**. The inner class is now sitting in a static area, and a static area cannot reach an instance variable. Measured on JDK 25:

```
error: non-static variable x cannot be referenced from a static context
```

| Inner class declared inside | Can access, of the outer class |
|---|---|
| an **instance** method | **both** static and non-static members directly |
| a **static** method | **only static** members directly |

---

# The most dangerous conclusion — local variables

He flags this as the most important point in the section.

```java
class Test {
    public void m1() {
        int x = 10;                    // local variable of m1
        x = 11;                        // ← reassigned

        class Inner {
            public void m2() {
                System.out.println(x);  // accessing m1's local variable
            }
        }

        Inner i = new Inner();
        i.m2();
    }

    public static void main(String[] args) {
        new Test().m1();
    }
}
```

Measured on JDK 25:

```
error: local variables referenced from an inner class must be final or effectively final
```

> **From a method local inner class we cannot access a local variable of the enclosing method unless that variable is `final` or effectively final** — meaning it is never reassigned after initialisation. The compiler is, in his words, a very decent person about it: the message names the fix.

**Delete the `x = 11;` line and it compiles and prints `10`**, with no `final` keyword anywhere — `x` is then effectively final. That single line is the whole difference.

## Why — the memory argument

He flags this as the reasoning to dig into, and it is the best deep-dive material in the chapter.

> [!question]- **Deep dive — why a non-final local variable cannot be reached, argued from stack and heap.** Open this for the mechanism; the rule above is what gets asked, but this is what makes it stick.
> Three facts have to be in place first:
>
> **1.** **Local variables live on the stack. Objects live on the heap.**
> **2.** A local variable is **created when the method starts executing and destroyed when the method completes.**
> **3.** **Every `final` variable is replaced by its value at compile time.**
>
> Now trace the program. `t.m1()` is called. Control enters `m1`, and `x = 10` is created **on the stack**. Then `new Inner()` runs, and that object is created **on the heap**. Calling `i.m2()` prints `x` — fine, `m1` is still executing, so `x` is still on the stack.
>
> Then `m1` completes. **The local variable `x` is destroyed.** But the `Inner` object on the heap **may still exist** — somebody may still hold a reference to it.
>
> And here is the problem. `m2()` is an inner class method, so it can be called directly on that surviving object without going through `m1` at all. Control arrives inside `m2`, reaches `System.out.println(x)` — and **where is `x` supposed to come from?** `m1` is not running. The stack frame that held `x` is gone.
>
> That is the whole reason for the restriction.
>
> **Now the case that works.** If `x` is never reassigned, fact 3 applies: the compiler can safely **copy the value into the `Inner` object** when that object is constructed, because the value can never change afterwards. So once `m1` completes and the stack frame is gone, `m2` calling `System.out.println(x)` is reading its own captured copy — **there is no dependency on the stack frame at all.**
>
> **This is why reassignment is the thing that breaks it.** If `x` could change after the capture, the `Inner` object's copy and the method's variable would silently disagree, and there would be no honest answer to which one does `m2` print?. Forbidding reassignment removes the question.
>
> Writing `final` was only ever ceremony confirming what the compiler can work out for itself — which is exactly why the keyword stopped being required.

---

# The three exam questions

He builds one program and varies it three times. This is the exact shape the certification question takes.

```java
class Test {
    int i = 10;                  // instance variable
    static int j = 20;           // static variable

    public void m1() {
        int k = 30;              // local variable
        final int m = 40;        // final local variable

        class Inner {
            public void m2() {
                // line 1 — which of i, j, k, m can be accessed here?
            }
        }
    }
}
```

**`k` is never reassigned in this program, so it is effectively final** — which is what makes all three answers work out the way they do. Measured on JDK 25 throughout.

## Question 1 — as written above

| Variable | Accessible? | Why |
|---|---|---|
| `i` | ✅ | `m1` is an instance method, so instance members are reachable |
| `j` | ✅ | static members are always reachable |
| `k` | ✅ | a local variable that is **effectively final** — never reassigned |
| `m` | ✅ | a local variable that **is** `final` |

**All four.**

## Question 2 — `m1` declared `static`

| Variable | Accessible? | Why |
|---|---|---|
| `i` | ❌ | **instance** variable, and we are now in a static context |
| `j` | ✅ | static |
| `k` | ✅ | effectively final |
| `m` | ✅ | final |

**Only `i` fails**, and losing the enclosing instance is the single thing that changed.

## Question 3 — `m2` declared `static`

The one most people get wrong by answering the variables at all.

> **Forget about accessing — the code will not compile.**

A static method inside an inner class is legal to **declare**, but it has no enclosing instance and no captured locals, so three of the four references fail outright:

```
error: non-static variable i cannot be referenced from a static context
error: non-static variable k cannot be referenced from a static context
error: non-static variable m cannot be referenced from a static context
```

**Only `j` survives** — and since the class does not compile, the honest answer to which variables are accessible is that the question does not arise.

> [!important] **If the exam asks why question 3 fails, the answer is the static-context rule.** Older material gives a different reason — that an inner class cannot declare static members at all — which was true through Java 15 and stopped being true in Java 16 (see note `01`). The verdict is the same either way; the reasoning is not.

---

# Modifiers on a method local inner class

The last point, and it comes from an analogy with local variables.

Inside a method, can you declare a local variable `public`, `private` or `protected`? **No** — a local variable's scope is only that method, so access modifiers are meaningless. **The only applicable modifier for a local variable is `final`.**

A method local inner class is in the same position:

> The only applicable modifiers for method local inner classes are **`final`**, **`abstract`** and **`strictfp`**. Applying any other modifier gives a compile-time error.

Measured on JDK 25:

| Modifier | Result |
|---|---|
| **default** | ✅ valid |
| `final` | ✅ valid |
| `abstract` | ✅ valid |
| `strictfp` | ✅ valid |
| `public` | ❌ `illegal start of expression` |
| `private` | ❌ `illegal start of expression` |
| `protected` | ❌ `illegal start of expression` |
| `static` | ❌ `illegal start of expression` |

Note that `final` and `abstract` are allowed **separately**, never together — that combination is illegal anywhere in Java.

---

# What this part established

| | |
|---|---|
| From a normal inner class you can access | **both** static and non-static members of the outer class |
| Declaring vs accessing | you cannot **declare** statics inside; you can **access** them |
| `this` inside an inner class | the current **inner** class object |
| To reach the outer object | **`Outer.this`** |
| `super` to reach the outer class | ❌ — the relation is **has-a**, not is-a |
| Modifiers, outer class | **5** — `public`, **default**, `final`, `abstract`, `strictfp` |
| Modifiers, inner class | **8** — those plus `private`, `protected`, `static` |
| Nesting of inner classes | ✅ any number of levels — `A$B$C.class` |
| A method local inner class is | a class declared **inside a method** |
| Why they exist | Java has **no nested methods** |
| Their purpose | method-specific, **repeatedly required** functionality |
| Their scope | only the method they are declared in — **most rarely used** type |
| Most **commonly** used type | **anonymous** inner classes |
| Inside an **instance** method | can access both static and non-static outer members |
| Inside a **static** method | can access **only static** outer members |
| Local variables of the enclosing method | ❌ unless **`final`** — **effectively final** since Java 8 |
| Modifiers on a method local inner class | only **`final`**, **`abstract`**, **`strictfp`** |
