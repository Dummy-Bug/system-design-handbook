#python #type-hints #typing #forward-references #type-checking #python-utils


`20-Annotated` established something small that turns out to have large consequences: **an annotation is an ordinary Python expression, and Python evaluates it.** That was why `x: int > 0` failed with a `TypeError` rather than being quietly ignored — the `>` really ran.

An expression can only name things that already exist. This concept is what happens when the thing you need to name doesn't exist yet.

## A class that cannot mention itself

Completely ordinary code — a class that makes another of itself:

```python
1  class Agent:
2      def __init__(self, name: str) -> None:
3          self.name = name
4
5      async def spawn_child(self) -> Agent:
6          return Agent(f"{self.name}-child")
7
8
9  print("module loaded")
```

```
$ mypy fw0.py
Success: no issues found in 1 source file
```

```
$ python3 fw0.py
  File "fw0.py", line 5, in Agent
    async def spawn_child(self) -> Agent:
                                   ^^^^^
NameError: name 'Agent' is not defined
```

Two things stand out.

**The direction is reversed.** Everywhere else in this folder, mypy complains about code Python runs happily. Here mypy is content and Python refuses. The checker reads the source as text and has no trouble seeing that `Agent` is the class being defined; the interpreter has to actually *have* it.

**And line 9 never ran.** This is not a bug that surfaces when the method is called — the module will not import.

## A `class` statement is executed, not declared

The reason is easier to see with the types removed entirely:

```python
 1  print("1. before the class statement")
 2
 3
 4  class Agent:
 5      print("2. now running INSIDE the class body")
 6      try:
 7          Agent
 8          print("3. ...and 'Agent' already exists")
 9      except NameError:
10          print("3. ...but 'Agent' does NOT exist yet")
11
12      print("4. class body finished")
13
14
15  print("5. after the class statement, Agent =", Agent)
```

```
$ python3 fw1.py
1. before the class statement
2. now running INSIDE the class body
3. ...but 'Agent' does NOT exist yet
4. class body finished
5. after the class statement, Agent = <class '__main__.Agent'>
```

Those `print` calls sit inside a class body and they **ran**. A `class` statement is not a declaration the way it is in Java — Python *executes* the body, top to bottom, like any other block.

The order is the entire answer:

1. Python begins executing the class body
2. every line in it runs — line 7 among them
3. the body finishes
4. **only now** is the name `Agent` created and pointed at the finished class

Line 7 happens at step 2. The name does not exist until step 4.

> [!important] `async def spawn_child(self) -> Agent:` is a line **in the class body**, so it runs at step 2. The method is being *defined*, not called — and building the function object means evaluating its annotations right there, which sends Python looking for a name that is still two steps from existing.
>
> Nothing about this is special to classes referring to themselves. It is the general rule: **an annotation is evaluated where it is written, so it can only name what exists at that moment.**

## The fix is quotation marks

```python
 4  class Agent:
 5      def __init__(self, name: str) -> None:
 6          self.name = name
 7
 8      async def spawn_child(self) -> "Agent":
 9          return Agent(f"{self.name}-child")
```

```
$ mypy fw2.py
fw2.py:15: note: Revealed type is "fw2.Agent"
Success: no issues found in 1 source file
```

```
$ python3 fw2.py
child name: root-child
annotation stored as: {'return': 'Agent'}
```

Both sides satisfied, and mypy resolved it to the real class — line 15 reveals `fw2.Agent`, so `kid.name` is fully checked.

The reason is almost too simple:

| written as | Python evaluates | result |
|---|---|---|
| `-> Agent` | a **name lookup** for `Agent` | `NameError` — not bound yet |
| `-> "Agent"` | a **string literal** | the string `"Agent"`, always fine |

A string requires nothing to exist. Python evaluates it, gets a string, stores it — visible in the output as `{'return': 'Agent'}`, the annotation kept verbatim as text.

mypy, which reads the file as text and never runs it, sees the string and looks `Agent` up **in the whole file**, where it plainly exists. It has no ordering problem because it is not executing anything.

> [!important] This is the pattern for the entire concept: **the checker needs a name it can resolve; the interpreter needs an expression it can evaluate.** A quoted annotation gives each of them exactly what it needs.

Line 9 — `return Agent(...)`, unquoted — is fine, because it runs when the method is *called*, long after step 4. Only the annotation was early.

And quoting is safe for a reason established all the way back in concept 1: **annotations are never enforced**, so the runtime *value* of one is irrelevant to behaviour. Degrading it to a string costs nothing. The function returns a real `Agent` regardless of what its annotation says.

## Turning it off for the whole file

Quoting every self-reference by hand is tedious and easy to forget. One line at the top removes the need:

```python
 1  from __future__ import annotations
 2
 3  import asyncio
 4
 5
 6  class Agent:
 7      def __init__(self, name: str) -> None:
 8          self.name = name
 9
10      async def spawn_child(self) -> Agent:
11          return Agent(f"{self.name}-child")
```

```
$ mypy fw3.py
Success: no issues found in 1 source file
```

```
$ python3 fw3.py
child name: root-child
spawn_child: {'return': 'Agent'}
__init__   : {'name': 'str', 'return': 'None'}
```

**Line 10 has no quotes and it works.**

The last two output lines say why. `'Agent'`, `'str'`, `'None'` — every one a string, none of them quoted in the source. That import tells Python: *do not evaluate annotations in this file; keep the source text.* It is the quoting trick applied automatically to everything, including annotations that never needed it.

| | what Python stores | needs the name to exist? |
|---|---|---|
| `-> Agent` | the class object | **yes** |
| `-> "Agent"` | `'Agent'` | no |
| `from __future__ import annotations` | `'Agent'`, and every other annotation too | no |

Quoting is surgical; the import is blanket. In a file where several classes reference each other, the blanket version is what you want — ordering stops being something you think about.

### What "evaluate" actually means

Worth making concrete, because the whole concept turns on it. **Evaluate = run the expression and produce a value.** Here the annotation is a function call, so it can be watched:

```python
 1  def make_type():
 2      print("   >>> the annotation is running RIGHT NOW")
 3      return int
 4
 5
 6  print("1. about to define the function")
 7
 8
 9  def handle(x: make_type()) -> None:
10      print("   inside handle")
11
12
13  print("2. function defined (not called yet)")
14  print("3. stored annotation:", handle.__annotations__)
```

**Without the future import:**

```
1. about to define the function
   >>> the annotation is running RIGHT NOW
2. function defined (not called yet)
3. stored annotation: {'x': <class 'int'>, 'return': None}
```

**With it:**

```
1. about to define the function
2. function defined (not called yet)
3. stored annotation: {'x': 'make_type()', 'return': 'None'}
```

- **Evaluated** — Python *ran* `make_type()`. The print fired. What is stored is `<class 'int'>`, the **result**.
- **Not evaluated** — the print never fired. What is stored is `'make_type()'`, the **source text**, characters and all.

Note the timing in the first run: the print lands between "1" and "2", *before* `handle` is ever called. Defining a function evaluates its annotations immediately — the same step-2 problem the `Agent` class had, in a plain function.

## What the future import costs

It is not switched on by default, and the reason is `20-Annotated`'s whole premise: **some libraries read annotations at runtime.** Pydantic builds validators by looking at yours.

Under `from __future__ import annotations` those annotations are strings. Pydantic needs the actual class object; it cannot build a validator out of six characters of text. So it has to turn `'Agent'` back into `Agent` — find what that name meant *in the module where it was written*. That is what `typing.get_type_hints()` does, and why it needs the function's globals: it re-evaluates the string, later, in the right place.

Which leaves both designs flawed:

| | problem |
|---|---|
| evaluate immediately (default) | cannot name anything not yet defined |
| never evaluate (`from __future__`) | runtime libraries receive strings and must re-resolve them |

> [!info] **Python 3.14 reworks this** (PEP 649/749) with lazy evaluation — annotations are computed on demand rather than eagerly or never, which is meant to give both sides what they want. Not verified here; check the current behaviour before relying on it.

## Circular imports — the case you actually hit

A self-referencing class is the textbook example. The one that shows up in real agent code is two modules needing each other's types: a tool reads the state, the state records which tool ran.

**`state.py`**

```python
1  from tools import Tool
2
3
4  class AgentState:
5      def __init__(self) -> None:
6          self.history: list[str] = []
7
8      def record(self, tool: Tool) -> None:
9          self.history.append(tool.name)
```

**`tools.py`**

```python
 1  from state import AgentState
 2
 3
 4  class Tool:
 5      def __init__(self, name: str) -> None:
 6          self.name = name
 7
 8      async def run(self, state: AgentState) -> str:
 9          state.record(self)
10         return f"{self.name} ran"
```

```
$ mypy main.py
Success: no issues found in 1 source file
```

```
$ python3 main.py
  File "state.py", line 1, in <module>
    from tools import Tool
  File "tools.py", line 1, in <module>
    from state import AgentState
ImportError: cannot import name 'AgentState' from 'state'
```

Same reversal — mypy content, Python dead — and the same *kind* of cause, timing:

1. `main.py` starts importing `state`
2. `state.py` line 1 → go and import `tools`
3. `tools.py` line 1 → go and import `state`, which is **already in progress** and has not got past its own line 1
4. `AgentState` does not exist yet → `ImportError`

Whichever module is imported first loses. Swapping the order only moves the crash.

### The future import alone does not fix it

The natural first attempt, since the annotations are what need the other module. Added to both files, nothing else changed:

```
$ python3 main.py
  File "tools.py", line 3, in <module>
    from state import AgentState
ImportError: cannot import name 'AgentState' from 'state'
```

Still dead — and note **which line**. Line 3, the `import` statement itself, not an annotation.

That is the gap. The future import changed what happens to the *annotations*, but `from state import AgentState` is a plain statement that runs regardless, and it is the thing that deadlocks. The annotations were made not to need `AgentState`, and then it was imported anyway.

There are two separate problems here:

| problem | fix |
|---|---|
| the annotation needs a name that isn't importable | the future import, or quotes |
| the import statement itself deadlocks | `if TYPE_CHECKING:` |

Neither fix addresses the other's problem.

### `TYPE_CHECKING` — one name, two truths

Look at *why* each import is there. `state.py` imports `Tool` only to write `tool: Tool`; `tools.py` imports `AgentState` only to write `state: AgentState`. Neither module ever calls the other's code — `record()` uses `tool.name`, `run()` uses `state.record()`, both reached through arguments handed in at runtime.

So the requirement is precise: **the import must run for mypy and not run for Python.**

```python
 1  from __future__ import annotations
 2
 3  from typing import TYPE_CHECKING
 4
 5  if TYPE_CHECKING:
 6      from tools import Tool
 7
 8
 9  class AgentState:
...
13      def record(self, tool: Tool) -> None:
```

```
$ mypy main.py
Success: no issues found in 1 source file
```

```
$ python3 main.py
search ran
['search']
```

Both sides, and the mechanism has no magic in it whatsoever:

```
$ python3 -c "from typing import TYPE_CHECKING; print(TYPE_CHECKING)"
False
```

**`TYPE_CHECKING` is an ordinary constant, and at runtime it is `False`.** Line 6 sits inside `if False:`, so Python skips it, never imports `tools`, and never deadlocks. Type checkers hard-code the opposite: mypy treats it as `True`, walks into the block, and picks the import up.

| | `TYPE_CHECKING` is | line 6 |
|---|---|---|
| mypy | `True` | imported — `Tool` resolves |
| Python | `False` | skipped — no circular import |

> [!important] **Both halves are load-bearing.**
>
> Remove `if TYPE_CHECKING:` and Python deadlocks on the import. Remove line 1 and Python crashes on the *annotation* instead — `Tool` was never imported, so evaluating `tool: Tool` finds nothing.
>
> `TYPE_CHECKING` removes the import; the future import (or quotes) makes the annotation survive its absence. Neither works alone.

## What this concept claims

**An annotation is an expression Python evaluates where it is written, so it can only name what already exists — and the fixes all work by making the checker and the interpreter read the same line differently.**

Five things to carry:

1. A `class` statement is **executed**, not declared. Its body runs top to bottom, and the class name is bound only after the body finishes — which is why a method annotated `-> Agent` inside `class Agent` raises `NameError` at import time, before anything is ever called.
2. The failure direction is the reverse of everything else in this folder: **mypy passes, Python crashes.** The checker reads the file as text and has no ordering problem; the interpreter has to actually possess the object.
3. Quoting an annotation replaces a name lookup with a string literal, which needs nothing to exist. `from __future__ import annotations` applies that to every annotation in the file. Both are safe because annotations are never enforced (concept 1), so the stored *value* of one has no effect on behaviour.
4. The cost of the future import is that runtime readers — Pydantic, anything built on `20-Annotated` — receive strings and must re-resolve them with `typing.get_type_hints()`, which needs the defining module's globals. Both designs are flawed; 3.14's PEP 649/749 lazy evaluation is the attempt to have both.
5. Circular imports are two problems wearing one error message. `if TYPE_CHECKING:` stops the import running at runtime — it is a plain constant that is `False` in Python and hard-coded `True` in checkers — and the future import or quotes keep the annotation valid once the name is gone. Applying only one of the two leaves you with a crash on the other line.
