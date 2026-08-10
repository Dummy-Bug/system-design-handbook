#python #type-hints #typing #annotated #python-utils

## A rule you can't write down

An agent's run configuration:

```python
 1  class RunConfig:
 2      def __init__(
 3          self,
 4          max_retries: int,
 5          temperature: float,
 6          model: str,
 7      ) -> None:
 8          self.max_retries = max_retries
 9          self.temperature = temperature
10          self.model = model
```

Three honest annotations. And three real rules the code depends on, none of them written anywhere:

- `max_retries` must be **at least 1** — zero means the retry loop never runs
- `temperature` must be **between 0.0 and 2.0** — the provider rejects anything else
- `model` must be **one of a known set**

The third one you can already express: `Literal["gpt-4o", "claude-opus-5"]` from `09-Literal-Final-ClassVar`, or an `Enum`. That's a genuine type.

The first two are not.

```python
1  from typing import Literal
2
3  max_retries: Literal[1, 2, 3, 4, 5]
4  max_retries: int > 0
```

Line 3 works, but only by **enumeration** — `Literal` lists exact values, and "at least 1" is infinitely many. Line 4 is what you'd want to write:

```
$ mypy an0c.py
an0c.py:4: error: Invalid type comment or annotation  [valid-type]
```

(It also reports `Name "max_retries" already defined on line 3` — an artefact of putting both attempts in one file. Noise.)

```
$ python3 an0c.py
max_retries: int > 0
             ^^^^^^^
TypeError: '>' not supported between instances of 'type' and 'int'
```

Both object, and Python's reason is the instructive one. It's **not** a syntax error — the line parses. An annotation is an ordinary expression that gets **evaluated**, and evaluating `int > 0` means comparing the class `int` against the integer `0`, which nothing supports.

So the annotation slot holds a type. "At least 1" is not a type, and there is nowhere else in the annotation to put it.

## Three places the rule could live

**A comment.** `max_retries: int  # must be >= 1`. Nothing reads it. Same category as carefully naming a parameter `thread_id` in `12-Type-Aliases-And-NewType` — documentation for humans, invisible to every tool.

**A `NewType`.** `PositiveInt = NewType("PositiveInt", int)` does make a distinct type, which is real progress. But look at what it can carry: `NewType(name, supertype)` takes a name and a base type, and that is all. **There is no slot for `>= 1`.** The rule would have to be encoded in the name and enforced by hand at every construction site.

**A structure off to one side.** Keep the annotations and put the rules next to them:

```python
CONSTRAINTS = {
    "max_retries": {"ge": 1},
    "temperature": {"ge": 0.0, "le": 2.0},
}
```

This one actually works, and it's worth being precise about why it's still wrong — because the two failures are what `Annotated` is shaped to fix.

**It drifts.** Rename `max_retries`, delete a parameter, and the dict silently goes stale. Nothing ties the two together, so no tool can report that the correspondence broke.

**It doesn't travel with the type.** From `04-Where-Annotations-Live`, annotations live on the function or class object itself, so they move with it — through imports, through subclassing, into anything that inspects the object. A dict off to one side has to be *found* separately. Hand your function to a library and it can read `__annotations__` and see `int`; it has no way to know your rules exist at all.

> [!important] The requirement that falls out: put the extra information **inside the annotation**, where anything reading the type will find it — without changing what the type is.

## `Annotated`

```python
 1  from typing import Annotated, get_type_hints
 2
 3
 4  class Ge:
 5      def __init__(self, value: int) -> None:
 6          self.value = value
 7
 8      def __repr__(self) -> str:
 9          return f"Ge({self.value})"
10
11
12  def configure(
13      max_retries: Annotated[int, Ge(1)],
14      note: Annotated[str, "anything at all", 42, ["even a list"]],
15  ) -> None:
16      print(max_retries, note)
17
18
19  reveal_type(configure)
20
21  configure(3, "ok")
22  configure(-5, "ok")
23  configure("three", "ok")
24
25  print(get_type_hints(configure))
26  print(get_type_hints(configure, include_extras=True))
```

Line 13 is the real use. Line 14 is a probe — three unrelated objects in one annotation, to find out what `Annotated` will tolerate.

```
$ mypy an1.py
an1.py:19: note: Revealed type is "def (max_retries: int, note: str)"
an1.py:23: error: Argument 1 to "configure" has incompatible type "str"; expected "int"  [arg-type]
```

```
$ python3 an1_run.py
3 ok
-5 ok
three ok
{'max_retries': <class 'int'>, 'note': <class 'str'>, 'return': <class 'NoneType'>}
{'max_retries': typing.Annotated[int, Ge(1)], 'note': typing.Annotated[str, 'anything at all', 42, ['even a list']], 'return': <class 'NoneType'>}
```

**Line 19 — the wrapper isn't even mentioned.** mypy reports `max_retries: int`. To a type checker, `Annotated[int, anything]` simply *is* `int`.

Which decides lines 22 and 23. `-5` violates `Ge(1)` and is **not** flagged, because mypy never saw a constraint. `"three"` **is** flagged, because the type underneath is unchanged and still doing its job.

**Line 14 is legal.** A string, an `int` and a list side by side, and neither tool objects. The extras are **arbitrary objects**; `Annotated` doesn't interpret them, it stores them.

And `configure("three", "ok")` printed `three` at runtime without crashing. Concept 1's rule holds — `Annotated` changes nothing about enforcement.

The last two printed lines are the mechanism:

- `get_type_hints(configure)` → `{'max_retries': <class 'int'>, …}`. **Extras stripped by default.** Every existing tool that reads annotations to learn types is completely unaffected.
- `get_type_hints(configure, include_extras=True)` → `typing.Annotated[int, Ge(1)]`. Ask, and they're there.

> [!important] `Annotated[X, …]` **is** `X` to anything that only wants the type, and carries a payload for anything that asks for it. Two audiences, one annotation, neither disturbing the other.

## What the object actually is

Nothing about `Annotated` requires a function or a class. It's a value:

```python
1  from typing import Annotated
2
3  X = Annotated[int, "hello", 42]
4
5  print(X)
6  print(X.__metadata__)
7  print(X.__origin__)
```

```
$ python3 an4.py
typing.Annotated[int, 'hello', 42]
('hello', 42)
<class 'int'>
```

- **Line 5** — it prints itself back. An ordinary value in an ordinary variable.
- **Line 6** — `__metadata__` is a **plain tuple** of everything after the type. `('hello', 42)`.
- **Line 7** — `__origin__` is the type itself, `<class 'int'>`.

> [!important] `Annotated` is a box with two compartments: **the type**, and **a tuple of whatever else you put in.** That is the whole of it.

## Who reads the extras

Nobody — unless somebody writes code to. `Ge` above is a class invented for this note; it means what its reader decides it means.

And "a library reads the metadata" is a loop over a tuple:

```python
1  X = Annotated[int, "hello", 42]
2
3  for extra in X.__metadata__:
4      print("found:", extra)
```

The only extra step for a real one is fetching that tuple off a function's annotations rather than a variable, and doing something more useful than printing:

```python
 1  from typing import Annotated, get_type_hints
 2
 3
 4  class Ge:
 5      def __init__(self, value: int) -> None:
 6          self.value = value
 7
 8
 9  def check(fn, **kwargs):
10      hints = get_type_hints(fn, include_extras=True)
11      for name, value in kwargs.items():
12          for extra in getattr(hints.get(name), "__metadata__", ()):
13              if isinstance(extra, Ge) and value < extra.value:
14                  raise ValueError(f"{name}={value} violates Ge({extra.value})")
15      return fn(**kwargs)
16
17
18  def configure(max_retries: Annotated[int, Ge(1)], temperature: float) -> None:
19      print("configured:", max_retries, temperature)
20
21
22  check(configure, max_retries=3, temperature=0.7)
23  check(configure, max_retries=0, temperature=0.7)
```

Line 10 asks for annotations **with** extras. Line 12 loops the tuple off each one — `getattr(…, "__metadata__", ())` means a plain `float` with no `Annotated` yields an empty tuple and is skipped. Line 13 recognises `Ge` specifically, because `check` is the code that defined `Ge` and knows what it stands for.

```
$ python3 an2.py
configured: 3 0.7
Traceback (most recent call last):
  File "an2.py", line 23, in <module>
    check(configure, max_retries=0, temperature=0.7)
  File "an2.py", line 14, in check
    raise ValueError(f"{name}={value} violates Ge({extra.value})")
ValueError: max_retries=0 violates Ge(1)
```

Line 22 runs, line 23 raises. The constraint is enforced — by a plain function, not by Python.

> [!info] This is the interview-relevant sentence, and it's worth being able to say once rather than drill: **a runtime library enforces `Annotated` constraints by calling `get_type_hints(…, include_extras=True)` and recognising the objects it put there itself.** It is the same answer as concept 1's — nothing is enforced by the language; a library chooses to read the annotations — one level up, now with the metadata riding along inside the annotation.
>
> You will not write that reader. Knowing it exists is what separates using a constraint because the docs said so from knowing why it can work at all.

## The form you'll actually write

`Ge(1)` was a *rule*. The extras can equally be a **function**, and that's the form that turns up in agent state.

An agent's state is shared, and several steps update it. Each step returns only the keys it touched, and the runtime merges that into the running state:

```python
1  class State(TypedDict):
2      messages: list[str]
3      step: int
4
5
6  state: State = {"messages": ["user question"], "step": 0}
7  update: State = {"messages": ["plan the search"], "step": 1}
8
9  merged = {**state, **update}
```

```
$ python3 dm1.py
{'messages': ['plan the search'], 'step': 1}
```

**The user's own question is gone**, overwritten by a step that only meant to add a line.

> [!info] `**` inside a dict literal unpacks that dict's pairs into the one being built.
>
> ```python
> a = {"x": 1, "y": 2}
> b = {"y": 99, "z": 3}
> ```
> ```
> $ python3 dm0.py
> {'x': 1, 'y': 2}
> {'x': 1, 'y': 99, 'z': 3}
> {'y': 2, 'z': 3, 'x': 1}
> ```
>
> `{**a}` copies. `{**a, **b}` takes `a`'s pairs then `b`'s, so on a shared key **the last one wins** — `y` is 99. Swap the order and `y` is 2. Keys print in first-seen order, which is why the third line leads with `b`'s.
>
> It's the same `**` as `def check(fn, **kwargs)`, pointed the other way: there it collects keyword arguments into a dict, here it spreads a dict back out.

Now the observation that matters: **overwriting is exactly right for `step`.** You want 1 to supersede 0. It is only wrong for `messages`, where the two lists should have been joined.

Two keys, one merge, two behaviours needed. So where does "join instead of overwrite" live?

- **In the merge code** — `if key == "messages": …`. But that code is the framework's, generic across every agent, and has never heard of your keys. Adding a field to your own state would mean editing the framework.
- **In a side dict** — ruled out at the top of this note. It drifts on a rename and it doesn't travel with the class.
- **Attached to the key**, in `State` itself, where the merge code will find it while reading the type it already has to read.

Which is `Annotated`:

```python
1  import operator
2
3
4  class State(TypedDict):
5      messages: Annotated[list[str], operator.add]
6      step: int
```

Line 5 reads: *a list of strings — and when two updates to this key meet, combine them with `operator.add`.* Line 6 carries no extra, so `step` keeps the default overwrite.

`operator.add(x, y)` is the `+` operator as a function:

```
$ python3 dm2.py
5
['a', 'b']
```

Arithmetic on numbers; on lists, `+` **concatenates** — which is precisely what `messages` needs.

> [!important] Nothing new about `Annotated` is involved. The extras are arbitrary objects and a function is an object. Earlier the extra was a `Ge(1)` *describing* a rule; here it's a function that *performs* one.
>
> The reason it has to go here is per-key behaviour: `messages` appends and `step` overwrites, so the instruction can't live in the shared merging code, and a side table would drift. **`Annotated` is how per-key behaviour gets attached to a type.**

The reading side needs no new ideas — the extras sit in a tuple, exactly as in `an4.py`:

| expression | is | gives |
|---|---|---|
| `State.__annotations__` | the dict of all annotations | `{"messages": Annotated[…], "step": int}` |
| `["messages"]` | one entry | `Annotated[list[str], operator.add]` |
| `.__metadata__` | the extras tuple | `(operator.add,)` |

A merge that consults it pulls the function out of that tuple and calls it with the old and new values; a key whose annotation has no `__metadata__` falls through to plain assignment. That function is a **reducer** — the name for anything that takes the old value and the new one and returns what should be stored.

You write the annotation. The framework writes the reader.

## What this concept claims

**`Annotated[X, …]` is `X` with a payload attached — invisible to type checkers, available to any runtime library that asks for it.**

Four things to carry:

1. It exists because plenty of real requirements are not types. "At least 1" can't be a type; `Literal` can only enumerate, `NewType` has no slot for it, and an annotation is an evaluated expression so `int > 0` is a `TypeError`, not a constraint.
2. The alternative — keeping rules in a structure alongside — fails on two counts: it **drifts** when names change, and it **doesn't travel** with the object the way an annotation does.
3. Type checkers see straight through it. `Annotated[int, Ge(1)]` reveals as `int`, so wrong *types* are still caught and violated *constraints* are not. `get_type_hints` strips the extras by default and returns them only for `include_extras=True`, which is why adding `Annotated` breaks nothing that already reads annotations.
4. The extras are arbitrary objects, and nothing reads them unless someone wrote code to. A validating library recognises the constraint objects it defined itself; a graph runtime pulls a reducer function out of the same tuple. Same mechanism, different payload.
