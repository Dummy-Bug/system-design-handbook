#python #type-hints #typing #typevar #generics #python-utils


## A helper that loses everything it knew

Take the first item off a list — the shape behind picking a tool, a candidate, a message:

```python
 1  from typing import Any
 2
 3
 4  def first(items: list[Any]) -> Any:
 5      return items[0]
 6
 7
 8  tool_names = ["search", "calculator", "summarize"]
 9  runs = [{"run_id": "r1"}, {"run_id": "r2"}]
10
11  t = first(tool_names)
12  r = first(runs)
13
14  reveal_type(t)
15  reveal_type(r)
16
17  print(t.upper())
18  print(r.upper())
```

`first` must work on a list of tool names *and* a list of run records, so `list[Any] -> Any` looks like the honest annotation — it genuinely does not know what's in the list.

Line 17 is correct: `t` is a string. Line 18 is a bug: `r` is a dict, and dicts have no `.upper()`.

```
$ mypy tv0.py

tv0.py:14: note: Revealed type is "Any"
tv0.py:15: note: Revealed type is "Any"
Success: no issues found in 1 source file
```

**Both are `Any`.** mypy knew perfectly well that `tool_names` was a `list[str]` and `runs` was a `list[dict[str, str]]` — and threw that away the moment the values passed through `first`, because the annotation told it to. Line 18 goes unchecked, and so does anything else written on `t` or `r`, by the spreading from `08-Any-Object-Never`.

> [!info] `reveal_type` raises `NameError` under `python3` — it's a name mypy recognises in source that doesn't exist at runtime. Fine to leave in a scratch file while checking; delete it before running.

The diagnosis: `first` **does** have a relationship between input and output — it returns an element of the list it was handed — and `list[Any] -> Any` says nothing about it. Two independent unknowns where there should be one shared one.

## One placeholder, mentioned twice

```python
 1  def first[T](items: list[T]) -> T:
 2      return items[0]
 3
 4
 5  tool_names = ["search", "calculator", "summarize"]
 6  runs = [{"run_id": "r1"}, {"run_id": "r2"}]
 7
 8  t = first(tool_names)
 9  r = first(runs)
10
11  reveal_type(t)
12  reveal_type(r)
13
14  print(t.upper())
15  print(r.upper())
```

Same file as before, with lines 1–2 replaced. The `from typing import Any` at the top is gone — there is nothing left to import.

`T` is declared in brackets after the name, then used in two places. The line reads: *given a list of `T`, return a `T`* — whatever `T` turns out to be at each call site.

```
$ mypy tv1.py

tv1.py:11: note: Revealed type is "str"
tv1.py:12: note: Revealed type is "dict[str, str]"
tv1.py:15: error: "dict[str, str]" has no attribute "upper"  [attr-defined]
```

`t` is `str`, `r` is `dict[str, str]`, and only the genuinely wrong line is flagged. The placeholder was resolved **separately for each call** — `T` was `str` for one and `dict[str, str]` for the other.

No explicit type argument is needed:

```
$ python3 tv2.py

SEARCH
s
```

`first(tool_names).upper()` works and `first(tool_names)[0]` gives `"s"` — mypy inferred `T` from the argument at each site. You *can* write `first[str](tool_names)` when inference fails, but you rarely need to.

> [!important] That's the difference from `Any` in one line. **`Any` is two unknowns that never meet. `T` is one unknown, mentioned twice** — which is what lets the answer flow from the input to the output.

## Where an unrestricted `T` breaks

A helper that picks the highest-scoring item — the shape behind any ranking or reranking step:

```python
1  def best[T](items: list[T]) -> T:
2      return max(items)
```

`max` has to compare items with `<`, and `T` is *any type at all*.

```
$ mypy tv3.py

tv3.py:2: error: Value of type variable "SupportsRichComparisonT" of "max" cannot be "T"  [type-var]
```

Rejected — and the message is worth reading, because **`max` is generic too**. Its placeholder is called `SupportsRichComparisonT`: a `TypeVar` that has been restricted to types supporting `<`. An unrestricted `T` doesn't qualify, so the call fails inside your own function body, before any caller exists.

There are two ways to restrict one, and they mean different things.

## A bound — `T: Message`

```python
19  def last[T: Message](msgs: list[T]) -> T:
20      return msgs[-1]
21
22
23  h = last([HumanMessage("hi", "u1"), HumanMessage("again", "u1")])
24  a = last([AIMessage("hello", "opus"), AIMessage("more", "opus")])
25
26  reveal_type(h)
27  reveal_type(a)
28
29  print(h.user_id)
30  print(a.user_id)
31
32  bad = last(["just", "strings"])
```

with `HumanMessage` and `AIMessage` both subclassing `Message`, and `user_id` existing only on the former.

```
$ mypy tv5.py

tv5.py:26: note: Revealed type is "tv5.HumanMessage"
tv5.py:27: note: Revealed type is "tv5.AIMessage"

tv5.py:30: error: "AIMessage" has no attribute "user_id"  [attr-defined]
tv5.py:32: error: Value of type variable "T" of "last" cannot be "str"  [type-var]
```

`T: Message` means **"`Message`, or any subclass of it."** Two consequences, and the second is the payoff:

- **Line 32 is rejected.** A `str` is not a `Message`, so the function cannot be called with one.
- **Lines 26–27 keep the *specific* subclass** — `HumanMessage` and `AIMessage`, not `Message`. Which is why line 29 finds `user_id` and line 30 correctly does not.

Annotating `msgs: list[Message] -> Message` would also have rejected the strings — and would have handed every caller back a plain `Message`, throwing the subclass away. The placeholder keeps it.

## Constraints — `T: (Candidate, ToolCall)`

```python
16  def best[T: (Candidate, ToolCall)](items: list[T]) -> T:
17      return max(items, key=lambda c: c.score)
...
25  bad = best(["x", "y"])
```

```
$ mypy tv4.py
tv4.py:22: note: Revealed type is "tv4.Candidate"
tv4.py:23: note: Revealed type is "tv4.ToolCall"
tv4.py:25: error: Value of type variable "T" of "best" cannot be "str"  [type-var]
```

A tuple means **"exactly one of these, and nothing else."** No subclasses, and no common base required — `Candidate` and `ToolCall` here are unrelated classes that merely both have a `.score`.

| | `T: Message` (bound) | `T: (Candidate, ToolCall)` (constraints) |
|---|---|---|
| written as | one type | a tuple of types |
| means | that type **or a subclass** | **exactly** one of these |
| open to new types? | yes — any future subclass | no — the list is closed |
| use when | there is a common base class | there isn't, and you want a fixed set |

A bound is what you'll write almost always. Constraints are for types that genuinely have nothing in common — and reaching for them because several unrelated classes share a *method* is a signal for a different tool, on a later rung.

## Declaring versus using

The bound goes on the declaration, not on each use. The alternative doesn't parse:

```python
4  def last(msgs: list[T: Message]) -> T:
```

```
$ python3 tv6.py

NameError: name 'T' is not defined
```

```
$ mypy tv6.py

tv6.py:4: error: Invalid type comment or annotation  [valid-type]
tv6.py:4: error: Name "T" is not defined  [name-defined]
```

`NameError` from Python itself is the clearest explanation: without the `[T]` after the function name, **`T` was never introduced**. It's an ordinary name lookup, exactly like `x: does_not_exist` in `02-Why-Bother-If-Nothing-Enforces-Them`, and nothing called `T` exists.

```python
def last[T: Message](msgs: list[T]) -> T:
        └─ declaration ─┘      └ uses ┘
```

`[T: Message]` introduces `T` and states its restriction, **once**. After that `T` is a name to write as often as needed — in `list[T]`, in `-> T`, in the body.

Put the bound at the use site and there's no answer to an obvious question:

```python
def merge(a: list[T: Message], b: list[T: HumanMessage]) -> T:
```

Two bounds on one placeholder, contradicting each other. Declaring once removes the question — the same reason a parameter is annotated at the `def` rather than at every line that reads it.

Same shape as the decorator in `10-Callable-And-ParamSpec`:

```python
def logged[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
```

`[**P, R]` declares; `Callable[P, R]` uses, twice.

The older spelling makes the declaration a literal statement, and you'll meet it in existing code:

```python
T = TypeVar("T", bound=Message)

def last(msgs: list[T]) -> T: ...
```

`T` is created on its own line with `bound=` as an argument, then used bare. The `[T: Message]` syntax is that same declaration moved onto the `def` line, where it's visible at the point it applies.

## What this concept claims

**A `TypeVar` is one unknown type mentioned in more than one place, which is how an output type gets tied to an input type.**

Four things to carry:

1. `list[Any] -> Any` and `list[T] -> T` look equally vague and are not. The first is two unrelated unknowns and destroys everything downstream; the second is one unknown, so the caller gets a real type back.
2. It resolves per call. The same function returns `str` at one call site and `dict[str, str]` at another, with no explicit type argument.
3. An unrestricted `T` can't be used for much — you can't compare it, add it, or call methods on it. `max` failing inside the body is the checker enforcing that.
4. A **bound** (`T: Message`) admits subclasses and preserves which one; **constraints** (`T: (A, B)`) admit exactly the listed types. Both are declared once, after the function name, because a placeholder used many times can only have one restriction.
