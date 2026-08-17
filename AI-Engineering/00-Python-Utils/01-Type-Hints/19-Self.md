#python #type-hints #typing #self #inheritance #python-utils


A method that builds a new object of its own class has to declare a return type, and the obvious choice is the name of the class it is written in. That choice is a bug: it hard-codes where the method was **written** rather than what it was **called on**, so every subclass silently degrades to the base type. The fix is a single word.

There is exactly one idea here:

```python
def clone(self) -> "Agent":     # always says Agent, whoever called it
def clone(self) -> Self:        # says whatever class actually called it
```

Everything below is that idea in two settings.

## The bug, restated

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
14  original = SearchAgent("finder")
15  copy = original.clone()
16
17  print("runtime class:", type(copy))
18  reveal_type(copy)
19  copy.search("why is the sky blue")
```

```
$ mypy sf0.py
sf0.py:18: note: Revealed type is "sf0.Agent"
sf0.py:19: error: "Agent" has no attribute "search"  [attr-defined]
```

```
$ python3 sf0.py
runtime class: <class '__main__.SearchAgent'>
```

Line 17 says the object **is** a `SearchAgent`. Line 18 says mypy believes it is an `Agent`. Line 19 is refused on a method the object genuinely has.

The cause is line 5. `-> "Agent"` names the class where the method was **written**, while line 6 — `type(self)(...)` — builds whatever class it was **called on**. The annotation cannot describe what the code does.

## The obvious fix, and where it runs out

Override `clone()` in the subclass and re-annotate it:

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
10      def clone(self) -> "SearchAgent":
11          return type(self)(self.name)
12
13      async def search(self, q: str) -> str:
14          return f"{self.name} searching {q}"
15
16
17  class CachedSearchAgent(SearchAgent):
18      async def cache_stats(self) -> int:
19          return 0
20
21
22  copy = SearchAgent("finder").clone()
23  reveal_type(copy)
24  copy.search("q")
25
26  deep = CachedSearchAgent("finder").clone()
27  reveal_type(deep)
28  deep.cache_stats()
```

```
$ mypy sf1.py
sf1.py:27: note: Revealed type is "sf1.SearchAgent"
sf1.py:28: error: "SearchAgent" has no attribute "cache_stats"  [attr-defined]
```

Lines 10-11 fix the first level — line 24 no longer errors.

**But line 27 is `SearchAgent` and line 28 fails.** `CachedSearchAgent` inherited `clone()` from `SearchAgent`, which promises a `SearchAgent`. The bug returned one level down.

And note what the fix cost even where it worked: lines 10-11 **duplicate the body** of lines 5-6 verbatim, every subclass needs its own copy forever, and the day somebody adds a fourth class and forgets, it silently degrades again.

The problem is structural. The thing being written down is a class name, and the class name is precisely what changes per subclass — so each override only moves the hard-coded name one level further down.

> [!info] That override is nonetheless **legal**, and `15-Variance` says why: an override may return a **narrower** type than the method it replaces, because return positions are covariant. `Self` does not introduce a new permission — it applies that existing one automatically.
>
> Worth being precise about a related claim: this is **not** a Liskov violation. A `SearchAgent` is usable everywhere an `Agent` is wanted; nothing about substitution breaks. The annotation simply discards information the code already has.

## Setting one: `Self`

```python
 1  from typing import Self
 2
 3
 4  class Agent:
 5      def __init__(self, name: str) -> None:
 6          self.name = name
 7
 8      def clone(self) -> Self:
 9          return type(self)(self.name)
10
11
12  class SearchAgent(Agent):
13      async def search(self, q: str) -> str:
14          return f"{self.name} searching {q}"
15
16
17  class CachedSearchAgent(SearchAgent):
18      async def cache_stats(self) -> int:
19          return 0
20
21
22  base = Agent("plain").clone()
23  reveal_type(base)
24
25  copy = SearchAgent("finder").clone()
26  reveal_type(copy)
27
28  deep = CachedSearchAgent("finder").clone()
29  reveal_type(deep)
```

```
$ mypy sf2.py
sf2.py:23: note: Revealed type is "sf2.Agent"
sf2.py:26: note: Revealed type is "sf2.SearchAgent"
sf2.py:29: note: Revealed type is "sf2.CachedSearchAgent"
Success: no issues found in 1 source file
```

```
$ python3 sf2.py
<class '__main__.Agent'>
<class '__main__.SearchAgent'>
<class '__main__.CachedSearchAgent'>
```

Three things, and only three:

- **`clone()` appears once**, on line 8, in the base class. `SearchAgent` and `CachedSearchAgent` never mention it — where `sf1.py` needed it rewritten in each.
- **Each call site gets a different type**: line 23 `Agent`, line 26 `SearchAgent`, line 29 `CachedSearchAgent`, all from that one method.
- **Line 29 is the case that was broken before**, and it works with nobody having written anything for it.

The two outputs also match exactly — mypy's three classes on the left, Python's on the right.

> [!important] `Self` is the check-time twin of the `type(self)` sitting one line below it, on line 9:
>
> | | means |
> |---|---|
> | `type(self)` | at **runtime** — the class this object actually is |
> | `Self` | at **check time** — the class this method was called on |
>
> The same idea in the two halves of the language, which is why lines 8 and 9 finally agree. Before `Self` existed, the annotation could only name a fixed class while the body was always dynamic — it was structurally incapable of describing the code.

## Setting two: method chaining

The version that shows up in library code — methods returning the object so calls can be strung together.

```python
 1  class Prompt:
 2      def __init__(self) -> None:
 3          self.parts: list[str] = []
 4
 5      def system(self, text: str) -> "Prompt":
 6          self.parts.append(f"[system] {text}")
 7          return self
 8
 9      def user(self, text: str) -> "Prompt":
10          self.parts.append(f"[user] {text}")
11          return self
12
13
14  class ToolPrompt(Prompt):
15      def tools(self, names: list[str]) -> "ToolPrompt":
16          self.parts.append(f"[tools] {names}")
17          return self
18
19
20  p = ToolPrompt().system("be brief").tools(["search"])
21  reveal_type(p)
```

```
$ mypy sf3.py
sf3.py:20: error: "Prompt" has no attribute "tools"  [attr-defined]
sf3.py:21: note: Revealed type is "Any"
```

Line 20 is the whole story, read left to right:

- `ToolPrompt()` → a `ToolPrompt`
- `.system("be brief")` → line 5 says this returns a **`Prompt`**
- `.tools([...])` → refused, because `Prompt` has no `tools`

The chain is **downgraded halfway through**. And line 7 is `return self` — the exact same object, which really is a `ToolPrompt`. The annotation on line 5 is lying about it.

This is worse than `clone()` because the damage compounds: one base-class method anywhere in the chain flattens everything after it, and the subclass's own methods become unreachable regardless of where they sit. Line 21 revealing `Any` is mypy giving up entirely after the error.

Swapping the three annotations:

```python
 1  from typing import Self
 2
 3
 4  class Prompt:
 5      def __init__(self) -> None:
 6          self.parts: list[str] = []
 7
 8      def system(self, text: str) -> Self:
 9          self.parts.append(f"[system] {text}")
10          return self
11
12      def user(self, text: str) -> Self:
13          self.parts.append(f"[user] {text}")
14          return self
15
16
17  class ToolPrompt(Prompt):
18      def tools(self, names: list[str]) -> Self:
19          self.parts.append(f"[tools] {names}")
20          return self
21
22
23  p = ToolPrompt().system("be brief").tools(["search"]).user("why is the sky blue")
24  reveal_type(p)
25  print(p.parts)
```

```
$ mypy sf4.py
sf4.py:24: note: Revealed type is "sf4.ToolPrompt"
Success: no issues found in 1 source file
```

```
$ python3 sf4.py
['[system] be brief', "[tools] ['search']", '[user] why is the sky blue']
```

Line 23 crosses back and forth — `.system()` from the base class, `.tools()` from the subclass, `.user()` from the base again — and remains a `ToolPrompt` throughout.

## What this concept claims

**`Self` names the class a method was called on, rather than the class it was written in — which is the only way an annotation can describe a body that uses `type(self)` or `return self`.**

Four things to carry:

1. Annotating a method with its **own class name** hard-codes where the method was written. Any subclass then degrades to the base type the moment a value passes through that method, and its own attributes become unreachable on an object that genuinely has them.
2. Overriding the method in each subclass works and is legal — `15-Variance` permits an override to return a **narrower** type — but it duplicates the body, must be repeated in every subclass forever, and breaks again at the next level down, because each override merely relocates the hard-coded name.
3. `Self` is the check-time counterpart of `type(self)`. One is what the object **is** at runtime; the other is what the checker calls it. With both in agreement, one method in the base class serves every depth of subclass.
4. It matters most where values flow back out of methods — alternative constructors, `clone`-style copies, and fluent chains. In a chain the damage compounds: a single base-class method annotated with the base class name flattens everything downstream of it.

> [!info] Not covered here, and worth picking up when it comes up: `Self` is also valid in a `@classmethod` (`def from_file(cls, path: str) -> Self`), where there is no `self` at all — it then means **the class the method was called on**, which is what makes alternative constructors inherit correctly.
