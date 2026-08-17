# The rule this whole part rests on

> **Lambda expressions are applicable only for functional interfaces.** If you do not have a functional interface, you cannot write a lambda expression.

> These two people have that much strong association. Without a functional interface, no chance of a lambda expression.

## One more warm-up, end to end

```java
interface Interf { public int squareIt(int n); }

class Test {
    public static void main(String[] args) {
        Interf i = n -> n * n;
        System.out.println(i.squareIt(4));
        System.out.println(i.squareIt(5));
    }
}
```

Measured on JDK 25:

```
16
25
```

The chain of reasoning, one step at a time — this is the mapping he wants automatic by now:

1. **Which reference holds this lambda?** `Interf`.
2. **Which method does `Interf` contain?** `squareIt`.
3. **Therefore `n` is the argument to `squareIt`, and `n * n` is what `squareIt` returns.**

When `i.squareIt(5)` is called, `n` becomes 5, and `5 * 5` gives 25.

---

# Doubt 1 — are lambda expressions actually used often?

Asked by a student: we do not always have a functional interface, so is this a rare thing?

> **No. Lambda expressions are a very commonly used concept, because functional interfaces are very common.**

Look at what a functional interface actually is — one method, one job. Now look at what ordinary programming consists of:

| Everyday requirement | Shape |
|---|---|
| is `x` greater than 10? | a **condition** → one boolean method |
| `x = x + 1` | an **operation** → one method |
| take a `Student` object and print its information | **consume** an object → one method |
| get me a connection object | **supply** an object → one method |

Every one of those is a single-method job, and Java 8 ships a package full of ready-made functional interfaces for exactly these shapes:

> **`java.util.function`** — several **predefined functional interfaces** covering the general requirements of programming.

That package is a later part of the chapter. The point here is only that the functional-interface shape is not rare — it is what most code is made of.

> The person who uses lambda expressions rarely — that person does not know the subject. If you know lambda expressions, you can use them everywhere.

---

# Doubt 2 — does a lambda generate a `.class` file?

The bigger doubt, raised by several students at once. The answer is **no**, and he proves it live by sorting his working folder by timestamp.

> **A separate `.class` file will never be generated for a lambda expression.** At compile time it is converted into a **private method** of the enclosing class.

## The proof

```java
interface Interf { public int squareIt(int n); }

class Test {
    public static void main(String[] args) {
        Interf i = n -> n * n;
        System.out.println(i.squareIt(4));
    }
}
```

Measured on JDK 25 — the class files produced:

```
Interf.class
Test.class
```

**Two files.** One for the interface, one for the class. Nothing for the lambda.

And the lambda has not vanished — `javap -p Test.class` shows where it went:

```
class Test {
  Test();
  public static void main(java.lang.String[]);
  private static int lambda$main$0(int);
}
```

**`private static int lambda$main$0(int)`** — the lambda body, compiled into a private method of `Test`, exactly as he describes.

## The contrast that settles the misconception

> Some people may feel lambda expressions came to replace anonymous inner classes. No — it is no way related to anonymous inner classes. That is why no `.class` file will be generated.

Write the same thing as an anonymous inner class and compile it. Measured on JDK 25:

```java
Interf2 i = new Interf2() {
    public int squareIt(int n) { return n * n; }
};
```

```
Anon$1.class
Anon.class
Interf2.class
```

**Three files** — the `Anon$1.class` is the anonymous inner class. The lambda version of the same program produces no such file.

> [!info] **Asked in the session: is there any difference between a normal `.class` file and a lambda-related `.class` file?** There is no such thing as a lambda-related class file, so the question does not arise. All class files are the same kind of file.

---

# Lambda expressions with multithreading

## The two ways to define a thread

1. By **implementing `Runnable`**
2. By **extending `Thread`**

`Runnable` contains only `run()` — **one abstract method** — so `Runnable` is a functional interface, and anywhere a `Runnable` is required a lambda can go instead.

## The old way

```java
class MyRunnable implements Runnable {
    public void run() {
        for (int i = 0; i < 10; i++) System.out.println("Child Thread");
    }
}

class ThreadDemo {
    public static void main(String[] args) {
        MyRunnable r = new MyRunnable();
        Thread t = new Thread(r);
        t.start();
        for (int i = 0; i < 10; i++) System.out.println("Main Thread");
    }
}
```

**Count the threads at each point.** Before `t.start()` there is exactly **one** thread — the **main thread**. After `t.start()` there are **two**: the main thread, which carries on with the loop in `main`, and the **child thread**, which executes the `run()` body. Both run **simultaneously**.

Measured on JDK 25 (one run, laid out on one line):

```
Main Thread Main Thread Main Thread Child Thread Child Thread Child Thread Child Thread
Child Thread Child Thread Child Thread Main Thread Main Thread Child Thread Child Thread
Child Thread Main Thread Main Thread Main Thread Main Thread Main Thread
```

**Mixed output — and we cannot predict the exact order.** That is the definition of two threads running at once. Run it again and the interleaving differs.

> [!info] **Why bother with threads at all.** If multiple threads execute simultaneously the job finishes in less time, so **performance improves**. That is the main advantage of multithreading.

## The lambda way

`Runnable` is a functional interface, so the entire `MyRunnable` class is unnecessary:

```java
class ThreadDemo2 {
    public static void main(String[] args) {
        Runnable r = () -> {
            for (int i = 0; i < 10; i++) System.out.println("Child Thread");
        };
        Thread t = new Thread(r);
        t.start();
        for (int i = 0; i < 10; i++) System.out.println("Main Thread");
    }
}
```

Measured on JDK 25 — same mixed interleaving, and only **one** class file (`ThreadDemo2.class`).

> Why this bloody `class MyRunnable implements Runnable` concept? Not required. From Java 1.8 onwards, this is the style we have to follow.

> [!question]- **Deep dive — but the `main` method got longer, so what did we save?** A fair objection raised in the session, and the answer is about the file, not the method.
>
> Yes, `main` grew by the lines that used to live in `run()`. But ask the other question: **how many top-level classes are in the file now?** One instead of two. The `MyRunnable` class — its declaration, its `implements` clause, its method signature, its braces — is gone entirely, and so is the `.class` file it produced.
>
> **The total length of the program went down, and readability went up.** Measuring one method instead of the whole file is what makes the saving look like a loss.

---

# Lambda expressions with collections

The second area where lambdas turn up constantly.

## Setting up the list

```java
import java.util.*;

ArrayList<Integer> l = new ArrayList<Integer>();
l.add(20); l.add(10); l.add(25); l.add(5); l.add(30); l.add(0); l.add(15);
System.out.println(l);
```

Measured on JDK 25:

```
[20, 10, 25, 5, 30, 0, 15]
```

Two things to read off that output:

- **The order is insertion order.** `ArrayList` preserves the order you added things in; it never sorts and never reorders.
- **The square brackets and commas come from `toString()`**, which every collection overrides to print as `[first, second, third]`.

`ArrayList<Integer>` — that angle-bracket syntax is **generics**, and it says this list holds `Integer` objects.

## Sorting needs a `Comparator`

`Collections.sort(l, c)` takes the list and a **comparator**, and the comparator decides the order.

> **`Comparator` contains only one method: `compare(Object obj1, Object obj2)`, and it returns an `int`.**

The contract, which has to be memorised in this exact form:

| Return | Meaning |
|---|---|
| **negative** | `obj1` has to come **before** `obj2` |
| **positive** | `obj1` has to come **after** `obj2` |
| **zero** | `obj1` and `obj2` are **equal** |

> Please insert this point in your mind, then you can understand my next-level discussion. Even if you don't know collections, try to remember these words.

## The old way — a separate comparator class

Ascending order. If 20 and 10 are compared, 20 must come **after** 10, so the smaller element returns negative:

```java
import java.util.*;

class MyComparator implements Comparator<Integer> {
    public int compare(Integer i1, Integer i2) {
        if (i1 < i2) return -1;
        else if (i1 > i2) return 1;
        else return 0;
    }
}

class Coll1 {
    public static void main(String[] args) {
        ArrayList<Integer> l = new ArrayList<Integer>();
        l.add(20); l.add(10); l.add(25); l.add(5); l.add(30); l.add(0); l.add(15);
        System.out.println(l);
        Collections.sort(l, new MyComparator());
        System.out.println(l);
    }
}
```

Measured on JDK 25:

```
[20, 10, 25, 5, 30, 0, 15]
[0, 5, 10, 15, 20, 25, 30]
```

> [!example]- **Deep dive — the live bug: a misspelled class name that compiled and ran anyway.** This happens to him mid-demo and it is worth keeping, because the failure mode is genuinely confusing and costs people hours.
>
> He mistyped the comparator's class name — the declaration said one thing, `new MyComparator()` said another. The expected result is a compile error. **Instead the program compiled and ran, and printed a sorted list.**
>
> Really, I got shocked.
>
> The reason: **an old `MyComparator.class` from an earlier example was still sitting in the working directory.** `javac` did not need the source — it found a matching `.class` file and linked against that. The output was produced by a comparator from a completely different program.
>
> He deletes the stale `MyComparator.class`, recompiles, and **now** the compiler says it cannot find `MyComparator` — the honest error that should have appeared in the first place.
>
> **The lesson:** a `.class` file left in the working directory is as real to the compiler as source code. When behaviour makes no sense — especially when something works that clearly should not — look at what is actually on disk. How stupid it is, man.

## Collapsing the comparator to one line

The `if / else if / else` is three returns choosing between three values, which is exactly what the **ternary operator** is for:

```java
public int compare(Integer i1, Integer i2) {
    return (i1 < i2) ? -1 : (i1 > i2) ? 1 : 0;
}
```

Read it as the same decision tree: if the first condition holds, return `-1`; otherwise test the second; if that holds return `1`; otherwise return `0`.

Measured on JDK 25: `[0, 5, 10, 15, 20, 25, 30]` — identical output.

## The lambda way

`Comparator` has exactly one abstract method, so it is a functional interface, so the class can go:

```java
import java.util.*;

class Coll3 {
    public static void main(String[] args) {
        ArrayList<Integer> l = new ArrayList<Integer>();
        l.add(20); l.add(10); l.add(25); l.add(5); l.add(30); l.add(0); l.add(15);
        Comparator<Integer> c = (i1, i2) -> (i1 < i2) ? -1 : (i1 > i2) ? 1 : 0;
        Collections.sort(l, c);
        System.out.println(l);
    }
}
```

Measured on JDK 25:

```
[0, 5, 10, 15, 20, 25, 30]
```

And the inference chain once more, because it is the same chain every time:

| Question | Answer | Because |
|---|---|---|
| These two arguments belong to which method? | `compare` | `Comparator` is a functional interface — it has only one |
| What type are they? | `Integer` | the reference is `Comparator<Integer>` |

> `class MyComparator implements Comparator`, dot dot dot — all that nonsense, gone.

---

# A taste of what is coming

Two one-liners shown in advance, with the explicit warning not to worry about the syntax yet.

## Printing every element

The Java 7 way needs a **cursor** — an `Iterator` or a `ListIterator`, a `while (it.hasNext())` loop, a `it.next()` inside it. The Java 8 way:

```java
l.stream().forEach(System.out::println);
```

Measured on JDK 25:

```
20
10
25
5
30
0
15
```

> The `::` in `System.out::println` is the **double colon operator** — a **method reference**. Method references and constructor references are a later part of the chapter.

## Collecting only the even numbers

```java
List<Integer> l2 = l.stream().filter(i -> i % 2 == 0).collect(Collectors.toList());
System.out.println(l2);
```

Measured on JDK 25:

```
[20, 10, 30, 0]
```

**One line.** It reads every element of `l`, keeps the even ones, collects them into a **new list**, and returns it — `l` itself is untouched. In Java 7 the same thing is a new `ArrayList`, a loop over every element, an `if`, and an `add`: minimum 10 lines of code.

> [!important] **The import that catches everyone, and it caught him live.** With only `import java.util.*;` the code does not compile. Measured on JDK 25:
> ```
> error: cannot find symbol
>   symbol:   variable Collectors
> ```
> `Collectors` lives in **`java.util.stream`**, which is a **sub-package** of `java.util`.
>
> > **If you import a package, only the classes present inside that package are available — not the classes of its sub-packages.** To use them you need a separate import down to the sub-package.
>
> So `import java.util.stream.*;` has to be added as well.

---

# What this part established

| | |
|---|---|
| Lambda expressions apply | **only** to functional interfaces — no exceptions |
| A lambda generates | **no `.class` file** — it becomes a **private method** of the enclosing class |
| Proof | `javap -p` shows `private static int lambda$main$0(int)` |
| An anonymous inner class generates | `Outer$1.class` — the contrast that shows they are unrelated |
| Are lambdas rare? | no — conditions, operations, consuming and supplying objects are all single-method jobs |
| The package of ready-made ones | **`java.util.function`** |
| `Runnable` | functional interface — `run()` — so a thread body can be a lambda |
| Threads after `t.start()` | **two** — main and child, running simultaneously, **output order unpredictable** |
| `ArrayList` order | **insertion order**; the `[a, b, c]` shape comes from `toString()` |
| `Comparator` | functional interface — `compare(obj1, obj2)` returning `int` |
| negative / positive / zero | `obj1` **before** / **after** / **equal to** `obj2` |
| Stale `.class` files | are linked against as readily as source — the cause of the live misspelling bug |
| `l.stream().forEach(System.out::println)` | `::` is the **method reference** operator |
| Importing a package | does **not** import its sub-packages |
