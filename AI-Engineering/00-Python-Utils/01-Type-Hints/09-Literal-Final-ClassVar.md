#python #type-hints #typing #literal #python-utils


`05-Built-In-Generics` made the same move one level out: `list` named a container and said nothing about the contents, so the brackets were added. This concept makes it again, one level further in. The annotation names a *type* and says nothing about **which values**.

## `str` is true and far too wide

```python
 1  def set_status(job: str, status: str) -> None:
 2      print(f"{job} -> {status}")
 3
 4
 5  set_status("build", "running")
 6  set_status("build", "runnning")
 7  set_status("build", "banana")
```

Line 6 has a typo — three n's. Line 7 is a status that has never existed in this system.

```
$ mypy st0.py
Success: no issues found in 1 source file
```

```
$ python3 st0.py
build -> running
build -> runnning
build -> banana
```

Both go through. `str` is a completely true annotation for all three, and every typo satisfies it. There are exactly three legal statuses and the annotation admits several billion.

## Naming the values

```python
 1  from typing import Literal
 2
 3
 4  def set_status(job: str, status: Literal["pending", "running", "done"]) -> None:
 5      print(f"{job} -> {status}")
 6
 7
 8  set_status("build", "running")
 9  set_status("build", "runnning")
10  set_status("build", "banana")
```

```
$ mypy st1.py
st1.py:9:  error: Argument 2 to "set_status" has incompatible type "Literal['runnning']"; expected "Literal['pending', 'running', 'done']"  [arg-type]
st1.py:10: error: Argument 2 to "set_status" has incompatible type "Literal['banana']"; expected "Literal['pending', 'running', 'done']"  [arg-type]
```

Both caught, and the message spells out the legal set for whoever has to fix it.

`Literal[...]` restricts a type to **exact values** — not "a string", but "one of these three strings". It works for numbers and booleans too: `Literal[0, 1]`, `Literal[True]`.

## The other answer: `Enum`

A fixed set of named values is what an enum is for in most languages, and Python has one:

```python
 1  from enum import Enum
 2
 3
 4  class Status(Enum):
 5      PENDING = "pending"
 6      RUNNING = "running"
 7      DONE = "done"
 8
 9
10  def set_status(job: str, status: Status) -> None:
11      print(f"{job} -> {status.value}")
12
13
14  set_status("build", Status.RUNNING)
15  set_status("build", "running")
```

```
$ mypy st2.py
st2.py:15: error: Argument 2 to "set_status" has incompatible type "str"; expected "Status"  [arg-type]
```

Also caught. The difference shows up when you delete the checker from the picture:

```
$ python3 st2.py
build -> running
Traceback (most recent call last):
  File "st2.py", line 15, in <module>
    set_status("build", "running")
  File "st2.py", line 11, in set_status
    print(f"{job} -> {status.value}")
AttributeError: 'str' object has no attribute 'value'
```

Line 15 **crashed**. An `Enum` is a real class producing real objects, so a bare string fails at runtime whether or not anyone ran a checker.

`Literal` is static-only. Run `st1.py` and it prints `banana` quite happily — the errors exist only for mypy.

| | `Literal` | `Enum` |
|---|---|---|
| enforcement | checker only | checker **and** runtime |
| the value at runtime | the plain string `"running"` | a `Status` object; `.value` gets the string |
| JSON / HTTP / DB | already the right shape | `.value` on the way out, `Status(...)` on the way in |
| cost | one import, no objects | a class, and conversions at every boundary |

The rough rule: **`Literal` when the value is already a string flowing through your system** — an API field, a config key, a tool name. **`Enum` when you want a real object with methods, or runtime enforcement.**

## Narrowing shrinks the set

Give the union a name on line 3 and reuse it:

```python
 1  from typing import Literal
 2
 3  Status = Literal["pending", "running", "done"]
 4
 5
 6  def describe(s: Status) -> str:
 7      reveal_type(s)
 8      if s == "pending":
 9          return "waiting in the queue"
10      reveal_type(s)
11      if s == "running":
12          return "in progress"
13      reveal_type(s)
14      if s == "done":
15          return "finished"
16      reveal_type(s)
```

```
$ mypy narrowlit.py
narrowlit.py:7:  note: Revealed type is "Literal['pending'] | Literal['running'] | Literal['done']"
narrowlit.py:10: note: Revealed type is "Literal['running'] | Literal['done']"
narrowlit.py:13: note: Revealed type is "Literal['done']"
Success: no issues found in 1 source file
```

Three values at line 7, two at line 10, one at line 13. This is the narrowing from `07-Unions-And-Optionality`, applied to a union of values rather than a union of types — each `if` eliminates one member.

**And there are four `reveal_type` calls but only three notes.** Line 16 got no answer at all, because by then `s` has no possible values left, so mypy worked out that **no execution can reach line 16** and didn't analyse it.

That's `Never` — the type with no values, from `08-Any-Object-Never`. There it came from a function that always raised; here it comes from narrowing having eliminated everything.

> [!info] It's also why `-> str` doesn't produce a *missing return statement* error, even though the function visibly ends without returning. The end is unreachable, so no path falls off it.

## `assert_never` — making exhaustiveness checkable

`assert_never` is an ordinary function in `typing`, and its whole implementation is four lines:

```python
def assert_never(arg: Never, /) -> Never:
    value = repr(arg)
    ...
    raise AssertionError(f"Expected code to be unreachable, but got: {value}")
```

```
signature: (arg: Never, /) -> Never
```

**The signature is the entire trick: its parameter is annotated `Never`.**

So `assert_never(s)` type-checks only if the checker believes `s` has no possible values at that point. Every case handled → `s` is `Never` → the call is valid. One case missed → `s` still holds that value → passing it to a `Never` parameter is an error.

It is a way of writing *"execution cannot reach this line"* in a form that gets verified.

```python
 1  from typing import Literal, assert_never
 2
 3  Status = Literal["pending", "running", "done"]
 4
 5
 6  def describe(s: Status) -> str:
 7      if s == "pending":
 8          return "waiting in the queue"
 9      if s == "running":
10          return "in progress"
11      if s == "done":
12          return "finished"
13      assert_never(s)
```

```
$ mypy exh1.py
Success: no issues found in 1 source file
```

Now the thing that happens six months later — someone adds a state on **line 3** and doesn't touch `describe`:

```python
 3  Status = Literal["pending", "running", "done", "failed"]
```

```
$ mypy exh2.py
exh2.py:13: error: Argument 1 to "assert_never" has incompatible type "Literal['failed']"; expected "Never"  [arg-type]
```

**It names the case you forgot.** Not "something is missing" — `Literal['failed']`, at line 13, in every function that switches on `Status`. Widen the type in one place and every unhandled switch reports itself.

### At runtime it fails loudly

The checker only sees what it can see. If a value gets in from an untyped caller, or from JSON, the call is actually reached:

```
$ python3 an_run.py
in progress
Traceback (most recent call last):
  File "an_run.py", line 17, in <module>
    print(describe("banana"))
  File "an_run.py", line 13, in describe
    assert_never(s)
AssertionError: Expected code to be unreachable, but got: 'banana'
```

It raises, and it prints the offending value.

### Without it, the same omission is silent

```python
 1  from typing import Literal
 2
 3  Status = Literal["pending", "running", "done", "failed"]
 4
 5
 6  def describe(s: Status) -> None:
 7      if s == "pending":
 8          print("waiting in the queue")
 9      if s == "running":
10          print("in progress")
11      if s == "done":
12          print("finished")
```

```
$ mypy exh3.py
Success: no issues found in 1 source file
```

Same missing state, and **nothing at all**. `describe("failed")` runs, matches no branch, returns `None`, prints nothing. No error at check time, no error at runtime — the bug is a blank field in a log six weeks later.

> [!important] `assert_never` turns *"did I handle every case?"* from something you remember to check into something both the checker and the runtime enforce. It works because `Never` has no values: reaching a line where the variable must be `Never` is only possible if every case really was eliminated.
>
> Any place a role, a status, or a result kind is switched on, this is what makes adding a fourth kind break the build instead of producing a silent no-op.

## `Final` — a constant that says so

Every codebase has these at the top of a module:

```python
 1  MAX_RETRIES = 3
 2  TIMEOUT_SECONDS = 30
 3
 4
 5  def retry_loop() -> None:
 6      for i in range(MAX_RETRIES):
 7          print(f"attempt {i}")
 8
 9
10  MAX_RETRIES = 0
11  retry_loop()
```

Line 10 is the kind of thing that arrives four hundred lines down in a real file, or in someone else's merge.

```
$ mypy fin0.py
Success: no issues found in 1 source file
```

```
$ python3 fin0.py
```

**Blank.** `retry_loop()` printed nothing at all — line 10 set `MAX_RETRIES` to `0`, so `range(0)` looped zero times. A silent behaviour change, with no complaint from anywhere.

### Capitals do nothing

The obvious objection is that `MAX_RETRIES` is in capitals, so surely something knows it's a constant. Nothing does. **Python has no `const` keyword**, and `MAX_RETRIES` and `max_retries` are the same kind of name with identical rules. The capitals are a message to human readers that no tool reads.

That is exactly the gap from `02-Why-Bother-If-Nothing-Enforces-Them`: a claim written as `# don't reassign this` or as capital letters exists only as marks on a screen, while a claim written as an annotation ends up somewhere a program can reach.

### Saying it so something can read it

```python
 1  from typing import Final
 2
 3  MAX_RETRIES: Final = 3
 4  TIMEOUT_SECONDS: Final[int] = 30
 5
 6
 7  def retry_loop() -> None:
 8      for i in range(MAX_RETRIES):
 9          print(f"attempt {i}")
10
11
12  MAX_RETRIES = 0
13  retry_loop()
```

```
$ mypy fin1.py
fin1.py:12: error: Cannot assign to final name "MAX_RETRIES"  [misc]
```

Caught at the reassignment, naming the constant.

Two spellings, both useful:

- **`Final`** alone — the type is inferred from the value. `MAX_RETRIES` is an `int` because `3` is one.
- **`Final[int]`** — states the type as well, for when the value alone would infer something narrower or wider than you meant.

### It is still only a claim

```
$ python3 fin1.py
```

Blank again. **The reassignment still happened** — the loop still ran zero times, exactly as before.

> [!warning] If you know `final` from Java, adjust one thing: there the compiler enforces it and the class genuinely cannot be built. `Final` here is a claim a checker verifies and the interpreter never looks at. It means *"nobody should reassign this, and mypy will tell you if they try"* — not *"this cannot be reassigned."*
>
> Same as every other annotation in this folder, and worth re-noticing precisely because `final` is a keyword you already trust in another language.

## `ClassVar` — shared, or just a default?

Two lines in a class body, identical in shape:

```python
 1  class Job:
 2      total_created = 0
 3      name = "unnamed"
 4
 5      def __init__(self, name: str) -> None:
 6          self.name = name
 7          Job.total_created += 1
 8
 9
10  a = Job("build")
11  b = Job("test")
12
13  print(a.name, b.name)
14  print(a.total_created, b.total_created, Job.total_created)
15  print(Job.name)
16  print("a.__dict__ =", a.__dict__)
```

```
$ python3 cv0.py
build test
2 2 2
unnamed
a.__dict__ = {'name': 'build'}
```

Line 14 prints `2 2 2` — one counter, three ways of reading it. No surprise.

**Line 13 prints `build test`, not `unnamed unnamed`**, and line 16 says why.

**Attribute lookup checks the instance first, then the class.** `a.__dict__` is `{'name': 'build'}`, put there by line 6. So `a.name` finds the instance's own copy and never reaches the class. Line 15 confirms `Job.name` is still `"unnamed"`, untouched.

So the two identical-looking lines do opposite jobs:

- **Line 2, `total_created = 0`** — genuinely shared. Never assigned on an instance, so every lookup falls through to the class and finds the same one.
- **Line 3, `name = "unnamed"`** — a **default**, shadowed the instant `__init__` assigns `self.name`. Only ever visible on an instance that skipped the assignment.

Nothing in the code says which you meant.

### Marking the wrong one

`ClassVar` might look like it means *"this line is in the class body"* — which would make both lines 2 and 3 qualify. Try it:

```python
 1  from typing import ClassVar
 2
 3
 4  class Job:
 5      total_created: ClassVar[int] = 0
 6      name: ClassVar[str] = "unnamed"
 7
 8      def __init__(self, name: str) -> None:
 9          self.name = name
10          Job.total_created += 1
```

```
$ mypy cv1.py
cv1.py:9: error: Cannot assign to class variable "name" via instance  [misc]
```

Line 9 is now an error — and line 9 is `self.name = name`, the line the constructor needs. Marking `name` as `ClassVar` contradicts what the class does.

> [!important] `ClassVar` does not mean "declared in the class body" — every line there is. It means **"this belongs to the class, and no instance ever gets its own."**

`total_created` qualifies. `name` does not: line 9 gives each instance its own, and the class-body value is just a default for anyone who skips it.

### What it catches

Mark only the honest one, and the bug it exists for shows up:

```python
 1  from typing import ClassVar
 2
 3
 4  class Job:
 5      total_created: ClassVar[int] = 0
 6
 7      def __init__(self) -> None:
 8          Job.total_created += 1
 9
10
11  a = Job()
12  b = Job()
13  print("start          ", a.total_created, b.total_created, Job.total_created)
14
15  Job.total_created = 99                  # via the CLASS
16  print("after Job.  =99", a.total_created, b.total_created, Job.total_created)
17
18  a.total_created = 500                   # via the INSTANCE
19  print("after a.   =500", a.total_created, b.total_created, Job.total_created)
20  print("a.__dict__ =", a.__dict__)
21  print("b.__dict__ =", b.__dict__)
```

```
$ mypy cv3.py
cv3.py:18: error: Cannot assign to class variable "total_created" via instance  [misc]
```

**Only line 18.** Line 15 is silent — assigning *through the class* is exactly what a class variable is for. Line 18 goes through `a`, an instance.

The runtime shows why they are not interchangeable:

```
$ python3 cv3.py
start            2   2   2
after Job.  =99  99  99  99
after a.   =500 500  99  99
a.__dict__ = {'total_created': 500}
b.__dict__ = {}
```

**Line 15, through the class** — all three readings become `99`. One value changed, everyone sees it. Shared state behaving as shared state.

**Line 18, through the instance** — `a` reads `500`; `b` and `Job` still read `99`.

The last two lines give the mechanism. `a.__dict__` now holds its own `total_created` and `b.__dict__` is empty. The assignment never touched the shared counter — **it created a new attribute on `a` that hides it**, the same shadowing that made `self.name` hide `Job.name` earlier.

> [!warning] `a.total_created = 500` looks like updating a counter and does the opposite: `a` breaks off from the shared value and disagrees with the rest of the program from then on. No error, no warning, and the symptom surfaces later as one object with a stale count.
>
> Reading `a.total_created` is fine and normal. **Writing** it through an instance is almost always a mistake, and `ClassVar` is what makes it visible.

The two annotations mark opposite intentions in lines that look the same:

| line in the class body | means |
|---|---|
| `name: str = "unnamed"` | every instance gets its own; this is the **default** |
| `total_created: ClassVar[int] = 0` | **one, shared** by the class; instances must not shadow it |

## What this concept claims

**All three of these narrow what an annotation permits, in a direction the plain type cannot express — which exact values, whether it may be reassigned, and whether it is shared.**

Five things to carry:

1. `Literal` restricts to exact values. `str` for a status is true and admits every typo; `Literal["pending", "running", "done"]` admits three things.
2. `Literal` is checker-only; `Enum` is a real object enforced at runtime too. Choose `Literal` when the value is already a string moving through your system, `Enum` when you want an object or runtime enforcement.
3. Narrowing shrinks a value-union the same way it shrinks a type-union, and once every member is eliminated the variable is `Never` and the line is unreachable.
4. `assert_never` makes exhaustiveness checkable: it takes a `Never`, so the call only compiles if every case was handled — and widening the type names the case you forgot.
5. `Final` and `ClassVar` are claims, not enforcement. `Final` flags reassignment while the reassignment still happens; `ClassVar` flags writing shared state through an instance, which at runtime silently creates a shadowing attribute instead.
