#python #type-hints #typing #traps #mutable-defaults #python-utils


`21-Deferred-Evaluation` established one fact that turns out to explain the worst trap in this note: **a `def` is a statement Python executes**, and executing it evaluates the annotations right there, once.

It evaluates the **defaults** at the same moment. That is the whole of the first trap.

## Mutable defaults

Two independent calls to a tool runner. Each starts a fresh log — or so it reads:

```python
 4  async def run_tool(name: str, log: list[str] = []) -> list[str]:
 5      log.append(f"ran {name}")
 6      return log
 7
 8
 9  async def main() -> None:
10      first = await run_tool("search")
11      print("first call :", first)
12
13      second = await run_tool("summarise")
14      print("second call:", second)
```

```
$ mypy tr0.py
Success: no issues found in 1 source file
```

Fully typed and fully accepted — the annotation `list[str]` is correct, it **is** a list of strings.

```
$ python3 tr0.py
first call : ['ran search']
second call: ['ran search', 'ran summarise']
```

The second call inherits the first call's work. And asking the function what its default **is**, after both calls, makes the reason plain:

```
stored default : (['ran search', 'ran summarise'],)
```

**The default value is the polluted list.** There was never a second list.

### Why: a default is built once, at definition

The same demonstration as concept 21's annotation experiment — make the default a function call so it can be watched:

```python
 1  def make_list():
 2      print("   >>> building the default list NOW")
 3      return []
 4
 5
 6  print("1. about to define the function")
 7
 8
 9  def run_tool(name, log=make_list()):
10      log.append(name)
11      return log
12
13
14  print("2. function defined")
15
16  print("3. first call :", run_tool("search"))
17  print("4. second call:", run_tool("summarise"))
```

```
1. about to define the function
   >>> building the default list NOW
2. function defined
3. first call : ['search']
4. second call: ['search', 'summarise']
```

The `>>>` line lands **between 1 and 2** — before either call — and appears **once**.

So `make_list()` ran when Python executed the `def` statement on line 9, not when the function was called. One list was built at definition time, and lines 16 and 17 were both handed that same one.

> [!important] `log: list[str] = []` reads like an instruction — **when nobody passes a log, make an empty one**. It is not. It is a **value computed once** and stored on the function object for the lifetime of the program.

In agent code this is the bug that eats an afternoon. A default `messages: list[Message] = []` on a conversation handler means every conversation the service has ever handled accumulates in one list, and turn 400 arrives carrying 399 strangers' messages.

### The fix

```python
async def run_tool(name: str, log: list[str] | None = None) -> list[str]:
    if log is None:
        log = []
    log.append(f"ran {name}")
    return log
```

`None` is immutable, so sharing it is harmless. The `[]` now sits in the function **body**, which runs per call, so every caller gets a genuinely new list.

> [!tip] **Vocabulary, since the trap turns on it.** A **default** is the value a parameter takes when the caller passes nothing:
>
> ```python
> 1  def greet(name: str = **world**) -> str:
> 2      return f**hello {name}**
> 5  print(greet())          → hello world
> 6  print(greet(**laxy**))    → hello laxy
> ```
>
> `= "world"` is the default. Line 5 passes nothing and gets it; line 6 passes something and doesn't.

## `= None` and the two meanings of optional

The fix above changed the annotation from `list[str]` to `list[str] | None`, which is where `07-Unions-And-Optionality` warned people get confused. The confusion has a specific shape:

```python
1  def run_tool(name: str, log: list[str] = None) -> list[str]:
2      log.append(name)
3      return log
```

This is not **a list of strings that is `None`** — that phrase describes nothing. It says **this is a list of strings** and then supplies a default of `None`, which is not a list of strings. The annotation and the default contradict each other, and all three tools say so:

```
$ mypy tr3.py
tr3.py:1: error: Incompatible default for parameter "log" (default has type "None", parameter has type "list[str]")  [assignment]
tr3.py:1: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
```

```
$ pyright tr3.py
tr3.py:1:42 - error: Expression of type "None" cannot be assigned to parameter of type "list[str]"
```

```
$ python3 tr3.py
AttributeError: 'NoneType' object has no attribute 'append'
```

### Implicit `Optional`, and why it was removed

That mypy **note** is history worth knowing. Older mypy silently rewrote `log: list[str] = None` into `log: list[str] | None = None` for you, assuming a `None` default meant you wanted `None` permitted. It was called **implicit `Optional`**, and it was removed because it made the signature lie: the annotation said **list of strings** while the checker quietly allowed `None`, so every caller reading the signature got the wrong contract.

You will still meet it in old code and old tutorials. It is no longer the default in any current checker.

### The four spellings

| | means | optional to **pass**? | may be `None`? |
|---|---|---|---|
| `log: list[str]` | must be a list | **no** — required | no |
| `log: list[str] = []` | must be a list | yes | no — but **shared across calls** |
| `log: list[str] \| None = None` | list or `None` | yes | yes |
| `log: list[str] = None` | contradiction | — | — |

> [!important] The word **optional does two unrelated jobs** in Python, which is the whole source of the confusion:
>
> - **optional to pass** — the parameter has a default. Controlled by `=`. Nothing to do with types.
> - **may be `None`** — controlled by `| None` in the annotation.
>
> `= None` is the one spelling where both happen at once, which is why they get fused. But `name: str = "world"` is optional to pass and can never be `None`, and `log: list[str] | None` with no default can be `None` and is required.

## Annotating `self`

The trap here is small; the one standing behind it is not. Both need one piece of machinery first.

### Aside — `type(x)` and how to read what it prints

```python
 1  class Agent:
 2      pass
 3
 4
 5  class SearchAgent(Agent):
 6      pass
 7
 8
 9  a = Agent()
10  s = SearchAgent()
```

```
a is       : <__main__.Agent object at 0x102429d30>
type(a) is : <class '__main__.Agent'>

s is       : <__main__.SearchAgent object at 0x102429fd0>
type(s) is : <class '__main__.SearchAgent'>
```

Two different things on each pair:

- `a` is an **object** — a thing that was made.
- `type(a)` is the **class** — the recipe it was made from.

And `type(s)` reports `SearchAgent`, not `Agent`. It gives what the object **actually is**, not what it inherits from.

The `__main__` in there is a **module name**. The same file, run two ways:

```
=== run it directly ===
__name__ in this file is: __main__
the class : <class '__main__.Agent'>
an object : <__main__.Agent object at 0x1031add30>

=== import it from somewhere else ===
__name__ in this file is: ty1
the class : <class 'ty1.Agent'>
an object : <ty1.Agent object at 0x100bc1d30>
```

`__main__` became `ty1`. It is simply the module the class lives in — `__main__` being the special name Python gives the file you launched, while any other file gets its own filename.

| part | means |
|---|---|
| `class` / `object` | which of the two this is — the recipe, or a thing made from it |
| `__main__` | the module it lives in |
| `Agent` | the class name |
| `at 0x1031add30` | where in memory this particular object sits |

The address appears only on objects, and it is what distinguishes two of them: three `Agent()` calls give three addresses and one class.

> [!tip] This is worth the detour because **mypy prints the same `module.Class` form everywhere** — `tr4.Agent`, `fw2.Agent`, `nr3.ToolMessage`. Every `Revealed type is "..."` in this folder is read the same way.

Which makes `type(self)(self.name)` readable: **`type(self)` is the class this object actually is, and calling a class makes a new instance of it.** So the expression means **make a new one of whatever class I am, passing my name** — as opposed to `Agent(self.name)`, which would always make an `Agent` regardless.

### The small trap: `self` is already known

```python
 1  class Agent:
 2      def __init__(self, name: str) -> None:
 3          self.name = name
 4
 5      def clone(self) -> "Agent":
 6          reveal_type(self)
 7          return type(self)(self.name)
```

```
tr4.py:6: note: Revealed type is "tr4.Agent"
```

`self` carries no annotation and mypy knows it is an `Agent` regardless — inferred from the class the method is written in. Writing `self: Agent` adds a line of noise that can only ever agree with what the checker already worked out. The same goes for `cls`.

### The real trap: the return type behind it

```python
 1  class Agent:
 2      def __init__(self, name: str) -> None:
 3          self.name = name
 4
 5      def clone(self) -> "Agent":
 6          return type(self)(self.name)
 7
 8
 9  class SearchAgent(Agent):
10      async def search(self, q: str) -> str:
11          return f"{self.name} searching {q}"
12
13
14  copy = SearchAgent("s").clone()
15  print("runtime class:", type(copy))
16  copy.search("x")
```

```
$ mypy tr5.py
tr5.py:16: error: "Agent" has no attribute "search"  [attr-defined]
```

```
$ python3 tr5.py
runtime class: <class '__main__.SearchAgent'>
```

The `reveal_type` from the previous file is gone, so `clone()` is two lines here. The object **is** a `SearchAgent` — line 6 is `type(self)(...)`, so `clone()` constructs whatever class it was called on. It genuinely has `.search`. mypy refuses the call anyway, because `-> "Agent"` promised less than the method delivers.

> [!important] `self` needs no annotation, but a **return type of the class name is a real bug**. It hard-codes the class where the method was **written**, not the class it was **called on**, so every subclass silently degrades to the base type the moment it passes through such a method.

Fixing that properly is its own rung — `19-Self`, which exists for exactly this.

### Why mypy can infer `self` at all

A natural worry is that `self` might be `None` until the object exists. It never is:

```python
1  class Agent:
2      def who(self):
3          print("   inside the method, self is:", self)
4
5
6  a = Agent()
7  print("the object a is           :", a)
8  a.who()
```

```
the object a is           : <__main__.Agent object at 0x10426dd30>
   inside the method, self is: <__main__.Agent object at 0x10426dd30>
```

**Same address both times.** `self` is not a placeholder that gets filled in later — it **is** `a`. Writing `a.who()` passes `a` in as the first argument, and `self` is simply the name that argument has inside the method.

Nor can it be dodged:

```python
13  Agent.who()
```

```
TypeError: Agent.who() missing 1 required positional argument: 'self'
```

Called on the class rather than an object there is nothing to pass, and Python says so in exactly those terms. It is an ordinary parameter with an ordinary name.

So `self` is never `None`, because a method cannot run without an object to run on — before instantiation the method is simply not executing. Which is precisely why the checker can infer it: inside `class Agent`, `self` can only ever be an `Agent`.

## Over-annotating

```python
1  name = "search"
2  count = 0
3  timeout = 1.5
4  results = []
```

```
tr6.py:4: error: Need type annotation for "results" (hint: "results: list[<type>] = ...")  [var-annotated]
tr6.py:6: note: Revealed type is "str"
tr6.py:7: note: Revealed type is "int"
tr6.py:8: note: Revealed type is "float"
tr6.py:9: note: Revealed type is "list[Any]"
```

Lines 1-3 need nothing. mypy reads the value and knows. Annotating them — `name: str = "search"` — adds a line that can only ever restate what the checker already worked out.

Line 4 is the opposite, and mypy asks for help by name: **`Need type annotation for "results"`**. `[]` is a list of **what**? There is no value to read the answer off, so without you it degrades to `list[Any]` — and concept 8's rule then applies to everything that comes out of it.

> [!important] The rule is a question: **would the checker have got there on its own?**
>
> | | |
> |---|---|
> | `name: str = "search"` | noise — the value says `str` |
> | `results: list[str] = []` | necessary — `[]` says nothing about its contents |
> | `cache: dict[str, int] = {}` | necessary — same reason |
> | `config: Config \| None = None` | necessary — `None` alone tells you nothing |
>
> Annotating the first kind is not merely harmless. It trains readers to skim annotations, which costs you on the lines where they carry real information.

## Believing a hint is a guarantee

The last trap is the one this whole folder has been quietly proving, rung after rung. It is concept 1's claim, and by now the evidence is overwhelming:

| rung | the demonstration |
|---|---|
| `01` | annotations are inert data; nothing reads them unless a library chooses to |
| `11` | a `TypedDict` never validates — hand it the wrong types and it stores them |
| `18` | `TypeIs` with a body of `return True` earns a clean `Success`, then `AttributeError` |
| `21` | an annotation can be the string `'Agent'` and the function still returns a real one |
| `22` | a `.pyi` can flatly contradict the source it describes; the checker believes the stub |
| `23` | `cast` is `return val` — an assertion with no check anywhere behind it |
| `25` | a `@dataclass` annotated `float` will hold `"0.9"` all day |

> [!warning] A type hint is a **claim about intent**, checked by a separate program that you have to actually run. It is never a runtime guarantee, and every escape hatch in the language exists because sometimes the claim is wrong on purpose.
>
> Which is why `25`'s conclusion holds: at a **trust boundary**, annotations are not enough. Something has to validate.

## What this concept claims

**Most typing traps are not typing bugs — they are Python's execution model showing through the annotations.**

Five things to carry:

1. A `def` is executed, and executing it evaluates the **defaults** as well as the annotations — once, at definition. So `log: list[str] = []` builds one list that every call then shares. In agent code this is a message list accumulating across every conversation the service has handled. Use `| None = None` and build the real value in the body.
2. `list[str] = None` is a contradiction, and all three of mypy, pyright and the runtime reject it. Old mypy used to silently rewrite it to `list[str] | None` — **implicit `Optional`**, removed because it made signatures lie to their callers.
3. **Optional means two unrelated things.** Optional to **pass** is the `=`; may be `None` is the `| None`. They coincide only in the `= None` spelling, which is why they get fused in people's heads.
4. `self` needs no annotation — it is an ordinary first parameter holding the very object the method was called on, so the checker infers it. But a **return type of the class name** is a genuine bug: it hard-codes where the method was written rather than what it was called on, and every subclass degrades to the base type. `19-Self` is the fix.
5. Annotate where the checker cannot infer — empty containers, `None` defaults — and nowhere else. Over-annotating trains readers to skim, which costs you exactly where it matters.
