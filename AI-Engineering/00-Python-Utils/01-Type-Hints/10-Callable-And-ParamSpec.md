#python #type-hints #typing #callable #python-utils


Every annotation so far has described **data** — a number, a list of strings, a status. This one describes a **function being passed around as a value**.

## A function that takes a function

```python
 1  def apply_twice(f, x: int) -> int:
 2      return f(f(x))
 3
 4
 5  def double(n: int) -> int:
 6      return n * 2
 7
 8
 9  print(apply_twice(double, 5))
10  print(apply_twice("not a function", 5))
```

`f` on line 1 is the only unannotated thing in the file — `x: int` was obvious, `f` was not. Line 9 passes a function; line 10 passes a string, and `"not a function"(5)` is nonsense.

```
$ mypy call0.py

Success: no issues found in 1 source file
```

```
$ python3 call0.py
20
Traceback (most recent call last):
  File "call0.py", line 10, in <module>
    print(apply_twice("not a function", 5))
  File "call0.py", line 2, in apply_twice
    return f(f(x))
TypeError: 'str' object is not callable
```

Silence from the checker, `20` from line 9, and line 10 dying inside **line 2** with `'str' object is not callable`. The blindness has the familiar cause: nothing was claimed about `f`, so nothing could be checked.

## `Callable`

```python
 1  from collections.abc import Callable
 2
 3
 4  def apply_twice(f: Callable, x: int) -> int:
 5      return f(f(x))
 6
 7
 8  def double(n: int) -> int:
 9      return n * 2
10
11
12  def shout(s: str) -> str:
13      return s.upper()
14
15
16  print(apply_twice(double, 5))
17  print(apply_twice("not a function", 5))
18  print(apply_twice(shout, 5))
```

```
$ mypy call1.py
call1.py:17: error: Argument 1 to "apply_twice" has incompatible type "str"; expected "Callable[..., Any]"  [arg-type]
```

The string is caught. `Callable` comes from **`collections.abc`** — the same place as `Iterable` and `Sequence` — and it names the category *"a thing you can put brackets after and call."*

But two details in that one line of output matter.

**mypy expanded the bare `Callable` into `Callable[..., Any]`** — *"takes any arguments at all, returns something I won't examine."* The `...` is a real spelling, not shorthand in the message.

**And only line 17 was flagged.** Line 18 passes `shout`, which takes a `str` and returns a `str`, into a function that will call it with `5` and then feed the result back in. That is a genuine bug and it went through.

This is `05-Built-In-Generics` again in a new costume: the bare form checks the box and ignores the contents.

## Parameterising it

The natural guess is `Callable[int, int]`, and it doesn't parse:

```python
3  wrong: Callable[int, int]
```

```
$ mypy call3.py
call3.py:3: error: The first argument to Callable must be a list of types, parameter specification, or "..."  [valid-type]
```

The arguments need brackets of their own:

```python
Callable[[arg1, arg2, ...], return_type]
```

Always exactly two slots. The first is a **list** of parameter types, because a function may take zero, one, or nine arguments and that count needs its own container. The second is the return type, of which there is always exactly one.

`Callable[int, int]` would have been ambiguous — two arguments and no return, or one argument and a return? The nested list removes the question.

```python
 1  from collections.abc import Callable
 2
 3
 4  def apply_twice(f: Callable[[int], int], x: int) -> int:
 5      return f(f(x))
 6
 7
 8  def double(n: int) -> int:
 9      return n * 2
10
11
12  def shout(s: str) -> str:
13      return s.upper()
14
15
16  def add(a: int, b: int) -> int:
17      return a + b
18
19
20  print(apply_twice(double, 5))
21  print(apply_twice("not a function", 5))
22  print(apply_twice(shout, 5))
23  print(apply_twice(add, 5))
```

```
$ mypy call2.py

call2.py:21: error: Argument 1 to "apply_twice" has incompatible type "str"; expected "Callable[[int], int]"  [arg-type]

call2.py:22: error: Argument 1 to "apply_twice" has incompatible type "Callable[[str], str]"; expected "Callable[[int], int]"  [arg-type]

call2.py:23: error: Argument 1 to "apply_twice" has incompatible type "Callable[[int, int], int]"; expected "Callable[[int], int]"  [arg-type]
```

Three errors; only line 20 survives.

Two things worth reading off those messages.

**The checker describes each function by its signature** — `Callable[[str], str]` for `shout`, `Callable[[int, int], int]` for `add`. It derived those from the `def` lines. Every annotated function already *has* a `Callable` type whether or not anyone writes one; `Callable[...]` is just how you name that type in a place where a function is being received rather than defined.

**Line 23 is the interesting failure.** `add` is a perfectly good function that takes ints and returns an int — it simply takes *two*. Nothing about its types is wrong; the count is.

> [!important] **The number of parameters is part of a function's type.** `Callable[[int], int]` and `Callable[[int, int], int]` are as different as `str` and `int`. That's the same idea as a tuple's length being part of its type, and it's the reason a decorator that flattens everything to `(*args, **kwargs)` loses real information — which is the problem the rest of this concept solves.

### `...` and `Any` relax different things

Worth pinning down before going further, because the two look interchangeable and the stricter one reads as the looser one:

```python
 5  def takes_ellipsis(f: Callable[..., Any]) -> None: ...
 6  def takes_one_any(f: Callable[[Any], Any]) -> None: ...
 7
 8
 9  def zero() -> str: ...
10  def one(a: int) -> str: ...
11  def two(a: int, b: int) -> str: ...
12
13
14  takes_ellipsis(zero)
15  takes_ellipsis(one)
16  takes_ellipsis(two)
17
18  takes_one_any(zero)
19  takes_one_any(one)
20  takes_one_any(two)
```

```
$ mypy ellipsis.py

ellipsis.py:18: error: Argument 1 to "takes_one_any" has incompatible type "Callable[[], str]"; expected "Callable[[Any], Any]"  [arg-type]

ellipsis.py:20: error: Argument 1 to "takes_one_any" has incompatible type "Callable[[int, int], str]"; expected "Callable[[Any], Any]"  [arg-type]
```

Lines 14–16 all pass; of 18–20 only 19 survives.

- **`Callable[..., Any]`** — any number of parameters, of any types. The count is unconstrained.
- **`Callable[[Any], Any]`** — **exactly one** parameter, whose type won't be checked. The count is fixed at one.

`...` relaxes the count. `Any` relaxes the type. Different axes, and `Callable[[Any], Any]` is the stricter of the two.

## The decorator problem

One line of vocabulary first: **`@logged` above a `def` means exactly `greet = logged(greet)`.** Python calls `logged` with the function and rebinds the name to whatever comes back. That is all a decorator is; the mechanics belong to a later folder.

```python
 1  from collections.abc import Callable
 2  from typing import Any
 3
 4
 5  def logged(fn: Callable[..., Any]) -> Callable[..., Any]:
 6      def wrapper(*args: Any, **kwargs: Any) -> Any:
 7          print(f"calling {fn.__name__}")
 8          return fn(*args, **kwargs)
 9      return wrapper
10
11
12  @logged
13  def greet(name: str, times: int) -> str:
14      return f"hello {name} " * times
15
16
17  print(greet("laxya", 2))
18  print(greet("laxya"))
19  print(greet(999, "two"))
20  print(greet("laxya", 2).upper())
```

Line 5 is the honest annotation for a decorator — it takes any callable and returns any callable, because `logged` is meant to wrap anything. `greet` is fully annotated. Line 18 omits an argument; line 19 has both arguments the wrong way round.

```
$ mypy deco0.py
Success: no issues found in 1 source file
```

```
$ python3 deco0.py

calling greet
hello laxya hello laxya 
calling greet
Traceback (most recent call last):
  File "deco0.py", line 18, in <module>
    print(greet("laxya"))
  File "deco0.py", line 8, in wrapper
    return fn(*args, **kwargs)
TypeError: greet() missing 1 required positional argument: 'times'
```

**Zero errors.** Lines 18, 19 and 20 are all unchecked, and line 18 crashes at runtime inside the wrapper.

### The decorator erased the signature

Two identical functions, one decorated:

```python
11  def plain(name: str, times: int) -> str: ...
12
13
14  @logged
15  def greet(name: str, times: int) -> str: ...
16
17
18  reveal_type(plain)
19  reveal_type(greet)
```

```
$ mypy deco1.py
deco1.py:20: note: Revealed type is "def (name: str, times: int) -> str"
deco1.py:21: note: Revealed type is "def (*Any, **Any) -> Any"
```

`plain` keeps its parameters and its return. `greet` — the same function, one line different — has become `(*Any, **Any) -> Any`.

And it was the *annotation* that did it, not the code. Line 5 promised to return `Callable[..., Any]`, so as far as the checker is concerned that is now all `greet` is. Everything downstream is `Any`, with the spreading from `08-Any-Object-Never` doing the rest — which is why line 20's `.upper()` on a possibly-non-string also went unmentioned.

> [!warning] **Adding a decorator to a function silently switches off checking at every call site of that function.** Nothing warns you. The checker still reports `Success`, and the only symptom is errors that stop being found.

## What the annotation needs to say

Describing `logged` as *"it returns the wrapper"* is true about the code and says nothing a type system can use — `wrapper` is an implementation detail the caller never sees.

What the caller experiences is that after `@logged`, `greet` still takes a `name: str` and a `times: int` and still gives back a `str`. The printing happens around it; the interface did not move. So the promise is:

> **"I return a function with exactly the same parameters and the same return type as the one you were given."**

That is unsayable with `Callable[[int], int]`, which names *specific* types, while `logged` must work for every signature there is. What's needed is a way to say *"whatever parameters the input had"* and then reuse that same unknown on the way out.

## `ParamSpec`

```python
1  from collections.abc import Callable
2
3
4  def logged[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
5      def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
6          print(f"calling {fn.__name__}")
7          return fn(*args, **kwargs)
8      return wrapper
```

Line 4 declares two placeholders, and the `**` says which kind each one is:

- **`R`** — an ordinary type placeholder. Stands for **one type**.
- **`**P`** — a *parameter-specification* placeholder. Stands for a **whole parameter list**: how many, their names, their types, which are positional and which are keyword.

The `**` is deliberately the same symbol as `**kwargs` — both mean "a bundle of arguments rather than one thing". Without it, `[P, R]` would declare two ordinary type placeholders and `Callable[P, R]` would not parse.

So line 4 reads: *takes a function with parameters `P` returning `R`, gives back a function with parameters `P` returning `R`* — the same `P`, the same `R`, whatever they turn out to be.

That's the 3.12+ spelling. Older code declares them separately and you will meet it:

```python
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def logged(fn: Callable[P, R]) -> Callable[P, R]: ...
```

Same file as before, one decorator changed:

```python
16  reveal_type(greet)
17
18  print(greet("laxya", 2))
19  print(greet("laxya"))
20  print(greet(999, "two"))
21  print(greet("laxya", 2).upper())
```

```
$ mypy deco2.py

deco2.py:16: note: Revealed type is "def (name: str, times: int) -> str"

deco2.py:19: error: Missing positional argument "times" in call to "greet"  
[call-arg]

deco2.py:20: error: Argument 1 to "greet" has incompatible type "int"; expected "str"  [arg-type]

deco2.py:20: error: Argument 2 to "greet" has incompatible type "str"; expected "int"  [arg-type]
```

Line 16 is the point: **`def (name: str, times: int) -> str`** — byte for byte what the *undecorated* function revealed. Parameter names, types and return all survived, where the `Callable[..., Any]` version had flattened the same function to `def (*Any, **Any) -> Any`.

Lines 19 and 20 are caught, with 20 producing one error per wrong argument. Line 21 is silent — correctly, because the return type is known to be `str` again rather than `Any`.

On line 5: `P.args` and `P.kwargs` spell "the positional half of `P`" and "the keyword half of `P`". They are used as a pair, only inside a function whose parameters are being described by `P`, and they are what tie `wrapper`'s arguments to the signature `logged` promised to preserve.

## Why there is no `**R`

A natural question, since `P` needed the `**` and `R` didn't. **A Python function returns exactly one object** — `return "alice", 30` is not two returns, it builds a tuple and returns that:

```
$ python3 multiret.py

returned: ('alice', 30)
how many objects came back: 1 - a tuple
```

```
$ mypy multiret.py

multiret.py:7: note: Revealed type is "tuple[str, int]"
multiret.py:8: note: Revealed type is "str"
multiret.py:9: note: Revealed type is "int"
```

`two_things()` is one value of type `tuple[str, int]`. `name, age = two_things()` unpacks it afterwards and the checker tracks each half — but the return itself was one thing with one type.

So `R` never needs to stand for a list, and `**R` is rejected outright:

```python
4  def logged[**P, **R](fn: Callable[P, R]) -> Callable[P, R]:
```

```
$ mypy badspec.py

badspec.py:4: error: Invalid location for ParamSpec "R"  [valid-type]
badspec.py:4: note: You can use ParamSpec as the first argument to Callable, e.g., "Callable[R, int]"
```

A `ParamSpec` may only appear as the **first** argument to `Callable` — the parameter-list slot. It is structurally the wrong kind of thing for a return.

| | what it is | placeholder |
|---|---|---|
| **parameters** | a list — variable count, names, positional vs keyword | `**P` |
| **return** | one value, always | `R` |

Which is the same asymmetry as `Callable[[int], int]`: the arguments needed their own brackets because a function may take zero or nine, and the return slot never did because there is always precisely one.

## What this concept claims

**A function is a value with a type, and that type is its whole signature — parameter count, parameter types, and return type together.**

Four things to carry:

1. Bare `Callable` means `Callable[..., Any]`: it checks the thing is callable and nothing more, exactly as bare `list` checks the box and not the contents.
2. `Callable[[int], int]` — arguments in their own list because a function may take any number, one return type because there is always exactly one. Arity is part of the type.
3. `...` and `Any` relax different axes. `Callable[..., Any]` is unconstrained in count; `Callable[[Any], Any]` is fixed at one parameter.
4. A decorator annotated `Callable[..., Any] -> Callable[..., Any]` silently unchecks every call site of every function it wraps. `[**P, R]` preserves the signature exactly, and any decorator in a typed codebase should use it.
