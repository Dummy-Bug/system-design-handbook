#python #type-hints #typing #overload #literal #python-utils


Exactly — `bool`, `Literal[True]` and `Literal[False]` are three different types, and the whole of this concept turns on the difference.

The setup is a function shape you write constantly in agent code: an LLM call that either returns the finished answer or streams it.

## An honest union that every caller pays for

```python
 1  import asyncio
 2  from collections.abc import AsyncIterator
 3
 4
 5  async def run(prompt: str, stream: bool = False) -> str | AsyncIterator[str]:
 6      if stream:
 7          return _chunks(prompt)
 8      return f"answer to {prompt}"
 9
10
11  async def _chunks(prompt: str) -> AsyncIterator[str]:
12      for word in ("answer", "to", prompt):
13          yield word
14
15
16  async def main() -> None:
17      whole = await run("why is the sky blue")
18      reveal_type(whole)
19      print(whole.upper())
20
21
22  asyncio.run(main())
```

```
$ mypy ov0.py
ov0.py:18: note: Revealed type is "str | AsyncIterator[str]"
ov0.py:19: error: Item "AsyncIterator[str]" of "str | AsyncIterator[str]" has no attribute "upper"  [union-attr]
```

Line 5's annotation is **honest** — the function really can return either. And line 17 did not ask for streaming, so a human reading it knows a `str` is coming back.

mypy does not. Line 18 is the full union and line 19 is `18-Narrowing`'s `[union-attr]` all over again.

### The workaround, and its price

```python
 1  import asyncio
 2  from collections.abc import AsyncIterator
 3
 4
 5  async def run(prompt: str, stream: bool = False) -> str | AsyncIterator[str]:
 6      if stream:
 7          return _chunks(prompt)
 8      return f"answer to {prompt}"
 9
10
11  async def _chunks(prompt: str) -> AsyncIterator[str]:
12      for word in ("answer", "to", prompt):
13          yield word
14
15
16  async def main() -> None:
17      whole = await run("why is the sky blue")
18      if not isinstance(whole, str):
19          raise TypeError("expected a string")
20      print(whole.upper())
21
22      parts = await run("why is the sky blue", stream=True)
23      if isinstance(parts, str):
24          raise TypeError("expected a stream")
25      async for chunk in parts:
26          print(chunk)
27
28
29  asyncio.run(main())
```

```
$ mypy ov1.py
Success: no issues found in 1 source file
```

```
$ python3 ov1.py
ANSWER TO WHY IS THE SKY BLUE
answer
to
why is the sky blue
```

Clean — and count the cost. **Lines 18-19 and 23-24 are four lines of dead code.** They can never fire. Line 17 did not pass `stream=True`, so `whole` cannot be an iterator; the check exists to prove something the line above already decided. Multiply by every call site in the codebase.

## Why `TypeVar` cannot fix it

`13-TypeVar-And-Generic-Functions` handles *"the return type depends on the argument"* — `list[T] → T`, where `list[str]` in gives `str` out. It is the obvious thing to reach for.

```python
 1  import asyncio
 2  from collections.abc import AsyncIterator
 3
 4
 5  async def run[T: bool](prompt: str, stream: T = False) -> T:
 6      ...
 7
 8
 9  async def main() -> None:
10      a = await run("q")
11      b = await run("q", stream=True)
12      c = await run("q", stream=False)
13      reveal_type(a)
14      reveal_type(b)
15      reveal_type(c)
16
17
18  asyncio.run(main())
```

```
$ mypy ov2.py
ov2.py:10: error: Need type annotation for "a"  [var-annotated]
ov2.py:13: note: Revealed type is "Any"
ov2.py:14: note: Revealed type is "bool"
ov2.py:15: note: Revealed type is "bool"
```

**Lines 14 and 15 are identical.** `stream=True` and `stream=False` both produce `bool` — at the type level there is nothing to tell them apart.

And there is a second, deeper reason that rules `TypeVar` out even if that were solved. To express the answer you would need to write, in the return position:

> *"if `T` is `Literal[True]` then `AsyncIterator[str]`, otherwise `str`"*

**Python's type system has no conditional types.** A `TypeVar` carries a type from input to output *unchanged*; it cannot **map** one type onto a different one.

| | what it does | can it help here? |
|---|---|---|
| `TypeVar` | carries the same type through | no — the output is not the input type |
| union return | states all possibilities | yes, but every caller must narrow |
| `@overload` | a different signature per calling pattern | ← what is needed |

## `@overload` — enumerate instead of compute

```python
 1  import asyncio
 2  from collections.abc import AsyncIterator
 3  from typing import Literal, overload
 4
 5
 6  @overload
 7  async def run(prompt: str, stream: Literal[False] = False) -> str: ...
 8  @overload
 9  async def run(prompt: str, stream: Literal[True]) -> AsyncIterator[str]: ...
10
11
12  async def run(prompt: str, stream: bool = False) -> str | AsyncIterator[str]:
13      if stream:
14          return _chunks(prompt)
15      return f"answer to {prompt}"
16
17
18  async def _chunks(prompt: str) -> AsyncIterator[str]:
19      for word in ("answer", "to", prompt):
20          yield word
21
22
23  async def main() -> None:
24      whole = await run("why is the sky blue")
25      reveal_type(whole)
26      print(whole.upper())
27
28      parts = await run("why is the sky blue", stream=True)
29      reveal_type(parts)
30      async for chunk in parts:
31          print(chunk)
32
33
34  asyncio.run(main())
```

```
$ mypy ov3.py
ov3.py:25: note: Revealed type is "str"
ov3.py:29: note: Revealed type is "typing.AsyncIterator[str]"
Success: no issues found in 1 source file
```

```
$ python3 ov3.py
ANSWER TO WHY IS THE SKY BLUE
answer
to
why is the sky blue
```

**`str` and `AsyncIterator[str]` from the same function**, with no narrowing at either call site — `ov1.py`'s four dead lines are gone and `whole.upper()` simply works.

Three `def run` in one file, which is the part that looks wrong at first. They are not three functions:

- **Lines 7 and 9** — the **overloads**. Bodies are `...`, exactly like the stub file in `22-Third-Party-Libraries`. Pure signature, and all a caller ever sees.
- **Line 12** — the **implementation**. The only one that runs. It takes plain `bool` and returns the honest union, because at runtime it genuinely handles both.

`Literal[False]` and `Literal[True]` do the work. `09-Literal-Final-ClassVar` gave `Literal` as *"this exact value, not merely this type"* — which is precisely the distinction `TypeVar` could not make. Now `stream=True` and `stream=False` are different **types**, so a different signature can be selected for each.

## The cost: a value known only at runtime

```python
 1  import asyncio
 2  import os
 3  from collections.abc import AsyncIterator
 4  from typing import Literal, overload
 5
 6
 7  @overload
 8  async def run(prompt: str, stream: Literal[False] = False) -> str: ...
 9  @overload
10  async def run(prompt: str, stream: Literal[True]) -> AsyncIterator[str]: ...
11
12
13  async def run(prompt: str, stream: bool = False) -> str | AsyncIterator[str]:
14      if stream:
15          return _chunks(prompt)
16      return f"answer to {prompt}"
17
18
19  async def _chunks(prompt: str) -> AsyncIterator[str]:
20      for word in ("answer", "to", prompt):
21          yield word
22
23
24  async def main() -> None:
25      flag = os.environ.get("STREAM") == "1"
26      reveal_type(flag)
27      result = await run("why is the sky blue", stream=flag)
28      print(result)
29
30
31  asyncio.run(main())
```

```
$ mypy ov4.py
ov4.py:26: note: Revealed type is "bool"
ov4.py:27: error: No overload variant of "run" matches argument types "str", "bool"  [call-overload]
ov4.py:27: note: Possible overload variants:
ov4.py:27: note:     def run(prompt: str, stream: Literal[False] = ...) -> Coroutine[Any, Any, str]
ov4.py:27: note:     def run(prompt: str, stream: Literal[True]) -> Coroutine[Any, Any, AsyncIterator[str]]
```

`flag` comes from an environment variable, so line 26 reveals plain `bool` — and mypy rejects the call. Note the error code `[call-overload]`, and that mypy lists every variant it tried; that listing is the most useful thing about overload errors.

This is the honest trade of the feature: **you enumerated the calling patterns, so anything outside the enumeration is now an error** — even though line 27 would run perfectly well, since the implementation on line 13 takes a plain `bool`.

### The objection, and why it is correct

The natural push-back: a `bool` is only ever `True` or `False`, so two overloads should cover it.

```python
 1  from typing import Literal
 2
 3
 4  def takes_bool(x: bool) -> None: ...
 5
 6
 7  def takes_either(x: Literal[True] | Literal[False]) -> None: ...
 8
 9
10  flag: bool = True
11  both: Literal[True] | Literal[False] = True
12
13  takes_either(flag)
14  takes_bool(both)
```

```
$ mypy ov5.py
Success: no issues found in 1 source file

$ pyright ov5.py
0 errors, 0 warnings, 0 informations
```

**The premise is right.** `bool` and `Literal[True] | Literal[False]` are mutually assignable, and both checkers agree.

What breaks is the *resolution algorithm*, not the type theory. Overload resolution is not asking *"do my variants between them cover this argument?"* — it must pick **exactly one variant**, because it must produce **exactly one return type**. And a plain `bool` is not assignable to either literal on its own:

```python
1  from typing import Literal
2
3
4  def only_false(x: Literal[False]) -> None: ...
5
6
7  flag: bool = True
8  only_false(flag)
```

```
$ mypy ov6.py
ov6.py:8: error: Argument 1 to "only_false" has incompatible type "bool"; expected "Literal[False]"  [arg-type]
```

Variant 1 does not match, variant 2 does not match, and mypy stops.

### The checkers disagree

```python
 1  import asyncio
 2  import os
 3  from collections.abc import AsyncIterator
 4  from typing import Literal, overload
 5
 6
 7  @overload
 8  async def run(prompt: str, stream: Literal[False] = False) -> str: ...
 9  @overload
10  async def run(prompt: str, stream: Literal[True]) -> AsyncIterator[str]: ...
11
12
13  async def run(prompt: str, stream: bool = False) -> str | AsyncIterator[str]:
14      if stream:
15          return _chunks(prompt)
16      return f"answer to {prompt}"
17
18
19  async def _chunks(prompt: str) -> AsyncIterator[str]:
20      for word in ("answer", "to", prompt):
21          yield word
22
23
24  async def main() -> None:
25      flag = os.environ.get("STREAM") == "1"
26      result = await run("why is the sky blue", stream=flag)
27      reveal_type(result)
28
29
30  asyncio.run(main())
```

```
$ pyright ov7.py
ov7.py:27:17 - information: Type of "result" is "AsyncIterator[str] | str"
0 errors, 0 warnings, 1 information
```

```
$ mypy ov7.py
ov7.py:27: note: Revealed type is "Any"
Found 1 error in 1 file (checked 1 source file)
```

Same file, same line, opposite verdicts.

Pyright does not stop when no single variant matches. It performs **argument type expansion**: split `bool` into `Literal[True] | Literal[False]`, resolve the call once per piece, and union the answers — producing `AsyncIterator[str] | str`. That is the objection above, implemented.

> [!important] This is the **second verified mypy/pyright disagreement** in this folder, after `16-Protocol`'s parameter-name mismatch. Both belong to `03-Static-Type-Checkers`, and both make *"which checker are you running?"* a real question rather than pedantry.

## The portable answer: a catch-all overload

```python
 1  import asyncio
 2  import os
 3  from collections.abc import AsyncIterator
 4  from typing import Literal, overload
 5
 6
 7  @overload
 8  async def run(prompt: str, stream: Literal[False] = False) -> str: ...
 9  @overload
10  async def run(prompt: str, stream: Literal[True]) -> AsyncIterator[str]: ...
11  @overload
12  async def run(prompt: str, stream: bool) -> str | AsyncIterator[str]: ...
13
14
15  async def run(prompt: str, stream: bool = False) -> str | AsyncIterator[str]:
16      if stream:
17          return _chunks(prompt)
18      return f"answer to {prompt}"
19
20
21  async def _chunks(prompt: str) -> AsyncIterator[str]:
22      for word in ("answer", "to", prompt):
23          yield word
24
25
26  async def main() -> None:
27      whole = await run("why is the sky blue")
28      reveal_type(whole)
29
30      parts = await run("why is the sky blue", stream=True)
31      reveal_type(parts)
32
33      flag = os.environ.get("STREAM") == "1"
34      unknown = await run("why is the sky blue", stream=flag)
35      reveal_type(unknown)
36
37
38  asyncio.run(main())
```

```
$ mypy ov8.py
ov8.py:28: note: Revealed type is "str"
ov8.py:31: note: Revealed type is "typing.AsyncIterator[str]"
ov8.py:35: note: Revealed type is "str | typing.AsyncIterator[str]"
Success: no issues found in 1 source file
```

```
$ pyright ov8.py
ov8.py:28:17 - information: Type of "whole" is "str"
ov8.py:31:17 - information: Type of "parts" is "AsyncIterator[str]"
ov8.py:35:17 - information: Type of "unknown" is "str | AsyncIterator[str]"
0 errors, 0 warnings, 3 informations
```

Precise where the value is known, honest where it is not. Only line 35's caller has to narrow — correctly, because only that caller genuinely does not know.

> [!warning] **Order matters.** The catch-all on line 12 is last. Checkers try variants top to bottom and take the first that matches, so putting the `bool` variant first would swallow both literal cases and return you to the union everywhere.

This is the pattern real libraries use in their stubs: precise types for the common literal cases, one wide variant for the rest.

## What this concept claims

**`@overload` is for when the return type depends on *how* a function is called rather than on the types it is given — you enumerate the calling patterns instead of computing an answer.**

Five things to carry:

1. A union return type is honest but charges every call site: each one must narrow, including the ones where the call itself already settles the question, producing runtime checks that can never fire.
2. A `TypeVar` cannot do this job. It carries a type from input to output **unchanged** and cannot map one type onto a different one — Python has no conditional types — and separately, `stream=True` and `stream=False` are both `bool`, so there is nothing for it to distinguish.
3. `Literal` is what creates the distinction, which is `09-Literal-Final-ClassVar` paying off: *this exact value*, not merely this type. It turns two calls that differ only in a **value** into two calls that differ in **type**.
4. The `@overload`-decorated definitions are pure signature with `...` bodies — the same construct as a `.pyi` stub — and they are all a caller sees. The final, undecorated definition is the implementation: wide parameter types, union return, and the only one that ever runs.
5. `bool` is assignable to `Literal[True] | Literal[False]` but **not** to either alone, and overload resolution must select exactly one variant. mypy therefore rejects a runtime `bool`; pyright expands the argument into its literals and unions the results. The portable fix is an explicit catch-all overload — placed **last**, since the first matching variant wins.
