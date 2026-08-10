#python #type-hints #typing #protocol #structural-typing #python-utils

## A helper for three unrelated classes

Reranking: given a list of things with scores, return the highest one.

```python
 1  class Candidate:
 2      def __init__(self, text: str, score: float) -> None:
 3          self.text = text
 4          self.score = score
 5
 6
 7  class ToolCall:
 8      def __init__(self, name: str, score: float) -> None:
 9          self.name = name
10          self.score = score
11
12
13  class RetrievedDoc:
14      def __init__(self, url: str, score: float) -> None:
15          self.url = url
16          self.score = score
17
18
19  def best[T: (Candidate, ToolCall)](items: list[T]) -> T:
20      return max(items, key=lambda c: c.score)
21
22
23  c = best([Candidate("a", 0.9), Candidate("b", 0.4)])
24  d = best([RetrievedDoc("u1", 0.9), RetrievedDoc("u2", 0.4)])
```

None of the three inherits from anything. They were written by different people at different times and have exactly one thing in common: an attribute called `score`.

`RetrievedDoc` is newer than `best`.

```
$ mypy p0.py

p0.py:24: error: Value of type variable "T" of "best" cannot be "RetrievedDoc"  [type-var]
```

Line 24 is rejected, and the rejection is *correct by the rules* — a tuple of constraints means "exactly one of these", and `RetrievedDoc` isn't one of them. Having a `.score` doesn't qualify it.

It's also useless. Run that line and it works fine; `max` reads `.score` and never asks what class the object is. The annotation is refusing something the program does correctly.

## Neither escape hatch fits

There are two standard ways out, and both cost something.

**Give them a common base class.**

```python
 1  class Scored:
 2      score: float
 3
 4
 5  class Candidate(Scored):
 6      def __init__(self, text: str, score: float) -> None:
 7          self.text = text
 8          self.score = score
 9
10
11  class ToolCall(Scored):
12      def __init__(self, name: str, score: float) -> None:
13          self.name = name
14          self.score = score
15
16
17  class RetrievedDoc:
18      def __init__(self, url: str, score: float) -> None:
19          self.url = url
20          self.score = score
21
22
23  def best[T: Scored](items: list[T]) -> T:
24      return max(items, key=lambda c: c.score)
25
26
27  c = best([Candidate("a", 0.9), Candidate("b", 0.4)])
28  d = best([RetrievedDoc("u1", 0.9), RetrievedDoc("u2", 0.4)])
```

```
$ mypy p1.py

p1.py:28: error: Value of type variable "T" of "best" cannot be "RetrievedDoc"  [type-var]
```

The bound is open-ended now — any future subclass of `Scored` qualifies without touching `best`. That fixes the *closed list* problem and does nothing for `RetrievedDoc`, because qualifying still requires the words `(Scored)` to be typed **in `RetrievedDoc`'s own file**. Say it came from a retrieval library you installed. That file isn't yours.

**Wrap it.** `class ScoredDoc(Scored)` holding a `RetrievedDoc` inside. This works, and the cost is a different object: every list gets wrapped on the way in, and anything that needs `.url` back unwraps on the way out. A class whose entire job is to satisfy a type checker.

> [!important] Both escapes are the same idea — **nominal typing**. The relationship exists only because somebody declared it by name. Java's `implements Scored` is the same thing: a phrase written inside the implementing class, so a class you can't edit can never implement your interface.
>
> What `best` actually needs is neither. It needs *anything that has a `.score`* — a description of a shape, not a list of approved names.

## Describing a shape

```python
 1  from typing import Protocol
 2
 3
 4  class Scored(Protocol):
 5      score: float
 6
 7
 8  class Candidate:
 9      def __init__(self, text: str, score: float) -> None:
10          self.text = text
11          self.score = score
12
13
14  class ToolCall:
15      def __init__(self, name: str, score: float) -> None:
16          self.name = name
17          self.score = score
18
19
20  class RetrievedDoc:
21      def __init__(self, url: str, score: float) -> None:
22          self.url = url
23          self.score = score
24
25
26  class Timer:
27      def __init__(self, ms: int) -> None:
28          self.ms = ms
29
30
31  def best[T: Scored](items: list[T]) -> T:
32      return max(items, key=lambda c: c.score)
33
34
35  c = best([Candidate("a", 0.9), Candidate("b", 0.4)])
36  d = best([RetrievedDoc("u1", 0.9), RetrievedDoc("u2", 0.4)])
37  t = best([Timer(10), Timer(20)])
38
39  reveal_type(c)
40  reveal_type(d)
```

```
$ mypy p2.py

p2.py:37: error: Value of type variable "T" of "best" cannot be "Timer"  [type-var]

p2.py:39: note: Revealed type is "p2.Candidate"
p2.py:40: note: Revealed type is "p2.RetrievedDoc"
```

Lines 8, 14 and 20 do not mention `Scored`. No inheritance, no wrapper, no edit to `RetrievedDoc` — and line 36 passes.

Line 37 is the proof this isn't just permissive: `Timer` has an `.ms` and no `.score`, and it's rejected.

The only change from the base-class version is line 4, `class Scored(Protocol)`. That one word changes the question the checker asks:

| | asks |
|---|---|
| `class Scored` (base class) | did this class **declare** that it is a `Scored`? |
| `class Scored(Protocol)` | does this class **have** what `Scored` describes? |

Which is the difference between **nominal** typing and **structural** typing. Nominal goes by declared name; structural goes by shape.

> [!important] Nothing is registered anywhere. When mypy checks line 36 it reads `RetrievedDoc`'s own definition — the library's source or its stub file — and compares members one by one against `Scored`. Neither file ever names the other, and the comparison is redone from scratch at every place the question comes up.
>
> Which is why the library doesn't have to have heard of your project. Import `RetrievedDoc` from anywhere and line 36 still passes.

### The duck-typing connection

Structural typing is the type checker finally being able to express what Python has always done at runtime. `max(items, key=lambda c: c.score)` never asked what class anything was; it asked for `.score` and got one. "If it walks like a duck" — a protocol is that sentence written down where a checker can read it.

## What counts as a match

```python
 1  from typing import Protocol
 2
 3
 4  class Scored(Protocol):
 5      score: float
 6
 7
 8  class Typo:
 9      def __init__(self) -> None:
10          self.scores = 0.9
11
12
13  class WrongType:
14      def __init__(self) -> None:
15          self.score = "0.9"
16
17
18  class Extra:
19      def __init__(self) -> None:
20          self.score = 0.9
21          self.url = "u1"
22          self.title = "t"
23
24
25  def take(x: Scored) -> None: ...
26
27
28  take(Typo())
29  take(WrongType())
30  take(Extra())
```

```
$ mypy p4.py

p4.py:28: error: Argument 1 to "take" has incompatible type "Typo"; expected "Scored"  [arg-type]

p4.py:29: error: Argument 1 to "take" has incompatible type "WrongType"; expected "Scored"  [arg-type]

p4.py:29: note: Following member(s) of "WrongType" have conflicts:

p4.py:29: note:     score: expected "float", got "str"
```

**Line 28** — `scores`, not `score`. A near-miss name is a total miss; there is no fuzzy matching. It gets no `Following member(s)` note, because nothing conflicted — the member is simply absent.

**Line 29** — present, but a `str`. That two-line `Following member(s) … have conflicts` note is the shape to recognise on sight: it means the name was found and the type disagreed.

**Line 30 passes.** `Extra` has `.url` and `.title` on top of `.score`, and that's fine.

> [!important] A protocol is a **minimum**, not an exact description. Every member it lists must be present with a compatible type; anything else the class happens to have is ignored.

## A class you can never use as one

`Scored` is written with `class`, so it's worth asking what it actually is at runtime.

```python
 1  from typing import Protocol
 2
 3
 4  class Scored(Protocol):
 5      score: float
 6
 7
 8  class RetrievedDoc:
 9      def __init__(self, url: str, score: float) -> None:
10          self.url = url
11          self.score = score
12
13
14  print("type(Scored)   ->", type(Scored))
15  print("Scored.__mro__ ->", Scored.__mro__)
16
17  try:
18      s = Scored()
19  except TypeError as e:
20      print("Scored()       -> TypeError:", e)
21
22  try:
23      print(isinstance(RetrievedDoc("u1", 0.9), Scored))
24  except TypeError as e:
25      print("isinstance     -> TypeError:", e)
```

```
$ mypy p5.py

p5.py:18: error: Cannot instantiate protocol class "Scored"  [misc]

p5.py:23: error: Only @runtime_checkable protocols can be used with instance and class checks  [misc]
```

```
$ python3 p5.py

type(Scored)   -> <class 'typing._ProtocolMeta'>

Scored.__mro__ -> (<class '__main__.Scored'>, <class 'typing.Protocol'>, <class 'typing.Generic'>, <class 'object'>)

Scored()       -> TypeError: Protocols cannot be instantiated

isinstance     -> TypeError: Instance and class checks can only be used with @runtime_checkable protocols
```

Both tools object, which is unusual — most of this folder is one or the other.

**It is a genuine class object.** It has an `__mro__`, it sits in `object`'s hierarchy. So it is *not* checker-only in the way `Literal` was.

**But you can't instantiate it.** `Protocols cannot be instantiated`, raised at runtime, not merely flagged. It describes a shape; there's nothing to make an instance of.

**And `isinstance` refuses to answer.** That's the important one, and the reason is visible in the `__mro__` line.

> [!info] `__mro__` — "method resolution order" — is the list of classes Python walks, in order, when looking something up on an object. You saw it in `11-TypedDict`, where `User.__mro__` coming back as `(User, dict, object)` was the proof a `TypedDict` really is a plain `dict`.
>
> It's the complete record of what a class inherits from, which makes it exactly where `isinstance` looks: `isinstance(x, Message)` is essentially *is `Message` in `type(x).__mro__`?*

`RetrievedDoc.__mro__` is `(RetrievedDoc, object)`. `Scored` is not in it and never will be — the class doesn't inherit from it, nothing was registered, and the entire match happened inside mypy. So `isinstance` has no record to consult, and raises rather than returning a wrong answer.

## `@runtime_checkable`

A decorator that opts a protocol in to `isinstance`. It changes nothing about type checking.

```python
 1  from typing import Protocol, runtime_checkable
 2
 3
 4  @runtime_checkable
 5  class Scored(Protocol):
 6      score: float
 7
 8
 9  class RetrievedDoc:
10      def __init__(self, url: str, score: float) -> None:
11          self.url = url
12          self.score = score
13
14
15  class WrongType:
16      def __init__(self) -> None:
17          self.score = "not a number"
18
19
20  class Timer:
21      def __init__(self, ms: int) -> None:
22          self.ms = ms
23
24
25  print(isinstance(RetrievedDoc("u1", 0.9), Scored))
26  print(isinstance(WrongType(), Scored))
27  print(isinstance(Timer(10), Scored))
```

```
$ python3 p6.py

True
True
False
```

**Line 26 is `True`**, and `WrongType.score` is the string `"not a number"`.

Since there's no inheritance record to consult, the check does the only thing left available to it: **it looks for an attribute of that name and stops.** One `hasattr` per member listed in the protocol. It never inspects what's inside.

Line 27 is `False` from the other side — `Timer` has no `.score` at all, so the name lookup fails.

> [!important] `isinstance` against a protocol is a **weaker test than the static one**. mypy caught `WrongType` with `score: expected "float", got "str"`; `@runtime_checkable` cannot. A `True` from it means the names are present — not that the object would satisfy the protocol.
>
> That gap is why the decorator is opt-in rather than the default: you have to ask for the weaker check, having been told it's weaker.

## Protocols of methods

`score: float` was the attribute form. The form you write in real code describes **methods**, because that's how components get swapped: a retriever, an LLM client, a checkpointer.

```python
 1  from typing import Protocol
 2
 3
 4  class Retriever(Protocol):
 5      def search(self, query: str, k: int) -> list[str]: ...
 6
 7
 8  class ChromaRetriever:
 9      def search(self, query: str, k: int) -> list[str]:
10          return ["chunk from chroma"]
11
12
13  class FakeRetriever:
14      def search(self, query: str, k: int) -> list[str]:
15          return ["canned chunk"]
16
17
18  class BM25Retriever:
19      def search(self, text: str, k: int) -> list[str]:
20          return ["chunk from bm25"]
21
22
23  class TopKRetriever:
24      def search(self, query: str) -> list[str]:
25          return ["chunk"]
26
27
28  def answer(r: Retriever, q: str) -> str:
29      return " ".join(r.search(q, k=3))
30
31
32  print(answer(ChromaRetriever(), "what is a checkpointer"))
33  print(answer(FakeRetriever(), "what is a checkpointer"))
34  print(answer(BM25Retriever(), "what is a checkpointer"))
35  print(answer(TopKRetriever(), "what is a checkpointer"))
```

Line 5 has no body — `...` is the entire method. Nothing is implemented in `Retriever`.

```
$ mypy p7.py

p7.py:35: error: Argument 1 to "answer" has incompatible type "TopKRetriever"; expected "Retriever"  [arg-type]

p7.py:35: note: Following member(s) of "TopKRetriever" have conflicts:
p7.py:35: note:     Expected:
p7.py:35: note:         def search(self, query: str, k: int) -> list[str]
p7.py:35: note:     Got:
p7.py:35: note:         def search(self, query: str) -> list[str]
```

**Line 35 rejected**, with the most readable message in this concept — expected signature printed above actual. `TopKRetriever.search` takes no `k`, so line 29 calling `r.search(q, k=3)` would crash. That's the arity rule from `10-Callable-And-ParamSpec`: the signature is part of the type.

The payoff is line 33. `FakeRetriever` is a test double returning canned chunks, and it satisfies `Retriever` by having the right method — no base class, no registration, no mock library. **The protocol is written by the code that consumes it, so anything can satisfy it, including something written only for a test.**

### Parameter names — where the checkers disagree

Line 34 was **accepted**, and `BM25Retriever` names its first parameter `text` rather than `query`. That's fine while the call is positional. Make it a keyword:

```python
 1  from typing import Protocol
 2
 3
 4  class Retriever(Protocol):
 5      def search(self, query: str, k: int) -> list[str]: ...
 6
 7
 8  class ChromaRetriever:
 9      def search(self, query: str, k: int) -> list[str]:
10          return ["chunk from chroma"]
11
12
13  class BM25Retriever:
14      def search(self, text: str, k: int) -> list[str]:
15          return ["chunk from bm25"]
16
17
18  def answer(r: Retriever, q: str) -> str:
19      return " ".join(r.search(query=q, k=3))
20
21
22  print(answer(ChromaRetriever(), "what is a checkpointer"))
23  print(answer(BM25Retriever(), "what is a checkpointer"))
```

`FakeRetriever` and `TopKRetriever` are dropped — the first has nothing left to show, the second was already rejected. Only the two that matter remain, which is why `answer` has moved to line 18.

```
$ mypy p8.py
Success: no issues found in 1 source file
```

```
$ python3 p8.py

chunk from chroma

Traceback (most recent call last):
  File "p8.py", line 23, in <module>
    print(answer(BM25Retriever(), "what is a checkpointer"))
  File "p8.py", line 19, in answer
    return " ".join(r.search(query=q, k=3))
TypeError: BM25Retriever.search() got an unexpected keyword argument 'query'
```

`Success`, then a crash. mypy compared the two signatures and treated the parameter **name** as outside the contract; `search(query=...)` is a name lookup at runtime, and there is no `query`.

pyright, on the identical file:

```
$ pyright p8.py
p8.py:23:14 - error: Argument of type "BM25Retriever" cannot be assigned to parameter "r" of type "Retriever" in function "answer"
    "BM25Retriever" is incompatible with protocol "Retriever"
      "search" is an incompatible type
        Type "(text: str, k: int) -> list[str]" is not assignable to type "(query: str, k: int) -> list[str]"
          Parameter name mismatch: "query" versus "text" (reportArgumentType)
```

**Caught, and named exactly.** This is the disagreement `03-Static-Type-Checkers` promised, with a concrete case behind it — and a consequential one, because pyright is what VS Code's Pylance runs. The editor and a mypy-based CI can reach opposite verdicts on the same protocol.

### Saying the names don't matter

If a protocol is only ever called positionally, declare that with `/`:

```python
1  def normal(query: str, k: int) -> None:
2      print("normal ok")
3
4
5  def posonly(query: str, k: int, /) -> None:
6      print("posonly ok")
7
8
9  normal("hi", 3)
10 normal(query="hi", k=3)
11 posonly("hi", 3)
12 posonly(query="hi", k=3)
```

```
$ python3 pa.py

normal ok
normal ok
posonly ok

posonly(query=...) -> TypeError: posonly() got some positional-only arguments passed as keyword arguments: 'query, k'
```

Ordinary Python syntax, nothing to do with typing: **everything left of the `/` can only be passed by position.** Line 10 works, line 12 raises. The parameter names become internal detail — the same way `len(obj)` gives you no name to pass by.

Put it in the protocol and the ambiguity is gone:

```python
 1  from typing import Protocol
 2
 3
 4  class Retriever(Protocol):
 5      def search(self, query: str, k: int, /) -> list[str]: ...
 6
 7
 8  class ChromaRetriever:
 9      def search(self, query: str, k: int) -> list[str]:
10          return ["chunk from chroma"]
11
12
13  class BM25Retriever:
14      def search(self, text: str, k: int) -> list[str]:
15          return ["chunk from bm25"]
16
17
18  def answer(r: Retriever, q: str) -> str:
19      return " ".join(r.search(query=q, k=3))
20
21
22  print(answer(ChromaRetriever(), "what is a checkpointer"))
23  print(answer(BM25Retriever(), "what is a checkpointer"))
```

The same file as before with one `/` added on line 5, and nothing else touched.

```
$ mypy p9.py

p9.py:19: error: Unexpected keyword argument "query" for "search" of "Retriever"  [call-arg]

p9.py:19: error: Unexpected keyword argument "k" for "search" of "Retriever"  [call-arg]
```

`BM25Retriever` is now accepted with no complaint, and **line 19 — the caller — is the error.** Which is the honest arrangement: the protocol never promised those names, so using them is the mistake.

## `Protocol` versus ABC

The named comparison, and the reason it's asked is that neither replaces the other.

```python
 1  from abc import ABC, abstractmethod
 2
 3
 4  class Retriever(ABC):
 5      @abstractmethod
 6      def search(self, query: str, k: int) -> list[str]: ...
 7
 8      def search_one(self, query: str) -> str:
 9          return self.search(query, 1)[0]
10
11
12  class ChromaRetriever(Retriever):
13      def search(self, query: str, k: int) -> list[str]:
14          return ["chunk from chroma"]
15
16
17  class Broken(Retriever):
18      pass
19
20
21  class Unrelated:
22      def search(self, query: str, k: int) -> list[str]:
23          return ["chunk"]
24
25
26  def answer(r: Retriever, q: str) -> str:
27      return r.search_one(q)
28
29
30  print(answer(ChromaRetriever(), "q"))
31  print(answer(Unrelated(), "q"))
32  b = Broken()
```

An **ABC** is an abstract base class. Line 5's `@abstractmethod` marks `search` as something every subclass must supply; line 8 is a concrete method the base implements for everyone.

```
$ mypy pb.py

pb.py:31: error: Argument 1 to "answer" has incompatible type "Unrelated"; expected "Retriever"  [arg-type]

pb.py:32: error: Cannot instantiate abstract class "Broken" with abstract attribute "search"  [abstract]
```

```
$ python3 pb.py

chunk from chroma

Traceback (most recent call last):
  File "pb.py", line 31, in <module>
    print(answer(Unrelated(), "q"))
  File "pb.py", line 27, in answer
    return r.search_one(q)
AttributeError: 'Unrelated' object has no attribute 'search_one'
```

**Line 31 rejected.** An ABC is a base class, so it's nominal like any other — `Unrelated` didn't inherit, so it isn't a `Retriever` however identical its `search` is. The same failure as the base-class attempt earlier in this note, and the entire reason `Protocol` exists.

The crash shows the rejection was *right*, not merely strict. `answer` calls `search_one`, which `Unrelated` has never heard of. Matching `search` was never enough.

**Line 32 objected to twice** — flagged by mypy, and `TypeError` from Python at instantiation if you ignore the checker. That's the ABC's distinctive power: **an incomplete implementation cannot come into existence**, with no checker in the loop.

### A protocol's implemented method is a requirement, not a gift

A protocol may also carry a real body, and it means something different:

```python
 1  from typing import Protocol
 2
 3
 4  class Retriever(Protocol):
 5      def search(self, query: str, k: int) -> list[str]: ...
 6
 7      def search_one(self, query: str) -> str:
 8          return self.search(query, 1)[0]
 9
10
11  class Unrelated:
12      def search(self, query: str, k: int) -> list[str]:
13          return ["chunk"]
14
15
16  def answer(r: Retriever, q: str) -> str:
17      return r.search_one(q)
18
19
20  print(answer(Unrelated(), "q"))
```

```
$ mypy pc.py

pc.py:20: error: Argument 1 to "answer" has incompatible type "Unrelated"; expected "Retriever"  [arg-type]
pc.py:20: note: "Unrelated" is missing following "Retriever" protocol member:
pc.py:20: note:     search_one
```

`Unrelated` is rejected for *not having `search_one`* — the very method the protocol implements on line 8.

> [!important] Nothing hands `search_one` to a class that merely matches. `Unrelated` doesn't inherit from `Retriever`, so implementing a method inside a protocol only adds **one more member the class has to have**. The body is inherited exclusively by a class that explicitly writes `class X(Retriever)`.
>
> An ABC is the opposite: inheritance is mandatory anyway, so a concrete method arrives free with the membership.

| | ABC | `Protocol` |
|---|---|---|
| how you qualify | inherit, by name | have the members |
| classes you don't own | can't use it | works |
| enforced when | **runtime** — can't instantiate an incomplete class | check time only |
| shared implementation | inherited free | a requirement unless you inherit |
| who writes the dependency | the implementer names your abstraction | the consumer describes what it needs |

The last row answers the question. **An ABC points from the implementer to the abstraction; a `Protocol` points from the consumer to it.**

So: your own class hierarchy, where an incomplete implementation must be impossible → ABC.
A boundary where the arriving things are third-party, test doubles, or otherwise not yours to change → `Protocol`.

Which is the agent case exactly. `Retriever`, `LLMClient`, `Checkpointer` are protocols, because a vector-store client, a provider SDK, and your fake-for-tests are never going to inherit from anything you wrote.

## Why this rung comes after variance

One fact first, because the demo rests on it:

```python
1  def take(x: float) -> None: ...
2
3  take(3)
4  take(3.0)
5
6  a: float = 3
7  b: int = 3.0
```

```
$ mypy pd.py

pd.py:7: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
```

Only line 7. **`float` is a special case in the type system**: an `int` is accepted anywhere a `float` is wanted, **despite `int` not being a subclass of `float`**. Not the reverse.

In `15-Variance`'s vocabulary: **`int` is narrower than `float`.**

Now two protocols describing the same thing in different words:

```python
 1  from typing import Protocol
 2
 3
 4  class HasScoreAttr(Protocol):
 5      score: float
 6
 7
 8  class HasScoreProp(Protocol):
 9      @property
10      def score(self) -> float: ...
11
12
13  class Doc:
14      def __init__(self) -> None:
15          self.score: int = 3
16
17
18  def a(x: HasScoreAttr) -> None: ...
19  def b(x: HasScoreProp) -> None: ...
20
21
22  a(Doc())
23  b(Doc())
```

Line 9's `@property` makes a method behave like a plain attribute — write `doc.score`, no parentheses, and the method runs. What matters here is that as written there is no way to *assign* to it: it is **read-only**. Line 5 is not — `x.score = 4.5` would be legal.

```
$ mypy p3.py

p3.py:22: error: Argument 1 to "a" has incompatible type "Doc"; expected "HasScoreAttr"  [arg-type]
p3.py:22: note: Following member(s) of "Doc" have conflicts:
p3.py:22: note:     score: expected "float", got "int"
```

**Line 22 fails, line 23 passes.** Same class, same `int`; the only difference is whether the protocol's member can be written to.

**Line 5 is writable**, so a function holding a `HasScoreAttr` may do `x.score = 4.5`. If `Doc` qualified, that would put a `float` into an attribute the rest of `Doc` believes is an `int` — the `list[Dog]` / `list[Animal]` problem on a single attribute instead of a container. Writable means **invariant**: exactly `float`, not even something narrower.

**Line 9 is read-only**, nobody can write through it, so the danger doesn't exist and the member can be **covariant** — narrower is fine, and `int` is narrower than `float`.

> [!important] A protocol member declared as a plain attribute is **invariant**; one declared read-only with `@property` is **covariant**. The same rule as `list` versus `Sequence`, for the same reason — a mutable thing must be safe in both directions, a read-only thing only in one.
>
> The practical consequence: **if your protocol only reads a value, declare it read-only.** `score: float` silently demands an exact `float` from every implementer; the property form accepts anything readable as one. That is `06-Abstract-Collection-Types`'s "annotate the weakest type the body needs", applied to a protocol's members.

`Protocol` needs nothing from variance in order to be *used*. But its member-compatibility rules **are** variance rules, so without that vocabulary the result above is a mystery to be memorised rather than a consequence.

## What this concept claims

**A protocol is a type defined by what an object has, rather than by what it declared itself to be.**

Five things to carry:

1. **Nominal versus structural.** A base class or an ABC requires the implementer to name your abstraction in their own file, which is impossible for a class you don't own — a fact no amount of open-endedness in the bound fixes. A protocol asks only whether the members are present, so the library never has to have heard of you.
2. **It is a minimum, matched from scratch.** Every listed member must exist with a compatible type; extras are ignored; a near-miss name is a total miss. Nothing is registered anywhere — the checker re-reads the class definition at each place the question arises.
3. **At runtime it is a class that can't be used as one.** It cannot be instantiated, and `isinstance` refuses to answer because the relationship exists in no `__mro__`. `@runtime_checkable` lets it answer by checking that the *names* exist, which is strictly weaker than the static check and will say `True` for an object of entirely the wrong type.
4. **`Protocol` versus ABC is a question of direction.** An ABC points from the implementer to the abstraction, enforces at runtime, and hands down shared implementation for free. A protocol points from the consumer to the abstraction, enforces only at check time, and treats an implemented method as one more requirement. Own the hierarchy → ABC; describing a boundary things arrive at → protocol.
5. **Member variance follows the same rule as containers.** A writable attribute is invariant, a read-only `@property` is covariant — so a protocol that only reads should say so, or it demands exactness it never needed.

One loose end left deliberately: mypy accepted a parameter-name mismatch that pyright rejected. A protocol match is only as strong as the members the checker chooses to compare, and which checker you run is part of the answer.
