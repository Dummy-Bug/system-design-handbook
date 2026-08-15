# First, the smaller question

> **Is it possible to create an object for an abstract class directly? No. Indirectly?**

Some of the class expects *yes* — that a constructor must exist for some hidden, indirect route to
object creation.

> **No. For an abstract class we cannot create an object either directly OR indirectly.**
>
> *"When should we go for an abstract class? A partially implemented class. If the implementation is
> not complete, how can you create an object?"*

**So the puzzle stands in its sharpest form:** you can never make one, yet it can have a constructor.
What for?

---

# The answer, by comparison

He builds the same program twice.

## Version 1 — no constructor in the abstract class

```java
abstract class Person {
    String name;
    int age;
}
```

Two properties, no constructor. Every child must therefore initialise everything itself:

```java
class Student extends Person {
    int rollNumber, marks;

    Student(String name, int age, int rollNumber, int marks) {
        this.name = name;              // parent's
        this.age = age;                // parent's
        this.rollNumber = rollNumber;  // own
        this.marks = marks;            // own
    }
}

class Teacher extends Person {
    double salary;
    String subject;

    Teacher(String name, int age, double salary, String subject) {
        this.name = name;              // parent's — AGAIN
        this.age = age;                // parent's — AGAIN
        this.salary = salary;
        this.subject = subject;
    }
}
```

**With two properties this looks harmless.** Now scale it the way he does.

> [!important] **Generalise: 100 properties in `Person`, 1,000 child classes.**
>
> Every one of those 1,000 constructors begins with **the same 100 assignment lines**. `this.name`,
> `this.age`, `this.height`, `this.weight`… a hundred times, copied into a thousand classes.
>
> > **Unnecessary duplicate code — code redundancy.**

## Version 2 — with a constructor in the abstract class

```java
abstract class Person {
    String name;
    int age;

    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

Now the children shrink:

```java
class Student extends Person {
    int rollNumber, marks;

    Student(String name, int age, int rollNumber, int marks) {
        super(name, age);              // ← the 100 lines become ONE
        this.rollNumber = rollNumber;
        this.marks = marks;
    }
}

class Teacher extends Person {
    double salary;
    String subject;

    Teacher(String name, int age, double salary, String subject) {
        super(name, age);              // ← the same one line
        this.salary = salary;
        this.subject = subject;
    }
}
```

> **Whatever the parent holds — 2 properties or 100 — every child needs exactly one line: `super(…)`.**

## The saving, counted

| | Without a constructor | With one |
|---|---|---|
| lines per child constructor | 100 inherited + its own | **1** (`super`) + its own |
| across 1,000 children | **100,000** duplicated lines | **1,000** `super` calls |

---

# The formal answer

> **The main objective of an abstract class constructor is to perform initialization for the instance
> variables which are inheriting from the abstract class to the child class.**
>
> **Whenever we are creating a child class object, the abstract class constructor will be executed to
> perform that initialization — code reusability.**

> [!important] **And this does not contradict "you cannot instantiate an abstract class."** The
> constructor never runs to build a `Person`. It runs **as part of building a `Student`**, to set up the
> half of that `Student` that came from `Person`. Note `17` proved there is only ever one object.

> [!info] **The wrong version of the answer, explicitly rejected.** *"Some people may feel: directly we
> can't create an object for an abstract class, but indirectly we can, and for that purpose the
> constructor is required. **100% wrong statement.** Either directly or indirectly we cannot create an
> object for an abstract class."*

---

# What this part established

| | |
|---|---|
| Object for an abstract class | impossible **directly or indirectly** |
| Without a parent constructor | every child re-initialises **all** inherited properties |
| At scale | 100 properties × 1,000 children = **massive duplication** |
| With a parent constructor | each child needs **one line** — `super(…)` |
| The purpose | initialise the instance variables **inherited** by the child |
| When it runs | whenever a **child** object is created |
| The benefit | **code reusability**, shorter code, better readability |
| The wrong answer | that it enables "indirect" object creation |
