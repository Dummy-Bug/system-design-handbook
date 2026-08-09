#python #type-hints #typing #generics #python-utils


`13-TypeVar-And-Generic-Functions` put a placeholder on a function, resolved fresh at every call. Some types have to remember the answer instead — you put a tool name in a store, and much later you take a tool name back out.

## A store that forgets

The shape behind a checkpoint store, a tool registry, a message buffer:

```python
 1  from typing import Any
 2
 3
 4  class Store:
 5      def __init__(self) -> None:
 6          self._items: list[Any] = []
 7
 8      def add(self, item: Any) -> None:
 9          self._items.append(item)
10
11      def get(self, i: int) -> Any:
12          return self._items[i]
13
14
15  tools = Store()
16  tools.add("search")
17  tools.add(42)
18
19  reveal_type(tools.get(0))
```

`tools` is meant to hold tool names. Line 17 puts an integer in it.

```
$ mypy gc0.py
gc0.py:19: note: Revealed type is "Any"
Success: no issues found in 1 source file
```

Line 17 unflagged, line 19 `Any`. Same failure as the `first` helper in the previous note, and the same cause — nothing ties what goes in to what comes out.

## Why a method-level placeholder can't fix it

The obvious repair is the one that worked last time:

```python
1  class Store:
2      def __init__(self) -> None:
3          self._items: list[T] = []
4
5      def add[T](self, item: T) -> None:
6          self._items.append(item)
7
8      def get[T](self, i: int) -> T:
9          return self._items[i]
```

```
$ mypy gc1.py
gc1.py:3: error: Name "T" is not defined  [name-defined]
gc1.py:8: error: A function returning TypeVar should receive at least one argument containing the same TypeVar  [type-var]
```

Two failures, and the second is the structural one.

**Line 3** — `T` was declared on `add`, so it does not exist in `__init__`. A method-level declaration is scoped to that method.

**Line 8** — `get[T]` declares a fresh `T` and promises to return it, but its only argument is `i: int`. There is nothing in the call to work `T` out from, and mypy says so: *a function returning a TypeVar should receive at least one argument containing the same TypeVar*.

> [!important] That's the difference from a generic *function*. `first(tool_names)` resolved `T` from the argument at that call. `get(0)` carries no such information — **the type was decided when the store was created, not when `get` was called.** So the placeholder has to belong to the object and survive across every method call on it.

## Declaring it on the class

```python
 1  class Store[T]:
 2      def __init__(self) -> None:
 3          self._items: list[T] = []
 4
 5      def add(self, item: T) -> None:
 6          self._items.append(item)
 7
 8      def get(self, i: int) -> T:
 9          return self._items[i]
10
11      def all(self) -> list[T]:
12          return self._items
13
14
15  tools: Store[str] = Store()
16  tools.add("search")
17  tools.add(42)
18
19  reveal_type(tools)
20  reveal_type(tools.get(0))
21  reveal_type(tools.all())
22  print(tools.get(0).upper())
23
24  runs: Store[dict[str, str]] = Store()
25  runs.add({"run_id": "r1"})
26  reveal_type(runs.get(0))
27  print(runs.get(0).upper())
```

```
$ mypy gc2.py
gc2.py:17: error: Argument 1 to "add" of "Store" has incompatible type "int"; expected "str"  [arg-type]
gc2.py:19: note: Revealed type is "gc2.Store[str]"
gc2.py:20: note: Revealed type is "str"
gc2.py:21: note: Revealed type is "list[str]"
gc2.py:26: note: Revealed type is "dict[str, str]"
gc2.py:27: error: "dict[str, str]" has no attribute "upper"  [attr-defined]
```

`[T]` moved from the methods to **line 1, after the class name** — declared once for the whole class, and every method may refer to it.

- **Line 17 caught** — an `int` into a `Store[str]`.
- **Line 20 is `str`**, so line 22's `.upper()` is fine. And it came from `get(0)`, whose arguments still carry no type information. The store remembered.
- **Line 21 is `list[str]`.** The placeholder composes — `T` inside `list[T]` resolves too.
- **Line 26 is `dict[str, str]`** and line 27 is caught. A second store, a different `T`, one class.

Line 15 is where `T` gets fixed: **`Store[str]`**. You supply the type argument when the object is created, and the class is written once for every possible one.

Which is what `list[str]` has been doing since `05-Built-In-Generics`. `list` is a generic class; you have been supplying its `T` all along.

## Where the brackets go

Two places, and they mean the same thing:

```python
12  a: Store[str] = Store()      # on the variable
13  reveal_type(a)
14
15  b = Store[str]()             # on the constructor call
16  reveal_type(b)
17
18  c = Store()                  # neither
19  c.add("search")
20  reveal_type(c)
```

```
$ mypy gc3.py
gc3.py:13: note: Revealed type is "gc3.Store[str]"
gc3.py:16: note: Revealed type is "gc3.Store[str]"
gc3.py:18: error: Need type annotation for "c"  [var-annotated]
gc3.py:20: note: Revealed type is "gc3.Store[Any]"
```

Lines 12 and 15 produce identical results. `Store[str]()` is the `new ArrayList<String>()` shape; `a: Store[str] = Store()` attaches the same information to the variable instead. Style, not meaning.

**Line 18 is the one to remember.** Bare `Store()` gets `Need type annotation`, and line 20 shows the fallback — **`Store[Any]`**, silently back where the concept started. The `add("search")` on line 19 does not rescue it: by then the object exists, and it was created knowing nothing.

`__init__` took no arguments, so there was nothing to infer from. Give it one:

```python
 2  def __init__(self, first: T) -> None:
 3      self._items: list[T] = [first]
...
 9  d = Store("search")
10  reveal_type(d)
11  reveal_type(d.get(0))
```

```
$ mypy gc4.py
gc4.py:10: note: Revealed type is "gc4.Store[str]"
gc4.py:11: note: Revealed type is "str"
Success: no issues found in 1 source file
```

No annotation anywhere and `T` is `str`, inferred from the constructor argument exactly as a generic function infers from its own.

> [!important] **`T` is fixed at construction.** If `__init__` receives something that determines it, mypy infers it. If not — an empty store, a fresh queue, a blank buffer — you must write `Store[str]`, and forgetting leaves you with `Store[Any]` and no checking at all.
>
> Same rule as `items: list[str] = []`, which needs its annotation for the same reason: an empty container tells you nothing about what it will hold.

### Where the inference comes from

`a: Store[str] = Store()` is the diamond operator, and Python's version of `<>` is simply nothing at all:

| Java | Python |
|---|---|
| `List<String> l = new ArrayList<>();` | `a: Store[str] = Store()` |
| `var l = new ArrayList<String>();` | `b = Store[str]()` |

It's genuine inference, not an unchecked assignment:

```python
 9  a: Store[str] = Store()       # bare — inferred from the left
10  a.add("search")
11  a.add(42)
12
13  b: Store[str] = Store[int]()  # explicit, and wrong
14
15  def make() -> Store[int]:
16      return Store()            # inferred from the return annotation
17
18  c: Store[str] = make()
```

```
$ mypy gc6.py
gc6.py:11: error: Argument 1 to "add" of "Store" has incompatible type "int"; expected "str"  [arg-type]
gc6.py:13: error: Incompatible types in assignment (expression has type "Store[int]", variable has type "Store[str]")  [assignment]
gc6.py:18: error: Incompatible types in assignment (expression has type "Store[int]", variable has type "Store[str]")  [assignment]
```

**Line 11** — `a` really did become `Store[str]`, so `add(42)` is an error. The annotation wasn't accepted and forgotten.

**Line 13** — an explicit type argument that disagrees is an error, not an override. The left side doesn't *force* anything; it states a requirement the right side has to satisfy. Bare `Store()` satisfies any `Store[X]` precisely because it is asking to be told.

**Line 16** — the same inference works from a return annotation. Anywhere the expected type is known, a bare constructor call takes it.

> [!info] One difference from Java. There, `<>` is a token you must type — omit it and you get a raw type plus a compiler warning. Python has no such marker, so the good case and the bad case look identical:
>
> ```python
> a: Store[str] = Store()     # inferred — fine
> c = Store()                 # nothing to infer from → Store[Any]
> ```
>
> `Need type annotation for "c"` is the diagnostic standing in for that warning: the checker saying it had nowhere to get the answer from.

## Brackets are not arguments

A natural mis-guess is `Store(str)` — passing the type in like a value:

```
$ python3 gc5.py
Store[str]       -> __main__.Store[str]
type of that     -> <class 'typing._GenericAlias'>
Store[str]()     -> <__main__.Store object at 0x104e12cf0>
type(b)          -> <class '__main__.Store'>
type(b) is Store -> True
type(a)          -> <class '__main__.Store'>
a and b same type? True

now trying Store(str):
  TypeError: Store.__init__() takes 1 positional argument but 2 were given
```

`Store(str)` fails, because `__init__` takes no arguments and `str` was arriving as an ordinary value. **Parentheses pass values at runtime; brackets supply types for the checker.**

The last three lines are the ones worth keeping:

- `Store[str]` is a `typing._GenericAlias` — a description object, not a class.
- `Store[str]()` produces a plain **`Store`**; `type(b) is Store` is `True`.
- `a` and `b` are **the same type**. Nothing on the object records that it holds strings.

> [!important] **The `[str]` is discarded at runtime.** A `Store[str]` and a `Store[dict]` are indistinguishable to the interpreter — same class, no tag, nothing to inspect.
>
> This is the one place the Java comparison from `01-What-A-Type-Hint-Is` lands exactly. Erasure there applies to **generic type parameters**, not to ordinary types — so `age: int` was never the erasure case, and `Store[str]` erasing to `Store` is precisely `ArrayList<String>` erasing to `ArrayList`.

## What this concept claims

**A generic class carries its placeholder on the object, so a type supplied once at construction is remembered by every method.**

Four things to carry:

1. A method-level `TypeVar` cannot do this. It is scoped to one method, and a method whose arguments don't mention it has nothing to infer from.
2. `class Store[T]` declares once, after the class name. Every method may then use `T`, including inside other generics like `list[T]`.
3. `T` is fixed at construction — inferred if `__init__` receives something that determines it, otherwise written explicitly as `Store[str]`. An unannotated empty container silently becomes `Store[Any]`.
4. It costs nothing and records nothing at runtime. `Store[str]()` builds a plain `Store`; the type argument exists only for the checker.
